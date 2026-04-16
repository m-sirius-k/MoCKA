import json
from collections import defaultdict

INPUT_PATH = "runtime/intent_history.json"
OUTPUT_PATH = "runtime/analysis/intent_graph.json"

def load_data():
    try:
        with open(INPUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def build_graph(data):
    edges = defaultdict(lambda: {"next": defaultdict(int)})

    for i in range(len(data)-1):
        current = data[i].get("goal", "unknown")
        nxt = data[i+1].get("goal", "unknown")

        edges[current]["next"][nxt] += 1

    return edges

def normalize(edges):
    result = {}

    for k, v in edges.items():
        total = sum(v["next"].values())
        result[k] = {}

        for nxt, count in v["next"].items():
            result[k][nxt] = round(count / total, 3)

    return result

def main():
    data = load_data()
    graph = build_graph(data)
    result = normalize(graph)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("INTENT GRAPH BUILT")

if __name__ == "__main__":
    main()
