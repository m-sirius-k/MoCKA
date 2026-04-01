import subprocess
import json
import os
from datetime import datetime

LOG_PATH = r"C:\Users\sirok\MoCKA\data\events.csv"

def run_caliber():
    result = subprocess.run(
        ["python", r"C:\Users\sirok\MoCKA\caliber\caliber_engine.py"],
        capture_output=True,
        text=True
    )
    return result.stdout

def extract_drift(output):
    try:
        data_start = output.find("{")
        data = json.loads(output[data_start:])
        return data["scores"]["D"]
    except:
        return 5  # 異常扱い

def evaluate_caliber():
    output = run_caliber()
    drift = extract_drift(output)

    if drift <= 1.5:
        status = "CALIBER_NORMAL"
    elif drift <= 3.0:
        status = "CALIBER_WARNING"
    elif drift <= 4.0:
        status = "CALIBER_DANGER"
    else:
        status = "CALIBER_CRITICAL"

    return drift, status

def write_log(drift, status):
    if not os.path.exists(LOG_PATH):
        return

    timestamp = datetime.now().isoformat()
    event = f"{timestamp},caliber_b,monitor,drift={drift}:{status}\n"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(event)

def main():
    drift, status = evaluate_caliber()
    write_log(drift, status)

    print("=== Caliber-B Monitor ===")
    print("drift:", drift)
    print("status:", status)

if __name__ == "__main__":
    main()

