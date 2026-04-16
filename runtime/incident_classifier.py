import json
import os
import re

BASE_DIR = os.path.dirname(__file__)

LEDGER_PATH = os.path.join(BASE_DIR,"incident_ledger.json")
CLASS_PATH = os.path.join(BASE_DIR,"incident_classification.json")

def extract_exception(text):

    lines = text.splitlines()

    for line in reversed(lines):

        m = re.match(r"([A-Za-z_]+Error|Exception)",line)

        if m:
            return m.group(1)

    return "Unknown"

def classify():

    if not os.path.exists(LEDGER_PATH):
        print("NO_LEDGER")
        return

    with open(LEDGER_PATH,"r",encoding="utf-8") as f:
        ledger = json.load(f)

    classes = {}

    for event in ledger:

        content = event.get("content","")

        exc = extract_exception(content)

        if exc not in classes:

            classes[exc] = {
                "count":0
            }

        classes[exc]["count"] += event.get("repeat_count",1)

    with open(CLASS_PATH,"w",encoding="utf-8") as f:
        json.dump(classes,f,indent=2)

    print("INCIDENT_CLASSIFICATION_UPDATED")

if __name__ == "__main__":
    classify()
