path = r"C:\Users\sirok\MoCKA\app.py"
with open(path, encoding="utf-8") as f:
    src = f.read()

old = r"""    ping_data, ping_age = {}, None
    if PING_PATH.exists():
        try:
            ping_data = json.loads(PING_PATH.read_text(encoding="utf-8"))
            age = datetime.datetime.now().timestamp() - PING_PATH.stat().st_mtime
            ping_age = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
        except: pass"""

new = r"""    ping_data, ping_age = {}, None
    # ping_latest.jsonを両パスから探す
    for pp in [PING_PATH,
               Path(r"C:\Users\sirok\MoCKA\data\storage\infield\PACKET\ping_latest.json")]:
        if pp.exists():
            try:
                raw = json.loads(pp.read_text(encoding="utf-8"))
                # ESSENCE_TRIGGER形式 or DNA形式どちらでも表示
                ping_data = raw
                age = datetime.datetime.now().timestamp() - pp.stat().st_mtime
                ping_age = f"{int(age//3600)}h {int((age%3600)//60)}m ago"
                break
            except: pass"""

if old in src:
    src2 = src.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src2)
    print("OK: ping parse fixed")
else:
    print("ERROR: pattern not found")
