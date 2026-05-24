import uuid
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class CounselorProfile(Base):
    __tablename__ = "counselor_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    college: Mapped[str] = mapped_column(String(128), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), default="")
    email: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
