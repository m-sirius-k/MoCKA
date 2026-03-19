import json
import os
import time

PROGRESS_FILE = "civilization_progress.json"
GOAL_FILE = "civilization_goal_state.json"
REFLECTION_FILE = "civilization_reflection.json"

ARCHIVE_FILE = "civilization_history_archive.json"

def load_json(path):

    if not os.path.exists(path):
        return None

    with open(path,"r") as f:
        return json.load(f)

def load_archive():

    if not os.path.exists(ARCHIVE_FILE):
        return []

    with open(ARCHIVE_FILE,"r") as f:
        return json.load(f)

def run():

    progress = load_json(PROGRESS_FILE)
    goal = load_json(GOAL_FILE)
    reflection = load_json(REFLECTION_FILE)

    archive = load_archive()

    record = {

        "timestamp":int(time.time()),
        "progress":progress.get("civilization_progress",0) if progress else 0,
        "goal":goal.get("goal","unknown") if goal else "unknown",
        "reflection":reflection.get("reflection_state","unknown") if reflection else "unknown"
    }

    archive.append(record)

    with open(ARCHIVE_FILE,"w") as f:
        json.dump(archive,f,indent=2)

    print("CIVILIZATION_HISTORY_ARCHIVED")
    print("records:",len(archive))

if __name__ == "__main__":
    run()
