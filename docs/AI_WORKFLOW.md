# AI Software Factory — Workflow Pipeline

## 概述

本项目的 AI 软件工厂由 4 个 AI Agent 组成流水线，配合严格的 Gate 机制，实现 spec-driven、test-gated 的软件开发。

## Agent 分工矩阵

| 角色 | Agent | 模型 | 职责 | 权限 |
|------|-------|------|------|------|
| Chief Architect | Claude Code | DeepSeek Pro | 架构规划、OpenSpec、任务拆解、最终 Review | 写 SPEC/TASKS/REVIEW，不可写业务代码 |
| Builder | Codex | DeepSeek Pro | 主力开发、并行实现、自动修复 | 写业务代码，不可修改 SPEC |
| QA | OpenCode | GLM 5.1 | 本地验证、回归测试、QA 报告 | 写测试/QA_REPORT，不可修改架构 |
| Hermes | Hermes | DeepSeek Flash | 微信入口、状态上报、任务调度提醒 | 只读，不上报时不影响流水线 |

## 流水线 Gate 机制

```
                    ┌─────────────┐
                    │  Planner    │
                    │  (Claude)   │
                    └──────┬──────┘
                           │ SPEC.md + TASKS.md
                           ▼
              ┌────────────────────────┐
              │  Human Approval Gate   │
              └────────────┬───────────┘
                           │ Approved
                           ▼
                    ┌─────────────┐
                    │  Builder     │
                    │  (Codex)     │
                    └──────┬──────┘
                           │ Implementation
                           ▼
              ┌────────────────────────┐
              │  Auto-fix Gate         │
              │  (max 3 rounds)        │
              └────────────┬───────────┘
                           │ Pass or exceeded
                           ▼
                    ┌─────────────┐
                    │  QA Agent    │
                    │  (OpenCode)  │
                    └──────┬──────┘
                           │ QA_REPORT.md
                           ▼
              ┌────────────────────────┐
              │  Verification Gate     │
              │  lint + typecheck      │
              │  + test + build        │
              └────────────┬───────────┘
                           │ All pass
                           ▼
                    ┌─────────────┐
                    │  Reviewer    │
                    │  (Claude)    │
                    └──────┬──────┘
                           │ REVIEW.md
                           ▼
              ┌────────────────────────┐
              │  Human Merge Gate      │
              └────────────┬───────────┘
                           │ Approved
                           ▼
                      ┌─────────┐
                      │  MERGE  │
                      └─────────┘
```

## 阶段定义

### Phase 1: PLAN（规划）

- **执行者**: Claude Code (Planner)
- **输入**: 用户需求 / PRD
- **输出**: SPEC.md + TASKS.md
- **Gate**: Human approval on SPEC before proceeding

### Phase 2: BUILD（构建）

- **执行者**: Codex (Builder)
- **输入**: SPEC.md + TASKS.md
- **输出**: Code changes + self-check
- **约束**: 不允许修改 SPEC 中定义的需求范围
- **自动修复**: 最多 3 轮
  - Round 1: lint/typecheck 错误自动修复
  - Round 2: test 失败自动修复
  - Round 3: build 失败自动修复
  - 超过 3 轮 → 标记 FAILED，上报 Planner 重新规划

### Phase 3: QA（验证）

- **执行者**: OpenCode + GLM 5.1 (QA Agent)
- **输入**: 构建产物
- **输出**: QA_REPORT.md
- **约束**:
  - 不允许修改架构
  - 不允许修改业务逻辑
  - 只允许添加/修改测试代码
- **验证门禁**:
  1. `npm run lint` (frontend) / `ruff check` (backend) — 必须 0 错误
  2. `vue-tsc --noEmit` (frontend) / `mypy` (backend) — 必须 0 错误
  3. `npm run test` (frontend) / `pytest` (backend) — 必须全部通过
  4. `npm run build` (frontend) / `docker build` (backend) — 必须成功
  5. 回归测试 — 已有测试不能失败

### Phase 4: REVIEW（审查）

- **执行者**: Claude Code (Reviewer)
- **输入**: Code diff + QA_REPORT.md
- **输出**: REVIEW.md
- **审查维度**:
  - Spec 符合度：代码是否完整实现了 SPEC
  - 架构一致性：是否引入了禁止的技术/模式
  - 安全性：是否有 SQL 注入、XSS、命令注入等漏洞
  - 代码质量：是否符合工程规范（文件大小、函数大小、单一职责）
  - QA 结果：所有门禁是否通过
- **Gate**: Human approval on REVIEW before merge

## 任务制品要求

每个任务必须包含以下 4 个制品：

| 制品 | 生成阶段 | 文件名 | 内容 |
|------|---------|--------|------|
| SPEC | PLAN | `.agent/tasks/{task-id}/SPEC.md` | 功能规格、输入输出、约束条件 |
| TASKS | PLAN | `.agent/tasks/{task-id}/TASKS.md` | 任务拆解、步骤顺序、验收标准 |
| QA_REPORT | QA | `.agent/reports/{task-id}/QA_REPORT.md` | 测试结果、门禁状态、回归报告 |
| REVIEW | REVIEW | `.agent/reports/{task-id}/REVIEW.md` | 审查结论、风险标注、合并建议 |

## 任务状态机

```
DRAFT
  → PLANNING
  → WAITING_APPROVAL (human gate after PLAN)
  → BUILDING
  → AUTO_FIXING (round 1-3)
  → QA_RUNNING
  → REVIEWING
  → WAITING_MERGE (human gate after REVIEW)
  → MERGED

Any state → FAILED (with reason logged)
```

## 约束矩阵

| 角色 | 写 SPEC | 写代码 | 写测试 | 改架构 | 改需求 | Merge |
|------|---------|--------|--------|--------|--------|-------|
| Planner | YES | NO | NO | YES | YES | NO |
| Builder | NO | YES | YES | NO | NO | NO |
| QA | NO | NO | YES | NO | NO | NO |
| Reviewer | NO | NO | NO | NO | NO | NO |
| Human | APPROVE | - | - | - | - | YES |
