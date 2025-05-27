from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.router import router as api_router
from app.expense_analyzer import ExpenseAnalyzer
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.expense_analyzer = ExpenseAnalyzer()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Bot Service for Telegram Expense Tracking",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(api_router)
