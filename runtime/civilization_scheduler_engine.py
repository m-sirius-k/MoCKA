import time
import importlib
from datetime import datetime
import json

SCHEDULER_LOG = "civilization_scheduler_log.json"

LOOP_ENGINE = "civilization_loop_engine"

INTERVAL_SECONDS = 30


def run():

    log = {
        "civilization_scheduler":{
            "start_time":datetime.utcnow().isoformat(),
            "cycles":[]
        }
    }

    while True:

        cycle_entry = {
            "time":datetime.utcnow().isoformat(),
            "status":"unknown"
        }

        try:

            mod = importlib.import_module(LOOP_ENGINE)
            mod.run()

            cycle_entry["status"] = "ok"

        except Exception as e:

            cycle_entry["status"] = "error"
            cycle_entry["error"] = str(e)

        log["civilization_scheduler"]["cycles"].append(cycle_entry)

        with open(SCHEDULER_LOG,"w",encoding="utf-8") as f:
            json.dump(log,f,indent=2)

        print("CIVILIZATION_CYCLE_COMPLETE")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
