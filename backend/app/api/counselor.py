from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.counselor import CounselorProfileRequest, CounselorProfileResponse
from app.repositories import CounselorRepository

router = APIRouter(prefix="/counselor", tags=["counselor"])


@router.get("/profile", response_model=CounselorProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    repo = CounselorRepository(db)
    profile = repo.get_first()
    return profile


@router.put("/profile", response_model=CounselorProfileResponse)
def save_profile(req: CounselorProfileRequest, db: Session = Depends(get_db)):
    repo = CounselorRepository(db)
    profile = repo.upsert(
        name=req.name,
        college=req.college,
        phone=req.phone or "",
        email=req.email or "",
    )
    return profile
