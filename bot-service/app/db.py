import logging
from datetime import datetime, timezone
from typing import Generator

from sqlalchemy import QueuePool, create_engine, event, text
from sqlmodel import Field, Session, SQLModel

from app.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Database engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.log_level == "DEBUG",
)


class SQLBaseModel(SQLModel):
    pass


class SQLBaseModelAudit(SQLBaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@event.listens_for(SQLBaseModelAudit, "before_update", propagate=True)
def updated_at(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


def get_session() -> Generator[Session, None, None]:
    session = Session(engine, autoflush=True)
    yield session
    session.close()


def get_session_no_transaction() -> Generator[Session, None, None]:
    session = Session(engine)
    yield session
    session.close()


def check_db_health() -> bool:
    """Check database health."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
