# SPEC: Monthly Workbench v2 (月度工作台增强)

## Summary

在 task-001 月度工作台基础上增加三个视图：本周优先事项、临近截止事项、AI 推荐下一步动作。页面从单一月份卡片列表升级为多层信息面板。

## Motivation

当前月度工作台展示 8 类 × 当月事项的扁平列表。辅导员需要快速识别"本周该做什么"和"什么快截止了"，以及 AI 主动推荐下一步。

## Input

- 当前月份（延续 task-001）
- 当前周数（系统计算）
- 任务完成状态（前端内存）

## Output

- **本月重点**：保留 task-001 的卡片网格
- **本周优先**：从当月事项中筛选本周应关注的 TOP 3
- **临近截止**：显示带 deadline 标记的事项（模拟数据）
- **AI 推荐**：调用 AI，基于月份 + 完成状态返回 2-3 条建议动作

## Functional Requirements

### FR-001: Weekly Priority Section
- 页面顶部新增"本周优先"横栏，展示 3 张高亮卡片
- 筛选逻辑：根据当前日期是当月第几周，从当月事项中选取 TOP 3
- TOP 3 规则：按 categoryOrder 排序取前 3 个未完成的 notice 类型事项
- 如果所有 notice 类型已完成 → 显示 talk 类型
- 如果当月事项不足 3 个 → 显示现有数量

### FR-002: Upcoming Deadline Section
- "临近截止"区域，展示带 deadline 的事项卡片
- deadline 来源：在 seed_monthly_tasks.py 中增加 `deadline_days` 字段（距月内第几天）
- 筛选逻辑：deadline_days ≤ 7 天（从今天算起，仅当月有效）
- 卡片显示倒计时标签（如"3天后"、"今天截止"）
- 如果本月无临近截止事项 → 显示"暂无临近截止事项"

### FR-003: AI Recommendation Section
- "AI 推荐下一步"区域，1-2 条 AI 生成的建议
- 调用新端点 `POST /api/workbench/recommend`
- 请求参数：当前月份、已完成事项 ID 列表
- AI 返回：2-3 条推荐动作（每条约 30 字），附带推荐理由
- 加载时显示骨架屏
- 失败时静默降级（不弹错误提示，仅不展示该区域）

### FR-004: Existing Cards Keep Working
- task-001 的月份切换、卡片操作（生成通知/谈心提醒/标记完成）保持不变
- 新增 UI 不破坏旧功能

### FR-005: Responsive
- 三个新增区域在移动端正常展示
- "本周优先"横栏在移动端改为纵向堆叠

## API Contract

### POST /api/workbench/recommend

Request:
```json
{
  "month": 5,
  "done_task_ids": ["uuid-1", "uuid-2"],
  "unread_task_ids": ["uuid-3", "uuid-4"]
}
```

Response:
```json
{
  "recommendations": [
    {"action": "建议本周完成防诈骗班会通知", "reason": "5月安全管理重点，尚未完成"}
  ]
}
```

## Data Model Change

### monthly_tasks 新增字段

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| deadline_days | INTEGER | null | 距月初第几天，null 表示无截止日 |

Seed data 更新：安全管理和日常管理类事项设置 deadline_days（3-25 不等），其他类别默认 null。

## Frontend / Backend Boundary

| 层 | 文件 | 操作 | 说明 |
|----|------|------|------|
| Frontend Page | `frontend/src/pages/MonthlyWorkbench.vue` | MODIFY | 新增三个 Section |
| Backend API | `backend/app/api/workbench.py` | NEW | recommend 端点 |
| Backend Router | `backend/app/main.py` | MODIFY | 注册 workbench 路由 |
| Backend Model | `backend/app/models/monthly_task.py` | MODIFY | 新增 deadline_days |
| Backend Migration | Alembic auto | NEW | 加列 migration |
| Backend Seed | `backend/app/db/seed_monthly_tasks.py` | MODIFY | 增加 deadline_days 数据 |
| Backend Test | `backend/tests/test_api/test_workbench.py` | NEW | recommend API 测试 |

## Acceptance Criteria

- [ ] AC-001: 工作台页面展示"本周优先"横栏，3 张高亮卡片
- [ ] AC-002: 工作台页面展示"临近截止"区域，带倒计时标签
- [ ] AC-003: 工作台页面展示"AI 推荐"区域，2-3 条建议
- [ ] AC-004: AI 推荐失败时静默降级，不影响页面其余功能
- [ ] AC-005: 移动端三区域正确堆叠
- [ ] AC-006: 旧功能（月份切换、卡片操作）不受影响
- [ ] AC-007: POST /api/workbench/recommend 返回正确的推荐格式
- [ ] AC-008: monthly_tasks 表新增 deadline_days 列，种子数据更新

## Constraints

- 不引入新第三方依赖
- 复用已有 PreGenerateDialog、noticeStore
- AI 推荐使用已有 DeepSeek API
- 推荐 Prompt 放在 `backend/app/prompts/workbench.py`

## Affected Files (Builder 可修改)

### 新建文件
- `backend/app/api/workbench.py`
- `backend/app/prompts/workbench.py`
- `backend/alembic/versions/xxx_monthly_tasks_deadline.py` (自动生成)
- `backend/tests/test_api/test_workbench.py`

### 可修改文件
- `backend/app/main.py` — 注册 workbench 路由
- `backend/app/models/monthly_task.py` — 新增 deadline_days 列
- `backend/app/db/seed_monthly_tasks.py` — 增加 deadline_days 数据
- `frontend/src/pages/MonthlyWorkbench.vue` — 新增三个 Section

### 冲突标记文件 (与 B-003 共享)
- `backend/app/main.py` — **冲突风险**，B-003 也需在此注册路由，合并时需同时包含两处修改

## Forbidden Files

- `backend/app/tasks/notice_task.py`
- `backend/app/workflows/`
- `backend/app/services/ai/client.py`
- `backend/app/engine/`
- `frontend/src/components/PreGenerateDialog.vue`
- `frontend/src/pages/NoticeGenerator.vue` — B-003 的文件，不要碰
- `frontend/src/stores/`

## Test Plan

| 测试 | 内容 |
|------|------|
| test_recommend_success | 正常请求返回 2-3 条推荐 |
| test_recommend_invalid_month | month=0 返回 422 |
| test_deadline_days_migration | 列存在，种子数据 deadline_days 正确 |
| test_weekly_priority_logic | 前端单元：本周筛选逻辑正确 |
| test_mobile_layout | 移动端断点三区域纵向堆叠 |
