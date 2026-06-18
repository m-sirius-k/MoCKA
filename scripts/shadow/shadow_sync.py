import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import shutil
import time

main = "runtime/main/ledger.json"
shadow = "runtime/shadow/ledger.json"

while True:

    shutil.copy(main,shadow)

    print("SHADOW SYNC")

    time.sleep(5)
