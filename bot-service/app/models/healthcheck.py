from app.db import SQLBaseModel


class HealthcheckResponse(SQLBaseModel):
    status: str
    service: str
    version: str
    database: str
    expense_categories: list[str]
