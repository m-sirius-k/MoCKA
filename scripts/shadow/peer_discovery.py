import json
import socket

FILE="runtime/network_topology.json"

def load():
    with open(FILE,"r",encoding="utf-8") as f:
        return json.load(f)

def save(d):
    with open(FILE,"w",encoding="utf-8") as f:
        json.dump(d,f,indent=2)

def main():

    topo=load()

    ip=socket.gethostbyname(socket.gethostname())

    node={
        "id":"node_"+ip.replace(".","_"),
        "address":ip,
        "port":9001
    }

    for n in topo["nodes"]:
        if n["address"]==ip:
            print("NODE EXISTS")
            return

    topo["nodes"].append(node)

    save(topo)

    print("NODE DISCOVERED",ip)

if __name__=="__main__":
    main()
