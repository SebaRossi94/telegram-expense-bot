from sqlmodel import Field
from app.db import SQLBaseModelAudit

class Users(SQLBaseModelAudit, table=True):
    id: int = Field(primary_key=True)
    telegram_id: str = Field(nullable=False, unique=True)
