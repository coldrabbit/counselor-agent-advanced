from pydantic import BaseModel, Field


class MonthlyTaskResponse(BaseModel):
    id: str
    month: int = Field(..., ge=1, le=12)
    category: str
    title: str
    description: str
    action_type: str
    action_label: str
    action_params: dict[str, str]

    model_config = {"from_attributes": True}
