import json
from datetime import datetime

SHUTDOWN_FILE = "civilization_shutdown_log.json"


def run():

    shutdown = {
        "civilization_shutdown":{
            "time":datetime.utcnow().isoformat(),
            "status":"stopped"
        }
    }

    with open(SHUTDOWN_FILE,"w",encoding="utf-8") as f:
        json.dump(shutdown,f,indent=2)

    print("CIVILIZATION_SHUTDOWN_COMPLETE")


if __name__ == "__main__":
    run()
