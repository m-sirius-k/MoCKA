import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from providers.google_provider import GoogleProvider
from providers.azure_provider import AzureProvider

class MoCKARouter:
    def __init__(self):
        self.providers = {
            "Gemini": GoogleProvider(),
            "Azure":  AzureProvider(),
        }
        self.members = ["Gemini", "ChatGPT", "Claude", "Copilot", "Perplexity"]

    def _call(self, provider_name, prompt):
        provider = self.providers.get(provider_name)
        if provider and provider.is_available():
            try:
                result = provider.generate({"prompt": prompt})
                return result["output"]
            except Exception as e:
                return f"[{provider_name}] ERROR: {e}"
        return f"[{provider_name}] unavailable"

    def collaborate(self, problem, mode="full"):
        debate_history = []

        # 1. 初案（Gemini）
        print("[1/3] Gemini: 初案作成中...")
        current_answer = self._call("Gemini", problem)
        debate_history.append({"role": "Gemini", "content": current_answer})

        # 2. 差分検証（Claude視点でdiffのみ）
        diff_prompt = f"""以下の問いと初案を読み、問題点・改善点のみを簡潔に指摘してください。

問い: {problem}
初案: {current_answer}

修正提案のみを返してください。"""

        print("[2/3] Claude: 差分検証中...")
        diff = self._call("Gemini", diff_prompt)
        debate_history.append({"role": "Claude(diff)", "content": diff})

        # 3. 統合（最終回答）
        final_prompt = f"""以下の初案と修正提案を統合し、最終回答を作成してください。

初案: {current_answer}
修正提案: {diff}"""

        print("[3/3] 統合中...")
        final = self._call("Gemini", final_prompt)
        debate_history.append({"role": "Conductor", "content": final})

        return {
            "final_answer": final,
            "process": debate_history
        }

if __name__ == "__main__":
    router = MoCKARouter()
    result = router.collaborate("MoCKAシステムの最大の課題は何か？")
    print("\n=== 最終回答 ===")
    print(result["final_answer"])
    print("\n=== 議事録 ===")
    for d in result["process"]:
        print(f"[{d['role']}] {d['content'][:100]}...")
