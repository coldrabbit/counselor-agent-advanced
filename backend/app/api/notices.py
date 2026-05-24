from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.notice import GenerateNoticeRequest, NoticeResponse, NoticeListItem
from app.repositories import NoticeRepository, TaskRepository, CounselorRepository
from app.tasks.notice_task import generate_notice_task
import json

router = APIRouter(prefix="/notices", tags=["notices"])


@router.post("/generate", response_model=NoticeResponse)
def generate_notice(req: GenerateNoticeRequest, db: Session = Depends(get_db)):
    notice_repo = NoticeRepository(db)
    task_repo = TaskRepository(db)
    counselor_repo = CounselorRepository(db)

    profile = counselor_repo.get_first()
    profile_dict = counselor_repo.to_dict(profile) if profile else None

    task = task_repo.create_task(
        task_type="generate_notice",
        task_input=req.event,
    )

    result = generate_notice_task(
        event=req.event,
        time=req.time or "",
        location=req.location or "",
        participants=req.participants or "",
        counselor_profile=profile_dict,
    )

    if result.get("success"):
        notice = notice_repo.create(
            title=result.get("title", ""),
            event=req.event,
            formal_notice=result.get("formal_notice", ""),
            wechat_notice=result.get("wechat_notice", ""),
            parent_notice=result.get("parent_notice", ""),
            sms_notice=result.get("sms_notice", ""),
            status="WAITING_APPROVAL",
        )
        task_repo.mark_success(
            task,
            output=json.dumps(result, ensure_ascii=False),
            model=result.get("model", ""),
            token_usage=result.get("token_usage", 0),
            duration_ms=result.get("duration_ms", 0),
        )
        return notice
    else:
        task_repo.mark_failed(task, result.get("error", "Unknown error"))
        raise HTTPException(status_code=500, detail=result.get("error", "生成失败"))


@router.get("", response_model=list[NoticeListItem])
def list_notices(db: Session = Depends(get_db)):
    return NoticeRepository(db).list_all()


@router.get("/{notice_id}", response_model=NoticeResponse)
def get_notice(notice_id: str, db: Session = Depends(get_db)):
    notice = NoticeRepository(db).get_by_id(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    return notice


@router.put("/{notice_id}/approve", response_model=NoticeResponse)
def approve_notice(notice_id: str, db: Session = Depends(get_db)):
    repo = NoticeRepository(db)
    notice = repo.get_by_id(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    return repo.update_status(notice, "APPROVED")


@router.put("/{notice_id}/reject", response_model=NoticeResponse)
def reject_notice(notice_id: str, db: Session = Depends(get_db)):
    repo = NoticeRepository(db)
    notice = repo.get_by_id(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    return repo.update_status(notice, "DRAFT")
