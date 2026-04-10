import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import AICallStatus, AICallType, Language


class AICall(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_calls"

    match_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id"), nullable=True, index=True
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )
    call_type: Mapped[AICallType] = mapped_column(
        Enum(AICallType, name="ai_call_type"), nullable=False
    )
    vapi_call_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[AICallStatus] = mapped_column(
        Enum(AICallStatus, name="ai_call_status"), nullable=False, index=True
    )
    language_detected: Mapped[Language | None] = mapped_column(
        Enum(Language, name="language", create_type=False), nullable=True
    )
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recording_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    match: Mapped["Match | None"] = relationship("Match", back_populates="ai_calls")
    worker: Mapped["Worker"] = relationship("Worker", back_populates="ai_calls")
    extractions: Mapped[list["AIExtraction"]] = relationship(
        "AIExtraction", back_populates="call"
    )
