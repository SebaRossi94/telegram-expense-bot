from fastapi.routing import APIRouter

from .expenses import router as expenses_router
from .users import router as users_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(users_router)
router.include_router(expenses_router)
