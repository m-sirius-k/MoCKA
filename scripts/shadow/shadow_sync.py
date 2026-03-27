import json
import shutil
import time

main = "runtime/main/ledger.json"
shadow = "runtime/shadow/ledger.json"

while True:

    shutil.copy(main,shadow)

    print("SHADOW SYNC")

    time.sleep(5)
