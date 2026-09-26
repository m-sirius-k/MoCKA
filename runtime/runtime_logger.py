# runtime/logging.py
# MoCKA v1.2.1+ — RuntimeLogger（ログ制度化）
# 全イベントの出力を統一形式で記録する。

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "logs" / "runtime.jsonl"


class RuntimeLogger:
    """
    run_cycle の入出力を data/logs/runtime.jsonl に追記する。
    上書きしない。観測専用。
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _LOG_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """イベント名と付帯データをJSONLに追記する。"""
        record = {
            "event":     event,
            "data":      data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status":    "recorded",
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def log_cycle(self, cycle_id: str, result: Dict[str, Any]) -> None:
        """run_cycle 1サイクル分を統一形式で記録する。"""
        self.log("cycle", {
            "cycle":     cycle_id,
            "decision":  result.get("decision"),
            "drift":     result.get("state", {}).get("drift"),
            "stability": result.get("state", {}).get("stability"),
            "audit":     result.get("audit", {}).get("status"),
        })
