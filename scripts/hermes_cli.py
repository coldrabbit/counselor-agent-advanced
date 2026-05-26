#!/usr/bin/env python3
"""Hermes bus CLI tool — command-line interface for the Hermes file-system status bus.

Commands:
    hermes status                  Show factory global status summary
    hermes tasks                   List all active tasks
    hermes task <task_id>          Show task STATUS.json details
    hermes events [--last N]       Show last N events from events.log
    hermes events --filter <type>  Filter events by event_type
    hermes validate [--strict]     Run validation on all bus files
    hermes update <task_id> ...    Update task status (see update_status.py)
    hermes append <task_id> ...    Append event (see append_event.py)
    hermes infra                   Show infrastructure report

Usage:
    python scripts/hermes_cli.py <command> [options]
"""

import argparse
import json
import os
import subprocess
import sys

AGENT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agent")
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_status(args):
    global_path = os.path.join(AGENT_ROOT, "status", "global.json")
    data = load_json(global_path)
    if not data:
        print("ERROR: global.json not found or empty")
        sys.exit(1)

    factory = data.get("factory", {})
    agents = data.get("agents", {})
    stats = data.get("stats", {})

    print(f"Factory: {factory.get('name', 'N/A')} v{factory.get('version', 'N/A')}")
    print(f"Phase:   {factory.get('phase', 'N/A')}")
    print(f"Level:   {factory.get('maturity_level', 'N/A')}")
    print(f"Updated: {factory.get('last_updated', 'N/A')}")
    print()
    print("Agents:")
    for name, info in agents.items():
        status = info.get("status", "unknown")
        task = info.get("current_task") or "-"
        print(f"  {name:12s} status={status:8s} task={task}")
    print()
    print("Stats:")
    for key, val in stats.items():
        print(f"  {key:24s} = {val}")


def cmd_tasks(args):
    active_path = os.path.join(AGENT_ROOT, "status", "active_tasks.json")
    data = load_json(active_path)
    if not data:
        print("ERROR: active_tasks.json not found or empty")
        sys.exit(1)

    summary = data.get("summary", {})
    print(f"Tasks Summary: total={summary.get('total',0)} active={summary.get('active',0)} "
          f"queued={summary.get('queued',0)} completed={summary.get('completed',0)} "
          f"failed={summary.get('failed',0)} blocked={summary.get('blocked',0)}")
    print()

    for task in data.get("tasks", []):
        tid = task.get("task_id", "?")
        title = task.get("title", "?")
        status = task.get("status", "?")
        phase = task.get("phase", "?")
        owner = task.get("owner_agent") or "-"
        priority = task.get("priority", "?")
        blockers = task.get("blockers", 0)
        print(f"  {tid:30s} [{status:25s}] phase={phase:10s} owner={owner:10s} p={priority} b={blockers}")
        print(f"    title: {title}")


def cmd_task(args):
    task_id = args.task_id
    status_path = os.path.join(AGENT_ROOT, "tasks", task_id, "STATUS.json")
    data = load_json(status_path)
    if not data:
        print(f"ERROR: STATUS.json not found for {task_id}")
        sys.exit(1)

    print(f"Task:     {data.get('task_id', '?')}")
    print(f"Title:    {data.get('title', '?')}")
    print(f"Status:   {data.get('status', '?')}")
    print(f"Phase:    {data.get('phase', '?')}")
    print(f"Priority: {data.get('priority', '?')}")
    print(f"Owner:    {data.get('owner_agent') or 'unassigned'}")
    print(f"Next:     {data.get('next_agent') or 'none'}")
    print(f"Created:  {data.get('created_at', '?')}")
    print(f"Updated:  {data.get('updated_at', '?')}")
    print(f"Blockers: {data.get('blockers', 0)}  Warnings: {data.get('warnings', 0)}")
    print(f"Auto-fix: {data.get('auto_fix_rounds_used', 0)}/{data.get('max_auto_fix_rounds', 3)}")
    print()

    gates = data.get("gates", {})
    print("Gates:")
    for gate, val in gates.items():
        icon = "+" if val == "pass" else "-" if val == "fail" else "." if val == "pending" else "s"
        print(f"  {gate:12s} [{icon}] {val}")

    print()
    approvals = data.get("approvals", {})
    print(f"Approvals: spec={approvals.get('spec_approved', False)} merge={approvals.get('merge_approved', False)}")

    agents = data.get("agents", {})
    if agents:
        print()
        print("Agents:")
        for name, info in agents.items():
            verdict = info.get("verdict") or "pending"
            completed = info.get("completed_at") or "-"
            print(f"  {name:12s} verdict={verdict:12s} completed={completed}")

    hermes = data.get("hermes", {})
    if hermes:
        print()
        print(f"Hermes: reported={hermes.get('last_reported_at') or '-'} "
              f"notified={hermes.get('notifications_sent', 0)} "
              f"pending={len(hermes.get('pending_notifications', []))}")


def cmd_events(args):
    events_log = os.path.join(AGENT_ROOT, "events", "events.log")
    if not os.path.isfile(events_log):
        print("ERROR: events.log not found")
        sys.exit(1)

    lines = []
    with open(events_log, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            lines.append(line)

    if args.filter:
        filtered = []
        for line in lines:
            try:
                evt = json.loads(line)
                if evt.get("event_type") == args.filter:
                    filtered.append(evt)
            except json.JSONDecodeError:
                continue
        print(f"Events filtered by '{args.filter}': {len(filtered)} found")
        for evt in filtered:
            ts = evt.get("timestamp", "?")
            tid = evt.get("task_id", "?")
            agent = evt.get("agent", "?")
            from_s = evt.get("from_state") or "-"
            to_s = evt.get("to_state", "?")
            cid = evt.get("correlation_id", "?")
            msg = evt.get("payload", {}).get("message", "")
            print(f"  {ts} | {tid} | {agent} | {from_s} -> {to_s} | {cid} | {msg}")
        return

    n = args.last or len(lines)
    recent = lines[-n:]
    print(f"Events (last {n} of {len(lines)}):")
    for line in recent:
        try:
            evt = json.loads(line)
            ts = evt.get("timestamp", "?")
            etype = evt.get("event_type", "?")
            tid = evt.get("task_id", "?")
            from_s = evt.get("from_state") or "-"
            to_s = evt.get("to_state", "?")
            cid = evt.get("correlation_id", "?")
            print(f"  {ts} | {etype:20s} | {tid} | {from_s} -> {to_s} | {cid}")
        except json.JSONDecodeError:
            print(f"  [PARSE ERROR] {line[:80]}")


def cmd_validate(args):
    script = os.path.join(SCRIPTS_DIR, "validate_status.py")
    cmd = [sys.executable, script]
    if args.strict:
        cmd.append("--strict")
    if args.task:
        cmd.extend(["--task", args.task])
    elif args.global_only:
        cmd.append("--global")
    elif args.events_only:
        cmd.append("--events")
    elif args.active_only:
        cmd.append("--active")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def cmd_update(args):
    script = os.path.join(SCRIPTS_DIR, "update_status.py")
    cmd = [sys.executable, script] + args.update_args
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def cmd_append(args):
    script = os.path.join(SCRIPTS_DIR, "append_event.py")
    cmd = [sys.executable, script] + args.append_args
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def cmd_infra(args):
    print("=" * 60)
    print("  HERMES BUS INFRASTRUCTURE REPORT")
    print("=" * 60)
    print()

    dirs = {
        "status": os.path.join(AGENT_ROOT, "status"),
        "events": os.path.join(AGENT_ROOT, "events"),
        "queue": os.path.join(AGENT_ROOT, "queue"),
        "logs": os.path.join(AGENT_ROOT, "logs"),
        "tasks": os.path.join(AGENT_ROOT, "tasks"),
        "templates": os.path.join(AGENT_ROOT, "templates"),
        "templates/schemas": os.path.join(AGENT_ROOT, "templates", "schemas"),
        "prompts": os.path.join(AGENT_ROOT, "prompts"),
        "reports": os.path.join(AGENT_ROOT, "reports"),
    }

    print("Directory Structure:")
    for name, path in dirs.items():
        exists = os.path.isdir(path)
        count = 0
        if exists:
            count = len([f for f in os.listdir(path) if not f.startswith(".")])
        status_icon = "OK" if exists else "MISSING"
        print(f"  .agent/{name:20s} [{status_icon}] files={count}")
    print()

    print("Status Files:")
    status_files = [
        ("global.json", os.path.join(AGENT_ROOT, "status", "global.json")),
        ("active_tasks.json", os.path.join(AGENT_ROOT, "status", "active_tasks.json")),
        ("current.json", os.path.join(AGENT_ROOT, "status", "current.json")),
    ]
    for name, path in status_files:
        exists = os.path.isfile(path)
        size = os.path.getsize(path) if exists else 0
        valid = "valid" if exists else "missing"
        if exists:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    json.load(f)
                valid = "valid JSON"
            except json.JSONDecodeError:
                valid = "INVALID JSON"
        print(f"  {name:20s} [{valid}] size={size}B")
    print()

    print("Task Status Files:")
    tasks_dir = os.path.join(AGENT_ROOT, "tasks")
    if os.path.isdir(tasks_dir):
        for entry in sorted(os.listdir(tasks_dir)):
            task_path = os.path.join(tasks_dir, entry)
            if os.path.isdir(task_path) and entry.startswith("task-"):
                status_path = os.path.join(task_path, "STATUS.json")
                has_status = os.path.isfile(status_path)
                files = [f for f in os.listdir(task_path) if not f.startswith(".")]
                print(f"  {entry:35s} STATUS={has_status} files={len(files)}")
    print()

    print("Events Log:")
    events_log = os.path.join(AGENT_ROOT, "events", "events.log")
    if os.path.isfile(events_log):
        line_count = 0
        with open(events_log, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    line_count += 1
        size = os.path.getsize(events_log)
        print(f"  events.log: {line_count} events, {size}B")
    else:
        print(f"  events.log: not found")
    print()

    print("Schema Files:")
    schemas_dir = os.path.join(AGENT_ROOT, "templates", "schemas")
    if os.path.isdir(schemas_dir):
        for f in sorted(os.listdir(schemas_dir)):
            if f.endswith(".json"):
                size = os.path.getsize(os.path.join(schemas_dir, f))
                print(f"  {f:30s} {size}B")
    else:
        print("  No schemas directory")
    print()

    print("Scripts:")
    scripts = [
        ("update_status.py", os.path.join(SCRIPTS_DIR, "update_status.py")),
        ("append_event.py", os.path.join(SCRIPTS_DIR, "append_event.py")),
        ("validate_status.py", os.path.join(SCRIPTS_DIR, "validate_status.py")),
        ("hermes_cli.py", os.path.join(SCRIPTS_DIR, "hermes_cli.py")),
    ]
    for name, path in scripts:
        exists = os.path.isfile(path)
        size = os.path.getsize(path) if exists else 0
        status_icon = "OK" if exists else "MISSING"
        print(f"  {name:25s} [{status_icon}] {size}B")
    print()

    print("=" * 60)
    print("  Run validation: python scripts/validate_status.py")
    print("  CLI: python scripts/hermes_cli.py <command>")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Hermes bus CLI — command-line interface for the Hermes file-system status bus",
        prog="hermes_cli",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("status", help="Show factory global status summary")
    subparsers.add_parser("tasks", help="List all active tasks")
    p_task = subparsers.add_parser("task", help="Show task STATUS.json details")
    p_task.add_argument("task_id", help="Task ID")

    p_events = subparsers.add_parser("events", help="Show events from events.log")
    p_events.add_argument("--last", type=int, default=20, help="Show last N events")
    p_events.add_argument("--filter", help="Filter by event_type")

    p_validate = subparsers.add_parser("validate", help="Validate Hermes bus files")
    p_validate.add_argument("--strict", action="store_true", help="Strict jsonschema validation")
    p_validate.add_argument("--task", help="Validate specific task")
    p_validate.add_argument("--global", dest="global_only", action="store_true", help="Validate global.json only")
    p_validate.add_argument("--events", dest="events_only", action="store_true", help="Validate events.log only")
    p_validate.add_argument("--active", dest="active_only", action="store_true", help="Validate active_tasks.json only")

    p_update = subparsers.add_parser("update", help="Update task status (delegates to update_status.py)")
    p_update.add_argument("update_args", nargs="+", help="Arguments for update_status.py")

    p_append = subparsers.add_parser("append", help="Append event (delegates to append_event.py)")
    p_append.add_argument("append_args", nargs="+", help="Arguments for append_event.py")

    subparsers.add_parser("infra", help="Show infrastructure report")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "status": cmd_status,
        "tasks": cmd_tasks,
        "task": cmd_task,
        "events": cmd_events,
        "validate": cmd_validate,
        "update": cmd_update,
        "append": cmd_append,
        "infra": cmd_infra,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()