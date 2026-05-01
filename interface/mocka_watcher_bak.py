"""
MoCKA Watcher 遯ｶ繝ｻFirestore intent_queue騾ｶ・｣髫輔・60驕伜・・・ｸｺ・ｨ邵ｺ・ｫpolling邵ｺ蜉ｱ窶ｻstatus=陞ｳ蠕｡・ｺ繝ｻ・定ｮ諛・｡・隶諛・｡咲ｸｺ蜉ｱ笳・ｹｧ螫ｰata/watcher_queue/邵ｺ・ｫJSON郢ｧ雋槭・陷峨・"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# 霑ｺ・ｰ陟・・・ｨ・ｭ陞ｳ螟ｲ・ｼ繝ｻEY_PATH邵ｺ・ｮ郢昴・繝ｵ郢ｧ・ｩ郢晢ｽｫ郢昜ｺ･ﾂ・､郢ｧ蜑・ｽｿ・ｮ雎・ｽ｣繝ｻ繝ｻKEY_PATH   = os.environ.get("MOCKA_FIREBASE_KEY_PATH", r"A:\secrets\mocka-knowledge-gate-firebase-adminsdk-fbsvc-53613922c1.json")
PROJECT_ID = os.environ.get("MOCKA_FIREBASE_PROJECT_ID", "mocka-knowledge-gate")
INTERVAL   = 60  # 驕倥・
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
            docs = db.collection("intent_queue").where("status", "==", "陞ｳ蠕｡・ｺ繝ｻ).stream()

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


