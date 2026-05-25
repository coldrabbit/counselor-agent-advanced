# task-001-monthly-workbench Builder Report

## Summary

已实现月度工作台 MVP：

- 新增 `monthly_tasks` 数据模型、迁移、Schema、Repository、API。
- 新增 12 个月、8 类别的静态种子数据，并支持幂等插入。
- 新增 `/api/monthly-tasks?month=1..12` 查询端点。
- 新增 `MonthlyWorkbench.vue`，作为认证后默认首页。
- 保留原 `Home.vue`，新增 `/assistant` 作为 AI 助手入口。
- 复用 `PreGenerateDialog.vue` 和已有 `/api/notices/generate` 通知生成流程。
- 本地内存维护“标记完成”状态，刷新后重置。

## Files

### Created

- `backend/app/models/monthly_task.py`
- `backend/app/schemas/monthly_task.py`
- `backend/app/repositories/monthly_task.py`
- `backend/app/api/monthly_tasks.py`
- `backend/app/db/seed_monthly_tasks.py`
- `backend/alembic/versions/4dfc2d0f3a12_012_monthly_tasks.py`
- `backend/tests/test_api/test_monthly_tasks.py`
- `frontend/src/pages/MonthlyWorkbench.vue`
- `.agent/reports/task-001-builder-report.md`

### Modified

- `backend/app/main.py`
- `backend/app/models/__init__.py`
- `backend/app/repositories/__init__.py`
- `backend/alembic/env.py`
- `frontend/src/router/index.ts`
- `frontend/src/App.vue`

## Scope Control

- 未修改 `SPEC.md`。
- 未修改禁止文件：`backend/app/models/notice.py`、`backend/app/tasks/notice_task.py`、`backend/app/api/notices.py`、`backend/app/workflows/`、`backend/app/services/ai/client.py`、`backend/app/engine/`、`frontend/src/components/PreGenerateDialog.vue`、`frontend/src/stores/`。
- 未引入新第三方依赖。

## Verification

### Lint

- `ruff check ...`：未执行成功，当前环境无 `ruff` 命令（`zsh: command not found: ruff`）。
- `npm run lint -- src/pages/MonthlyWorkbench.vue`：未执行成功，`frontend/package.json` 无 `lint` 脚本。

### Typecheck

- `PYTHONPATH=backend python -c "from app.models.monthly_task import MonthlyTask; from app.schemas.monthly_task import MonthlyTaskResponse; print('ok')"`：通过，输出 `ok`。
- `cd frontend && npx vue-tsc --noEmit`：通过。

### Test

- `PYTHONPATH=backend pytest backend/tests/test_api/test_monthly_tasks.py -v`：通过，`6 passed`。
- `PYTHONPATH=backend pytest backend/tests/ -v`：通过，`60 passed, 111 warnings`。
- `npm run test`：未执行成功，`frontend/package.json` 无 `test` 脚本。

### Build

- `cd frontend && npm run build`：通过。Vite 输出既有依赖告警：`@vueuse/core` pure annotation warning 和 chunk size warning。
- `docker compose build`：未执行成功，当前环境无 `docker` 命令（`zsh: command not found: docker`）。

### Migration / Seed

- `PYTHONPATH=. alembic upgrade head`（backend 目录）：通过。
- `PYTHONPATH=. python -m app.db.seed_monthly_tasks`（backend 目录）：通过，输出 `monthly_tasks seed inserted: 0`，说明当前库已存在种子数据且幂等。

### Browser Verification

使用本地 FastAPI + Vite 服务做页面级验证：

- `/` 登录后显示“月度工作台”和当月任务。
- 桌面视口 1280px：首行 4 张卡片。
- 移动视口 390px：首行 1 张卡片。
- 点击“生成通知”：`PreGenerateDialog` 打开，事件描述预填。
- 点击“谈心提醒”：跳转 `/talk-record`。
- 点击“标记完成”：卡片显示完成态。
- 月份切换到 6 月后显示“端午假期安全提醒”。
- `/assistant` 可访问原 AI 助手首页。

本地浏览器验证中，普通 uvicorn startup 在当前沙箱未完成监听；已单独验证 startup 内部迁移/seed 逻辑可完成，并使用 `--lifespan off` 对已迁移/已 seed 的 SQLite 数据库完成页面验证。
