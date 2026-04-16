import os
import sys
import sqlite3
import importlib
import inspect
from datetime import datetime, timezone

# sys.path fix for "import src...."
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(THIS_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DB_PATH_DEFAULT = r"audit\ed25519\audit.db"

def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def db_connect(db_path):
    con = sqlite3.connect(db_path)
    try:
        con.execute("PRAGMA foreign_keys=ON")
    except Exception:
        pass
    return con

def ensure_key_revocation(con):
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS key_revocation (
            key_id TEXT PRIMARY KEY,
            revoked_at TEXT NOT NULL,
            reason_code TEXT NOT NULL,
            reason_text TEXT,
            revoked_by TEXT NOT NULL,
            audit_event_id TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_key_revocation_revoked_at
        ON key_revocation(revoked_at)
        """
    )
    con.commit()

def upsert_revocation(con, key_id, revoked_at, reason_code, reason_text, revoked_by):
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO key_revocation(key_id, revoked_at, reason_code, reason_text, revoked_by, audit_event_id)
        VALUES(?,?,?,?,?,NULL)
        ON CONFLICT(key_id) DO UPDATE SET
          revoked_at=excluded.revoked_at,
          reason_code=excluded.reason_code,
          reason_text=excluded.reason_text,
          revoked_by=excluded.revoked_by
        """,
        (key_id, revoked_at, reason_code, reason_text, revoked_by),
    )
    con.commit()

def set_audit_event_id(con, key_id, audit_event_id):
    cur = con.cursor()
    cur.execute("UPDATE key_revocation SET audit_event_id=? WHERE key_id=?", (audit_event_id, key_id))
    con.commit()

def read_last_event_id_from_db(db_path):
    if not db_path or not os.path.exists(db_path):
        return ""
    con = sqlite3.connect(db_path)
    try:
        cur = con.cursor()
        row = cur.execute("SELECT event_id FROM audit_ledger_event ORDER BY created_at DESC LIMIT 1").fetchone()
        return str(row[0]) if row and row[0] else ""
    finally:
        con.close()

def find_audit_writer():
    candidates = [
        "src.mocka_audit.audit_writer",
        "src.mocka_audit_v2.audit_writer_v2",
    ]
    last_err = None
    for modname in candidates:
        try:
            mod = importlib.import_module(modname)
            for clsname in ["AuditWriter", "AuditWriterV2", "AuditWriterV1"]:
                if hasattr(mod, clsname):
                    return (modname, getattr(mod, clsname))
            for name in dir(mod):
                if name.lower().endswith("auditwriter"):
                    return (modname, getattr(mod, name))
        except Exception as e:
            last_err = e
    raise RuntimeError("AuditWriter import failed: %s" % str(last_err))

def construct_writer(WriterCls, db_path):
    for kwargs in [
        {"db_path": db_path},
        {"audit_db_path": db_path},
        {"audit_db": db_path},
        {"ledger_db_path": db_path},
        {"path": db_path},
    ]:
        try:
            return WriterCls(**kwargs)
        except Exception:
            pass
    try:
        return WriterCls(db_path)
    except Exception:
        pass
    try:
        sig = inspect.signature(WriterCls)
        raise RuntimeError("Cannot construct AuditWriter. ctor signature=%s" % str(sig))
    except Exception:
        raise RuntimeError("Cannot construct AuditWriter. ctor signature unknown")

def _extract_event_id_from_return(ret, db_path):
    if isinstance(ret, dict) and "event_id" in ret:
        return str(ret["event_id"])
    if isinstance(ret, tuple) and len(ret) >= 1 and ret[0]:
        return str(ret[0])
    if isinstance(ret, str) and ret:
        return ret
    return read_last_event_id_from_db(db_path)

def call_write_event(writer, event_dict, db_path):
    if not hasattr(writer, "write_event"):
        raise RuntimeError("AuditWriter has no write_event")

    m = getattr(writer, "write_event")

    # 1) try positional first (fast path)
    try:
        ret = m(event_dict)
        return _extract_event_id_from_return(ret, db_path)
    except Exception as pos_err:
        last_err = pos_err

    # 2) introspect signature, then call with correct kw name
    try:
        sig = inspect.signature(m)
        params = list(sig.parameters.values())
        # bound method: first is usually "self"; filter it out
        params = [p for p in params if p.name != "self"]

        # If it accepts **kwargs, we can use the most common "event" key safely
        if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params):
            try:
                ret = m(event=event_dict)
                return _extract_event_id_from_return(ret, db_path)
            except Exception as e:
                last_err = e

        # If exactly 1 param remains, use its name
        if len(params) == 1:
            pname = params[0].name
            try:
                ret = m(**{pname: event_dict})
                return _extract_event_id_from_return(ret, db_path)
            except Exception as e:
                last_err = e

        # If multiple params, try common one among them
        names = [p.name for p in params]
        for key in ["event", "event_dict", "event_content", "content"]:
            if key in names:
                try:
                    ret = m(**{key: event_dict})
                    return _extract_event_id_from_return(ret, db_path)
                except Exception as e:
                    last_err = e

        raise RuntimeError("write_event signature not matchable: %s" % str(sig))
    except Exception as e:
        # preserve last_err if it is more specific
        raise RuntimeError("write_event failed: %s" % str(last_err))

def main():
    # Usage:
    #   python tools/revoke_key_with_audit_event.py <key_id> [reason_code] [revoked_by] [reason_text] [db_path]
    if len(sys.argv) < 2:
        print("USAGE: python tools/revoke_key_with_audit_event.py <key_id> [reason_code] [revoked_by] [reason_text] [db_path]", file=sys.stderr)
        return 2

    key_id = sys.argv[1].strip()
    reason_code = sys.argv[2].strip() if len(sys.argv) >= 3 else "compromise"
    revoked_by = sys.argv[3].strip() if len(sys.argv) >= 4 else "operator"
    reason_text = sys.argv[4].strip() if len(sys.argv) >= 5 else "manual revoke"
    db_path = sys.argv[5] if len(sys.argv) >= 6 else DB_PATH_DEFAULT

    if not os.path.exists(db_path):
        print("DB NOT FOUND:", db_path, file=sys.stderr)
        return 3

    revoked_at = utc_now_iso()

    # 1) upsert revocation (audit_event_id NULL first)
    con = db_connect(db_path)
    try:
        ensure_key_revocation(con)
        upsert_revocation(con, key_id, revoked_at, reason_code, reason_text, revoked_by)
    finally:
        con.close()

    # 2) append audit ledger event
    modname, WriterCls = find_audit_writer()
    writer = construct_writer(WriterCls, db_path)

    event_dict = {
        "schema": "mocka.audit.revocation.v1",
        "action": "revoke",
        "key_id": key_id,
        "revoked_at": revoked_at,
        "reason_code": reason_code,
        "reason_text": reason_text,
        "revoked_by": revoked_by,
    }

    event_id = call_write_event(writer, event_dict, db_path)
    if not event_id:
        print("ERROR: audit event_id empty", file=sys.stderr)
        return 4

    # 3) write back audit_event_id
    con2 = db_connect(db_path)
    try:
        set_audit_event_id(con2, key_id, event_id)
    finally:
        con2.close()

    print("OK")
    print("writer_module:", modname)
    print("key_id:", key_id)
    print("revoked_at:", revoked_at)
    print("audit_event_id:", event_id)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())