# -*- coding: utf-8 -*-
import json
import random

HISTORY_PATH = "runtime/intent_history.json"

def load():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save(data):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    history = load()

    if not history:
        print("NO HISTORY")
        return

    last = history[-1]

    # 成功 / 失敗ランダム（後で実データに置換）
    outcome = random.choice(["success", "fail"])
    last["result"] = outcome

    if outcome == "success":
        if last.get("mutation"):
            last["score"] = last.get("score", 0) + 2
        else:
            last["score"] = last.get("score", 0) + 1
    else:
        last["score"] = last.get("score", 0) - 2

    save(history)

    print("RESULT:", outcome, "| UPDATED:", last)

if __name__ == "__main__":
    main()
