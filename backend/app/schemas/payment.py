from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CommissionBreakdown(BaseModel):
    daily_rate: Decimal
    duration_days: int
    headcount: int
    job_value: Decimal
    commission_pct: Decimal
    commission_amount: Decimal
    currency: str
    status: str | None = None


class PaymentResponse(BaseModel):
    id: UUID
    match_id: UUID
    company_id: UUID
    job_value: Decimal | None = None
    commission_pct: Decimal
    amount: Decimal
    currency: str
    payment_type: str
    status: str
    invoice_date: date | None = None
    paid_date: date | None = None

    model_config = {"from_attributes": True}


class PaymentListItem(BaseModel):
    id: UUID
    match_id: UUID
    company_id: UUID
    company_name: str = ""
    worker_name: str = ""
    job_title: str = ""
    trade: str | None = None
    job_value: Decimal | None = None
    commission_pct: Decimal
    amount: Decimal
    currency: str
    status: str
    invoice_date: date | None = None
    paid_date: date | None = None

    model_config = {"from_attributes": True}


class BillingStats(BaseModel):
    commissions_pending: Decimal
    commissions_collected: Decimal
    average_commission: Decimal
    total_job_value_active: Decimal
    currency: str = "GTQ"
