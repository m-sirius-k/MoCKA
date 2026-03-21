import json

FILE="runtime/network_topology.json"

data={
    "nodes":[
        {
            "id":"node_local",
            "address":"127.0.0.1",
            "port":9001
        }
    ]
}

with open(FILE,"w",encoding="utf-8") as f:
    json.dump(data,f,indent=2)

print("TOPOLOGY CREATED")
