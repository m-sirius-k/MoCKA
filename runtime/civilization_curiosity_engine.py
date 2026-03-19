import json
import os
from collections import defaultdict

GRAPH_FILE = "civilization_knowledge_graph.json"
CURIOSITY_FILE = "civilization_curiosity_target.json"

def load_graph():

    if not os.path.exists(GRAPH_FILE):
        return None

    with open(GRAPH_FILE,"r") as f:
        return json.load(f)

def run():

    graph = load_graph()

    if not graph:
        print("NO_GRAPH")
        return

    degree = defaultdict(int)

    for edge in graph.get("edges",[]):
        degree[edge["from"]] += 1
        degree[edge["to"]] += 1

    least_connected = None
    lowest = 999

    for node in graph.get("nodes",[]):

        nid = node["id"]
        score = degree[nid]

        if score < lowest:
            lowest = score
            least_connected = nid

    result = {
        "curiosity_strategy":least_connected,
        "connection_score":lowest
    }

    with open(CURIOSITY_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("CURIOSITY_TARGET_SELECTED")
    print("strategy:",least_connected)

if __name__ == "__main__":
    run()
