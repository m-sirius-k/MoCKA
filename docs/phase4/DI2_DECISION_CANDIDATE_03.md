# Decision Candidate 3: DI2 Gate Timeout and Stuck Gate Handling

**Candidate ID**: DI2_DC_03_20260820  
**Related**: DI2_DI2_UNKNOWN_LIST.md - Unknown 2.4  
**Status**: CANDIDATE (awaiting Human Gate decision)  
**Created**: 2026-08-20  
**For**: Human Gate (博士)

---

## The Decision

When a gate is executing but never completes, the system must decide: how long to wait before treating it as "stuck" and triggering failure recovery?

**What This Decision Determines**:
- Maximum timeout per gate type (or global timeout)
- When to stop waiting and treat gate as failed
- Impact on system responsiveness vs. tolerance for slow operations

---

## The Problem: Stuck Gates

A gate could be stuck for several reasons:

1. **Temporary network issue**: Service momentarily unreachable (transient, will recover)
2. **Slow service**: Service responding slowly but will eventually respond (slow, not stuck)
3. **Deadlock**: Service is deadlocked and will never respond (stuck, needs recovery)
4. **Resource exhaustion**: System out of memory/disk (stuck, needs recovery)
5. **Bug**: Gate code infinite loop (stuck, needs recovery)

**Challenge**: How to distinguish transient from permanent without knowing root cause?

**Time Sensitivity**:
- Too short timeout (1-5s): False positives (legitimate slow operations mistaken for stuck)
- Too long timeout (5min+): Slow failure detection (stuck gates block operations for minutes)
- No timeout: System could wait indefinitely (worst case)

---

## Current Design (Default Recommendation)

### Exponential Backoff Retry Strategy

```
Gate Execution:
  ├─ Attempt 1: Call gate (max 1 second)
  ├─ Timeout? → Retry with backoff
  ├─ Retry 1: Wait 1s, call gate (max 1 second)
  ├─ Timeout? → Retry with backoff
  ├─ Retry 2: Wait 2s, call gate (max 1 second)
  ├─ Timeout? → Retry with backoff
  ├─ Retry 3: Wait 4s, call gate (max 1 second)
  ├─ Timeout? → Gate stuck, fail
  └─ Max total time: ~8 seconds (1 + 1 + 2 + 4)
```

### Rationale

- **Short per-call timeout** (1s): Catches genuine stuck gates quickly
- **Exponential backoff**: Gives transient issues time to recover
- **Max 3 retries**: Limits total waiting time to ~8 seconds
- **Max total time**: 8 seconds is reasonable for gate recovery

### Pros

- **Responsive**: Stuck gates detected within ~8 seconds
- **Tolerant**: Transient issues get multiple chances
- **Balanced**: Not too aggressive, not too passive

### Cons

- **Per-gate timeout not tunable**: All gates same 1s timeout
- **Backoff assumes transient**: If issue is permanent, delays won't help
- **Could still be slow**: 8 seconds is long for some operations

---

## Option A: Default (Recommended)

### Per-Call Timeout: 1 second, Max Retries: 3

```
Total time bound: ~8 seconds
├─ Call 1: 0s + 1s timeout = 1s
├─ Call 2: 1s + 1s timeout = 2s
├─ Call 3: 3s + 1s timeout = 4s
└─ Call 4: 7s + 1s timeout = 8s
```

### When to Use

- Works for most gates
- Tolerable latency for operations
- Balanced timeout strategy

### Pros

- **Simple**: Same timeout for all gates
- **Predictable**: Known max latency (8s)
- **Reasonable**: 1s per call is not too short

### Cons

- **Not granular**: Some gates might need different timeout
- **Fixed backoff**: Doesn't adapt to gate characteristics

### Recommendation

✓ **RECOMMENDED** - Default, reasonable for most gates

---

## Option B: Short Timeout (Aggressive)

### Per-Call Timeout: 100ms, Max Retries: 3

```
Total time bound: ~800ms
├─ Call 1: 0ms + 100ms timeout = 100ms
├─ Call 2: 100ms + 100ms timeout = 200ms
├─ Call 3: 300ms + 100ms timeout = 400ms
└─ Call 4: 700ms + 100ms timeout = 800ms
```

### When to Use

- Only for fast gates (tools that should respond in <100ms)
- Operations that need quick failure detection

### Pros

- **Fast failure detection**: Stuck gates caught quickly
- **Low latency**: Operations fail fast, no long waiting
- **Responsive**: Better user experience (no long hangs)

### Cons

- **False positives**: Legitimate 500ms operations treated as stuck
- **Too strict**: Network latency alone could trigger timeout
- **Retry won't help**: If issue is network, exponential backoff won't fix it

### Recommendation

❌ **NOT RECOMMENDED** - Too aggressive, risk of false positives

---

## Option C: Long Timeout (Conservative)

### Per-Call Timeout: 5 seconds, Max Retries: 3

```
Total time bound: ~45 seconds
├─ Call 1: 0s + 5s timeout = 5s
├─ Call 2: 5s + 5s timeout = 10s
├─ Call 3: 15s + 5s timeout = 20s
└─ Call 4: 35s + 5s timeout = 40s
```

### When to Use

- Slow operations (e.g., large file processing)
- Gates that legitimately take time

### Pros

- **Tolerant**: Slow operations get time to complete
- **Low false positive rate**: Rarely mistaken for stuck

### Cons

- **Long failure detection**: Stuck gates detected after 40 seconds
- **High latency**: Operations wait a very long time
- **Not responsive**: Bad user experience (long hangs)

### Recommendation

❌ **NOT RECOMMENDED** - Too conservative, operations block too long

---

## Option D: Per-Gate Timeout (Granular)

### Different Timeout per Gate Type

| Gate Type | Per-Call Timeout | Max Retries | Total Time |
|---|---|---|---|
| Tool Availability | 500ms | 3 | ~4s |
| Approval | 1s | 3 | ~8s |
| Validation | 2s | 3 | ~21s |
| Authorization | 500ms | 3 | ~4s |
| File Operation | 5s | 2 | ~15s |
| Git Operation | 10s | 2 | ~30s |

### Rationale

- Fast gates (tool, auth): Short timeout
- Medium gates (approval, validation): Medium timeout
- Slow gates (file, git): Long timeout

### Pros

- **Optimal per gate**: Each gate has appropriate timeout
- **Flexible**: Adapts to gate characteristics
- **Fine-tuned**: Balanced responsiveness and tolerance

### Cons

- **Complexity**: Need to configure and test each gate
- **Maintenance**: Need to adjust if gate performance changes
- **Coordination**: Must be careful that timeouts don't interact badly

### Recommendation

⚠️ **CONDITIONAL** - Good if gates have very different performance profiles

---

## Option E: No Timeout (Status Quo Gap)

### No Explicit Timeout

```
Gate Execution:
  └─ Wait indefinitely for gate to respond
```

### Pros

- **No false positives**: Gate never mistaken for stuck
- **Simple**: No timeout logic needed

### Cons

- **Can hang forever**: Stuck gates block forever
- **No failure detection**: Silent failure recreated
- **Bad governance**: System could be stuck without knowing

### Recommendation

✗ **NOT RECOMMENDED** - This is the current gap we're fixing

---

## Decision Matrix

| Aspect | Option A (1s/3) | Option B (100ms/3) | Option C (5s/3) | Option D (Per-Gate) | Option E (None) |
|--------|---|---|---|---|---|
| **Fast Detection** | ✓ Good | ✓✓ Excellent | ✗ Poor | ✓✓ Excellent | ✗ None |
| **False Positives** | ✓ Low | ✗ High | ✓✓ Very Low | ✓ Low | ✗ N/A |
| **User Experience** | ✓ Good | ✓✓ Excellent | ✗ Poor | ✓✓ Excellent | ✗ Bad |
| **Simplicity** | ✓✓ Simple | ✓✓ Simple | ✓✓ Simple | ✗ Complex | ✓✓ Simple |
| **Robustness** | ✓ Good | ✗ Risky | ✓ Good | ✓✓ Excellent | ✗ Bad |

**Best Overall**: Option A (simple, good balance)  
**Best Responsiveness**: Option B (but risky)  
**Best Flexibility**: Option D (but complex)

---

## Implementation Considerations

### Timeout Mechanism

Timeouts are typically implemented using:

1. **Thread/Process timeout**: OS-level timeout on process execution
2. **Future/Promise timeout**: Async operation timeout
3. **Timer-based polling**: Check if gate has responded, timeout if not

### Cascading Timeouts

If gates call other gates, timeouts cascade:

```
Gate A timeout (10s) ← Must be > Gate B timeout (5s) + Buffer
  └─ Calls Gate B timeout (5s)
```

**Rule**: Parent gate timeout > child gate timeout + 2 seconds (buffer)

### Monitoring

Timeout behavior should be monitored:

- How many gates hit timeout per day?
- Which gates timeout most frequently?
- If > 5% of gates timeout, may need to increase timeout or fix gate

---

## Backoff Strategy Variations

Instead of exponential backoff, could use:

1. **Linear backoff**: Wait 1s, 2s, 3s (simpler)
2. **Fixed backoff**: Always wait 1s (simpler, less adaptive)
3. **Jittered backoff**: Add randomness to avoid thundering herd (complex)

**Current design (exponential)** is appropriate for the use case.

---

## Human Gate Decision Form

**Which option do you choose?**

- [ ] Option A: 1s timeout, 3 retries (RECOMMENDED)
- [ ] Option B: 100ms timeout, 3 retries (aggressive)
- [ ] Option C: 5s timeout, 3 retries (conservative)
- [ ] Option D: Per-gate timeout (granular)
- [ ] Option E: No timeout (NOT RECOMMENDED)
- [ ] Other (please specify):

**If Option D (Per-Gate), specify timeout for each:**

Gate Type | Per-Call Timeout | Max Retries | Rationale
--|--|--|--
Tool Availability | ___ | ___ | 
Approval | ___ | ___ | 
Validation | ___ | ___ | 
Authorization | ___ | ___ | 
File Operation | ___ | ___ | 
Git Operation | ___ | ___ | 

**Additional Constraints**:

---

## Related Design Elements

**In DI2_ERROR_MODEL_SPECIFICATION_DRAFT.md**:
- §5 (Recovery Flow) - Timeout handling in recovery decision tree
- Error code TOOL_E004: Tool timeout

**In DI2_DI2_RISK_LIST.md**:
- Risk 8: File operation verification deadlock (timeout related)

**In TEST_PLAN_DI1_DI2.md**:
- Test Phase 3: Timeout scenarios (if applicable)

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Candidate | Claude (Phase 4 Review Prep) | Initial decision candidate |

