import time
import uuid


def create_event(source: str, payload: dict) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "source": source,
        "type": "external_signal",
        "payload": payload,
        "timestamp": int(time.time()),
        "immutable": True
    }
