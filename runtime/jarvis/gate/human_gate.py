class HumanGate:
    def __init__(self):
        self.status = "WAITING"

    def request(self, decision_id):
        return {
            "decision_id": decision_id,
            "status": self.status,
            "authority": "human"
        }

    def approve(self, decision_id):
        self.status = "APPROVED"
        return {
            "decision_id": decision_id,
            "status": self.status
        }

    def reject(self, decision_id):
        self.status = "REJECTED"
        return {
            "decision_id": decision_id,
            "status": self.status
        }