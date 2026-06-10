#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
handshake.py -- Institution Handshake Protocol (TODO_282)
AIがMoCKAに参加する際の「朝礼」プロトコル。
POST /api/handshake
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
import db_helper as db

from flask import Blueprint, jsonify, request

handshake_bp = Blueprint('handshake', __name__, url_prefix='/api')

CONTRACT_VERSION = "1.0"
CONTRACT_SEAL = "5641bd41"
JST = timezone(timedelta(hours=9))

VALID_SCOPES = {"mocka", "vasai", "mini-mocka", "all"}

ROLE_REGISTRY = {
    "R01": {
        "name": "General",
        "responsibilities": "汎用作業。指示書に基づくタスク実行。",
        "capability": {"read": True, "write": True, "propose": True, "approve": False, "delete": False, "seal": False},
        "trust_level": "Verified",
    },
    "R02": {
        "name": "Design Reviewer",
        "responsibilities": "設計提案のレビュー。TODO依存関係・リスク分析。",
        "capability": {"read": True, "write": True, "propose": True, "approve": False, "delete": False, "seal": False},
        "trust_level": "Verified",
    },
}

CURRENT_PHASE = "Phase 4: 商用製品展開フェーズ"

OPEN_ISSUES = [
    "relay_dom_selector_fail: health_check.pyがFAIL判定中",
    "tic_tech_watcher_noise: 動的コンテンツ誤検知リスク",
]


def _get_top_todo(limit=5):
    import json
    todo_path = Path(db.MOCKA_ROOT) / "data" / "MOCKA_TODO.json"
    try:
        data = json.loads(todo_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    todos = [t for t in data.get("todos", []) if t.get("status") not in ("完了", "done", "DONE")]
    priority_order = {"最高": 0, "高": 1, "中": 2, "低": 3}
    todos.sort(key=lambda t: priority_order.get(t.get("priority"), 9))
    return [
        {"id": t.get("id"), "priority": t.get("priority"), "title": t.get("title")}
        for t in todos[:limit]
    ]


def _next_session_id():
    now = datetime.now(JST)
    return f"SESSION_{now.strftime('%Y%m%d_%H%M%S')}"


@handshake_bp.route('/handshake', methods=['POST'])
def handshake():
    data = request.get_json(silent=True) or {}

    ai_id = data.get("ai_id")
    role = data.get("role")
    scope = data.get("scope")
    contract_version = data.get("contract_version")

    if not ai_id or not role or not scope:
        return jsonify({"error": "ai_id, role, scope は必須です"}), 400

    if contract_version and contract_version != CONTRACT_VERSION:
        return jsonify({
            "handshake": "VERSION_MISMATCH",
            "contract_version": CONTRACT_VERSION,
            "received_version": contract_version,
        }), 200

    if scope not in VALID_SCOPES:
        return jsonify({"error": f"scope は {sorted(VALID_SCOPES)} のいずれかを指定してください"}), 400

    role_info = ROLE_REGISTRY.get(role, ROLE_REGISTRY["R01"])
    capability = dict(role_info["capability"])

    observation_mode = bool(data.get("observation_mode", False))
    if observation_mode:
        capability["write"] = False
        capability["propose"] = False

    session_id = _next_session_id()
    now = datetime.now(JST)

    from prediction_engine import get_active_warnings
    from mentor_engine import get_mentor_package

    response = {
        "handshake": "READY",
        "contract_version": CONTRACT_VERSION,
        "contract_seal": CONTRACT_SEAL,
        "ai_id": ai_id,
        "role": {
            "id": role,
            "name": role_info["name"],
            "responsibilities": role_info["responsibilities"],
        },
        "capability": capability,
        "permission": {
            "scope": scope,
            "observation_mode": observation_mode,
            "trust_level": role_info["trust_level"],
        },
        "current_phase": CURRENT_PHASE,
        "top_todo": _get_top_todo(5),
        "open_issues": OPEN_ISSUES,
        "pending_review": [],
        "recent_decisions": [],
        "warnings": get_active_warnings(),
        "mentor_package": get_mentor_package(role, scope, ai_id)["mentor_package"],
        "session_id": session_id,
        "timestamp": now.isoformat(),
    }

    eid = db.get_next_event_id()
    db.write_event({
        "event_id": eid,
        "when": now.isoformat(),
        "who_actor": ai_id,
        "what_type": "HANDSHAKE",
        "where_component": "interface/handshake.py",
        "why_purpose": "Institution Handshake Protocol",
        "how_trigger": "POST /api/handshake",
        "title": f"Institution Handshake: {ai_id} / {role}",
        "short_summary": f"scope={scope} session_id={session_id}",
        "trace_id": session_id,
    })

    return jsonify(response)
