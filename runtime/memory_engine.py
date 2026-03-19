import json, os

MEM_PATH = "memory/runtime/state.json"

def load_state():
    if not os.path.exists(MEM_PATH):
        return {}
    with open(MEM_PATH,"r",encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    os.makedirs("memory/runtime",exist_ok=True)
    with open(MEM_PATH,"w",encoding="utf-8") as f:
        json.dump(state,f,indent=2)

def update(event):
    s = load_state()
    s["last_event"] = event
    save_state(s)

if __name__ == "__main__":
    update("init")
