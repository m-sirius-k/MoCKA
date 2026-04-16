import json
from datetime import datetime

INPUT_PATH = "runtime/input/human_feedback.json"
OUTPUT_PATH = "runtime/state/human_evaluation.json"

def load_feedback():
    try:
        with open(INPUT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def build_evaluation(feedback):
    if not feedback:
        return None

    evaluation = {
        "action": feedback.get("action"),
        "score": feedback.get("score", 0),
        "feedback": feedback.get("feedback", "neutral"),
        "success": feedback.get("success", False),
        "context": feedback.get("context", "default"),
        "source": feedback.get("source", "human"),
        "timestamp": datetime.utcnow().isoformat()
    }
    return evaluation

def save_evaluation(evaluation):
    if not evaluation:
        return
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2)

if __name__ == "__main__":
    fb = load_feedback()
    ev = build_evaluation(fb)
    save_evaluation(ev)
    print("HUMAN EVAL WITH CONTEXT SAVED")
