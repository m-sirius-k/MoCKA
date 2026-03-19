import importlib
import json
from datetime import datetime

LOOP_LOG_FILE = "civilization_loop_log.json"

ENGINE_ORDER = [
"civilization_heartbeat_engine",
"civilization_monitor_engine",
"civilization_status_engine",
"civilization_culture_engine",
"civilization_institution_engine",
"civilization_economy_engine",
"civilization_memory_engine",
"civilization_archive_engine",
"civilization_timeline_engine",
"civilization_identity_engine",
"civilization_signal_engine",
"civilization_observer_engine",
"civilization_guardian_engine",
"civilization_council_engine",
"civilization_decision_engine",
"civilization_action_engine",
"civilization_feedback_engine",
"civilization_learning_engine",
"civilization_evolution_engine",
"civilization_meta_engine",
"civilization_registry_engine"
]


def run():

    log = {
        "civilization_loop":{
            "time":datetime.utcnow().isoformat(),
            "engines":[]
        }
    }

    for engine in ENGINE_ORDER:

        try:

            mod = importlib.import_module(engine)
            mod.run()

            log["civilization_loop"]["engines"].append({
                "engine":engine,
                "status":"ok"
            })

        except Exception as e:

            log["civilization_loop"]["engines"].append({
                "engine":engine,
                "status":"error",
                "error":str(e)
            })

    with open(LOOP_LOG_FILE,"w",encoding="utf-8") as f:
        json.dump(log,f,indent=2)

    print("CIVILIZATION_LOOP_COMPLETE")


if __name__ == "__main__":
    run()
