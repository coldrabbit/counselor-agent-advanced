#!/usr/bin/env python3
"""Task activation script for Hermes file-system bus.

One-command task activation: validates preconditions, updates STATUS.json,
updates active_tasks.json, appends events, and outputs next-agent prompt path.

Usage:
    python scripts/start_task.py \
        --task B-002-monthly-workbench-v2 \
        --owner codex \
        --stage building \
        --next-agent opencode

Steps:
    1. Validate task directory exists under .agent/tasks/
    2. Validate SPEC.md and TASKS.md exist in task directory
    3. Update task STATUS.json (atomic write)
    4. Update .agent/status/active_tasks.json (atomic write)
    5. Append STATE_TRANSITION + AGENT_ASSIGNED events to events.log
    6. Output next agent prompt file path
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

AGENT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agent")
TASKS_DIR = os.path.join(AGENT_ROOT, "tasks")
STATUS_DIR = os.path.join(AGENT_ROOT, "status")
EVENTS_DIR = os.path.join(AGENT_ROOT, "events")
EVENTS_LOG = os.path.join(EVENTS_DIR, "events.log")
TEMPLATES_DIR = os.path.join(AGENT_ROOT, "templates")
PROMPTS_DIR = os.path.join(AGENT_ROOT, "prompts")

VALID_STATUSES = [
    "DRAFT", "PLANNING", "WAITING_SPEC_APPROVAL", "BUILDING",
    "AUTO_FIXING", "QA_RUNNING", "REVIEWING", "NEEDS_FIX",
    "WAITING_MERGE_APPROVAL", "MERGED", "FAILED", "CANCELLED",
]

STAGE_TO_STATUS = {
    "draft": "DRAFT",
    "planning": "PLANNING",
    "spec_approval": "WAITING_SPEC_APPROVAL",
    "building": "BUILDING",
    "auto_fixing": "AUTO_FIXING",
    "qa": "QA_RUNNING",
    "reviewing": "REVIEWING",
    "needs_fix": "NEEDS_FIX",
    "merge_approval": "WAITING_MERGE_APPROVAL",
}

STAGE_TO_PHASE = {
    "draft": "init",
    "planning": "plan",
    "spec_approval": "plan",
    "building": "build",
    "auto_fixing": "build",
    "qa": "qa",
    "reviewing": "review",
    "needs_fix": "build",
    "merge_approval": "review",
}

AGENT_TO_PROMPT = {
    "planner": ".agent/prompts/planner.md",
    "builder": ".agent/prompts/builder.md",
    "codex": ".agent/prompts/builder.md",
    "qa": ".agent/prompts/qa.md",
    "opencode": ".agent/prompts/qa.md",
    "reviewer": ".agent/prompts/reviewer.md",
    "hermes": ".agent/prompts/hermes-supervisor.md",
}

NEXT_AGENT_TO_BUS_AGENT = {
    "planner": "planner",
    "builder": "builder",
    "codex": "builder",
    "qa": "qa",
    "opencode": "qa",
    "reviewer": "reviewer",
    "hermes": "hermes",
}

REQUIRED_ARTIFACTS_BY_STAGE = {
    "planning": [],
    "spec_approval": ["SPEC.md", "TASKS.md"],
    "building": ["SPEC.md", "TASKS.md"],
    "auto_fixing": ["SPEC.md", "TASKS.md"],
    "qa": ["SPEC.md", "TASKS.md"],
    "reviewing": ["SPEC.md", "TASKS.md"],
    "needs_fix": ["SPEC.md", "TASKS.md"],
    "merge_approval": ["SPEC.md", "TASKS.md"],
}

TASK_SEQ_MAP = {}


def atomic_write_json(path: str, data: dict) -> None:
    dir_name = os.path.dirname(path)
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".tmp", dir=dir_name)
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def load_task_seq_map() -> dict:
    if not os.path.isfile(EVENTS_LOG):
        return {}
    seq_map = {}
    with open(EVENTS_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
                cid = evt.get("correlation_id", "")
                if cid.startswith("evt-"):
                    parts = cid.split("-")
                    task_seq = int(parts[1])
                    event_seq = int(parts[2])
                    seq_map[task_seq] = max(seq_map.get(task_seq, 0), event_seq)
            except (json.JSONDecodeError, ValueError, IndexError):
                continue
    return seq_map


def next_correlation_id(task_id: str) -> str:
    global TASK_SEQ_MAP
    if not TASK_SEQ_MAP:
        TASK_SEQ_MAP = load_task_seq_map()
    try:
        task_seq = int(task_id.split("-")[1])
    except (IndexError, ValueError):
        task_seq = 999
    current_seq = TASK_SEQ_MAP.get(task_seq, 0) + 1
    TASK_SEQ_MAP[task_seq] = current_seq
    return f"evt-{task_seq:03d}-{current_seq:04d}"


def append_event(event: dict) -> None:
    if not os.path.isdir(EVENTS_DIR):
        os.makedirs(EVENTS_DIR, exist_ok=True)
    event_json = json.dumps(event, ensure_ascii=False)
    with open(EVENTS_LOG, "a", encoding="utf-8") as f:
        f.write(event_json + "\n")
        f.flush()
        os.fsync(f.fileno())


def resolve_task_dir(task_id: str) -> str:
    if os.path.isdir(os.path.join(TASKS_DIR, task_id)):
        return os.path.join(TASKS_DIR, task_id)
    candidates = [d for d in os.listdir(TASKS_DIR)
                  if d.startswith("task-") and d.endswith(f"-{task_id}")]
    if len(candidates) == 1:
        return os.path.join(TASKS_DIR, candidates[0])
    if len(candidates) > 1:
        print(f"ERROR: multiple task directories match '{task_id}': {candidates}")
        sys.exit(1)
    print(f"ERROR: task directory not found for '{task_id}'")
    print(f"  Available: {[d for d in os.listdir(TASKS_DIR) if d.startswith('task-')]}")
    sys.exit(1)


def validate_artifacts(task_dir: str, stage: str) -> None:
    required = REQUIRED_ARTIFACTS_BY_STAGE.get(stage, [])
    missing = []
    for artifact in required:
        path = os.path.join(task_dir, artifact)
        if not os.path.isfile(path):
            missing.append(artifact)
    if missing:
        print(f"ERROR: missing required artifacts for stage '{stage}': {missing}")
        print(f"  Task directory: {task_dir}")
        sys.exit(1)


def load_or_create_status(task_dir: str, task_id: str) -> dict:
    status_path = os.path.join(task_dir, "STATUS.json")
    if os.path.isfile(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
            return json.load(f)
    template_path = os.path.join(TEMPLATES_DIR, "STATUS.template.json")
    if not os.path.isfile(template_path):
        print(f"ERROR: STATUS.template.json not found: {template_path}")
        sys.exit(1)
    with open(template_path, "r", encoding="utf-8") as f:
        template = json.load(f)
    template.pop("_comment", None)
    template["task_id"] = task_id
    template["title"] = task_id
    template["created_at"] = datetime.now(timezone.utc).isoformat()
    template["updated_at"] = datetime.now(timezone.utc).isoformat()
    spec_path = os.path.join(task_dir, "SPEC.md")
    tasks_path = os.path.join(task_dir, "TASKS.md")
    vision_path = os.path.join(task_dir, "VISION.md")
    if os.path.isfile(spec_path):
        template["artifacts"]["spec"] = os.path.relpath(spec_path, AGENT_ROOT)
    if os.path.isfile(tasks_path):
        template["artifacts"]["tasks"] = os.path.relpath(tasks_path, AGENT_ROOT)
    if os.path.isfile(vision_path):
        template["artifacts"]["vision"] = os.path.relpath(vision_path, AGENT_ROOT)
    return template


def activate_status(status: dict, task_id: str, stage: str, owner: str, next_agent: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    new_status_val = STAGE_TO_STATUS.get(stage, "BUILDING")
    new_phase = STAGE_TO_PHASE.get(stage, "build")
    old_status = status.get("status", "DRAFT")

    if status.get("lifecycle"):
        if status["lifecycle"].get("current_phase"):
            status["lifecycle"]["phase_history"].append({
                "phase": status["lifecycle"]["current_phase"],
                "entered_at": status["lifecycle"].get("phase_entered_at", now),
                "exited_at": now,
            })
        status["lifecycle"]["current_phase"] = new_status_val
        status["lifecycle"]["phase_entered_at"] = now

    status["status"] = new_status_val
    status["phase"] = new_phase
    status["updated_at"] = now
    status["owner_agent"] = owner
    status["next_agent"] = next_agent

    bus_agent = NEXT_AGENT_TO_BUS_AGENT.get(next_agent, next_agent)
    if "agents" in status and bus_agent in status["agents"]:
        status["agents"][bus_agent]["agent"] = owner

    return status, old_status, new_status_val


def update_active_tasks(task_id: str, status: dict, stage: str, owner: str, next_agent: str) -> None:
    active_path = os.path.join(STATUS_DIR, "active_tasks.json")
    now = datetime.now(timezone.utc).isoformat()

    if os.path.isfile(active_path):
        with open(active_path, "r", encoding="utf-8") as f:
            active = json.load(f)
    else:
        active = {
            "$schema": "https://counselor-os.local/schemas/active-tasks-v1.json",
            "last_updated": now,
            "summary": {"total": 0, "active": 0, "queued": 0, "completed": 0, "failed": 0, "blocked": 0},
            "tasks": [],
        }

    existing_idx = None
    for i, t in enumerate(active["tasks"]):
        if t["task_id"] == task_id:
            existing_idx = i
            break

    task_entry = {
        "task_id": task_id,
        "title": status.get("title", task_id),
        "status": STAGE_TO_STATUS.get(stage, "BUILDING"),
        "phase": STAGE_TO_PHASE.get(stage, "build"),
        "owner_agent": owner,
        "next_agent": next_agent,
        "priority": status.get("priority", 1),
        "created_at": status.get("created_at", now),
        "merged_at": None,
        "branch": None,
        "tag": None,
        "blockers": status.get("blockers", 0),
        "auto_fix_rounds": status.get("auto_fix_rounds_used", 0),
        "artifacts": status.get("artifacts", {}),
        "gates": status.get("gates", {}),
    }

    if existing_idx is not None:
        active["tasks"][existing_idx] = task_entry
    else:
        active["tasks"].append(task_entry)

    total = len(active["tasks"])
    active_count = sum(1 for t in active["tasks"]
                       if t["status"] not in ("MERGED", "FAILED", "CANCELLED"))
    completed_count = sum(1 for t in active["tasks"] if t["status"] == "MERGED")
    failed_count = sum(1 for t in active["tasks"] if t["status"] == "FAILED")
    blocked_count = sum(1 for t in active["tasks"] if t["blockers"] > 0)

    active["summary"] = {
        "total": total,
        "active": active_count,
        "queued": 0,
        "completed": completed_count,
        "failed": failed_count,
        "blocked": blocked_count,
    }
    active["last_updated"] = now

    atomic_write_json(active_path, active)


def emit_events(task_id: str, old_status: str, new_status: str, owner: str, next_agent: str, stage: str) -> None:
    now = datetime.now(timezone.utc).isoformat()

    transition_event = {
        "timestamp": now,
        "event_type": "STATE_TRANSITION",
        "task_id": task_id,
        "agent": owner,
        "from_state": old_status,
        "to_state": new_status,
        "payload": {
            "message": f"Task {task_id} activated at stage {stage}",
            "phase": STAGE_TO_PHASE.get(stage, "build"),
            "progress": 10,
        },
        "correlation_id": next_correlation_id(task_id),
    }
    append_event(transition_event)

    bus_agent = NEXT_AGENT_TO_BUS_AGENT.get(next_agent, next_agent)
    assigned_event = {
        "timestamp": now,
        "event_type": "AGENT_ASSIGNED",
        "task_id": task_id,
        "agent": owner,
        "from_state": new_status,
        "to_state": new_status,
        "payload": {
            "message": f"Agent {next_agent} assigned to {task_id}",
            "phase": STAGE_TO_PHASE.get(stage, "build"),
            "progress": 10,
            "agent": next_agent,
            "role": bus_agent,
        },
        "correlation_id": next_correlation_id(task_id),
    }
    append_event(assigned_event)


def main():
    parser = argparse.ArgumentParser(
        description="Activate a task on the Hermes status bus",
        epilog="Example:\n"
               "  python scripts/start_task.py --task B-002-monthly-workbench-v2 --owner codex --stage building --next-agent opencode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--task", required=True, help="Task ID or slug (e.g. B-002-monthly-workbench-v2)")
    parser.add_argument("--owner", required=True, help="Owner agent identity (e.g. codex, opencode)")
    parser.add_argument("--stage", required=True,
                        choices=list(STAGE_TO_STATUS.keys()),
                        help="Activation stage (e.g. building, qa, reviewing)")
    parser.add_argument("--next-agent", required=True,
                        choices=list(AGENT_TO_PROMPT.keys()),
                        help="Next agent to execute (e.g. opencode, codex, planner)")
    parser.add_argument("--title", default=None, help="Task title (optional, uses existing or task ID)")
    parser.add_argument("--priority", type=int, default=1, choices=range(1, 6), help="Priority 1-5 (default: 1)")

    args = parser.parse_args()

    print(f"[1/6] Resolving task directory for: {args.task}")
    task_dir = resolve_task_dir(args.task)
    task_id = os.path.basename(task_dir)
    print(f"  OK: {task_dir}")

    print(f"[2/6] Validating required artifacts for stage: {args.stage}")
    validate_artifacts(task_dir, args.stage)
    print(f"  OK: SPEC.md and TASKS.md present")

    print(f"[3/6] Updating STATUS.json")
    status = load_or_create_status(task_dir, task_id)
    if args.title:
        status["title"] = args.title
    status["priority"] = args.priority
    status, old_status, new_status = activate_status(status, task_id, args.stage, args.owner, args.next_agent)
    status_path = os.path.join(task_dir, "STATUS.json")
    atomic_write_json(status_path, status)
    print(f"  OK: {old_status} -> {new_status} (atomic write)")

    print(f"[4/6] Updating active_tasks.json")
    update_active_tasks(task_id, status, args.stage, args.owner, args.next_agent)
    print(f"  OK: task entry updated (atomic write)")

    print(f"[5/6] Appending events to events.log")
    emit_events(task_id, old_status, new_status, args.owner, args.next_agent, args.stage)
    print(f"  OK: STATE_TRANSITION + AGENT_ASSIGNED appended")

    prompt_path = AGENT_TO_PROMPT[args.next_agent]
    prompt_full = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), prompt_path)

    print(f"[6/6] Next agent prompt:")
    print(f"  AGENT:    {args.next_agent} -> {NEXT_AGENT_TO_BUS_AGENT[args.next_agent]}")
    print(f"  PROMPT:   {prompt_path}")
    print(f"  TASK_DIR: {os.path.relpath(task_dir, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}")
    print(f"  STATUS:   {os.path.relpath(status_path, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}")

    if not os.path.isfile(prompt_full):
        print(f"  WARN: prompt file not found: {prompt_full}")

    print()
    print(f"=== TASK ACTIVATED: {task_id} ===")
    print(f"  Stage: {args.stage} | Status: {new_status} | Owner: {args.owner} | Next: {args.next_agent}")
    print(f"  Prompt: {prompt_path}")


if __name__ == "__main__":
    main()