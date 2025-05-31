import pytest


class TestGetAllUsers:
    """Test cases for GET /users/ endpoint"""

    def test_get_all_users_success(self, client, session, sample_users):
        """Test successful retrieval of all users"""
        # Make the request
        response = client.get("/v1/users/")

        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["telegram_id"] == "john@example.com"
        assert response_data[1]["telegram_id"] == "jane@example.com"

    def test_get_all_users_empty_list(self, client, session):
        """Test retrieval when no users exist"""
        # Make the request
        response = client.get("/v1/users/")

        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == []


class TestCreateUser:
    """Test cases for POST /users/ endpoint"""

    def test_create_user_success(self, client, session, sample_user_create):
        """Test successful user creation"""

        # Prepare request data
        user_data = {"telegram_id": "newuser2@example.com"}

        # Make the request
        response = client.post("/v1/users/", json=user_data)

        # Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert "id" in response_data.keys()
        assert response_data["telegram_id"] == "newuser2@example.com"

    def test_create_user_invalid_data(self, client, session):
        """Test user creation with invalid data"""

        # Prepare invalid request data (missing required fields)
        invalid_user_data = {"name": "asd"}

        # Make the request
        response = client.post("/v1/users/", json=invalid_user_data)

        # Assertions - FastAPI should return 422 for validation errors
        assert response.status_code == 422

    def test_create_user_empty_data(self, client, session):

        # Make the request with empty data
        response = client.post("/v1/users/", json={})

        # Assertions - FastAPI should return 422 for validation errors
        assert response.status_code == 422


class TestUserRoutesIntegration:
    """Integration tests for user routes"""

    def test_create_and_retrieve_user_flow(self, client, session):
        """Test the complete flow of creating and then retrieving users"""

        # Create a user
        user_data = {"telegram_id": "test100@example.com"}
        create_response = client.post("/v1/users/", json=user_data)
        assert create_response.status_code == 200

        # Retrieve all users
        get_response = client.get("/v1/users/")
        assert get_response.status_code == 200

        users_data = get_response.json()
        assert len(users_data) == 1
        assert users_data[0]["telegram_id"] == "test100@example.com"


@pytest.mark.asyncio
class TestAsyncUserRoutes:
    """Test cases for async functionality"""

    async def test_concurrent_requests(self, client, session):
        """Test handling of concurrent requests"""
        import asyncio

        # Simulate concurrent requests
        async def make_request():
            return client.get("/v1/users/")

        # Create multiple concurrent requests
        tasks = [make_request() for _ in range(5)]
        responses = await asyncio.gather(*tasks)

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
