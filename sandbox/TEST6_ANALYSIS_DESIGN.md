# PHASE 4: TEST 6 ROOT-CAUSE ANALYSIS DESIGN

## Objective
Identify why original TARGET-1 test_target1_final.py Test 6 (20 threads × 100 IDs) timed out/incomplete.

## Evidence from TARGET-1 Audit
- Test 6: "Parallel 20 threads x 100 IDs" = 2000 concurrent operations
- Result: **INCOMPLETE** (no output captured)
- Connection timeout setting: **30.0 seconds**
- Production DB counter at 9348 suggests massive activity occurred
- Test 5 (10 threads × 50 = 500) PASSED with 0 duplicates
- Test 12 (5 threads × 100 = 500) PASSED in 31.93s at 16 IDs/sec

## Root-Cause Hypotheses

### H1: Insufficient Timeout Value (PLAUSIBLE)
- 2000 operations × average 30ms/op = 60 seconds
- 30-second timeout insufficient
- Evidence: Test 5 (500 ops) succeeded; Test 12 (500 ops) took 32s
- Extrapolating: 2000 ops might require 128 seconds

### H2: SQLite Lock Contention (LIKELY)
- 20 threads competing for single DB lock (BEGIN IMMEDIATE)
- Each transaction: INSERT → UPDATE → SELECT (3 statements)
- Lock held for entire transaction duration
- Under high contention: lock acquisition time >> transaction time
- Evidence: Production counter at 9348 (far exceeding expected ~500-1000 for tests)

### H3: Test Harness Issue (POSSIBLE)
- Output capture failure (ThreadPoolExecutor + Tee-Object interaction)
- Test completed but output lost
- Process actually succeeded, but results not captured

### H4: Connection Pool Exhaustion (LOW PROBABILITY)
- Python sqlite3 doesn't use connection pooling by default
- Each thread opens new connection
- 20 connections should be acceptable

### H5: Timeout During Lock Wait (POSSIBLE)
- Connection timeout applies to lock acquisition
- If any thread waits > 30s for lock, connection times out
- Cascading failures: timed-out thread → exception → test incomplete

## Investigation Plan (Sandbox)

### Step 1: Baseline Measurements
```
Test A: Single-threaded (1 thread × 100 IDs)
  - Expected: < 1 second
  - Measurement: actual time + counter final value

Test B: Sequential 2000 calls (single thread)
  - Expected: < 10 seconds
  - Measurement: time distribution, counter progression
```

### Step 2: Instrumentation
Add timing to decision ID generation:
```python
import time
start = time.time()
try:
    id_val = next_decision_id()
    elapsed = time.time() - start
    timings.append(elapsed)
except timeout_error:
    timedout_count += 1
```

Measure:
- Transaction time (begin → commit)
- Lock acquisition time
- Total ID generation time
- Exception frequency

### Step 3: Threading Tests (Progressive Load)
```
Test C: 2 threads × 100 IDs = 200 ops
  - Expected to complete, measure time

Test D: 5 threads × 100 IDs = 500 ops
  - Expected to complete, measure contention

Test E: 10 threads × 100 IDs = 1000 ops
  - Expected to complete, measure degradation

Test F: 20 threads × 100 IDs = 2000 ops
  - Monitor for timeout/completion
  - Measure lock contention if completes
```

### Step 4: Timeout Behavior Analysis
```
With timeout=30.0:
- Measure: How many threads hit timeout
- Measure: At what operation count timeout occurs
- Measure: Thread interleaving pattern

With timeout=120.0:
- Measure: Does test complete
- Measure: Actual required time
- If completes: is timeout the only issue
```

### Step 5: Lock Contention Quantification
```python
# Instrumented counter increment
start_lock = time.time()
con.execute("BEGIN IMMEDIATE")  # Measure time to acquire lock
lock_acquired = time.time()
# ... transaction ...
con.commit()
end = time.time()

lock_wait_time = lock_acquired - start_lock
transaction_time = end - lock_acquired
total_time = end - start_lock
```

## Expected Findings

### Most Likely: H1 + H2 Combined
- Timeout value insufficient for 2000 high-contention operations
- Average transaction time increases under contention
- 20 threads → 20× lock competition → serialization
- Solution: Either extend timeout or redesign counter increment

### Evidence Collection
For each test run, collect:
1. **Total time elapsed**
2. **Operations completed**
3. **Operations timed out**
4. **Lock wait times** (p50, p95, p99)
5. **Transaction times**
6. **Counter final value vs. expected**
7. **Exception type distribution**

## Success Criteria
- Root cause identified with supporting measurements
- Hypothesis confirmed or eliminated with evidence
- Recommendation for remediation (adjust timeout vs. redesign)
- NOT: "probably timeout" without measurement

## Scope Boundary
This investigation is IN SANDBOX ONLY.
- No production DB testing
- No production counter inspection
- No modifications to production code
