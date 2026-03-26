import json
import time
import os

STATE_PATH = "state.json"
GOAL_PATH = "goal.json"

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

def select_goal(scores):
    # 最高スコアを目標にする
    return max(scores, key=scores.get)

def main():
    print("=== GOAL ENGINE (AUTO MODE) ===")

    while True:
        state = load_json(STATE_PATH)

        if not state:
            time.sleep(5)
            continue

        scores = compute_scores(state)
        best = select_goal(scores)

        goal = {
            "target": f"maximize_{best}",
            "scores": scores
        }

        save_json(GOAL_PATH, goal)

        print("GOAL UPDATED:", goal)

        time.sleep(10)

if __name__=="__main__":
    main()
