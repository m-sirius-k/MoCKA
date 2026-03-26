import json, hashlib, os

PATH = "runtime/ledger.json"

def load():
    if not os.path.exists(PATH):
        return []
    with open(PATH,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save(d):
    with open(PATH,"w",encoding="utf-8") as f:
        json.dump(d,f,indent=2)

def h(ev):
    data = {
        "type": ev.get("type"),
        "action": ev.get("action"),
        "ts": ev.get("ts")
    }
    s = json.dumps(data, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    ledger = load()

    if not ledger:
        print("EMPTY")
        return

    new = []

    for i, ev in enumerate(ledger):
        ev_new = {
            "type": ev.get("type"),
            "action": ev.get("action"),
            "ts": ev.get("ts")
        }

        if i == 0:
            ev_new["prev_hash"] = None
        else:
            ev_new["prev_hash"] = h(new[-1])

        new.append(ev_new)

    save(new)

    print("CHAIN REBUILT:", len(new))

if __name__=="__main__":
    main()
