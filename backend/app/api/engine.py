from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.engine.graph import StateGraph
from app.engine.workflows import create_risk_workflow, create_notice_workflow_graph

router = APIRouter(prefix="/engine", tags=["engine"])

# 内存中的工作流实例（生产环境应持久化到数据库）
_active_workflows: dict[str, StateGraph] = {}


@router.post("/run/{workflow_type}")
def run_workflow(workflow_type: str, data: dict = {}):
    builders = {"risk": create_risk_workflow, "notice": create_notice_workflow_graph}
    if workflow_type not in builders:
        raise HTTPException(status_code=400, detail=f"Unknown workflow: {workflow_type}")

    wf_id = f"{workflow_type}_{len(_active_workflows)}"
    wf = builders[workflow_type]()
    result = wf.run(data)
    _active_workflows[wf_id] = wf
    return {"id": wf_id, **result}


@router.post("/resume/{wf_id}")
def resume_workflow(wf_id: str, action: str | None = None):
    wf = _active_workflows.get(wf_id)
    if not wf:
        raise HTTPException(status_code=404, detail="工作流不存在")
    result = wf.resume(action)
    return {"id": wf_id, **result}


@router.get("/status/{wf_id}")
def workflow_status(wf_id: str):
    wf = _active_workflows.get(wf_id)
    if not wf:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return wf.to_dict()
