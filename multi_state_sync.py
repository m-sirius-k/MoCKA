import shutil
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
