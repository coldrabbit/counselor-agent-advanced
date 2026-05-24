from sqlalchemy.orm import Session
from app.models.activity import Activity
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, db: Session):
        super().__init__(Activity, db)

    def list_all(self):
        return super().list_all(order_by=Activity.created_at.desc())
