# file: C:\Users\sirok\MoCKA\mocka-governance-kernel\tools\make_manifest_v1.py
from __future__ import annotations
import argparse, hashlib, os, json
from datetime import datetime, timezone
from typing import List, Dict

def utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()

    items: List[Dict[str,str]] = []
    for p in a.files:
        apath = os.path.abspath(p)
        items.append({
            "path": apath,
            "sha256": sha256_file(apath),
            "bytes": str(os.path.getsize(apath))
        })

    m = {
        "manifest_version": "v1",
        "generated_at_utc": utc(),
        "items": items
    }

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=True, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()
