#!/usr/bin/env python3
"""Build the read-only MOCKA_LIVING_CONTEXT_SNAPSHOT_v1 artifact.

This module intentionally does not update TODOs, ledgers, events, or Human Gate
state.  It projects the current canonical sources into a portable JSON or YAML
document so another AI can reuse the same observed state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "MOCKA_LIVING_CONTEXT_SNAPSHOT_v1"
ACTIVE_STATUSES = {"未着手", "進行中"}
BLOCKED_STATUS_MARKERS = ("保留", "ブロック", "blocked", "pending")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return default


def source_record(root: Path, relative_path: str, role: str) -> dict[str, Any]:
    path = root / relative_path
    record: dict[str, Any] = {
        "path": relative_path.replace("\\", "/"),
        "role": role,
        "exists": path.exists(),
        "read_only": True,
    }
    if path.exists():
        payload = path.read_bytes()
        record["sha256"] = hashlib.sha256(payload).hexdigest()
        record["modified_at"] = datetime.fromtimestamp(
            path.stat().st_mtime, timezone.utc
        ).isoformat().replace("+00:00", "Z")
    return record


def project_todo(todo: dict[str, Any]) -> dict[str, str]:
    return {
        "id": str(todo.get("id", "")),
        "status": str(todo.get("status", "")),
        "summary": str(todo.get("title", "")),
    }


def git_branch(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip() or "unknown"
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load_decisions(db_path: Path, limit: int = 20) -> list[dict[str, str]]:
    """Read only explicit decision records; never infer a decision from events."""
    if not db_path.exists():
        return []
    try:
        connection = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
        try:
            rows = connection.execute(
                "SELECT event_id, decision, reason, created_at "
                "FROM judgement_reason ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        finally:
            connection.close()
    except sqlite3.Error:
        return []
    return [
        {
            "id": str(event_id or ""),
            "status": str(status or ""),
            "summary": str(reason or ""),
            "recorded_at": str(recorded_at or ""),
        }
        for event_id, status, reason, recorded_at in rows
    ]


def contains_human_gate(item: dict[str, Any]) -> bool:
    searchable = " ".join(
        str(item.get(field, ""))
        for field in ("title", "description", "assigned_to", "note", "status")
    ).lower()
    return "human gate" in searchable or "人間ゲート" in searchable


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def to_yaml(value: Any, indent: int = 0) -> str:
    """Small dependency-free YAML serializer for the Snapshot's JSON-safe values."""
    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(to_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {yaml_scalar(item)}")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return f"{prefix}[]"
        lines = []
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append(f"{prefix}- {{}}")
                    continue
                first_key, first_value = next(iter(item.items()))
                if isinstance(first_value, (dict, list)):
                    lines.append(f"{prefix}- {first_key}:")
                    lines.append(to_yaml(first_value, indent + 4))
                else:
                    lines.append(f"{prefix}- {first_key}: {yaml_scalar(first_value)}")
                for key, nested in list(item.items())[1:]:
                    if isinstance(nested, (dict, list)):
                        lines.append(f"{prefix}  {key}:")
                        lines.append(to_yaml(nested, indent + 4))
                    else:
                        lines.append(f"{prefix}  {key}: {yaml_scalar(nested)}")
            elif isinstance(item, list):
                lines.append(f"{prefix}- ")
                lines.append(to_yaml(item, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{prefix}{yaml_scalar(value)}"


def build_snapshot(root: Path) -> dict[str, Any]:
    """Create one Snapshot from canonical sources without changing those sources."""
    overview = read_json(root / "data/MOCKA_OVERVIEW.json", {})
    todo_document = read_json(root / "data/MOCKA_TODO.json", {})
    todos = todo_document.get("todos", []) if isinstance(todo_document, dict) else []
    completed = todo_document.get("completed", []) if isinstance(todo_document, dict) else []
    todos = todos if isinstance(todos, list) else []
    completed = completed if isinstance(completed, list) else []

    active_raw = [todo for todo in todos if str(todo.get("status", "")) in ACTIVE_STATUSES]
    blocked_raw = [
        todo
        for todo in todos
        if any(marker in str(todo.get("status", "")).lower() for marker in BLOCKED_STATUS_MARKERS)
    ]
    immediate = overview.get("next_actions", {}).get("immediate", []) if isinstance(overview, dict) else []
    immediate = immediate if isinstance(immediate, list) else []
    issues = overview.get("current_issues", {}) if isinstance(overview, dict) else {}
    issues = issues if isinstance(issues, dict) else {}
    phase = str(overview.get("current_phase") or todo_document.get("current_phase", ""))
    next_boundary = str(immediate[0]) if immediate else "No immediate boundary is recorded."
    summary = phase
    if next_boundary and immediate:
        summary = f"{phase} Next boundary: {next_boundary}"

    sources = [
        source_record(root, "data/MOCKA_OVERVIEW.json", "phase, issues, and next boundary"),
        source_record(root, "data/MOCKA_TODO.json", "active, blocked, and completed work"),
        source_record(root, "data/lever_essence.json", "institutional context lineage (not summarized in v1)"),
        source_record(root, "data/mocka_events.db", "explicit decision records"),
        source_record(root, "runtime/main/ledger.json", "ledger lineage only; no decision status projection"),
        source_record(root, "gateway/context_builder.py", "existing Context Builder lineage"),
    ]
    db_path = root / "data/mocka_events.db"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": utc_now(),
        "project": {"name": "MoCKA", "phase": phase, "branch": git_branch(root)},
        "current_state": {"summary": summary},
        "completed": {"items": [project_todo(item) for item in completed]},
        "active": {"items": [project_todo(item) for item in active_raw]},
        "blocked": {"items": [project_todo(item) for item in blocked_raw]},
        "decisions": load_decisions(db_path),
        "unknowns": {
            "items": [f"{key}: {value}" for key, value in issues.items()]
            or ["No current issues are recorded in MOCKA_OVERVIEW.json."]
        },
        "next_boundary": {"description": next_boundary},
        "human_gate_required": any(contains_human_gate(item) for item in active_raw + blocked_raw),
        "source_lineage": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate MOCKA_LIVING_CONTEXT_SNAPSHOT_v1.")
    parser.add_argument("command", choices=["snapshot"], help="Command to execute.")
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
    parser.add_argument("--output", type=Path, help="Output file; stdout when omitted.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    snapshot = build_snapshot(args.root.resolve())
    output = (
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
        if args.format == "json"
        else to_yaml(snapshot) + "\n"
    )
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
