import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import time
import os
import subprocess

EVENT_PATH = "runtime/events.json"
last = 0

print("EVENT WATCHER START")

while True:
    if os.path.exists(EVENT_PATH):
        t = os.path.getmtime(EVENT_PATH)

        if t != last:
            last = t
            print("EVENT DETECTED")

            subprocess.run(["python", "runtime/event_ingestor.py"])
            subprocess.run(["python", "runtime/action_selector.py"])

    time.sleep(1)
