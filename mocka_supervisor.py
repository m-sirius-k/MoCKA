import subprocess
import time
import os

BASE = r"C:\Users\sirok\MoCKA"

def run(script):
    p = subprocess.run(
        ["python", os.path.join(BASE, script)],
        capture_output=True,
        text=True
    )
    print(p.stdout)
    if p.stderr:
        print(p.stderr)

print("MoCKA Supervisor START")

while True:

    print("---- cycle start ----")

    run("emit_event.py")

    run("state_engine.py")

    run("ledger_snapshot.py")

    run("snapshot_seal.py")

    run("ledger_verify.py")

    run("ledger_repair.py")

    run("node_health_monitor.py")

    print("cycle complete")

    time.sleep(20)
