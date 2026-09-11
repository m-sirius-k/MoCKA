#!/usr/bin/env python3
"""
CRITICAL-002: Simulate Decision-Event Binding Audit
Test orphan detection, binding verification, and recovery procedures
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

# Simulate ledger and event store
LEDGER_PATH = Path("/tmp/test_decision_ledger_002.jsonl")
EVENT_STORE_PATH = Path("/tmp/test_event_store_002.jsonl")

def simulate_decision(decision_id, title, status="Active"):
    """Write decision to ledger"""
    record = {
        "decision_id": decision_id,
        "title": title,
        "status": status,
        "approved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "maker": "test_authority",
        "decision": "Accept",
        "rationale": f"Rationale for {decision_id}"
    }
    with open(LEDGER_PATH, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return decision_id

def simulate_event(event_id, decision_id):
    """Write event to event store with decision_ledger tag"""
    record = {
        "event_id": event_id,
        "decision_id": decision_id,
        "tags": [f"decision_ledger,{decision_id}"],
        "title": f"Event for {decision_id}",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "authority": "test_authority"
    }
    with open(EVENT_STORE_PATH, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return event_id

def binding_audit():
    """
    Binding verification algorithm (CRITICAL-002)
    Returns: audit report with orphan detection
    """
    audit_report = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_decisions": 0,
        "complete_bindings": 0,
        "type1_orphans": [],  # Decision without Event
        "type2_orphans": [],  # Event without Decision
        "binding_completeness": 0.0
    }

    # Load all decisions
    decisions = {}
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH) as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    did = record.get("decision_id")
                    if did:
                        decisions[did] = record

    audit_report["total_decisions"] = len(decisions)

    # Load all events with decision_ledger tag
    events_by_decision = defaultdict(list)
    all_events = {}
    if EVENT_STORE_PATH.exists():
        with open(EVENT_STORE_PATH) as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    eid = record.get("event_id")
                    all_events[eid] = record

                    # Extract decision_id from tags
                    tags = record.get("tags", [])
                    for tag in tags:
                        if tag.startswith("decision_ledger,"):
                            decision_id = tag.split(",")[1]
                            events_by_decision[decision_id].append(eid)

    # FORWARD CHECK: Decision -> Event (find Type 1 orphans)
    for decision_id, decision in decisions.items():
        if decision_id in events_by_decision and len(events_by_decision[decision_id]) > 0:
            audit_report["complete_bindings"] += 1
        else:
            # Type 1 orphan: Decision exists but no Event
            audit_report["type1_orphans"].append({
                "decision_id": decision_id,
                "decision_timestamp": decision.get("approved_at"),
                "title": decision.get("title"),
                "status": decision.get("status")
            })

    # REVERSE CHECK: Event -> Decision (find Type 2 orphans)
    for event_id, event in all_events.items():
        tags = event.get("tags", [])
        for tag in tags:
            if tag.startswith("decision_ledger,"):
                decision_id = tag.split(",")[1]
                if decision_id not in decisions:
                    # Type 2 orphan: Event exists but no Decision
                    audit_report["type2_orphans"].append({
                        "event_id": event_id,
                        "decision_id": decision_id,
                        "event_timestamp": event.get("timestamp"),
                        "title": event.get("title")
                    })

    # Calculate binding completeness
    if audit_report["total_decisions"] > 0:
        audit_report["binding_completeness"] = (
            audit_report["complete_bindings"] / audit_report["total_decisions"] * 100
        )

    return audit_report

# Clean up
if LEDGER_PATH.exists():
    LEDGER_PATH.unlink()
if EVENT_STORE_PATH.exists():
    EVENT_STORE_PATH.unlink()

print("=" * 70)
print("CRITICAL-002: Decision-Event Binding Audit")
print("=" * 70)

# ===== Test 1: Complete Binding =====
print("\n[TEST 1] Complete Binding (Decision + Event)")
simulate_decision("DC_TEST_001", "Complete Decision")
simulate_event("E_TEST_001", "DC_TEST_001")
audit = binding_audit()
assert audit["complete_bindings"] == 1, f"Expected 1 complete, got {audit['complete_bindings']}"
assert len(audit["type1_orphans"]) == 0, f"Expected 0 Type1 orphans, got {len(audit['type1_orphans'])}"
print(f"  ✓ PASS: Binding complete ({audit['binding_completeness']:.1f}%)")

# ===== Test 2: Type 1 Orphan (Decision without Event) =====
print("\n[TEST 2] Type 1 Orphan Detection (Decision without Event)")
simulate_decision("DC_TEST_002", "Orphaned Decision")
audit = binding_audit()
assert len(audit["type1_orphans"]) == 1, f"Expected 1 Type1 orphan, got {len(audit['type1_orphans'])}"
assert audit["type1_orphans"][0]["decision_id"] == "DC_TEST_002"
print(f"  ✓ PASS: Type 1 orphan detected: {audit['type1_orphans'][0]['decision_id']}")

# ===== Test 3: Type 2 Orphan (Event without Decision) =====
print("\n[TEST 3] Type 2 Orphan Detection (Event without Decision)")
simulate_event("E_TEST_003", "DC_TEST_003")  # Decision never created
audit = binding_audit()
assert len(audit["type2_orphans"]) == 1, f"Expected 1 Type2 orphan, got {len(audit['type2_orphans'])}"
assert audit["type2_orphans"][0]["decision_id"] == "DC_TEST_003"
print(f"  ✓ PASS: Type 2 orphan detected: {audit['type2_orphans'][0]['decision_id']}")

# ===== Test 4: Binding Completeness =====
print("\n[TEST 4] Binding Completeness Calculation")
# Current state: 2 decisions (DC_TEST_001, DC_TEST_002)
# 2 events (E_TEST_001 -> DC_TEST_001, E_TEST_003 -> DC_TEST_003)
# 1 complete binding, 1 type1 orphan, 1 type2 orphan
audit = binding_audit()
expected_completeness = 50.0  # 1 complete out of 2 decisions
print(f"  Total decisions: {audit['total_decisions']}")
print(f"  Complete bindings: {audit['complete_bindings']}")
print(f"  Type 1 orphans: {len(audit['type1_orphans'])}")
print(f"  Type 2 orphans: {len(audit['type2_orphans'])}")
print(f"  Binding completeness: {audit['binding_completeness']:.1f}%")
assert audit["total_decisions"] == 2
assert audit["complete_bindings"] == 1
assert len(audit["type1_orphans"]) == 1
assert len(audit["type2_orphans"]) == 1
print(f"  ✓ PASS: Completeness metrics verified")

# ===== Test 5: Recovery Simulation (Type 1) =====
print("\n[TEST 5] Recovery Procedure (Type 1 Orphan)")
# Simulate recovery: create event for orphaned decision
orphaned_did = audit["type1_orphans"][0]["decision_id"]
recovery_event_id = f"E_RECOVERY_{orphaned_did}"
simulate_event(recovery_event_id, orphaned_did)
audit_after = binding_audit()
print(f"  Before recovery: {len(audit['type1_orphans'])} Type 1 orphans")
print(f"  After recovery: {len(audit_after['type1_orphans'])} Type 1 orphans")
assert len(audit_after["type1_orphans"]) == 0, "Type 1 orphan should be recovered"
assert audit_after["complete_bindings"] == 2, "Should have 2 complete bindings now"
print(f"  ✓ PASS: Type 1 orphan recovered via event creation")

# ===== Test 6: Audit Report Consistency =====
print("\n[TEST 6] Audit Report Consistency")
final_audit = binding_audit()
print(f"  Final state:")
print(f"    Total decisions: {final_audit['total_decisions']}")
print(f"    Complete bindings: {final_audit['complete_bindings']}")
print(f"    Type 1 orphans: {len(final_audit['type1_orphans'])}")
print(f"    Type 2 orphans: {len(final_audit['type2_orphans'])}")
print(f"    Binding completeness: {final_audit['binding_completeness']:.1f}%")
assert final_audit['total_decisions'] == 2
assert final_audit['complete_bindings'] == 2
assert len(final_audit['type1_orphans']) == 0
assert len(final_audit['type2_orphans']) == 1  # E_TEST_003 orphan still exists
assert final_audit['binding_completeness'] == 100.0  # 2 out of 2 decisions now complete
print(f"  ✓ PASS: Audit report consistent and accurate")

print("\n" + "=" * 70)
print("SIMULATION RESULTS: ALL TESTS PASSED")
print("=" * 70)
print("\nImplementation Evidence:")
print("  ✓ Forward binding verification (Decision → Event) implemented")
print("  ✓ Reverse binding verification (Event → Decision) implemented")
print("  ✓ Type 1 orphan detection (Decision without Event) verified")
print("  ✓ Type 2 orphan detection (Event without Decision) verified")
print("  ✓ Binding completeness calculation verified")
print("  ✓ Recovery procedure (create event) simulated and verified")
print("  ✓ Audit report consistency validated")
print("\nNext: Implement mocka_binding_audit() MCP tool in mocka_mcp_server.py")
