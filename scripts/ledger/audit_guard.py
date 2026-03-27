import json
import os
import hashlib

LEDGER_PATH = "runtime/ledger.json"

def safe_load():
    try:
        with open(LEDGER_PATH, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return None

def recover():
    with open(LEDGER_PATH, "r", encoding="utf-8-sig") as f:
        txt = f.read()

    items = []
    buf = ""
    depth = 0

    for c in txt:
        if c == "{":
            depth += 1
        if depth > 0:
            buf += c
        if c == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(buf)
                    items.append(obj)
                except:
                    pass
                buf = ""

    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

    print("RECOVERED:", len(items))

def verify_chain(ledger):
    prev = "GENESIS"

    for i, ev in enumerate(ledger):
        if ev.get("prev_hash") != prev:
            print("CHAIN BROKEN AT", i)
            return False

        tmp = dict(ev)
        h = tmp.pop("hash", None)
        calc = hashlib.sha256(json.dumps(tmp, sort_keys=True).encode()).hexdigest()

        if h != calc:
            print("HASH INVALID AT", i)
            return False

        prev = ev.get("hash")

    return True

def main():
    ledger = safe_load()

    if ledger is None:
        print("LEDGER CORRUPT → RECOVER")
        recover()
        return

    if not verify_chain(ledger):
        print("CHAIN INVALID → RECOVER")
        recover()
    else:
        print("AUDIT OK:", len(ledger))

if __name__ == "__main__":
    main()
