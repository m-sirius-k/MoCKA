import json
import os

BASE = r"C:\Users\sirok\MoCKA"
CLOCK_FILE = os.path.join(BASE,"runtime","lamport_clock.json")

def load_clock():
    if not os.path.exists(CLOCK_FILE):
        return {"clock":0}
    with open(CLOCK_FILE,"r",encoding="utf-8") as f:
        return json.load(f)

def save_clock(data):
    with open(CLOCK_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def tick():
    c = load_clock()
    c["clock"] += 1
    save_clock(c)
    return c["clock"]

if __name__ == "__main__":
    print(tick())
