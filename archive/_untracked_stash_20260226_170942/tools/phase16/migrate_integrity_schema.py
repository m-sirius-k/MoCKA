"""
Phase16 integrity DB schema migration tool
date: 2026-02-24

note:
- Fix: ensure repo root is on sys.path so "src.*" imports work
- Explicit migration only
- Safe to run repeatedly
"""

from __future__ import annotations

import argparse
import os
import sys

# Ensure repository root is importable (so "src" package resolves)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.mocka_integrity.integrity_db import IntegrityDBConfig, migrate_schema


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None, help="integrity db path (optional)")
    args = ap.parse_args()

    cfg = IntegrityDBConfig(db_path=args.db) if args.db else IntegrityDBConfig()
    ok, msg = migrate_schema(cfg)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
