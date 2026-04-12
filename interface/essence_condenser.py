import json
from pathlib import Path
from datetime import datetime

ESSENCE_PATH   = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")
CONDENSED_PATH = Path("C:/Users/sirok/MoCKA/data/essence_condensed.json")
CONDENSE_UNIT  = 20  # 何件ずつ濃縮するか

def load_essence() -> list:
    if not ESSENCE_PATH.exists():
        return []
    data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
    return data.get("essence", [])

def load_condensed() -> dict:
    if CONDENSED_PATH.exists():
        return json.loads(CONDENSED_PATH.read_text(encoding="utf-8"))
    return {"last_condensed_index": 0, "batches": []}

def save_condensed(data: dict):
    CONDENSED_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def condense_batch(entries: list, batch_no: int) -> dict:
    """20件をタイプ別に集約して濃縮"""
    by_type = {"INCIDENT": [], "PHILOSOPHY": [], "OPERATION": []}
    for e in entries:
        t = e.get("type", "OPERATION") if isinstance(e, dict) else "OPERATION"
        text = e.get("text", e) if isinstance(e, dict) else str(e)
        by_type[t].append(text[:200])

    # 各タイプのキーワードを抽出（先頭20文字×件数）
    summary = {}
    for t, texts in by_type.items():
        if texts:
            summary[t] = {
                "count": len(texts),
                "core": texts[:3]  # 代表3件
            }

    return {
        "batch_no": batch_no,
        "timestamp": datetime.now().isoformat(),
        "total_entries": len(entries),
        "summary": summary
    }

def run_condensation():
    essence = load_essence()
    condensed = load_condensed()
    last_idx = condensed["last_condensed_index"]
    new_entries = essence[last_idx:]

    print(f"[CONDENSER] 総essence: {len(essence)}件 / 未濃縮: {len(new_entries)}件")

    if len(new_entries) < CONDENSE_UNIT:
        print(f"[CONDENSER] 未達 ({len(new_entries)}/{CONDENSE_UNIT}) → スキップ")
        return

    batch_no = len(condensed["batches"]) + 1
    processed = 0

    while len(new_entries) >= CONDENSE_UNIT:
        batch_entries = new_entries[:CONDENSE_UNIT]
        new_entries = new_entries[CONDENSE_UNIT:]
        batch = condense_batch(batch_entries, batch_no)
        condensed["batches"].append(batch)
        batch_no += 1
        processed += CONDENSE_UNIT
        print(f"[CONDENSER] Batch {batch['batch_no']} 完了 → INCIDENT:{batch['summary'].get('INCIDENT',{}).get('count',0)} / PHILOSOPHY:{batch['summary'].get('PHILOSOPHY',{}).get('count',0)} / OPERATION:{batch['summary'].get('OPERATION',{}).get('count',0)}")

    condensed["last_condensed_index"] = last_idx + processed
    save_condensed(condensed)
    print(f"[CONDENSER] 完了 → {batch_no-1}バッチ生成 / 次回: あと{CONDENSE_UNIT - len(new_entries)}件後")

if __name__ == "__main__":
    run_condensation()

