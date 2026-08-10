from dataclasses import dataclass, asdict
import datetime


@dataclass
class DecisionRecord:
    decision_id: str
    status: str
    actor: str = "HUMAN_GATE"

    def to_dict(self):
        return {
            **asdict(self),
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }