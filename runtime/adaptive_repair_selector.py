import json
import os

MODEL_FILE="repair_strategy_model.json"
PROPOSAL_FILE="repair_proposals.json"
SELECT_FILE="adaptive_repair_selection.json"

def load_json(path):

    if not os.path.exists(path):
        return None

    with open(path,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def compute_score(model):

    scores={}

    for rid,data in model.items():

        attempts=data.get("attempts",0)
        success=data.get("success",0)

        if attempts==0:
            score=0
        else:
            score=success/attempts

        scores[rid]=score

    return scores

def select_best(scores):

    if not scores:
        return None

    best=max(scores,key=scores.get)

    return {
        "repair_id":best,
        "score":scores[best]
    }

def save_selection(sel):

    with open(SELECT_FILE,"w",encoding="utf-8") as f:
        json.dump(sel,f,indent=2)

def main():

    model=load_json(MODEL_FILE)

    if not model:
        print("NO_MODEL")
        return

    scores=compute_score(model)

    sel=select_best(scores)

    save_selection(sel)

    print("ADAPTIVE_REPAIR_SELECTED")

if __name__=="__main__":
    main()
