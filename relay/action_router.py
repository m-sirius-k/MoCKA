# relay/action_router.py
# Relay Phase3 — Policy decisionを実行可能なactionへ変換する層。
#
# 注意: 本番のGovernance layer(execution_order_engine等)・governance write
# (process_event/validate())とは無関係。本クラスはgovernanceに一切接続せず、
# decision文字列をaction文字列に機械的に写像するだけの単一責務層である。
#
# 絶対条件:
#   - stateを変更しない（読み取りも不要、policyのdecisionのみを見る）
#   - governance/validateを呼ばない
#   - action schema固定: {action, status}（forwardフィールドは廃止）

class ActionRouter:
    def __init__(self):
        self.version = "action-router-v1"

    def route(self, state: dict, policy: dict) -> dict:
        decision = policy.get("decision")

        if decision == "accept_telemetry":
            return self._accept()

        if decision == "reject":
            return self._reject()

        if decision == "defer":
            return self._defer()

        return self._unknown()

    def _accept(self) -> dict:
        return {"action": "STORE_EVENT", "status": "approved"}

    def _reject(self) -> dict:
        return {"action": "DROP_EVENT", "status": "blocked"}

    def _defer(self) -> dict:
        return {"action": "QUEUE_EVENT", "status": "delayed"}

    def _unknown(self) -> dict:
        return {"action": "DROP_EVENT", "status": "error_fallback"}
