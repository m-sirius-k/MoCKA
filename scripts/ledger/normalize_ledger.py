import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
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