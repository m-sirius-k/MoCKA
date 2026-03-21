import json
import time
import hashlib
from pathlib import Path
from mutation_engine import choose_mutation

MAIN_LEDGER = Path("runtime/main/ledger.json")
BRANCH_DIR = Path("runtime/branches")

FUTURE_STEPS = 5
PARALLEL_BRANCHES = 5


def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(p, data):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def hash_event(event):
    s = json.dumps(event, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()


def generate_event(last_event):

    event_type = choose_mutation()

    payload = {
        "mutation": event_type,
        "value": int(time.time()) % 100
    }

    event = {
        "event_id": last_event["event_id"] + 1,
        "timestamp": int(time.time()),
        "type": event_type,
        "payload": payload,
        "prev_hash": last_event["event_hash"]
    }

    event["event_hash"] = hash_event(event)

    return event


def create_branch(base_ledger):

    branch_events = list(base_ledger)

    last = branch_events[-1]

    for _ in range(FUTURE_STEPS):

        new_event = generate_event(last)

        branch_events.append(new_event)

        last = new_event

    branch_name = "branch_" + str(int(time.time() * 1000))

    branch_path = BRANCH_DIR / branch_name

    branch_path.mkdir(parents=True, exist_ok=True)

    save_json(branch_path / "ledger.json", branch_events)

    print("branch created:", branch_name)


def main():

    ledger = load_json(MAIN_LEDGER)

    print("ledger events:", len(ledger))

    for _ in range(PARALLEL_BRANCHES):
        create_branch(ledger)

    print("parallel branches:", PARALLEL_BRANCHES)
    print("future steps:", FUTURE_STEPS)


if __name__ == "__main__":
    main()
