import socket
import json
import os

PORT = 8891
MODEL_FILE="repair_strategy_model.json"

def load_model():
    if not os.path.exists(MODEL_FILE):
        return {}
    with open(MODEL_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save_model(m):
    with open(MODEL_FILE,"w",encoding="utf-8") as f:
        json.dump(m,f,indent=2)

def merge(local,remote):

    for rid,data in remote.items():

        if rid not in local:
            local[rid]=data
            continue

        l=local[rid]
        l["attempts"]=max(l.get("attempts",0),data.get("attempts",0))
        l["success"]=max(l.get("success",0),data.get("success",0))
        l["fail"]=max(l.get("fail",0),data.get("fail",0))

    return local

def listen():

    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind(("",PORT))

    print("MOCKA_KNOWLEDGE_LISTENER_START")

    while True:

        data,addr = s.recvfrom(4096)

        try:
            msg = json.loads(data.decode())
        except:
            continue

        if msg.get("type")!="knowledge_sync":
            continue

        remote_model = msg.get("model")

        local_model = load_model()

        merged = merge(local_model,remote_model)

        save_model(merged)

        print("KNOWLEDGE_SYNC_APPLIED FROM",addr[0])

if __name__=="__main__":
    listen()
