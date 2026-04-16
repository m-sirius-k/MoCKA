import json
from pathlib import Path

AUDIT_DIR = Path(r"C:\Users\sirok\MoCKA\audit")
LAST_EVENT_FILE = AUDIT_DIR / "last_event_id.txt"

events = {}

for f in AUDIT_DIR.glob("*.json"):
    try:
        with open(f, "r", encoding="utf-8-sig") as fh:
            obj = json.load(fh)
        eid = obj.get("event_id")
        if not eid:
            continue
        events[eid] = obj.get("previous_event_id")
    except Exception:
        continue

if not LAST_EVENT_FILE.exists():
    print("NO LAST_EVENT_ID")
    raise SystemExit(1)

current = LAST_EVENT_FILE.read_text(encoding="utf-8").strip()

visited = set()

while True:
    prev = events.get(current, "__MISSING__")
    print("EVENT:", current, "PREV:", prev)

    if current in visited:
        print("LOOP AT:", current)
        break

    visited.add(current)

    if prev in (None, "", "__MISSING__"):
        if prev == "__MISSING__":
            print("BROKEN LINK: event json not found for current id")
        break

    current = prev

print("DONE")