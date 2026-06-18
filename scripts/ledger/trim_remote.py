import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json

p="runtime/remote_ledger.json"

with open(p,"r",encoding="utf-8") as f:
    d=json.load(f)

d=d[:-2]

with open(p,"w",encoding="utf-8") as f:
    json.dump(d,f,indent=2)

print("REMOTE LEDGER TRIMMED")
