from sqlalchemy.orm import Session
from app.models.class_model import Class
from app.repositories.base import BaseRepository


class ClassRepository(BaseRepository[Class]):
    def __init__(self, db: Session):
        super().__init__(Class, db)

    def list_all(self):
        return super().list_all(order_by=Class.created_at.asc())
