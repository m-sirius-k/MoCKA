# relay/policy_engine.py
# Relay Phase2 — 判断ロジックを持たない軽量Policy層。
#
# 絶対条件:
#   - state読み取りのみ（書き込まない）
#   - governance/validateには一切触れない
#   - decision schema固定: {decision, confidence, reason}
# このクラスは「判断」ではなく、Relay stateへの意味付きタグ付けのみを行う。

class PolicyEngine:
    def __init__(self):
        self.version = "policy-v1"

    def evaluate(self, state: dict) -> dict:
        return self._decide(state)

    def _decide(self, state: dict) -> dict:
        last_type = state.get("last_type")
        last_source = state.get("last_source")
        event_count = state.get("event_count", 0)

        if event_count > 100:
            return {
                "decision": "defer",
                "confidence": 0.5,
                "reason": "high_volume",
            }

        if last_source == "github" or last_type == "github_event":
            return {
                "decision": "accept_telemetry",
                "confidence": 0.9,
                "reason": "source_github",
            }

        if last_source == "filesystem" or last_type == "filesystem_event":
            return {
                "decision": "accept_telemetry",
                "confidence": 0.8,
                "reason": "source_filesystem",
            }

        return {
            "decision": "accept_telemetry",
            "confidence": 0.6,
            "reason": "default",
        }
