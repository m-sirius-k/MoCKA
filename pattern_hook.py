import sys
sys.path.insert(0, "C:/Users/sirok/MoCKA")

def run_pattern_score(text):
    try:
        import pattern_engine
        result = pattern_engine.score_text(text)
        print(f"[PATTERN] verdict={result['verdict']} success={result['success_score']} failure={result['failure_score']}")
        # スコアをevents的に記録
        score_path = "C:/Users/sirok/MoCKA/data/latest_score.json"
        import json, os
        with open(score_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return result
    except Exception as e:
        print(f"[PATTERN] score error: {e}")
        return None