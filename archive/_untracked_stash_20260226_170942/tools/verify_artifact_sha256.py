import hashlib
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def fail(msg):
    print("FAIL: verify_artifact_sha256.py: " + msg)
    return 1

def main():
    event = os.path.join(PROJECT_ROOT, "audit", "audit_event_latest.json")
    if not os.path.exists(event):
        return fail("audit_event_latest.json missing: " + event)

    try:
        with open(event, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as e:
        return fail("invalid json: " + str(e))

    path = payload.get("outbox_latest_path")
    expected = payload.get("outbox_latest_sha256")

    if path is None:
        return fail("outbox_latest_path is None")
    if expected is None:
        return fail("outbox_latest_sha256 is None")
    if not os.path.exists(path):
        return fail("artifact missing: " + str(path))

    actual = sha256_file(path)
    if actual != expected:
        return fail("sha256 mismatch expected=" + str(expected) + " actual=" + str(actual))

    print("OK: verify_artifact_sha256.py")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
