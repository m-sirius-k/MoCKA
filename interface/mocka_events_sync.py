"""
MOCKA events.csv → Firestore mocka_events 同期スクリプト v2
APIキーは環境変数から取得（ハードコード禁止）

依存: pip install firebase-admin
"""

import sys, json, csv, hashlib, os
from pathlib import Path
from datetime import datetime

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("firebase-adminをインストールしてください: pip install firebase-admin")
    sys.exit(1)

KEY_PATH   = os.environ.get("MOCKA_FIREBASE_KEY_PATH",
                             r"X:\down\mocka-knowledge-gate-130cbb27554d.json")
EVENTS_CSV = Path("C:/Users/sirok/MoCKA/data/events.csv")
SYNCED_LOG = Path("C:/Users/sirok/MoCKA/data/firestore_synced.json")
COLLECTION = "mocka_events"

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()

def load_synced():
    if SYNCED_LOG.exists():
        data = json.loads(SYNCED_LOG.read_text(encoding="utf-8"))
        return set(data.get("synced_ids", []))
    return set()

def save_synced(synced_ids):
    SYNCED_LOG.write_text(
        json.dumps({"synced_ids": sorted(list(synced_ids)),
                    "updated_at": datetime.now().isoformat(),
                    "count": len(synced_ids)},
                   ensure_ascii=False, indent=2),
        encoding="utf-8")

def load_events():
    if not EVENTS_CSV.exists():
        print(f"ERROR: {EVENTS_CSV} が見つかりません")
        return []
    with open(EVENTS_CSV, encoding="utf-8", errors="replace") as f:
        return [dict(row) for row in csv.DictReader(f)]

def get_event_id(event):
    eid = event.get("event_id") or event.get("id") or event.get("ID")
    if eid and eid.strip():
        return eid.strip()
    content = json.dumps(event, ensure_ascii=False, sort_keys=True)
    return "EVT-" + hashlib.md5(content.encode()).hexdigest()[:12]

def event_to_doc(event):
    doc = {k: v.strip() for k, v in event.items() if v and v.strip()}
    doc["synced_at"] = datetime.now().isoformat()
    doc["source"]    = "events.csv"
    return doc

def main():
    print("=== events.csv → Firestore mocka_events 同期 ===\n")
    db      = init_firebase()
    events  = load_events()
    if not events: return

    synced  = load_synced()
    pending = [e for e in events if get_event_id(e) not in synced]
    print(f"対象: {len(events)}件 / 同期済み: {len(synced)}件 / 未同期: {len(pending)}件\n")

    if not pending:
        print("差分なし")
        return

    col_ref = db.collection(COLLECTION)
    ok = err = 0
    for event in pending:
        eid = get_event_id(event)
        try:
            col_ref.document(eid).set(event_to_doc(event))
            synced.add(eid)
            print(f"  ✅ {eid}")
            ok += 1
        except Exception as e:
            print(f"  ❌ {eid}: {e}")
            err += 1

    save_synced(synced)
    print(f"\n完了: {ok}件追加 / エラー: {err}件")

if __name__ == "__main__":
    main()
