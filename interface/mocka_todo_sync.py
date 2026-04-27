"""
mocka_todo_sync.py - ローカルTODO.json -> Firestore 双方向同期
配置: C:/Users/sirok/MoCKA/interface/mocka_todo_sync.py
"""
import json, os
from pathlib import Path
from datetime import datetime

KEY_PATH   = os.environ.get("MOCKA_FIREBASE_KEY_PATH",
             r"X:\down\MoCKA_Downloads\mocka-knowledge-gate-130cbb27554d.json")
PROJECT_ID = os.environ.get("MOCKA_FIREBASE_PROJECT_ID", "mocka-knowledge-gate")
TODO_PATH  = Path(r"C:/Users/sirok/MOCKA_TODO.json")

def get_db():
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred, {"projectId": PROJECT_ID})
    return firestore.client()

def push_todo_to_firestore(todo_id=None):
    """ローカルTODO.json -> Firestore intent_queue へpush"""
    if not TODO_PATH.exists():
        print("[NG] MOCKA_TODO.json not found")
        return False
    with open(TODO_PATH, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    todos = data.get("todos", [])
    completed = data.get("completed", [])
    all_todos = todos + completed
    if todo_id:
        all_todos = [t for t in all_todos if t.get("id") == todo_id]
    db = get_db()
    col = db.collection("intent_queue")
    pushed = 0
    for todo in all_todos:
        tid = todo.get("id")
        if not tid:
            continue
        doc = {
            "id":          tid,
            "title":       todo.get("title", ""),
            "status":      todo.get("status", "未着手"),
            "priority":    todo.get("priority", "中"),
            "assigned_to": todo.get("assigned_to", ""),
            "note":        todo.get("note", ""),
            "category":    todo.get("category", ""),
            "updated_at":  datetime.now().isoformat(),
            "source":      "local_sync",
        }
        col.document(tid).set(doc, merge=True)
        pushed += 1
    print(f"[OK] {pushed}件 -> Firestore intent_queue にpush完了")
    return True

def pull_from_firestore():
    """Firestore intent_queue -> ローカルTODO.json へ反映（status更新のみ）"""
    if not TODO_PATH.exists():
        print("[NG] MOCKA_TODO.json not found")
        return False
    with open(TODO_PATH, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    db = get_db()
    docs = db.collection("intent_queue").stream()
    updated = 0
    for doc in docs:
        d = doc.to_dict()
        tid = d.get("id") or doc.id
        new_status = d.get("status")
        new_note   = d.get("note", "")
        if not new_status:
            continue
        for todo in data.get("todos", []):
            if todo.get("id") == tid and todo.get("status") != new_status:
                todo["status"] = new_status
                if new_note:
                    todo["note"] = new_note
                updated += 1
    if updated:
        with open(TODO_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] {updated}件 ローカルに反映完了")
    else:
        print("[OK] 更新なし")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--push", action="store_true", help="ローカル->Firestore")
    parser.add_argument("--pull", action="store_true", help="Firestore->ローカル")
    parser.add_argument("--id",   type=str, default=None, help="特定TODO_IDのみ")
    args = parser.parse_args()
    if args.push:
        push_todo_to_firestore(args.id)
    elif args.pull:
        pull_from_firestore()
    else:
        print("使い方: --push (ローカル->Firestore) / --pull (Firestore->ローカル)")