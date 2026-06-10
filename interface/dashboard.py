#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dashboard.py -- Institutional Dashboard API (TODO_283)
GET /api/dashboard
"""

import sys
import socket
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
import db_helper as db
from handshake import CURRENT_PHASE, CONTRACT_SEAL, _get_top_todo

from flask import Blueprint, jsonify

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

JST = timezone(timedelta(hours=9))
CACHE_TTL = 30  # seconds

_cache = {"data": None, "ts": 0}

CONNECTORS = {
    "mcp_caliber": ("127.0.0.1", 5002),
    "command_center": ("127.0.0.1", 5000),
    "caliber_pipeline": ("127.0.0.1", 5679),
}


def _check_port(host, port, timeout=0.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "up"
    except Exception:
        return "down"


def _recent_events(limit=10):
    rows = db.read_events(limit=limit)
    return [
        {
            "event_id": r.get("event_id"),
            "when": r.get("when_ts") or r.get("when"),
            "what_type": r.get("what_type"),
            "title": r.get("title"),
        }
        for r in rows
    ]


def _filtered_events(keyword, limit=10):
    try:
        conn = db._get_conn()
        rows = conn.execute(
            "SELECT event_id, when_ts, title, short_summary, free_note "
            "FROM events WHERE title LIKE ? OR free_note LIKE ? "
            "ORDER BY when_ts DESC LIMIT ?",
            (f"%{keyword}%", f"%{keyword}%", limit)
        ).fetchall()
        conn.close()
        return [
            {"event_id": r["event_id"], "when": r["when_ts"], "title": r["title"], "short_summary": r["short_summary"]}
            for r in rows
        ]
    except Exception:
        return []


def _knowledge_summary():
    summary = {"total_events": 0, "total_todos_active": 0, "guidelines_count": 0}
    try:
        conn = db._get_conn()
        summary["total_events"] = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        summary["guidelines_count"] = conn.execute("SELECT COUNT(*) FROM guidelines_reviewed").fetchone()[0]
        conn.close()
    except Exception:
        pass
    summary["total_todos_active"] = len(_get_top_todo(1000))
    return summary


def _build_dashboard():
    now = datetime.now(JST)
    return {
        "project_status": {
            "phase": CURRENT_PHASE,
            "seal": CONTRACT_SEAL,
            "last_updated": now.strftime("%Y-%m-%d"),
        },
        "top_todo": _get_top_todo(10),
        "recent_events": _recent_events(10),
        "open_incidents": _filtered_events("INCIDENT", 10),
        "pending_reviews": _filtered_events("REVIEW", 10),
        "active_connectors": {
            name: {"port": port, "status": _check_port(host, port)}
            for name, (host, port) in CONNECTORS.items()
        },
        "knowledge_summary": _knowledge_summary(),
        "generated_at": now.isoformat(),
    }


@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    now_ts = time.time()
    if _cache["data"] is not None and (now_ts - _cache["ts"]) < CACHE_TTL:
        return jsonify(_cache["data"])

    data = _build_dashboard()
    _cache["data"] = data
    _cache["ts"] = now_ts
    return jsonify(data)
