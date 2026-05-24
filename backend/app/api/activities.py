from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.repositories import CounselorRepository
from app.tasks.activity_task import generate_activity_plan
from app.repositories.activity import ActivityRepository

router = APIRouter(prefix="/activities", tags=["activities"])


class GenerateActivityRequest(BaseModel):
    theme: str
    budget: str = ""
    participants: str = ""


class ActivityResponse(BaseModel):
    id: str
    title: str
    theme: str
    plan: str
    schedule: str
    host_script: str
    promotion: str
    summary_template: str
    budget: str
    participants: str
    status: str
    created_at: str | None = None

    model_config = {"from_attributes": True}


@router.post("/generate", response_model=ActivityResponse)
def generate_activity(req: GenerateActivityRequest, db: Session = Depends(get_db)):
    profile = CounselorRepository(db).get_first()
    profile_dict = CounselorRepository(db).to_dict(profile) if profile else None

    result = generate_activity_plan(
        theme=req.theme,
        budget=req.budget,
        participants=req.participants,
        counselor_profile=profile_dict,
    )
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "生成失败"))

    repo = ActivityRepository(db)
    return repo.create(
        title=result["title"],
        theme=req.theme,
        plan=result["plan"],
        schedule=result["schedule"],
        host_script=result["host_script"],
        promotion=result["promotion"],
        summary_template=result["summary_template"],
        budget=req.budget,
        participants=req.participants,
    )


@router.get("", response_model=list[ActivityResponse])
def list_activities(db: Session = Depends(get_db)):
    return ActivityRepository(db).list_all()


@router.get("/{id}", response_model=ActivityResponse)
def get_activity(id: str, db: Session = Depends(get_db)):
    a = ActivityRepository(db).get_by_id(id)
    if not a:
        raise HTTPException(status_code=404, detail="不存在")
    return a
