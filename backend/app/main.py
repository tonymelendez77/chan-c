from fastapi import FastAPI

from app.api import api_router

app = FastAPI(
    title="CHAN-C API",
    description="Skilled trades marketplace for Guatemala's informal labor market",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}
