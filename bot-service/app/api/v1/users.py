from typing import Sequence
from fastapi import Depends
from fastapi.routing import APIRouter
from sqlmodel import Session, select
from app.db import get_session
from app.models.users import UserCreate, UserResponse, Users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
async def get_all_users(session: Session = Depends(get_session)) -> Sequence[Users]:
    """
    Get all users.
    """
    users = session.exec(select(Users)).all()
    return users

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, session: Session = Depends(get_session)) -> Users:
    """
    Create a new user.
    """
    created_user = Users(**user.model_dump())
    session.add(created_user)
    session.commit()
    session.refresh(created_user)
    return created_user