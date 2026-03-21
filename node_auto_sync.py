import subprocess
import time

while True:

    subprocess.run(["python","ledger_diff.py"])
    subprocess.run(["python","ledger_sync.py"])

    print("AUTO SYNC DONE")

    time.sleep(60)

