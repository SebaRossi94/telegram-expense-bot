import logging
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from app.models.messages import MessageRequest
from app.expense_analyzer import expense_analyzer
from app.api.v1.dependencies import validate_telegram_id

router = APIRouter(prefix="/expenses", tags=["expenses"])

logger = logging.getLogger(__name__)

@router.post("/{telegram_id}")
async def add_expense_to_user(telegram_id: Annotated[str, Depends(validate_telegram_id)], message: MessageRequest):
    """
    Add expense to user.
    """
    # Process the message
    try:
        result = await expense_analyzer.analyze_message(message.message)
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Invalid message"
            )
    except Exception as e:
        logger.error(f"Error in expense_analyzer.analyze_message: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    return result
