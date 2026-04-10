import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDMixin
from .enums import SkillLevel, Trade


class WorkerTrade(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "worker_trades"

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False, index=True
    )
    trade: Mapped[Trade] = mapped_column(
        Enum(Trade, name="trade"), nullable=False
    )
    skill_level: Mapped[SkillLevel] = mapped_column(
        Enum(SkillLevel, name="skill_level"), nullable=False
    )
    years_experience: Mapped[int] = mapped_column(Integer, nullable=False)
    can_cover: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    cannot_cover: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    verified_by_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    worker: Mapped["Worker"] = relationship("Worker", back_populates="trades")
