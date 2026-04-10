import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import RatedBy


class Rating(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ratings"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False, index=True
    )
    rated_by: Mapped[RatedBy] = mapped_column(
        Enum(RatedBy, name="rated_by"), nullable=False
    )
    rating_score: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="ratings")
    match: Mapped["Match"] = relationship("Match", back_populates="ratings")
