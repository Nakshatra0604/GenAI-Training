from datetime import datetime

from sqlalchemy.orm import Session

from observability.observability_models import RequestLog
from observability.observability_models import RetrievedSource
from observability.observability_models import GuardrailDecision


def create_request_log(
    db: Session,
    request_id: str,
    endpoint: str,
    started_at: datetime,
    model_version: str | None = None,
    prompt_version: str | None = None,
):
    request_log = RequestLog(
        request_id=request_id,
        endpoint=endpoint,
        started_at=started_at,
        model_version=model_version,
        prompt_version=prompt_version,
        outcome="started",
    )

    db.add(request_log)
    db.commit()
    db.refresh(request_log)

    return request_log


def create_retrieved_source_logs(
    db: Session,
    request_id: str,
    sources: list[str],
    scores: list[float],
):
    for source_id, score in zip(sources, scores):
        source_log = RetrievedSource(
            request_id=request_id,
            source_id=source_id,
            score=score,
        )

        db.add(source_log)

    db.commit()


def create_guardrail_decision(
    db: Session,
    request_id: str,
    control: str,
    outcome: str,
    reason_code: str,
):
    guardrail_decision = GuardrailDecision(
        request_id=request_id,
        control=control,
        outcome=outcome,
        reason_code=reason_code,
    )

    db.add(guardrail_decision)
    db.commit()
    db.refresh(guardrail_decision)

    return guardrail_decision


def update_request_log(
    db: Session,
    request_log: RequestLog,
    latency_ms: float,
    outcome: str,
    error_category: str | None = None,
    audio_filename: str | None = None,
    audio_type: str | None = None,
    audio_size_bytes: int | None = None,
    transcript: str | None = None,
    stt_latency_ms: float | None = None,
    rag_latency_ms: float | None = None,
    failure_stage: str | None = None,
    retrieval_latency_ms: float | None = None,
    generation_latency_ms: float | None = None,
    tts_latency_ms: float | None = None,
):
    request_log.latency_ms = latency_ms
    request_log.outcome = outcome
    request_log.error_category = error_category

    request_log.audio_filename = audio_filename
    request_log.audio_type = audio_type
    request_log.audio_size_bytes = audio_size_bytes
    request_log.transcript = transcript

    request_log.stt_latency_ms = stt_latency_ms
    request_log.rag_latency_ms = rag_latency_ms
    request_log.retrieval_latency_ms = retrieval_latency_ms
    request_log.generation_latency_ms = generation_latency_ms
    request_log.tts_latency_ms = tts_latency_ms

    request_log.failure_stage = failure_stage

    db.commit()
    db.refresh(request_log)

    return request_log