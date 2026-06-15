"""
prediction/history.py -- TIC Prediction History (Phase6)

prediction_history.jsonl への append-only 記録。
pred_id採番: PR_{6桁連番}。同日・同コンポーネントは重複しない（冪等性）。
"""

import json
import datetime
from pathlib import Path

PREDICTION_PATH = Path("C:/Users/sirok/MoCKA/data/tic/prediction_history.jsonl")


def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def load_all() -> list:
    return _load_jsonl(PREDICTION_PATH)


def load_today() -> dict:
    """本日分のエントリを {component: entry} で返す"""
    today_str = datetime.date.today().isoformat()
    return {e["component"]: e for e in load_all() if e.get("date") == today_str}


def record(result: dict) -> dict:
    """resultをprediction_history.jsonlにappendする（冪等）。
    既に本日同コンポーネントの記録があれば追記せずそのまま返す。"""
    today = load_today()
    existing = today.get(result["component"])
    if existing:
        return existing

    all_entries = load_all()
    seq = len(all_entries) + 1

    entry = {
        "pred_id":         f"PR_{seq:06d}",
        "component":       result["component"],
        "date":            result["date"],
        "status":          result["status"],
        "trace_count":     result["trace_count"],
        "predicted_score": result["predicted_score"],
        "confidence":      result["confidence"],
        "model":           result["model"],
    }

    PREDICTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PREDICTION_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry
