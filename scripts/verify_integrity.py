#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/verify_integrity.py -- Phase5-2 Event Integrity Framework CLI

Flaskサーバーを起動せずに Integrity Verification + Recovery Support を
実行できるCLI。schema_audit.pyのCLIパターンに合わせる。

使い方:
  python scripts/verify_integrity.py            -- 検証のみ
  python scripts/verify_integrity.py --diagnose -- 検証+異常診断
"""

import sqlite3
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "phi_os"))
sys.path.insert(0, str(_REPO_ROOT))

import integrity  # noqa: E402

DB_PATH = _REPO_ROOT / "data" / "mocka_events.db"


def main() -> int:
    diagnose_requested = "--diagnose" in sys.argv

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        result = integrity.verify_chain(conn)
    finally:
        conn.close()

    print(f"{'OK' if result['ok'] else 'NG'}: checked={result['checked']} "
          f"anomalies={len(result['anomalies'])}")

    for a in result["anomalies"]:
        print(f"  - {a['type']} seq={a['seq']} event_id={a['event_id']}: {a['detail']}")

    if diagnose_requested and result["anomalies"]:
        print("\n--- Recovery Support: diagnosis ---")
        for d in integrity.diagnose(result["anomalies"]):
            print(f"  location: {d['location']}")
            print(f"  affected_range: {d['affected_range']}")
            print(f"  candidate_cause: {d['candidate_cause']}")
            print(f"  candidate_repair: {d['candidate_repair']}")
            print("")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
