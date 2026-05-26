# AI Software Factory — Standard Operating Procedure

基于 task-001-monthly-workbench 完整开发流程总结。

---

## 1. 开发流水线

```
VISION → SPEC → [Human Gate] → TASKS → BUILD → AUTO-FIX(≤3) → QA → REVIEW → [Human Gate] → MERGE
```

| 阶段 | Agent | 输入 | 输出 | Human Gate |
|------|-------|------|------|------------|
| VISION | Human | 需求想法 | VISION.md | — |
| SPEC | Planner | VISION.md + 代码库 | SPEC.md | **SPEC 审批** |
| TASKS | Planner | SPEC.md | TASKS.md | — |
| BUILD | Builder | SPEC + TASKS | Code + Self-check | — |
| AUTO-FIX | Builder | Gate failures | Fixes (≤3轮) | — |
| QA | QA Agent | 构建产物 | QA_REPORT.md | — |
| REVIEW | Reviewer | SPEC + Diff + QA_REPORT | REVIEW.md | **Merge 审批** |
| MERGE | Human | REVIEW=APPROVED | 合并到 main | **最终确认** |

## 2. Agent 职责矩阵

### Planner (Claude Code + DeepSeek Pro)

**负责：**
- 分析 VISION，结合代码库现状做架构设计
- 产出 SPEC.md（功能需求、API 契约、数据模型、验收标准）
- 产出 TASKS.md（实现步骤、文件清单、验证命令）
- 明确 Affected Files（可修改）和 Forbidden Files（禁止触碰）
- 更新 .agent/status/current.json

**禁止：**
- 写业务代码
- 修改源文件
- 运行 build/test 命令
- 合并分支

### Builder (Codex + DeepSeek Pro)

**负责：**
- 严格按 SPEC + TASKS 逐步骤实现
- 每个 Step 完成后自检
- Gate 失败时进入自动修复循环（最多 3 轮）
- 复用已有组件和接口，不重复造轮子

**禁止：**
- 修改 SPEC 中定义的需求范围
- 引入 SPEC 未列出的新依赖或架构模式
- 触碰 Forbidden Files 清单中的文件
- 删除已有测试
- 在业务代码中内联 AI prompt（必须用 `backend/app/prompts/`）

**自动修复策略（3 轮）：**

| 轮次 | 修复范围 | 禁止 |
|------|---------|------|
| Round 1 | lint / typecheck 错误 | 不改逻辑 |
| Round 2 | test 失败 | 不删已有测试 |
| Round 3 | build 失败 | 不降级依赖 |
| 超出 3 轮 | 标记 FAILED → 回报 Planner | — |

### QA Agent (OpenCode + GLM 5.1)

**负责：**
- 运行全部 4 个 Gate：lint / typecheck / test / build
- 运行全量回归测试
- 逐条验证 Acceptance Criteria
- 检查 Forbidden Files 是否被触碰
- 产出 QA_REPORT.md

**禁止：**
- 修改架构代码
- 修改业务逻辑
- 修改 SPEC 或 TASKS
- 修改 API Schema 或数据库模型

### Reviewer (Claude Code + DeepSeek Pro)

**负责：**
- 审查 git diff 的每一个变更
- 验证 SPEC 符合度
- 检查是否引入禁止技术
- 安全扫描（SQL 注入、XSS、命令注入）
- 代码质量审查（文件大小、函数大小、类型标注）
- 产出 REVIEW.md，给出 APPROVED / NEEDS_FIX / REJECTED

**禁止：**
- 修改任何源文件
- 写代码修复问题
- 修改 SPEC 或 TASKS
- 直接合并分支

### Hermes (DeepSeek Flash)

**负责：**
- 微信入口消息接收
- 流水线状态变更通知
- 任务调度提醒
- 不参与代码生成或审查

## 3. 正确行为（来自 task-001 经验）

### 3.1 复用优先
- task-001 复用了 `PreGenerateDialog.vue` 组件而非重写
- 复用了 `POST /api/notices/generate` 接口而非新建
- 复用了 `noticeStore.generate()` 方法

### 3.2 保持模式一致
- Repository 继承 `BaseRepository`，与其他 14 个 Repository 一致
- API 使用 `Depends(get_db)` + Pydantic Response Model，与现有模式一致
- 前端使用 `axios` + `ElMessage` + Element Plus 栅格，与现有页面一致

### 3.3 种子数据幂等
- 使用 `uuid.uuid5(namespace, key)` 确定性生成 ID
- `seed_monthly_tasks()` 检查已有 ID 再插入，重复运行安全

### 3.4 SPEC 明确列出文件清单
- Affected Files: 新建和可修改文件
- Forbidden Files: 明确哪些文件不能碰
- 这避免了 Builder 误改核心模块

### 3.5 QA 全量回归
- 不仅运行新测试 (6/6)，还运行全部已有测试 (60/60)
- 任何已有测试失败都是回归问题

## 4. 禁止行为（来自 task-001 实际教训）

### 4.1 禁止修改 SPEC 未列出的文件

**实例：** task-001 中 Builder 修改了 `CLAUDE.md`（行尾不可见字符 + superpowers-zh 配置删除），导致 REVIEW 阶段被标记 BLOCKER。

**规则：** 所有变更必须在 SPEC 的 Affected Files 中列出。若有未预见的必要修改（如 `alembic/env.py` 模型导入），需在 Builder Report 中说明。

### 4.2 禁止跳过 Gate

每个 Gate 必须实际运行并确认通过，不能因为"看起来没问题"而跳过。
- `ruff check` → 必须 0 错误
- `vue-tsc --noEmit` → 必须 0 错误
- `pytest -v` → 全部通过
- `npm run build` → 构建成功

### 4.3 禁止引入 SPEC 外的依赖

task-001 要求"不引入新的第三方依赖"，Builder 严格遵守。任何新依赖必须在 SPEC 阶段明确并获批准。

### 4.4 禁止触碰 Forbidden Files

```
- backend/app/models/notice.py         # 核心模型
- backend/app/tasks/notice_task.py      # 核心任务
- backend/app/api/notices.py            # 核心 API
- backend/app/workflows/                # 工作流引擎
- backend/app/services/ai/client.py     # AI 服务
- backend/app/engine/                   # 引擎层
- frontend/src/components/PreGenerateDialog.vue  # 复用组件
- frontend/src/stores/                  # 全局状态
```

### 4.5 禁止引入禁止技术

```
禁止清单（除非 Planner 评估并获 Human 批准）：
- LangGraph / LangChain
- CrewAI / AutoGen / 多 Agent 自主协作
- Kubernetes (k8s)
- 事件总线 / 消息队列 (RabbitMQ/Kafka)
- 微服务拆分
- CQRS / Event Sourcing
- DDD 战术模式
- 向量数据库 (Pinecone/Milvus)
- RAG（当前 Phase 不做）
```

## 5. 自动修复策略

```
BUILD 完成
  → Gate Check (lint + typecheck + test + build)
  → PASS → 进入 QA
  → FAIL → Auto-fix Round 1: lint/typecheck 修复
  → Gate Check
  → PASS → 进入 QA
  → FAIL → Auto-fix Round 2: test 修复
  → Gate Check
  → PASS → 进入 QA
  → FAIL → Auto-fix Round 3: build 修复
  → Gate Check
  → PASS → 进入 QA
  → FAIL → 标记 FAILED，回报 Planner 重新评估
```

**关键约束：**
- 每轮修复后必须重新运行全部 Gate
- Round 1 只修 lint/typecheck，不改逻辑
- Round 2 只修测试，不删已有测试
- Round 3 只修 build，不降级依赖
- 超过 3 轮 → 不是 Builder 能解决的问题，需要 Planner 介入

## 6. Worktree 使用规范

```
# 创建隔离工作区（推荐）
git worktree add -b feature/<task-id> ../counselor-<task-id> main

# 完成后清理
git worktree remove ../counselor-<task-id>
git branch -d feature/<task-id>
```

**使用场景：**
- 每个 task 使用独立的 worktree
- 避免多个 task 交叉污染
- 完成后必须清理 worktree 和 branch

**不使用 worktree 的替代方案：**
- 在同一个仓库中 `git checkout -b feature/<task-id>`
- 确保一次只做一个 task

## 7. Branch 规范

```
分支命名: feature/<task-id>
示例:     feature/task-001-monthly-workbench

生命周期:
  main ← feature/task-001（开发中）
  main ← feature/task-001（合并后删除分支）
```

**规则：**
- 一个 task 一个分支
- 分支从 main 最新 commit 创建
- 合并使用 Fast-forward（保持线性历史）
- 合并后删除 feature 分支
- 禁止直接在 main 上开发

## 8. PR / Merge 规范

### Tag 命名

```
v<major>.<minor>-<description>
示例: v0.1-ai-workflow-first
```

### Commit Message

```
<type>: <short description>

<detailed body>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Type 使用 Conventional Commits：`feat`, `fix`, `refactor`, `docs`, `test`

### Merge 前置条件

所有条件必须满足才能合并：

- [ ] SPEC.md 获 Human 批准
- [ ] QA_REPORT.md 全部 Gate PASS
- [ ] QA_REPORT.md 全部 AC PASS
- [ ] QA_REPORT.md 回归测试全部 PASS
- [ ] REVIEW.md 结论为 APPROVED
- [ ] REVIEW.md 无 BLOCKER 级别问题
- [ ] git diff 仅包含 SPEC 授权文件

## 9. Hermes 汇报规范

Hermes 负责微信端的任务状态通知，在以下关键节点发送：

| 阶段 | 状态 | 通知内容 |
|------|------|---------|
| SPEC 完成 | WAITING_APPROVAL | "task-xxx SPEC 已完成，请审批" |
| BUILD 完成 | BUILD_COMPLETE | "task-xxx 构建完成，Gate 全部通过" |
| BUILD 失败 | FAILED (3轮超) | "task-xxx 自动修复失败，需 Planner 介入" |
| QA 完成 | QA_COMPLETE | "task-xxx QA 完成，结论: PASS/FAIL" |
| REVIEW 完成 | APPROVED | "task-xxx Review 通过，可以合并" |
| REVIEW 阻塞 | NEEDS_FIX | "task-xxx Review 受阻: N个BLOCKER" |
| MERGE 完成 | MERGED | "task-xxx 已合并到 main，tag: vX.Y" |

## 10. Merge Checklist（最终核对）

合并前 Operator 必须逐条确认：

```
[ ] 1. 当前在 main 分支
[ ] 2. git status 干净（无未提交变更）
[ ] 3. REVIEW.md 结论为 APPROVED
[ ] 4. QA_REPORT.md 所有 Gate PASS
[ ] 5. git diff 仅含 SPEC 授权文件
[ ] 6. git log 确认无意外 commit
[ ] 7. CLOSE.md / docs/PRD.md 等工程文件未被修改
[ ] 8. git merge feature/<task-id> 使用 Fast-forward
[ ] 9. git tag vX.Y-<描述> 已创建
[ ] 10. git push origin main --tags 成功
```

---

## 附录：task-001 实际数据

| 指标 | 数值 |
|------|------|
| 新建文件 | 7 (业务) + 3 (doc) + 4 (agent prompts) |
| 修改文件 | 4 (授权) + 2 (必要但未列出) |
| 代码行数 | ~550 行 (含种子数据 214 行) |
| 测试用例 | 6 个 (5 API + 1 seed) |
| 最大文件 | MonthlyWorkbench.vue 242 行 |
| Gate 通过率 | 6/6 (Docker build 环境受限 skip) |
| AC 通过率 | 9/9 (100%) |
| Auto-fix 轮次 | 0 (一次通过) |
| Forbidden 触碰 | 0 |
| 发现 BLOCKER | 1 (CLAUDE.md unauthorized change) |
| 修复耗时 | 1 条命令 (`git checkout CLAUDE.md`) |
