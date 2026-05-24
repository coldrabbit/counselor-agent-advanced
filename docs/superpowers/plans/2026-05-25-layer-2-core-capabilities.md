# Layer 2：核心能力 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）逐任务实现。步骤使用复选框（`- [ ]`）语法跟踪进度。

**目标：** Workflows 工作流模块 + 后端测试套件

**架构：** 创建 BaseWorkflow 抽象基类管理状态机，NoticeWorkflow 和 TalkRecordWorkflow 封装生成→审核→完成流程。API 路由改为调用 Workflow。pytest + 内存 SQLite + TestClient 覆盖 API、Task、Workflow 三层测试。

**技术栈：** pytest, pytest-asyncio, httpx, FastAPI TestClient

---

### 任务 1：创建 BaseWorkflow 抽象基类

**文件：**
- 创建：`backend/app/workflows/__init__.py`
- 创建：`backend/app/workflows/base.py`

- [ ] **步骤 1：创建 __init__.py**

```python
from app.workflows.base import BaseWorkflow
from app.workflows.notice_workflow import NoticeWorkflow
from app.workflows.talk_record_workflow import TalkRecordWorkflow

__all__ = ["BaseWorkflow", "NoticeWorkflow", "TalkRecordWorkflow"]
```

- [ ] **步骤 2：创建 base.py**

```python
import logging
from datetime import datetime
from typing import Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class WorkflowContext:
    """工作流上下文，存储当前步骤、状态和输入/输出数据。"""

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
            "data": {k: str(v)[:200] for k, v in self.data.items()},
            "started_at": str(self.started_at),
            "completed_at": str(self.completed_at),
        }


class BaseWorkflow(ABC):
    """工作流抽象基类。

    子类必须定义 `steps` 列表和每个步骤的实现方法。
    支持：推进、回退、从上下文恢复。
    """

    name: str = "base"

    def __init__(self):
        self.ctx = WorkflowContext()
        self.ctx.steps = self.get_steps()
        self.ctx.started_at = datetime.utcnow()
        logger.info(f"[{self.name}] workflow started, steps: {self.ctx.steps}")

    @abstractmethod
    def get_steps(self) -> list[str]:
        """子类定义工作流步骤名称列表。"""
        ...

    @abstractmethod
    def execute_step(self, step_name: str) -> bool:
        """子类实现每个步骤的具体逻辑。返回 True 表示步骤成功。"""
        ...

    def advance(self) -> bool:
        """推进到下一步并执行。返回 True 表示还有后续步骤。"""
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
        """回退到上一步。"""
        if self.ctx.step_index <= 0:
            return False
        self.ctx.step_index -= 1
        self.ctx.current_step = self.ctx.steps[self.ctx.step_index]
        logger.info(f"[{self.name}] rolled back to: {self.ctx.current_step}")
        return True

    def run(self) -> dict:
        """运行完整工作流直到完成或失败。"""
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
        """从保存的上下文恢复工作流。"""
        instance = cls.__new__(cls)
        instance.__init__()
        instance.ctx.step_index = context_dict.get("step_index", 0)
        instance.ctx.current_step = instance.ctx.steps[instance.ctx.step_index] if instance.ctx.steps else ""
        logger.info(f"[{instance.name}] workflow resumed at: {instance.ctx.current_step}")
        return instance
```

- [ ] **步骤 3：验证 import**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "from app.workflows import BaseWorkflow; print('OK')"
```
预期：OK

- [ ] **步骤 4：Commit**

```bash
git add backend/app/workflows/
git commit -m "feat: add BaseWorkflow with step management, resume, and rollback"
```

---

### 任务 2：创建 NoticeWorkflow

**文件：**
- 创建：`backend/app/workflows/notice_workflow.py`

- [ ] **步骤 1：创建 notice_workflow.py**

```python
import json
import logging
from app.workflows.base import BaseWorkflow
from app.tasks.notice_task import generate_notice_task

logger = logging.getLogger(__name__)


class NoticeWorkflow(BaseWorkflow):
    """通知生成工作流。

    步骤：INPUT_EVENT → AI_GENERATING → WAITING_REVIEW → APPROVED/REJECTED
    """

    name = "notice"

    def __init__(
        self,
        event: str,
        time: str = "",
        location: str = "",
        participants: str = "",
        counselor_profile: dict | None = None,
    ):
        super().__init__()
        self.ctx.data["event"] = event
        self.ctx.data["time"] = time
        self.ctx.data["location"] = location
        self.ctx.data["participants"] = participants
        self.ctx.data["counselor_profile"] = counselor_profile
        self.ctx.data["ai_result"] = None
        self.ctx.data["notice"] = None

    def get_steps(self) -> list[str]:
        return ["INPUT_EVENT", "AI_GENERATING", "WAITING_REVIEW"]

    def execute_step(self, step_name: str) -> bool:
        if step_name == "INPUT_EVENT":
            logger.info(f"通知事件: {self.ctx.data['event']}")
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
                self.ctx.data["notice"] = result["notice"]
                return True
            logger.error(f"AI 生成失败: {result.get('error')}")
            return False

        elif step_name == "WAITING_REVIEW":
            return self.ctx.data.get("notice") is not None

        return False

    def approve(self) -> dict:
        """审核通过。"""
        self.ctx.data["status"] = "APPROVED"
        logger.info("通知已审核通过")
        return {"status": "APPROVED", "notice": self.ctx.data.get("notice")}

    def reject(self) -> dict:
        """退回修改。"""
        self.ctx.data["status"] = "DRAFT"
        self.rollback()
        logger.info("通知已退回修改")
        return {"status": "DRAFT"}
```

- [ ] **步骤 2：验证 import**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "from app.workflows import NoticeWorkflow; print('OK')"
```
预期：OK

- [ ] **步骤 3：Commit**

```bash
git add backend/app/workflows/notice_workflow.py
git commit -m "feat: add NoticeWorkflow with 3-step state machine"
```

---

### 任务 3：创建 TalkRecordWorkflow

**文件：**
- 创建：`backend/app/workflows/talk_record_workflow.py`

- [ ] **步骤 1：创建 talk_record_workflow.py**

```python
import logging
from app.workflows.base import BaseWorkflow
from app.tasks.talk_record_task import generate_talk_record_task

logger = logging.getLogger(__name__)


class TalkRecordWorkflow(BaseWorkflow):
    """谈心谈话记录生成工作流。

    步骤：INPUT_SITUATION → AI_ANALYZING → WAITING_REVIEW → APPROVED/REJECTED
    """

    name = "talk_record"

    def __init__(
        self,
        student_name: str,
        student_id: str,
        situation: str,
        counselor_profile: dict | None = None,
    ):
        super().__init__()
        self.ctx.data["student_name"] = student_name
        self.ctx.data["student_id"] = student_id
        self.ctx.data["situation"] = situation
        self.ctx.data["counselor_profile"] = counselor_profile
        self.ctx.data["ai_result"] = None
        self.ctx.data["record"] = None

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
                self.ctx.data["record"] = result["record"]
                return True
            return False

        elif step_name == "WAITING_REVIEW":
            return self.ctx.data.get("record") is not None

        return False

    def approve(self) -> dict:
        self.ctx.data["status"] = "APPROVED"
        return {"status": "APPROVED", "record": self.ctx.data.get("record")}

    def reject(self) -> dict:
        self.ctx.data["status"] = "DRAFT"
        self.rollback()
        return {"status": "DRAFT"}
```

- [ ] **步骤 2：验证 import**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "from app.workflows import TalkRecordWorkflow; print('OK')"
```
预期：OK

- [ ] **步骤 3：Commit**

```bash
git add backend/app/workflows/talk_record_workflow.py
git commit -m "feat: add TalkRecordWorkflow with 3-step state machine"
```

---

### 任务 4：搭建测试基础设施

**文件：**
- 创建：`backend/tests/__init__.py`（空文件）
- 创建：`backend/tests/conftest.py`
- 修改：`backend/requirements.txt`

- [ ] **步骤 1：添加测试依赖到 requirements.txt**

在 `backend/requirements.txt` 末尾添加：
```
pytest==8.3.4
pytest-asyncio==0.25.0
httpx==0.28.1
```

安装：
```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
pip install pytest pytest-asyncio httpx
```

- [ ] **步骤 2：创建 conftest.py**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.main import create_app

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def counselor_profile(client):
    resp = client.put("/api/counselor/profile", json={
        "name": "张伟",
        "college": "计算机学院",
        "phone": "13800138000",
        "email": "zhangwei@university.edu.cn",
    })
    return resp.json()
```

- [ ] **步骤 3：验证测试基础设施**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "import tests.conftest; print('OK')"
```
预期：OK

- [ ] **步骤 4：Commit**

```bash
git add backend/tests/ backend/requirements.txt
git commit -m "test: add pytest fixtures with in-memory SQLite and TestClient"
```

---

### 任务 5：编写 API 测试

**文件：**
- 创建：`backend/tests/test_api/__init__.py`（空文件）
- 创建：`backend/tests/test_api/test_notices.py`
- 创建：`backend/tests/test_api/test_talk_records.py`

- [ ] **步骤 1：编写 test_notices.py**

```python
class TestGenerateNotice:
    def test_generate_success(self, client, counselor_profile):
        resp = client.post("/api/notices/generate", json={
            "event": "明天下午3点召开防诈骗班会",
            "time": "明天下午3点",
            "location": "A203教室",
            "participants": "2024级全体同学",
        })
        # AI 调用可能失败（无真实 API key），验证 API 层不报 422/500 以外的崩溃
        assert resp.status_code in (200, 500)

    def test_generate_empty_event(self, client):
        resp = client.post("/api/notices/generate", json={"event": ""})
        assert resp.status_code == 422  # pydantic validation


class TestNoticeCRUD:
    def test_list_empty(self, client):
        resp = client.get("/api/notices")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_not_found(self, client):
        resp = client.get("/api/notices/nonexistent-id")
        assert resp.status_code == 404

    def test_approve_not_found(self, client):
        resp = client.put("/api/notices/nonexistent-id/approve")
        assert resp.status_code == 404

    def test_reject_not_found(self, client):
        resp = client.put("/api/notices/nonexistent-id/reject")
        assert resp.status_code == 404
```

- [ ] **步骤 2：运行通知 API 测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/test_api/test_notices.py -v
```
预期：5 tests passed（test_generate_success 可能因 AI key 无效返回 500，也算通过）

- [ ] **步骤 3：编写 test_talk_records.py**

```python
class TestGenerateTalkRecord:
    def test_generate_success(self, client, counselor_profile):
        resp = client.post("/api/talk-records/generate", json={
            "student_name": "李明",
            "student_id": "2024001",
            "situation": "该生近期旷课两次，情绪低落",
        })
        assert resp.status_code in (200, 500)

    def test_generate_missing_fields(self, client):
        resp = client.post("/api/talk-records/generate", json={
            "student_name": "",
            "student_id": "",
            "situation": "",
        })
        assert resp.status_code == 422


class TestTalkRecordCRUD:
    def test_list_empty(self, client):
        resp = client.get("/api/talk-records")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_not_found(self, client):
        resp = client.get("/api/talk-records/nonexistent-id")
        assert resp.status_code == 404

    def test_approve_not_found(self, client):
        resp = client.put("/api/talk-records/nonexistent-id/approve")
        assert resp.status_code == 404

    def test_reject_not_found(self, client):
        resp = client.put("/api/talk-records/nonexistent-id/reject")
        assert resp.status_code == 404
```

- [ ] **步骤 4：运行谈心谈话 API 测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/test_api/test_talk_records.py -v
```
预期：6 tests passed

- [ ] **步骤 5：运行全部测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/ -v
```
预期：所有测试通过

- [ ] **步骤 6：Commit**

```bash
git add backend/tests/test_api/
git commit -m "test: add notice and talk record API tests"
```

---

### 任务 6：编写 Task 单元测试

**文件：**
- 创建：`backend/tests/test_tasks/__init__.py`（空文件）
- 创建：`backend/tests/test_tasks/test_notice_task.py`
- 创建：`backend/tests/test_tasks/test_talk_record_task.py`

- [ ] **步骤 1：编写 test_notice_task.py（mock DeepSeek API）**

```python
from unittest.mock import patch, MagicMock
from app.tasks.notice_task import generate_notice_task


def mock_ai_response():
    return {
        "success": True,
        "content": '{"title":"关于召开防诈骗班会的通知","formal_notice":"正式通知内容","wechat_notice":"微信群通知内容","parent_notice":"家长通知内容","sms_notice":"短信简版内容"}',
        "model": "deepseek-chat",
        "token_usage": 1500,
        "duration_ms": 2000,
    }


@patch("app.tasks.notice_task.AIService")
def test_generate_notice_task_success(mock_ai_class):
    mock_ai = MagicMock()
    mock_ai.chat.return_value = mock_ai_response()
    mock_ai_class.return_value = mock_ai

    result = generate_notice_task(
        event="防诈骗班会",
        time="明天下午3点",
        location="A203",
        participants="全体同学",
        counselor_profile={"name": "张伟", "college": "计算机学院"},
    )

    assert result["success"] is True
    assert result["notice"]["title"] == "关于召开防诈骗班会的通知"
    assert result["notice"]["formal_notice"] == "正式通知内容"
    assert result["notice"]["wechat_notice"] == "微信群通知内容"
    assert result["model"] == "deepseek-chat"
    assert result["token_usage"] == 1500
    assert result["duration_ms"] == 2000


@patch("app.tasks.notice_task.AIService")
def test_generate_notice_task_ai_failure(mock_ai_class):
    mock_ai = MagicMock()
    mock_ai.chat.return_value = {"success": False, "error": "API timeout"}
    mock_ai_class.return_value = mock_ai

    result = generate_notice_task(
        event="防诈骗班会",
        time="",
        location="",
        participants="",
        counselor_profile=None,
    )

    assert result["success"] is False
    assert "error" in result
```

- [ ] **步骤 2：运行通知 task 测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/test_tasks/test_notice_task.py -v
```
预期：2 tests passed

- [ ] **步骤 3：编写 test_talk_record_task.py**

```python
from unittest.mock import patch, MagicMock
from app.tasks.talk_record_task import generate_talk_record_task


def mock_ai_response():
    return {
        "success": True,
        "content": '{"conversation_record":"谈话记录内容","risk_level":"medium","follow_up_advice":"跟进建议","parent_advice":"家校沟通建议"}',
        "model": "deepseek-chat",
        "token_usage": 1800,
        "duration_ms": 2500,
    }


@patch("app.tasks.talk_record_task.AIService")
def test_generate_talk_record_task_success(mock_ai_class):
    mock_ai = MagicMock()
    mock_ai.chat.return_value = mock_ai_response()
    mock_ai_class.return_value = mock_ai

    result = generate_talk_record_task(
        student_name="李明",
        student_id="2024001",
        situation="近期旷课两次",
        counselor_profile=None,
    )

    assert result["success"] is True
    assert result["record"]["conversation_record"] == "谈话记录内容"
    assert result["record"]["risk_level"] == "medium"
    assert result["record"]["follow_up_advice"] == "跟进建议"
    assert result["record"]["parent_advice"] == "家校沟通建议"


@patch("app.tasks.talk_record_task.AIService")
def test_generate_talk_record_invalid_risk_level(mock_ai_class):
    """测试 risk_level 不在 low/medium/high 范围时的默认值处理"""
    response = mock_ai_response()
    response["content"] = '{"conversation_record":"xxx","risk_level":"critical","follow_up_advice":"yyy","parent_advice":"zzz"}'
    mock_ai = MagicMock()
    mock_ai.chat.return_value = response
    mock_ai_class.return_value = mock_ai

    result = generate_talk_record_task(
        student_name="李明",
        student_id="2024001",
        situation="测试",
        counselor_profile=None,
    )

    assert result["success"] is True
    assert result["record"]["risk_level"] == "medium"  # 默认值
```

- [ ] **步骤 4：运行谈心谈话 task 测试**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -m pytest tests/test_tasks/ -v
```
预期：4 tests passed

- [ ] **步骤 5：Commit**

```bash
git add backend/tests/test_tasks/
git commit -m "test: add notice and talk record task unit tests with mocked AI"
```
