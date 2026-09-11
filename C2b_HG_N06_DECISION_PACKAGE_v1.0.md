# C2-b HG-N06 Decision Package: Recovery Procedures Strategy Selection

**Document Number:** C2B-HG-N06-DECISION-v1.0
**Date:** 2026-09-12
**Session:** claude/kuroko-c2b-route-audit-n51wgf
**Phase:** Human Gate Decision Point HG-N06
**Status:** PENDING HUMAN GATE DECISION

---

## Executive Summary

**Decision Required:** Which recovery strategy should be adopted for each of 9 critical failure scenarios?

**Current State:** 2-3 candidate recovery strategies designed for each scenario (18 strategies total from STEP 6). All scenarios identified; no current handling except orphan detection and retry exhaustion.

**Recommendation by Scenario:** See Strategic Recommendations section (Scenario-specific choices based on failure severity and recovery complexity).

**Human Authority:** きむら博士 (HUMAN_AUTHORITY)

**Timeline:** 1 week review → Decision → Implementation (4-8 hours coding + testing per STEP 10)

---

## Current State

### Problem Statement

ROUTE 7 (Recovery Procedures) is currently NOT_READY because critical failure scenarios lack formal recovery procedures. System currently relies on:
- Implicit exception handling (failures propagate to caller)
- Idempotency key mechanism (retry-safe) — implemented
- Orphan detection via verify_chain() — partially implemented
- No timeout handling
- No rollback procedures
- No escalation decision trees

**Evidence:** STEP 6 audit identified 9 failure scenarios; only 2 have existing procedures.

**Impact:** Cannot recover from transient failures (DB lock, network timeout, partial writes). Authorization boundaries cannot be preserved under failure conditions.

### Decision Scope

This decision establishes:
1. Recovery strategy for each of 9 failure scenarios
2. Automatic vs. manual recovery boundary
3. Escalation triggers and decision points
4. Retry limits and backoff strategies
5. Fail-closed enforcement during recovery

This decision does NOT:
- Assign human decision-makers to specific scenarios (きむら博士 is HUMAN_AUTHORITY for all)
- Implement recovery code (comes after Decision)
- Change current behavior until Decision is approved

---

## 9 Failure Scenarios & Recovery Strategies

### SCENARIO S1: Event Timeout (no response within N seconds)

**Problem:** _write() operation blocks indefinitely (DB locked, network latency, etc.)

**Current State:** No timeout; blocks forever

**Severity:** CRITICAL (freezes event pipeline)

#### S1-A: Aggressive Timeout + Automatic Retry

| Aspect | Detail |
|---|---|
| Timeout | 5 seconds |
| Retries | 3 attempts with exponential backoff (2s, 4s, 8s) |
| Escalation | Auto-escalate to KUROKO_MONITOR after max retries |
| Recovery Time | Max 19 seconds (5 + 2 + 4 + 8) |
| Fail-Closed | Yes (timeout forces rejection) |
| Implementation | Signal-based timeout (may not work on Windows) |

**Advantages:** Fast failure detection, automatic recovery attempt

**Disadvantages:** Platform-dependent, abrupt termination risk

#### S1-B: Conservative Timeout + Manual Escalation

| Aspect | Detail |
|---|---|
| Timeout | 30 seconds |
| Retries | 0 (manual decision after timeout) |
| Escalation | Escalate to HUMAN_AUTHORITY for decision |
| Recovery Time | 30s + human decision time (minutes) |
| Fail-Closed | Yes (timeout forces escalation) |
| Implementation | Thread-based (cross-platform) |

**Advantages:** Permits legitimate slow operations, human oversight

**Disadvantages:** Long wait before escalation, requires human decision

#### S1-C: Adaptive Timeout (No fixed timeout)

| Aspect | Detail |
|---|---|
| Timeout | None (relies on monitoring) |
| Retries | N/A |
| Escalation | Monitoring detects >60min stuck writes, alerts |
| Recovery Time | 60+ minutes |
| Fail-Closed | Weak (hangs indefinitely without monitoring) |
| Implementation | Monitoring job every 5 minutes |

**Advantages:** No timeout implementation needed

**Disadvantages:** Long detection latency, weak fail-closed guarantee

**RECOMMENDED:** S1-B (Conservative Timeout + Manual Escalation)
- Rationale: 30s timeout is reasonable for DB operations; manual escalation preserves HUMAN_AUTHORITY oversight; cross-platform reliability
- Conditions: KUROKO_MONITOR monitors EVENT_WRITE_TIMEOUT events for patterns

---

### SCENARIO S2: Event Write Failure (INSERT fails)

**Problem:** Database INSERT fails (DB locked, out of space, constraint violation, etc.)

**Current State:** Exception propagates; no automatic recovery

**Severity:** HIGH (event not persisted, no retry logic)

#### S2-A: Immediate Rollback + Alert

| Aspect | Detail |
|---|---|
| Strategy | Fail fast, rollback immediately |
| Retries | 0 (no automatic retry) |
| Escalation | Alert KUROKO_MONITOR immediately |
| Recovery Time | Manual (human-driven investigation) |
| Fail-Closed | Yes (clear failure signal) |
| Implementation | Explicit conn.rollback() on error |

**Advantages:** Clear failure signal, no partial writes

**Disadvantages:** Requires manual intervention for every transient failure

#### S2-B: Retry with Exponential Backoff

| Aspect | Detail |
|---|---|
| Strategy | Automatic retry on transient failures |
| Retries | 3 attempts with exponential backoff |
| Escalation | Escalate only on permanent failure detection |
| Recovery Time | Up to 6.5 seconds (transient) or manual (permanent) |
| Fail-Closed | Yes (escalates on permanent failure) |
| Implementation | Detect "database is locked" error; retry |

**Advantages:** Automatic recovery for transient failures, reduces manual intervention

**Disadvantages:** Cannot always distinguish transient from permanent; adds latency

#### S2-C: Queue and Retry Later (Batch Retry)

| Aspect | Detail |
|---|---|
| Strategy | Queue failed writes for batch retry |
| Retries | Batch job retries every 5 minutes |
| Escalation | Alert after N batch retry failures |
| Recovery Time | Up to 5 minutes per batch cycle |
| Fail-Closed | Weak (queued events not immediately handled) |
| Implementation | Queue mechanism + batch retry job |

**Advantages:** Non-blocking, preserves event data, batch efficiency

**Disadvantages:** Complex queue management, delayed recovery, potential queue growth

**RECOMMENDED:** S2-B (Retry with Exponential Backoff)
- Rationale: Most transient failures are DB-locked; exponential backoff is proven pattern; clear escalation on permanent failure
- Conditions: Max retries = 3; backoff: 0.5-1.5s, 1-2s, 2-3s; escalate after exhaustion

---

### SCENARIO S3: Decision Write Failure (JSONL write fails)

**Problem:** Writing to decision_ledger.jsonl fails (file locked, disk full, permission denied, etc.)

**Current State:** No backup mechanism; no dual-write

**Severity:** HIGH (decision not recorded; authorization boundary violated)

**RECOMMENDED:** S3-Dual-Write (Primary + Backup Location)

| Aspect | Detail |
|---|---|
| Strategy | Write to primary; on failure, write to backup location |
| Locations | Primary: data/decisions/decision_ledger.jsonl; Backup: data/decisions/decision_ledger_backup_TIMESTAMP.jsonl |
| Escalation | Alert KUROKO_MONITOR on primary failure; escalate on both failures |
| Recovery Time | <1 second (backup write) |
| Fail-Closed | Yes (decision preserved in backup; manual merge later) |
| Implementation | Try-except with second write attempt to backup path |

**Advantages:** Ensures decision is persisted even if primary fails; clear audit trail of backup

**Disadvantages:** Requires backup file merge procedure (manual process post-recovery)

---

### SCENARIO S4: Partial Write (INSERT succeeds, UPDATE fails)

**Problem:** Event created in database but signing/binding fails; creates unsigned orphan

**Current State:** Orphan created; detected later by verify_chain()

**Severity:** CRITICAL (authorization boundary violated; orphan undetectable in real-time)

**RECOMMENDED:** S4-Rollback-on-Binding-Failure

| Aspect | Detail |
|---|---|
| Strategy | Atomic all-or-nothing: if binding fails, rollback INSERT |
| Boundary | If signing fails AFTER INSERT, immediately delete row |
| Implementation | Wrap event creation + signing in transaction; rollback on signing failure |
| Recovery | Exception propagates; retry entire operation (idempotency_key prevents duplicates) |
| Escalation | Alert KUROKO_MONITOR on binding failure |
| Fail-Closed | Yes (no orphans created; fail-closed principle maintained) |

**Advantages:** Prevents orphans; maintains atomicity; clear failure signal

**Disadvantages:** Requires atomic transaction wrapping; may add latency

---

### SCENARIO S5: Signing Failure (sign_event() fails during hash chain computation)

**Problem:** Integrity signing fails (e.g., hash computation timeout, missing previous_hash, etc.)

**Current State:** Exception propagates; event orphaned if partial write occurred

**Severity:** HIGH (binding not created; orphan risk)

**RECOMMENDED:** S5-Deferred-Signing-with-Retry-Job

| Aspect | Detail |
|---|---|
| Strategy | On signing failure, defer signing; retry in background job |
| Behavior | Event marked as UNSIGNED; retry job attempts signing every 5 minutes |
| Implementation | If sign_event() fails, save event with UNSIGNED marker; retry job runs verify_chain() + repair |
| Escalation | After 10 retry attempts, escalate to KUROKO_MONITOR |
| Recovery Time | Up to 50 minutes (10 retries × 5 min) |
| Fail-Closed | Partial (event persisted but unsigned; detect via monitoring) |

**Advantages:** Doesn't block event creation; preserves event data; automatic retry

**Disadvantages:** Temporary unsigned events; requires monitoring

---

### SCENARIO S6: Retry Exhaustion (retried N times, still fails)

**Problem:** Operation fails repeatedly; max retries exhausted

**Current State:** Operation fails; exception propagated

**Severity:** HIGH (prevents progress; requires human decision)

**RECOMMENDED:** S6-Auto-Escalate-to-Human-Gate

| Aspect | Detail |
|---|---|
| Strategy | After max retries exhausted, auto-escalate to HUMAN_AUTHORITY |
| Trigger | N consecutive failures (N = 3 for timeout, 3 for write, 10 for signing) |
| Escalation | Invoke mocka_write_event(RETRY_EXHAUSTED) + alert きむら博士 |
| Decision Options | (a) Skip this event, (b) Investigate and retry, (c) Rollback and restart |
| Implementation | Explicit escalation_to_human_gate(reason, event_id, alternatives) |
| Recovery Time | Depends on human response (minutes to hours) |
| Fail-Closed | Yes (escalates to HUMAN_AUTHORITY; prevents auto-retry loops) |

**Advantages:** Prevents infinite retry loops; ensures human oversight

**Disadvantages:** Requires human decision; slow recovery

---

### SCENARIO S7: Orphan Detection (verify_chain finds unsigned event)

**Problem:** During integrity verification, orphan detected (signed event without corresponding rows)

**Current State:** detect() generates diagnostic; suggests repair

**Severity:** MEDIUM (already outside authorization boundary; detection is recovery)

**RECOMMENDED:** S7-Diagnostic-Plus-Manual-Repair

| Aspect | Detail |
|---|---|
| Strategy | diagnose() provides repair suggestions; KUROKO_MONITOR implements approved repair |
| Repairs Available | (a) Link missing rows, (b) Delete orphan + retry signing, (c) Mark as unrecoverable |
| Escalation | KUROKO_MONITOR proposes repair; HUMAN_AUTHORITY approves |
| Implementation | diagnose() already implemented; wrap in approval workflow |
| Recovery Time | Minutes to hours (human-driven) |
| Fail-Closed | Yes (repair requires approval) |

**Advantages:** Leverages existing diagnose() logic; human oversight

**Disadvantages:** Manual repair complexity; requires expert judgment

---

### SCENARIO S8: Rollback Scenario (INVALIDATED state needed)

**Problem:** Prior decision must be invalidated (e.g., decision reversed, wrong authorization)

**Current State:** No rollback procedure

**Severity:** HIGH (authorization boundary breach if not handled)

**RECOMMENDED:** S8-Invalidation-with-Audit-Trail

| Aspect | Detail |
|---|---|
| Strategy | Mark decision INVALIDATED; create cascading invalidation records |
| Implementation | (a) Insert INVALIDATED marker into decision_ledger.jsonl, (b) Mark all derived events with INVALIDATED_BY reference |
| Escalation | HUMAN_AUTHORITY initiates invalidation; KUROKO_MONITOR executes |
| Audit Trail | Complete trail preserved; all invalidations tracked |
| Recovery | Subsequent authorization checks skip INVALIDATED decisions |
| Fail-Closed | Yes (invalidation is explicit, not silent deletion) |

**Advantages:** Preserves audit trail; no data deletion

**Disadvantages:** Requires downstream logic to skip INVALIDATED records

---

### SCENARIO S9: Recovery Failure (repair attempt fails)

**Problem:** Repair attempt fails (e.g., diagnose() suggests link, but link creation fails)

**Current State:** No cascading failure handling

**Severity:** CRITICAL (double failure; authorization boundary compromised)

**RECOMMENDED:** S9-Escalate-Plus-Freeze

| Aspect | Detail |
|---|---|
| Strategy | When recovery fails, escalate to HUMAN_AUTHORITY + freeze authorization checks |
| Behavior | (a) Alert きむら博士 immediately, (b) Set system flag RECOVERY_FAILURE=true, (c) All new authorizations go to HOLD until human resolves |
| Implementation | catch exception in recovery_attempt(); trigger RECOVERY_FAILURE alert + system halt |
| Decision | HUMAN_AUTHORITY decides: (a) manual repair, (b) restore from backup, (c) escalate to external support |
| Recovery Time | Human-driven (hours or days) |
| Fail-Closed | Yes (fails to HOLD state; no unauthorized operations continue) |

**Advantages:** Prevents cascading failures; ensures human oversight

**Disadvantages:** System freeze; impacts availability

---

## Strategic Recommendations Summary

| Scenario | Problem | Recommended Strategy | Rationale |
|---|---|---|---|
| **S1** | Timeout | B: Conservative + Manual | Cross-platform, permits slow ops, human oversight |
| **S2** | Write Failure | B: Retry + Backoff | Proven pattern, auto-recovery for transient, escalates on permanent |
| **S3** | Decision Write | Dual-Write | Ensures decision persisted; backup merge is manual post-recovery |
| **S4** | Partial Write | Atomic Rollback | Prevents orphans; maintains atomicity |
| **S5** | Signing Failure | Deferred Signing + Retry Job | Non-blocking; automatic retry; monitoring detects |
| **S6** | Retry Exhaustion | Auto-Escalate | Prevents infinite loops; ensures human decision |
| **S7** | Orphan Detection | Diagnostic + Approval | Leverages existing logic; human oversight on repair |
| **S8** | Rollback Needed | Invalidation + Audit Trail | Preserves history; clean reversal without deletion |
| **S9** | Recovery Failure | Escalate + Freeze | Prevents cascading; forces human intervention |

**Total Strategy Count:** 9 scenarios × 1 recommended strategy = 9 decisions required

---

## Recovery Decision Questions for Human Authority

### S1: Event Timeout Handling
**HG-N06-S1-1:** Accept Candidate B (30-second timeout + manual escalation) for event timeout handling?

**HG-N06-S1-2:** Is 30 seconds an appropriate timeout for database write operations, or adjust to: (a) 15 seconds (aggressive), (b) 60 seconds (conservative)?

**HG-N06-S1-3:** Should timeout escalations go directly to HUMAN_AUTHORITY or first to KUROKO_MONITOR for pattern analysis?

---

### S2: Event Write Failure Handling
**HG-N06-S2-1:** Accept Candidate B (retry with exponential backoff) for write failure recovery?

**HG-N06-S2-2:** What is max retry count? (Recommended: 3; Range: 1-5)

**HG-N06-S2-3:** Is 6.5-second maximum retry latency acceptable, or use Candidate C (queue) for non-blocking behavior?

---

### S3: Decision Write Failure Handling
**HG-N06-S3-1:** Accept dual-write strategy (primary + backup) for decision ledger?

**HG-N06-S3-2:** Who triggers backup file merge (recovery.py script or manual process)?

---

### S4: Partial Write Prevention
**HG-N06-S4-1:** Accept atomic rollback strategy (if binding fails, delete INSERT)?

**HG-N06-S4-2:** Should orphan detection monitoring run continuously or on-demand?

---

### S5: Signing Failure Recovery
**HG-N06-S5-1:** Accept deferred signing strategy (background retry job every 5 minutes)?

**HG-N06-S5-2:** Max retry attempts before escalation? (Recommended: 10; Range: 3-20)

---

### S6: Retry Exhaustion Escalation
**HG-N06-S6-1:** Accept auto-escalation to HUMAN_AUTHORITY when retries exhausted?

**HG-N06-S6-2:** Define retry limits per scenario:
- Event timeout: 3? 5? (recommended: 3)
- Write failure: 3? 5? (recommended: 3)
- Signing failure: 10? 20? (recommended: 10)

---

### S7: Orphan Repair Procedure
**HG-N06-S7-1:** Accept diagnostic + approval workflow (existing diagnose() + HUMAN_AUTHORITY approval)?

**HG-N06-S7-2:** Should KUROKO_MONITOR auto-implement approved repairs or require explicit human confirmation?

---

### S8: Rollback/Invalidation Procedure
**HG-N06-S8-1:** Accept invalidation strategy (mark INVALIDATED, preserve audit trail)?

**HG-N06-S8-2:** Who initiates invalidation: (a) HUMAN_AUTHORITY only, (b) KUROKO_MONITOR proposes, HUMAN_AUTHORITY approves?

---

### S9: Cascading Failure (Recovery Failure)
**HG-N06-S9-1:** Accept freeze strategy (RECOVERY_FAILURE flag + new authorizations → HOLD)?

**HG-N06-S9-2:** What actions should きむら博士 be notified of:
- Recovery failure alert (immediate)
- Manual repair options (summary)
- Estimated recovery time (estimate)

---

## Implementation Readiness

### Code Changes Required (After Decision)

**File: phi_os/recovery.py** (new)
```python
# Recovery procedures for all 9 scenarios
class RecoveryManager:
    def handle_event_timeout(event_id, retry_count=0):
        # S1: Conservative timeout + manual escalation
        pass
    
    def handle_write_failure(event_id, error, retry_count=0):
        # S2: Retry with backoff
        pass
    
    def handle_decision_write_failure(decision, primary_path, backup_path):
        # S3: Dual write
        pass
    
    def handle_partial_write(event_id):
        # S4: Atomic rollback
        pass
    
    def handle_signing_failure(event_id, retry_attempt=0):
        # S5: Deferred signing + retry job
        pass
    
    def handle_retry_exhaustion(operation, event_id):
        # S6: Auto-escalate to HUMAN_AUTHORITY
        pass
    
    # S7-S9: Orchestrate with existing procedures
```

**Files to Update:**
- `phi_os/event_gate.py` — Integrate S1-S2 timeout/retry handling
- `phi_os/integrity.py` — Integrate S4-S5 signing/atomic strategies
- `structural/recovery_job.py` — Implement S5 retry job, S7 orphan repair orchestration
- `governance/decision_handler.py` — Integrate S3 dual-write, S8 invalidation

**Effort Estimate:** 4-8 hours coding + 2-3 hours testing = 6-11 hours total

**Timeline (Post-Decision):**
- Day 1: Code recovery manager + integrate into event_gate.py (4 hours)
- Day 1: Code recovery job + integrate into integrity.py (2 hours)
- Day 2: Unit tests (2 hours)
- Day 2: Integration tests (1 hour)
- Day 3: Failure injection tests (2 hours)
- Day 4: Regression verification (1 hour)

---

## Evidence Summary

**Design Evidence:**
- STEP 6: Comprehensive failure scenario analysis (9 scenarios identified)
- 2-3 candidate strategies per scenario (18 strategies total)
- Code examples for all strategies
- Recovery time estimates
- Fail-closed verification

**Comparison Basis:**
- 10-axis decision framework:
  1. Automatic vs. Manual recovery boundary
  2. Recovery time SLA
  3. Fail-closed guarantee
  4. Escalation clarity
  5. Implementation complexity
  6. Platform compatibility
  7. Auditability
  8. Testability
  9. Authorization boundary preservation
  10. Coordination with other ROUTEs

**Strategic Selection Rationale:**
- S1-B: Long timeout respects legitimate slow operations; manual escalation ensures HUMAN_AUTHORITY oversight
- S2-B: Exponential backoff is proven pattern; auto-recovery for transient, escalate on permanent
- S3: Dual-write ensures decision persisted; backup merge is post-recovery manual step
- S4: Atomic rollback prevents orphan creation; maintains fail-closed principle
- S5: Deferred signing non-blocking; allows event creation; background retry handles eventual signing
- S6: Auto-escalate prevents infinite loops; forces human decision on hard failures
- S7: Diagnostic + approval leverages existing logic; preserves human oversight
- S8: Invalidation preserves audit trail; no silent deletions
- S9: Escalate + Freeze prevents cascading failures; forces human expertise

---

## Next Steps (After Decision)

1. **If All Recommended Strategies Approved:**
   - Implement phi_os/recovery.py with 9 recovery procedures
   - Integrate each procedure into appropriate module (event_gate.py, integrity.py, etc.)
   - Create failure injection tests for each scenario
   - Execute recovery verification tests
   - Update ROUTE 7 status from NOT_READY to PASS
   - Document recovery decision in decision_ledger.jsonl

2. **If Alternative Strategies Selected:**
   - Adapt implementation to chosen strategies
   - Timeline adjusts accordingly (typically +/-2 hours per strategy change)

---

## Current Decision Status

**HG-N06 DECISION = PENDING HUMAN GATE**

**Awaiting きむら博士 (HUMAN_AUTHORITY) decision on:**
1. Recommended strategy for each of 9 scenarios (or alternatives)
2. Retry limits and timeout values per scenario
3. Escalation procedures and decision authority
4. Approval workflows for manual recovery steps

**Decision Required Before:** Implementation Authorization phase can proceed to code changes

**Document Status:** COMPLETE — Ready for Human Gate review

---

**Custodian:** KUROKO Monitor
**Session:** claude/kuroko-c2b-route-audit-n51wgf
**Evidence:** STEP 6 Recovery Procedures Design + Strategic Analysis
**Recommendations:** 9 scenario-specific recovery strategies
**Final Authority:** きむら博士 (HUMAN_AUTHORITY)
