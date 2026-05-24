# Layer 1：架构基础 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）逐任务实现。步骤使用复选框（`- [ ]`）语法跟踪进度。

**目标：** 安全加固 + Alembic 迁移配置 + Repositories 层 + Bug 修复

**架构：** 添加 `.gitignore` 保护敏感文件，配置 Alembic 管理数据库版本，创建 Repository 泛型基类及 4 个子类，将 API 路由直接 SQLAlchemy 调用改为通过 Repository 访问，修复 schemas/__init__.py、死代码、代码重复。

**技术栈：** Python 3.12, SQLAlchemy 2.0, Alembic 1.14, FastAPI

---

### 任务 1：安全加固 — .gitignore + .env.example

**文件：**
- 创建：`.gitignore`
- 创建：`backend/.env.example`

- [ ] **步骤 1：创建根目录 .gitignore**

```gitignore
# 环境变量（含密钥）
.env

# 数据库文件
*.db

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Build
dist/
*.egg-info/

# Alembic
alembic/versions/*.pyc
```

- [ ] **步骤 2：创建 backend/.env.example**

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DATABASE_URL=sqlite:///./counselor.db
```

- [ ] **步骤 3：从 git 追踪中移除 .env**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced
git rm --cached backend/.env 2>/dev/null
git rm --cached backend/counselor.db 2>/dev/null
git rm --cached -r backend/app/__pycache__ 2>/dev/null
git rm --cached -r __pycache__ 2>/dev/null
```

- [ ] **步骤 4：Commit**

```bash
git add .gitignore backend/.env.example
git commit -m "chore: add .gitignore and .env.example, remove sensitive files from tracking"
```

---

### 任务 2：配置 Alembic 数据库迁移

**文件：**
- 创建：`backend/alembic.ini`
- 创建：`backend/alembic/env.py`
- 创建：`backend/alembic/script.py.mako`
- 修改：`backend/app/main.py:15-18`

- [ ] **步骤 1：创建 alembic.ini**

```ini
[alembic]
script_location = alembic
sqlalchemy.url = sqlite:///./counselor.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **步骤 2：创建 alembic/env.py**

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.db.database import Base
from app.models import Notice, Task, CounselorProfile, TalkRecord  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **步骤 3：创建 alembic/script.py.mako**

```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

- [ ] **步骤 4：生成初始迁移**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
pip install alembic
alembic revision --autogenerate -m "001_initial"
```

- [ ] **步骤 5：修改 main.py — 移除 create_all，添加 alembic 迁移**

在 `backend/app/main.py` 中，将：
```python
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
```
替换为：
```python
from alembic.config import Config
from alembic import command

@app.on_event("startup")
async def startup():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

- [ ] **步骤 6：运行迁移验证**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
alembic upgrade head
```
预期：输出 "Running upgrade -> 001_initial"

- [ ] **步骤 7：Commit**

```bash
git add backend/alembic.ini backend/alembic/ backend/app/main.py
git commit -m "feat: add Alembic migration setup, replace create_all with upgrade"
```

---

### 任务 3：创建 BaseRepository 泛型基类

**文件：**
- 创建：`backend/app/repositories/__init__.py`
- 创建：`backend/app/repositories/base.py`

- [ ] **步骤 1：创建 repositories/__init__.py**

```python
from app.repositories.base import BaseRepository
from app.repositories.notice import NoticeRepository
from app.repositories.talk_record import TalkRecordRepository
from app.repositories.counselor import CounselorRepository
from app.repositories.task import TaskRepository

__all__ = [
    "BaseRepository",
    "NoticeRepository",
    "TalkRecordRepository",
    "CounselorRepository",
    "TaskRepository",
]
```

- [ ] **步骤 2：创建 base.py**

```python
from typing import TypeVar, Generic, Optional, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """泛型 Repository 基类，封装通用 CRUD 操作。"""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: str) -> Optional[ModelType]:
        return self.db.get(self.model, id)

    def list_all(self, order_by=None) -> Sequence[ModelType]:
        stmt = select(self.model)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        return self.db.scalars(stmt).all()

    def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: ModelType) -> None:
        self.db.delete(instance)
        self.db.commit()
```

- [ ] **步骤 3：验证 import 无误**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "from app.repositories import BaseRepository; print('OK')"
```
预期：OK

- [ ] **步骤 4：Commit**

```bash
git add backend/app/repositories/
git commit -m "feat: add BaseRepository generic base class"
```

---

### 任务 4：创建 4 个具体 Repository

**文件：**
- 创建：`backend/app/repositories/notice.py`
- 创建：`backend/app/repositories/talk_record.py`
- 创建：`backend/app/repositories/counselor.py`
- 创建：`backend/app/repositories/task.py`

- [ ] **步骤 1：创建 notice.py**

```python
from sqlalchemy.orm import Session
from app.models.notice import Notice
from app.repositories.base import BaseRepository


class NoticeRepository(BaseRepository[Notice]):
    def __init__(self, db: Session):
        super().__init__(Notice, db)

    def list_all(self):
        return super().list_all(order_by=Notice.created_at.desc())

    def update_status(self, notice: Notice, status: str) -> Notice:
        return self.update(notice, status=status)
```

- [ ] **步骤 2：创建 talk_record.py**

```python
from sqlalchemy.orm import Session
from app.models.talk_record import TalkRecord
from app.repositories.base import BaseRepository


class TalkRecordRepository(BaseRepository[TalkRecord]):
    def __init__(self, db: Session):
        super().__init__(TalkRecord, db)

    def list_all(self):
        return super().list_all(order_by=TalkRecord.created_at.desc())

    def update_status(self, record: TalkRecord, status: str) -> TalkRecord:
        return self.update(record, status=status)
```

- [ ] **步骤 3：创建 counselor.py**

```python
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.counselor import CounselorProfile
from app.repositories.base import BaseRepository


class CounselorRepository(BaseRepository[CounselorProfile]):
    def __init__(self, db: Session):
        super().__init__(CounselorProfile, db)

    def get_first(self) -> Optional[CounselorProfile]:
        stmt = select(self.model).limit(1)
        return self.db.scalars(stmt).first()

    def upsert(self, **kwargs) -> CounselorProfile:
        existing = self.get_first()
        if existing:
            return self.update(existing, **kwargs)
        return self.create(**kwargs)

    def to_dict(self, profile: CounselorProfile) -> dict:
        return {
            "name": profile.name,
            "college": profile.college,
            "phone": profile.phone,
            "email": profile.email,
        }
```

- [ ] **步骤 4：创建 task.py**

```python
from sqlalchemy.orm import Session
from app.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: Session):
        super().__init__(Task, db)

    def create_task(
        self,
        task_type: str,
        task_input: str,
        status: str = "RUNNING",
    ) -> Task:
        return self.create(
            type=task_type,
            input=task_input,
            status=status,
        )

    def mark_success(
        self,
        task: Task,
        output: str,
        model: str,
        token_usage: int,
        duration_ms: int,
    ) -> Task:
        return self.update(
            task,
            status="SUCCESS",
            output=output,
            model=model,
            token_usage=token_usage,
            duration_ms=duration_ms,
        )

    def mark_failed(self, task: Task, error: str) -> Task:
        return self.update(task, status="FAILED", error=error)
```

- [ ] **步骤 5：验证 import**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "from app.repositories import NoticeRepository, TalkRecordRepository, CounselorRepository, TaskRepository; print('OK')"
```
预期：OK

- [ ] **步骤 6：Commit**

```bash
git add backend/app/repositories/
git commit -m "feat: add Notice, TalkRecord, Counselor, Task repositories"
```

---

### 任务 5：改造 API 路由使用 Repository + 修复 Bug

**文件：**
- 修改：`backend/app/api/notices.py`
- 修改：`backend/app/api/talk_records.py`
- 修改：`backend/app/api/counselor.py`
- 修改：`backend/app/schemas/__init__.py`
- 修改：`backend/app/services/ai/client.py`

- [ ] **步骤 1：修复 schemas/__init__.py**

当前内容导入的是 Model 而非 Schema。将：
```python
from app.models import Notice, Task
```
改为：
```python
from app.schemas.notice import GenerateNoticeRequest, NoticeResponse, NoticeListItem
from app.schemas.talk_record import GenerateTalkRecordRequest, TalkRecordResponse, TalkRecordListItem
from app.schemas.counselor import CounselorProfileRequest, CounselorProfileResponse
```

- [ ] **步骤 2：删除 AIService.generate_notice 死代码**

在 `services/ai/client.py` 中，删除 `generate_notice` 方法（大约第 70-110 行，包含 JSON 解析逻辑的方法体）。

- [ ] **步骤 3：改造 api/notices.py**

关键改动：
- 注入 `NoticeRepository`, `TaskRepository`, `CounselorRepository`
- 使用 repository 方法替代直接 session 操作
- 删除 `_profile_to_dict()` 函数（改用 `CounselorRepository.to_dict()`）

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.notice import GenerateNoticeRequest, NoticeResponse, NoticeListItem
from app.repositories import NoticeRepository, TaskRepository, CounselorRepository
from app.tasks.notice_task import generate_notice_task
import json

router = APIRouter(prefix="/notices", tags=["notices"])


@router.post("/generate", response_model=NoticeResponse)
def generate_notice(req: GenerateNoticeRequest, db: Session = Depends(get_db)):
    notice_repo = NoticeRepository(db)
    task_repo = TaskRepository(db)
    counselor_repo = CounselorRepository(db)

    profile = counselor_repo.get_first()
    profile_dict = counselor_repo.to_dict(profile) if profile else None

    task = task_repo.create_task(
        task_type="generate_notice",
        task_input=req.event,
    )

    result = generate_notice_task(
        event=req.event,
        time=req.time or "",
        location=req.location or "",
        participants=req.participants or "",
        counselor_profile=profile_dict,
    )

    if result.get("success"):
        notice_data = result["notice"]
        notice = notice_repo.create(
            title=notice_data["title"],
            event=req.event,
            formal_notice=notice_data.get("formal_notice", ""),
            wechat_notice=notice_data.get("wechat_notice", ""),
            parent_notice=notice_data.get("parent_notice", ""),
            sms_notice=notice_data.get("sms_notice", ""),
            status="WAITING_APPROVAL",
        )
        task_repo.mark_success(
            task,
            output=json.dumps(notice_data, ensure_ascii=False),
            model=result.get("model", ""),
            token_usage=result.get("token_usage", 0),
            duration_ms=result.get("duration_ms", 0),
        )
        return notice
    else:
        task_repo.mark_failed(task, result.get("error", "Unknown error"))
        raise HTTPException(status_code=500, detail=result.get("error", "生成失败"))


@router.get("", response_model=list[NoticeListItem])
def list_notices(db: Session = Depends(get_db)):
    return NoticeRepository(db).list_all()


@router.get("/{notice_id}", response_model=NoticeResponse)
def get_notice(notice_id: str, db: Session = Depends(get_db)):
    notice = NoticeRepository(db).get_by_id(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    return notice


@router.put("/{notice_id}/approve", response_model=NoticeResponse)
def approve_notice(notice_id: str, db: Session = Depends(get_db)):
    repo = NoticeRepository(db)
    notice = repo.get_by_id(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    return repo.update_status(notice, "APPROVED")


@router.put("/{notice_id}/reject", response_model=NoticeResponse)
def reject_notice(notice_id: str, db: Session = Depends(get_db)):
    repo = NoticeRepository(db)
    notice = repo.get_by_id(notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="通知不存在")
    return repo.update_status(notice, "DRAFT")
```

- [ ] **步骤 4：改造 api/talk_records.py（同样模式）**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.talk_record import GenerateTalkRecordRequest, TalkRecordResponse, TalkRecordListItem
from app.repositories import TalkRecordRepository, TaskRepository, CounselorRepository
from app.tasks.talk_record_task import generate_talk_record_task
import json

router = APIRouter(prefix="/talk-records", tags=["talk_records"])


@router.post("/generate", response_model=TalkRecordResponse)
def generate_talk_record(req: GenerateTalkRecordRequest, db: Session = Depends(get_db)):
    record_repo = TalkRecordRepository(db)
    task_repo = TaskRepository(db)
    counselor_repo = CounselorRepository(db)

    profile = counselor_repo.get_first()
    profile_dict = counselor_repo.to_dict(profile) if profile else None

    task = task_repo.create_task(
        task_type="generate_talk_record",
        task_input=req.situation,
    )

    result = generate_talk_record_task(
        student_name=req.student_name,
        student_id=req.student_id,
        situation=req.situation,
        counselor_profile=profile_dict,
    )

    if result.get("success"):
        data = result["record"]
        record = record_repo.create(
            student_name=req.student_name,
            student_id=req.student_id,
            situation=req.situation,
            conversation_record=data.get("conversation_record", ""),
            risk_level=data.get("risk_level", "medium"),
            follow_up_advice=data.get("follow_up_advice", ""),
            parent_advice=data.get("parent_advice", ""),
            status="WAITING_APPROVAL",
        )
        task_repo.mark_success(
            task,
            output=json.dumps(data, ensure_ascii=False),
            model=result.get("model", ""),
            token_usage=result.get("token_usage", 0),
            duration_ms=result.get("duration_ms", 0),
        )
        return record
    else:
        task_repo.mark_failed(task, result.get("error", "Unknown error"))
        raise HTTPException(status_code=500, detail=result.get("error", "生成失败"))


@router.get("", response_model=list[TalkRecordListItem])
def list_talk_records(db: Session = Depends(get_db)):
    return TalkRecordRepository(db).list_all()


@router.get("/{record_id}", response_model=TalkRecordResponse)
def get_talk_record(record_id: str, db: Session = Depends(get_db)):
    record = TalkRecordRepository(db).get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="谈话记录不存在")
    return record


@router.put("/{record_id}/approve", response_model=TalkRecordResponse)
def approve_talk_record(record_id: str, db: Session = Depends(get_db)):
    repo = TalkRecordRepository(db)
    record = repo.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="谈话记录不存在")
    return repo.update_status(record, "APPROVED")


@router.put("/{record_id}/reject", response_model=TalkRecordResponse)
def reject_talk_record(record_id: str, db: Session = Depends(get_db)):
    repo = TalkRecordRepository(db)
    record = repo.get_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="谈话记录不存在")
    return repo.update_status(record, "DRAFT")
```

- [ ] **步骤 5：改造 api/counselor.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.counselor import CounselorProfileRequest, CounselorProfileResponse
from app.repositories import CounselorRepository

router = APIRouter(prefix="/counselor", tags=["counselor"])


@router.get("/profile", response_model=CounselorProfileResponse)
def get_profile(db: Session = Depends(get_db)):
    repo = CounselorRepository(db)
    profile = repo.get_first()
    return profile


@router.put("/profile", response_model=CounselorProfileResponse)
def save_profile(req: CounselorProfileRequest, db: Session = Depends(get_db)):
    repo = CounselorRepository(db)
    profile = repo.upsert(
        name=req.name,
        college=req.college,
        phone=req.phone or "",
        email=req.email or "",
    )
    return profile
```

- [ ] **步骤 6：验证构建**

```bash
cd /Users/songjie/mine/code/counselor-agent-advanced/backend
python -c "from app.main import app; print('FastAPI app loaded successfully')"
```
预期：FastAPI app loaded successfully

- [ ] **步骤 7：Commit**

```bash
git add backend/app/api/ backend/app/schemas/__init__.py backend/app/services/ai/client.py
git commit -m "refactor: adapt API routes to use repositories, fix schema imports, remove dead code"
```
