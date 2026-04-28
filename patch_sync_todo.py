import re

path = r"C:\Users\sirok\MoCKA\app.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """@app.route('/sync/todo', methods=['POST'])
def sync_todo():"""

# 関数全体を特定して置換
import re
pattern = r"@app\.route\('/sync/todo'.*?(?=\n@app\.route|\nif __name__)"
match = re.search(pattern, content, re.DOTALL)
if match:
    new_func = """@app.route('/sync/todo', methods=['POST'])
def sync_todo():
    import json as _json
    from pathlib import Path as _Path
    try:
        _TODO = _Path("C:/Users/sirok/MOCKA_TODO.json")
        with _TODO.open("r", encoding="utf-8-sig") as _f:
            _data = _json.load(_f)
        _count = len((_data.get("todos") or []) + (_data.get("completed") or []))
        return _json.dumps({"ok": True, "count": _count, "message": "local only"}), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return _json.dumps({"ok": False, "error": str(e)}), 500, {"Content-Type": "application/json"}

"""
    content = content[:match.start()] + new_func + content[match.end():]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCH OK")
else:
    print("PATTERN NOT FOUND")