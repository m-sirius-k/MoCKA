"""
MOCKA Firestore 双方向同期スクリプト v2
APIキーは環境変数から取得（ハードコード禁止）

使い方:
  python mocka_firestore_sync.py push   # ローカル→Firebase
  python mocka_firestore_sync.py pull   # Firebase→ローカル
  python mocka_firestore_sync.py watch  # 60秒ごとに自動同期
"""

import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

PROJECT_ID = os.environ.get("MOCKA_FIREBASE_PROJECT_ID", "mocka-knowledge-gate")
API_KEY    = os.environ.get("MOCKA_FIREBASE_API_KEY", "")

if not API_KEY:
    print("ERROR: 環境変数 MOCKA_FIREBASE_API_KEY が未設定")
    sys.exit(1)

BASE_URL   = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"
COLLECTION = "intent_queue"
TODO_PATH  = Path("C:/Users/sirok/MOCKA_TODO.json")

def to_fs(val):
    if val is None:           return {"nullValue": None}
    if isinstance(val, bool): return {"booleanValue": val}
    if isinstance(val, int):  return {"integerValue": str(val)}
    if isinstance(val, float):return {"doubleValue": val}
    if isinstance(val, str):  return {"stringValue": val}
    if isinstance(val, list): return {"arrayValue": {"values": [to_fs(v) for v in val]}}
    if isinstance(val, dict): return {"mapValue": {"fields": {k: to_fs(v) for k, v in val.items()}}}
    return {"stringValue": str(val)}

def from_fs(fval):
    if "nullValue"    in fval: return None
    if "booleanValue" in fval: return fval["booleanValue"]
    if "integerValue" in fval: return int(fval["integerValue"])
    if "doubleValue"  in fval: return fval["doubleValue"]
    if "stringValue"  in fval: return fval["stringValue"]
    if "arrayValue"   in fval: return [from_fs(v) for v in fval["arrayValue"].get("values", [])]
    if "mapValue"     in fval: return {k: from_fs(v) for k, v in fval["mapValue"].get("fields", {}).items()}
    return None

def fs_get_all():
    url = f"{BASE_URL}/{COLLECTION}?key={API_KEY}&pageSize=200"
    with urllib.request.urlopen(urllib.request.Request(url)) as res:
        data = json.loads(res.read())
    return {doc["name"].split("/")[-1]: {k: from_fs(v) for k, v in doc.get("fields",{}).items()}
            for doc in data.get("documents", [])}

def fs_patch(tid, todo):
    url  = f"{BASE_URL}/{COLLECTION}/{tid}?key={API_KEY}"
    body = json.dumps({"fields": {k: to_fs(v) for k, v in todo.items()}}).encode("utf-8")
    req  = urllib.request.Request(url, data=body, method="PATCH", headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req): pass

def load_local():
    with open(TODO_PATH, encoding="utf-8") as f: return json.load(f)

def save_local(data):
    data["meta"]["updated"]    = datetime.now().strftime("%Y-%m-%d")
    data["meta"]["updated_by"] = "firestore_sync"
    with open(TODO_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def local_map(data):
    return {t["id"]: t for t in data.get("todos",[]) + data.get("completed",[]) if "id" in t}

def cmd_push():
    print("=== PUSH: ローカル → Firestore ===")
    data, ok = load_local(), 0
    todos = local_map(data)
    for tid, todo in todos.items():
        try:
            fs_patch(tid, todo)
            print(f"  ✅ {tid}")
            ok += 1
        except Exception as e:
            print(f"  ❌ {tid}: {e}")
    print(f"\n完了: {ok}/{len(todos)}件")

def cmd_pull():
    print("=== PULL: Firestore → ローカル ===")
    data    = load_local()
    lmap    = local_map(data)
    fb      = fs_get_all()
    updated = 0
    for tid, fb_todo in fb.items():
        if not tid.startswith("TODO_"): continue
        if tid not in lmap:
            data["todos"].append(fb_todo)
            print(f"  ➕ 新規: {tid}")
            updated += 1
        else:
            # 完了報告のみ取り込む（ローカルの完了を未着手に戻さない）
            fb_s  = fb_todo.get("status","")
            loc_s = lmap[tid].get("status","")
            if fb_s == "完了" and loc_s != "完了":
                for lst in [data["todos"], data.get("completed",[])]:
                    for item in lst:
                        if item.get("id") == tid:
                            item["status"] = fb_s
                            if fb_todo.get("note"):         item["note"] = fb_todo["note"]
                            if fb_todo.get("handoff_report"):item["handoff_report"] = fb_todo["handoff_report"]
                            break
                print(f"  🔄 完了取込: {tid}")
                updated += 1
    if updated:
        save_local(data)
        print(f"\nローカル保存: {updated}件更新")
    else:
        print("\n差分なし")

def cmd_watch(interval=60):
    print(f"=== WATCH: {interval}秒ごと自動同期 ===")
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 同期中...")
            cmd_pull()
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n停止"); break
        except Exception as e:
            print(f"エラー: {e}"); time.sleep(interval)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pull"
    if   cmd == "push":  cmd_push()
    elif cmd == "pull":  cmd_pull()
    elif cmd == "watch": cmd_watch()
    else: print("使い方: python mocka_firestore_sync.py [push|pull|watch]")
