from pathlib import Path
import json
import uuid
import time
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from api.models import (
    AskRequest,
    IngestRequest,
    IngestResponse,
    DocumentResponse
)

from answer_model import AnswerResponse
from generate import answer_question
from ingest import ingest_documents

from grounded_prompt import PROMPT_VERSION
from generate import GENERATION_MODEL

from observability.database import SessionLocal
from observability.logging_service import (
    create_request_log,
    create_retrieved_source_logs,
    update_request_log,
)

router = APIRouter()


@router.post(
    "/ingest",
    response_model=IngestResponse
)
def ingest(request: IngestRequest):

    file_path = Path(request.file_path)

    # Validate that the referenced file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document file not found."
        )

    # Only Markdown documents are approved
    # for this ingestion flow
    if file_path.suffix.lower() != ".md":
        raise HTTPException(
            status_code=400,
            detail="Only Markdown documents are supported."
        )

    # Invoke the existing ingestion pipeline.
    #
    # This is a synchronous route, so FastAPI can
    # execute the blocking ingestion work safely.
    result = ingest_documents()

    # Find chunks belonging to the requested document
    document_chunks = [
        chunk
        for chunk in result["chunks"]
        if chunk["source_path"] == str(
            file_path.relative_to("documents")
        )
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


@router.post(
    "/ask",
    response_model=AnswerResponse
)
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
            PROMPT_VERSION,
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
            response.scores,
        )

        error_category = None

        if response.status == "insufficient_evidence":
            error_category = "missing_evidence"

        update_request_log(
            db,
            request_log,
            latency_ms,
            response.status,
            error_category,
        )

        return response

    except Exception:

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        # Only update the request log if it was successfully created.
        if "request_log" in locals():
            update_request_log(
                db,
                request_log,
                latency_ms,
                "error",
                "internal_error",
            )

        raise

    finally:
        db.close()


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