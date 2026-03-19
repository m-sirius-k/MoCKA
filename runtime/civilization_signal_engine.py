import json
import os
from datetime import datetime

IDENTITY_FILE = "civilization_identity.json"
SIGNAL_FILE = "civilization_signal.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def run():

    identity = load_json(IDENTITY_FILE)

    signal = {
        "civilization_signal":{
            "status":"active",
            "identity":identity,
            "signal_time":datetime.utcnow().isoformat()
        }
    }

    save_json(SIGNAL_FILE,signal)

    print("CIVILIZATION_SIGNAL_EMITTED")


if __name__ == "__main__":
    run()
