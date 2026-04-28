with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

new_block = """
@app.route('/sync/todo', methods=['POST'])
def sync_todo():
    print("SYNC_TODO_V4_ADMINSDK_ENTERED")
    try:
        import json as _json
        from pathlib import Path as _Path
        import firebase_admin
        from firebase_admin import credentials as _creds, firestore as _firestore
        _KEY_PATH = _Path("C:/Users/sirok/MoCKA/secrets/firebase_adminsdk.json")
        if not firebase_admin._apps:
            _cred = _creds.Certificate(str(_KEY_PATH))
            firebase_admin.initialize_app(_cred)
        _db = _firestore.client()
        _TODO = _Path("C:/Users/sirok/MOCKA_TODO.json")
        with _TODO.open("r", encoding="utf-8-sig") as _f:
            _data = _json.load(_f)
        _raw = (_data.get("todos") or []) + (_data.get("completed") or [])
        _todos = {}
        for _t in _raw:
            if not isinstance(_t, dict): continue
            _tid = _t.get("id")
            if _tid is None: continue
            _todos[str(_tid)] = _t
        _ok, _errors = 0, []
        _col = _db.collection("todos")
        for tid, todo in _todos.items():
            try:
                _col.document(tid).set(todo, merge=True)
                _ok += 1
            except Exception as e:
                _errors.append(str(e)[:60])
        from flask import jsonify
        return jsonify({"status": "ok", "pushed": _ok, "total": len(_todos), "errors": _errors[:5]})
    except Exception as e:
        from flask import jsonify
        return jsonify({"status": "error", "message": str(e)}), 500

"""

target = 'if __name__ == "__main__":'
content = content.replace(target, new_block + target)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
print("DONE")