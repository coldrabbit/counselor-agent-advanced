from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.risk_record import RiskRecord
from app.models.student import Student
from app.repositories.base import BaseRepository


class RiskRepository(BaseRepository[RiskRecord]):
    def __init__(self, db: Session):
        super().__init__(RiskRecord, db)

    def list_all(self, risk_level: str | None = None, status: str | None = None):
        stmt = select(RiskRecord, Student.name, Student.student_id).join(
            Student, RiskRecord.student_id == Student.id
        )
        if risk_level:
            stmt = stmt.where(RiskRecord.risk_level == risk_level)
        if status:
            stmt = stmt.where(RiskRecord.status == status)
        stmt = stmt.order_by(RiskRecord.created_at.desc())
        rows = self.db.execute(stmt).all()
        return [
            {**r[0].__dict__, "student_name": r[1], "student_code": r[2]}
            for r in rows
        ]

    def get_stats(self) -> dict:
        stmt = select(RiskRecord.risk_level, func.count(RiskRecord.id)).group_by(RiskRecord.risk_level)
        rows = self.db.execute(stmt).all()
        counts = {r[0]: r[1] for r in rows}
        return {
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
            "total": sum(counts.values()),
        }

    def update_status(self, record: RiskRecord, status: str) -> RiskRecord:
        return self.update(record, status=status)
