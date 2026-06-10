#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prediction_engine.py -- Prediction Engine (TODO_288)
既存データ（recurrence_registry.csv / trajectory.csv）から
「次にどこで再発するか」を予測してSession/Handshakeに注入する。
GET /api/prediction/risk
"""

import csv
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent))
import db_helper as db

from flask import Blueprint, jsonify

prediction_bp = Blueprint('prediction', __name__, url_prefix='/api')

JST = timezone(timedelta(hours=9))

RECURRENCE_CSV = db.MOCKA_ROOT / "data" / "recurrence_registry.csv"
TRAJECTORY_CSV = db.MOCKA_ROOT / "data" / "trajectory.csv"

# component/what_type 別のミティゲーション知見（既存インシデント由来）
_MITIGATIONS = {
    ("relay", "encoding"): "cp932環境での書き込み操作時に再発リスク高。UTF-8 BOMなし固定が必須。",
}

HIGH_RISK_THRESHOLD = 3


def _read_recurrence_rows() -> list[dict]:
    if not RECURRENCE_CSV.exists():
        return []
    with open(RECURRENCE_CSV, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _high_risk_areas() -> list[dict]:
    rows = _read_recurrence_rows()
    by_component: dict[tuple, dict] = {}

    for row in rows:
        component = row.get("component", "unknown")
        what_type = row.get("what_type", "unknown")
        key = (component, what_type)
        try:
            count = int(row.get("recurrence_count", 0))
        except (TypeError, ValueError):
            count = 0

        existing = by_component.get(key)
        if existing is None or count > existing["recurrence_count"]:
            by_component[key] = {
                "component": component,
                "risk_type": what_type,
                "recurrence_count": count,
                "last_incident": row.get("current_event_id", ""),
                "note": row.get("note", ""),
            }

    areas = []
    for (component, what_type), info in by_component.items():
        if info["recurrence_count"] < HIGH_RISK_THRESHOLD:
            continue
        mitigation = _MITIGATIONS.get((component.lower(), what_type.lower()),
                                       f"{component}/{what_type}: 過去{info['recurrence_count']}回再発。同種の操作を行う前に履歴を確認すること。")
        areas.append({
            "component": component,
            "risk_type": what_type,
            "recurrence_count": info["recurrence_count"],
            "last_incident": info["last_incident"],
            "prediction": f"{component}での{what_type}操作時に再発リスク高（過去{info['recurrence_count']}回）",
            "mitigation": mitigation,
        })

    areas.sort(key=lambda a: a["recurrence_count"], reverse=True)
    return areas


def _trajectory_trend() -> dict:
    if not TRAJECTORY_CSV.exists():
        return {}

    with open(TRAJECTORY_CSV, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        return {}

    last = rows[-1]
    try:
        x, y, z = float(last["X"]), float(last["Y"]), float(last["Z"])
    except (KeyError, ValueError):
        return {}

    trend = "stable"
    window = rows[-11:-1] if len(rows) > 10 else rows[:-1]
    if window:
        try:
            prev_avg_z = sum(float(r["Z"]) for r in window) / len(window)
            if z > prev_avg_z + 0.02:
                trend = "improving"
            elif z < prev_avg_z - 0.02:
                trend = "degrading"
        except (KeyError, ValueError):
            pass

    return {"X": x, "Y": y, "Z": z, "trend": trend}


def get_risk_prediction() -> dict:
    return {
        "high_risk_areas": _high_risk_areas(),
        "trajectory_trend": _trajectory_trend(),
        "generated_at": datetime.now(JST).isoformat(),
    }


def get_active_warnings() -> list[str]:
    warnings = []
    for area in _high_risk_areas():
        warnings.append(
            f"{area['component']}/{area['risk_type']}: 再発注意（過去{area['recurrence_count']}回）"
        )
    return warnings


@prediction_bp.route('/prediction/risk', methods=['GET'])
def prediction_risk():
    return jsonify(get_risk_prediction())
