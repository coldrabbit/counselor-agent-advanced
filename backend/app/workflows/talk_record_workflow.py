import logging
from app.workflows.base import BaseWorkflow
from app.tasks.talk_record_task import generate_talk_record_task

logger = logging.getLogger(__name__)


class TalkRecordWorkflow(BaseWorkflow):
    name = "talk_record"

    def __init__(self, student_name: str, student_id: str, situation: str,
                 counselor_profile: dict | None = None):
        super().__init__()
        self.ctx.data["student_name"] = student_name
        self.ctx.data["student_id"] = student_id
        self.ctx.data["situation"] = situation
        self.ctx.data["counselor_profile"] = counselor_profile
        self.ctx.data["status"] = "PENDING"

    def get_steps(self) -> list[str]:
        return ["INPUT_SITUATION", "AI_ANALYZING", "WAITING_REVIEW"]

    def execute_step(self, step_name: str) -> bool:
        if step_name == "INPUT_SITUATION":
            return bool(self.ctx.data["student_name"] and self.ctx.data["student_id"])
        elif step_name == "AI_ANALYZING":
            result = generate_talk_record_task(
                student_name=self.ctx.data["student_name"],
                student_id=self.ctx.data["student_id"],
                situation=self.ctx.data["situation"],
                counselor_profile=self.ctx.data.get("counselor_profile"),
            )
            self.ctx.data["ai_result"] = result
            if result.get("success"):
                self.ctx.data["status"] = "WAITING_APPROVAL"
                return True
            return False
        elif step_name == "WAITING_REVIEW":
            return self.ctx.data.get("ai_result") is not None
        return False

    def approve(self) -> dict:
        self.ctx.data["status"] = "APPROVED"
        return {"status": "APPROVED", "result": self.ctx.data.get("ai_result")}

    def reject(self) -> dict:
        self.ctx.data["status"] = "DRAFT"
        self.rollback()
        return {"status": "DRAFT"}
