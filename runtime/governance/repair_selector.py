def generate_repair_candidates(countermeasure):
    return [
        {"plan": countermeasure, "type": "direct"},
        {"plan": "ログ強化：" + countermeasure, "type": "log_enhanced"},
        {"plan": "事前防止：" + countermeasure, "type": "preventive"}
    ]

def score_candidate(candidate):
    plan = candidate["plan"]

    score = 0

    if "防止" in plan:
        score += 3
    if "ログ" in plan:
        score += 2
    if "直接" in plan or candidate["type"] == "direct":
        score += 1

    return score

def select_best(candidates):
    scored = [(c, score_candidate(c)) for c in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]
