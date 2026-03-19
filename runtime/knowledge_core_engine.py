import json
import os
from datetime import datetime

FILES = [
"civilization_research_lab_log.json",
"civilization_knowledge_graph.json",
"civilization_theory.json",
"civilization_philosophy.json",
"civilization_culture.json",
"civilization_institutions.json"
]

OUTPUT_FILE = "civilization_knowledge_core.json"


def load_json(path):

    if os.path.exists(path):

        try:
            with open(path,"r",encoding="utf-8") as f:
                return json.load(f)

        except:
            return None

    return None


def run():

    core = {
        "civilization_knowledge_core":{
            "time":datetime.utcnow().isoformat(),
            "modules":{}
        }
    }

    for f in FILES:

        core["civilization_knowledge_core"]["modules"][f] = load_json(f)

    with open(OUTPUT_FILE,"w",encoding="utf-8") as fp:
        json.dump(core,fp,indent=2)

    print("CIVILIZATION_KNOWLEDGE_CORE_UPDATED")


if __name__ == "__main__":
    run()
