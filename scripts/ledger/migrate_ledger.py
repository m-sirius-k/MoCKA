import json, hashlib, uuid, os

LEDGER_PATH = r"runtime\main\ledger.json"
BACKUP_PATH = r"runtime\main\ledger_pre_migration.json"

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

with open(LEDGER_PATH, "r", encoding="utf-8") as f:
    ledger = json.load(f)

# バックアップ
with open(BACKUP_PATH, "w", encoding="utf-8") as f:
    json.dump(ledger, f, indent=2)
print(f"BACKUP: {BACKUP_PATH}")

# マイグレーション
new_ledger = []
prev_hash = "0" * 64
for e in ledger:
    new_e = {
        "event_id": str(uuid.uuid4()),
        "type": e.get("type", "UNKNOWN"),
        "action": e.get("action", ""),
        "timestamp": e.get("ts", e.get("timestamp", 0)),
        "prev_hash": prev_hash,
    }
    raw = f"{new_e['event_id']}{new_e['timestamp']}{new_e['type']}{new_e['action']}{prev_hash}"
    new_e["event_hash"] = sha256(raw)
    prev_hash = new_e["event_hash"]
    new_ledger.append(new_e)

with open(LEDGER_PATH, "w", encoding="utf-8") as f:
    json.dump(new_ledger, f, indent=2)

print(f"MIGRATED: {len(new_ledger)} records")
