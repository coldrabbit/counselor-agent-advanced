from pydantic import BaseModel
from datetime import datetime


class DocumentCreate(BaseModel):
    title: str
    content: str
    category: str = "通用"
    tags: str = ""


class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = {"from_attributes": True}
