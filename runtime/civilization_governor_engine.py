import json
import os

ANALYTICS_FILE="mocka_civilization_analytics.json"
TREND_FILE="mocka_civilization_trend.json"
GOVERNOR_FILE="mocka_civilization_governor.json"

LOW_STABILITY = 0.3
HIGH_STABILITY = 0.7

def load(path):
    if not os.path.exists(path):
        return None
    with open(path,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def decide(analytics,trend):

    stability = analytics.get("civilization_stability",0)

    if stability < LOW_STABILITY:
        mode="exploration"

    elif stability > HIGH_STABILITY:
        mode="stable_operation"

    else:
        mode="balanced"

    return {
        "mode":mode,
        "stability":stability,
        "trend":trend.get("trend","unknown")
    }

def main():

    analytics=load(ANALYTICS_FILE)
    trend=load(TREND_FILE)

    if analytics is None or trend is None:
        print("NO_DATA")
        return

    decision=decide(analytics,trend)

    with open(GOVERNOR_FILE,"w",encoding="utf-8") as f:
        json.dump(decision,f,indent=2)

    print("CIVILIZATION_GOVERNOR_UPDATED")

if __name__=="__main__":
    main()
