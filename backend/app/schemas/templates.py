from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    content: str
    category: str = "通用"


class TemplateUpdate(BaseModel):
    name: str | None = None
    content: str | None = None
    category: str | None = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    category: str
    content: str

    model_config = {"from_attributes": True}
