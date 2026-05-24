from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.schemas.talk_record import GenerateTalkRecordRequest, TalkRecordResponse, TalkRecordListItem
from app.repositories import TalkRecordRepository, TaskRepository, CounselorRepository
from app.tasks.talk_record_task import generate_talk_record_task
import json

router = APIRouter(prefix="/talk-records", tags=["talk_records"])


class ReviewRequest(BaseModel):
    comment: str = ""


@router.post("/generate", response_model=TalkRecordResponse)
def generate_talk_record(req: GenerateTalkRecordRequest, db: Session = Depends(get_db)):
    record_repo = TalkRecordRepository(db)
    task_repo = TaskRepository(db)
    counselor_repo = CounselorRepository(db)

    profile = counselor_repo.get_first()
    profile_dict = counselor_repo.to_dict(profile) if profile else None

    task = task_repo.create_task(
        task_type="generate_talk_record",
        task_input=req.situation,
    )

    result = generate_talk_record_task(
        student_name=req.student_name,
        student_id=req.student_id,
        situation=req.situation,
        counselor_profile=profile_dict,
    )

    if result.get("success"):
        record = record_repo.create(
            student_name=req.student_name,
            student_id=req.student_id,
            situation=req.situation,
            conversation_record=result.get("conversation_record", ""),
            risk_level=result.get("risk_level", "medium"),
            follow_up_advice=result.get("follow_up_advice", ""),
            parent_advice=result.get("parent_advice", ""),
            status="WAITING_APPROVAL",
        )
        task_repo.mark_success(
            task,
            output=json.dumps(result, ensure_ascii=False),
            model=result.get("model", ""),
            token_usage=result.get("token_usage", 0),
            duration_ms=result.get("duration_ms", 0),
        )
        return record
    else:
        task_repo.mark_failed(task, result.get("error", "Unknown error"))
        raise HTTPException(status_code=500, detail=result.get("error", "生成失败"))


@router.get("", response_model=list[TalkRecordListItem])
def list_talk_records(db: Session = Depends(get_db)):
    return TalkRecordRepository(db).list_all()


@router.get("/{record_id}", response_model=TalkRecordResponse)
def get_talk_record(record_id: str, db: Session = Depends(get_db)):
    record = TalkRecordRepository(db).get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="谈话记录不存在")
    return record


@router.put("/{record_id}/approve", response_model=TalkRecordResponse)
def approve_talk_record(record_id: str, req: ReviewRequest = ReviewRequest(), db: Session = Depends(get_db)):
    repo = TalkRecordRepository(db)
    record = repo.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="谈话记录不存在")
    return repo.update(record, status="APPROVED", review_comment=req.comment or None, reviewed_at=datetime.utcnow())


@router.put("/{record_id}/reject", response_model=TalkRecordResponse)
def reject_talk_record(record_id: str, req: ReviewRequest = ReviewRequest(), db: Session = Depends(get_db)):
    repo = TalkRecordRepository(db)
    record = repo.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="谈话记录不存在")
    return repo.update(record, status="DRAFT", review_comment=req.comment or None, reviewed_at=datetime.utcnow())
