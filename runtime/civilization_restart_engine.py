import json
import importlib
from datetime import datetime

RESTART_LOG_FILE = "civilization_restart_log.json"
BOOT_ENGINE = "civilization_boot_engine"


def run():

    log = {
        "civilization_restart":{
            "time":datetime.utcnow().isoformat(),
            "status":"starting"
        }
    }

    try:

        mod = importlib.import_module(BOOT_ENGINE)
        mod.run()

        log["civilization_restart"]["status"] = "booted"

    except Exception as e:

        log["civilization_restart"]["status"] = "error"
        log["civilization_restart"]["error"] = str(e)

    with open(RESTART_LOG_FILE,"w",encoding="utf-8") as f:
        json.dump(log,f,indent=2)

    print("CIVILIZATION_RESTART_COMPLETE")


if __name__ == "__main__":
    run()
