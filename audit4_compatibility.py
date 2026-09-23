#!/usr/bin/env python3
"""AUDIT-4: Backward Compatibility Analysis"""

print("BACKWARD COMPATIBILITY AUDIT")
print("=" * 60)

# Old format: DC_YYYYMMDD_NNN (all numeric suffix)
# New format: DC_YYYYMMDD_TTTTTTTTTTXX (9 digits + 4 hex suffix)

print("\nFORMAT COMPARISON:")
print("-" * 60)
print("Old: DC_YYYYMMDD_NNN")
print("     Example: DC_20260705_001")
print("     Suffix: 3 digits (all numeric)")
print()
print("New: DC_YYYYMMDD_TTTTTTTTTTXX")
print("     Example: DC_20260921_462773700df95")
print("     Suffix: 13 chars (9 digits + 4 hex)")

print("\n\nREADER COMPATIBILITY CHECK:")
print("-" * 60)

# Simulate old code behavior
def old_format_parser(decision_id):
    """How old _next_decision_id() parses IDs"""
    parts = decision_id.split('_')
    if len(parts) != 3:
        return None
    if parts[0] != 'DC':
        return None
    if not parts[1].isdigit() or len(parts[1]) != 8:
        return None

    # This checks .isdigit() on suffix
    if parts[2].isdigit():
        return int(parts[2])
    else:
        return None

# Test cases
test_ids = [
    ("DC_20260705_001", "old format"),
    ("DC_20260705_002", "old format"),
    ("DC_20260921_462773700df95", "new format"),
    ("DC_20260921_000000000ab", "new format lowercase"),
]

print("\nOLD CODE PARSING RESULTS:")
for decision_id, label in test_ids:
    result = old_format_parser(decision_id)
    if result is not None:
        print(f"  ✓ {decision_id:30} ({label:15}) → parsed as {result}")
    else:
        print(f"  ✗ {decision_id:30} ({label:15}) → SKIPPED (not numeric)")

print("\n\nIMPACT ANALYSIS:")
print("-" * 60)
print("Scenario 1: Old code reading ledger with mixed IDs")
print("  - Old format IDs: Parsed as integers (used for max(used))")
print("  - New format IDs: Skipped (hex suffix fails .isdigit())")
print("  - Result: max(used) only considers old IDs")
print("  - Verdict: INCOMPATIBLE - new IDs ignored in collision check")
print()
print("Scenario 2: Collision detection")
print("  - Old code: max(old_ids) + 1 = next ID")
print("  - New code: time-based + random")
print("  - If old code runs after new code generates ID:")
print("    → Old code doesn't see new ID (hex fails .isdigit())")
print("    → Old code might generate same 3-digit suffix")
print("    → DIFFERENT full ID but confusion risk")
print("  - Verdict: HIGH RISK of mixing logic")

print("\n\nREADER FUNCTION ANALYSIS:")
print("-" * 60)
print("_read_decisions() function:")
print("  - Reads all records from JSONL")
print("  - No parsing of decision_id (just returns raw)")
print("  - Result: CAN read both old and new formats")
print()
print("_next_decision_id() function:")
print("  - Old version: Reads all IDs, parses numeric suffixes only")
print("  - New version: Uses time, doesn't read existing IDs")
print("  - Result: No conflict (different algorithms)")

print("\n\nCOMPOUND COMPATIBILITY:")
print("-" * 60)
print("If BOTH old and new code run in same system:")
print()
print("Sequence A: Old code runs, then new code")
print("  1. Old: DC_20260921_001, 002")
print("  2. New: DC_20260921_000000000XX")
print("  3. Next old call: max(001, 002) + 1 = 003")
print("  Result: No collision")
print()
print("Sequence B: New code runs, then old code")
print("  1. New: DC_20260921_462750000AB")
print("  2. Old runs: doesn't see new ID (hex suffix)")
print("  3. Old generates: DC_20260921_001")
print("  Result: Different full ID, but mixing is fragile")
print()
print("Verdict: MIXING BOTH GENERATORS IS RISKY")

print("\n\nFINAL VERDICT:")
print("=" * 60)
print("Reading existing data: YES (format-compatible)")
print("Writing new data: CONDITIONAL")
print("Mixing old+new generators: NO (unsafe)")
print()
print("Classification: READ COMPATIBLE ONLY")
