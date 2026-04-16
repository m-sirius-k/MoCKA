# C:\Users\sirok\MoCKA\tools\diagnose_chain_hash_rule.py
# Purpose: infer chain_hash recomputation rule by testing candidates against a verify_pack extract dir.
# Usage:
#   python tools\diagnose_chain_hash_rule.py <extract_dir>

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon_bytes(obj: Any) -> bytes:
    # best-effort deterministic json bytes
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")


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


def get_prev_id(obj: Dict[str, Any]) -> Optional[str]:
    for k in ["previous_event_id", "prev_event_id", "prev", "prev_id", "prevEventId", "prev_event", "prevEvent"]:
        v = obj.get(k)
        if isinstance(v, str) and is_hex64(v):
            return v.strip()
    return None


def get_chain_hash(obj: Dict[str, Any]) -> Optional[str]:
    for k in ["chain_hash", "chainHash"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def get_prev_chain_hash(obj: Dict[str, Any]) -> Optional[str]:
    for k in ["prev_chain_hash", "prevChainHash", "prev_chain", "prevChain"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def get_event_id(obj: Dict[str, Any]) -> Optional[str]:
    for k in ["event_id", "eventId", "id"]:
        v = obj.get(k)
        if isinstance(v, str) and is_hex64(v):
            return v.strip()
    return None


def get_signature(obj: Dict[str, Any]) -> Optional[str]:
    v = obj.get("signature")
    if isinstance(v, str) and v.strip():
        return v.strip()
    return None


def load_nodes(root: str) -> Dict[str, Tuple[str, Dict[str, Any]]]:
    nodes: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    for fn in os.listdir(root):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(root, fn)
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            continue
        eid = get_event_id(obj)
        # if event_id exists use it, else fallback to stem
        key = eid or os.path.splitext(fn)[0]
        nodes[key] = (fn, obj)
    return nodes


def build_chain(nodes: Dict[str, Tuple[str, Dict[str, Any]]]) -> List[str]:
    # linearize by prev pointers (genesis -> tip)
    forward: Dict[str, List[str]] = {}
    genesis: List[str] = []
    for k, (_, obj) in nodes.items():
        prev = get_prev_id(obj)
        if not prev or prev not in nodes:
            genesis.append(k)
        if prev:
            forward.setdefault(prev, []).append(k)

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


def b(s: str) -> bytes:
    return s.encode("utf-8")


def guess_rules() -> List[Tuple[str, callable]]:
    # candidate recompute rules: f(prev_chain_hash, obj, computed_json_sha) -> candidate_chain_hash
    rules: List[Tuple[str, callable]] = []

    def add(name: str, fn) -> None:
        rules.append((name, fn))

    # Common primitives
    def eid(obj: Dict[str, Any]) -> str:
        return (get_event_id(obj) or "")

    def prev_eid(obj: Dict[str, Any]) -> str:
        return (get_prev_id(obj) or "")

    def sig(obj: Dict[str, Any]) -> str:
        return (get_signature(obj) or "")

    def jh(obj: Dict[str, Any]) -> str:
        return sha256_hex(canon_bytes(obj))

    seps = ["", "\n", ":", "|", " ", "\t", ","]
    # Try concat patterns
    for sep in seps:
        add(f"sha256(prev+sep+event_id) sep={repr(sep)}",
            lambda p, o, sep=sep: sha256_hex(b(p + sep + eid(o))))
        add(f"sha256(event_id+sep+prev) sep={repr(sep)}",
            lambda p, o, sep=sep: sha256_hex(b(eid(o) + sep + p)))
        add(f"sha256(prev+sep+json_sha) sep={repr(sep)}",
            lambda p, o, sep=sep: sha256_hex(b(p + sep + jh(o))))
        add(f"sha256(json_sha+sep+prev) sep={repr(sep)}",
            lambda p, o, sep=sep: sha256_hex(b(jh(o) + sep + p)))
        add(f"sha256(prev+sep+prev_event_id) sep={repr(sep)}",
            lambda p, o, sep=sep: sha256_hex(b(p + sep + prev_eid(o))))
        add(f"sha256(prev+sep+signature) sep={repr(sep)}",
            lambda p, o, sep=sep: sha256_hex(b(p + sep + sig(o))))

    # Try double concat: prev + sep1 + prev_event_id + sep2 + event_id
    for sep1 in ["", ":", "|", "\n"]:
        for sep2 in ["", ":", "|", "\n"]:
            add(f"sha256(prev+{repr(sep1)}+prev_event_id+{repr(sep2)}+event_id)",
                lambda p, o, sep1=sep1, sep2=sep2: sha256_hex(b(p + sep1 + prev_eid(o) + sep2 + eid(o))))

    return rules


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python diagnose_chain_hash_rule.py <extract_dir>")
        return 2

    root = sys.argv[1]
    if not os.path.isdir(root):
        print("not a directory:", root)
        return 2

    nodes = load_nodes(root)
    order = build_chain(nodes)

    # Collect edges where chain_hash exists and there is a previous chain hash (field or carry)
    edges: List[Tuple[str, str, str, str]] = []
    last_chain_hash: Optional[str] = None

    for k in order:
        _, obj = nodes[k]
        ch = get_chain_hash(obj)
        pch = get_prev_chain_hash(obj)
        prev = pch or last_chain_hash
        if ch and prev:
            edges.append((k, prev, ch, (get_prev_id(obj) or "")))
        if ch:
            last_chain_hash = ch

    print(json.dumps({
        "json_files": len(nodes),
        "linear_chain_length": len(order),
        "edges_with_chainhash": len(edges),
    }, ensure_ascii=False, indent=2))

    if not edges:
        print("no edges to test (need chain_hash and prev reference)")
        return 0

    rules = guess_rules()
    scores: List[Tuple[int, str]] = []
    for name, fn in rules:
        ok = 0
        for (k, prev_ch, ch, _prev_eid) in edges:
            _, obj = nodes[k]
            try:
                got = fn(prev_ch, obj)
            except Exception:
                got = None
            if isinstance(got, str) and got.lower() == ch.lower():
                ok += 1
        scores.append((ok, name))

    scores.sort(key=lambda x: (-x[0], x[1]))
    top = scores[:15]

    print("TOP_RULES:")
    for ok, name in top:
        print(f"{ok}/{len(edges)}  {name}")

    # Show the first failing edge under best rule, to help manual confirmation
    best_ok, best_name = top[0]
    best_fn = None
    for name, fn in rules:
        if name == best_name:
            best_fn = fn
            break

    if best_fn is not None:
        for (k, prev_ch, ch, prev_eid_val) in edges:
            _, obj = nodes[k]
            got = best_fn(prev_ch, obj)
            if got.lower() != ch.lower():
                print("FIRST_FAIL_UNDER_BEST_RULE:")
                print(json.dumps({
                    "event_id": get_event_id(obj),
                    "previous_event_id": prev_eid_val,
                    "prev_chain_hash_used": prev_ch,
                    "stored_chain_hash": ch,
                    "recomputed_chain_hash": got,
                    "best_rule": best_name,
                }, ensure_ascii=False, indent=2))
                break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())