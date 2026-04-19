"""
MoCKA Executor Bridge — watcher_queueを監視
新規JSONを検知したらpending_reviews/にREVIEW_{todo_id}.mdを生成
Claudeへの通知ファイルとして機能する
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

WATCHER_QUEUE = Path("C:/Users/sirok/MoCKA/data/watcher_queue")
PROCESSED_DIR = WATCHER_QUEUE / "processed"
REVIEWS_DIR   = Path("C:/Users/sirok/MoCKA/data/pending_reviews")
INTERVAL      = 10  # 秒

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print(f"[{datetime.now()}] MoCKA Executor Bridge started. Scanning every {INTERVAL}s.")

    while True:
        try:
            json_files = list(WATCHER_QUEUE.glob("*.json"))

            for json_file in json_files:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                todo_id     = data.get("todo_id", "UNKNOWN")
                report      = data.get("handoff_report", "")
                assigned_to = data.get("assigned_to", "")

                review_file = REVIEWS_DIR / f"REVIEW_{todo_id}.md"
                content = f"""# MoCKA Task Review Request
**TODO ID:** {todo_id}
**担当AI:** {assigned_to}
**検知日時:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## handoff_report 全文

{report}

---

## 執行官(Claude)への通知

上記の内容を確認し、整合性チェックおよび本体統合を実施してください。
"""
                with open(review_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"[{datetime.now()}] Generated Review: REVIEW_{todo_id}.md")

                # 処理済みに移動
                target = PROCESSED_DIR / json_file.name
                if target.exists():
                    os.remove(target)
                json_file.rename(target)

        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
