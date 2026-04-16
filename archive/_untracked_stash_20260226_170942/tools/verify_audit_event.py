import json
import os
import re
import sys

HEX64 = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_TOP = ["run_id", "ts_utc", "actor", "decision", "policy", "artifacts"]
REQUIRED_POLICY = ["version", "result"]
REQUIRED_ART = ["kind", "path", "sha256"]

def fail(msg: str, code: int = 2) -> int:
    print("FAIL:", msg)
    return code

def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_path = os.path.join(root, "schemas", "audit_event.schema.json")
    sample_path = os.path.join(root, "examples", "audit_event_latest.json")

    if not os.path.isfile(schema_path):
        return fail(f"MISSING_SCHEMA_FILE: {schema_path}")

    if not os.path.isfile(sample_path):
        return fail(f"MISSING_SAMPLE_FILE: {sample_path}")

    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return fail("TOP_LEVEL_NOT_OBJECT")

    for k in REQUIRED_TOP:
        if k not in data:
            return fail(f"MISSING_KEY: {k}")

    if not isinstance(data["policy"], dict):
        return fail("POLICY_NOT_OBJECT")
    for k in REQUIRED_POLICY:
        if k not in data["policy"]:
            return fail(f"MISSING_POLICY_KEY: {k}")

    arts = data["artifacts"]
    if not isinstance(arts, list) or len(arts) == 0:
        return fail("ARTIFACTS_NOT_NONEMPTY_LIST")

    for i, a in enumerate(arts):
        if not isinstance(a, dict):
            return fail(f"ARTIFACT_{i}_NOT_OBJECT")
        for k in REQUIRED_ART:
            if k not in a:
                return fail(f"MISSING_ARTIFACT_{i}_KEY: {k}")
        if not isinstance(a["sha256"], str) or not HEX64.match(a["sha256"]):
            return fail(f"BAD_SHA256_ARTIFACT_{i}")

    print("OK: audit_event_latest.json passes minimal checks")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
