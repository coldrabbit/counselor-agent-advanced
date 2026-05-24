from datetime import datetime
from pydantic import BaseModel, Field


class GenerateNoticeRequest(BaseModel):
    event: str = Field(..., min_length=1, max_length=2000, description="事件描述")
    time: str | None = Field(None, max_length=256, description="时间")
    location: str | None = Field(None, max_length=256, description="地点")
    participants: str | None = Field(None, max_length=512, description="参加人员")


class NoticeResponse(BaseModel):
    id: str
    title: str
    event: str
    formal_notice: str
    wechat_notice: str
    parent_notice: str
    sms_notice: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoticeListItem(BaseModel):
    id: str
    title: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
