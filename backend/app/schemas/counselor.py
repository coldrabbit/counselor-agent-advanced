from pydantic import BaseModel


class CounselorProfileRequest(BaseModel):
    name: str
    college: str
    phone: str | None = None
    email: str | None = None


class CounselorProfileResponse(BaseModel):
    id: str
    name: str
    college: str
    phone: str | None = None
    email: str | None = None

    model_config = {"from_attributes": True}
