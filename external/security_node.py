class SecurityNode:
    def __init__(self):
        self.name = "security_expert"
        self.trust_score = 1.0

    def think(self, prompt):
        danger_keywords = ["delete", "rm -rf", "株価", "投資", "殺す"]
        if any(word in prompt.lower() for word in danger_keywords):
            return f"[DANGER] セキュリティポリシーにより、問い '{prompt}' は制限されました。"
        return "[LOGIC-CHECK] Validated request. No immediate threats found."
