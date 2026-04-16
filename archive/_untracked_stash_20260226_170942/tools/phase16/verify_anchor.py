from __future__ import annotations

import argparse
import json
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.mocka_integrity.verify_anchor import verify_anchor_by_final_chain_hash
from src.mocka_integrity.integrity_db import IntegrityDBConfig


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--final-chain-hash", required=True)
    ap.add_argument("--public-key-path", required=True)
    ap.add_argument("--integrity-db", default=None)
    args = ap.parse_args()

    cfg = IntegrityDBConfig(db_path=args.integrity_db) if args.integrity_db else IntegrityDBConfig()

    result = verify_anchor_by_final_chain_hash(
        cfg,
        final_chain_hash=args.final_chain_hash,
        public_key_path=args.public_key_path,
    )

    print(json.dumps({
        "status": result.status,
        "reason": result.reason,
        "detail": result.detail
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
