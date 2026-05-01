"""
MoCKA Watcher 窶・Firestore intent_queue逶｣隕・60遘偵＃縺ｨ縺ｫpolling縺励※status=螳御ｺ・ｒ讀懃衍
讀懃衍縺励◆繧嬰ata/watcher_queue/縺ｫJSON繧貞・蜉・"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# 迺ｰ蠅・ｨｭ螳夲ｼ・EY_PATH縺ｮ繝・ヵ繧ｩ繝ｫ繝亥､繧剃ｿｮ豁｣・・KEY_PATH   = os.environ.get("MOCKA_FIREBASE_KEY_PATH",
                             r"X:\down\MoCKA_Downloads\mocka-knowledge-gate-130cbb27554d.json")
PROJECT_ID = os.environ.get("MOCKA_FIREBASE_PROJECT_ID", "mocka-knowledge-gate")
INTERVAL   = 60  # 遘・
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

def save_processed_ids(processed_ids):
    with open(PROCESSED_LOG, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f, ensure_ascii=False, indent=2)

def main():
    db = initialize_firebase()
    print(f"[{datetime.now()}] MoCKA Watcher started. Polling every {INTERVAL}s.")

    while True:
        try:
            processed_ids = load_processed_ids()
            docs = db.collection("intent_queue").where("status", "==", "螳御ｺ・).stream()

            new_count = 0
            for doc in docs:
                todo_id = doc.id
                data    = doc.to_dict()

                if todo_id not in processed_ids and data.get("handoff_report"):
                    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = WATCHER_QUEUE / f"{todo_id}_{timestamp}.json"

                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump({
                            "todo_id":        todo_id,
                            "assigned_to":    data.get("assigned_to", ""),
                            "handoff_report": data.get("handoff_report", ""),
                            "detected_at":    timestamp
                        }, f, ensure_ascii=False, indent=2)

                    print(f"[{datetime.now()}] Detected and queued: {todo_id}")
                    processed_ids.add(todo_id)
                    new_count += 1

            save_processed_ids(processed_ids)
            if new_count == 0:
                print(f"[{datetime.now()}] No new completions. Next in {INTERVAL}s.")

        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()

