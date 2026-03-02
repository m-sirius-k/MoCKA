from pathlib import Path
import json

BASE = Path(__file__).resolve().parent
REG_PATH = BASE / "KEY_REGISTRY_v4.jsonl"

class RegistryError(Exception):
    pass

def load_registry():
    if not REG_PATH.exists():
        raise RegistryError("KEY_REGISTRY_v4.jsonl not found")

    active_keys = {}
    revoked_keys = set()
    seen_key_ids = set()

    lines = REG_PATH.read_text(encoding="utf-8").strip().splitlines()

    for line in lines:
        obj = json.loads(line)

        event_type = obj.get("event_type")
        key_id = obj.get("key_id")

        if not key_id:
            raise RegistryError("Missing key_id")

        if event_type == "register":
            if key_id in seen_key_ids:
                raise RegistryError(f"Duplicate key_id: {key_id}")
            seen_key_ids.add(key_id)
            if obj.get("status") != "active":
                raise RegistryError(f"Register must set status=active: {key_id}")
            active_keys[key_id] = obj

        elif event_type == "revoke":
            if key_id not in active_keys:
                raise RegistryError(f"Revoke unknown key: {key_id}")
            revoked_keys.add(key_id)
            active_keys.pop(key_id, None)

        else:
            raise RegistryError(f"Unknown event_type: {event_type}")

    return active_keys, revoked_keys

def verify_registry():
    active, revoked = load_registry()
    print("OK: registry structure valid")
    print(f"Active keys: {len(active)}")
    print(f"Revoked keys: {len(revoked)}")

if __name__ == "__main__":
    verify_registry()