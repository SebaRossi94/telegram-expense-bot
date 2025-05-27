from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    message: str = Field(
        ..., min_length=1, max_length=1000, description="Message content"
    )
