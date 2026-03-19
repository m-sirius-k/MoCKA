import socket
import json
import os

PORT = 8890
REGISTRY = "mocka_civilization_registry.json"

def load_registry():
    if not os.path.exists(REGISTRY):
        return []
    with open(REGISTRY,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save_registry(data):
    with open(REGISTRY,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def upsert(node):

    registry = load_registry()

    node_id = node.get("node")

    updated = False

    for i,r in enumerate(registry):

        if r.get("node")==node_id:
            registry[i]=node
            updated=True

    if not updated:
        registry.append(node)

    save_registry(registry)

def listen():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", PORT))

    print("MOCKA_AUTO_REGISTRY_START")

    while True:

        data, addr = s.recvfrom(4096)

        try:
            msg = json.loads(data.decode())
        except:
            continue

        node={
            "node": msg.get("node"),
            "address": addr[0],
            "service": msg.get("service")
        }

        upsert(node)

        print("NODE_REGISTERED:", node)

if __name__=="__main__":
    listen()
