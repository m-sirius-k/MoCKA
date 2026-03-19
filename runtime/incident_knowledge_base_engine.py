import json
import os
from datetime import datetime

INCIDENT_FILE="incident_ledger.json"
REPAIR_FILE="repair_execution_result.json"
VERIFY_FILE="repair_verification.json"
KB_FILE="incident_knowledge_base.json"

def load_json(path):

    if not os.path.exists(path):
        return None

    with open(path,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def load_kb():

    if not os.path.exists(KB_FILE):
        return []

    with open(KB_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save_kb(data):

    with open(KB_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def main():

    incident=load_json(INCIDENT_FILE)
    repair=load_json(REPAIR_FILE)
    verify=load_json(VERIFY_FILE)

    kb=load_kb()

    record={
        "timestamp":datetime.utcnow().isoformat(),
        "incident":incident,
        "repair":repair,
        "verification":verify
    }

    kb.append(record)

    save_kb(kb)

    print("KNOWLEDGE_BASE_UPDATED")

if __name__=="__main__":
    main()
