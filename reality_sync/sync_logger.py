# -*- coding: utf-8 -*-
"""Sync Logger (Phase 4-2 Reality Sync Layer)

EVIDENCE_ONLY ログを出力する。
- 推測ログは禁止 (このモジュールは SyncResult.evidence のみを書き出す)
- 差分 (discrepancy_type != NONE) のみを記録する
"""

import json
from datetime import datetime
from pathlib import Path

from reality_sync.sync_registry import REPO_ROOT
from reality_sync.sync_result_model import SyncResult

LOG_DIR = REPO_ROOT / "reality_sync" / "logs"
LOG_FILE = LOG_DIR / "sync_log.jsonl"


def log_results(results: list[SyncResult]) -> Path:
    """discrepancy_type != NONE の SyncResult のみを EVIDENCE_ONLY 形式で
    sync_log.jsonl に追記する。戻り値はログファイルパス。
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    lines = []
    for r in results:
        if r.discrepancy_type == "NONE":
            continue
        record = {
            "timestamp": timestamp,
            "file_path": r.file_path,
            "reported_status": r.reported_status,
            "actual_status": r.actual_status,
            "discrepancy_type": r.discrepancy_type,
            "severity": r.severity,
            "fix_required": r.fix_required,
            "evidence": r.evidence,
            "sources": r.sources,
        }
        lines.append(json.dumps(record, ensure_ascii=False))

    if lines:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

    return LOG_FILE


if __name__ == "__main__":
    print(f"LOG_FILE = {LOG_FILE}")
