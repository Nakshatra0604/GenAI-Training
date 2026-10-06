from pathlib import Path
import json
import uuid
import time
import tempfile
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from api.models import (
    AskRequest,
    IngestRequest,
    IngestResponse,
    DocumentResponse
)

from answer_model import AnswerResponse
from generate import answer_question
from ingest import ingest_documents
from stt import transcribe_audio
from tts import synthesize_speech

from grounded_prompt import PROMPT_VERSION
from generate import GENERATION_MODEL

from observability.database import SessionLocal
from observability.logging_service import (
    create_request_log,
    create_retrieved_source_logs,
    update_request_log,
)

from api.audio_validation import validate_audio_file


router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    file_path = Path(request.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document file not found."
        )

    if file_path.suffix.lower() != ".md":
        raise HTTPException(
            status_code=400,
            detail="Only Markdown documents are supported."
        )

    result = ingest_documents()

    document_chunks = [
        chunk
        for chunk in result["chunks"]
        if chunk["source_path"] == str(file_path.relative_to("documents"))
    ]

    if not document_chunks:
        raise HTTPException(
            status_code=404,
            detail="Document was not found in the ingestion results."
        )

    document_id = document_chunks[0]["document_id"]

    return IngestResponse(
        document_id=document_id,
        chunk_count=len(document_chunks),
        status="processed"
    )


@router.post("/ask", response_model=AnswerResponse)
def ask(request: AskRequest):
    request_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)
    start_time = time.perf_counter()

    db = SessionLocal()

    try:
        request_log = create_request_log(
            db,
            request_id,
            "/ask",
            started_at,
            GENERATION_MODEL,
            PROMPT_VERSION
        )

        response = answer_question(
            request.question,
            request.category,
            request.max_distance
        )

        response.request_id = request_id

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        create_retrieved_source_logs(
            db,
            request_id,
            response.sources,
            response.scores
        )

        error_category = None

        if response.status == "insufficient_evidence":
            error_category = "missing_evidence"

        update_request_log(
            db,
            request_log,
            latency_ms,
            response.status,
            error_category
        )

        return response

    except Exception:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        if "request_log" in locals():
            update_request_log(
                db,
                request_log,
                latency_ms,
                "error",
                "internal_error"
            )

        raise

    finally:
        db.close()


@router.post("/voice/ask")
async def voice_ask(file: UploadFile = File(...)):
    request_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)
    start_time = time.perf_counter()

    db = SessionLocal()
    request_log = None
    temp_path = None

    file_size = 0
    audio_filename = file.filename or ""
    audio_type = Path(audio_filename).suffix.lower()

    stt_latency_ms = None
    retrieval_latency_ms = None
    generation_latency_ms = None
    rag_latency_ms = None
    tts_latency_ms = None

    transcript = None
    failure_stage = None

    audio_reference = None
    audio_format = None
    synthetic_voice = False
    tts_status = "not_attempted"

    try:
        while True:
            chunk = await file.read(1024 * 1024)

            if not chunk:
                break

            file_size += len(chunk)

        validation = validate_audio_file(
            audio_filename,
            file_size
        )

        if not validation["valid"]:
            failure_stage = "audio_validation"

            raise HTTPException(
                status_code=422,
                detail={
                    "error_code": validation["error_code"],
                    "message": validation["message"]
                }
            )

        request_log = create_request_log(
            db,
            request_id,
            "/voice/ask",
            started_at,
            GENERATION_MODEL,
            PROMPT_VERSION
        )

        request_log.audio_filename = audio_filename
        request_log.audio_type = audio_type
        request_log.audio_size_bytes = file_size

        db.commit()

        suffix = Path(audio_filename).suffix.lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_path = temp_file.name

            await file.seek(0)

            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        # STT stage
        failure_stage = "stt"

        transcription_started = time.perf_counter()

        transcription = transcribe_audio(
            temp_path
        )

        stt_latency_ms = (
            time.perf_counter() - transcription_started
        ) * 1000

        transcript = transcription["transcript"]
        language = transcription["language"]

        if not transcript.strip():
            raise HTTPException(
                status_code=422,
                detail={
                    "error_code": "EMPTY_TRANSCRIPT",
                    "message": "No speech could be detected in the audio."
                }
            )

        # RAG stage
        failure_stage = "rag"

        rag_started = time.perf_counter()

        timing = {}

        response = answer_question(
            transcript,
            None,
            None,
            timing=timing
        )

        rag_latency_ms = (
            time.perf_counter() - rag_started
        ) * 1000

        retrieval_latency_ms = timing.get(
            "retrieval_latency_ms"
        )

        generation_latency_ms = timing.get(
            "generation_latency_ms"
        )

        # TTS stage
        # Only the validated grounded answer is sent to TTS.
        if response.status == "answered":
            failure_stage = "tts"
            tts_status = "failed"

            audio_path = (
                Path("generated_audio")
                / f"{request_id}.wav"
            )

            tts_started = time.perf_counter()

            try:
                tts_result = synthesize_speech(
                    response.answer,
                    str(audio_path)
                )

                tts_latency_ms = (
                    time.perf_counter() - tts_started
                ) * 1000

                audio_reference = (
                    f"/voice/audio/{request_id}"
                )

                audio_format = tts_result["audio_format"]
                synthetic_voice = tts_result["synthetic"]
                tts_status = "generated"

                failure_stage = None

            except Exception:
                tts_latency_ms = (
                    time.perf_counter() - tts_started
                ) * 1000

                # TTS failure must not remove
                # the validated text answer.
                audio_reference = None
                audio_format = None
                synthetic_voice = False
                tts_status = "failed"
                failure_stage = "tts"

        else:
            tts_status = "not_attempted"
            failure_stage = None

        total_latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        create_retrieved_source_logs(
            db,
            request_id,
            response.sources,
            response.scores
        )

        error_category = None

        if response.status == "insufficient_evidence":
            error_category = "missing_evidence"

        update_request_log(
            db,
            request_log,
            total_latency_ms,
            response.status,
            error_category,
            audio_filename,
            audio_type,
            file_size,
            transcript,
            stt_latency_ms,
            rag_latency_ms,
            failure_stage,
            retrieval_latency_ms,
            generation_latency_ms,
            tts_latency_ms,
        )

        return {
            "request_id": request_id,
            "status": response.status,
            "transcript": transcript,
            "language": language,
            "stt_latency_ms": round(
                stt_latency_ms,
                2
            ),
            "retrieval_latency_ms": round(
                retrieval_latency_ms,
                2
            ) if retrieval_latency_ms is not None else None,
            "generation_latency_ms": round(
                generation_latency_ms,
                2
            ) if generation_latency_ms is not None else None,
            "rag_latency_ms": round(
                rag_latency_ms,
                2
            ),
            "tts_latency_ms": round(
                tts_latency_ms,
                2
            ) if tts_latency_ms is not None else None,
            "total_latency_ms": round(
                total_latency_ms,
                2
            ),
            "answer": response.answer,
            "sources": response.sources,
            "chunks": response.chunks,
            "scores": response.scores,
            "retrieved_source_ids": response.retrieved_source_ids,
            "audio": {
                "reference": audio_reference,
                "format": audio_format,
                "synthetic": synthetic_voice,
                "tts_status": tts_status,
            },
        }

    except HTTPException as exc:

        if request_log is not None:
            total_latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            update_request_log(
                db,
                request_log,
                total_latency_ms,
                "error",
                (
                    exc.detail.get("error_code")
                    if isinstance(exc.detail, dict)
                    else "voice_validation_error"
                ),
                audio_filename,
                audio_type,
                file_size,
                transcript,
                stt_latency_ms,
                rag_latency_ms,
                failure_stage,
                retrieval_latency_ms,
                generation_latency_ms,
                tts_latency_ms,
            )

        raise

    except Exception as exc:

        if request_log is not None:
            total_latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            update_request_log(
                db,
                request_log,
                total_latency_ms,
                "error",
                "internal_error",
                audio_filename,
                audio_type,
                file_size,
                transcript,
                stt_latency_ms,
                rag_latency_ms,
                failure_stage,
                retrieval_latency_ms,
                generation_latency_ms,
                tts_latency_ms,
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "VOICE_PROCESSING_ERROR",
                "message": str(exc)
            }
        )

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        db.close()


@router.get("/voice/audio/{request_id}")
def get_voice_audio(request_id: str):
    audio_path = (
        Path("generated_audio")
        / f"{request_id}.wav"
    )

    if not audio_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Generated audio not found."
        )

    return FileResponse(
        path=audio_path,
        media_type="audio/wav",
        filename=f"{request_id}.wav",
        headers={
            "X-Voice-Type": "synthetic"
        },
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse
)
def get_document(document_id: str):
    chunks_file = Path("chunks.jsonl")

    if not chunks_file.exists():
        raise HTTPException(
            status_code=500,
            detail="Document metadata is unavailable."
        )

    document_chunks = []

    with chunks_file.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            if not line.strip():
                continue

            chunk = json.loads(line)

            if chunk.get("document_id") == document_id:
                document_chunks.append(chunk)

    if not document_chunks:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    first_chunk = document_chunks[0]

    return {
        "document_id": first_chunk["document_id"],
        "title": first_chunk["title"],
        "source_path": first_chunk["source_path"],
        "updated_at": first_chunk["updated_at"],
        "category": first_chunk["category"],
        "chunk_count": len(document_chunks),
        "status": "processed"
    }