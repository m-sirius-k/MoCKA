import os
import sqlite3

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
OUT_PATH = os.path.join(os.getcwd(), "audit", "db_ledger_dump.tsv")


def table_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def pick_ledger_table(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]

    for t in tables:
        cols = table_columns(conn, t)
        if "event_id" in cols and ("previous_event_id" in cols or "prev_event_id" in cols):
            prev_col = "previous_event_id" if "previous_event_id" in cols else "prev_event_id"
            return t, prev_col

    return None, None


def main():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"DB not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        table, prev_col = pick_ledger_table(conn)
        if not table:
            raise SystemExit("No ledger-like table found (need event_id and previous_event_id/prev_event_id)")

        cur = conn.cursor()
        cur.execute(f"SELECT event_id, {prev_col} FROM {table}")
        rows = cur.fetchall()

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            f.write("event_id\tprevious_event_id\n")
            for eid, pid in rows:
                f.write(f"{eid}\t{pid}\n")

        print(f"OK: db={DB_PATH}")
        print(f"OK: table={table} prev_col={prev_col}")
        print(f"OK: dumped_rows={len(rows)}")
        print(f"OK: out={OUT_PATH}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
