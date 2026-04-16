import json
import os

STATE_PATH = "state.json"
GRAPH_PATH = "causal_graph.json"

def update_causal_graph():
    if not os.path.exists(STATE_PATH):
        return

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)

    history = state.get("history", [])

    graph = {
        "nodes": [],
        "edges": []
    }

    for i, item in enumerate(history):
        action = item.get("action")
        node_id = f"N{i}"

        graph["nodes"].append({
            "id": node_id,
            "action": action
        })

        if i > 0:
            graph["edges"].append({
                "from": f"N{i-1}",
                "to": node_id
            })

    with open(GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    print("CAUSAL GRAPH UPDATED")
