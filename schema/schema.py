"""
MoCKA Schema v1.0
全スクリプトはここからimportしてスキーマを統一する
"""
import json
import hashlib
import uuid
from datetime import datetime, timezone

# =========================
# 定数
# =========================
# パス自動解決（Windows/Linux共通）
from pathlib import Path as _Path
_ROOT = _Path(__file__).resolve().parent.parent
LEDGER_PATH = str(_ROOT / "runtime" / "main" / "ledger.json")
GENESIS_PREV_HASH = "0" * 64

# =========================
# ハッシュ計算（既存方式に統一）
# =========================
def calc_hash(event: dict) -> str:
    raw = f"{event['event_id']}{event['timestamp']}{event['type']}{event['action']}{event['prev_hash']}"
    return hashlib.sha256(raw.encode()).hexdigest()

# =========================
# イベント生成
# =========================
def new_event(type: str, action, prev_hash: str) -> dict:
    event = {
        "event_id":  str(uuid.uuid4()),
        "type":      type,
        "action":    action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prev_hash": prev_hash,
    }
    event["event_hash"] = calc_hash(event)
    return event

# =========================
# Ledger操作
# =========================
def load_ledger(path: str = LEDGER_PATH) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ledger(ledger: list, path: str = LEDGER_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)

def append_event(type: str, action, path: str = LEDGER_PATH) -> dict:
    ledger = load_ledger(path)
    prev_hash = ledger[-1]["event_hash"] if ledger else GENESIS_PREV_HASH
    event = new_event(type, action, prev_hash)
    ledger.append(event)
    save_ledger(ledger, path)
    return event

# =========================
# 検証
# =========================
def verify_ledger(path: str = LEDGER_PATH) -> bool:
    ledger = load_ledger(path)
    prev_hash = GENESIS_PREV_HASH
    for e in ledger:
        if calc_hash(e) != e["event_hash"]:
            print(f"HASH ERROR: {e['event_id']}")
            return False
        if e["prev_hash"] != prev_hash:
            print(f"CHAIN BREAK: {e['event_id']}")
            return False
        prev_hash = e["event_hash"]
    return True

if __name__ == "__main__":
    print("VERIFY:", verify_ledger())
    event = append_event("TEST", "SCHEMA_TEST")
    print("APPENDED:", event["event_id"])
    print("VERIFY:", verify_ledger())
