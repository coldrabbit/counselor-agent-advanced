from sqlalchemy.orm import Session
from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(Task, db)

    def create_task(self, task_type: str, task_input: str, status: str = "RUNNING") -> Task:
        return self.create(type=task_type, input=task_input, status=status)

    def mark_success(self, task: Task, output: str, model: str, token_usage: int, duration_ms: int) -> Task:
        return self.update(task, status="SUCCESS", output=output, model=model,
                          token_usage=token_usage, duration_ms=duration_ms)

    def mark_failed(self, task: Task, error: str) -> Task:
        return self.update(task, status="FAILED", error=error)
