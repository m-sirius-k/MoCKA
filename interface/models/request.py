from dataclasses import dataclass
import time, uuid

@dataclass
class MoCKARequest:
    prompt: str
    metadata: dict = None

    def to_dict(self):
        return {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "prompt": self.prompt,
            "metadata": self.metadata or {}
        }
