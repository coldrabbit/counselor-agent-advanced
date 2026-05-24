from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    role: str = "counselor"
    college: str = ""


class UserResponse(BaseModel):
    id: str
    name: str
    role: str
    college: str
    created_at: datetime | None = None
    model_config = {"from_attributes": True}
