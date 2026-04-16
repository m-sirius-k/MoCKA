import os
import sys
import sqlite3
from datetime import datetime

# Default DB (authoritative)
DEFAULT_DB_PATH = r"audit\ed25519\audit.db"

def eprint(*args):
    print(*args, file=sys.stderr)

def read_all_schema(cur):
    user_version = cur.execute("PRAGMA user_version;").fetchone()

    tables = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    ).fetchall()]

    schema_objects = cur.execute(
        """
        SELECT type, name, sql
        FROM sqlite_master
        WHERE type IN ('table','index','trigger','view')
        ORDER BY type, name;
        """
    ).fetchall()

    return user_version, tables, schema_objects

def format_output(db_path, user_version, tables, schema_objects):
    lines = []
    lines.append("=== DB PATH ===")
    lines.append(db_path)

    lines.append("\n=== PRAGMA user_version ===")
    lines.append(str(user_version))

    lines.append("\n=== TABLE LIST ===")
    if tables:
        lines.extend(tables)
    else:
        lines.append("(no tables)")

    lines.append("\n=== FULL SCHEMA ===")
    for obj_type, name, sql in schema_objects:
        lines.append(f"\n-- {obj_type} {name}")
        lines.append(sql if sql else "(sql is null)")
    return "\n".join(lines) + "\n"

def main():
    # Usage:
    #   python tools/dump_schema.py
    #   python tools/dump_schema.py path\to\dbfile.db
    #   python tools/dump_schema.py path\to\dbfile.db out\schema.txt
    db_path = DEFAULT_DB_PATH
    out_path = None

    if len(sys.argv) >= 2:
        db_path = sys.argv[1]
    if len(sys.argv) >= 3:
        out_path = sys.argv[2]

    if not os.path.exists(db_path):
        eprint("DB NOT FOUND:", db_path)
        eprint("HINT: run in repo root, or pass explicit path as argv[1].")
        return 1

    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        user_version, tables, schema_objects = read_all_schema(cur)
        out_text = format_output(db_path, user_version, tables, schema_objects)
    finally:
        con.close()

    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(out_text)
        print("WROTE:", out_path)
    else:
        print(out_text, end="")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())