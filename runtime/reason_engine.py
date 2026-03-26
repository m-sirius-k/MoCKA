import json
import time
import os

STATE_PATH = "state.json"
PLAN_PATH = "plan.json"
CAUSAL_PATH = "causal_graph.json"
LEDGER_PATH = "ledger.json"
OUTPUT_PATH = "reason_log.json"

def load_json(path):
    try:
        with open(path,"r",encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return {}

def save_json(path,data):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def compute_scores(state):
    scores={}
    for k,v in state.items():
        if v["count"]>0:
            scores[k]=v["score"]/v["count"]
        else:
            scores[k]=0
    return scores

def get_last_action(ledger):
    if not ledger:
        return None
    return ledger[-1].get("selected")

def causal_strength(causal, last, current):
    if not last:
        return 0
    key = last.lower()+"->"+current.lower()
    return causal.get("causal_edges",{}).get(key,{}).get("count",0)

def generate_reason(state, plan, causal, ledger):
    scores = compute_scores(state)
    best = plan["plan"][0]["action"]

    last = get_last_action(ledger)
    causal_val = causal_strength(causal, last, best)

    return {
        "selected": best,
        "reason": f"{best} chosen because score={scores[best]:.3f}, causal({last}->{best})={causal_val}"
    }

def main():
    print("=== REASON ENGINE (ADVANCED) ===")

    while True:
        state = load_json(STATE_PATH)
        plan = load_json(PLAN_PATH)
        causal = load_json(CAUSAL_PATH)
        ledger = load_json(LEDGER_PATH)

        if not state or not plan:
            time.sleep(5)
            continue

        reason = generate_reason(state, plan, causal, ledger)

        save_json(OUTPUT_PATH, reason)

        print("REASON:", reason)

        time.sleep(5)

if __name__=="__main__":
    main()
