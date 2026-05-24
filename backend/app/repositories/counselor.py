from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.counselor import CounselorProfile
from app.repositories.base import BaseRepository


class CounselorRepository(BaseRepository[CounselorProfile]):
    def __init__(self, db: Session):
        super().__init__(CounselorProfile, db)

    def get_first(self) -> Optional[CounselorProfile]:
        stmt = select(self.model).limit(1)
        return self.db.scalars(stmt).first()

    def upsert(self, **kwargs) -> CounselorProfile:
        existing = self.get_first()
        if existing:
            return self.update(existing, **kwargs)
        return self.create(**kwargs)

    def to_dict(self, profile: CounselorProfile) -> dict:
        return {
            "name": profile.name,
            "college": profile.college,
            "phone": profile.phone,
            "email": profile.email,
        }
