import pytest

pytestmark = pytest.mark.asyncio


async def test_add_expense_success(client_with_analyzer, mock_analyzer, sample_users):
    """Test successful expense addition"""
    # Mock the analyzer response
    mock_analyzer.analyze_message.return_value = {
        "amount": 100.0,
        "category": "Food",
        "description": "Lunch",
    }

    response = client_with_analyzer.post(
        f"/v1/expenses/{sample_users[0].telegram_id}", json={"message": "100 for lunch"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100.0
    assert data["category"] == "Food"
    assert data["description"] == "Lunch"
    assert data["user_id"] == sample_users[0].id


async def test_add_expense_invalid_message(
    client_with_analyzer, mock_analyzer, sample_users
):
    """Test expense addition with invalid message"""
    # Mock analyzer to return None for invalid message
    mock_analyzer.analyze_message.return_value = None

    response = client_with_analyzer.post(
        f"/v1/expenses/{sample_users[0].telegram_id}",
        json={"message": "invalid message"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid message"


async def test_add_expense_analyzer_error(
    client_with_analyzer, mock_analyzer, sample_users
):
    """Test expense addition when analyzer raises an error"""
    # Mock analyzer to raise an exception
    mock_analyzer.analyze_message.side_effect = Exception("Analysis error")

    response = client_with_analyzer.post(
        f"/v1/expenses/{sample_users[0].telegram_id}", json={"message": "100 for lunch"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"


async def test_get_user_expenses_success(
    client_with_analyzer, sample_users, sample_expense
):
    """Test successful retrieval of user expenses"""
    response = client_with_analyzer.get(f"/v1/expenses/{sample_users[0].telegram_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == 100.0
    assert data[0]["category"] == "Food"
    assert data[0]["description"] == "Lunch"
    assert data[0]["user_id"] == sample_users[0].id


async def test_get_user_expenses_empty(client_with_analyzer, sample_users):
    """Test getting expenses for user with no expenses"""
    response = client_with_analyzer.get(f"/v1/expenses/{sample_users[1].telegram_id}")

    assert response.status_code == 200
    assert response.json() == []


async def test_invalid_telegram_id(client_with_analyzer):
    """Test endpoints with invalid telegram ID"""
    # Test POST endpoint
    response = client_with_analyzer.post(
        "/v1/expenses/nonexistent", json={"message": "100 for lunch"}
    )
    assert response.status_code == 404

    # Test GET endpoint
    response = client_with_analyzer.get("/v1/expenses/nonexistent")
    assert response.status_code == 404
