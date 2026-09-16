from datetime import datetime

from sqlalchemy.orm import Session

from observability.observability_models import RequestLog
from observability.observability_models import RetrievedSource

def create_request_log(
    db: Session,
    request_id: str,
    endpoint: str,
    started_at: datetime,
    model_version: str | None,
    prompt_version: str | None,
) -> RequestLog:

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
) -> None:

    for source_id, score in zip(sources, scores):
        source_log = RetrievedSource(
            request_id=request_id,
            source_id=source_id,
            score=score,
        )

        db.add(source_log)

    db.commit()


def update_request_log(
    db: Session,
    request_log: RequestLog,
    latency_ms: float,
    outcome: str,
    error_category: str | None = None,
) -> RequestLog:

    request_log.latency_ms = latency_ms
    request_log.outcome = outcome
    request_log.error_category = error_category

    db.commit()
    db.refresh(request_log)

    return request_log
