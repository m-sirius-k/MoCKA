import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import shutil
import time

main = "runtime/main/ledger.json"

targets = [
    "runtime/shadow_1/ledger.json",
    "runtime/shadow_2/ledger.json",
    "runtime/shadow_3/ledger.json"
]

while True:

    for t in targets:
        shutil.copy(main,t)

    print("MULTI SHADOW SYNC")

    time.sleep(5)
