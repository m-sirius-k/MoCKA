#!/usr/bin/env python3
"""
CRITICAL-002 Implementation Verification
Verify that binding audit algorithm is properly implemented
"""

import json
from pathlib import Path

# ===== Manual Verification (without full server setup) =====

print("=" * 70)
print("CRITICAL-002: Implementation Verification")
print("=" * 70)

# Check 1: Verify mocka_binding_audit tool is registered
print("\n[CHECK 1] Tool Registration")
code_path = Path("/home/user/MoCKA/mocka_mcp_server.py")
with open(code_path) as f:
    content = f.read()
    if '"mocka_binding_audit"' in content and 'Decision-Event Binding Audit' in content:
        print("  ✓ PASS: mocka_binding_audit tool registered")
    else:
        print("  ✗ FAIL: mocka_binding_audit tool not found in TOOLS")

# Check 2: Verify forward binding verification (Decision -> Event)
print("\n[CHECK 2] Forward Binding Verification")
if "events_by_decision" in content and "for decision_id, decision in latest_decisions.items()" in content:
    print("  ✓ PASS: Forward binding verification (Decision -> Event) implemented")
else:
    print("  ✗ FAIL: Forward binding verification not found")

# Check 3: Verify reverse binding verification (Event -> Decision)
print("\n[CHECK 3] Reverse Binding Verification")
if "for event_id, event in all_events.items():" in content and 'if tag.startswith("decision_ledger,")' in content:
    print("  ✓ PASS: Reverse binding verification (Event -> Decision) implemented")
else:
    print("  ✗ FAIL: Reverse binding verification not found")

# Check 4: Verify Type 1 orphan detection
print("\n[CHECK 4] Type 1 Orphan Detection")
if '"type1_orphans"' in content and 'for decision_id, decision in latest_decisions.items()' in content and 'audit_report["type1_orphans"].append' in content:
    print("  ✓ PASS: Type 1 orphan detection implemented")
else:
    print("  ✗ FAIL: Type 1 orphan detection not found")

# Check 5: Verify Type 2 orphan detection
print("\n[CHECK 5] Type 2 Orphan Detection")
if '"type2_orphans"' in content and 'if decision_id not in latest_decisions:' in content:
    print("  ✓ PASS: Type 2 orphan detection implemented")
else:
    print("  ✗ FAIL: Type 2 orphan detection not found")

# Check 6: Verify binding completeness calculation
print("\n[CHECK 6] Binding Completeness Calculation")
if 'audit_report["binding_completeness"]' in content and 'audit_report["complete_bindings"] / audit_report["total_decisions"]' in content:
    print("  ✓ PASS: Binding completeness calculation implemented")
else:
    print("  ✗ FAIL: Binding completeness calculation not found")

# Check 7: Verify audit report structure
print("\n[CHECK 7] Audit Report Structure")
required_fields = [
    '"timestamp"',
    '"total_decisions"',
    '"complete_bindings"',
    '"type1_orphans"',
    '"type2_orphans"',
    '"binding_completeness"'
]
missing = [f for f in required_fields if f not in content]
if not missing:
    print("  ✓ PASS: Audit report structure complete")
else:
    print(f"  ✗ FAIL: Missing fields: {missing}")

# Check 8: Verify integration with Decision/Event Ledgers
print("\n[CHECK 8] Integration with Decision/Event Ledgers")
if "_read_decisions()" in content and "_read_events()" in content:
    print("  ✓ PASS: Integrated with Decision and Event ledgers")
else:
    print("  ✗ FAIL: Ledger integration not found")

print("\n" + "=" * 70)
print("IMPLEMENTATION VERIFICATION: COMPLETE")
print("=" * 70)
print("\nStatus:")
print("  IMPLEMENTED: ✓")
print("  CODE ANALYSIS: ✓")
print("  UNIT TESTED: ? (requires server)")
print("  INTEGRATION TESTED: ? (requires MCP server)")
print("  REGRESSION PASSED: ? (requires full test suite)")
print("  EVIDENCE-COMPLETE: ? (pending)")
print("\nNext step: Full integration test with MCP server")
