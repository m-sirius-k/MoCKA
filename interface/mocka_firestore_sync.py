"""
MOCKA Firestore 双方向同期スクリプト
ローカル MOCKA_TODO.json ↔ Firestore intent_queue

使い方:
  python mocka_firestore_sync.py push   # ローカル→Firebase
  python mocka_firestore_sync.py pull   # Firebase→ローカル
  python mocka_firestore_sync.py watch  # 60秒ごとに自動同期（pull優先）
"""

import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Firebase設定
PROJECT_ID = "mocka-knowledge-gate"
API_KEY = "AIzaSyCZWcJ3UmS3ux02LKYFGEBkOKuIZ7LSNFg"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
COLLECTION = "intent_queue"

# ローカルパス
TODO_PATH = Path("C:/Users/sirok/MOCKA_TODO.json")


# ── Firestore変換ユーティリティ ──────────────────────────

def to_firestore_value(val):
    if val is None:
        return {"nullValue": None}
    elif isinstance(val, bool):
        return {"booleanValue": val}
    elif isinstance(val, int):
        return {"integerValue": str(val)}
    elif isinstance(val, float):
        return {"doubleValue": val}
    elif isinstance(val, str):
        return {"stringValue": val}
    elif isinstance(val, list):
        return {"arrayValue": {"values": [to_firestore_value(v) for v in val]}}
    elif isinstance(val, dict):
        return {"mapValue": {"fields": {k: to_firestore_value(v) for k, v in val.items()}}}
    else:
        return {"stringValue": str(val)}


def from_firestore_value(fval: dict):
    if "nullValue" in fval:
        return None
    elif "booleanValue" in fval:
        return fval["booleanValue"]
    elif "integerValue" in fval:
        return int(fval["integerValue"])
    elif "doubleValue" in fval:
        return fval["doubleValue"]
    elif "stringValue" in fval:
        return fval["stringValue"]
    elif "arrayValue" in fval:
        return [from_firestore_value(v) for v in fval["arrayValue"].get("values", [])]
    elif "mapValue" in fval:
        return {k: from_firestore_value(v) for k, v in fval["mapValue"].get("fields", {}).items()}
    return None


def fields_to_dict(fields: dict) -> dict:
    return {k: from_firestore_value(v) for k, v in fields.items()}


# ── Firestore REST API ───────────────────────────────────

def firestore_get_all() -> dict:
    """intent_queue全件取得 → {todo_id: dict}"""
    url = f"{BASE_URL}/{COLLECTION}?key={API_KEY}&pageSize=200"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
    result = {}
    for doc in data.get("documents", []):
        name = doc["name"].split("/")[-1]
        result[name] = fields_to_dict(doc.get("fields", {}))
    return result


def firestore_patch(todo_id: str, todo: dict):
    """1件をFirestoreにPATCH（upsert）"""
    url = f"{BASE_URL}/{COLLECTION}/{todo_id}?key={API_KEY}"
    fields = {k: to_firestore_value(v) for k, v in todo.items()}
    body = json.dumps({"fields": fields}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH",
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req):
        pass


# ── ローカルI/O ──────────────────────────────────────────

def load_local() -> dict:
    with open(TODO_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_local(data: dict):
    data["meta"]["updated"] = datetime.now().strftime("%Y-%m-%d")
    data["meta"]["updated_by"] = "firestore_sync"
    with open(TODO_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def local_todos_map(data: dict) -> dict:
    """todos + completed を {id: dict} で返す"""
    result = {}
    for t in data.get("todos", []) + data.get("completed", []):
        if "id" in t:
            result[t["id"]] = t
    return result


# ── PUSH: ローカル → Firebase ────────────────────────────

def cmd_push():
    print("=== PUSH: ローカル → Firestore ===")
    data = load_local()
    todos = local_todos_map(data)
    success = 0
    for tid, todo in todos.items():
        try:
            firestore_patch(tid, todo)
            print(f"  ✅ {tid}")
            success += 1
        except Exception as e:
            print(f"  ❌ {tid}: {e}")
    print(f"\n完了: {success}/{len(todos)}件")


# ── PULL: Firebase → ローカル ────────────────────────────

def cmd_pull():
    print("=== PULL: Firestore → ローカル ===")
    data = load_local()
    local_map = local_todos_map(data)

    fb_map = firestore_get_all()
    updated = 0

    for tid, fb_todo in fb_map.items():
        if tid not in local_map:
            # 新規（他AIが追加）→ todosに追加
            data["todos"].append(fb_todo)
            print(f"  ➕ 新規追加: {tid}")
            updated += 1
        else:
            local = local_map[tid]
            fb_status = fb_todo.get("status", "")
            local_status = local.get("status", "")

            # Firebaseの方がステータスが進んでいれば上書き
            if fb_status != local_status:
                # todos/completedどちらに入っているか特定して更新
                for lst in [data["todos"], data.get("completed", [])]:
                    for item in lst:
                        if item.get("id") == tid:
                            item["status"] = fb_status
                            if fb_todo.get("note"):
                                item["note"] = fb_todo["note"]
                            if fb_todo.get("handoff_report"):
                                item["handoff_report"] = fb_todo["handoff_report"]
                            break
                print(f"  🔄 更新: {tid} [{local_status}→{fb_status}]")
                updated += 1

    if updated:
        save_local(data)
        print(f"\nローカル保存完了: {updated}件更新")
    else:
        print("\n差分なし")


# ── WATCH: 自動同期 ──────────────────────────────────────

def cmd_watch(interval=60):
    print(f"=== WATCH: {interval}秒ごとに自動同期 (Ctrl+Cで停止) ===\n")
    while True:
        try:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] 同期中...")
            cmd_pull()
            print(f"次回: {interval}秒後\n")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n停止")
            break
        except Exception as e:
            print(f"エラー: {e} → {interval}秒後に再試行")
            time.sleep(interval)


# ── エントリーポイント ───────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pull"
    if cmd == "push":
        cmd_push()
    elif cmd == "pull":
        cmd_pull()
    elif cmd == "watch":
        cmd_watch()
    else:
        print("使い方: python mocka_firestore_sync.py [push|pull|watch]")
