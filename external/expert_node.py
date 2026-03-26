class SecurityExpertNode:
    def __init__(self):
        self.name = "node_3_security"
        self.trust_score = 0.95  # セキュリティに関しては最高権威

    def think(self, prompt, context):
        # 簡易的な論理・セキュリティ・フィルタリング・シミュレーション
        trigger_words = ["password", "eval", "exec", "system", "delete"]
        if any(word in prompt.lower() for word in trigger_words):
            return f"[SECURITY-ALERT] Potentially unsafe operation detected in: {prompt}"
        
        return f"[LOGIC-CHECK] Validated request. No immediate threats found in: {prompt}"
