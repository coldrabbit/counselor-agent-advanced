import logging
from datetime import datetime
from typing import Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class WorkflowContext:
    def __init__(self):
        self.steps: list[str] = []
        self.current_step: str = ""
        self.step_index: int = -1
        self.data: dict[str, Any] = {}
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "steps": self.steps,
            "current_step": self.current_step,
            "step_index": self.step_index,
            "data": self.data,
            "started_at": str(self.started_at),
            "completed_at": str(self.completed_at),
        }


class BaseWorkflow(ABC):
    name: str = "base"

    def __init__(self):
        self.ctx = WorkflowContext()
        self.ctx.steps = self.get_steps()
        self.ctx.started_at = datetime.utcnow()
        logger.info(f"[{self.name}] workflow started, steps: {self.ctx.steps}")

    @abstractmethod
    def get_steps(self) -> list[str]:
        ...

    @abstractmethod
    def execute_step(self, step_name: str) -> bool:
        ...

    def advance(self) -> bool:
        self.ctx.step_index += 1
        if self.ctx.step_index >= len(self.ctx.steps):
            self.ctx.completed_at = datetime.utcnow()
            logger.info(f"[{self.name}] workflow completed")
            return False
        self.ctx.current_step = self.ctx.steps[self.ctx.step_index]
        logger.info(f"[{self.name}] executing step: {self.ctx.current_step}")
        success = self.execute_step(self.ctx.current_step)
        if not success:
            logger.error(f"[{self.name}] step failed: {self.ctx.current_step}")
        return success and (self.ctx.step_index + 1 < len(self.ctx.steps))

    def rollback(self) -> bool:
        if self.ctx.step_index <= 0:
            return False
        self.ctx.step_index -= 1
        self.ctx.current_step = self.ctx.steps[self.ctx.step_index]
        logger.info(f"[{self.name}] rolled back to: {self.ctx.current_step}")
        return True

    def run(self) -> dict:
        try:
            for _ in self.ctx.steps:
                has_more = self.advance()
                if not has_more:
                    break
            return {"success": True, "context": self.ctx.to_dict()}
        except Exception as e:
            logger.exception(f"[{self.name}] workflow error: {e}")
            return {"success": False, "error": str(e), "context": self.ctx.to_dict()}

    @classmethod
    def resume(cls, context_dict: dict) -> "BaseWorkflow":
        instance = cls.__new__(cls)
        instance.__init__()
        instance.ctx.step_index = context_dict.get("step_index", 0)
        if instance.ctx.steps:
            instance.ctx.current_step = instance.ctx.steps[instance.ctx.step_index]
        logger.info(f"[{instance.name}] workflow resumed at: {instance.ctx.current_step}")
        return instance
