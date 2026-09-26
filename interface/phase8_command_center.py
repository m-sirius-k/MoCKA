#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phase8_command_center.py -- Flask blueprint for Command Center Phase 8 ledger integration
Exposes Decision Ledger and Event Log queries via HTTP
"""

from flask import Blueprint, jsonify, request
from pathlib import Path
from .phase8_ledger import Phase8LedgerQuery

phase8_bp = Blueprint('phase8_ledger', __name__, url_prefix='/api/phase8')

# Initialize ledger query interface
_repo_root = Path(__file__).resolve().parent.parent
_ledger = Phase8LedgerQuery(repo_root=_repo_root)


@phase8_bp.route('/health', methods=['GET'])
def phase8_health():
    """Health check for Phase 8 ledger integration"""
    ledger_exists = _ledger.ledger_path.exists()
    event_exists = _ledger.event_path.exists()

    return jsonify({
        "status": "ok" if (ledger_exists and event_exists) else "partial",
        "ledger_file": str(_ledger.ledger_path),
        "ledger_exists": ledger_exists,
        "event_file": str(_ledger.event_path),
        "event_exists": event_exists
    }), 200


@phase8_bp.route('/locate/task/<task_id>', methods=['GET'])
def locate_task(task_id):
    """Locate decisions by task_id"""
    decisions = _ledger.get_decisions_for_task(task_id)

    return jsonify({
        "task_id": task_id,
        "found": len(decisions) > 0,
        "decision_count": len(decisions),
        "decisions": [
            {
                "decision_id": d.get('decision_id'),
                "title": d.get('title'),
                "approved_by": d.get('approved_by'),
                "status": d.get('status'),
                "approved_at": d.get('approved_at')
            }
            for d in decisions
        ]
    }), 200


@phase8_bp.route('/locate/correlation/<corr_id>', methods=['GET'])
def locate_correlation(corr_id):
    """Locate decision by correlation_id"""
    decision = _ledger.locate_by_correlation_id(corr_id)

    return jsonify({
        "correlation_id": corr_id,
        "found": decision is not None,
        "decision": {
            "decision_id": decision.get('decision_id'),
            "title": decision.get('title'),
            "approved_by": decision.get('approved_by'),
            "status": decision.get('status')
        } if decision else None
    }), 200


@phase8_bp.route('/locate/decision/<decision_id>', methods=['GET'])
def locate_decision(decision_id):
    """Locate decision by decision_id and get associated events"""
    decision = _ledger.locate_by_decision_id(decision_id)
    events = _ledger.get_events_for_decision(decision_id) if decision else []

    return jsonify({
        "decision_id": decision_id,
        "found": decision is not None,
        "decision": {
            "title": decision.get('title'),
            "context": decision.get('context'),
            "decision": decision.get('decision'),
            "rationale": decision.get('rationale'),
            "impact": decision.get('impact'),
            "approved_by": decision.get('approved_by'),
            "approved_at": decision.get('approved_at'),
            "status": decision.get('status')
        } if decision else None,
        "event_count": len(events),
        "events": [
            {
                "event_id": e.get('event_id'),
                "event_type": e.get('event_type'),
                "status": e.get('status')
            }
            for e in events
        ]
    }), 200


@phase8_bp.route('/locate/event/<event_id>', methods=['GET'])
def locate_event(event_id):
    """Locate event by event_id"""
    event = _ledger.locate_by_event_id(event_id)

    return jsonify({
        "event_id": event_id,
        "found": event is not None,
        "event": {
            "event_type": event.get('event_type'),
            "decision_id": event.get('decision_id'),
            "correlation_id": event.get('correlation_id'),
            "status": event.get('status'),
            "timestamp": event.get('timestamp'),
            "who_actor": event.get('who_actor'),
            "what_type": event.get('what_type')
        } if event else None
    }), 200


@phase8_bp.route('/trace/<task_id>', methods=['GET'])
def trace_execution_chain(task_id):
    """Trace complete execution chain for a task"""
    trace = _ledger.trace_execution_chain(task_id)

    return jsonify(trace), 200


@phase8_bp.route('/decisions/recent', methods=['GET'])
def get_recent_decisions():
    """Get recent decisions (limit=20 by default)"""
    limit = request.args.get('limit', 20, type=int)
    decisions = _ledger.get_all_decisions(limit=limit)

    return jsonify({
        "count": len(decisions),
        "decisions": [
            {
                "decision_id": d.get('decision_id'),
                "title": d.get('title'),
                "approved_by": d.get('approved_by'),
                "status": d.get('status'),
                "approved_at": d.get('approved_at')
            }
            for d in decisions
        ]
    }), 200


@phase8_bp.route('/events/recent', methods=['GET'])
def get_recent_events():
    """Get recent events (limit=20 by default)"""
    limit = request.args.get('limit', 20, type=int)
    events = _ledger.get_all_events(limit=limit)

    return jsonify({
        "count": len(events),
        "events": [
            {
                "event_id": e.get('event_id'),
                "event_type": e.get('event_type'),
                "decision_id": e.get('decision_id'),
                "status": e.get('status'),
                "timestamp": e.get('timestamp')
            }
            for e in events
        ]
    }), 200


@phase8_bp.route('/index/status', methods=['GET'])
def index_status():
    """Get index status and availability"""
    try:
        decisions = _ledger._load_decisions()
        events = _ledger._load_events()

        return jsonify({
            "status": "ok",
            "decision_ledger": {
                "file": str(_ledger.ledger_path),
                "exists": _ledger.ledger_path.exists(),
                "record_count": len(decisions)
            },
            "event_log": {
                "file": str(_ledger.event_path),
                "exists": _ledger.event_path.exists(),
                "record_count": len(events)
            },
            "indices": {
                "task_index": "available",
                "correlation_index": "available",
                "decision_to_event": "available"
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
