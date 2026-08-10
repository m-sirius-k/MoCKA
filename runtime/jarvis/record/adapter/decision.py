from datetime import datetime, timezone


class DecisionRecordAdapter:
    def create(self, decision_id, status):
        return {
            "decision_id": decision_id,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat()
        }