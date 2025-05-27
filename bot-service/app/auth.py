from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from app.settings import settings

api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)


# Simple API Key authentication dependency
async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == settings.api_key_secret:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate API KEY",
    )
