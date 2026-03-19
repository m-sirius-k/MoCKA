import json
import os

MODEL_FILE="repair_strategy_model.json"
ANALYTICS_FILE="mocka_civilization_analytics.json"

def load_model():
    if not os.path.exists(MODEL_FILE):
        return {}
    with open(MODEL_FILE,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def compute(model):

    total_attempts=0
    total_success=0
    total_fail=0

    for rid,data in model.items():

        attempts=data.get("attempts",0)
        success=data.get("success",0)
        fail=data.get("fail",0)

        total_attempts+=attempts
        total_success+=success
        total_fail+=fail

    if total_attempts==0:
        stability=0
    else:
        stability=total_success/total_attempts

    analytics={
        "total_repairs":len(model),
        "attempts":total_attempts,
        "success":total_success,
        "fail":total_fail,
        "civilization_stability":stability
    }

    return analytics

def save(data):

    with open(ANALYTICS_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

def main():

    model=load_model()

    analytics=compute(model)

    save(analytics)

    print("CIVILIZATION_ANALYTICS_UPDATED")

if __name__=="__main__":
    main()
