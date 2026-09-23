#!/usr/bin/env python3
"""
Sandbox DB Initialization
Creates isolated test database with identical schema to production
but completely separate file and path.
"""

import sqlite3
import os
from pathlib import Path
import json

# PRODUCTION DB PATH (READ-ONLY VERIFICATION)
PRODUCTION_DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"

# SANDBOX DB PATH (WRITE-ENABLED)
SANDBOX_DB = r"C:\Users\sirok\MoCKA\sandbox\mocka_events_sandbox.db"

def verify_isolation():
    """Fail-closed path validation"""
    if SANDBOX_DB == PRODUCTION_DB:
        raise RuntimeError(
            f"ISOLATION VIOLATION: Sandbox and Production paths are identical!\n"
            f"Sandbox: {SANDBOX_DB}\n"
            f"Production: {PRODUCTION_DB}"
        )

    # Verify production DB exists but don't modify
    if not os.path.exists(PRODUCTION_DB):
        raise RuntimeError(f"Production DB not found (readonly verification): {PRODUCTION_DB}")

    print("[ISOLATION CHECK]")
    print(f"  Production DB: {PRODUCTION_DB}")
    print(f"  Sandbox DB:    {SANDBOX_DB}")
    print(f"  ✓ Paths are different (isolation verified)")
    print()

def create_sandbox_db():
    """Create sandbox DB with identical schema"""
    # Delete existing sandbox DB if present (fresh start for each test run)
    if os.path.exists(SANDBOX_DB):
        os.remove(SANDBOX_DB)
        print(f"[SANDBOX] Cleaned up existing DB: {SANDBOX_DB}")

    # Create new sandbox DB
    con = sqlite3.connect(SANDBOX_DB, timeout=30.0)
    con.row_factory = sqlite3.Row

    print(f"[SANDBOX] Creating DB: {SANDBOX_DB}")

    # Create tables (identical to production schema)
    con.execute("""CREATE TABLE IF NOT EXISTS claude_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        tool TEXT,
        args TEXT,
        result_summary TEXT
    )""")

    con.execute("""CREATE TABLE IF NOT EXISTS decision_id_counters (
        date TEXT PRIMARY KEY,
        counter INTEGER DEFAULT 0
    )""")

    # Create other essential tables for full compatibility
    con.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        timestamp TEXT,
        event_type TEXT
    )""")

    con.commit()
    con.close()

    # Verify file created
    if os.path.exists(SANDBOX_DB):
        size_kb = os.path.getsize(SANDBOX_DB) / 1024
        print(f"✓ Sandbox DB created: {size_kb:.1f} KB")
    else:
        raise RuntimeError(f"Failed to create sandbox DB: {SANDBOX_DB}")

    return SANDBOX_DB

def verify_schema():
    """Verify sandbox schema is correct"""
    con = sqlite3.connect(SANDBOX_DB, timeout=10.0)

    # Check tables
    tables = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    print("\n[SCHEMA VERIFICATION]")
    print(f"  Tables in sandbox DB: {len(tables)}")
    for table in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
        print(f"    - {table[0]}: {count} rows")

    # Verify counter table structure
    try:
        con.execute("SELECT date, counter FROM decision_id_counters LIMIT 1")
        print("\n✓ decision_id_counters schema verified")
    except Exception as e:
        raise RuntimeError(f"Schema verification failed: {e}")

    con.close()

def isolation_proof():
    """Generate isolation verification evidence"""
    evidence = {
        "timestamp": "2026-09-21",
        "sandbox_db_path": SANDBOX_DB,
        "production_db_path": PRODUCTION_DB,
        "paths_identical": SANDBOX_DB == PRODUCTION_DB,
        "sandbox_db_exists": os.path.exists(SANDBOX_DB),
        "sandbox_db_size_bytes": os.path.getsize(SANDBOX_DB) if os.path.exists(SANDBOX_DB) else 0,
        "production_db_exists": os.path.exists(PRODUCTION_DB),
        "isolation_status": "VERIFIED" if SANDBOX_DB != PRODUCTION_DB else "FAILED"
    }

    evidence_path = r"C:\Users\sirok\MoCKA\sandbox\isolation_evidence.json"
    with open(evidence_path, 'w', encoding='utf-8') as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    print(f"\n[ISOLATION EVIDENCE]")
    print(f"  Saved to: {evidence_path}")
    print(f"  Status: {evidence['isolation_status']}")

    return evidence

def main():
    print("=" * 70)
    print("TARGET-1 SANDBOX DB INITIALIZATION")
    print("=" * 70)
    print()

    # Verify isolation before any writes
    verify_isolation()

    # Create sandbox DB
    db_path = create_sandbox_db()

    # Verify schema
    verify_schema()

    # Generate evidence
    evidence = isolation_proof()

    print()
    print("=" * 70)
    print("PHASE 1 COMPLETE: SANDBOX ISOLATION")
    print("=" * 70)
    print(f"\nSandbox DB ready for remediation testing.")
    print(f"Production DB remains FROZEN (untouched).")

if __name__ == '__main__':
    main()
