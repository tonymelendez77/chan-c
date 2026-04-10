from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_admin
from app.models import Worker, WorkerProfile, WorkerReference, WorkerTrade
from app.models.enums import Trade
from app.schemas.auth import TokenData
from app.schemas.worker import (
    WorkerCreate,
    WorkerDetailRead,
    WorkerListRead,
    WorkerUpdate,
)

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("", response_model=list[WorkerListRead])
async def list_workers(
    trade: Trade | None = None,
    zone: str | None = None,
    is_available: bool | None = None,
    is_vetted: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List all active workers with optional filters for trade, zone, availability, and vetting status."""
    stmt = select(Worker).where(Worker.is_active.is_(True))

    if zone is not None:
        stmt = stmt.where(Worker.zone == zone)
    if is_available is not None:
        stmt = stmt.where(Worker.is_available.is_(is_available))
    if is_vetted is not None:
        stmt = stmt.where(Worker.is_vetted.is_(is_vetted))
    if trade is not None:
        stmt = stmt.join(Worker.trades).where(WorkerTrade.trade == trade)

    stmt = stmt.order_by(Worker.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{worker_id}", response_model=WorkerDetailRead)
async def get_worker(
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Get a single worker with their trades, references, and profile."""
    stmt = (
        select(Worker)
        .where(Worker.id == worker_id)
        .options(
            selectinload(Worker.profile),
            selectinload(Worker.trades),
            selectinload(Worker.references),
        )
    )
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.post("", response_model=WorkerDetailRead, status_code=201)
async def create_worker(
    data: WorkerCreate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Create a new worker with optional trades, references, and profile. Admin only."""
    worker = Worker(
        full_name=data.full_name,
        phone=data.phone,
        dpi=data.dpi,
        zone=data.zone,
        language=data.language,
        is_available=data.is_available,
        notes=data.notes,
    )
    db.add(worker)
    await db.flush()

    if data.profile:
        profile = WorkerProfile(worker_id=worker.id, **data.profile.model_dump())
        db.add(profile)

    if data.trades:
        for t in data.trades:
            db.add(WorkerTrade(worker_id=worker.id, **t.model_dump()))

    if data.references:
        for r in data.references:
            db.add(WorkerReference(worker_id=worker.id, **r.model_dump()))

    await db.commit()

    # Re-fetch with relationships loaded
    stmt = (
        select(Worker)
        .where(Worker.id == worker.id)
        .options(
            selectinload(Worker.profile),
            selectinload(Worker.trades),
            selectinload(Worker.references),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.patch("/{worker_id}", response_model=WorkerDetailRead)
async def update_worker(
    worker_id: UUID,
    data: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Update worker fields. Only provided fields are changed."""
    stmt = (
        select(Worker)
        .where(Worker.id == worker_id)
        .options(
            selectinload(Worker.profile),
            selectinload(Worker.trades),
            selectinload(Worker.references),
        )
    )
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(worker, field, value)

    await db.commit()
    await db.refresh(worker)
    return worker


@router.delete("/{worker_id}", status_code=200)
async def deactivate_worker(
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Soft-delete a worker by setting is_active=False. Never hard deletes."""
    stmt = select(Worker).where(Worker.id == worker_id)
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.is_active = False
    await db.commit()
    return {"detail": "Worker deactivated"}
