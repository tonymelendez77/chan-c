import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import ExtractionFinalStatus


class AIExtraction(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_extractions"

    call_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_calls.id"), nullable=False, index=True
    )
    can_cover: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    cannot_cover: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    counteroffer_price: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    counteroffer_dates: Mapped[str | None] = mapped_column(String(255), nullable=True)
    counteroffer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    availability_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_status: Mapped[ExtractionFinalStatus | None] = mapped_column(
        Enum(ExtractionFinalStatus, name="extraction_final_status"), nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    requires_admin_review: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    extraction_model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    call: Mapped["AICall"] = relationship("AICall", back_populates="extractions")
