import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, UUIDMixin
from .enums import ProfileStatus


class WorkerProfile(UUIDMixin, Base):
    __tablename__ = "worker_profiles"

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workers.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    initial_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    profile_status: Mapped[ProfileStatus] = mapped_column(
        Enum(ProfileStatus, name="profile_status"),
        default=ProfileStatus.pending_review,
        nullable=False,
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    profile_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    total_earnings: Mapped[float] = mapped_column(
        Numeric(12, 2), default=0, nullable=False
    )
    response_rate: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )
    completion_rate: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, nullable=False
    )

    # Relationships
    worker: Mapped["Worker"] = relationship("Worker", back_populates="profile")
