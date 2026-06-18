import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import sys
sys.path.insert(0, r"C:\Users\sirok\MoCKA")
from schema.schema import verify_ledger

if verify_ledger():
    print("LEDGER OK")
else:
    print("LEDGER ERROR")
