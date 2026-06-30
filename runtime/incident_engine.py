import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import json
import time
import os
import subprocess
import hashlib
import sys

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR,".."))
LEDGER_PATH = os.path.join(BASE_DIR,"incident_ledger.json")

sys.path.insert(0, os.path.join(ROOT_DIR, "governance"))
from mocka_git_safe_commit import mocka_git_safe_commit  # noqa: E402

COMMIT_INTERVAL = 10

def load_ledger():

    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH,"r",encoding="utf-8") as f:
            return json.load(f)

    return []

def save_ledger(data):

    with open(LEDGER_PATH,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def git_commit():
    # TODO_364: git add/commit/pushをmocka_git_safe_commit経由に統一。
    result = mocka_git_safe_commit(
        paths=["runtime/incident_ledger.json"],
        message="MoCKA incident batch update",
        push=True, root=ROOT_DIR
    )
    if result["error"]:
        print("GIT_RECORD_FAILED", result["error"])
    else:
        print("INCIDENT_BATCH_GIT_RECORDED")

def incident_hash(title,content,source):

    raw = title + content + source
    return hashlib.sha256(raw.encode()).hexdigest()

def record_event(
    event_type,
    actor,
    title,
    content,
    source,
    impact,
    focus_point,
    incident_candidate
):

    ledger = load_ledger()
    now = int(time.time())

    hash_id = incident_hash(title,content,source)

    if ledger:

        last = ledger[-1]

        if last.get("incident_hash") == hash_id:

            last["repeat_count"] = last.get("repeat_count",1) + 1
            last["last_seen"] = now

            save_ledger(ledger)

            if last["repeat_count"] % COMMIT_INTERVAL == 0:
                git_commit()

            print("INCIDENT_AGGREGATED",hash_id,last["repeat_count"])
            return

    event = {
        "timestamp": now,
        "first_seen": now,
        "last_seen": now,
        "repeat_count": 1,
        "incident_hash": hash_id,
        "event_type": event_type,
        "actor": actor,
        "title": title,
        "content": content,
        "source": source,
        "impact": impact,
        "focus_point": focus_point,
        "incident_candidate": incident_candidate
    }

    ledger.append(event)

    save_ledger(ledger)
    git_commit()

    print("INCIDENT_RECORDED",hash_id)

