from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.monthly_task import MonthlyTaskRepository
from app.schemas.monthly_task import MonthlyTaskResponse

router = APIRouter(prefix="/monthly-tasks", tags=["monthly-tasks"])


@router.get("", response_model=list[MonthlyTaskResponse])
def list_monthly_tasks(
    month: Annotated[int, Query(ge=1, le=12)],
    db: Session = Depends(get_db),
):
    return MonthlyTaskRepository(db).get_by_month(month)
