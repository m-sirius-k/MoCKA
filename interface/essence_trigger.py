import json
import sys
from pathlib import Path
from datetime import datetime

ESSENCE_PATH    = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")
CONDENSED_PATH  = Path("C:/Users/sirok/MoCKA/data/essence_condensed.json")
PING_PATH       = Path("C:/Users/sirok/MoCKA/data/ping_latest.json")

def load_essence_summary() -> dict:
    """essenceとcondensedから注入パケットを構築"""
    essence_data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
    entries = essence_data.get("essence", [])

    by_type = {"INCIDENT": [], "PHILOSOPHY": [], "OPERATION": []}
    for e in entries:
        t = e.get("type", "OPERATION") if isinstance(e, dict) else "OPERATION"
        text = e.get("text", "") if isinstance(e, dict) else str(e)
        by_type[t].append(text[:200])

    # 各タイプから最新3件を代表として抽出
    summary = {}
    for t, texts in by_type.items():
        summary[t] = {
            "count": len(texts),
            "latest": texts[-3:] if texts else []
        }

    # 濃縮バッチ数
    batch_count = 0
    if CONDENSED_PATH.exists():
        condensed = json.loads(CONDENSED_PATH.read_text(encoding="utf-8"))
        batch_count = len(condensed.get("batches", []))

    return {
        "triggered_by": "essence_keyword",
        "timestamp": datetime.now().isoformat(),
        "total_essence": len(entries),
        "condensed_batches": batch_count,
        "summary": summary
    }

def trigger_essence():
    print("[TRIGGER] essenceキーワード検知 → 注入パケット生成開始")

    packet = load_essence_summary()

    # ping_latest.jsonに書き込み
    existing = {}
    if PING_PATH.exists():
        existing = json.loads(PING_PATH.read_text(encoding="utf-8"))

    existing["ESSENCE_TRIGGER"] = packet
    PING_PATH.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"[TRIGGER] 完了")
    print(f"  総essence    : {packet['total_essence']}件")
    print(f"  濃縮バッチ   : {packet['condensed_batches']}バッチ")
    print(f"  INCIDENT     : {packet['summary']['INCIDENT']['count']}件")
    print(f"  PHILOSOPHY   : {packet['summary']['PHILOSOPHY']['count']}件")
    print(f"  OPERATION    : {packet['summary']['OPERATION']['count']}件")
    print(f"[TRIGGER] ping_latest.json更新完了 → MoCKA-START.bat起動時に自動注入されます")

    return packet

if __name__ == "__main__":
    trigger_essence()

