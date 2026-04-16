import glob
import hashlib
import json
import os
import time
from typing import Optional


ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _pick_latest(pattern: str) -> Optional[str]:
    hits = glob.glob(pattern)
    if not hits:
        return None
    hits.sort(key=lambda p: os.path.getmtime(p))
    return hits[-1]


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)


def _atomic_replace_latest(latest_path: str, new_path: str) -> None:
    try:
        if os.path.exists(latest_path):
            os.remove(latest_path)
    except OSError:
        pass
    os.replace(new_path, latest_path)


def main() -> int:
    audit_dir = os.path.join(PROJECT_ROOT, "audit")
    events_dir = os.path.join(audit_dir, "events")
    _ensure_dir(events_dir)

    outbox_dir = os.path.join(PROJECT_ROOT, "outbox")
    latest_outbox = _pick_latest(os.path.join(outbox_dir, "*.json"))

    ts_unix = int(time.time())
    ts_id = time.strftime("%Y%m%d_%H%M%S", time.localtime(ts_unix))

    payload = {
        "schema": "mocka.audit_event.v1",
        "ts_unix": ts_unix,
        "ts_id": ts_id,
        "project_root": PROJECT_ROOT,
        "outbox_latest_path": latest_outbox,
        "outbox_latest_sha256": _sha256_file(latest_outbox)
        if latest_outbox and os.path.exists(latest_outbox)
        else None,
    }

    immutable_path = os.path.join(events_dir, f"audit_event_{ts_id}.json")
    tmp_path = immutable_path + ".tmp"

    _write_json(tmp_path, payload)
    os.replace(tmp_path, immutable_path)

    latest_path = os.path.join(audit_dir, "audit_event_latest.json")
    tmp_latest = os.path.join(audit_dir, f"audit_event_latest_{ts_id}.json.tmp")
    _write_json(tmp_latest, payload)
    _atomic_replace_latest(latest_path, tmp_latest)

    print(f"OK: wrote {immutable_path}")
    print(f"OK: updated {latest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())