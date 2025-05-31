import pytest
from fastapi import HTTPException, status
from fastapi.security.api_key import APIKeyHeader

from app.auth import get_api_key
from app.settings import settings


@pytest.mark.asyncio
async def test_valid_api_key():
    """Test authentication with valid API key."""
    api_key = settings.api_key_secret
    result = await get_api_key(api_key)
    assert result == api_key


@pytest.mark.asyncio
async def test_invalid_api_key():
    """Test authentication with invalid API key."""
    with pytest.raises(HTTPException) as exc_info:
        await get_api_key("invalid_key")

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Could not validate API KEY"


@pytest.mark.asyncio
async def test_empty_api_key():
    """Test authentication with empty API key."""
    with pytest.raises(HTTPException) as exc_info:
        await get_api_key("")

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Could not validate API KEY"


def test_api_key_header_configuration():
    """Test API key header configuration."""
    header = APIKeyHeader(name=settings.api_key_header, auto_error=False)
    assert isinstance(header, APIKeyHeader)
    assert header.model.name == settings.api_key_header
    assert not header.auto_error  # Ensures we handle the error ourselves
