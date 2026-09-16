from pathlib import Path
from unittest.mock import MagicMock
import sys

# Prevent heavy ML dependencies from loading during API tests.
# We mock only retrieve, NOT generate, so that the real
# GENERATION_MODEL value is still available to the observability logger.
mock_retrieve = MagicMock()
sys.modules["retrieve"] = mock_retrieve

from fastapi.testclient import TestClient

from api.main import app
from answer_model import AnswerResponse
from api.errors import ProviderError


client = TestClient(app, raise_server_exceptions=False)


def test_invalid_ask_request():
    response = client.post(
        "/ask",
        json={}
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error_code"] == "VALIDATION_ERROR"
    assert "request_id" in data


def test_unknown_document():
    response = client.get(
        "/documents/nonexistent-document"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error_code"] == "DOCUMENT_NOT_FOUND"
    assert "request_id" in data


def test_missing_evidence(monkeypatch):
    def mock_answer_question(
        question,
        category=None,
        max_distance=None
    ):
        return AnswerResponse(
            answer="Insufficient evidence.",
            sources=[],
            chunks=[],
            scores=[],
            status="insufficient_evidence"
        )

    monkeypatch.setattr(
        "api.routes.answer_question",
        mock_answer_question
    )

    response = client.post(
        "/ask",
        json={
            "question": "What is information not present in the documents?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "insufficient_evidence"
    assert "request_id" in data
    assert data["request_id"] is not None


def test_successful_ask(monkeypatch):
    def mock_answer_question(
        question,
        category=None,
        max_distance=None
    ):
        return AnswerResponse(
            answer="This is a test answer.",
            sources=["document_1"],
            chunks=["This is a test chunk."],
            scores=[0.15],
            status="answered"
        )

    monkeypatch.setattr(
        "api.routes.answer_question",
        mock_answer_question
    )

    response = client.post(
        "/ask",
        json={
            "question": "What is the test question?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "answered"
    assert data["answer"] == "This is a test answer."
    assert data["sources"] == ["document_1"]
    assert "request_id" in data
    assert data["request_id"] is not None


def test_provider_failure(monkeypatch):
    def mock_answer_question(
        question,
        category=None,
        max_distance=None
    ):
        raise ProviderError("Simulated provider failure")

    monkeypatch.setattr(
        "api.routes.answer_question",
        mock_answer_question
    )

    response = client.post(
        "/ask",
        json={
            "question": "Trigger provider failure"
        }
    )

    assert response.status_code == 502

    data = response.json()

    assert data["error_code"] == "PROVIDER_ERROR"
    assert "request_id" in data

    # Internal/provider exception details must not be exposed.
    assert "Simulated provider failure" not in response.text


def test_successful_ingestion(monkeypatch):
    test_file = Path("documents/test_api_ingestion.md")

    test_file.write_text(
        "# Test Document\n\nThis is test content.",
        encoding="utf-8"
    )

    def mock_ingest_documents():
        return {
            "chunks": [
                {
                    "document_id": "test-document-id",
                    "title": "Test Document",
                    "source_path": "test_api_ingestion.md",
                    "category": "Technology",
                }
            ]
        }

    monkeypatch.setattr(
        "api.routes.ingest_documents",
        mock_ingest_documents
    )

    try:
        response = client.post(
            "/ingest",
            json={
                "file_path": str(test_file)
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["document_id"] == "test-document-id"
        assert data["chunk_count"] == 1
        assert data["status"] == "processed"

    finally:
        if test_file.exists():
            test_file.unlink()