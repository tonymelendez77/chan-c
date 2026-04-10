import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin
from .enums import SMSDirection, SMSStatus


class SMSLog(UUIDMixin, Base):
    __tablename__ = "sms_logs"

    worker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=True, index=True
    )
    match_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id"), nullable=True, index=True
    )
    direction: Mapped[SMSDirection] = mapped_column(
        Enum(SMSDirection, name="sms_direction"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    twilio_sid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[SMSStatus] = mapped_column(
        Enum(SMSStatus, name="sms_status"), nullable=False, index=True
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    worker: Mapped["Worker | None"] = relationship(
        "Worker", back_populates="sms_logs"
    )
    match: Mapped["Match | None"] = relationship("Match", back_populates="sms_logs")
