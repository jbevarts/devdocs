"""
Health check endpoints
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check():
    """Readiness check for dependencies"""
    # TODO: Add database and Redis checks
    return {"status": "ready"}

