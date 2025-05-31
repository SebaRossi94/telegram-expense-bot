import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Set test environment variables before importing settings
os.environ.update(
    {
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "test_password",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "test_db",
        "DATABASE_URL": "postgresql://test_user:test_password@localhost:5432/test_db",
        "OPENAI_API_KEY": "test_openai_key",
        "LLM_MODEL": "gpt-3.5-turbo",
        "HUGGINGFACEHUB_API_TOKEN": "test_hf_token",
        "HUGGINGFACEHUB_MODEL": "test_hf_model",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "LOG_LEVEL": "INFO",
        "APP_NAME": "Test Telegram Expense Bot Service",
        "VERSION": "1.0.0",
        "DEV": "true",
        "EXPENSE_CATEGORIES": '["Food","Transportation","Entertainment","Shopping","Bills","Healthcare","Other"]',
        "API_KEY_HEADER": "X-API-Key",
        "API_KEY_SECRET": "test_secret_key",
    }
)

from app.auth import get_api_key  # noqa: E402
from app.db import get_session  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(name="session")
def session_fixture():
    """Session fixture"""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine, autoflush=True) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session_no_transaction")
def session_no_transaction_fixture():
    """Session no transaction fixture"""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def auth_client_fixture(session: Session):
    """Client fixture for requests without authorized user"""

    def get_session_override():
        return session

    def get_api_key_override():
        return None

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_api_key] = get_api_key_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="unauthorized_client")
def client_fixture(session: Session):
    """Client fixture for requests without authorized user"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
