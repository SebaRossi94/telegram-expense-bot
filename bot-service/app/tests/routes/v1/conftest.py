from unittest.mock import AsyncMock

import pytest

from app.expense_analyzer import ExpenseAnalyzer
from app.models.expenses import Expenses
from app.models.users import Users


@pytest.fixture
def sample_users(session):
    """Sample user data for testing"""
    users = [
        Users(id=1, telegram_id="john@example.com"),
        Users(id=2, telegram_id="jane@example.com"),
    ]
    session.add_all(users)
    session.commit()
    return users


@pytest.fixture
def sample_user_create(session):
    """Sample user creation data"""
    user = Users(id=1, telegram_id="newuser@example.com")
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def mock_analyzer(mocker):
    """Mock expense analyzer"""
    mock = AsyncMock(spec=ExpenseAnalyzer)
    return mock


@pytest.fixture
def client_with_analyzer(client, mock_analyzer):
    """Client fixture with expense analyzer in app state"""
    client.app.state.expense_analyzer = mock_analyzer
    return client


@pytest.fixture
def sample_expense(session, sample_users):
    """Sample expense data for testing"""
    expense = Expenses(
        id=1,
        user_id=sample_users[0].id,
        amount=100.0,
        category="Food",
        description="Lunch",
    )
    session.add(expense)
    session.commit()
    return expense
