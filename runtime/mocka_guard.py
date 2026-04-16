import json
import os
import sys

BASE_DIR = os.path.dirname(__file__)

ALERT_PATH = os.path.join(BASE_DIR,"incident_alert.json")

def guard():

    if not os.path.exists(ALERT_PATH):
        print("NO_ALERT_FILE")
        return

    with open(ALERT_PATH,"r",encoding="utf-8") as f:
        alert = json.load(f)

    if alert.get("alert"):

        print("MOCKA GUARD TRIGGERED")
        print("SYSTEM HALT RECOMMENDED")

        sys.exit(1)

    else:

        print("MOCKA SYSTEM SAFE")

if __name__ == "__main__":
    guard()
