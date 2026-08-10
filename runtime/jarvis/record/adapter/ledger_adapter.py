from runtime.jarvis.record.schema.decision_record import DecisionRecord
from runtime.jarvis.record.persistence.ledger_store import LedgerStore


class LedgerAdapter:
    def __init__(self):
        self.store = LedgerStore()

    def record(self, decision_id, status):
        record = DecisionRecord(
            decision_id,
            status
        ).to_dict()

        return self.store.save(record)