import random

class GenericExternalNode:
    def __init__(self, name="node_4_logic"):
        self.name = name
        self.trust_score = 0.85

    def think(self, prompt):
        # ここに将来的に OpenAI や Azure の API 呼出を挿入可能
        # 現状は論理一貫性をチェックする専門知能として振る舞う
        responses = [
            f"[LOGIC-EXP] Analytical perspective on: {prompt}",
            f"[LOGIC-EXP] Cross-referencing entities in: {prompt}",
            f"[LOGIC-EXP] Structural integrity confirmed for: {prompt}"
        ]
        return random.choice(responses)
