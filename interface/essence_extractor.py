import json
import re
from pathlib import Path
from datetime import datetime

ESSENCE_PATH = Path("C:/Users/sirok/planningcaliber/workshop/needle_eye_project/experiments/lever_essence.json")
EVENTS_CSV   = Path("C:/Users/sirok/MoCKA/data/events.csv")
EXTRACT_LOG  = Path("C:/Users/sirok/MoCKA/data/extract_log.json")
TRIGGER_COUNT = 20  # 何件蓄積で抽出するか

def load_extract_log() -> dict:
    if EXTRACT_LOG.exists():
        return json.loads(EXTRACT_LOG.read_text(encoding="utf-8"))
    return {"last_extracted_line": 0, "extract_history": []}

def save_extract_log(log: dict):
    EXTRACT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

def count_new_events(last_line: int) -> int:
    if not EVENTS_CSV.exists():
        return 0
    lines = EVENTS_CSV.read_text(encoding="utf-8-sig", errors="replace").strip().splitlines()
    return max(0, len(lines) - 1 - last_line)  # ヘッダー除く

def extract_from_events(last_line: int) -> list:
    """events.csvの新規行からテキストを抽出"""
    if not EVENTS_CSV.exists():
        return []
    lines = EVENTS_CSV.read_text(encoding="utf-8-sig", errors="replace").strip().splitlines()
    new_lines = lines[last_line + 1:]  # ヘッダー+既読をスキップ
    extracted = []
    for line in new_lines:
        parts = line.split(",")
        if len(parts) > 14:
            title = parts[14].strip().strip('"')
            summary = parts[15].strip().strip('"') if len(parts) > 15 else ""
            if title:
                extracted.append(title + " " + summary[:80])
    return extracted

def run_extraction():
    log = load_extract_log()
    last_line = log["last_extracted_line"]
    new_count = count_new_events(last_line)

    print(f"[EXTRACTOR] 新規イベント数: {new_count} / トリガー閾値: {TRIGGER_COUNT}")

    if new_count < TRIGGER_COUNT:
        print(f"[EXTRACTOR] 未達 ({new_count}/{TRIGGER_COUNT}) → スキップ")
        return

    # 抽出実行
    texts = extract_from_events(last_line)
    print(f"[EXTRACTOR] 抽出対象: {len(texts)}件 → essence分類開始")

    # essence_classifierを利用
    import sys
    sys.path.insert(0, str(Path("C:/Users/sirok/MoCKA/interface")))
    from essence_classifier import add_essence

    added = 0
    skipped = 0
    for text in texts:
        if len(text.strip()) < 5:
            continue
        result = add_essence(text, source="auto_extractor")
        if result["status"] == "ADDED":
            added += 1
        else:
            skipped += 1

    # ログ更新
    total_lines = len(EVENTS_CSV.read_text(encoding="utf-8-sig", errors="replace").strip().splitlines()) - 1
    log["last_extracted_line"] = total_lines
    log["extract_history"].append({
        "timestamp": datetime.now().isoformat(),
        "new_events": new_count,
        "added_to_essence": added,
        "skipped": skipped
    })
    save_extract_log(log)

    print(f"[EXTRACTOR] 完了 → ADDED:{added} / SKIP:{skipped}")
    print(f"[EXTRACTOR] 次回トリガー: あと{TRIGGER_COUNT}件蓄積後")

if __name__ == "__main__":
    run_extraction()
