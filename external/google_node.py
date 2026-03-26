class GoogleNode:
    def __init__(self):
        self.name = "google_genai"
        self.trust_score = 0.95

    def think(self, prompt):
        # 本来は Gemini API を叩く場所
        return f"[GOOGLE] '{prompt}' に対する創造的な回答を生成しました。"
