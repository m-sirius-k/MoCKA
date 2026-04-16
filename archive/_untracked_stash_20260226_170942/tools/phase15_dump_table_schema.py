import argparse
import json
import os
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB = os.path.join(ROOT, "audit", "ed25519", "audit.db")

def object_info(conn: sqlite3.Connection, name: str):
    cur = conn.execute(
        "SELECT type, sql FROM sqlite_master WHERE name=? AND type IN ('table','view')",
        (name,),
    )
    row = cur.fetchone()
    if not row:
        return None, None
    return row[0], row[1]

def get_columns(conn: sqlite3.Connection, name: str):
    cur = conn.execute(f"PRAGMA table_info({name})")
    rows = cur.fetchall()
    cols = []
    for r in rows:
        cols.append({
            "cid": r[0],
            "name": r[1],
            "type": r[2],
            "notnull": r[3],
            "dflt_value": r[4],
            "pk": r[5],
        })
    return cols

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--table", required=True)
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print(json.dumps({"status": "NG", "error": "db_not_found", "path": args.db}, indent=2))
        raise SystemExit(2)

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    try:
        obj_type, sql = object_info(conn, args.table)
        cols = get_columns(conn, args.table)
    finally:
        conn.close()

    if obj_type is None:
        print(json.dumps({
            "status": "NG",
            "error": "table_or_view_not_found",
            "db_path": os.path.relpath(args.db, ROOT),
            "name": args.table,
        }, indent=2))
        raise SystemExit(3)

    out = {
        "status": "OK",
        "db_path": os.path.relpath(args.db, ROOT),
        "name": args.table,
        "object_type": obj_type,
        "create_sql": sql,
        "columns": cols,
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()