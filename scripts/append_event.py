#!/usr/bin/env python3
"""Append-only event writer for Hermes file-system bus.

Appends JSON events to events.log (JSONL format) with fsync.
Follows the append protocol from EVENT_BUS.md.

Usage:
    python scripts/append_event.py <task_id> <event_type> [--from-state <from>] [--to-state <to>] [--payload-json <json_str>]
    python scripts/append_event.py <task_id> <event_type> --payload-file <json_file>
    python scripts/append_event.py --from-event-file <json_file>

Examples:
    python scripts/append_event.py task-002-notification TASK_CREATED --to-state DRAFT --payload-json '{"title":"Notification MVP","priority":1}'
    python scripts/append_event.py task-002-notification STATE_TRANSITION --from-state DRAFT --to-state BUILDING --payload-json '{"message":"Build started","phase":"build","progress":10}'
    python scripts/append_event.py task-002-notification GATE_RESULT --payload-file gate_results.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

AGENT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".agent")
EVENTS_DIR = os.path.join(AGENT_ROOT, "events")
EVENTS_LOG = os.path.join(EVENTS_DIR, "events.log")

VALID_EVENT_TYPES = [
    "TASK_CREATED", "AGENT_ASSIGNED", "STATE_TRANSITION",
    "ARTIFACT_CREATED", "GATE_RESULT", "BLOCKER_FOUND",
    "ERROR", "RETRY_STARTED", "HUMAN_ACTION",
    "AGENT_RELEASED", "TASK_COMPLETED",
]

VALID_AGENTS = ["planner", "builder", "qa", "reviewer", "hermes", "human", "system"]
VALID_STATES = [
    "DRAFT", "PLANNING", "WAITING_SPEC_APPROVAL", "BUILDING",
    "AUTO_FIXING", "QA_RUNNING", "REVIEWING", "NEEDS_FIX",
    "WAITING_MERGE_APPROVAL", "MERGED", "FAILED", "CANCELLED",
]

TASK_SEQ_MAP = {}


def load_task_seq_map() -> dict:
    events_log = EVENTS_LOG
    if not os.path.isfile(events_log):
        return {}
    seq_map = {}
    with open(events_log, "r", encoding="utf-8") as f:
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


def extract_task_seq(task_id: str) -> int:
    global TASK_SEQ_MAP
    if task_id not in TASK_SEQ_MAP:
        try:
            num_part = task_id.split("-")[1]
            TASK_SEQ_MAP[task_id] = int(num_part)
        except (IndexError, ValueError):
            TASK_SEQ_MAP[task_id] = 999
    return TASK_SEQ_MAP[task_id]


def next_correlation_id(task_id: str) -> str:
    global TASK_SEQ_MAP
    if not TASK_SEQ_MAP:
        TASK_SEQ_MAP = load_task_seq_map()
    task_seq = extract_task_seq(task_id)
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

    print(f"OK: event appended | type={event['event_type']} | cid={event['correlation_id']}")


def build_event(args) -> dict:
    now = datetime.now(timezone.utc).isoformat()

    if args.payload_file:
        with open(args.payload_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    elif args.payload_json:
        payload = json.loads(args.payload_json)
    else:
        payload = {"message": f"{args.event_type} for {args.task_id}", "phase": "init", "progress": 0}

    if "message" not in payload:
        payload["message"] = f"{args.event_type} for {args.task_id}"
    if "phase" not in payload:
        payload["phase"] = "init"
    if "progress" not in payload:
        payload["progress"] = 0

    event = {
        "timestamp": now,
        "event_type": args.event_type,
        "task_id": args.task_id,
        "agent": args.agent or "system",
        "from_state": args.from_state,
        "to_state": args.to_state or args.from_state or "DRAFT",
        "payload": payload,
        "correlation_id": next_correlation_id(args.task_id),
    }
    return event


def main():
    parser = argparse.ArgumentParser(description="Append event to Hermes bus events.log")
    parser.add_argument("task_id", nargs="?", help="Task ID (e.g. task-002-notification)")
    parser.add_argument("event_type", nargs="?", help="Event type")
    parser.add_argument("--from-state", default=None, help="From state (optional)")
    parser.add_argument("--to-state", default=None, help="To state")
    parser.add_argument("--agent", default="system", help="Agent name (default: system)")
    parser.add_argument("--payload-json", help="Payload as JSON string")
    parser.add_argument("--payload-file", help="Payload from JSON file")
    parser.add_argument("--from-event-file", help="Complete event object from JSON file")

    args = parser.parse_args()

    if args.from_event_file:
        with open(args.from_event_file, "r", encoding="utf-8") as f:
            event = json.load(f)
        if "correlation_id" not in event:
            event["correlation_id"] = next_correlation_id(event.get("task_id", "task-000-unknown"))
        if "timestamp" not in event:
            event["timestamp"] = datetime.now(timezone.utc).isoformat()
        append_event(event)
        return

    if not args.task_id or not args.event_type:
        parser.print_help()
        sys.exit(1)

    if args.event_type not in VALID_EVENT_TYPES:
        print(f"ERROR: invalid event_type '{args.event_type}'. Valid: {VALID_EVENT_TYPES}")
        sys.exit(1)

    if args.agent not in VALID_AGENTS:
        print(f"ERROR: invalid agent '{args.agent}'. Valid: {VALID_AGENTS}")
        sys.exit(1)

    event = build_event(args)
    append_event(event)


if __name__ == "__main__":
    main()