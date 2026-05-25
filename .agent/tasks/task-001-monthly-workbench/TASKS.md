# TASKS: Monthly Workbench (月度工作台)

## Dependencies

无外部依赖。本任务独立可完成。

---

## Step 1: Backend — 数据模型与迁移

**Files:**
- `backend/app/models/monthly_task.py` — 新建
- `backend/alembic/versions/xxx_monthly_tasks.py` — 自动生成

**Description:**
创建 `monthly_tasks` 表的 SQLAlchemy 模型，字段与 SPEC 一致。使用 Alembic 自动生成迁移文件。

**Verify:**
- `python -c "from app.models.monthly_task import MonthlyTask; print('OK')"` 无报错
- `alembic upgrade head` 成功创建表

---

## Step 2: Backend — Schema + Repository + Seed Data

**Files:**
- `backend/app/schemas/monthly_task.py` — 新建
- `backend/app/repositories/monthly_task.py` — 新建
- `backend/app/repositories/__init__.py` — 修改（导出）
- `backend/app/db/seed_monthly_tasks.py` — 新建

**Description:**
- Schema: Pydantic 模型定义 API 输入输出
- Repository: 继承 `BaseRepository`，添加 `get_by_month(month: int)` 方法
- Seed Data: 覆盖 12 个月、8 个类别的高校辅导员工作清单。种子脚本可独立运行 (`python -m app.db.seed_monthly_tasks`)，幂等（重复运行不重复插入）。

**Verify:**
- `python -m app.db.seed_monthly_tasks` 成功插入数据
- 重复运行不产生重复记录

---

## Step 3: Backend — API 端点

**Files:**
- `backend/app/api/monthly_tasks.py` — 新建
- `backend/app/main.py` — 修改（注册路由）

**Description:**
- `GET /api/monthly-tasks?month=5` → 返回当月事项列表
- 参数校验：month 必须是 1-12 的整数
- 按 category 和 title 排序

**Verify:**
- `curl http://localhost:8000/api/monthly-tasks?month=5` 返回 JSON 数组
- `curl http://localhost:8000/api/monthly-tasks?month=13` 返回 422
- `curl http://localhost:8000/api/monthly-tasks` 返回 422（必填参数）

---

## Step 4: Frontend — 月度工作台页面

**Files:**
- `frontend/src/pages/MonthlyWorkbench.vue` — 新建
- `frontend/src/router/index.ts` — 修改（添加路由、调整默认首页）
- `frontend/src/App.vue` — 修改（导航栏）

**Description:**

### 页面结构
```
MonthlyWorkbench
├── 页面头部（月份切换器 + 标题）
├── 分类标签筛选 (可选，MVP 可省略)
└── 卡片网格
    └── TaskCard × N
        ├── 类别标签 (el-tag)
        ├── 标题
        ├── 描述
        └── 操作按钮组
            ├── "生成通知" (action_type=notice)
            ├── "谈心提醒" (action_type=talk)
            └── "标记完成" (action_type=todo)
```

### 月份切换
- 使用 Element Plus `<el-select>` 或月份左右箭头
- 默认值为当前月份 (`new Date().getMonth() + 1`)

### 卡片点击行为
- `action_type=notice`: 打开 `PreGenerateDialog`，预填 `initialEvent` 为 `action_params.event`
- `action_type=talk`: `router.push('/talk-record')`
- `action_type=todo`: 切换卡片 `done` 状态（前端 ref）

### 响应式布局
- 使用 Element Plus `<el-row>` + `<el-col>` 栅格
- `:xs="24" :sm="12" :md="8" :lg="6"`

### 路由变更
- `/` → MonthlyWorkbench（认证后首页）
- `/assistant` → 原 Home.vue（AI 助手）
- 路由守卫逻辑不变

### 导航栏变更
- 新增"工作台"链接 → `/`
- "Counselor OS" 品牌文字点击 → `/`
- 原"首页"位置替换为"AI 助手" → `/assistant`

**Verify:**
- 浏览器访问 `http://localhost` 登录后直接看到工作台
- 月份切换卡片内容正确变化
- 点击"生成通知"弹出 PreGenerateDialog 且事件已预填
- 确认后通知成功生成
- 移动端浏览器卡片单列显示

---

## Step 5: Backend — 测试

**Files:**
- `backend/tests/test_api/test_monthly_tasks.py` — 新建

**Description:**
- `test_get_monthly_tasks_success`: 验证返回列表
- `test_get_monthly_tasks_invalid_month_negative`: month=0 返回 422
- `test_get_monthly_tasks_invalid_month_exceed`: month=13 返回 422
- `test_get_monthly_tasks_missing_param`: 缺少 month 参数返回 422
- `test_seed_idempotent`: 重复运行种子不重复

**Verify:**
- `pytest backend/tests/test_api/test_monthly_tasks.py -v` 全部通过

---

## Verification Gates (全部必须通过)

1. **Lint**
   ```bash
   ruff check backend/app/models/monthly_task.py backend/app/schemas/monthly_task.py backend/app/repositories/monthly_task.py backend/app/api/monthly_tasks.py backend/app/db/seed_monthly_tasks.py
   cd frontend && npm run lint -- src/pages/MonthlyWorkbench.vue
   ```

2. **Typecheck**
   ```bash
   # backend: 确认无 Python 导入错误
   python -c "from app.models.monthly_task import MonthlyTask; from app.schemas.monthly_task import MonthlyTaskResponse; print('ok')"
   cd frontend && vue-tsc --noEmit
   ```

3. **Test**
   ```bash
   pytest backend/tests/test_api/test_monthly_tasks.py -v
   pytest backend/tests/ -v  # 回归测试
   cd frontend && npm run test
   ```

4. **Build**
   ```bash
   cd frontend && npm run build
   docker compose build
   ```

---

## Estimated File Sizes

| File | Lines (max) |
|------|-------------|
| monthly_task.py (model) | ~30 |
| monthly_task.py (schema) | ~25 |
| monthly_task.py (repository) | ~25 |
| seed_monthly_tasks.py | ~150 (seed data) |
| monthly_tasks.py (api) | ~35 |
| MonthlyWorkbench.vue | ~200 |
| test_monthly_tasks.py | ~60 |
