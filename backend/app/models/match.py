import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import MatchStatus, WorkerReply


class Match(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "matches"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True
    )
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"), nullable=False, index=True
    )
    offered_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    final_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    company_notified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    worker_sms_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    worker_replied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    worker_reply: Mapped[WorkerReply | None] = mapped_column(
        Enum(WorkerReply, name="worker_reply"), nullable=True
    )
    company_decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="matches")
    worker: Mapped["Worker"] = relationship("Worker", back_populates="matches")
    counteroffers: Mapped[list["Counteroffer"]] = relationship(
        "Counteroffer", back_populates="match"
    )
    ai_calls: Mapped[list["AICall"]] = relationship("AICall", back_populates="match")
    sms_logs: Mapped[list["SMSLog"]] = relationship("SMSLog", back_populates="match")
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="match")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="match")
