from datetime import datetime
from pydantic import BaseModel, Field


class GenerateTalkRecordRequest(BaseModel):
    student_name: str = Field(..., min_length=1, max_length=64, description="学生姓名")
    student_id: str = Field(..., min_length=1, max_length=64, description="学生学号")
    situation: str = Field(..., min_length=1, max_length=3000, description="谈话情况描述")


class TalkRecordResponse(BaseModel):
    id: str
    student_name: str
    student_id: str
    situation: str
    conversation_record: str
    risk_level: str
    follow_up_advice: str
    parent_advice: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TalkRecordListItem(BaseModel):
    id: str
    student_name: str
    risk_level: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
