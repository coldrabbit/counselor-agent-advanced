# 后端架构补全设计文档

**日期**：2026-05-25
**状态**：已确认
**版本**：1.0

---

## 目标

按 CLAUDE.md 和 PRD.md 要求，补全 Phase 1 MVP 缺失的后端模块：Alembic 迁移、Repositories 层、Workflows 模块、后端测试、Docker 部署、安全加固。

数据库继续使用 SQLite，后期可切换到 PostgreSQL（仅需改 DATABASE_URL）。

---

## 第 1 层：架构基础

### 1.1 Alembic 迁移配置

移除 `main.py` 中 `Base.metadata.create_all()`，改用 Alembic 管理数据库版本。

```
backend/
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py    # notices, tasks, counselor_profiles, talk_records
```

`alembic.ini` 中 `sqlalchemy.url` = `sqlite:///./counselor.db`

初始迁移使用 `--autogenerate` 从现有 Model 自动生成。

### 1.2 Repositories 层

```txt
backend/app/repositories/
├── __init__.py
├── base.py                # BaseRepository[ModelType]
├── notice.py
├── talk_record.py
├── counselor.py
└── task.py
```

BaseRepository 提供通用方法（get_by_id, list_all, create, update, delete），子类按需扩展。

### 1.3 Bug 修复

| 文件 | 问题 | 修复 |
|------|------|------|
| `schemas/__init__.py` | 导入 Model 而非 Schema | 改为导入 Pydantic Schema 类 |
| `services/ai/client.py` | `generate_notice()` 死代码 | 删除 |
| `api/notices.py` + `talk_records.py` | `_profile_to_dict()` 重复 | 移至 repository |

---

## 第 2 层：核心能力

### 2.1 Workflows 模块

```txt
backend/app/workflows/
├── __init__.py
├── base.py
├── notice_workflow.py
└── talk_record_workflow.py
```

NoticeWorkflow 状态机：

```
INPUT_EVENT → AI_GENERATING → WAITING_REVIEW → APPROVED / REJECTED
                                               ↘ SENT
```

### 2.2 后端测试

```txt
backend/tests/
├── conftest.py                    # fixtures（测试DB, TestClient）
├── test_api/
│   ├── test_notices.py
│   └── test_talk_records.py
├── test_tasks/
│   ├── test_notice_task.py
│   └── test_talk_record_task.py
└── test_workflows/
    └── test_notice_workflow.py
```

使用 pytest + FastAPI TestClient + 内存 SQLite。

---

## 第 3 层：交付准备

### 3.1 Docker 部署

```
backend/Dockerfile          # Python 3.12 + uvicorn
frontend/Dockerfile         # Node 构建 → nginx 服务
docker-compose.yml          # backend + frontend 编排
```

### 3.2 安全加固

- `.env` → 加入 `.gitignore`，创建 `.env.example`
- `*.db`、`__pycache__/` 等加入 `.gitignore`
- 用户需在 DeepSeek 控制台重新生成 API key

---

## 实施顺序

1. 安全加固（先保护现有代码）
2. Alembic 配置
3. Repositories 层
4. Bug 修复 + API 适配 repository
5. Workflows 模块 + API 适配 workflow
6. 后端测试
7. Docker 配置
