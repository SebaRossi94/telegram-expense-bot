import logging
from typing import Annotated, Sequence
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlmodel import Session, select

from app.db import get_session
from app.models.messages import MessageRequest
from app.models.expenses import Expenses
from app.models.users import Users
from app.expense_analyzer import ExpenseAnalyzer
from app.api.v1.dependencies import validate_telegram_id, get_analyzer

router = APIRouter(prefix="/expenses", tags=["expenses"])

logger = logging.getLogger(__name__)

@router.post("/{telegram_id}")
async def add_expense_to_user(
    user: Annotated[Users, Depends(validate_telegram_id)],
    payload: MessageRequest,
    analyzer: Annotated[ExpenseAnalyzer, Depends(get_analyzer)],
    session: Annotated[Session, Depends(get_session)],
    ) -> Expenses:
    """
    Add expense to user.
    """
    # Process the message
    try:
        result = await analyzer.analyze_message(payload.message)
    except Exception as e:
        logger.error(f"Error in expense_analyzer.analyze_message: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    else:
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Invalid message"
            )
        new_expense = Expenses(user_id=user.id, **result)
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)
        return new_expense


@router.get("/{telegram_id}")
async def get_user_expenses(
    user: Annotated[Users, Depends(validate_telegram_id)],
    session: Annotated[Session, Depends(get_session)],
    ) -> Sequence[Expenses]:
    """
    Get user expenses.
    """
    expenses = session.exec(
        select(Expenses).where(Expenses.user_id == user.id)
    ).all()
    return expenses