import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import shutil
import time

SRC = "runtime/state.json"

TARGETS = [
"runtime/shadow_1/state.json",
"runtime/shadow_2/state.json",
"runtime/shadow_3/state.json"
]

while True:

    for t in TARGETS:

        try:
            shutil.copyfile(SRC,t)
        except:
            pass

    print("STATE SYNC")

    time.sleep(5)
