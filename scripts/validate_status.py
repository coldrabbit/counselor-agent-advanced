#!/usr/bin/env python3
"""Status validator for Hermes file-system bus.

Validates all JSON files against their schemas defined in
.agent/templates/schemas/.

Usage:
    python scripts/validate_status.py                  # validate all
    python scripts/validate_status.py --task <task_id> # validate single task
    python scripts/validate_status.py --global          # validate global.json only
    python scripts/validate_status.py --events          # validate events.log entries
    python scripts/validate_status.py --active          # validate active_tasks.json only
    python scripts/validate_status.py --strict           # use strict JSON Schema validation (requires jsonschema)

Exit codes:
    0 - all valid
    1 - validation errors found
    2 - schema/structural errors
"""

import argparse
import json
import os
import sys

AGENT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agent")
SCHEMAS_DIR = os.path.join(AGENT_ROOT, "templates", "schemas")

VALID_TASK_STATUSES = [
    "DRAFT", "PLANNING", "WAITING_SPEC_APPROVAL", "BUILDING",
    "AUTO_FIXING", "QA_RUNNING", "REVIEWING", "NEEDS_FIX",
    "WAITING_MERGE_APPROVAL", "MERGED", "FAILED", "CANCELLED",
]

VALID_PHASES = ["init", "plan", "build", "qa", "review", "completed"]

VALID_EVENT_TYPES = [
    "TASK_CREATED", "AGENT_ASSIGNED", "STATE_TRANSITION",
    "ARTIFACT_CREATED", "GATE_RESULT", "BLOCKER_FOUND",
    "ERROR", "RETRY_STARTED", "HUMAN_ACTION",
    "AGENT_RELEASED", "TASK_COMPLETED",
]

VALID_AGENTS = ["planner", "builder", "qa", "reviewer", "hermes", "human", "system"]

VALID_GATE_VALUES = ["pending", "pass", "fail", "skipped"]

STATUS_REQUIRED_FIELDS = [
    "task_id", "title", "created_at", "updated_at",
    "status", "phase", "priority", "owner_agent", "next_agent",
    "blockers", "warnings", "auto_fix_rounds_used", "max_auto_fix_rounds",
    "artifacts", "approvals", "agents", "gates", "files", "lifecycle", "hermes",
]

EVENT_REQUIRED_FIELDS = [
    "timestamp", "event_type", "task_id", "agent",
    "from_state", "to_state", "payload", "correlation_id",
]

errors = []
warnings_list = []


def load_schema(name: str) -> dict:
    path = os.path.join(SCHEMAS_DIR, name)
    if not os.path.isfile(path):
        errors.append(f"Schema file not found: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_status_basic(data: dict, task_id: str) -> list:
    errs = []
    for field in STATUS_REQUIRED_FIELDS:
        if field not in data:
            errs.append(f"[{task_id}] missing required field: {field}")

    if "status" in data and data["status"] not in VALID_TASK_STATUSES:
        errs.append(f"[{task_id}] invalid status: {data['status']}")

    if "phase" in data and data["phase"] not in VALID_PHASES:
        errs.append(f"[{task_id}] invalid phase: {data['phase']}")

    if "priority" in data and not (1 <= data["priority"] <= 5):
        errs.append(f"[{task_id}] priority must be 1-5: {data['priority']}")

    if "auto_fix_rounds_used" in data and data["auto_fix_rounds_used"] > 3:
        errs.append(f"[{task_id}] auto_fix_rounds_used > 3: {data['auto_fix_rounds_used']}")

    if "gates" in data:
        for gate_name, gate_val in data["gates"].items():
            if gate_val not in VALID_GATE_VALUES:
                errs.append(f"[{task_id}] invalid gate value for {gate_name}: {gate_val}")

    if "artifacts" in data:
        required_artifacts = ["vision", "spec", "tasks", "qa_report", "review"]
        for art in required_artifacts:
            if art not in data["artifacts"]:
                errs.append(f"[{task_id}] missing artifact field: {art}")

    if "approvals" in data:
        for key in ["spec_approved", "merge_approved"]:
            if key not in data["approvals"]:
                errs.append(f"[{task_id}] missing approval field: {key}")
            elif not isinstance(data["approvals"][key], bool):
                errs.append(f"[{task_id}] approval.{key} must be bool")

    if "agents" in data:
        required_agents = ["planner", "builder", "qa", "reviewer"]
        for ag in required_agents:
            if ag not in data["agents"]:
                errs.append(f"[{task_id}] missing agent section: {ag}")

    if "lifecycle" in data:
        lc = data["lifecycle"]
        for key in ["current_phase", "phase_entered_at", "phase_history", "retry_count", "max_retries_per_phase"]:
            if key not in lc:
                errs.append(f"[{task_id}] missing lifecycle field: {key}")

    if "hermes" in data:
        hm = data["hermes"]
        for key in ["last_reported_at", "notifications_sent", "pending_notifications"]:
            if key not in hm:
                errs.append(f"[{task_id}] missing hermes field: {key}")

    return errs


def validate_event_basic(data: dict, line_num: int) -> list:
    errs = []
    for field in EVENT_REQUIRED_FIELDS:
        if field not in data:
            errs.append(f"[events.log:{line_num}] missing field: {field}")

    if "event_type" in data and data["event_type"] not in VALID_EVENT_TYPES:
        errs.append(f"[events.log:{line_num}] invalid event_type: {data['event_type']}")

    if "agent" in data and data["agent"] not in VALID_AGENTS:
        errs.append(f"[events.log:{line_num}] invalid agent: {data['agent']}")

    if "payload" in data:
        for key in ["message", "phase", "progress"]:
            if key not in data["payload"]:
                warnings_list.append(f"[events.log:{line_num}] payload missing recommended field: {key}")

    return errs


def validate_global_basic(data: dict) -> list:
    errs = []
    required_sections = ["factory", "agents", "gates", "constraints", "project", "stats"]
    for section in required_sections:
        if section not in data:
            errs.append(f"[global.json] missing required section: {section}")

    if "factory" in data:
        for key in ["version", "phase", "maturity_level", "last_updated", "uptime_started"]:
            if key not in data["factory"]:
                errs.append(f"[global.json.factory] missing field: {key}")

    if "agents" in data:
        required_agents = ["planner", "builder", "qa", "reviewer", "hermes"]
        for ag in required_agents:
            if ag not in data["agents"]:
                errs.append(f"[global.json.agents] missing agent: {ag}")
            else:
                for key in ["agent", "model", "status", "current_task", "prompt_file"]:
                    if key not in data["agents"][ag]:
                        errs.append(f"[global.json.agents.{ag}] missing field: {key}")
                if data["agents"][ag].get("status") not in ("idle", "busy", "standby", "offline", "ready"):
                    errs.append(f"[global.json.agents.{ag}] invalid status: {data['agents'][ag]['status']}")

    if "constraints" in data:
        for key in ["max_auto_fix_rounds", "max_file_lines", "max_parallel_tasks", "forbidden_tech"]:
            if key not in data["constraints"]:
                errs.append(f"[global.json.constraints] missing field: {key}")

    return errs


def validate_active_tasks_basic(data: dict) -> list:
    errs = []
    required_sections = ["last_updated", "summary", "tasks"]
    for section in required_sections:
        if section not in data:
            errs.append(f"[active_tasks.json] missing required section: {section}")

    if "summary" in data:
        for key in ["total", "active", "queued", "completed", "failed", "blocked"]:
            if key not in data["summary"]:
                errs.append(f"[active_tasks.json.summary] missing field: {key}")

    if "tasks" in data:
        for i, task in enumerate(data["tasks"]):
            for key in ["task_id", "title", "status", "phase", "priority"]:
                if key not in task:
                    errs.append(f"[active_tasks.json.tasks[{i}] missing field: {key}")
            if "status" in task and task["status"] not in VALID_TASK_STATUSES:
                errs.append(f"[active_tasks.json.tasks[{i}] invalid status: {task['status']}")

    return errs


def validate_with_jsonschema(data: dict, schema_name: str) -> list:
    try:
        import jsonschema
    except ImportError:
        warnings_list.append("jsonschema not installed, skipping strict validation. Install: pip install jsonschema")
        return []

    schema = load_schema(schema_name)
    if not schema:
        return [f"Could not load schema: {schema_name}"]

    errs = []
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        errs.append(f"[{schema_name}] {e.message}")
    except jsonschema.SchemaError as e:
        errs.append(f"[{schema_name}] schema error: {e.message}")
    return errs


def validate_task_status(task_id: str, strict: bool) -> list:
    task_dir = os.path.join(AGENT_ROOT, "tasks", task_id)
    status_path = os.path.join(task_dir, "STATUS.json")

    if not os.path.isfile(status_path):
        return [f"STATUS.json not found for task: {task_id}"]

    with open(status_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errs = validate_status_basic(data, task_id)
    if strict:
        errs.extend(validate_with_jsonschema(data, "task-status-v1.json"))
    return errs


def validate_all_tasks(strict: bool) -> list:
    errs = []
    tasks_dir = os.path.join(AGENT_ROOT, "tasks")
    if not os.path.isdir(tasks_dir):
        return [f"tasks directory not found: {tasks_dir}"]

    for entry in os.listdir(tasks_dir):
        task_path = os.path.join(tasks_dir, entry)
        if os.path.isdir(task_path) and entry.startswith("task-"):
            errs.extend(validate_task_status(entry, strict))
    return errs


def validate_events(strict: bool) -> list:
    events_log = os.path.join(AGENT_ROOT, "events", "events.log")
    if not os.path.isfile(events_log):
        return [f"events.log not found: {events_log}"]

    errs = []
    with open(events_log, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                errs.append(f"[events.log:{line_num}] JSON parse error: {e}")
                continue
            errs.extend(validate_event_basic(data, line_num))
            if strict:
                errs.extend(validate_with_jsonschema(data, "event-v1.json"))
    return errs


def validate_global(strict: bool) -> list:
    global_path = os.path.join(AGENT_ROOT, "status", "global.json")
    if not os.path.isfile(global_path):
        return [f"global.json not found: {global_path}"]

    with open(global_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errs = validate_global_basic(data)
    if strict:
        errs.extend(validate_with_jsonschema(data, "global-status-v1.json"))
    return errs


def validate_active(strict: bool) -> list:
    active_path = os.path.join(AGENT_ROOT, "status", "active_tasks.json")
    if not os.path.isfile(active_path):
        return [f"active_tasks.json not found: {active_path}"]

    with open(active_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errs = validate_active_tasks_basic(data)
    if strict:
        errs.extend(validate_with_jsonschema(data, "active-tasks-v1.json"))
    return errs


def main():
    parser = argparse.ArgumentParser(description="Validate Hermes bus JSON files against schemas")
    parser.add_argument("--task", help="Validate single task STATUS.json")
    parser.add_argument("--global", dest="global_flag", action="store_true", help="Validate global.json only")
    parser.add_argument("--events", action="store_true", help="Validate events.log only")
    parser.add_argument("--active", action="store_true", help="Validate active_tasks.json only")
    parser.add_argument("--strict", action="store_true", help="Use jsonschema for strict validation")

    args = parser.parse_args()

    all_errors = []

    if args.task:
        all_errors.extend(validate_task_status(args.task, args.strict))
    elif args.global_flag:
        all_errors.extend(validate_global(args.strict))
    elif args.events:
        all_errors.extend(validate_events(args.strict))
    elif args.active:
        all_errors.extend(validate_active(args.strict))
    else:
        print("=== Validating global.json ===")
        all_errors.extend(validate_global(args.strict))
        print("=== Validating active_tasks.json ===")
        all_errors.extend(validate_active(args.strict))
        print("=== Validating all task STATUS.json ===")
        all_errors.extend(validate_all_tasks(args.strict))
        print("=== Validating events.log ===")
        all_errors.extend(validate_events(args.strict))

    print()
    if all_errors:
        print(f"FAILED: {len(all_errors)} errors found")
        for err in all_errors:
            print(f"  ERROR: {err}")
    else:
        print("PASSED: all validations successful")

    if warnings_list:
        print(f"\nWARNINGS: {len(warnings_list)}")
        for w in warnings_list:
            print(f"  WARN: {w}")

    sys.exit(1 if all_errors else 0)


if __name__ == "__main__":
    main()