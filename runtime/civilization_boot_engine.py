import importlib
from datetime import datetime
import json

BOOT_LOG_FILE = "civilization_boot_log.json"

ENGINE_SEQUENCE = [
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

    boot_log = {
        "civilization_boot":{
            "time":datetime.utcnow().isoformat(),
            "engines_run":[]
        }
    }

    for engine in ENGINE_SEQUENCE:

        try:
            mod = importlib.import_module(engine)
            mod.run()

            boot_log["civilization_boot"]["engines_run"].append({
                "engine":engine,
                "status":"ok"
            })

        except Exception as e:

            boot_log["civilization_boot"]["engines_run"].append({
                "engine":engine,
                "status":"error",
                "error":str(e)
            })

    with open(BOOT_LOG_FILE,"w",encoding="utf-8") as f:
        json.dump(boot_log,f,indent=2)

    print("CIVILIZATION_BOOT_COMPLETE")


if __name__ == "__main__":
    run()
