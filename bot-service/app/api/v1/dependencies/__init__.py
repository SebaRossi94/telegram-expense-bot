from typing import Annotated
from fastapi import HTTPException, Depends
from sqlmodel import select, Session

from app.db import get_session
from app.models.users import Users


async def validate_telegram_id(telegram_id: str, session: Annotated[Session, Depends(get_session)]):
    """
    Validate Telegram ID.
    """
    user = session.exec(select(Users).where(Users.telegram_id == telegram_id)).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user.telegram_id