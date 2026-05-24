from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.employment import Employment
from app.repositories.base import BaseRepository


class EmploymentRepository(BaseRepository[Employment]):
    def __init__(self, db: Session):
        super().__init__(Employment, db)

    def list_all(self, status: str | None = None):
        stmt = select(self.model)
        if status:
            stmt = stmt.where(Employment.status == status)
        stmt = stmt.order_by(Employment.created_at.desc())
        return self.db.scalars(stmt).all()

    def get_stats(self) -> dict:
        stmt = select(Employment.status, func.count(Employment.id)).group_by(Employment.status)
        rows = self.db.execute(stmt).all()
        counts = {r[0]: r[1] for r in rows}
        return {
            "seeking": counts.get("seeking", 0),
            "interviewing": counts.get("interviewing", 0),
            "offered": counts.get("offered", 0),
            "accepted": counts.get("accepted", 0),
            "total": sum(counts.values()),
        }
