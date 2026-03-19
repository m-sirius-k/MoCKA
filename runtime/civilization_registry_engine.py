import json
import os
from datetime import datetime

REGISTRY_FILE = "civilization_registry.json"

ENGINE_LIST = [
"civilization_culture_engine.py",
"civilization_institution_engine.py",
"civilization_economy_engine.py",
"civilization_memory_engine.py",
"civilization_archive_engine.py",
"civilization_timeline_engine.py",
"civilization_identity_engine.py",
"civilization_signal_engine.py",
"civilization_observer_engine.py",
"civilization_guardian_engine.py",
"civilization_council_engine.py",
"civilization_decision_engine.py",
"civilization_action_engine.py",
"civilization_feedback_engine.py",
"civilization_learning_engine.py",
"civilization_evolution_engine.py",
"civilization_meta_engine.py"
]


def run():

    registry = {
        "civilization_registry":{
            "time":datetime.utcnow().isoformat(),
            "engine_count":0,
            "engines":[]
        }
    }

    for engine in ENGINE_LIST:

        entry = {
            "engine":engine,
            "exists":os.path.exists(engine)
        }

        registry["civilization_registry"]["engines"].append(entry)

    registry["civilization_registry"]["engine_count"] = len(registry["civilization_registry"]["engines"])

    with open(REGISTRY_FILE,"w",encoding="utf-8") as f:
        json.dump(registry,f,indent=2)

    print("CIVILIZATION_REGISTRY_CREATED")


if __name__ == "__main__":
    run()
