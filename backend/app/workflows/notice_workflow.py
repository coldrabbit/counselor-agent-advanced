import logging
from app.workflows.base import BaseWorkflow
from app.tasks.notice_task import generate_notice_task

logger = logging.getLogger(__name__)


class NoticeWorkflow(BaseWorkflow):
    name = "notice"

    def __init__(self, event: str, time: str = "", location: str = "",
                 participants: str = "", counselor_profile: dict | None = None):
        super().__init__()
        self.ctx.data["event"] = event
        self.ctx.data["time"] = time
        self.ctx.data["location"] = location
        self.ctx.data["participants"] = participants
        self.ctx.data["counselor_profile"] = counselor_profile
        self.ctx.data["status"] = "PENDING"

    def get_steps(self) -> list[str]:
        return ["INPUT_EVENT", "AI_GENERATING", "WAITING_REVIEW"]

    def execute_step(self, step_name: str) -> bool:
        if step_name == "INPUT_EVENT":
            return bool(self.ctx.data["event"])
        elif step_name == "AI_GENERATING":
            result = generate_notice_task(
                event=self.ctx.data["event"],
                time=self.ctx.data.get("time", ""),
                location=self.ctx.data.get("location", ""),
                participants=self.ctx.data.get("participants", ""),
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
