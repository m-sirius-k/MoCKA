import json
import os
from datetime import datetime

CULTURE_FILE = "civilization_culture.json"
THEORY_FILE = "civilization_theory.json"
GRAPH_FILE = "civilization_knowledge_graph.json"
RESEARCH_FILE = "civilization_research_lab_log.json"


def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)


def get_last_research_success(research):

    if research is None:
        return False

    if isinstance(research, list):
        if len(research) == 0:
            return False
        last = research[-1]
        return last.get("success", False)

    if isinstance(research, dict):
        return research.get("success", False)

    return False


def run():

    theory = load_json(THEORY_FILE)
    graph = load_json(GRAPH_FILE)
    research = load_json(RESEARCH_FILE)
    culture = load_json(CULTURE_FILE)

    if culture is None:
        culture = {
            "civilization_culture":[],
            "last_update":None
        }

    dominant = None
    if theory:
        dominant = theory.get("dominant_strategy")

    node_count = 0
    if graph:
        node_count = graph.get("nodes",0)

    success = get_last_research_success(research)

    if dominant and success:

        entry = {
            "strategy":dominant,
            "type":"successful_research",
            "knowledge_nodes":node_count,
            "timestamp":datetime.utcnow().isoformat()
        }

        culture["civilization_culture"].append(entry)

    culture["last_update"] = datetime.utcnow().isoformat()

    save_json(CULTURE_FILE,culture)

    print("CIVILIZATION_CULTURE_UPDATED")
    print("culture_entries:",len(culture["civilization_culture"]))


if __name__ == "__main__":
    run()
