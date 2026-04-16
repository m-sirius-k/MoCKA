import json, os
from datetime import datetime

WEIGHTS = {
    "accuracy": 0.30,
    "reproducibility": 0.25,
    "nonvalue_match": 0.20,
    "confidence_consistency": 0.15,
    "history_alignment": 0.10
}

SCORES_DIR = r"C:\Users\sirok\planningcaliber\data\scores"
LOGS_DIR   = r"C:\Users\sirok\planningcaliber\data\logs"

def evaluate(task_log: dict) -> dict:
    c = task_log
    components = {
        "accuracy":               1.0 if c.get("executed_correctly") else 0.0,
        "reproducibility":        float(c.get("reproducibility", 0.8)),
        "nonvalue_match":         1.0 if not c.get("nonvalue_flag") else 0.5,
        "confidence_consistency": float(c.get("confidence_consistency", 0.8)),
        "history_alignment":      float(c.get("history_alignment", 0.9))
    }
    score = sum(components[k] * WEIGHTS[k] for k in WEIGHTS)
    result = {
        "task": c.get("task", "unknown"),
        "ai_member": c.get("ai_member", "unknown"),
        "evaluated_at": datetime.now().isoformat(),
        "TRUST_SCORE": round(score, 4),
        "components": {k: round(v, 4) for k, v in components.items()},
        "verdict": "TRUSTED" if score >= 0.75 else "SUSPICIOUS" if score >= 0.5 else "UNTRUSTED"
    }
    _save(result)
    return result

def _save(result: dict):
    os.makedirs(SCORES_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"trust_{result['ai_member']}_{ts}.json"
    with open(os.path.join(SCORES_DIR, fname), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[trust_score_caliber] 保存: {fname}")

def evaluate_from_file(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        task_log = json.load(f)
    return evaluate(task_log)

if __name__ == "__main__":
    test_log = {
        "task": "lever_verification",
        "ai_member": "Claude",
        "executed_correctly": True,
        "reproducibility": 1.0,
        "nonvalue_flag": False,
        "confidence_consistency": 1.0,
        "history_alignment": 1.0
    }
    result = evaluate(test_log)
    print(json.dumps(result, ensure_ascii=False, indent=2))
