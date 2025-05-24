from fastapi.routing import APIRouter
from app.settings import settings
from app.db import check_db_health

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = check_db_health()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": settings.app_name,
        "version": settings.version,
        "database": "connected" if db_healthy else "disconnected"
    }
