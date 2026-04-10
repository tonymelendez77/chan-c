import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import AICallStatus, OnboardingCallType


class WorkerOnboardingCall(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "worker_onboarding_calls"

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )
    call_type: Mapped[OnboardingCallType] = mapped_column(
        Enum(OnboardingCallType, name="onboarding_call_type"), nullable=False
    )
    vapi_call_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[AICallStatus] = mapped_column(
        Enum(AICallStatus, name="ai_call_status", create_type=False), nullable=False
    )
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    worker: Mapped["Worker"] = relationship(
        "Worker", back_populates="onboarding_calls"
    )
