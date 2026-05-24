from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.students import StudentCreate, StudentUpdate, StudentResponse
from app.repositories.students import StudentRepository

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentResponse])
def list_students(
    class_id: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return StudentRepository(db).list_all(class_id=class_id, search=search)


@router.post("", response_model=StudentResponse)
def create_student(req: StudentCreate, db: Session = Depends(get_db)):
    return StudentRepository(db).create(
        name=req.name, student_id=req.student_id, class_id=req.class_id,
        phone=req.phone, risk_level=req.risk_level,
    )


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: str, req: StudentUpdate, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    student = repo.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    return repo.update(student, **update_data)


@router.delete("/{student_id}")
def delete_student(student_id: str, db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    student = repo.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    repo.delete(student)
    return {"ok": True}
