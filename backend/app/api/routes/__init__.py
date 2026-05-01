from fastapi import APIRouter

from .auth import router as auth_router
from .workers import router as workers_router
from .companies import router as companies_router
from .jobs import router as jobs_router
from .matches import router as matches_router
from .dashboard import router as dashboard_router
from .sms import router as sms_router
from .ai_pipeline import router as ai_pipeline_router
from .recruitment import router as recruitment_router
from .whatsapp import router as whatsapp_router
from .billing import router as billing_router
from .admin_whatsapp import router as admin_whatsapp_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(workers_router)
api_router.include_router(companies_router)
api_router.include_router(jobs_router)
api_router.include_router(matches_router)
api_router.include_router(dashboard_router)
api_router.include_router(sms_router)
api_router.include_router(ai_pipeline_router)
api_router.include_router(recruitment_router)
api_router.include_router(whatsapp_router)
api_router.include_router(billing_router)
api_router.include_router(admin_whatsapp_router)
