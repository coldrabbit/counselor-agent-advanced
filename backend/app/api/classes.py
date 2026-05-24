from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.classes import ClassCreate, ClassResponse
from app.repositories.classes import ClassRepository

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("", response_model=list[ClassResponse])
def list_classes(db: Session = Depends(get_db)):
    return ClassRepository(db).list_all()


@router.post("", response_model=ClassResponse)
def create_class(req: ClassCreate, db: Session = Depends(get_db)):
    return ClassRepository(db).create(name=req.name, grade=req.grade, major=req.major)
