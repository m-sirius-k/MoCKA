from __future__ import annotations

import argparse
import json
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.mocka_integrity.create_anchor import create_anchor


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-event-id", required=True)
    ap.add_argument("--source-chain-hash", required=True)
    ap.add_argument("--final-chain-hash", required=True)
    ap.add_argument("--private-key-path", required=True)
    ap.add_argument("--public-key-id", required=True)
    ap.add_argument("--integrity-db", default=None)

    args = ap.parse_args()

    out = create_anchor(
        source_event_id=args.source_event_id,
        source_chain_hash=args.source_chain_hash,
        final_chain_hash=args.final_chain_hash,
        private_key_path=args.private_key_path,
        public_key_id=args.public_key_id,
        integrity_db_path=args.integrity_db,
    )

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())