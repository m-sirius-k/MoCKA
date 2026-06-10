#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_session.py -- AI Command Session API (TODO_282 / TODO_279)
GET /api/session/start
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
import db_helper as db
from handshake import (
    CURRENT_PHASE, OPEN_ISSUES, _get_top_todo, _next_session_id,
)

from flask import Blueprint, jsonify, request

ai_session_bp = Blueprint('ai_session', __name__, url_prefix='/api')

JST = timezone(timedelta(hours=9))


def _recent_events(limit=20):
    rows = db.read_events(limit=limit)
    return [
        {
            "event_id": r.get("event_id"),
            "when": r.get("when_ts") or r.get("when"),
            "what_type": r.get("what_type"),
            "title": r.get("title"),
            "short_summary": r.get("short_summary"),
        }
        for r in rows
    ]


def _essence():
    try:
        conn = db._get_conn()
        rows = conn.execute("SELECT axis, content, source_count FROM essence").fetchall()
        conn.close()
        return [{"axis": r["axis"], "content": r["content"], "source_count": r["source_count"]} for r in rows]
    except Exception:
        return []


def _guidelines_top10():
    try:
        conn = db._get_conn()
        rows = conn.execute(
            "SELECT gl_id, category, score, action_summary "
            "FROM guidelines_reviewed WHERE verdict='KEEP' "
            "ORDER BY score DESC LIMIT 10"
        ).fetchall()
        conn.close()
        return [
            {"gl_id": r["gl_id"], "category": r["category"], "score": r["score"], "action_summary": r["action_summary"]}
            for r in rows
        ]
    except Exception:
        return []


def _capability_registry():
    return {
        "R01": {"name": "General", "capability": {"read": True, "write": True, "propose": True, "approve": False, "delete": False, "seal": False}},
        "R02": {"name": "Design Reviewer", "capability": {"read": True, "write": True, "propose": True, "approve": False, "delete": False, "seal": False}},
    }


def _progress():
    try:
        conn = db._get_conn()
        row = conn.execute("SELECT last_index, total, keep_count, skip_count, updated_at FROM guidelines_review_progress LIMIT 1").fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception:
        pass
    return {}


@ai_session_bp.route('/session/start', methods=['GET'])
def session_start():
    role = request.args.get("role", "R01")
    scope = request.args.get("scope", "mocka")
    mode = request.args.get("mode", "quick")

    now = datetime.now(JST)
    session_id = _next_session_id()

    response = {
        "session_id": session_id,
        "timestamp": now.isoformat(),
        "role": role,
        "scope": scope,
        "mode": mode,
        "current_phase": CURRENT_PHASE,
        "top_todo": _get_top_todo(5),
        "open_issues": OPEN_ISSUES,
    }

    if mode in ("resume", "full"):
        response["recent_decisions"] = []
        response["pending_review"] = []
        response["progress"] = _progress()

    if mode == "full":
        from reflection_engine import get_recent_reflections
        response["recent_events"] = _recent_events(20)
        response["essence"] = _essence()
        response["guidelines_top10"] = _guidelines_top10()
        response["capability_registry"] = _capability_registry()
        response["recent_reflections"] = get_recent_reflections(limit=3)
        response["warning"] = "full mode: token cost high"

    eid = db.get_next_event_id()
    db.write_event({
        "event_id": eid,
        "when": now.isoformat(),
        "who_actor": role,
        "what_type": "SESSION_START",
        "where_component": "interface/ai_session.py",
        "why_purpose": "AI Command Session API",
        "how_trigger": f"GET /api/session/start?mode={mode}",
        "title": f"Session Start: role={role} scope={scope} mode={mode}",
        "short_summary": f"session_id={session_id}",
        "trace_id": session_id,
    })

    return jsonify(response)
