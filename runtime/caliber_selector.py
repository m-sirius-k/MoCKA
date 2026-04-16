def evaluate_providers(task):
    # 仮スコア（後で実データ接続）
    return {
        "Gemini": 3,
        "GPT": 4,
        "Claude": 5,
        "Perplexity": 2,
        "default": 1
    }

def select_best(scores):
    return max(scores, key=scores.get)
