#!/usr/bin/env python3
"""Quick TARGET-1 verification"""

import sys
import datetime
sys.path.insert(0, '.')
from mocka_mcp_server import _next_decision_id, _read_decisions

print("TARGET-1 IMPLEMENTATION VERIFICATION")
print("=" * 60)

# Test 1: Format
print("\n[VERIFY 1] Format")
id1 = _next_decision_id()
print(f"Generated: {id1}")

parts = id1.split('_')
assert len(parts) == 3, "Wrong structure"
assert parts[0] == 'DC', "Wrong prefix"
assert len(parts[1]) == 8 and parts[1].isdigit(), "Wrong date"
assert len(parts[2]) == 3 and parts[2].isdigit(), "Wrong suffix"

today = datetime.date.today().strftime('%Y%m%d')
assert parts[1] == today, "Wrong date value"

print(f"✓ Format: DC_YYYYMMDD_NNN")

# Test 2: Monotonic
print("\n[VERIFY 2] Monotonicity")
ids = [_next_decision_id() for _ in range(5)]
nums = [int(x.split('_')[2]) for x in ids]
print(f"Sequence: {nums}")

for i in range(1, len(nums)):
    assert nums[i] > nums[i-1], f"Not monotonic: {nums[i-1]} vs {nums[i]}"

print(f"✓ Monotonic increment verified")

# Test 3: Existing ledger
print("\n[VERIFY 3] Existing Ledger")
records, broken = _read_decisions()
print(f"Total records: {len(records)}")
print(f"Broken: {broken}")
print(f"✓ Ledger readable")

# Test 4: Multi-threaded
print("\n[VERIFY 4] Multi-threaded Safety")
import threading

ids = []
lock = threading.Lock()

def gen():
    for _ in range(50):
        id_val = _next_decision_id()
        with lock:
            ids.append(id_val)

threads = [threading.Thread(target=gen) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

unique = len(set(ids))
dupes = len(ids) - unique

print(f"Generated: {len(ids)} IDs")
print(f"Duplicates: {dupes}")

assert dupes == 0, f"Collision detected: {dupes} duplicates"
print(f"✓ Zero collisions in multi-threaded access")

print("\n" + "=" * 60)
print("TARGET-1 = PASS")
print("=" * 60)
