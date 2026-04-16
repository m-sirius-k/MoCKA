path = r"C:\Users\sirok\MoCKA\app.py"
with open(path, encoding="utf-8") as f:
    src = f.read()

new_endpoints = r"""
# ── LOOP STATUS ──────────────────────────────────────────
@app.route("/loop/status")
def loop_status():
    import json, datetime
    from pathlib import Path
    ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
    INJECT_FLAG  = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    PING_PATH    = Path(r"C:\Users\sirok\MoCKA\ping_latest.json")
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
        except: pass

    ping_data, ping_age = {}, None
    if PING_PATH.exists():
        try:
            ping_data = json.loads(PING_PATH.read_text(encoding="utf-8"))
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            ping_age = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except: pass

    raw_count = len(list(RAW_DIR.glob("*.json"))) if RAW_DIR.exists() else 0

    return jsonify({
        "inject_mode":   inject_mode,
        "essence_count": essence_count,
        "raw_count":     raw_count,
        "ping_latest":   ping_data,
        "ping_age":      ping_age,
    })

@app.route("/loop/inject_toggle", methods=["POST"])
def inject_toggle():
    from pathlib import Path
    INJECT_FLAG = Path(r"C:\Users\sirok\MOCKA_INJECT_MODE.txt")
    current = "ON"
    if INJECT_FLAG.exists():
        v = INJECT_FLAG.read_text(encoding="utf-8").strip().upper()
        current = v if v in ["ON","OFF"] else "ON"
    new_mode = "OFF" if current == "ON" else "ON"
    INJECT_FLAG.write_text(new_mode, encoding="utf-8")
    return jsonify({"inject_mode": new_mode})

"""

old = 'if __name__ == "__main__":'
if old in src:
    src2 = src.replace(old, new_endpoints + old)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src2)
    print("OK: /loop/status + /loop/inject_toggle added")
else:
    print("ERROR: not found")
    print(repr(src[-200:]))
