import json
import time
import os

LEDGER_PATH = "ledger.json"
GRAPH_PATH = "knowledge_graph.json"

def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def normalize(text):
    return str(text).lower().strip()

def extract_words(text):
    return text.split()

def main():
    print("=== KNOWLEDGE GRAPH BUILDER START ===")

    while True:
        if not os.path.exists(LEDGER_PATH):
            time.sleep(5)
            continue

        ledger = load_json(LEDGER_PATH)

        if not os.path.exists(GRAPH_PATH):
            graph = {"nodes": {}, "edges": {}}
        else:
            graph = load_json(GRAPH_PATH)

        updated = False

        for entry in ledger:
            if entry.get("event_type") != "external_input":
                continue

            text = normalize(entry.get("message",""))
            words = extract_words(text)

            # ノード追加
            for w in words:
                if w not in graph["nodes"]:
                    graph["nodes"][w] = {"count": 0}

                graph["nodes"][w]["count"] += 1

            # 共起（エッジ）
            for i in range(len(words)):
                for j in range(i+1, len(words)):
                    pair = words[i] + "|" + words[j]

                    if pair not in graph["edges"]:
                        graph["edges"][pair] = {"weight": 0}

                    graph["edges"][pair]["weight"] += 1

            updated = True

        if updated:
            save_json(GRAPH_PATH, graph)
            print("GRAPH UPDATED:",
                  len(graph["nodes"]),
                  "nodes /",
                  len(graph["edges"]),
                  "edges")

        time.sleep(5)

if __name__ == "__main__":
    main()
