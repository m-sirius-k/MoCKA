# FILE: runtime\intent_evaluator.py

import json
import os
import csv

MEM_PATH = os.path.join("runtime", "intent_memory.json")
CSV_PATH = os.path.join("runtime", "index", "event_timeline.csv")
RESULT_PATH = os.path.join("runtime", "execution_result.json")

def load_mem():
    with open(MEM_PATH, encoding="utf-8-sig") as f:
        return json.load(f)

def save_mem(mem):
    with open(MEM_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

def load_state():
    incidents = 0
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["type"] == "incident" and r["status"] == "active":
                incidents += 1
    return incidents

def load_result():
    try:
        with open(RESULT_PATH, encoding="utf-8-sig") as f:
            return json.load(f).get("last_result")
    except:
        return None

def evaluate():

    mem = load_mem()
    history = mem.get("history", [])
    incidents = load_state()
    result = load_result()

    if not history:
        return

    last = history[-1]

    score = 0

    # --- 状態評価 ---
    if incidents > 0:
        if last["goal"] == "prevent_incident":
            score += 3
        else:
            score -= 2
    else:
        if last["goal"] == "optimize_execution":
            score += 2

    # --- 実行結果評価（ここが最重要） ---
    if result is True:
        score += 2
    elif result is False:
        score -= 2

    last["score"] = score

    save_mem(mem)

    print("EVALUATED:", last)

if __name__ == "__main__":
    evaluate()
