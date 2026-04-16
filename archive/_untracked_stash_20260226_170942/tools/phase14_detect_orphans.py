import os
import sys
import sqlite3
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple

NOTE = "Phase14 orphan detection tool (write-once evidence generator)"

DEFAULT_DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
DEFAULT_TIP_FILE = r"C:\Users\sirok\MoCKA\audit\last_event_id.txt"

def _read_tip(tip_file: str) -> Optional[str]:
    if os.path.exists(tip_file):
        s = open(tip_file, "r", encoding="utf-8").read().strip()
        return s if s else None
    return None

def _list_tables(conn: sqlite3.Connection) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    return [r[0] for r in cur.fetchall()]

def _table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    return [r[1] for r in cur.fetchall()]

def _pick_ledger_table(conn: sqlite3.Connection) -> Tuple[str, str, str]:
    # Heuristic: find table containing event_id and prev-like column.
    candidates = []
    for t in _list_tables(conn):
        cols = [c.lower() for c in _table_columns(conn, t)]
        if "event_id" in cols:
            prev_col = None
            for pc in ["prev_event_id", "prev", "parent_event_id"]:
                if pc in cols:
                    prev_col = pc
                    break
            if prev_col:
                candidates.append((t, "event_id", prev_col))
    if not candidates:
        raise RuntimeError("No ledger-like table found (need columns: event_id + prev_event_id/prev/parent_event_id)")
    # Prefer table name containing 'ledger'
    candidates.sort(key=lambda x: (0 if "ledger" in x[0].lower() else 1, x[0].lower()))
    return candidates[0]

def _load_edges(conn: sqlite3.Connection, table: str, id_col: str, prev_col: str) -> Tuple[Dict[str, Optional[str]], List[str]]:
    cur = conn.cursor()
    cur.execute(f"SELECT {id_col}, {prev_col} FROM {table};")
    m: Dict[str, Optional[str]] = {}
    ids: List[str] = []
    for eid, pid in cur.fetchall():
        if eid is None:
            continue
        se = str(eid)
        sp = str(pid) if pid is not None else None
        m[se] = sp
        ids.append(se)
    return m, ids

def _reachable_from_tip(prev_map: Dict[str, Optional[str]], tip: str) -> List[str]:
    reached = []
    seen = set()
    cur = tip
    while cur and cur not in seen:
        seen.add(cur)
        reached.append(cur)
        cur = prev_map.get(cur)
    return reached

def main(argv: List[str]) -> int:
    db = DEFAULT_DB
    tip_file = DEFAULT_TIP_FILE

    if len(argv) >= 2:
        db = argv[1]
    if len(argv) >= 3:
        tip_file = argv[2]

    if not os.path.exists(db):
        print("ERROR: db not found:", db)
        return 2

    conn = sqlite3.connect(db)
    try:
        table, id_col, prev_col = _pick_ledger_table(conn)
        prev_map, all_ids = _load_edges(conn, table, id_col, prev_col)

        tip = _read_tip(tip_file)
        if not tip:
            # Fallback: pick any id that is not referenced as prev (a head candidate)
            referenced = set(pid for pid in prev_map.values() if pid)
            heads = [eid for eid in prev_map.keys() if eid not in referenced]
            tip = heads[0] if heads else None

        if not tip:
            print("ERROR: TIP not found (no tip file, no head candidate).")
            return 3

        reachable = set(_reachable_from_tip(prev_map, tip))
        orphans = sorted([eid for eid in prev_map.keys() if eid not in reachable])

        print("NOTE:", NOTE)
        print("DB:", db)
        print("LEDGER_TABLE:", table)
        print("TIP:", tip)
        print("TOTAL_EVENTS:", len(prev_map))
        print("REACHABLE_COUNT:", len(reachable))
        print("ORPHAN_COUNT:", len(orphans))

        if orphans:
            print()
            print("ORPHANS:")
            for eid in orphans:
                print(" -", eid, "prev=", prev_map.get(eid))
        else:
            print()
            print("ORPHANS: NONE")

        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
