import json
import os

class MoCKARouter:
    def __init__(self):
        self.members = ["Gemini", "ChatGPT", "Claude", "Copilot", "Perplexity"]

    def collaborate(self, problem, mode):
        debate_history = []
        current_answer = ""

        # 1. 提起 (第1走者: Gemini)
        current_answer = f"[Main: Gemini] {problem} に対する初案を作成しました。"
        debate_history.append(current_answer)

        # 2. 順次検証 (modeに応じてループ)
        # 実際にはここで各APIを呼び出すが、構造を定義
        for member in self.members[1:]:
            verification = f"[{member}] 前の回答を検証し、最適解を更新しました。"
            debate_history.append(verification)
            if mode == "1回ループ" and member == "Claude": break

        return {
            "final_answer": debate_history[-1],
            "process": "\n".join(debate_history)
        }
