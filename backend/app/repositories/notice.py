from sqlalchemy.orm import Session
from app.models.notice import Notice
from app.repositories.base import BaseRepository


class NoticeRepository(BaseRepository[Notice]):
    def __init__(self, db: Session):
        super().__init__(Notice, db)

    def list_all(self):
        return super().list_all(order_by=Notice.created_at.desc())

    def update_status(self, notice: Notice, status: str) -> Notice:
        return self.update(notice, status=status)
