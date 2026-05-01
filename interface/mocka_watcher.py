"""
MoCKA Watcher - Firestore intent_queue監視。60秒ごとにpollingしてstatus=完了を検知。
検知したらdata/watcher_queue/にJSONを出力。
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# 環境設定（KEY_PATHのデフォルト値を修正）
KEY_PATH   = os.environ.get("MOCKA_FIREBASE_KEY_PATH",
                             r"A:\secrets\mocka-knowledge-gate-firebase-adminsdk-fbsvc-53613922c1.json")
PROJECT_ID = os.environ.get("MOCKA_FIREBASE_PROJECT_ID", "mocka-knowledge-gate")
INTERVAL   = 60  # 秒
WATCHER_QUEUE = Path("C:/Users/sirok/MoCKA/data/watcher_queue")
PROCESSED_LOG = Path("C:/Users/sirok/MoCKA/data/watcher_processed.json")
WATCHER_QUEUE.mkdir(parents=True, exist_ok=True)

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
    return firestore.client()

def load_processed_ids():
    if PROCESSED_LOG.exists():
        with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_processed_ids(ids):
    with open(PROCESSED_LOG, "w", encoding="utf-8") as f:
        json.dump(list(ids), f, ensure_ascii=False)

def write_handoff(doc_id, data):
    out_path = WATCHER_QUEUE / f"{doc_id}.json"
    payload = {
        "doc_id": doc_id,
        "detected_at": datetime.now().isoformat(),
        "data": data
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[WATCHER] handoff written: {out_path}")

def poll(db, processed_ids):
    docs = db.collection("intent_queue").where("status", "==", "完了").stream()
    for doc in docs:
        doc_id = doc.id
        if doc_id in processed_ids:
            continue
        data = doc.to_dict()
        print(f"[WATCHER] 完了検知: {doc_id}")
        write_handoff(doc_id, data)
        processed_ids.add(doc_id)
    save_processed_ids(processed_ids)

def main():
    print("[WATCHER] 起動中...")
    db = initialize_firebase()
    processed_ids = load_processed_ids()
    print(f"[WATCHER] 監視開始。既処理: {len(processed_ids)}件 / interval={INTERVAL}秒")
    while True:
        try:
            poll(db, processed_ids)
        except Exception as e:
            print(f"[WATCHER] エラー: {e}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()