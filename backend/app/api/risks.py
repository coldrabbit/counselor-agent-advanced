from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.risk import RiskRecordCreate, RiskRecordUpdate, RiskRecordResponse, RiskStats
from app.repositories.risk import RiskRepository

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("/stats", response_model=RiskStats)
def risk_stats(db: Session = Depends(get_db)):
    return RiskRepository(db).get_stats()


@router.get("", response_model=list[RiskRecordResponse])
def list_risks(
    risk_level: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return RiskRepository(db).list_all(risk_level=risk_level, status=status)


@router.post("", response_model=RiskRecordResponse)
def create_risk(req: RiskRecordCreate, db: Session = Depends(get_db)):
    return RiskRepository(db).create(student_id=req.student_id, risk_level=req.risk_level, reason=req.reason)


@router.put("/{risk_id}", response_model=RiskRecordResponse)
def update_risk(risk_id: str, req: RiskRecordUpdate, db: Session = Depends(get_db)):
    repo = RiskRepository(db)
    risk = repo.get_by_id(risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="风险记录不存在")
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    return repo.update(risk, **update_data)
