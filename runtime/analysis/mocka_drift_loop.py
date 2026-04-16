# mocka_drift_loop.py
# Phase5-B2+: 停止制御付きループ

import time
import subprocess
import os

BASE = r"C:\Users\sirok\MoCKA"

PIPELINE = [
    "runtime\\analysis\\drift_predictor.py",
    "runtime\\analysis\\caliber_drift_bridge.py",
    "runtime\\analysis\\router_guard.py",
    "runtime\\analysis\\drift_logger.py",
    "runtime\\analysis\\dashboard_drift_view.py"
]

INTERVAL = 5
STOP_FILE = BASE + r"\\runtime\\control\\STOP"

def run_step(script):
    path = BASE + "\\" + script
    print(f"\\n[RUN] {script}")
    subprocess.run(["python", path])

def check_stop():
    return os.path.exists(STOP_FILE)

def main():
    print("=== MoCKA Drift Loop START ===")

    while True:
        if check_stop():
            print("\\n[STOP DETECTED] Loop terminated safely.")
            break

        for step in PIPELINE:
            run_step(step)

        print("\\n--- cycle complete ---")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
