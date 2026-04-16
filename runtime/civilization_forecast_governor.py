import json
import os

PRED_FILE = "civilization_prediction.json"
GOV_FILE = "mocka_civilization_governor.json"

def load_prediction():

    if not os.path.exists(PRED_FILE):
        return None

    with open(PRED_FILE,"r") as f:
        return json.load(f)

def determine_mode(pred):

    state = pred.get("prediction","unknown")

    if state == "accelerating":
        return "stable_operation"

    if state == "steady_growth":
        return "balanced_evolution"

    if state == "stagnation":
        return "exploration"

    if state == "decline":
        return "diagnostic_mode"

    return "exploration"

def run():

    pred = load_prediction()

    if not pred:
        print("NO_PREDICTION_DATA")
        return

    mode = determine_mode(pred)

    governor = {
        "mode":mode,
        "prediction":pred.get("prediction","unknown")
    }

    with open(GOV_FILE,"w") as f:
        json.dump(governor,f,indent=2)

    print("FORECAST_GOVERNOR_UPDATED")
    print("mode:",mode)

if __name__ == "__main__":
    run()
