import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import CounterofferProposedBy, CounterofferStatus


class Counteroffer(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "counteroffers"

    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False, index=True
    )
    proposed_by: Mapped[CounterofferProposedBy] = mapped_column(
        Enum(CounterofferProposedBy, name="counteroffer_proposed_by"), nullable=False
    )
    original_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    proposed_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    original_start: Mapped[date] = mapped_column(Date, nullable=False)
    proposed_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    original_end: Mapped[date] = mapped_column(Date, nullable=False)
    proposed_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[CounterofferStatus] = mapped_column(
        Enum(CounterofferStatus, name="counteroffer_status"), nullable=False
    )
    responded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="counteroffers")
