import json

path = "runtime/ledger.json"

with open(path, "r", encoding="utf-8-sig") as f:
    txt = f.read()

# JSON配列の中身を強制抽出
items = []
buf = ""
depth = 0

for c in txt:
    if c == "{":
        depth += 1
    if depth > 0:
        buf += c
    if c == "}":
        depth -= 1
        if depth == 0:
            try:
                obj = json.loads(buf)
                items.append(obj)
            except:
                pass
            buf = ""

with open(path, "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2)

print("LEDGER RECOVERED:", len(items))
