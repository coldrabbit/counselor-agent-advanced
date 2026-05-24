import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.workflow import WorkflowRepository
from app.engine.workflows import create_risk_workflow, create_notice_workflow_graph

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("")
def list_workflows(status: str | None = Query(None), db: Session = Depends(get_db)):
    return WorkflowRepository(db).list_by_status(status=status)


@router.post("/run/{wf_type}")
def run_workflow(wf_type: str, data: dict = {}, db: Session = Depends(get_db)):
    builders = {"risk": create_risk_workflow, "notice": create_notice_workflow_graph}
    if wf_type not in builders:
        raise HTTPException(status_code=400, detail=f"Unknown workflow: {wf_type}")

    repo = WorkflowRepository(db)
    wf_record = repo.create_workflow(wf_type)

    wf = builders[wf_type]()
    result = wf.run(data)

    repo.save_state(wf_record, result["status"], result["current_node"], result.get("data"))
    return {"id": wf_record.id, **result}


@router.post("/resume/{wf_id}")
def resume_workflow(wf_id: str, action: str | None = None, db: Session = Depends(get_db)):
    repo = WorkflowRepository(db)
    wf_record = repo.get_by_id(wf_id)
    if not wf_record:
        raise HTTPException(status_code=404, detail="工作流不存在")

    builders = {"risk": create_risk_workflow, "notice": create_notice_workflow_graph}
    wf = builders[wf_record.type]()

    if wf_record.state_data:
        try:
            wf.state.data = json.loads(wf_record.state_data)
        except Exception:
            pass

    result = wf.resume(action)
    repo.save_state(wf_record, result["status"], result["current_node"], result.get("data"))
    return {"id": wf_id, **result}


@router.get("/{wf_id}")
def get_workflow(wf_id: str, db: Session = Depends(get_db)):
    wf = WorkflowRepository(db).get_by_id(wf_id)
    if not wf:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return {
        "id": wf.id,
        "type": wf.type,
        "status": wf.status,
        "current_step": wf.current_step,
        "created_at": str(wf.created_at),
    }
