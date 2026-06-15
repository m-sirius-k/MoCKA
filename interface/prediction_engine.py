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


# ============================================================
# TIC Prediction Facade (Phase6) -- TODO_321
# 上記の既存コード（TODO_288）とは独立。risk_history.jsonl ベースの
# TICリスクスコア予測を prediction/ パッケージ経由で提供する。
# ============================================================
import datetime as _dt

_sys_path = str(Path(__file__).resolve().parent)
if _sys_path not in sys.path:
    sys.path.insert(0, _sys_path)

from prediction import gate as _gate
from prediction import models as _models
from prediction import history as _history
from prediction import provider as _provider

TIC_DAYS_AHEAD = 14


def run_tic_prediction(days_ahead: int = TIC_DAYS_AHEAD) -> list:
    """各コンポーネントのTICリスクスコア予測を返す。
    Gate未達（trace_count < REQUIRED_TRACE_COUNT）はINSUFFICIENT_DATA。
    結果はprediction_history.jsonlにappendされる（冪等）。"""
    today_str = _dt.date.today().isoformat()
    components = _provider.get_components()
    results = []

    for comp in components:
        series = _provider.get_score_series_for(comp, window=_gate.REQUIRED_TRACE_COUNT)
        trace_count = len(series)

        if not _gate.check(trace_count):
            result = {
                "status":          "INSUFFICIENT_DATA",
                "component":       comp,
                "date":            today_str,
                "trace_count":     trace_count,
                "required":        _gate.REQUIRED_TRACE_COUNT,
                "predicted_score": None,
                "confidence":      None,
                "days_ahead":      days_ahead,
                "model":           None,
            }
        else:
            pred = _models.predict(series, days_ahead=days_ahead)
            result = {
                "status":          "OK",
                "component":       comp,
                "date":            today_str,
                "trace_count":     trace_count,
                "required":        _gate.REQUIRED_TRACE_COUNT,
                "predicted_score": pred["predicted_score"],
                "confidence":      pred["confidence"],
                "days_ahead":      pred["days_ahead"],
                "model":           pred["model"],
            }

        recorded = _history.record(result)
        # 既存記録がある場合はそちらをstatus/値として優先（冪等）
        result["status"]          = recorded["status"]
        result["predicted_score"] = recorded["predicted_score"]
        result["confidence"]      = recorded["confidence"]
        result["model"]           = recorded["model"]
        results.append(result)

    return results


if __name__ == "__main__":
    _results = run_tic_prediction()
    if not _results:
        print("[prediction_engine] risk_history.jsonl が空。終了。")
    for _r in _results:
        if _r["status"] == "INSUFFICIENT_DATA":
            print(
                f"  {_r['component']:<20} : Waiting for sufficient history "
                f"({_r['trace_count']:>2} / {_r['required']})"
            )
        else:
            print(
                f"  {_r['component']:<20} : {_r['predicted_score']}  "
                f"(confidence: {int(_r['confidence'] * 100)}%)  "
                f"▲ {_r['model']}"
            )
