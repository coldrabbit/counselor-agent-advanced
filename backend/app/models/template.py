import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class NoticeTemplate(Base):
    __tablename__ = "notice_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="通用")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
