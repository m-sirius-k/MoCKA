import json
import os
from collections import defaultdict

KB_FILE="incident_knowledge_base.json"
MODEL_FILE="repair_strategy_model.json"

def load_kb():

    if not os.path.exists(KB_FILE):
        print("NO_KB")
        return []

    with open(KB_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def build_model(records):

    model=defaultdict(lambda:{
        "attempts":0,
        "success":0,
        "fail":0
    })

    for r in records:

        repair=r.get("repair",{})
        verify=r.get("verification",{})

        rid=repair.get("repair_id","UNKNOWN")

        model[rid]["attempts"]+=1

        if verify.get("verification")=="runtime_ok":
            model[rid]["success"]+=1
        else:
            model[rid]["fail"]+=1

    return model

def save_model(model):

    with open(MODEL_FILE,"w",encoding="utf-8") as f:
        json.dump(model,f,indent=2)

def main():

    kb=load_kb()

    model=build_model(kb)

    save_model(model)

    print("LEARNING_MODEL_UPDATED")

if __name__=="__main__":
    main()
