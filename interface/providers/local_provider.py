from .base import BaseProvider
from interface.memory_engine import find_similar

class LocalProvider(BaseProvider):

    def name(self):
        return "local"

    def is_available(self):
        return True

    def _classify(self, prompt):
        p = prompt.lower()

        if "compare" in p:
            return "analysis"
        elif "error" in p or "fail" in p:
            return "recovery"
        elif "optimize" in p:
            return "optimization"
        else:
            return "general"

    def _generate_response(self, prompt, category):

        if category == "analysis":
            return f"[LOCAL-ANALYSIS] analyzing: {prompt}"

        if category == "recovery":
            return f"[LOCAL-RECOVERY] attempting recovery for: {prompt}"

        if category == "optimization":
            return f"[LOCAL-OPTIMIZE] optimizing: {prompt}"

        return f"[LOCAL-GENERAL] processing: {prompt}"

    def generate(self, request):
        prompt = request["prompt"]

        # --- memory参照 ---
        past = find_similar(prompt)
        if past:
            return {
                "provider": "local",
                "model": "rule-v2-memory",
                "status": "success",
                "memory_hit": True,
                "output": "[MEMORY RECALL] " + str(past["analysis"])
            }

        # --- 通常処理 ---
        category = self._classify(prompt)
        output = self._generate_response(prompt, category)

        return {
            "provider": "local",
            "model": "rule-v2-memory",
            "status": "success",
            "memory_hit": False,
            "category": category,
            "output": output
        }
