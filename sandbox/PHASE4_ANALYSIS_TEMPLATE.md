# PHASE 4 ROOT-CAUSE ANALYSIS TEMPLATE

## Test Matrix Results Summary

| Stage | Processes | IDs/Proc | Total Ops | Wall-Clock (s) | IDs Generated | Throughput (IDs/s) | Status |
|-------|-----------|----------|-----------|----------------|---------------|--------------------|--------|
| A | 1 | 10 | 10 | 2.24 | 10 | 4.5 | ✓ |
| B | 2 | 10 | 20 | 3.85 | 20 | 5.2 | ✓ |
| C | 5 | 10 | 50 | 2.12 | 50 | 23.6 | ✓ |
| D | 10 | 10 | 100 | TBD | TBD | TBD | RUNNING |
| E | 20 | 10 | 200 | TBD | TBD | TBD | RUNNING |
| F-B | 2 | 50 | 100 | TBD | TBD | TBD | PLANNED |
| F-C | 5 | 50 | 250 | TBD | TBD | TBD | PLANNED |
| F-D | 10 | 50 | 500 | TBD | TBD | TBD | PLANNED |

## Analysis Questions

### Q1: Is There a Process Count Cliff?

**Hypothesis:** Performance degrades catastrophically at N processes

Expected if true: 
- Stages A-C smooth progression
- Stage D (10 procs) shows sharp degradation
- Stage E (20 procs) times out or very slow

Expected if false:
- Throughput continues improving or plateaus gracefully
- Linear degradation (not exponential)

### Q2: Does 20 Processes × 50 IDs Match Original Timeout?

**Hypothesis:** 20 × 50 IDs timeouts match original 20 × 100 thread test

Expected:
- 20 × 50 = 1000 operations
- If scales linearly with Stage C throughput: 1000 / 23.6 = 42.4 seconds
- If scales sub-linearly (worse contention): 100-200+ seconds
- If times out: suggests lock contention catastrophic at 20 procs

### Q3: Is the Original Test Harness Different?

**Key Difference:** Original used threading, not multiprocessing

Threading vs Multiprocessing:
- Threading: Shared memory, GIL contention, lock waits visible as delays
- Multiprocessing: Separate interpreters, true parallelism, OS scheduling
- SQLite with threading vs multiprocessing: Different contention patterns

### Q4: What's the Actual Bottleneck?

Observed so far:
- Lock acquisition: 0.2ms (negligible)
- COMMIT duration: 200-280ms (dominant in Stage A)
- Multi-process: parallelism improves throughput 5× at 5 processes

Remaining unknowns:
- Does lock wait increase exponentially at 10+ processes?
- Does COMMIT duration increase under high contention?
- Is there a process scheduling ceiling?

## Decision Criteria

### If Stages D-E Complete Normally:
- Continue with Stage F (50 IDs per process)
- Investigate: why does original test timeout if parallelism works?
- Hypothesis: Original test used threading, not multiprocessing
- Action: Test with threading module to reproduce original behavior

### If Stage D Times Out:
- Root cause confirmed: Process count > 10 causes timeout
- Evidence: Clear degradation cliff between 5 and 10 processes
- Remediation options:
  1. Limit process pool to 5 or fewer
  2. Extend timeout to accommodate 10+ process degradation
  3. Redesign counter algorithm to reduce lock contention

### If Stage E Times Out:
- Root cause confirmed: Process count = 20 causes timeout
- Evidence: Direct reproduction of original TEST 6 timeout
- Possible causes:
  1. SQLite lock serialization under 20 process load
  2. Disk I/O bottleneck (fsync) serializes all commits
  3. Process scheduling/OS resource limit
- Remediation: Combination of timeout extension + algorithm redesign

## What "Timeout" Means

If a stage times out:
1. p.join(timeout=120.0) expires
2. Some or all child processes may still be running
3. Results queue may be incomplete
4. No clear evidence of where execution stopped

This is different from a VERIFIED timeout at specific operation.

## Production Decision Gates

Once D-E results available:

1. **Root Cause Classification:**
   - VERIFIED: Measured data confirms cause
   - HYPOTHESIS: Pattern suggests cause but not conclusive
   - ENVIRONMENT-LIMITED: Cannot determine due to system characteristics

2. **Timeout Acceptability:**
   - Is 180s timeout insufficient? (H1)
   - Is lock contention severe? (H2)
   - Are there operational constraints? (scheduling, disk speed)

3. **Remediation Path:**
   - Timeout extension: Quick but treats symptom
   - Algorithm redesign: Complex but treats root cause
   - Hybrid: Extend timeout + reduce process count
