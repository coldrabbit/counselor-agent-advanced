from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.monthly_task import MonthlyTask
from app.repositories.base import BaseRepository


class MonthlyTaskRepository(BaseRepository[MonthlyTask]):
    def __init__(self, db: Session):
        super().__init__(MonthlyTask, db)

    def get_by_month(self, month: int) -> list[MonthlyTask]:
        stmt = (
            select(MonthlyTask)
            .where(MonthlyTask.month == month)
            .order_by(MonthlyTask.category.asc(), MonthlyTask.title.asc())
        )
        return list(self.db.scalars(stmt).all())
