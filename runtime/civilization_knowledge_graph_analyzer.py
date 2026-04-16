import json
import os
from collections import defaultdict

GRAPH_FILE = "civilization_knowledge_graph.json"
ANALYSIS_FILE = "civilization_knowledge_analysis.json"

def load_graph():
    if not os.path.exists(GRAPH_FILE):
        return None
    with open(GRAPH_FILE,"r") as f:
        return json.load(f)

def analyze(graph):

    degree = defaultdict(int)

    for edge in graph.get("edges",[]):
        degree[edge["from"]] += 1
        degree[edge["to"]] += 1

    central = None
    best = -1

    for node in graph.get("nodes",[]):
        nid = node["id"]
        score = degree[nid]
        if score > best:
            best = score
            central = nid

    return {
        "most_connected_strategy":central,
        "connection_score":best,
        "total_nodes":len(graph.get("nodes",[])),
        "total_edges":len(graph.get("edges",[]))
    }

def run():

    graph = load_graph()

    if not graph:
        print("NO_GRAPH")
        return

    result = analyze(graph)

    with open(ANALYSIS_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("KNOWLEDGE_GRAPH_ANALYZED")
    print("central_strategy:",result["most_connected_strategy"])

if __name__ == "__main__":
    run()
