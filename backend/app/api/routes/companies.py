from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models import Company, Job
from app.schemas.auth import TokenData
from app.schemas.company import (
    CompanyCreate,
    CompanyDetailRead,
    CompanyListRead,
    CompanyUpdate,
)

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyListRead])
async def list_companies(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List all companies ordered by creation date."""
    stmt = select(Company).order_by(Company.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{company_id}", response_model=CompanyDetailRead)
async def get_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Get a single company with its job count."""
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get job count
    count_stmt = select(func.count()).select_from(Job).where(Job.company_id == company_id)
    job_count = (await db.execute(count_stmt)).scalar() or 0

    data = CompanyDetailRead.model_validate(company)
    data.job_count = job_count
    return data


@router.post("", response_model=CompanyDetailRead, status_code=201)
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Create a new company linked to an existing user account."""
    company = Company(**data.model_dump())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return CompanyDetailRead.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyDetailRead)
async def update_company(
    company_id: UUID,
    data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Update company fields. Only provided fields are changed."""
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    await db.commit()
    await db.refresh(company)
    return CompanyDetailRead.model_validate(company)
