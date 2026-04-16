import json
import hashlib
from pathlib import Path

AUDIT_DIR = Path(r"C:\Users\sirok\MoCKA\audit")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_events():
    events = {}
    for f in AUDIT_DIR.glob("*.json"):
        try:
            if f.stat().st_size == 0:
                continue
            with open(f, "r", encoding="utf-8-sig") as fh:
                obj = json.load(fh)
            eid = obj.get("event_id")
            if not eid:
                continue
            events[eid] = {
                "previous_event_id": obj.get("previous_event_id"),
                "chain_hash": obj.get("chain_hash"),
                "file": str(f),
            }
        except Exception:
            continue
    return events

def ok_link(events, eid):
    d = events[eid]
    prev = d["previous_event_id"]
    ch = d["chain_hash"]
    if not ch:
        return False
    if prev:
        return ch == sha256_hex((prev + eid).encode("utf-8"))
    return ch == eid

def walk_back(events, tip):
    visited = set()
    cur = tip
    length = 0
    while cur:
        if cur in visited:
            return (False, length, "cycle", cur)
        if cur not in events:
            return (False, length, "missing", cur)
        if not ok_link(events, cur):
            return (False, length, "chain_hash_mismatch", cur)
        visited.add(cur)
        length += 1
        cur = events[cur]["previous_event_id"]
    return (True, length, "ok", tip)

def main():
    events = load_events()
    if not events:
        print("NO EVENTS")
        return 1

    # candidate tips = event_id that is not referenced as previous_event_id by any other
    referenced = set()
    for d in events.values():
        p = d["previous_event_id"]
        if p:
            referenced.add(p)

    tips = [eid for eid in events.keys() if eid not in referenced]
    if not tips:
        tips = list(events.keys())

    best = None
    best_len = -1
    best_detail = None

    for t in tips:
        ok, ln, why, at = walk_back(events, t)
        if ok and ln > best_len:
            best = t
            best_len = ln
            best_detail = (ok, ln, why, at)

    if not best:
        # no fully-ok chain; choose longest partial (still useful)
        for t in tips:
            ok, ln, why, at = walk_back(events, t)
            if ln > best_len:
                best = t
                best_len = ln
                best_detail = (ok, ln, why, at)

    ok, ln, why, at = best_detail
    print("TIP=", best)
    print("LENGTH=", ln)
    print("STATUS=", "OK" if ok else "PARTIAL")
    print("DETAIL=", why, at)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())