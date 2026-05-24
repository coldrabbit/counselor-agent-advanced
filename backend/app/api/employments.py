import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.repositories.employment import EmploymentRepository
from app.repositories import CounselorRepository
from app.services.ai.client import AIService
from app.prompts.employment import build_employment_prompt, build_employment_stats_prompt

router = APIRouter(prefix="/employments", tags=["employments"])


class EmploymentCreate(BaseModel):
    student_name: str
    student_id: str = ""
    company: str = ""
    position: str = ""
    status: str = "seeking"
    offer_date: str | None = None
    notes: str = ""


class EmploymentUpdate(BaseModel):
    company: str | None = None
    position: str | None = None
    status: str | None = None
    offer_date: str | None = None
    notes: str | None = None


class EmploymentResponse(BaseModel):
    id: str
    student_name: str
    student_id: str
    company: str
    position: str
    status: str
    offer_date: str | None = None
    notes: str
    created_at: str | None = None

    model_config = {"from_attributes": True}


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return EmploymentRepository(db).get_stats()


@router.get("", response_model=list[EmploymentResponse])
def list_employments(status: str | None = Query(None), db: Session = Depends(get_db)):
    return EmploymentRepository(db).list_all(status=status)


@router.post("", response_model=EmploymentResponse)
def create_employment(req: EmploymentCreate, db: Session = Depends(get_db)):
    return EmploymentRepository(db).create(
        student_name=req.student_name,
        student_id=req.student_id,
        company=req.company,
        position=req.position,
        status=req.status,
        offer_date=req.offer_date,
        notes=req.notes,
    )


@router.put("/{id}", response_model=EmploymentResponse)
def update_employment(id: str, req: EmploymentUpdate, db: Session = Depends(get_db)):
    repo = EmploymentRepository(db)
    emp = repo.get_by_id(id)
    if not emp:
        raise HTTPException(status_code=404, detail="记录不存在")
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    return repo.update(emp, **data)


@router.delete("/{id}")
def delete_employment(id: str, db: Session = Depends(get_db)):
    repo = EmploymentRepository(db)
    emp = repo.get_by_id(id)
    if not emp:
        raise HTTPException(status_code=404, detail="记录不存在")
    repo.delete(emp)
    return {"ok": True}


class ResumeAdviceRequest(BaseModel):
    student_name: str
    major: str = ""
    target_position: str = ""


@router.post("/resume-advice")
def resume_advice(req: ResumeAdviceRequest, db: Session = Depends(get_db)):
    profile = CounselorRepository(db).get_first()
    profile_dict = CounselorRepository(db).to_dict(profile) if profile else None

    system_prompt = build_employment_prompt(profile_dict)
    user_message = f"学生：{req.student_name}，专业：{req.major or '未知'}，目标岗位：{req.target_position or '未指定'}"

    ai = AIService()
    result = ai.chat(system_prompt=system_prompt, user_message=user_message)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "AI 调用失败"))

    try:
        content = result["content"].strip().removeprefix("```json").removesuffix("```").strip()
        return {"success": True, "advice": json.loads(content)}
    except json.JSONDecodeError:
        return {"success": True, "advice": {"raw": result["content"]}}


class StatsAnalysisRequest(BaseModel):
    data_text: str = ""


@router.post("/stats-analysis")
def stats_analysis(req: StatsAnalysisRequest):
    ai = AIService()
    result = ai.chat(
        system_prompt=build_employment_stats_prompt(),
        user_message=f"就业数据：\n{req.data_text}" if req.data_text else "请根据当前记录的就业情况进行分析",
    )
    if result.get("success"):
        try:
            content = result["content"].strip().removeprefix("```json").removesuffix("```").strip()
            return {"success": True, "analysis": json.loads(content)}
        except json.JSONDecodeError:
            return {"success": True, "analysis": {"raw": result["content"]}}
    raise HTTPException(status_code=500, detail=result.get("error", "AI 调用失败"))
