import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from .base import Base, UUIDMixin
from .enums import ReferenceOutcome


class WorkerReference(UUIDMixin, Base):
    __tablename__ = "worker_references"

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )
    reference_name: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_phone: Mapped[str] = mapped_column(String(50), nullable=False)
    relationship: Mapped[str] = mapped_column(String(100), nullable=False)
    call_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    outcome: Mapped[ReferenceOutcome | None] = mapped_column(
        Enum(ReferenceOutcome, name="reference_outcome"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )

    # Relationships
    worker: Mapped["Worker"] = sa_relationship("Worker", back_populates="references")
