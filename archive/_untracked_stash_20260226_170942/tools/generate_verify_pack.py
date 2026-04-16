# C:\Users\sirok\MoCKA\tools\generate_verify_pack.py
# Phase12-B: External Verify Pack Generator (stdlib only)
# - Extract chain from TIP to GENESIS boundary
# - Bundle public key
# - Generate verify.py (compat chain_hash verifier)
# - Zip and print SHA256

from __future__ import annotations

import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIT_DIR = os.path.join(ROOT, "audit")
RECOVERY_DIR = os.path.join(AUDIT_DIR, "recovery")
KEY_DIR = os.path.join(AUDIT_DIR, "ed25519", "keys")
OUTBOX_DIR = os.path.join(ROOT, "outbox", "verify_pack")


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_text(p: str) -> str:
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def read_json(p: str) -> Dict[str, Any]:
    with open(p, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise ValueError("json is not an object: " + p)
    return obj


def is_hex64(s: Any) -> bool:
    if not isinstance(s, str):
        return False
    t = s.strip()
    if len(t) != 64:
        return False
    for c in t.lower():
        if c not in "0123456789abcdef":
            return False
    return True


def pick_event_id_from_value(v: Any) -> Optional[str]:
    if isinstance(v, str) and is_hex64(v):
        return v.strip()
    if isinstance(v, dict):
        for k in ["event_id", "eventId", "id", "tip", "TIP", "tip_event_id", "last_event_id", "lastEventId"]:
            vv = v.get(k)
            if isinstance(vv, str) and is_hex64(vv):
                return vv.strip()
    return None


def find_tip_from_regenesis(regenesis_path: str) -> Optional[str]:
    obj = read_json(regenesis_path)

    keys = [
        "tip_event_id",
        "tip",
        "TIP",
        "tipEventId",
        "last_event_id",
        "lastEventId",
        "event_id",
        "eventId",
        "head",
        "HEAD",
        "current",
        "cur",
    ]
    for k in keys:
        if k in obj:
            eid = pick_event_id_from_value(obj.get(k))
            if eid:
                return eid

    def deep_scan(x: Any) -> Optional[str]:
        if isinstance(x, str) and is_hex64(x):
            return x.strip()
        if isinstance(x, dict):
            for vv in x.values():
                hit = deep_scan(vv)
                if hit:
                    return hit
        if isinstance(x, list):
            for vv in x:
                hit = deep_scan(vv)
                if hit:
                    return hit
        return None

    return deep_scan(obj)


def find_tip() -> str:
    regenesis = os.path.join(RECOVERY_DIR, "regenesis.json")
    if os.path.exists(regenesis):
        tip = find_tip_from_regenesis(regenesis)
        if tip:
            return tip

    last_id_txt = os.path.join(AUDIT_DIR, "last_event_id.txt")
    if os.path.exists(last_id_txt):
        t = read_text(last_id_txt).strip()
        if is_hex64(t):
            return t

    best: Optional[Tuple[float, str]] = None
    if os.path.isdir(AUDIT_DIR):
        for fn in os.listdir(AUDIT_DIR):
            if not fn.lower().endswith(".json"):
                continue
            stem = os.path.splitext(fn)[0]
            if not is_hex64(stem):
                continue
            p = os.path.join(AUDIT_DIR, fn)
            try:
                mt = os.path.getmtime(p)
            except Exception:
                continue
            if best is None or mt > best[0]:
                best = (mt, stem)
    if best:
        return best[1]

    raise ValueError("cannot resolve TIP from regenesis.json / last_event_id.txt / latest audit json")


def find_event_file(event_id: str) -> str:
    p = os.path.join(AUDIT_DIR, f"{event_id}.json")
    if not os.path.exists(p):
        raise FileNotFoundError("event file not found: " + p)
    return p


def get_prev_id(obj: Dict[str, Any]) -> Optional[str]:
    keys = [
        "previous_event_id",  # current chain
        "prev_event_id",      # older schema
        "previousEventId",
        "prevEventId",
        "prev",
        "prev_id",
        "prev_event",
        "prevEvent",
    ]
    for k in keys:
        v = obj.get(k)
        if isinstance(v, str) and is_hex64(v):
            return v.strip()
    return None


def extract_chain_from_tip(tip: str) -> List[str]:
    chain_files: List[str] = []
    current = tip
    visited = set()

    while current and current not in visited:
        visited.add(current)
        p = find_event_file(current)
        chain_files.append(p)

        obj = read_json(p)
        prev = get_prev_id(obj)
        if not prev:
            break
        current = prev

    chain_files.reverse()
    return chain_files


def find_public_key() -> str:
    preferred = os.path.join(KEY_DIR, "ed25519_public.key")
    if os.path.exists(preferred):
        return preferred

    best: Optional[Tuple[float, str]] = None
    if os.path.isdir(KEY_DIR):
        for fn in os.listdir(KEY_DIR):
            low = fn.lower()
            if not low.endswith(".key"):
                continue
            if "public" not in low:
                continue
            p = os.path.join(KEY_DIR, fn)
            try:
                mt = os.path.getmtime(p)
            except Exception:
                continue
            if best is None or mt > best[0]:
                best = (mt, p)
    if best:
        return best[1]

    raise FileNotFoundError("public key not found: " + KEY_DIR)


def write_verify_script(dest_dir: str) -> None:
    # Compat verifier:
    # - does NOT try to re-derive event_id (because MoCKA may have multiple historical rules)
    # - verifies chain linearization by previous_event_id/prev_event_id pointers
    # - verifies chain_hash by accepting multiple known historical rules
    code = r'''
import hashlib, json, os, sys

def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()

def is_hex64(s):
    if not isinstance(s, str):
        return False
    t = s.strip()
    if len(t) != 64:
        return False
    for c in t.lower():
        if c not in "0123456789abcdef":
            return False
    return True

def get_event_id(obj):
    for k in ["event_id","eventId","id"]:
        v = obj.get(k)
        if isinstance(v, str) and is_hex64(v):
            return v.strip()
    return None

def get_prev_id(obj):
    for k in ["previous_event_id","prev_event_id","previousEventId","prevEventId","prev","prev_id","prev_event","prevEvent"]:
        v = obj.get(k)
        if isinstance(v, str) and is_hex64(v):
            return v.strip()
    return None

def get_chain_hash(obj):
    for k in ["chain_hash","chainHash"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def load_nodes(root):
    nodes = {}
    for fn in os.listdir(root):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(root, fn)
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            continue
        eid = get_event_id(obj)
        if not eid:
            continue
        nodes[eid] = {"fn": fn, "obj": obj}
    return nodes

def build_chain(nodes):
    forward = {}
    genesis = []
    for eid, n in nodes.items():
        prev = get_prev_id(n["obj"])
        if not prev or prev not in nodes:
            genesis.append(eid)
        if prev:
            forward.setdefault(prev, []).append(eid)

    if not genesis:
        genesis = [next(iter(nodes.keys()))]
    genesis.sort()

    cur = genesis[0]
    chain = [cur]
    visited = set(chain)
    while True:
        nxts = forward.get(cur, [])
        if not nxts:
            break
        nxts.sort()
        nxt = nxts[0]
        if nxt in visited:
            break
        chain.append(nxt)
        visited.add(nxt)
        cur = nxt
    return chain

def verify_chain_hash(chain, nodes):
    # Rules accepted (compat):
    # A) atomic_append: if no prev -> chain_hash == event_id
    # B) atomic_append / contract_v1: sha256(prev_event_id + event_id)
    # C) audit_writer: sha256(prev_chain_hash + event_id)
    # D) audit_writer fallback: sha256((prev_event_id or "GENESIS") + event_id)
    failed = 0
    matched = {"A_genesis_eq_eid":0, "B_prev_eid_plus_eid":0, "C_prev_chain_plus_eid":0, "D_genesis_or_prev_eid_plus_eid":0}

    prev_eid = None
    prev_chain_hash = None

    for eid in chain:
        obj = nodes[eid]["obj"]
        stored = get_chain_hash(obj) or ""
        prev_ptr = get_prev_id(obj)  # may be None at genesis

        candidates = []

        # A) genesis special
        if not prev_ptr:
            candidates.append(("A_genesis_eq_eid", eid))
            candidates.append(("D_genesis_or_prev_eid_plus_eid", sha256_hex(("GENESIS" + eid).encode("utf-8"))))
        else:
            # B) prev_event_id + eid
            candidates.append(("B_prev_eid_plus_eid", sha256_hex((prev_ptr + eid).encode("utf-8"))))

            # C) prev_chain_hash + eid (if we have it)
            if prev_chain_hash:
                candidates.append(("C_prev_chain_plus_eid", sha256_hex((prev_chain_hash + eid).encode("utf-8"))))

            # D) (prev_event_id or GENESIS) + eid
            base = (prev_ptr or "GENESIS") + eid
            candidates.append(("D_genesis_or_prev_eid_plus_eid", sha256_hex(base.encode("utf-8"))))

        ok = False
        for name, cand in candidates:
            if cand.lower() == stored.lower():
                matched[name] += 1
                ok = True
                break

        if not ok:
            failed += 1

        prev_eid = eid
        prev_chain_hash = stored or prev_chain_hash

    return failed, matched

def main():
    if len(sys.argv) != 2:
        print("usage: python verify.py <dir>")
        return 2

    root = sys.argv[1]
    if not os.path.isdir(root):
        print("not a directory:", root)
        return 2

    nodes = load_nodes(root)
    chain = build_chain(nodes)

    failed, matched = verify_chain_hash(chain, nodes)

    status = "OK" if failed == 0 else "NG"
    out = {
        "status": status,
        "linear_chain_length": len(chain),
        "chainhash_failed": failed,
        "chainhash_matched_counts": matched,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if status == "OK" else 1

if __name__ == "__main__":
    raise SystemExit(main())
'''.strip()

    with open(os.path.join(dest_dir, "verify.py"), "w", encoding="utf-8") as f:
        f.write(code + "\n")


def zip_dir(src_dir: str, zip_path: str) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in os.listdir(src_dir):
            p = os.path.join(src_dir, fn)
            if os.path.isfile(p):
                z.write(p, arcname=fn)


def main() -> None:
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    tip = find_tip()
    chain_files = extract_chain_from_tip(tip)
    pubkey = find_public_key()

    utc = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    work_dir = os.path.join(OUTBOX_DIR, f"work_{utc}")
    os.makedirs(work_dir, exist_ok=True)

    for p in chain_files:
        shutil.copy2(p, os.path.join(work_dir, os.path.basename(p)))

    shutil.copy2(pubkey, os.path.join(work_dir, os.path.basename(pubkey)))

    write_verify_script(work_dir)

    zip_path = os.path.join(OUTBOX_DIR, f"mocka_phase12_verify_{utc}.zip")
    zip_dir(work_dir, zip_path)

    with open(zip_path, "rb") as f:
        h = sha256_hex(f.read())

    print("VERIFY PACK GENERATED")
    print("TIP:", tip)
    print("CHAIN_FILES:", len(chain_files))
    print("ZIP:", zip_path)
    print("SHA256:", h)


if __name__ == "__main__":
    main()