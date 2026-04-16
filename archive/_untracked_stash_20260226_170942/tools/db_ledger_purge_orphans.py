import glob
import json
import os
import sqlite3

ROOT = os.getcwd()
AUDIT_DIR = os.path.join(ROOT, "audit")
RECOVERY_FILE = os.path.join(AUDIT_DIR, "recovery", "regenesis.json")

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
TABLE = "audit_ledger_event"
OUT_REPORT = os.path.join(AUDIT_DIR, "db_purge_report.txt")


def read_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_tip_from_regenesis():
    if not os.path.exists(RECOVERY_FILE):
        raise SystemExit(f"regenesis.json not found: {RECOVERY_FILE}")
    obj = read_json_file(RECOVERY_FILE)
    tip = obj.get("regensis_event_id")
    if not tip:
        raise SystemExit("regenesis.json missing regensis_event_id")
    return tip


def load_events_from_files():
    files = sorted(glob.glob(os.path.join(AUDIT_DIR, "*.json")))
    id_map = {}
    skipped = []

    for f in files:
        try:
            if os.path.getsize(f) == 0:
                skipped.append((f, "empty"))
                continue
            obj = read_json_file(f)
            if not isinstance(obj, dict):
                skipped.append((f, "not_object"))
                continue
            eid = obj.get("event_id")
            if not eid:
                skipped.append((f, "missing_event_id"))
                continue
            id_map[eid] = obj
        except Exception:
            skipped.append((f, "read_error"))

    return id_map, skipped


def reachable_set_from_tip(id_map, tip):
    reachable = set()
    cur = tip
    visited = set()

    while True:
        if cur in visited:
            raise SystemExit(f"cycle detected while tracing files from tip: {cur}")
        visited.add(cur)

        e = id_map.get(cur)
        if not e:
            raise SystemExit(f"tip not found in audit/*.json: {cur}")

        reachable.add(cur)

        prev = e.get("previous_event_id")
        if prev is None:
            break

        if prev in id_map:
            cur = prev
            continue

        break

    return reachable


def main():
    tip = load_tip_from_regenesis()
    id_map, skipped = load_events_from_files()
    reachable = reachable_set_from_tip(id_map, tip)

    if not os.path.exists(DB_PATH):
        raise SystemExit(f"DB not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
        before_count = int(cur.fetchone()[0])

        cur.execute(f"SELECT event_id FROM {TABLE}")
        db_ids = [r[0] for r in cur.fetchall()]

        to_delete = [eid for eid in db_ids if eid not in reachable]

        for eid in to_delete:
            cur.execute(f"DELETE FROM {TABLE} WHERE event_id = ?", (eid,))

        conn.commit()

        cur.execute(f"SELECT COUNT(*) FROM {TABLE}")
        after_count = int(cur.fetchone()[0])

    finally:
        conn.close()

    lines = []
    lines.append("DB ledger purge report")
    lines.append(f"db_path: {DB_PATH}")
    lines.append(f"table: {TABLE}")
    lines.append(f"tip: {tip}")
    lines.append(f"reachable_count_from_files: {len(reachable)}")
    lines.append(f"db_rows_before: {before_count}")
    lines.append(f"db_rows_after: {after_count}")
    lines.append(f"deleted_count: {len(to_delete)}")
    if skipped:
        lines.append("skipped_files:")
        for p, reason in skipped:
            lines.append(f"  - {p} : {reason}")
    if to_delete:
        lines.append("deleted_event_ids:")
        for eid in to_delete:
            lines.append(f"  - {eid}")

    os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"OK: deleted_count={len(to_delete)}")
    print(f"OK: db_rows_before={before_count} db_rows_after={after_count}")
    print(f"OK: report={OUT_REPORT}")


if __name__ == "__main__":
    main()