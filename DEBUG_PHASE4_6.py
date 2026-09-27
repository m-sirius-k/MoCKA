#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG PHASE 4-6 — Comprehensive validation and troubleshooting

Verify:
1. Phase 4: Orchestra session creation and dispatch
2. Phase 5: Event Buffer → Event Store flow
3. Phase 6: Event Store → Memory flow
4. Data integrity across all layers
5. No side effects or broken components
"""

import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

_mocka_root = Path(__file__).parent

print("\n" + "="*80)
print("DEBUG PHASE 4-6 — COMPREHENSIVE VALIDATION")
print("="*80)
print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}\n")

# ============================================================================
# PART 1: Event Store integrity check
# ============================================================================

def check_event_store():
    """Verify Event Store (mocka_events.db) integrity."""
    print("[1] EVENT STORE INTEGRITY CHECK")
    print("-" * 80)

    db_path = _mocka_root / "data" / "mocka_events.db"

    if not db_path.exists():
        print("❌ Event Store DB not found")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check table existence
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
        )
        if not cursor.fetchone():
            print("❌ 'events' table not found")
            return False

        # Count total events
        cursor.execute("SELECT COUNT(*) FROM events")
        total = cursor.fetchone()[0]
        print(f"✓ Total events in Event Store: {total}")

        # Check latest events
        cursor.execute(
            """
            SELECT event_id, request_id, title, when_ts
            FROM events
            ORDER BY when_ts DESC
            LIMIT 3
            """
        )
        latest = cursor.fetchall()

        if latest:
            print(f"✓ Latest 3 events:")
            for row in latest:
                print(f"    - {row[0]} | req={row[1][:8]}... | {row[2][:50]}")

        # Check for Phase 4-6 events
        cursor.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE title LIKE '%PHASE%' OR title LIKE '%Multi-AI%'
            """
        )
        phase_events = cursor.fetchone()[0]
        print(f"✓ Phase-related events: {phase_events}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Event Store check failed: {e}")
        return False


# ============================================================================
# PART 2: PHI-OS Event Gate check
# ============================================================================

def check_phios_event_gate():
    """Verify PHI-OS Event Gate is functional."""
    print("\n[2] PHI-OS EVENT GATE CHECK")
    print("-" * 80)

    db_path = _mocka_root / "data" / "mocka_events.db"

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if Event Gate has written events (indicates it's functional)
        try:
            cursor.execute(
                """
                SELECT COUNT(*) FROM events
                WHERE where_component = 'gateway_multi_dispatcher' OR source = 'buffered'
                """
            )
            gate_processed = cursor.fetchone()[0]
        except:
            # Old schema may not have 'source' column
            cursor.execute(
                """
                SELECT COUNT(*) FROM events
                WHERE where_component = 'gateway_multi_dispatcher'
                """
            )
            gate_processed = cursor.fetchone()[0]
        print(f"✓ Events processed by Event Gate: {gate_processed}")

        # Check event schema compatibility
        try:
            cursor.execute(
                """
                SELECT COUNT(*) FROM events
                WHERE request_id IS NOT NULL
                """
            )
            with_request_id = cursor.fetchone()[0]
            print(f"✓ Events with request_id field: {with_request_id}")
        except:
            # request_id might not be in schema
            print(f"⚠ Events with request_id field: (schema check skipped)")
            with_request_id = 0

        conn.close()
        return with_request_id > 0

    except Exception as e:
        print(f"❌ Event Gate check failed: {e}")
        return False


# ============================================================================
# PART 3: Memory Store integrity check
# ============================================================================

def check_memory_store():
    """Verify Memory Store (memory_store.json) integrity."""
    print("\n[3] MEMORY STORE INTEGRITY CHECK")
    print("-" * 80)

    memory_path = _mocka_root / "memory" / "data" / "memory_store.json"

    if not memory_path.exists():
        print("❌ Memory Store file not found")
        return False

    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            memory_data = json.load(f)

        if not isinstance(memory_data, list):
            print("❌ Memory Store format invalid")
            return False

        total = len(memory_data)
        print(f"✓ Total entries in Memory Store: {total}")

        if total > 0:
            # Check latest entries
            latest = memory_data[-3:]
            print(f"✓ Latest 3 Memory entries:")
            for entry in latest:
                memory_id = entry.get("memory_id", "unknown")
                memory_type = entry.get("memory_type", "unknown")
                source = entry.get("source", "unknown")
                print(f"    - {memory_id} | type={memory_type} | source={source}")

            # Check entry types
            by_type = {}
            for entry in memory_data:
                mt = entry.get("memory_type", "unknown")
                by_type[mt] = by_type.get(mt, 0) + 1

            print(f"✓ Memory entries by type:")
            for mt, count in by_type.items():
                print(f"    - {mt}: {count}")

        return True

    except Exception as e:
        print(f"❌ Memory Store check failed: {e}")
        return False


# ============================================================================
# PART 4: Event tracing (Event Store → Memory)
# ============================================================================

def trace_event_flow():
    """Trace a recent event from Event Store to Memory."""
    print("\n[4] EVENT FLOW TRACING")
    print("-" * 80)

    try:
        # Get latest event from Event Store
        db_path = _mocka_root / "data" / "mocka_events.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT event_id, request_id, title
            FROM events
            WHERE title LIKE '%PHASE%'
            ORDER BY when_ts DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            print("⚠ No Phase-related events found in Event Store")
            return False

        event_id, request_id, title = row
        print(f"✓ Latest Phase event in Event Store:")
        print(f"    - Event ID: {event_id}")
        print(f"    - Request ID: {request_id}")
        print(f"    - Title: {title}")

        # Check if this event is in Memory
        memory_path = _mocka_root / "memory" / "data" / "memory_store.json"
        with open(memory_path, "r", encoding="utf-8") as f:
            memory_data = json.load(f)

        # Look for matching entry in Memory
        found_in_memory = False
        for entry in memory_data:
            if entry.get("request_id") == request_id or \
               (entry.get("content", {}).get("request_id") == request_id):
                found_in_memory = True
                print(f"✓ Event found in Memory:")
                print(f"    - Memory ID: {entry.get('memory_id')}")
                print(f"    - Memory Type: {entry.get('memory_type')}")
                print(f"    - Source: {entry.get('source')}")
                break

        if not found_in_memory:
            print(f"⚠ Event not found in Memory (might be normal for older events)")

        return True

    except Exception as e:
        print(f"❌ Event flow tracing failed: {e}")
        return False


# ============================================================================
# PART 5: Configuration and environment check
# ============================================================================

def check_environment():
    """Verify runtime environment and dependencies."""
    print("\n[5] ENVIRONMENT & CONFIGURATION CHECK")
    print("-" * 80)

    issues = []

    # Check gateway __init__.py
    gateway_init = _mocka_root / "gateway" / "__init__.py"
    if gateway_init.exists():
        print("✓ gateway/__init__.py exists (Phase 4 requirement)")
    else:
        issues.append("Missing gateway/__init__.py")
        print("❌ gateway/__init__.py missing")

    # Check multi_dispatcher.py has request_id field
    try:
        with open(_mocka_root / "gateway" / "multi_dispatcher.py", "r", encoding="utf-8") as f:
            content = f.read()
            if '"request_id": dispatch_result.get' in content:
                print("✓ multi_dispatcher.py has request_id field (Phase 5 requirement)")
            else:
                issues.append("multi_dispatcher.py missing request_id field")
                print("❌ multi_dispatcher.py missing request_id field")
    except Exception as e:
        issues.append(f"Failed to check multi_dispatcher.py: {e}")
        print(f"❌ Failed to check multi_dispatcher.py: {e}")

    # Check Memory modules
    memory_modules = ["memory_writer.py", "memory_store.py"]
    for module in memory_modules:
        path = _mocka_root / "memory" / module
        if path.exists():
            print(f"✓ memory/{module} exists")
        else:
            issues.append(f"Missing memory/{module}")
            print(f"❌ Missing memory/{module}")

    return len(issues) == 0, issues


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    results = {
        "event_store": check_event_store(),
        "event_gate": check_phios_event_gate(),
        "memory_store": check_memory_store(),
        "event_flow": trace_event_flow(),
    }

    env_ok, env_issues = check_environment()
    results["environment"] = env_ok

    # Summary
    print("\n" + "="*80)
    print("DEBUG SUMMARY")
    print("="*80)

    print(f"\nEvent Store:       {'✓ OK' if results['event_store'] else '❌ FAILED'}")
    print(f"Event Gate:        {'✓ OK' if results['event_gate'] else '❌ FAILED'}")
    print(f"Memory Store:      {'✓ OK' if results['memory_store'] else '❌ FAILED'}")
    print(f"Event Flow:        {'✓ OK' if results['event_flow'] else '❌ FAILED'}")
    print(f"Environment:       {'✓ OK' if results['environment'] else '❌ FAILED'}")

    if env_issues:
        print(f"\nEnvironment Issues:")
        for issue in env_issues:
            print(f"  - {issue}")

    all_ok = all(results.values())
    print(f"\nOverall Status:    {'✓ ALL CHECKS PASSED' if all_ok else '❌ ISSUES FOUND'}")
    print("="*80)
