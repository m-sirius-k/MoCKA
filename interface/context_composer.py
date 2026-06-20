#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
context_composer.py -- Context Composer (TODO_290)
Reflection / Prediction / Mentor / Institution を
ひとつの working_context に統合する。
GET /api/context/compose
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
import db_helper as db
from handshake import CURRENT_PHASE, OPEN_ISSUES, _get_top_todo, _next_session_id, ROLE_REGISTRY
from prediction_engine import get_active_warnings, get_risk_prediction
from reflection_engine import get_recent_reflections
from mentor_engine import get_mentor_package

from flask import Blueprint, jsonify, request

context_bp = Blueprint('context_composer', __name__, url_prefix='/api')

JST = timezone(timedelta(hours=9))
INSTITUTION_DIR = Path(db.MOCKA_ROOT) / "data" / "institution"


def _essence():
    try:
        conn = db._get_conn()
        rows = conn.execute("SELECT axis, content, source_count FROM essence").fetchall()
        conn.close()
        return [{"axis": r["axis"], "content": r["content"], "source_count": r["source_count"]} for r in rows]
    except Exception:
        return []


def _guidelines_top5():
    try:
        conn = db._get_conn()
        rows = conn.execute(
            "SELECT gl_id, category, score, action_summary "
            "FROM guidelines_reviewed WHERE verdict='KEEP' "
            "ORDER BY score DESC LIMIT 5"
        ).fetchall()
        conn.close()
        return [
            {"gl_id": r["gl_id"], "category": r["category"], "score": r["score"], "action_summary": r["action_summary"]}
            for r in rows
        ]
    except Exception:
        return []


def _recent_decisions(days: int = 30, limit: int = 10) -> list[dict]:
    try:
        conn = db._get_conn()
        cutoff = (datetime.now(JST) - timedelta(days=days)).isoformat()
        rows = conn.execute(
            "SELECT event_id, when_ts, title, short_summary FROM events "
            "WHERE what_type = 'DECISION_APPROVED' AND when_ts >= ? "
            "ORDER BY when_ts DESC LIMIT ?",
            (cutoff, limit)
        ).fetchall()
        conn.close()
        return [
            {"event_id": r["event_id"], "when": r["when_ts"], "title": r["title"], "short_summary": r["short_summary"]}
            for r in rows
        ]
    except Exception:
        return []


def _relevant_decisions(days: int = 7) -> list[dict]:
    return _recent_decisions(days=days, limit=5)


def _institution_rules() -> dict:
    rules = {"universal_rules": [], "trust_levels": {}}
    try:
        v2 = json.loads((INSTITUTION_DIR / "institution_contract_v2.json").read_text(encoding="utf-8"))
        rules["universal_rules"] = v2.get("universal_rules", [])
        rules["trust_levels"] = v2.get("trust_levels", {})
    except Exception:
        pass
    rules["guidelines_top5"] = _guidelines_top5()
    return rules


def _applicable_templates(role: str) -> dict:
    role_info = ROLE_REGISTRY.get(role, ROLE_REGISTRY["R01"])
    commissions = []
    try:
        data = json.loads((INSTITUTION_DIR / "commission_registry.json").read_text(encoding="utf-8"))
        commissions = [c for c in data.get("commissions", []) if c.get("status") == "active"]
    except Exception:
        pass
    return {
        "role_capability": role_info.get("capability", {}),
        "active_commissions": commissions,
    }


def _past_failure_patterns() -> list[str]:
    warnings = get_active_warnings()
    risk = get_risk_prediction()
    patterns = list(warnings)
    for area in risk.get("high_risk_areas", [])[:5]:
        patterns.append(f"{area.get('component')}/{area.get('risk_type')}: {area.get('mitigation')}")
    return patterns


class ContextComposer:
    """
    Reflection + Prediction + Mentor + Institution を
    一つのworking_contextに統合する。
    """

    def compose(self, role: str = "R01", mode: str = "full", ai_id: str = "unknown", scope: str = "mocka") -> dict:
        session_id = _next_session_id()
        mentor_data = get_mentor_package(role, scope, ai_id)["mentor_package"]

        working_context = {
            "session_id": session_id,
            "role": role,
            "mode": mode,
            "priority": _get_top_todo(3),
            "objectives": {
                "current_phase": CURRENT_PHASE,
                "open_issues": OPEN_ISSUES,
            },
            "known_risks": get_active_warnings(),
            "relevant_decisions": _relevant_decisions(days=7),
            "institution_rules": _institution_rules(),
            "applicable_templates": _applicable_templates(role),
            "past_failures": _past_failure_patterns(),
            "recommended_strategy": mentor_data,
            "decision_history": _recent_decisions(days=30),
            "essence": _essence(),
        }

        now = datetime.now(JST)
        from event_buffer import get_buffer  # Phase5-1: db.write_event直接禁止 → Gate経由
        get_buffer().push({
            "when": now.isoformat(),
            "who_actor": role,
            "what_type": "CONTEXT_COMPOSE",
            "where_component": "interface/context_composer.py",
            "why_purpose": "Context Composer",
            "how_trigger": f"GET /api/context/compose?mode={mode}&role={role}",
            "title": f"Context Compose: role={role} mode={mode}",
            "short_summary": f"session_id={session_id}",
            "trace_id": session_id,
        })

        return {
            "working_context": working_context,
            "generated_at": now.isoformat(),
            "expires_in_seconds": 3600,
        }


@context_bp.route('/context/compose', methods=['GET'])
def api_context_compose():
    role = request.args.get('role', 'R01')
    mode = request.args.get('mode', 'full')
    ai_id = request.args.get('ai_id', 'unknown')
    scope = request.args.get('scope', 'mocka')
    composer = ContextComposer()
    return jsonify(composer.compose(role=role, mode=mode, ai_id=ai_id, scope=scope))
