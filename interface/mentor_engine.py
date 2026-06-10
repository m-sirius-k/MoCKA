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


_STRATEGY_BY_ROLE = {
    "R01": "top_todoの最優先項目から着手し、ファイル変更前後でmocka_write_event(CHANGE_START/CHANGE_DONE)を必ず記録すること。",
    "R02": "設計提案・TODO依存関係をレビューし、known_risksに該当する変更には特に注意してリスク分析コメントを残すこと。",
}


def _institution_focus() -> str:
    try:
        conn = db._get_conn()
        row = conn.execute(
            "SELECT content FROM essence WHERE axis = 'PHILOSOPHY' ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if row and row["content"]:
            return row["content"][:200]
    except Exception:
        pass
    return "記録なき作業はMoCKAとして存在しない（Structure / Record / Verification）"


def generate_briefing(role: str, scope: str, mentor_data: dict) -> dict:
    from handshake import CURRENT_PHASE, OPEN_ISSUES, _get_top_todo

    top_todo = _get_top_todo(1)
    top_priority = top_todo[0]["title"] if top_todo else "アクティブなTODOなし"

    mission = f"{CURRENT_PHASE}において、最優先TODO「{top_priority}」を進めること。"

    risk_prediction = mentor_data.get("risk_prediction", {})
    high_risk_areas = risk_prediction.get("high_risk_areas", [])[:3]
    known_risks = [area["mitigation"] for area in high_risk_areas]
    known_risks += OPEN_ISSUES

    strategy = _STRATEGY_BY_ROLE.get(role, _STRATEGY_BY_ROLE["R01"])
    if known_risks:
        strategy += f" 特に注意: {known_risks[0]}"

    return {
        "mission": mission,
        "top_priority": top_priority,
        "known_risks": known_risks,
        "institution_focus": _institution_focus(),
        "recommended_strategy": strategy,
    }


@mentor_bp.route('/mentor', methods=['GET'])
def mentor():
    role = request.args.get("role", "R01")
    scope = request.args.get("scope", "mocka")
    ai_id = request.args.get("ai_id", "unknown")
    return jsonify(get_mentor_package(role, scope, ai_id))
