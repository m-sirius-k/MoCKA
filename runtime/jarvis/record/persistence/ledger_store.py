import json
from pathlib import Path


class LedgerStore:
    def __init__(self, path="data/jarvis_ledger.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, record):
        existing = self.load_all()

        if any(
            item.get("decision_id") == record.get("decision_id")
            for item in existing
        ):
            return record

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return record

    def load_all(self):
        if not self.path.exists():
            return []

        with self.path.open("r", encoding="utf-8") as f:
            return [
                json.loads(line)
                for line in f
                if line.strip()
            ]