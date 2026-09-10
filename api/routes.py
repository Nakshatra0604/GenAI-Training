from pathlib import Path
import json

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from api.models import (
    AskRequest,
    IngestRequest,
    IngestResponse,
    DocumentResponse
)

from answer_model import AnswerResponse
from generate import answer_question
from ingest import ingest_documents


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
async def ask(request: AskRequest):

    response = await run_in_threadpool(
        answer_question,
        request.question,
        request.category,
        request.max_distance
    )

    return response


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