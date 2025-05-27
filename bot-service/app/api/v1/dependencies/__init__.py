from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session, select

from app.db import get_session
from app.expense_analyzer import ExpenseAnalyzer
from app.models.users import Users


async def validate_telegram_id(
    telegram_id: str, session: Annotated[Session, Depends(get_session)]
) -> Users:
    """
    Validate Telegram ID.
    """
    user = session.exec(select(Users).where(Users.telegram_id == telegram_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_analyzer(request: Request) -> ExpenseAnalyzer:
    return request.app.state.expense_analyzer
