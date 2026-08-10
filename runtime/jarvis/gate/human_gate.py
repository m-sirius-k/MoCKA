from runtime.jarvis.record.adapter.ledger_adapter import LedgerAdapter


class HumanGate:
    def __init__(self):
        self.status = "WAITING"
        self.ledger = LedgerAdapter()

    def request(self, decision_id):
        return {
            "decision_id": decision_id,
            "status": self.status,
            "authority": "human"
        }

    def approve(self, decision_id):
        self.status = "APPROVED"
        return self.ledger.record(
            decision_id,
            self.status
        )

    def reject(self, decision_id):
        self.status = "REJECTED"
        return self.ledger.record(
            decision_id,
            self.status
        )