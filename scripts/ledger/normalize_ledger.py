import json

with open("runtime/incident_ledger.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("runtime/incident_ledger.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )

print("NORMALIZED")