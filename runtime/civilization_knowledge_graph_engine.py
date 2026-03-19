import json
import os

MODEL_FILE = "repair_strategy_model.json"
LAB_FILE = "civilization_research_lab_log.json"
GRAPH_FILE = "civilization_knowledge_graph.json"

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path,"r") as f:
        return json.load(f)

def run():

    model = load_json(MODEL_FILE)
    lab = load_json(LAB_FILE)

    nodes = []
    edges = []

    if model:
        for rid,data in model.items():

            nodes.append({
                "id":rid,
                "type":"strategy",
                "attempts":data.get("attempts",0),
                "success":data.get("success",0)
            })

            parent = data.get("parent")
            if parent:
                edges.append({
                    "from":parent,
                    "to":rid,
                    "relation":"mutation"
                })

    if lab:
        for entry in lab:

            edges.append({
                "from":entry["base_strategy"],
                "to":"lab",
                "relation":"experiment",
                "success":entry["success"]
            })

    graph = {
        "nodes":nodes,
        "edges":edges
    }

    with open(GRAPH_FILE,"w") as f:
        json.dump(graph,f,indent=2)

    print("KNOWLEDGE_GRAPH_UPDATED")
    print("nodes:",len(nodes))
    print("edges:",len(edges))

if __name__ == "__main__":
    run()
