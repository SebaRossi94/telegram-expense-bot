from sqlmodel import Field
from app.db import SQLBaseModelAudit

class Expenses(SQLBaseModelAudit, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    description: str = Field(nullable=False)
    amount: float = Field(nullable=False)
    category: str = Field(nullable=False)
