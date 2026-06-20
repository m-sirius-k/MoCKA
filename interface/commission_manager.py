#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
commission_manager.py -- Commission Registry (TODO_286)
Role(継続的資格)とCommission(期間限定任務)を分離して管理する。
GET /api/commission/list
GET /api/commission/<commission_id>
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
import db_helper as db

from flask import Blueprint, jsonify, abort

commission_bp = Blueprint('commission', __name__, url_prefix='/api')

JST = timezone(timedelta(hours=9))
REGISTRY_PATH = Path(db.MOCKA_ROOT) / "data" / "institution" / "commission_registry.json"


def _load_registry() -> dict:
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"version": "1.0", "commissions": []}


def _save_registry(data: dict):
    REGISTRY_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def create_commission(commission_id: str, role: str, scope: str, assigned_to: str,
                       assigned_by: str, todos: list, end_condition: str = "") -> dict:
    """新しいCommission(期間限定任務)をregistryに追記する"""
    data = _load_registry()
    now = datetime.now(JST)

    commission = {
        "commission_id": commission_id,
        "role": role,
        "scope": scope,
        "assigned_to": assigned_to,
        "assigned_by": assigned_by,
        "status": "active",
        "start_date": now.strftime("%Y-%m-%d"),
        "end_condition": end_condition,
        "todos": todos,
        "audit_log": [],
    }
    data["commissions"].append(commission)
    _save_registry(data)
    return commission


def close_commission(commission_id: str, result: str) -> dict:
    """Commissionをclosedにし、audit_logに結果を記録する"""
    data = _load_registry()
    now = datetime.now(JST)

    target = None
    for c in data["commissions"]:
        if c["commission_id"] == commission_id:
            target = c
            break
    if target is None:
        raise ValueError(f"commission not found: {commission_id}")

    target["status"] = "closed"
    target["audit_log"].append({
        "when": now.isoformat(),
        "result": result,
    })
    _save_registry(data)

    from event_buffer import get_buffer  # Phase5-1: db.write_event直接禁止 → Gate経由
    get_buffer().push({
        "when": now.isoformat(),
        "who_actor": target.get("assigned_to"),
        "what_type": "COMMISSION_CLOSED",
        "where_component": "interface/commission_manager.py",
        "why_purpose": "Commission completion",
        "how_trigger": "close_commission()",
        "title": f"Commission Closed: {commission_id}",
        "short_summary": result,
        "trace_id": commission_id,
    })

    return target


@commission_bp.route('/commission/list', methods=['GET'])
def commission_list():
    data = _load_registry()
    active = [c for c in data.get("commissions", []) if c.get("status") == "active"]
    return jsonify({"version": data.get("version", "1.0"), "commissions": active})


@commission_bp.route('/commission/<commission_id>', methods=['GET'])
def commission_detail(commission_id):
    data = _load_registry()
    for c in data.get("commissions", []):
        if c["commission_id"] == commission_id:
            return jsonify(c)
    abort(404)
