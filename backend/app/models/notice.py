import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

import enum


class NoticeStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"
    SENT = "SENT"


class Notice(Base):
    __tablename__ = "notices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    event: Mapped[str] = mapped_column(Text, nullable=False)
    formal_notice: Mapped[str] = mapped_column(Text, nullable=False)
    wechat_notice: Mapped[str] = mapped_column(Text, nullable=False)
    parent_notice: Mapped[str] = mapped_column(Text, nullable=False)
    sms_notice: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NoticeStatus] = mapped_column(SAEnum(NoticeStatus), default=NoticeStatus.DRAFT, nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
