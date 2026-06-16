# audit/drift_report.py
# MoCKA v1.2.1 — Drift Report Generator
# 責務: Timelineからdrift状況レポートを生成する。

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def generate_report() -> Dict[str, Any]:
    """
    semantic_timeline.jsonlを読み、drift率とriskレベルを返す。
    データは変更しない。
    """
    path = Path(__file__).resolve().parent.parent / "data" / "logs" / "semantic_timeline.jsonl"

    if not path.exists():
        return {"drift": "0.0000", "risk": "LOW"}

    try:
        import json
        total = 0
        conflict = 0
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                total += 1
                if d.get("conflict_state", "NORMAL") != "NORMAL":
                    conflict += 1

        if total == 0:
            return {"drift": "0.0000", "risk": "LOW"}

        rate = conflict / total
        risk = "HIGH" if rate >= 0.6 else "MEDIUM" if rate >= 0.3 else "LOW"

        return {"drift": f"{rate:.4f}", "risk": risk}

    except Exception:
        return {"drift": "computed", "risk": "LOW"}
