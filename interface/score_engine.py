import json
import os

SCORE_PATH = "runtime/score.json"

def load_scores():
    if not os.path.exists(SCORE_PATH):
        return {}
    with open(SCORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_scores(scores):
    with open(SCORE_PATH, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

def update(provider, success):

    scores = load_scores()

    if provider not in scores:
        scores[provider] = {"success": 0, "fail": 0}

    if success:
        scores[provider]["success"] += 1
    else:
        scores[provider]["fail"] += 1

    save_scores(scores)

def get_score(provider):

    scores = load_scores()

    if provider not in scores:
        return 0

    s = scores[provider]["success"]
    f = scores[provider]["fail"]

    if s + f == 0:
        return 0

    return s / (s + f)
