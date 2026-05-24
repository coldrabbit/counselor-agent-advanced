from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.template import NoticeTemplate
from app.repositories.base import BaseRepository


class TemplateRepository(BaseRepository[NoticeTemplate]):
    def __init__(self, db: Session):
        super().__init__(NoticeTemplate, db)

    def list_all(self, category: str | None = None):
        stmt = select(self.model)
        if category:
            stmt = stmt.where(NoticeTemplate.category == category)
        stmt = stmt.order_by(NoticeTemplate.created_at.desc())
        return self.db.scalars(stmt).all()
