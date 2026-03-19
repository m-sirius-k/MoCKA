import json
import os
import time

PROGRESS_FILE = "civilization_progress.json"
REFLECTION_FILE = "civilization_reflection.json"
HISTORY_FILE = "civilization_progress_history.json"

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path,"r") as f:
        return json.load(f)

def save_history(progress):

    history = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE,"r") as f:
            history = json.load(f)

    history.append({
        "progress":progress,
        "timestamp":int(time.time())
    })

    with open(HISTORY_FILE,"w") as f:
        json.dump(history,f,indent=2)

    return history

def reflect(history):

    if len(history) < 2:
        return "insufficient_data"

    delta = history[-1]["progress"] - history[-2]["progress"]

    if delta > 0.02:
        return "rapid_evolution"
    elif delta > 0:
        return "steady_progress"
    else:
        return "stagnation"

def run():

    progress_data = load_json(PROGRESS_FILE)

    if not progress_data:
        print("NO_PROGRESS_DATA")
        return

    progress = progress_data.get("civilization_progress",0)

    history = save_history(progress)

    state = reflect(history)

    result = {
        "progress":progress,
        "reflection_state":state,
        "history_length":len(history)
    }

    with open(REFLECTION_FILE,"w") as f:
        json.dump(result,f,indent=2)

    print("CIVILIZATION_REFLECTION_UPDATED")
    print("state:",state)

if __name__ == "__main__":
    run()
