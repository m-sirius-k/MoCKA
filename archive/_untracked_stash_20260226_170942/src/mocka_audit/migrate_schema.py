"""
MoCKA Phase10
Canonical DB path unification for schema migration.
"""

import os
from src.mocka_audit.db_schema import (
    connect,
    ensure_schema_versions,
    ensure_audit_ledger_table,
)

# === Phase10 Canonical DB Path (Single Source of Truth) ===
CANONICAL_DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"


def resolve_db_path() -> str:
    """
    Single resolution rule:
    1. MOCKA_AUDIT_DB_PATH env (if explicitly set)
    2. Canonical DB path
    """
    return os.environ.get("MOCKA_AUDIT_DB_PATH", CANONICAL_DB_PATH)


def main():
    db_path = resolve_db_path()
    print("db:", db_path)

    conn = connect(db_path)
    try:
        ensure_schema_versions(conn)
        ensure_audit_ledger_table(conn)
        print("OK: schema up-to-date")
    finally:
        conn.close()


if __name__ == "__main__":
    main()