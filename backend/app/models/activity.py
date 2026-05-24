import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    theme: Mapped[str] = mapped_column(Text, default="")
    plan: Mapped[str] = mapped_column(Text, default="")
    schedule: Mapped[str] = mapped_column(Text, default="")
    host_script: Mapped[str] = mapped_column(Text, default="")
    promotion: Mapped[str] = mapped_column(Text, default="")
    summary_template: Mapped[str] = mapped_column(Text, default="")
    budget: Mapped[str] = mapped_column(String(64), default="")
    participants: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="DRAFT")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
