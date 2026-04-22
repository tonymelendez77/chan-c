import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import JobStatus, SkillLevelRequired, Trade


class Job(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_required: Mapped[Trade] = mapped_column(
        Enum(Trade, name="trade", create_type=False), nullable=False
    )
    skill_level_required: Mapped[SkillLevelRequired] = mapped_column(
        Enum(SkillLevelRequired, name="skill_level_required"), nullable=False
    )
    zone: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    daily_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="GTQ", nullable=False)
    headcount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # TODO: add migration for total_value
    # Total agreed job value (daily_rate × duration × headcount)
    total_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    special_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="jobs")
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="job")
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="job")
