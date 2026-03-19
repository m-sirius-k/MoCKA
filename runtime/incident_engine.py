import json
import time
import os
import subprocess
import hashlib

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR,".."))
LEDGER_PATH = os.path.join(BASE_DIR,"incident_ledger.json")

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

    try:

        subprocess.run(["git","add","runtime/incident_ledger.json"],cwd=ROOT_DIR)
        subprocess.run(["git","commit","-m","MoCKA incident batch update"],cwd=ROOT_DIR)
        subprocess.run(["git","push"],cwd=ROOT_DIR)

        print("INCIDENT_BATCH_GIT_RECORDED")

    except Exception as e:

        print("GIT_RECORD_FAILED",str(e))

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

