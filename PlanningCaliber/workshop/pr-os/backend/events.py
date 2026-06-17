"""
events.py — PR-OS唯一の記録層
Single Source of Truth: data/events.jsonl
"""

import json
import time
from pathlib import Path

EVENTS_PATH = Path(__file__).parent.parent / "data" / "events.jsonl"


def _ensure_dir():
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)


def write(action: str, status: str, result: dict = None, error: str = None) -> dict:
    """
    イベントを必ずこの形で記録する。
    {ts, action, status, result, error}
    """
    _ensure_dir()
    event = {
        "ts": time.time(),
        "action": action,
        "status": status,   # "success" | "failed" | "running"
        "result": result or {},
        "error": error,     # 正常時はnull
    }
    with open(EVENTS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def read_all(limit: int = 50) -> list:
    """
    最新N件のイベントを返す。
    ファイルが壊れていても最後の正常行だけ読む（フェイルセーフ）。
    """
    _ensure_dir()
    if not EVENTS_PATH.exists():
        return []

    events = []
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                # 壊れた行は無視（クラッシュさせない）
                continue

    return events[-limit:]


def count() -> int:
    """イベント総件数を返す。"""
    _ensure_dir()
    if not EVENTS_PATH.exists():
        return 0
    n = 0
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n
