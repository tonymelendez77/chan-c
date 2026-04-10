from pydantic import BaseModel


class DashboardStats(BaseModel):
    active_workers: int
    vetted_workers: int
    open_jobs: int
    active_matches: int
    pending_matches: int
    completed_jobs_this_month: int
    total_companies: int
