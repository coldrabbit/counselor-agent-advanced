import json

from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.repositories.base import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    def __init__(self, db: Session):
        super().__init__(Workflow, db)

    def create_workflow(self, wf_type: str) -> Workflow:
        return self.create(type=wf_type, status="PENDING")

    def save_state(self, wf: Workflow, status: str, current_step: str, state_data: dict | None = None):
        data = {}
        if state_data:
            data = {k: str(v)[:500] for k, v in state_data.items()}
        return self.update(wf, status=status, current_step=current_step, state_data=json.dumps(data, ensure_ascii=False))

    def list_by_status(self, status: str | None = None):
        from sqlalchemy import select
        stmt = select(self.model)
        if status:
            stmt = stmt.where(Workflow.status == status)
        stmt = stmt.order_by(Workflow.created_at.desc())
        return self.db.scalars(stmt).all()
