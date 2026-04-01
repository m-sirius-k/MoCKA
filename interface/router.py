import csv
import os
import time
from datetime import datetime

EVENTS_PATH = r"C:\Users\sirok\MoCKA\data\events.csv"

def read_recent(n=10):
    if not os.path.exists(EVENTS_PATH):
        return []
    with open(EVENTS_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    return rows[-n:]

def calc_error_rate():
    rows = read_recent()
    if not rows:
        return 0.0
    err = sum(1 for r in rows if "ERROR" in str(r))
    return round(err / max(len(rows), 1), 2)

def get_router_mode():
    rows = read_recent()
    err = sum(1 for r in rows if "ERROR" in str(r))
    score = err * 0.5

    if score < 1.0:
        return "full_orchestra"
    if score < 2.0:
        return "share_only"
    if score < 3.0:
        return "save_only"
    return "audit_mode"

def record(event_type, note):
    os.makedirs(os.path.dirname(EVENTS_PATH), exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    event_id = f"E{timestamp}"

    error_rate = calc_error_rate()
    mode = get_router_mode()

    free_note = f"{note} | error_rate={error_rate} | router_mode={mode}"

    row = [event_id, event_type, free_note]

    with open(EVENTS_PATH, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    print(f"[saved] {event_id} {free_note}")

def save(title, note):
    record("save", note)

def collaborate(query):
    start = time.time()

    mode = get_router_mode()
    print(f"[RouterMode] {mode}")

    # 疑似処理
    time.sleep(1)

    end = time.time()
    response_time = round(end - start, 2)

    note = f"{query} | response_time={response_time}s"
    record("collaborate", note)

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2:
        cmd = sys.argv[1]

        if cmd == "save":
            save(sys.argv[2], sys.argv[3])
        elif cmd == "collaborate":
            collaborate(sys.argv[2])
