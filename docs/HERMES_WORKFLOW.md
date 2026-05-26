# Hermes Supervisor Workflow

## 概述

Hermes 是 AI 软件工厂的**状态总线监督员**，负责：

1. 轮询文件系统状态总线
2. 检测状态变化
3. 发现阻塞
4. 通过微信上报进度
5. 请求人工决策

Hermes 不执行任务，不写代码，不修改状态文件。纯只读 + 通知。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Software Factory                       │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Planner  │  │ Builder  │  │   QA     │  │ Reviewer │   │
│  │ (Claude) │→│ (Codex)  │→│(OpenCode)│→│ (Claude) │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│       │         WRITE STATUS       │              │         │
│       └──────────────┴──────────────┴──────────────┘         │
│                          │                                   │
│                          ▼                                   │
│              ┌───────────────────────┐                       │
│              │    FILE SYSTEM BUS    │                       │
│              │  .agent/status/*.json │                       │
│              │  .agent/events/*.log  │                       │
│              └───────────┬───────────┘                       │
│                          │                                   │
│                          │ READ ONLY (poll every 30s)        │
│                          ▼                                   │
│                    ┌──────────┐                              │
│                    │  Hermes  │                              │
│                    │ (Flash)  │                              │
│                    └────┬─────┘                              │
│                         │                                    │
│                         │ WeChat API                         │
│                         ▼                                    │
│                    ┌──────────┐                              │
│                    │  WeChat  │                              │
│                    │  (Human) │                              │
│                    └──────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 文件系统状态总线

### 目录结构

```
.agent/
├── status/
│   ├── global.json          # 工厂全局状态（Agent 列表、Gate 定义、约束）
│   └── active_tasks.json    # 所有任务摘要索引（状态、owner、phase）
├── events/
│   └── events.log           # 追加式事件流（每行一个 JSON 事件）
├── queue/
│   └── (待处理任务队列文件)
├── logs/
│   └── (按任务日志文件)
├── tasks/
│   └── {task-id}/
│       ├── VISION.md         # 用户需求
│       ├── SPEC.md           # 功能规格
│       ├── TASKS.md          # 任务拆解
│       └── STATUS.json       # 任务详细状态
├── reports/
│   ├── {task-id}/
│   │   ├── QA_REPORT.md     # QA 报告
│   │   └── REVIEW.md        # 审查报告
│   └── task-xxx-builder-report.md
├── templates/
│   └── STATUS.template.json  # 任务状态模板
└── prompts/
    └── hermes-supervisor.md  # Hermes 行为定义
```

### 读写权限模型

| Agent | status/ | events/ | tasks/ | prompts/ | src/ |
|-------|---------|---------|--------|----------|------|
| Planner | WRITE | APPEND | WRITE | READ | READ |
| Builder | WRITE | APPEND | READ | READ | WRITE |
| QA | WRITE | APPEND | READ | READ | WRITE(tests) |
| Reviewer | WRITE | APPEND | READ | READ | READ |
| **Hermes** | **READ** | **APPEND** | **READ** | **READ** | **NONE** |

---

## 任务生命周期

```
                         ┌─────────┐
                         │  DRAFT  │
                         └────┬────┘
                              │ Planner: 创建 SPEC + TASKS
                              ▼
                      ┌───────────────┐
                      │   PLANNING    │
                      └───────┬───────┘
                              │ Planner: 完成规划
                              ▼
                 ┌────────────────────────┐
                 │ WAITING_SPEC_APPROVAL  │ ← Hermes 通知 Human
                 └───────────┬────────────┘
                             │ Human: approve
                             ▼
                      ┌──────────────┐
                      │   BUILDING   │
                      └──────┬───────┘
                             │ Builder: Gate check
              ┌──────────────┼──────────────┐
              │ PASS         │ FAIL         │
              ▼              ▼              │
       ┌──────────┐  ┌────────────┐        │
       │ QA_RUNNING│  │ AUTO_FIXING│ (≤3轮) │
       └─────┬────┘  └──────┬─────┘        │
             │              │ PASS          │
             │              ▼               │
             │       ┌──────────┐           │
             │       │ QA_RUNNING│ ←───────┘
             │       └─────┬────┘
             │             │ FAIL (3轮超)
             │             ▼
             │       ┌──────────┐
             │       │  FAILED  │ ← Hermes Alert
             │       └──────────┘
             │
             │ QA: Gate + 回归 + AC 全部通过
             ▼
      ┌──────────────┐
      │   REVIEWING  │
      └──────┬───────┘
             │ Reviewer: 审查结论
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│APPROVED│ │NEEDS_FIX │ │ REJECTED │
└───┬────┘ └────┬─────┘ └────┬─────┘
    │           │             │
    ▼           ▼             ▼
┌───────────────┐   ┌──────────┐   ┌──────────┐
│WAITING_MERGE  │   │ Builder  │   │ Planner  │
│   _APPROVAL   │   │  修复    │   │ 重新规划 │
└───────┬───────┘   └──────────┘   └──────────┘
        │ Human: approve merge
        ▼
   ┌──────────┐
   │  MERGED  │ ← Hermes 通知完成
   └──────────┘
```

### 阶段责任表

| 阶段 | Owner | 进入条件 | 退出条件 | 最大重试 |
|------|-------|---------|---------|---------|
| DRAFT | — | 任务创建 | Planner 开始 | — |
| PLANNING | Planner | SPEC 编写 | SPEC+TASKS 完成 | — |
| WAITING_SPEC_APPROVAL | Human | Planner 完成 | Human 批准 | — |
| BUILDING | Builder | SPEC 批准 | Gate 检查 | — |
| AUTO_FIXING | Builder | Gate 失败 | Gate 通过 or 3 轮耗尽 | 3 |
| QA_RUNNING | QA Agent | Builder Gate 通过 | QA 全部通过 | 1 |
| REVIEWING | Reviewer | QA 完成 | 审查结论 | 1 |
| NEEDS_FIX | Builder | Reviewer BLOCKER | 修复完成 | — |
| WAITING_MERGE_APPROVAL | Human | Review APPROVED | Human 合并 | — |
| MERGED | — | 合并成功 | — | — |
| FAILED | Planner | 3 轮超/REJECTED | Planner 重新评估 | — |
| CANCELLED | Human | 任何阶段 | — | — |

---

## Hermes 轮询循环

```
┌─────────────────────────────────────────┐
│          Hermes Poll Loop                │
│                                          │
│  ┌──────────────────────────┐           │
│  │ Sleep 30s                │←──────────┘
│  └──────────┬───────────────┘
│             ▼
│  ┌──────────────────────────┐
│  │ Read global.json         │
│  │ Read active_tasks.json   │
│  └──────────┬───────────────┘
│             ▼
│  ┌──────────────────────────┐
│  │ Compare with last state  │
│  └──────────┬───────────────┘
│             ▼
│      ┌──────────────┐
│      │ Changes found?│
│      └──┬───────┬───┘
│         │ YES   │ NO → loop back
│         ▼       │
│  ┌──────────────────────────┐
│  │ Classify change:         │
│  │ - STATE_TRANSITION       │
│  │ - GATE_RESULT            │
│  │ - BLOCKER_FOUND          │
│  │ - HUMAN_ACTION           │
│  └──────────┬───────────────┘
│             ▼
│  ┌──────────────────────────┐
│  │ Check blockage rules:    │
│  │ - Stale task?            │
│  │ - Auto-fix exhausted?    │
│  │ - Agent conflict?        │
│  │ - Approval overdue?      │
│  └──────────┬───────────────┘
│             ▼
│  ┌──────────────────────────┐
│  │ Determine priority:      │
│  │ URGENT / HIGH / NORMAL   │
│  └──────────┬───────────────┘
│             ▼
│  ┌──────────────────────────┐
│  │ Send WeChat notification │
│  │ (only if action needed)  │
│  └──────────┬───────────────┘
│             ▼
│  ┌──────────────────────────┐
│  │ Append to events.log     │
│  └──────────┬───────────────┘
│             │
│             └────────────────→ loop back
└─────────────────────────────────────────┘
```

---

## 微信通知触发表

| 触发条件 | 优先级 | 消息模板 |
|---------|--------|---------|
| 新任务创建 | NORMAL | "新任务 {id} 已创建: {title}" |
| 等待 SPEC 审批 | HIGH | "task-xxx 需要 SPEC 审批" |
| 等待 Merge 审批 | HIGH | "task-xxx Review 通过，可以合并" |
| Gate 失败 | HIGH | "task-xxx {gate} 失败: {detail}" |
| Auto-fix 第 1 轮 | LOW | "task-xxx 自动修复中 (1/3)" |
| Auto-fix 第 3 轮 | HIGH | "task-xxx 最后一轮自动修复 (3/3)" |
| Auto-fix 耗尽 | URGENT | "task-xxx 自动修复失败，需 Planner 介入" |
| Review BLOCKER | URGENT | "task-xxx 发现 {n} 个 BLOCKER: {list}" |
| 合并完成 | NORMAL | "task-xxx 已合并, tag: {tag}" |
| 任务失败 | URGENT | "task-xxx 失败: {reason}" |
| 审批超时 24h | HIGH | "task-xxx 审批等待超过 24 小时" |

---

## 阻塞处理决策树

```
发现阻塞
  ├── 审批等待超时 (24h)
  │     → WeChat 提醒 Human + 标记 URGENT
  │
  ├── Auto-fix 3 轮耗尽
  │     → WeChat 通知 Planner 介入
  │     → 更新任务状态为 FAILED
  │     → 将任务移回 Planner 队列
  │
  ├── Review BLOCKER
  │     → WeChat 通知 Human: "N 个 BLOCKER 需处理"
  │     → 等待 Human 决策: "修复" or "忽略并合并"
  │
  ├── Agent 不可用 (例如 QA busy)
  │     → 任务排队等待
  │     → WeChat 通知: "task-xxx 排队等待 QA Agent"
  │
  └── Gate 持续失败 (同一 gate 失败 > 2 次)
        → WeChat 通知 Planner: "可能需要重新评估技术方案"
```

---

## 与现有 Agent 的集成

### Planner 集成
- SPEC 完成后 → 更新 STATUS.json → Hermes 检测到 `WAITING_SPEC_APPROVAL` → 通知 Human

### Builder 集成
- BUILD 完成 → Gate 检查结果写入 STATUS.json → Hermes 检测变化 → 通知
- Auto-fix 每轮 → 更新 `auto_fix_rounds_used` → Hermes 跟踪轮次

### QA 集成
- QA 完成 → QA_REPORT.md + STATUS.json 更新 → Hermes 检测 → 通知 Review 结果

### Reviewer 集成
- Review 完成 → REVIEW.md + STATUS.json 更新 → Hermes 区分 APPROVED/NEEDS_FIX/REJECTED
- NEEDS_FIX → 通知 Builder/Human
- APPROVED → 通知 Human 合并

### Human 集成
- Human 审批 → 更新 STATUS.json → Hermes 检测 HUMAN_ACTION → 推进流水线
