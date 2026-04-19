"""
MOCKA events.csv → Firestore mocka_events 同期スクリプト
実行: python mocka_events_sync.py

依存: pip install firebase-admin
"""

import sys
import csv
import json
import hashlib
from pathlib import Path
from datetime import datetime

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("firebase-adminをインストールしてください: pip install firebase-admin")
    sys.exit(1)

# 設定
KEY_PATH = r"X:\down\mocka-knowledge-gate-130cbb27554d.json"
EVENTS_CSV = Path("C:/Users/sirok/MoCKA/data/events.csv")
SYNCED_LOG = Path("C:/Users/sirok/MoCKA/data/firestore_synced.json")
COLLECTION = "mocka_events"


def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()


def load_synced() -> set:
    """同期済みイベントIDを読み込む"""
    if SYNCED_LOG.exists():
        data = json.loads(SYNCED_LOG.read_text(encoding="utf-8"))
        return set(data.get("synced_ids", []))
    return set()


def save_synced(synced_ids: set):
    """同期済みイベントIDを保存"""
    data = {
        "synced_ids": sorted(list(synced_ids)),
        "updated_at": datetime.now().isoformat(),
        "count": len(synced_ids)
    }
    SYNCED_LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_events() -> list:
    """events.csvを読み込む"""
    if not EVENTS_CSV.exists():
        print(f"❌ events.csvが見つかりません: {EVENTS_CSV}")
        return []
    events = []
    with open(EVENTS_CSV, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(dict(row))
    return events


def event_to_doc(event: dict) -> dict:
    """events.csvの1行をFirestoreドキュメントに変換"""
    doc = {}
    for k, v in event.items():
        if v and v.strip():
            doc[k] = v.strip()
    # タイムスタンプ追加
    doc["synced_at"] = datetime.now().isoformat()
    doc["source"] = "events.csv"
    return doc


def get_event_id(event: dict) -> str:
    """イベントIDを取得（なければハッシュで生成）"""
    eid = event.get("event_id") or event.get("id") or event.get("ID")
    if eid and eid.strip():
        return eid.strip()
    # IDがなければ内容からハッシュ生成
    content = json.dumps(event, ensure_ascii=False, sort_keys=True)
    return "EVT-" + hashlib.md5(content.encode()).hexdigest()[:12]


def sync_events(db, events: list, synced: set) -> tuple:
    """未同期イベントをFirestoreにpush"""
    new_synced = 0
    errors = 0
    col_ref = db.collection(COLLECTION)

    for event in events:
        eid = get_event_id(event)
        if eid in synced:
            continue  # 同期済みスキップ

        try:
            doc = event_to_doc(event)
            col_ref.document(eid).set(doc)
            synced.add(eid)
            print(f"  ✅ {eid}")
            new_synced += 1
        except Exception as e:
            print(f"  ❌ {eid}: {e}")
            errors += 1

    return new_synced, errors


def main():
    print("=== events.csv → Firestore mocka_events 同期 ===\n")

    db = init_firebase()
    events = load_events()
    if not events:
        return

    synced = load_synced()
    total = len(events)
    already = sum(1 for e in events if get_event_id(e) in synced)
    pending = total - already

    print(f"events.csv: {total}件 / 同期済み: {already}件 / 未同期: {pending}件\n")

    if pending == 0:
        print("差分なし。全件同期済みです。")
        return

    new_synced, errors = sync_events(db, events, synced)
    save_synced(synced)

    print(f"\n完了: {new_synced}件追加 / エラー: {errors}件")
    print(f"Firestoreで確認: https://console.firebase.google.com/project/mocka-knowledge-gate/firestore/data/{COLLECTION}")


if __name__ == "__main__":
    main()
