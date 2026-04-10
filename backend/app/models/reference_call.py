import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import ReferenceCallStatus, ReferenceOutcome


class ReferenceCall(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "reference_calls"

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )
    reference_name: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_phone: Mapped[str] = mapped_column(String(50), nullable=False)
    call_status: Mapped[ReferenceCallStatus] = mapped_column(
        Enum(ReferenceCallStatus, name="reference_call_status"), nullable=False
    )
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[ReferenceOutcome | None] = mapped_column(
        Enum(ReferenceOutcome, name="reference_outcome", create_type=False),
        nullable=True,
    )
    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    called_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    worker: Mapped["Worker"] = relationship(
        "Worker", back_populates="reference_calls"
    )
