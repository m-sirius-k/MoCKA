import json
import os
from collections import defaultdict

LEDGER_PATH = "runtime/ledger.json"
POLICY_PATH = "runtime/policy.json"

WINDOW = 20  # ★直近のみ使う

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path,"r",encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return default

def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def main():
    ledger = load_json(LEDGER_PATH,[])

    freq = defaultdict(float)

    recent = ledger[-WINDOW:]

    for ev in recent:
        if ev.get("type")=="DECISION":
            for a in ev.get("action",[]):
                freq[a]+=1

    total = sum(freq.values()) or 1.0

    # ★ 正規化（確率化）
    policy = {k: v/total for k,v in freq.items()}

    save_json(POLICY_PATH,policy)

    print("POLICY (NORMALIZED):", policy)

if __name__=="__main__":
    main()
