import time
import importlib
import json
from datetime import datetime

ENGINES = [
"observatory_engine",
"knowledge_core_engine",
"storage_engine",
"audit_engine"
]

LOG_FILE = "civilization_runtime_log.json"

INTERVAL_SECONDS = 30


def run_cycle():

    results = []

    for engine in ENGINES:

        entry = {
            "engine":engine,
            "status":"ok"
        }

        try:

            module = importlib.import_module(engine)
            module.run()

        except Exception as e:

            entry["status"] = "error"
            entry["error"] = str(e)

        results.append(entry)

    return results


def run():

    runtime_log = {
        "civilization_runtime":{
            "start_time":datetime.utcnow().isoformat(),
            "cycles":[]
        }
    }

    print("MOCKA CIVILIZATION RUNTIME START")

    while True:

        cycle = {
            "time":datetime.utcnow().isoformat(),
            "engines":run_cycle()
        }

        runtime_log["civilization_runtime"]["cycles"].append(cycle)

        with open(LOG_FILE,"w",encoding="utf-8") as f:
            json.dump(runtime_log,f,indent=2)

        print("CIVILIZATION CYCLE COMPLETE")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
