import json
import hashlib

def canonical_json(obj):
    return json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )

def compute_hash(event):
    e = dict(event)
    e.pop("hash", None)
    s = canonical_json(e)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
