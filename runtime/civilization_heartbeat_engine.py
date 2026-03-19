import json
import os
from datetime import datetime

HEARTBEAT_FILE = "civilization_heartbeat.json"


def run():

    heartbeat = {
        "civilization_heartbeat":{
            "time":datetime.utcnow().isoformat(),
            "status":"alive"
        }
    }

    with open(HEARTBEAT_FILE,"w",encoding="utf-8") as f:
        json.dump(heartbeat,f,indent=2)

    print("CIVILIZATION_HEARTBEAT_EMITTED")


if __name__ == "__main__":
    run()
