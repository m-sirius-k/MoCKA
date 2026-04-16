import hashlib
import json
import os
from datetime import datetime, timezone


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

HISTORY = os.path.join(DATA, "KEY_HISTORY_LOG_v3.jsonl")
ALLOWLIST = os.path.join(DATA, "LEGACY_DUPLICATE_ALLOWLIST_v3.json")


def fail(msg: str) -> int:
    print("status: FAIL")
    print("error: " + msg)
    return 1


def parse_utc(ts: str) -> datetime:
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s).astimezone(timezone.utc)


def sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_allowlist() -> set:
    allow = set()
    if os.path.isfile(ALLOWLIST):
        with open(ALLOWLIST, "r", encoding="utf-8-sig", newline="\n") as f:
            obj = json.load(f)
        if isinstance(obj, list):
            for x in obj:
                if isinstance(x, str) and x.strip():
                    allow.add(x.strip().lower())
    return allow


def canonical_prev(obj: dict) -> str:
    for k in ["previous_event_sha256", "previousEventSha256", "prev_event_sha256", "prev", "prev_id"]:
        v = obj.get(k)
        if isinstance(v, str):
            return v.strip().lower()
    return ""


def canonical_ts(obj: dict) -> str:
    for k in ["recorded_at_utc", "recordedAtUtc", "ts_utc", "timestamp_utc", "timestamp", "ts"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def event_sha(obj: dict) -> str:
    for k in ["event_sha256", "eventSha256"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip().lower()
    return ""


def event_identity(obj: dict) -> str:
    # stable identity for legacy-duplicate allowance:
    # hash of semantic payload excluding recorded_at_utc and previous_event_sha256 and event_sha256
    base = dict(obj)
    for k in [
        "recorded_at_utc",
        "recordedAtUtc",
        "previous_event_sha256",
        "previousEventSha256",
        "event_sha256",
        "eventSha256",
    ]:
        if k in base:
            del base[k]
    payload = json.dumps(base, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_hex_bytes(payload).lower()


def main() -> int:
    if not os.path.isfile(HISTORY):
        return fail("missing history: " + HISTORY)

    try:
        allow = load_allowlist()
    except Exception as e:
        return fail("allowlist load error: " + str(e))

    seen_event_sha = set()
    prev_chain = None
    rows = 0
    events = 0

    with open(HISTORY, "r", encoding="utf-8-sig", newline="\n") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            rows += 1

            try:
                obj = json.loads(line)
            except Exception as e:
                return fail("jsonl parse error at row " + str(rows) + ": " + str(e))

            if not isinstance(obj, dict):
                return fail("row must be object at row " + str(rows))

            sha = event_sha(obj)
            if not sha:
                return fail("missing event_sha256 at row " + str(rows))

            ts = canonical_ts(obj)
            if not ts:
                return fail("missing utc timestamp at row " + str(rows))
            try:
                _ = parse_utc(ts)
            except Exception as e:
                return fail("timestamp parse error at row " + str(rows) + ": " + str(e))

            prev = canonical_prev(obj)

            if prev_chain is None:
                if prev not in ["", "genesis"]:
                    return fail("first row previous_event_sha256 must be empty/GENESIS")
            else:
                if prev != prev_chain:
                    return fail("chain broken at row " + str(rows) + ": prev != previous event")

            # duplicate policy:
            # duplicates are defined by event_sha256 (strict), but legacy duplicates can be allowlisted by event_identity
            if sha in seen_event_sha:
                ident = event_identity(obj)
                if ident not in allow:
                    return fail("duplicate event_sha256 not allowlisted at row " + str(rows) + ": " + sha)
            else:
                seen_event_sha.add(sha)

            prev_chain = sha
            events += 1

    if events == 0:
        return fail("no events found in history")

    print("status: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
