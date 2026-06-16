# audit/consistency_check.py
# MoCKA v1.2.1 — Consistency Check
# 責務: Timelineの整合性（改ざん・欠損・順序異常）を検証する。

from __future__ import annotations

from pathlib import Path


def check_system_integrity() -> bool:
    """
    data/logs/semantic_timeline.jsonl の存在と読み取り可能性を確認する。
    v1.3で改ざん検知（ハッシュ連鎖）に拡張予定。
    """
    path = Path(__file__).resolve().parent.parent / "data" / "logs" / "semantic_timeline.jsonl"

    if not path.exists():
        return True  # 未使用は整合性違反ではない

    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    import json
                    json.loads(line)  # 各行がvalidなJSONであること
        return True
    except Exception:
        return False
