import hashlib, json, os, sys

def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

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

def get_prev_id(obj):
    for k in ["previous_event_id","prev_event_id","prev","prev_id","prevEventId","prev_event","prevEvent"]:
        v = obj.get(k)
        if isinstance(v, str) and is_hex64(v):
            return v.strip()
    return None

def get_chain_hash(obj):
    for k in ["chain_hash", "chainHash"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def get_prev_chain_hash(obj):
    for k in ["prev_chain_hash", "prevChainHash", "prev_chain", "prevChain"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def recompute_chain_hash(prev_chain_hash, event_id):
    return sha256_hex((prev_chain_hash + event_id).encode("utf-8"))

def load_nodes(root):
    nodes = {}
    for fn in os.listdir(root):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(root, fn)
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        computed_id = sha256_hex(canon(obj))
        claimed_id = obj.get("event_id")
        prev_id = get_prev_id(obj)
        key = claimed_id or computed_id
        nodes[key] = (fn, obj, computed_id, claimed_id, prev_id)
    return nodes

def build_chain(nodes):
    genesis = []
    for key, (_, _, _, _, prev) in nodes.items():
        if (not prev) or (prev not in nodes):
            genesis.append(key)
    if not genesis:
        genesis = [next(iter(nodes.keys()))]
    genesis.sort()
    cur = genesis[0]
    chain = [cur]

    forward = {}
    for key, (_, _, _, _, prev) in nodes.items():
        if prev:
            forward.setdefault(prev, []).append(key)

    visited = set([cur])
    while True:
        succ = forward.get(cur, [])
        if not succ:
            break
        succ.sort()
        nxt = succ[0]
        if nxt in visited:
            break
        chain.append(nxt)
        visited.add(nxt)
        cur = nxt
    return chain

def main():
    if len(sys.argv) != 2:
        print("usage: python verify.py <dir>")
        return 2
    root = sys.argv[1]
    nodes = load_nodes(root)
    order = build_chain(nodes)

    last_chain_hash = None
    chainhash_checked = 0
    chainhash_failed = 0

    id_mismatch = 0
    mismatch_samples = []

    for key in order:
        fn, obj, computed_id, claimed_id, _ = nodes[key]
        if claimed_id and computed_id and claimed_id != computed_id:
            id_mismatch += 1
            if len(mismatch_samples) < 3:
                mismatch_samples.append({"file": fn, "claimed_event_id": claimed_id, "computed_event_id": computed_id})

        ch = get_chain_hash(obj)
        pch = get_prev_chain_hash(obj)

        if ch and (pch or last_chain_hash):
            expected_prev = pch or last_chain_hash
            if expected_prev:
                eid = claimed_id or key
                recomputed = recompute_chain_hash(expected_prev, eid)
                chainhash_checked += 1
                if recomputed.lower() != ch.lower():
                    chainhash_failed += 1
            last_chain_hash = ch
        elif ch:
            last_chain_hash = ch

    status = "OK" if (chainhash_failed == 0) else "NG"
    out = {
        "status": status,
        "linear_chain_length": len(order),
        "event_id_mismatch_info": id_mismatch,
        "event_id_mismatch_samples": mismatch_samples,
        "chainhash_checked": chainhash_checked,
        "chainhash_failed": chainhash_failed,
        "final_chain_hash_observed": last_chain_hash,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if status == "OK" else 1

if __name__ == "__main__":
    raise SystemExit(main())
