import socket
import json
import os

PORT = 8891
MODEL_FILE="repair_strategy_model.json"

def load_model():
    if not os.path.exists(MODEL_FILE):
        return None
    with open(MODEL_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def broadcast_model():

    model = load_model()

    if model is None:
        print("NO_MODEL_TO_BROADCAST")
        return

    msg = {
        "type":"knowledge_sync",
        "model":model
    }

    data = json.dumps(msg).encode()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    s.sendto(data,("<broadcast>",PORT))

    print("KNOWLEDGE_BROADCAST_SENT")

if __name__=="__main__":
    broadcast_model()
