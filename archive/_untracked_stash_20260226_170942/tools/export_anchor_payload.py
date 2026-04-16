import sqlite3
from pathlib import Path

GOV_DB = r"C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\governance.db"
OUT_PATH = r"C:\Users\sirok\MoCKA\outbox\governance_anchor_proof_payload.json"

def main():
    conn = sqlite3.connect(GOV_DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT payload_json FROM governance_ledger_event "
        "WHERE event_type='ANCHOR_PROOF' "
        "ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if not row:
        print("NO ANCHOR_PROOF FOUND")
        return 1

    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(row["payload_json"])

    print("EXPORTED:", OUT_PATH)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
