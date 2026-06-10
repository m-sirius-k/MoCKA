#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reflection_engine.py -- Reflection Engine (TODO_287)
Commission/Session終了時に「なぜ起きたか」を自動構造化する。
GET  /api/reflection?session_id=...
POST /api/reflection/generate
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import db_helper as db
from structural import morphology

from flask import Blueprint, jsonify, request

reflection_bp = Blueprint('reflection', __name__, url_prefix='/api')

JST = timezone(timedelta(hours=9))


def _events_for_session(session_id: str) -> list[dict]:
    if not db.DB_PATH.exists():
        return []
    conn = db._get_conn()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM events WHERE trace_id = ? ORDER BY when_ts ASC",
        (session_id,)
    ).fetchall()]
    conn.close()
    for r in rows:
        if "when_ts" in r:
            r["when"] = r.pop("when_ts")
    return rows


def _recent_session_ids(limit: int = 3) -> list[str]:
    if not db.DB_PATH.exists():
        return []
    conn = db._get_conn()
    rows = conn.execute(
        "SELECT DISTINCT trace_id FROM events "
        "WHERE what_type = 'SESSION_START' AND trace_id IS NOT NULL "
        "ORDER BY when_ts DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]


def generate_reflection(session_id: str, commission_id: str = None) -> dict:
    events = _events_for_session(session_id)

    what_happened = "; ".join(
        f"{e.get('what_type')}: {e.get('title')}" for e in events
    ) or "no events recorded for this session"

    text = " ".join(
        f"{e.get('title') or ''} {e.get('short_summary') or ''}" for e in events
    ).strip()

    pattern_match = []
    why_happened = "no structural pattern matched"
    confidence = 0.0
    if text:
        result = morphology.analyze(text, source_event_id=session_id)
        if result["structures"]:
            why_happened = ", ".join(result["structures"])
            pattern_match = result["tag_details"]
            confidence = min(1.0, 0.3 + 0.1 * len(result["structures"]))
        else:
            confidence = 0.1

    guideline_candidates = []
    for e in events:
        if e.get("what_type") in ("INCIDENT", "DEVIATION") or (e.get("risk_level") or "").lower() in ("high", "critical"):
            guideline_candidates.append({
                "event_id": e.get("event_id"),
                "title": e.get("title"),
                "reason": "high risk / incident event in this session",
            })

    return {
        "session_id": session_id,
        "commission_id": commission_id,
        "what_happened": what_happened,
        "why_happened": why_happened,
        "pattern_match": pattern_match,
        "guideline_candidates": guideline_candidates,
        "confidence": round(confidence, 2),
        "generated_at": datetime.now(JST).isoformat(),
    }


def get_recent_reflections(limit: int = 3) -> list[dict]:
    return [generate_reflection(sid) for sid in _recent_session_ids(limit)]


@reflection_bp.route('/reflection', methods=['GET'])
def reflection_get():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id は必須です"}), 400
    return jsonify(generate_reflection(session_id))


@reflection_bp.route('/reflection/generate', methods=['POST'])
def reflection_generate():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    commission_id = data.get("commission_id")
    if not session_id:
        return jsonify({"error": "session_id は必須です"}), 400

    reflection = generate_reflection(session_id, commission_id)

    eid = db.get_next_event_id()
    db.write_event({
        "event_id": eid,
        "when": datetime.now(JST).isoformat(),
        "who_actor": "reflection_engine",
        "what_type": "REFLECTION",
        "where_component": "interface/reflection_engine.py",
        "why_purpose": "Reflection Engine",
        "how_trigger": "POST /api/reflection/generate",
        "title": f"Reflection generated for {session_id}",
        "short_summary": reflection["why_happened"][:200],
        "trace_id": session_id,
    })

    return jsonify(reflection)
