import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

import enum


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    CANCELLED = "CANCELLED"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    input: Mapped[str] = mapped_column(Text, default="")
    output: Mapped[str] = mapped_column(Text, default="")
    model: Mapped[str] = mapped_column(String(128), default="")
    token_usage: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
