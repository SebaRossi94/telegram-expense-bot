from fastapi.routing import APIRouter
from app.settings import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "service": settings.app_name,
        "version": settings.version,
    }