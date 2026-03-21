import json
import time

FILE="runtime/node_map.json"

def load():
    try:
        with open(FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"nodes":[]}

def save(d):
    with open(FILE,"w",encoding="utf-8") as f:
        json.dump(d,f,indent=2)

def add_node(node):

    d=load()

    for n in d["nodes"]:
        if n["id"]==node:
            print("NODE EXISTS")
            return

    d["nodes"].append({
        "id":node,
        "joined":int(time.time()),
        "status":"alive"
    })

    save(d)

    print("NODE ADDED",node)

if __name__=="__main__":

    add_node("node_local")
