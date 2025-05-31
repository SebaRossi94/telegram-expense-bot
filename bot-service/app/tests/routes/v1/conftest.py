import pytest

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
