from sqlmodel import Field

from app.db import SQLBaseModel, SQLBaseModelAudit


class Users(SQLBaseModelAudit, table=True):
    id: int = Field(primary_key=True)
    telegram_id: str = Field(nullable=False, unique=True)


class UserCreate(SQLBaseModel):
    telegram_id: str


class UserResponse(SQLBaseModel):
    id: int
    telegram_id: str
