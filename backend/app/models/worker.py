import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import Language


class Worker(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "workers"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    dpi: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zone: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[Language] = mapped_column(
        Enum(Language, name="language"), default=Language.spanish, nullable=False
    )
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_vetted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    vetting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    vetted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    rating_avg: Mapped[float] = mapped_column(Numeric(3, 2), default=0, nullable=False)
    total_jobs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # TODO: add migration for whatsapp_enabled
    whatsapp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # TODO: add migration for availability fields
    paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    paused_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    paused_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pause_reason_code: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    profile: Mapped["WorkerProfile | None"] = relationship(
        "WorkerProfile", back_populates="worker", uselist=False
    )
    trades: Mapped[list["WorkerTrade"]] = relationship(
        "WorkerTrade", back_populates="worker"
    )
    references: Mapped[list["WorkerReference"]] = relationship(
        "WorkerReference", back_populates="worker"
    )
    reference_calls: Mapped[list["ReferenceCall"]] = relationship(
        "ReferenceCall", back_populates="worker"
    )
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="worker")
    ai_calls: Mapped[list["AICall"]] = relationship("AICall", back_populates="worker")
    onboarding_calls: Mapped[list["WorkerOnboardingCall"]] = relationship(
        "WorkerOnboardingCall", back_populates="worker"
    )
    sms_logs: Mapped[list["SMSLog"]] = relationship("SMSLog", back_populates="worker")
