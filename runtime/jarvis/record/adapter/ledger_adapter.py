from runtime.jarvis.record.ledger import JarvisLedger


class LedgerAdapter:
    def __init__(self):
        self.ledger = JarvisLedger()

    def record(self, decision_id, status):
        return self.ledger.append(decision_id, status)