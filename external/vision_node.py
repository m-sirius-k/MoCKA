class VisionContextNode:
    def __init__(self):
        self.name = "node_4_vision"
        self.trust_score = 0.88

    def think(self, prompt, context=None):
        # 拡張子が画像やPDFなどの場合、特別な解析フラグを立てるシミュレーション
        if any(ext in prompt.lower() for ext in [".jpg", ".png", ".pdf", ".exe"]):
            return f"[FILE-ANALYSIS] Deep scanning required for: {prompt}"
        
        return f"[CONTEXT-OK] No external file reference detected."
