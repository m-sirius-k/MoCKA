import datetime


class JarvisLedger:
    def __init__(self):
        self.records = []

    def append(self, decision_id, status):
        record = {
            "decision_id": decision_id,
            "status": status,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }
        self.records.append(record)
        return record