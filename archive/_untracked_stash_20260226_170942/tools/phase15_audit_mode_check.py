import os
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    result = {"status":"UNKNOWN","governance":{},"integrity":{}}

    gov_db = ROOT / "mocka-governance-kernel" / "governance" / "governance.db"
    if not gov_db.exists():
        result["status"]="NG"
        result["error"]="governance.db not found"
        print(json.dumps(result,indent=2))
        return

    conn = sqlite3.connect(str(gov_db))
    conn.row_factory = sqlite3.Row

    ledger="governance_ledger_event"
    tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    if ledger not in tables:
        result["status"]="NG"
        result["error"]="ledger table missing"
        print(json.dumps(result,indent=2))
        return

    cols=[r[1] for r in conn.execute(f"PRAGMA table_info({ledger})")]
    result["governance"]["columns"]=cols
    result["governance"]["row_count"]=conn.execute(f"SELECT COUNT(1) FROM {ledger}").fetchone()[0]

    if "event_type" in cols:
        types=[r[0] for r in conn.execute(f"SELECT DISTINCT event_type FROM {ledger}")]
        result["governance"]["event_types"]=types
        if "ANCHOR_PROOF" in types:
            row=conn.execute(f"SELECT * FROM {ledger} WHERE event_type='ANCHOR_PROOF' ORDER BY rowid DESC LIMIT 1").fetchone()
            if row:
                if "crypto_verified" in row.keys():
                    result["governance"]["anchor_crypto_verified"]=bool(row["crypto_verified"])
    conn.close()

    integrity_db = ROOT / "infield" / "phase16" / "db" / "integrity.db"
    if integrity_db.exists():
        ic = sqlite3.connect(str(integrity_db))
        itables=[r[0] for r in ic.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        result["integrity"]["tables"]=itables
        ic.close()

    result["status"]="OK"
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
