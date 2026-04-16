import json
from pathlib import Path

p = Path(r"C:\Users\sirok\MoCKA\audit\recovery\regenesis.json")

with p.open("r", encoding="utf-8") as f:
    data = json.load(f)

if "regensis_event_id" not in data:
    data["regensis_event_id"] = data["tip_event_id"]

with p.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("SAFE_WRITE_OK")
