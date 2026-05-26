#!/usr/bin/env python3
"""Atomic status update script for Hermes file-system bus.

Writes STATUS.json using atomic write (tmp file + os.rename)
to prevent Hermes from reading partial data.

Usage:
    python scripts/update_status.py <task_id> <field> <value>
    python scripts/update_status.py <task_id> --from-json <json_file>
    python scripts/update_status.py <task_id> --state <new_state> [--agent <agent>]

Examples:
    python scripts/update_status.py task-002-notification status BUILDING
    python scripts/update_status.py task-002-notification --state QA_RUNNING --agent qa
    python scripts/update_status.py task-002-notification --from-json updated_status.json
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone

AGENT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agent")
TASKS_DIR = os.path.join(AGENT_ROOT, "tasks")

VALID_TASK_STATUSES = [
    "DRAFT", "PLANNING", "WAITING_SPEC_APPROVAL", "BUILDING",
    "AUTO_FIXING", "QA_RUNNING", "REVIEWING", "NEEDS_FIX",
    "WAITING_MERGE_APPROVAL", "MERGED", "FAILED", "CANCELLED",
]

VALID_PHASES = ["init", "plan", "build", "qa", "review", "completed"]


def find_task_dir(task_id: str) -> str:
    task_dir = os.path.join(TASKS_DIR, task_id)
    if not os.path.isdir(task_dir):
        print(f"ERROR: task directory not found: {task_dir}")
        sys.exit(1)
    return task_dir


def read_status(task_id: str) -> dict:
    task_dir = find_task_dir(task_id)
    status_path = os.path.join(task_dir, "STATUS.json")
    if not os.path.isfile(status_path):
        print(f"ERROR: STATUS.json not found: {status_path}")
        sys.exit(1)
    with open(status_path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def update_field(status: dict, field: str, value: str) -> dict:
    if field == "status":
        if value not in VALID_TASK_STATUSES:
            print(f"ERROR: invalid status '{value}'. Valid: {VALID_TASK_STATUSES}")
            sys.exit(1)
        status["status"] = value
    elif field == "phase":
        if value not in VALID_PHASES:
            print(f"ERROR: invalid phase '{value}'. Valid: {VALID_PHASES}")
            sys.exit(1)
        status["phase"] = value
    elif field == "priority":
        status["priority"] = int(value)
    elif field == "owner_agent":
        status["owner_agent"] = value if value != "null" else None
    elif field == "next_agent":
        status["next_agent"] = value if value != "null" else None
    elif field == "blockers":
        status["blockers"] = int(value)
    elif field == "warnings":
        status["warnings"] = int(value)
    elif field == "auto_fix_rounds_used":
        status["auto_fix_rounds_used"] = int(value)
    elif field in ("approvals.spec_approved", "approvals.merge_approved"):
        key = field.split(".")[1]
        status["approvals"][key] = value.lower() in ("true", "1", "yes")
    elif field.startswith("gates."):
        gate = field.split(".")[1]
        if value not in ("pending", "pass", "fail", "skipped"):
            print(f"ERROR: invalid gate value '{value}'. Valid: pending, pass, fail, skipped")
            sys.exit(1)
        status["gates"][gate] = value
    elif field.startswith("agents."):
        parts = field.split(".")
        agent_name = parts[1]
        agent_field = parts[2] if len(parts) > 2 else "verdict"
        if agent_name not in status["agents"]:
            print(f"ERROR: unknown agent '{agent_name}'")
            sys.exit(1)
        if agent_field == "completed_at":
            status["agents"][agent_name]["completed_at"] = value if value != "null" else None
        elif agent_field == "verdict":
            status["agents"][agent_name]["verdict"] = value if value != "null" else None
        elif agent_field == "auto_fix_rounds":
            status["agents"][agent_name]["auto_fix_rounds"] = int(value)
        elif agent_field == "blockers":
            status["agents"][agent_name]["blockers"] = int(value)
        elif agent_field == "warnings":
            status["agents"][agent_name]["warnings"] = int(value)
        else:
            print(f"ERROR: unknown agent field '{agent_field}'")
            sys.exit(1)
    else:
        print(f"ERROR: unknown field '{field}'")
        sys.exit(1)
    return status


def update_state_transition(status: dict, new_state: str, agent: str) -> dict:
    if new_state not in VALID_TASK_STATUSES:
        print(f"ERROR: invalid state '{new_state}'")
        sys.exit(1)

    old_state = status.get("status", "DRAFT")
    now = datetime.now(timezone.utc).isoformat()

    if status.get("lifecycle"):
        if status["lifecycle"].get("current_phase"):
            status["lifecycle"]["phase_history"].append({
                "phase": status["lifecycle"]["current_phase"],
                "entered_at": status["lifecycle"]["phase_entered_at"],
                "exited_at": now,
            })
        status["lifecycle"]["current_phase"] = new_state
        status["lifecycle"]["phase_entered_at"] = now

    status["status"] = new_state
    status["updated_at"] = now
    status["owner_agent"] = agent if agent else status.get("owner_agent")

    print(f"Transition: {old_state} -> {new_state} (agent={agent})")
    return status


def main():
    parser = argparse.ArgumentParser(description="Atomic status update for Hermes bus")
    parser.add_argument("task_id", help="Task ID (e.g. task-002-notification)")
    parser.add_argument("field", nargs="?", help="Field to update (e.g. status, phase, gates.lint)")
    parser.add_argument("value", nargs="?", help="New value for the field")
    parser.add_argument("--from-json", help="Replace entire STATUS.json from a JSON file")
    parser.add_argument("--state", help="Perform state transition to new status")
    parser.add_argument("--agent", help="Agent performing the update (for state transitions)")

    args = parser.parse_args()

    if args.from_json:
        with open(args.from_json, "r", encoding="utf-8") as f:
            new_status = json.load(f)
        new_status["updated_at"] = datetime.now(timezone.utc).isoformat()
        task_dir = find_task_dir(args.task_id)
        status_path = os.path.join(task_dir, "STATUS.json")
        atomic_write_json(status_path, new_status)
        print(f"OK: STATUS.json updated from file (atomic write)")
        return

    if args.state:
        status = read_status(args.task_id)
        status = update_state_transition(status, args.state, args.agent or "")
        task_dir = find_task_dir(args.task_id)
        status_path = os.path.join(task_dir, "STATUS.json")
        atomic_write_json(status_path, status)
        print(f"OK: state transition written (atomic)")
        return

    if not args.field or not args.value:
        parser.print_help()
        sys.exit(1)

    status = read_status(args.task_id)
    status = update_field(status, args.field, args.value)
    status["updated_at"] = datetime.now(timezone.utc).isoformat()

    task_dir = find_task_dir(args.task_id)
    status_path = os.path.join(task_dir, "STATUS.json")
    atomic_write_json(status_path, status)
    print(f"OK: {args.field} = {args.value}")


if __name__ == "__main__":
    main()