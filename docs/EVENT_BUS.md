# Event Bus — File System Design

## 设计原则

1. **文件系统即总线** — 不引入 MQ/Kafka/Redis，JSON 文件即消息载体
2. **追加式事件日志** — events.log 只追加不修改，天然审计追踪
3. **轮询式消费** — Hermes 每 30s 读取文件，对比快照检测变化
4. **任务隔离** — 每个 task 独立的 STATUS.json，并行任务互不干扰
5. **人类可读** — 所有文件为 JSON/Markdown，Human 可直接阅读和修改

---

## Event Schema v1.0

### 事件格式

```json
{
  "timestamp": "2026-05-26T02:35:00+08:00",
  "event_type": "STATE_TRANSITION | GATE_RESULT | BLOCKER_FOUND | ERROR | HUMAN_ACTION | ARTIFACT_CREATED | TASK_CREATED | TASK_COMPLETED | AGENT_ASSIGNED | AGENT_RELEASED | RETRY_STARTED",
  "task_id": "task-xxx",
  "agent": "planner | builder | qa | reviewer | hermes | human | system",
  "from_state": "DRAFT | PLANNING | WAITING_SPEC_APPROVAL | BUILDING | AUTO_FIXING | QA_RUNNING | REVIEWING | NEEDS_FIX | WAITING_MERGE_APPROVAL | MERGED | FAILED | CANCELLED",
  "to_state": "...",
  "payload": {},
  "correlation_id": "evt-{task-num}-{seq}"
}
```

### Event Types

| event_type | 触发时机 | payload 内容 |
|-----------|---------|-------------|
| TASK_CREATED | 新任务创建 | `{title, priority}` |
| AGENT_ASSIGNED | Agent 接手任务 | `{agent, role}` |
| STATE_TRANSITION | 任何阶段变化 | `{phase, message}` |
| ARTIFACT_CREATED | SPEC/TASKS/REPORT 产出 | `{artifacts: [filenames]}` |
| GATE_RESULT | Gate 检查完成 | `{gates: {lint, typecheck, test, build}, auto_fix_rounds}` |
| BLOCKER_FOUND | Review 发现 BLOCKER | `{blocker, warnings[]}` |
| ERROR | 任何错误 | `{error_type, message, stack}` |
| RETRY_STARTED | 进入自动修复 | `{round, max_rounds, failing_gate}` |
| HUMAN_ACTION | Human 审批/操作 | `{action, command}` |
| AGENT_RELEASED | Agent 完成任务 | `{agent, result}` |
| TASK_COMPLETED | 任务合并且 tag | `{tag, commit, total_duration}` |

### Correlation ID 规范

```
格式: evt-{task_seq}-{event_seq}
示例: evt-001-0014
      evt = event
      001 = task-001
      0014 = 第 14 个事件
```

### Payload 最小字段

每个 payload 必须包含：

```json
{
  "message": "human-readable description",
  "phase": "current phase name",
  "progress": "0-100"
}
```

---

## STATUS.json Schema v1.0

### 任务级状态文件

```
.agent/tasks/{task-id}/STATUS.json
```

### 必填字段

```json
{
  "task_id": "string (required)",
  "title": "string (required)",
  "created_at": "ISO8601 (required)",
  "updated_at": "ISO8601 (required)",
  "status": "enum (required)",
  "phase": "enum (required)",
  "priority": "int 1-5 (required)",
  "owner_agent": "string | null (required)",
  "next_agent": "string | null (required)",
  "blockers": "int >= 0 (required)",
  "warnings": "int >= 0 (required)",
  "auto_fix_rounds_used": "int 0-3 (required)",
  "max_auto_fix_rounds": "int (required)",
  "artifacts": {
    "vision": "path | null",
    "spec": "path | null",
    "tasks": "path | null",
    "qa_report": "path | null",
    "review": "path | null"
  },
  "approvals": {
    "spec_approved": "bool (required)",
    "merge_approved": "bool (required)"
  },
  "agents": {
    "planner": {"agent": "string", "verdict": "string|null", "completed_at": "ISO8601|null"},
    "builder": {"agent": "string", "verdict": "string|null", "auto_fix_rounds": "int", "completed_at": "ISO8601|null"},
    "qa": {"agent": "string", "verdict": "string|null", "completed_at": "ISO8601|null"},
    "reviewer": {"agent": "string", "verdict": "string|null", "blockers": "int", "warnings": "int", "completed_at": "ISO8601|null"}
  },
  "gates": {
    "lint": "pending | pass | fail",
    "typecheck": "pending | pass | fail",
    "test": "pending | pass | fail",
    "build": "pending | pass | fail | skipped"
  },
  "files": {
    "created": ["path"],
    "modified": ["path"],
    "forbidden": ["path"]
  },
  "lifecycle": {
    "current_phase": "string | null",
    "phase_entered_at": "ISO8601 | null",
    "phase_history": [{"phase": "string", "entered_at": "ISO8601", "exited_at": "ISO8601"}],
    "retry_count": "int",
    "max_retries_per_phase": {
      "building": 3,
      "auto_fixing": 3,
      "qa": 1,
      "reviewing": 1
    }
  },
  "hermes": {
    "last_reported_at": "ISO8601 | null",
    "notifications_sent": "int",
    "pending_notifications": ["string"]
  }
}
```

### 状态枚举

```
任务状态:
  DRAFT | PLANNING | WAITING_SPEC_APPROVAL | BUILDING | AUTO_FIXING |
  QA_RUNNING | REVIEWING | NEEDS_FIX | WAITING_MERGE_APPROVAL |
  MERGED | FAILED | CANCELLED

Gate 状态:
  pending | pass | fail | skipped

Agent Verdict:
  PASS | FAIL | APPROVED | NEEDS_FIX | REJECTED

阶段:
  init | plan | build | qa | review | completed
```

---

## events.log 格式规范

### 文件规则

1. 每行一个完整的 JSON 事件对象（JSONL 格式）
2. 只追加（append-only），绝不修改已有行
3. 编码: UTF-8
4. 行分隔符: `\n`
5. 不做轮转（MVP 阶段），手动归档即可

### 追加协议

```
伪代码:
  event_json = json.dumps(event, ensure_ascii=False)
  with open(".agent/events/events.log", "a", encoding="utf-8") as f:
      f.write(event_json + "\n")
      f.flush()
      os.fsync(f.fileno())
```

### 读取协议

```
# 读取最后 N 行
tail -n 100 .agent/events/events.log

# 按 task_id 过滤
grep '"task_id":"task-001"' .agent/events/events.log

# 按 event_type 过滤
grep '"event_type":"BLOCKER_FOUND"' .agent/events/events.log

# 时间范围过滤（需要 jq）
cat .agent/events/events.log | while read line; do
  echo "$line" | jq 'select(.timestamp >= "2026-05-26T00:00:00")'
done
```

---

## global.json Schema v1.0

### 工厂全局状态

```json
{
  "factory": {
    "version": "string",
    "phase": "string",
    "maturity_level": "string",
    "last_updated": "ISO8601",
    "uptime_started": "ISO8601 | null"
  },
  "agents": {
    "<agent_name>": {
      "agent": "string (agent identity)",
      "model": "string (model name)",
      "status": "idle | busy | standby | offline",
      "current_task": "task_id | null",
      "prompt_file": "path"
    }
  },
  "gates": {
    "<gate_name>": {
      "backend": "command",
      "frontend": "command"
    }
  },
  "constraints": {
    "max_auto_fix_rounds": "int",
    "max_file_lines": "int",
    "max_parallel_tasks": "int",
    "forbidden_tech": ["string"],
    "qa_cannot_modify": ["string"],
    "builder_cannot_modify": ["string"],
    "reviewer_cannot_modify": ["string"]
  },
  "project": {
    "name": "string",
    "current_phase": "string",
    "tech_stack": {}
  },
  "stats": {
    "total_tasks": "int",
    "completed_tasks": "int",
    "failed_tasks": "int",
    "active_tasks": "int",
    "queued_tasks": "int",
    "total_auto_fix_rounds": "int",
    "total_blockers_found": "int",
    "total_merge_cycles": "int"
  }
}
```

---

## active_tasks.json Schema v1.0

### 任务索引

```json
{
  "last_updated": "ISO8601",
  "summary": {
    "total": "int",
    "active": "int",
    "queued": "int",
    "completed": "int",
    "failed": "int",
    "blocked": "int"
  },
  "tasks": [
    {
      "task_id": "string (required)",
      "title": "string (required)",
      "status": "enum (required)",
      "phase": "enum (required)",
      "owner_agent": "string | null (required)",
      "next_agent": "string | null (required)",
      "priority": "int 1-5 (required)",
      "created_at": "ISO8601 (required)",
      "merged_at": "ISO8601 | null",
      "branch": "string | null",
      "tag": "string | null",
      "blockers": "int",
      "auto_fix_rounds": "int",
      "artifacts": {},
      "gates": {}
    }
  ]
}
```

---

## Retry Schema

### 自动修复重试记录

放在 `STATUS.json` 的 `lifecycle` 字段中：

```json
{
  "lifecycle": {
    "retry_count": 0,
    "max_retries_per_phase": {
      "building": 3,
      "auto_fixing": 3,
      "qa": 1,
      "reviewing": 1
    },
    "phase_history": [
      {
        "phase": "AUTO_FIXING",
        "entered_at": "2026-05-26T01:30:00+08:00",
        "exited_at": "2026-05-26T01:32:00+08:00",
        "retry_round": 1,
        "failing_gate": "lint",
        "result": "pass"
      }
    ]
  }
}
```

### 重试决策规则

```
IF phase == "AUTO_FIXING" AND retry_count >= 3:
  → 状态 → FAILED
  → 原因: "3 轮自动修复耗尽"
  → 下一个 Agent: "planner"
  → Hermes: URGENT 通知

IF phase == "AUTO_FIXING" AND retry_count < 3:
  → 继续修复
  → 进入下一轮
  → Hermes: NORMAL 通知 (round 1) / HIGH 通知 (round 3)

IF phase == "QA_RUNNING" AND gates contain "fail":
  → 如果是新测试失败 → 状态 → AUTO_FIXING
  → 如果是回归测试失败 → 状态 → FAILED (需立即处理)
```

---

## 并行安全设计

### 问题：多个 Builder 并行修改

**方案：任务隔离 + Builder Slot 管理**

```
global.json:
  builder.parallel_slots: 3
  builder.active_slots: 1

active_tasks.json:
  每个 task 独立 owner_agent
  同一 slot 同时只跑一个 task

Hermes Rule 5:
  IF active_slots > parallel_slots → ALERT
```

### 问题：Hermes 与 Agent 同时写 events.log

**方案：追加式写入，短临界区**

```python
# 每个 Agent 写入 events.log 时：
# 单行 JSON + fsync，写入时间 < 1ms
# 追加操作在 POSIX 文件系统上是原子的（对于小于 PIPE_BUF 的写入）
```

### 问题：Hermes 读取时 Agent 正在写 STATUS.json

**方案：原子写入**

```python
# Agent 写 STATUS.json 时：
# 1. 写入 .STATUS.json.tmp
# 2. os.rename(.tmp, STATUS.json)  # 原子操作
# Hermes 读取时要么读到旧版要么读到新版，不会读到半成品
```

---

## 与 task-001 的向后兼容

task-001 的 `STATUS.json` 与新版 template 的差异：

| 字段 | task-001 | v1.0 template | 迁移 |
|------|---------|---------------|------|
| `phase` | `"review"` | `"completed"` | 手动更新 |
| `lifecycle` | 无 | 完整 | 补充 |
| `hermes` | 无 | 完整 | 补充 |
| `agents.*.completed_at` | 无 | ISO8601 | 补充 |
| `approvals.spec_approved` | `true` | `true` | 无需变 |
| `approvals.merge_approved` | `true` | `true` | 无需变 |

迁移策略：新 task 使用 v1.0 template，task-001 保留原格式不做强制迁移。
