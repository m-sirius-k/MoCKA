from runtime.jarvis.record.ledger import JarvisLedger
from runtime.jarvis.record.persistence.ledger_store import LedgerStore


class LedgerAdapter:
    def __init__(self):
        self.ledger = JarvisLedger()
        self.store = LedgerStore()

    def record(self, decision_id, status):
        record = self.ledger.append(
            decision_id,
            status
        )
        return self.store.save(record)