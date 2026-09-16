from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from observability.database import Base


class RequestLog(Base):
    __tablename__= "request_logs"

    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    request_id : Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    endpoint : Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    started_at: Mapped[float | None] = mapped_column(
        DateTime,
        nullable=False
    )

    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    model_version: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    prompt_version: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    outcome: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    error_category: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    retrieved_sources: Mapped[list["RetrievedSource"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan"
    )


class RetrievedSource(Base):
    __tablename__ = "retrieved_sources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    request_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("request_logs.request_id"),
        nullable=False,
        index=True
    )

    source_id: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    request: Mapped["RequestLog"] = relationship(
        back_populates="retrieved_sources"
    )