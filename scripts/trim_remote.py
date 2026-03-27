import json

p="runtime/remote_ledger.json"

with open(p,"r",encoding="utf-8") as f:
    d=json.load(f)

d=d[:-2]

with open(p,"w",encoding="utf-8") as f:
    json.dump(d,f,indent=2)

print("REMOTE LEDGER TRIMMED")
