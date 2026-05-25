# SPEC: Monthly Workbench (月度工作台)

## Summary

新增"月度工作台"页面，作为辅导员登录后的首页。页面以卡片网格展示当月重点工作事项，用户可一键生成通知草稿或创建谈心提醒。MVP 数据为静态种子数据，覆盖 12 个月的高校辅导员工作清单。

## Motivation

当前首页 (`Home.vue`) 是通用 AI 问答，缺乏"辅导员视角"的工作流入口。月度工作台将首页从聊天形态转变为**任务驱动的工作面板**，符合 workflow-first 的设计原则。

## Input

- 当前月份（系统时间 → 自动匹配，用户可手动切换）
- 用户点击卡片触发操作

## Output

- 当月工作事项卡片列表
- 点击"生成通知" → 弹出 PreGenerateDialog → 调用已有 `/api/notices/generate`
- 点击"谈心提醒" → 跳转 `/talk-record` 页面
- 本地"标记完成"状态（不持久化，MVP 范围）

## Functional Requirements

### FR-001: Monthly Task Cards
- 页面根据当前月份（1-12）展示对应工作事项
- 支持手动切换月份
- 事项按类别分组：安全管理、学风建设、心理健康、资助管理、活动组织、党团建设、就业实习、日常管理

### FR-002: Quick Action — Generate Notice
- 卡片提供"生成通知"按钮
- 点击弹出复用已有组件 `PreGenerateDialog.vue`
- dialog 预填事件标题（从卡片数据填充）
- 确认后调用 `POST /api/notices/generate`
- 生成成功后提示用户可去通知页查看

### FR-003: Quick Action — Talk Record Reminder
- 卡片提供"谈心提醒"按钮
- 点击跳转 `/talk-record` 页面

### FR-004: Quick Action — Mark Done
- 卡片提供"标记完成"按钮
- 点击后卡片变为完成态（划线/降低透明度）
- 状态仅保存在前端内存（刷新后重置），MVP 不做持久化

### FR-005: Responsive Layout
- 桌面端：3-4 列卡片网格
- 平板端：2 列
- 移动端：1 列
- 使用 Element Plus 响应式栅格

### FR-006: Navigation
- 路由 `/workbench` 设为认证后默认首页（替换当前 `/` → `Home.vue` 的首页地位）
- 原 `Home.vue` 保留在 `/assistant` 作为 AI 助手
- 导航栏增加"工作台"入口，Home 改名为"AI 助手"

## API Contract

### GET /api/monthly-tasks

Query params:
- `month` (int, 1-12, required) — 月份

Response:
```json
[
  {
    "id": "uuid",
    "month": 5,
    "category": "安全管理",
    "title": "防诈骗安全教育",
    "description": "面向全体学生开展防诈骗主题班会，重点讲解刷单、网贷等常见骗局",
    "action_type": "notice",
    "action_label": "生成通知",
    "action_params": {
      "event": "防诈骗安全教育主题班会",
      "time": "",
      "location": "",
      "participants": "全体学生"
    }
  }
]
```

## Data Model

### monthly_tasks 表

| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) PK | UUID |
| month | INTEGER | 1-12 |
| category | VARCHAR(64) | 类别 |
| title | VARCHAR(256) | 事项标题 |
| description | TEXT | 事项说明 |
| action_type | VARCHAR(32) | notice / talk / todo |
| action_label | VARCHAR(64) | 按钮文案 |
| action_params | JSON | 预填参数 |

## Frontend / Backend Boundary

| 层 | 文件 | 说明 |
|----|------|------|
| Frontend Page | `frontend/src/pages/MonthlyWorkbench.vue` | 新建 |
| Frontend Route | `frontend/src/router/index.ts` | 修改：添加 `/workbench` 路由，调整首页默认 |
| Frontend Nav | `frontend/src/App.vue` | 修改：增加"工作台"链接，调整 AI 助手文案 |
| Backend Model | `backend/app/models/monthly_task.py` | 新建 |
| Backend Schema | `backend/app/schemas/monthly_task.py` | 新建 |
| Backend Repository | `backend/app/repositories/monthly_task.py` | 新建 |
| Backend API | `backend/app/api/monthly_tasks.py` | 新建 |
| Backend Seed | `backend/app/db/seed_monthly_tasks.py` | 新建 |
| Backend Migration | Alembic 自动生成 | 新建 |
| Backend Router | `backend/app/main.py` | 修改：注册路由 |

## Acceptance Criteria

- [ ] AC-001: 用户登录后首页为工作台，显示当前月份工作事项卡片
- [ ] AC-002: 月份切换器可用，切换后显示对应月份的事项
- [ ] AC-003: 点击"生成通知"弹出预填好的 PreGenerateDialog
- [ ] AC-004: 确认生成后成功调用 API 并创建通知
- [ ] AC-005: 点击"谈心提醒"正确跳转到谈心谈话页面
- [ ] AC-006: 点击"标记完成"卡片变为完成态 UI
- [ ] AC-007: 页面在移动端、平板、桌面端均正确布局
- [ ] AC-008: 旧首页 `/assistant` 仍可访问
- [ ] AC-009: 导航栏正确显示"工作台"和"AI 助手"

## Constraints

- 不引入新的第三方依赖
- 复用 `PreGenerateDialog.vue` 组件
- 复用已有 `/api/notices/generate` 接口
- 种子数据覆盖 12 个月，每类别 1-3 条
- 不实现复杂权限
- 完成状态不持久化（MVP 不做）

## Affected Files (Builder 可修改)

### 新建文件
- `backend/app/models/monthly_task.py`
- `backend/app/schemas/monthly_task.py`
- `backend/app/repositories/monthly_task.py`
- `backend/app/api/monthly_tasks.py`
- `backend/app/db/seed_monthly_tasks.py`
- `backend/alembic/versions/xxx_monthly_tasks.py` (自动生成)
- `frontend/src/pages/MonthlyWorkbench.vue`

### 可修改文件
- `backend/app/main.py` — 注册新路由
- `backend/app/repositories/__init__.py` — 导出新 Repository
- `frontend/src/router/index.ts` — 添加路由
- `frontend/src/App.vue` — 导航栏调整

## Forbidden Files (Builder 禁止修改)

- `backend/app/models/notice.py` — 核心模型，不允许改动
- `backend/app/tasks/notice_task.py` — 核心任务，不允许改动
- `backend/app/api/notices.py` — 核心 API，不允许改动
- `backend/app/workflows/` — 工作流引擎，不允许改动
- `backend/app/services/ai/client.py` — AI 服务，不允许改动
- `backend/app/engine/` — 引擎层，不允许改动
- `frontend/src/components/PreGenerateDialog.vue` — 复用即可，不修改
- `frontend/src/stores/` — 复用 stores，不修改

## Test Plan

| 测试 | 类型 | 内容 |
|------|------|------|
| test_monthly_tasks_api | 后端集成 | GET /api/monthly-tasks?month=5 返回正确数据；无效 month 返回 422 |
| test_seed_data | 后端单元 | 种子数据覆盖 12 个月，每条数据字段完整 |
| MonthlyWorkbench page | 前端 E2E | 卡片渲染、月份切换、操作按钮可见 |
| Notice generation flow | 集成 | 点击生成通知 → dialog 弹出 → 确认 → 通知创建成功 |
| Navigation | 集成 | 路由正确、导航栏链接正确 |
