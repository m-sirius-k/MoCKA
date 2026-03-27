import json
import os
from datetime import datetime

LEDGER_PATH = "runtime/ledger.json"

def main():
    if not os.path.exists(LEDGER_PATH):
        print("NO LEDGER")
        return

    with open(LEDGER_PATH, "r", encoding="utf-8-sig") as f:
        ledger = json.load(f)

    print("=== LEDGER VIEW ===")

    for i, ev in enumerate(ledger):
        ts = datetime.fromtimestamp(ev["ts"]).strftime("%Y-%m-%d %H:%M:%S")

        if ev.get("type") == "DSL_APPLY":
            ctxs = ",".join(ev.get("contexts", []))
            exp = ev.get("experiment_id", "LEGACY")
            print(f"[{i}] {ts} | EXP {exp} START → [{ctxs}]")

        elif ev.get("type") == "ACTION":
            exp = ev.get("experiment_id", "LEGACY")
            print(f"[{i}] {ts} | EXP {exp} | {ev['context']} → {ev['action']} (w={ev['weight']})")

        elif "context" in ev and "action" in ev:
            print(f"[{i}] {ts} | LEGACY {ev['context']} → {ev['action']}")

        else:
            print(f"[{i}] {ts} | UNKNOWN")

if __name__ == "__main__":
    main()
