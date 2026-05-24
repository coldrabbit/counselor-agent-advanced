from pydantic import BaseModel


class StudentCreate(BaseModel):
    name: str
    student_id: str
    class_id: str | None = None
    phone: str = ""
    risk_level: str = "low"


class StudentUpdate(BaseModel):
    name: str | None = None
    student_id: str | None = None
    class_id: str | None = None
    phone: str | None = None
    risk_level: str | None = None


class StudentResponse(BaseModel):
    id: str
    name: str
    student_id: str
    class_id: str | None = None
    phone: str
    risk_level: str
    created_at: str | None = None
    updated_at: str | None = None
    model_config = {"from_attributes": True}
