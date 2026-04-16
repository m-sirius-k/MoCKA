path = r"C:\Users\sirok\MoCKA\app.py"
with open(path, encoding="utf-8") as f:
    src = f.read()

old = r'    PING_PATH    = Path(r"C:\Users\sirok\MoCKA\data\ping_latest.json")'
new = r'    PING_PATH    = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\PACKET\ping_latest.json")'

if old in src:
    src2 = src.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(src2)
    print("OK: PING_PATH → PACKET/ping_latest.json")
else:
    print("ERROR: not found")
