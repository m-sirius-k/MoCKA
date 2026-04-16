import json
import os

MODEL_FILE="repair_strategy_model.json"
NEW_REPAIR_FILE="generated_repair_proposals.json"

def load_model():
    if not os.path.exists(MODEL_FILE):
        return {}
    with open(MODEL_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def generate_repairs(model):

    proposals=[]

    for rid,data in model.items():

        attempts=data.get("attempts",0)
        success=data.get("success",0)

        if attempts>0 and success==0:

            proposals.append({
                "base_repair":rid,
                "new_repair":"R004",
                "proposal":"disable_test_exception_in_civilization_loop"
            })

    if not proposals:
        proposals.append({
            "base_repair":"none",
            "new_repair":"R004",
            "proposal":"disable_test_exception_in_civilization_loop"
        })

    return proposals

def save(p):

    with open(NEW_REPAIR_FILE,"w",encoding="utf-8") as f:
        json.dump(p,f,indent=2)

def main():

    model=load_model()

    proposals=generate_repairs(model)

    save(proposals)

    print("NEW_REPAIR_STRATEGY_GENERATED")

if __name__=="__main__":
    main()
