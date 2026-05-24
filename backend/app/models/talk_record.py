import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

import enum


class TalkRecordStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"


class TalkRecord(Base):
    __tablename__ = "talk_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_name: Mapped[str] = mapped_column(String(64), nullable=False)
    student_id: Mapped[str] = mapped_column(String(64), nullable=False)
    situation: Mapped[str] = mapped_column(Text, nullable=False)
    conversation_record: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    follow_up_advice: Mapped[str] = mapped_column(Text, nullable=False)
    parent_advice: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TalkRecordStatus] = mapped_column(SAEnum(TalkRecordStatus), default=TalkRecordStatus.DRAFT, nullable=False)
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
