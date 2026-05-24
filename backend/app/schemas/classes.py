from pydantic import BaseModel


class ClassCreate(BaseModel):
    name: str
    grade: str = ""
    major: str = ""


class ClassResponse(BaseModel):
    id: str
    name: str
    grade: str
    major: str
    model_config = {"from_attributes": True}
