import json
import os

ANALYTICS_FILE="mocka_civilization_analytics.json"
HISTORY_FILE="mocka_civilization_history.json"
TREND_FILE="mocka_civilization_trend.json"

def load(path):
    if not os.path.exists(path):
        return None
    with open(path,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def compute_trend(history,current):

    if not history:
        return {"trend":"unknown"}

    last = history[-1]

    last_model = last.get("model",{})

    last_attempts=0
    last_success=0

    for r in last_model.values():
        last_attempts+=r.get("attempts",0)
        last_success+=r.get("success",0)

    if last_attempts==0:
        last_rate=0
    else:
        last_rate=last_success/last_attempts

    current_rate=current.get("civilization_stability",0)

    if current_rate > last_rate:
        return {"trend":"improving"}
    elif current_rate < last_rate:
        return {"trend":"degrading"}
    else:
        return {"trend":"stable"}

def main():

    analytics=load(ANALYTICS_FILE)
    history=load(HISTORY_FILE)

    if analytics is None:
        print("NO_ANALYTICS")
        return

    trend=compute_trend(history,analytics)

    with open(TREND_FILE,"w",encoding="utf-8") as f:
        json.dump(trend,f,indent=2)

    print("CIVILIZATION_TREND_UPDATED")

if __name__=="__main__":
    main()
