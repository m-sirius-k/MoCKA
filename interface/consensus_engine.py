from interface.score_engine import get_score, update

def decide(results, analysis):

    valid = [r for r in results if r.get("status") == "success"]

    # スコア評価
    if valid:
        best = None
        best_score = -1

        for r in valid:
            score = get_score(r["provider"])
            if score > best_score:
                best_score = score
                best = r

        update(best["provider"], True)

        return {
            "decision": best,
            "reason": "score_based"
        }

    # 全失敗
    for r in results:
        update(r.get("provider"), False)

    fallback = next((r for r in results if r.get("provider") == "local"), None)

    return {
        "decision": fallback,
        "reason": "all_failed_fallback"
    }
