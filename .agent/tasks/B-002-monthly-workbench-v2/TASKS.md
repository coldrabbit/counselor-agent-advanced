# TASKS: Monthly Workbench v2 (月度工作台增强)

## Dependencies

- 依赖 task-001 的 MonthlyWorkbench.vue 基座
- 与 B-003 共享 `backend/app/main.py` 路由注册（冲突文件，需协调合并顺序）

---

## Step 1: Backend — monthly_tasks 模型增加 deadline_days

**Files:**
- `backend/app/models/monthly_task.py` — MODIFY：新增 `deadline_days: Mapped[int | None]`
- Alembic migration — 自动生成

**Description:**
在 MonthlyTask 模型增加 `deadline_days = mapped_column(Integer, nullable=True, default=None)`，生成 Alembic 迁移。

**Verify:**
- `alembic upgrade head` 成功
- `python -c "from app.models.monthly_task import MonthlyTask; print(MonthlyTask.__table__.columns.keys())"` 包含 deadline_days

---

## Step 2: Backend — 种子数据增加 deadline_days

**Files:**
- `backend/app/db/seed_monthly_tasks.py` — MODIFY

**Description:**
- 在 MONTHLY_WORK_ITEMS 的 tuple 中增加第 4 个元素 `deadline_days: int | None`
- 安全管理、日常管理类别设置 deadline_days（3-25 随机分配）
- 其他类别默认 None
- `_build_seed()` 函数增加 deadline_days 参数

**Verify:**
- `python -m app.db.seed_monthly_tasks` 幂等运行
- 查询验证：`SELECT month, category, title, deadline_days FROM monthly_tasks WHERE deadline_days IS NOT NULL;` 返回数据

---

## Step 3: Backend — Workbench API (recommend)

**Files:**
- `backend/app/prompts/workbench.py` — NEW
- `backend/app/api/workbench.py` — NEW
- `backend/app/main.py` — MODIFY（注册路由）

**Description:**

### Prompt: workbench.py
```python
def build_workbench_recommend_prompt(month, done_count, unread_count):
    return """你是高校辅导员工作顾问。根据当前月份和任务完成情况，
推荐 2-3 条本月辅导员应优先完成的工作动作。
每条推荐包含 action（动作描述，30字以内）和 reason（推荐理由，20字以内）。
输出 JSON: {"recommendations": [{"action": "...", "reason": "..."}]}"""
```

### API: POST /api/workbench/recommend
- Request: `{month: int, done_task_ids: [str], unread_task_ids: [str]}`
- 调用 AIService.chat() 生成推荐
- 返回 `{recommendations: [{action, reason}]}`
- 错误处理：AI 调用失败返回空列表（不抛 500）

**Verify:**
- `curl -X POST http://localhost:8000/api/workbench/recommend -H 'Content-Type: application/json' -d '{"month":5,"done_task_ids":[],"unread_task_ids":[]}'` 返回推荐列表
- AI 不可用时返回 `{"recommendations": []}` 200（不报错）

---

## Step 4: Frontend — MonthlyWorkbench.vue 增强

**Files:**
- `frontend/src/pages/MonthlyWorkbench.vue` — MODIFY

**Description:**

在现有卡片网格上方新增三个区域：

### 1. 本周优先区域
```
<div class="priority-strip">
  <h2>⚡ 本周优先</h2>
  <el-row :gutter="16">
    <el-col v-for="task in weeklyPriorityTasks" :key="task.id" :xs="24" :sm="8">
      <el-card class="priority-card"> ... </el-card>
    </el-col>
  </el-row>
</div>
```
- `weeklyPriorityTasks` computed: 从 orderedTasks 中取前 3 个 `action_type='notice'` 且未完成的事项
- 高亮卡片样式：渐变背景，更明显的阴影和边框

### 2. 临近截止区域
```
<div class="deadline-section">
  <h2>🔔 临近截止</h2>
  <el-row>
    <el-col v-for="task in deadlineTasks" :key="task.id" ...>
      <el-card class="deadline-card">
        <el-tag :type="deadlineUrgency(task)">距截止 {n} 天</el-tag>
        ...
      </el-card>
    </el-col>
  </el-row>
  <el-empty v-if="deadlineTasks.length===0" description="暂无临近截止事项" />
</div>
```
- `deadlineTasks` computed: 筛选 `deadline_days` 存在且 `deadline_days - dayOfMonth ≤ 7` 的事项
- 后端返回 `deadline_days` 字段需加入 API response（schema 已包含，无需改 schema）

### 3. AI 推荐区域
```
<div class="recommend-section">
  <h2>🤖 AI 推荐下一步</h2>
  <el-skeleton v-if="recommendLoading" :rows="2" animated />
  <div v-else v-for="rec in recommendations" class="recommend-item">
    <p class="recommend-action">{{ rec.action }}</p>
    <p class="recommend-reason">{{ rec.reason }}</p>
  </div>
</div>
```
- `loadRecommendations()`: 调用 `POST /api/workbench/recommend`
- 失败时 `recommendations = []`，区域不渲染（静默降级）

### 页面结构（从上到下）
```
页面头部（月份切换器 + 标题）
→ AI 推荐下一步
→ 本周优先 (3 卡片横栏)
→ 临近截止 (动态数量)
→ 类别统计标签
→ 本月全部 (保留 task-001 卡片网格)
```

**Verify:**
- 桌面端浏览器：四个区域正常显示
- 移动端（375px）：所有区域纵向堆叠
- AI 推荐请求失败 → 区域不显示，无 console 报错

---

## Step 5: Backend — 测试

**Files:**
- `backend/tests/test_api/test_workbench.py` — NEW

**Description:**
- `test_recommend_success`: 验证返回结构
- `test_recommend_invalid_month`: month=0 返回 422
- `test_deadline_days_in_seed`: 种子数据中 deadline_days 列正确填充
- `test_monthly_tasks_include_deadline`: GET /api/monthly-tasks 返回含 deadline_days

**Verify:**
- `pytest backend/tests/test_api/test_workbench.py -v` 全部通过
- `pytest backend/tests/ -v` 回归全部通过

---

## Verification Gates

```bash
# 1. Lint
ruff check backend/app/api/workbench.py backend/app/prompts/workbench.py backend/app/models/monthly_task.py backend/app/db/seed_monthly_tasks.py
cd frontend && npm run lint -- src/pages/MonthlyWorkbench.vue

# 2. Typecheck
python -c "from app.api.workbench import router; from app.prompts.workbench import build_workbench_recommend_prompt; print('ok')"
cd frontend && vue-tsc --noEmit

# 3. Test
pytest backend/tests/test_api/test_workbench.py -v
pytest backend/tests/ -v  # 回归

# 4. Build
cd frontend && npm run build
```
