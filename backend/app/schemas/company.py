from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import CompanyType, SubscriptionPlan


class CompanyBase(BaseModel):
    name: str
    contact_name: str
    phone: str
    email: str
    zone: str
    company_type: CompanyType
    tax_id: str
    notes: str | None = None


class CompanyCreate(CompanyBase):
    user_id: UUID


class CompanyUpdate(BaseModel):
    name: str | None = None
    contact_name: str | None = None
    phone: str | None = None
    email: str | None = None
    zone: str | None = None
    company_type: CompanyType | None = None
    tax_id: str | None = None
    is_verified: bool | None = None
    subscription_plan: SubscriptionPlan | None = None
    subscription_start: date | None = None
    subscription_end: date | None = None
    notes: str | None = None


class CompanyListRead(BaseModel):
    id: UUID
    name: str
    contact_name: str
    phone: str
    email: str
    zone: str
    company_type: CompanyType
    is_verified: bool
    subscription_plan: SubscriptionPlan
    created_at: datetime

    model_config = {"from_attributes": True}


class CompanyDetailRead(CompanyListRead):
    user_id: UUID
    tax_id: str
    subscription_start: date | None = None
    subscription_end: date | None = None
    notes: str | None = None
    job_count: int = 0

    model_config = {"from_attributes": True}
