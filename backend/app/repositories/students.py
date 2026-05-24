from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, db: Session):
        super().__init__(Student, db)

    def list_all(self, class_id: str | None = None, search: str | None = None):
        stmt = select(self.model)
        if class_id:
            stmt = stmt.where(Student.class_id == class_id)
        if search:
            stmt = stmt.where(
                (Student.name.contains(search)) | (Student.student_id.contains(search))
            )
        stmt = stmt.order_by(Student.created_at.desc())
        return self.db.scalars(stmt).all()
