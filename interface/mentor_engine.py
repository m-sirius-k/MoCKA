#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mentor_engine.py -- Mentor Engine (TODO_289)
新AIがHandshakeした瞬間に、関連する過去の監査済み経験を自動配布する。
GET /api/mentor?role=R02&scope=mocka&ai_id=gpt-4o
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
import db_helper as db
from prediction_engine import get_active_warnings, get_risk_prediction
from reflection_engine import get_recent_reflections

from flask import Blueprint, jsonify, request

mentor_bp = Blueprint('mentor', __name__, url_prefix='/api')

JST = timezone(timedelta(hours=9))

GUIDELINE_TRUST_THRESHOLD = 0.7


def _past_commissions(role: str, limit: int = 5) -> list[dict]:
    if not db.DB_PATH.exists():
        return []
    conn = db._get_conn()
    rows = conn.execute(
        "SELECT event_id, when_ts, title, short_summary, what_type "
        "FROM events WHERE what_type IN ('SEAL_READY','CHANGE_DONE') "
        "ORDER BY when_ts DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()

    commissions = []
    for r in rows:
        commissions.append({
            "commission_id": r["event_id"],
            "outcome": "SUCCESS" if r["what_type"] == "SEAL_READY" else "DONE",
            "key_learning": (r["short_summary"] or r["title"] or "")[:200],
        })
    return commissions


def _applicable_guidelines(limit: int = 10) -> list[dict]:
    try:
        conn = db._get_conn()
        rows = conn.execute(
            "SELECT gl_id, category, score, action_summary "
            "FROM guidelines_reviewed WHERE verdict='KEEP' AND score > ? "
            "ORDER BY score DESC LIMIT ?",
            (GUIDELINE_TRUST_THRESHOLD, limit)
        ).fetchall()
        conn.close()
        return [
            {"gl_id": r["gl_id"], "category": r["category"], "trust_score": r["score"], "action_summary": r["action_summary"]}
            for r in rows
        ]
    except Exception:
        return []


def _institution_memory_snapshot() -> dict:
    from handshake import CURRENT_PHASE, _get_top_todo

    todo_path = Path(db.MOCKA_ROOT) / "data" / "MOCKA_TODO.json"
    active_todos = 0
    try:
        data = json.loads(todo_path.read_text(encoding="utf-8"))
        active_todos = len([t for t in data.get("todos", []) if t.get("status") not in ("完了", "done", "DONE")])
    except Exception:
        pass

    return {
        "total_events": db.count_events(),
        "active_todos": active_todos,
        "current_phase": CURRENT_PHASE,
        "top_todo": _get_top_todo(3),
    }


def get_mentor_package(role: str, scope: str, ai_id: str) -> dict:
    from handshake import ROLE_REGISTRY

    role_info = ROLE_REGISTRY.get(role, ROLE_REGISTRY["R01"])

    past_commissions = _past_commissions(role)
    applicable_guidelines = _applicable_guidelines()
    known_risks = get_active_warnings()
    reflections = get_recent_reflections(limit=3)
    snapshot = _institution_memory_snapshot()

    handover_lines = []
    if known_risks:
        handover_lines.append("既知のリスク: " + " / ".join(known_risks))
    if past_commissions:
        handover_lines.append(f"直近の完了作業: {past_commissions[0]['key_learning']}")
    if reflections and reflections[0].get("why_happened") not in (None, "no structural pattern matched"):
        handover_lines.append(f"直近セッションの構造: {reflections[0]['why_happened']}")
    if not handover_lines:
        handover_lines.append("特記事項なし。top_todoを確認の上、指示に従って着手してください。")

    return {
        "mentor_package": {
            "role": role,
            "ai_id": ai_id,
            "message": f"あなたは{role_info['name']}として参加します。",
            "past_commissions": past_commissions,
            "applicable_guidelines": applicable_guidelines,
            "known_risks": known_risks,
            "risk_prediction": get_risk_prediction(),
            "recent_reflections": reflections,
            "institution_memory_snapshot": snapshot,
            "handover_message": " / ".join(handover_lines),
        }
    }


@mentor_bp.route('/mentor', methods=['GET'])
def mentor():
    role = request.args.get("role", "R01")
    scope = request.args.get("scope", "mocka")
    ai_id = request.args.get("ai_id", "unknown")
    return jsonify(get_mentor_package(role, scope, ai_id))
