import json
import os

NODE_PATH = "runtime/nodes.json"

def load_nodes():
    if not os.path.exists(NODE_PATH):
        return []
    with open(NODE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_nodes(nodes):
    with open(NODE_PATH, "w", encoding="utf-8") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)

def register(node_name):

    nodes = load_nodes()

    if node_name not in nodes:
        nodes.append(node_name)
        save_nodes(nodes)

    return nodes
