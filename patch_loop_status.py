import re

path = r"C:\Users\sirok\MoCKA\app.py"
with open(path, encoding="utf-8") as f:
    src = f.read()

# loop_status関数全体を置換
old_func = re.search(
    r'@app\.route\("/loop/status"\).*?@app\.route\("/loop/inject_toggle"',
    src, re.DOTALL
).group()[:-len('@app.route("/loop/inject_toggle')]

new_func = r'''@app.route("/loop/status")
def loop_status():
    import json, datetime
    from pathlib import Path
    ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    INJECT_FLAG  = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    PING_PATH    = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\PACKET\ping_latest.json")
    RAW_DIR      = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW")

    inject_mode = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8").strip().upper()
        inject_mode = v if v in ["ON","OFF"] else "ON"

    essence_count = 0
    if ESSENCE_PATH.exists():
        try:
            data = json.loads(ESSENCE_PATH.read_text(encoding="utf-8"))
            essence_count = len(data.get("essence", []))
        except:
            pass

    ping_data = {}
    ping_age = None
    if PING_PATH.exists():
        try:
            text = PING_PATH.read_text(encoding="utf-8")
            ping_data = json.loads(text)
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            ping_age = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except:
            pass

    raw_count = len(list(RAW_DIR.glob("*.json"))) if RAW_DIR.exists() else 0

    return jsonify({
        "inject_mode":   inject_mode,
        "essence_count": essence_count,
        "raw_count":     raw_count,
        "ping_latest":   ping_data,
        "ping_age":      ping_age,
    })

'''

src2 = src.replace(old_func, new_func)
if src2 != src:
    with open(path, "w", encoding="utf-8") as f:
        f.write(src2)
    print("OK: loop_status rewritten")
else:
    print("ERROR: no change")
