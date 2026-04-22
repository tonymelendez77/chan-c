from decimal import Decimal

from pydantic import BaseModel


class DashboardStats(BaseModel):
    active_workers: int
    vetted_workers: int
    open_jobs: int
    active_matches: int
    pending_matches: int
    completed_jobs_this_month: int
    total_companies: int
    commissions_pending: Decimal = Decimal("0")
    commissions_collected: Decimal = Decimal("0")
    average_commission: Decimal = Decimal("0")
    total_job_value_active: Decimal = Decimal("0")
