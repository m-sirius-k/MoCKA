
import os
import sqlite3

NOTE = "Phase14 deterministic TIP reselection tool (auto-ledger-detect)"

DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
TIP_FILE = r"C:\Users\sirok\MoCKA\audit\last_event_id.txt"

def detect_ledger_table(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]

    for t in tables:
        cur.execute(f"PRAGMA table_info({t});")
        cols = [c[1].lower() for c in cur.fetchall()]
        if "event_id" in cols:
            if "prev_event_id" in cols:
                return t, "event_id", "prev_event_id"
            if "prev" in cols:
                return t, "event_id", "prev"
    raise RuntimeError("No ledger-like table found")

def load_edges(conn, table, id_col, prev_col):
    cur = conn.cursor()
    cur.execute(f"SELECT {id_col}, {prev_col} FROM {table};")
    return cur.fetchall()

def compute_lengths(edges):
    prev = {e:p for e,p in edges}
    lengths = {}

    def length(e):
        if e in lengths:
            return lengths[e]
        p = prev.get(e)
        if not p:
            lengths[e] = 1
        else:
            lengths[e] = 1 + length(p)
        return lengths[e]

    for e,_ in edges:
        length(e)

    return lengths

def main():
    if not os.path.exists(DB):
        raise RuntimeError("DB not found: " + DB)

    conn = sqlite3.connect(DB)
    table, id_col, prev_col = detect_ledger_table(conn)
    edges = load_edges(conn, table, id_col, prev_col)
    conn.close()

    if not edges:
        raise RuntimeError("No events in ledger")

    lengths = compute_lengths(edges)
    max_len = max(lengths.values())
    candidates = [e for e,l in lengths.items() if l == max_len]
    tip = sorted(candidates)[0]

    with open(TIP_FILE, "w", encoding="utf-8") as f:
        f.write(tip)

    print("LEDGER_TABLE:", table)
    print("NEW_TIP_SELECTED:", tip)
    print("CHAIN_LENGTH:", max_len)

if __name__ == "__main__":
    main()
