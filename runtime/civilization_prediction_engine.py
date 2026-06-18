import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import json
import os

HISTORY_FILE = "civilization_history_archive.json"
PREDICTION_FILE = "civilization_prediction.json"

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE,"r") as f:
        return json.load(f)

def predict(history):

    if len(history) < 2:
        return {
            "prediction":"insufficient_data"
        }

    last = history[-1]["progress"]
    prev = history[-2]["progress"]

    delta = last - prev

    if delta > 0.02:
        state = "accelerating"

    elif delta > 0:
        state = "steady_growth"

    elif delta == 0:
        state = "stagnation"

    else:
        state = "decline"

    return {
        "progress_delta":delta,
        "prediction":state
    }

def run():

    history = load_history()

    result = predict(history)

    with open(PREDICTION_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("CIVILIZATION_PREDICTION_UPDATED")
    print("prediction:",result["prediction"])

if __name__ == "__main__":
    run()
