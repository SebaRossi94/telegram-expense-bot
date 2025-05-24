from fastapi.routing import APIRouter
from .users import router as users_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(users_router)