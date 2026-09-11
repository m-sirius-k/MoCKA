# C2-b Phase 3 Readiness - Remediation Matrix v0.1

**Phase**: Remediation Design Specification (Post-Investigation)
**Date**: 2026-09-11
**Purpose**: Map C2-b check routes to remediation paths (per HG-C14 Candidate B binding standard)
**System State**: HOLD / FAIL-CLOSED (maintained)

---

## Overview

This specification documents:
- C2-b binding standard (HG-C14 Candidate B)
- Check routes and current status
- Root cause analysis for each FAIL route
- Remediation design for each FAIL
- Verification method for each route
- Prerequisite sequencing

**NOT**: Implementation of fixes, code changes, new authorizations

**Rule**: 1 route FAIL => C2-b BLOCK (do NOT change this rule)

---

## Part 1: C2-b Binding Standard Overview

### HG-C14 Candidate B Definition

**Scope**: Binding standard for decision-making authority, evidence integrity, and runtime enforcement

**Core Principle**: Every system-level decision must be:
1. Properly authorized (by right authority)
2. Recorded with evidence (in Decision Ledger + Event Store)
3. Verifiable (binding chain is complete and auditable)
4. Enforceable (runtime checks prevent deviation)
5. Recoverable (failed decisions can be rolled back)

### C2-b Readiness Requirements

**C2-b Phase 3** requires ALL check routes to PASS:

```
1. ROUTE_CLOCK_SYNC: Clock synchronization verified
2. ROUTE_HG_API_STABLE: Decision/Event binding chain proven atomic
3. ROUTE_BINDING_COMPLETE: All decisions have corresponding events
4. ROUTE_ROLE_AUTHORITY: Roles formally defined with authority matrix
5. ROUTE_AUTHORIZATION_BOUNDARY: Enforcement points specified and verified
6. ROUTE_AUDIT_TRAIL: Complete audit capability confirmed
7. ROUTE_RECOVERY: Decision rollback/recovery procedures designed
8. ROUTE_MONITORING: Continuous verification monitoring designed

Current Status: 0/8 PASS (all 8 are FAIL or UNKNOWN)
```

---

## Part 2: Check Route Remediation Matrix

### ROUTE 1: CLOCK_SYNC

**Binding Standard Requirement**:
- Events must have reliable timestamps
- Event ordering must reflect causality
- Clock drift must be bounded and measured

**Current Status**: FAIL

**Current Evidence**:
- Timestamps exist in ISO 8601 format
- UTC timezone specified (+00:00 or Z)
- Container system time synchronized

**Gaps Identified**:
- No NTP sync status (container environment)
- No clock drift measurement data
- No timestamp ordering verification (1000+ sample test)
- No formal verification protocol defined
- No acceptable drift threshold defined

**Root Cause**:
- Timestamps exist but verification protocol not implemented
- Verification measurements not performed
- Protocol not formally specified
- Monitoring not configured

**Remediation Path**:

```
Step 1: Protocol Design (8 hours estimate)
  - Define acceptable clock drift threshold (suggest 100ms)
  - Define timestamp ordering verification test (1000+ samples)
  - Define measurement collection method
  - Define failure behavior (what if drift exceeded)
  - Define monitoring frequency (continuous/hourly/daily)

Step 2: Evidence Collection (4 hours estimate)
  - Collect actual drift measurements over 24+ hours
  - Run timestamp ordering verification test (1000+ samples)
  - Document results with confidence intervals
  - Create clock sync audit report

Step 3: Implementation (4 hours estimate)
  - Implement monitoring agent
  - Create alerting on drift exceeded
  - Implement fail-closed behavior (stop accepting events if drift too high)
  - Document protocol in governance

Step 4: Verification (2 hours estimate)
  - Test clock sync monitoring
  - Verify drift measurement accuracy
  - Confirm fail-closed behavior works
  - Document test results

Total Estimate: 18 hours
```

**Verification Method**:

```
Pass Criteria:
  1. Clock Sync Verification Protocol document exists
  2. Drift threshold defined and documented
  3. Measurement data from 24+ hours collected
  4. 1000+ event timestamp ordering verified
  5. No ordering violations found
  6. Monitoring agent deployed and reporting
  7. Alert mechanism tested
  8. Fail-closed behavior verified

Verification Test:
  - Collect samples: every 10 seconds for 24 hours (8640 samples)
  - Measure: drift between system clock and external source
  - Verify: all timestamps within threshold
  - Order check: all event timestamps monotonically increasing
  - Result: PASS if no violations found
```

**Prerequisite**: None (can proceed independently)

**Blocking**: YES - This is critical path item

---

### ROUTE 2: HG_API_STABLE

**Binding Standard Requirement**:
- Decision + Event must be atomic (both succeed or both fail)
- No orphaned decisions without events
- Event creation failures must fail-close decision
- Caller must not see "success" when binding incomplete

**Current Status**: FAIL

**Current Evidence**:
- mocka_decision_write exists
- Companion event creation attempted
- Some fail-closed concept exists

**Gaps Identified** (CRITICAL):
- Decision write always succeeds even if event fails
- Silent timeout handling (no retry)
- No rollback on event failure
- Caller receives "ok" regardless of event status
- No atomic guarantees
- Chain break creates orphaned decisions

**Root Cause**:
- mocka_decision_write line 995: _append_decision() called unconditionally
- Lines 1001-1017: event creation in try-except, silently continues on failure
- Line 1030: returns "ok" regardless of event_id status
- No retry logic for timeout
- No rollback for failure

**Remediation Path**:

```
Step 1: Design Selection (2 hours)
  - Confirm Option A: Fail-Closed with Atomic + Retry
  - Specify retry logic: exponential backoff (2s, 4s, 8s), max 3 attempts
  - Specify rollback behavior: remove decision from JSONL if event fails
  - Specify error response format

Step 2: Implementation (8 hours)
  - Modify mocka_decision_write to:
    a. Validate inputs first (fail-closed on validation)
    b. Write decision to ledger (TENTATIVE state)
    c. Create event with retry logic
    d. On event success: mark decision COMMITTED
    e. On event failure (retry exhausted): delete from ledger (ROLLBACK)
  - Add retry logic: exponential backoff
  - Add error response codes and messages
  - Add monitoring/logging

Step 3: Testing (6 hours)
  - Unit tests: each code path
  - Integration test: Decision + Event atomicity
  - Timeout test: verify retry behavior
  - Rollback test: verify orphan prevention
  - Concurrent request test: race condition check

Step 4: Verification (2 hours)
  - Run full test suite
  - Verify no orphaned decisions created
  - Verify error responses correct
  - Document results

Total Estimate: 18 hours
```

**Verification Method**:

```
Pass Criteria:
  1. mocka_decision_write implementation reviewed
  2. Atomic semantics confirmed (decision + event together)
  3. Retry logic verified (exponential backoff tested)
  4. Rollback logic verified (orphan prevention tested)
  5. End-to-end chain test PASS (decision -> event created)
  6. Timeout test PASS (timeout triggers retry)
  7. Concurrent test PASS (no race conditions)
  8. Error response test PASS (correct error codes/messages)

Verification Test:
  - Happy path: mocka_decision_write returns ok + decision_id + event_id
  - Timeout path: GATE times out, retry succeeds, returns ok
  - Failure path: GATE errors persist, decision rolled back, returns fail_closed
  - Orphan audit: scan Decision Ledger, verify all decisions have events
  - Result: PASS if no orphaned decisions found and all tests pass
```

**Prerequisite**: None (can proceed independently but critical path)

**Blocking**: YES - CRITICAL FINDING, required for C2-b

---

### ROUTE 3: BINDING_COMPLETE

**Binding Standard Requirement**:
- All decisions must have corresponding events in Event Store
- Binding verification mechanism must exist
- Orphaned decisions must be detected and recovered
- Zero unknown/unbound decisions allowed

**Current Status**: FAIL

**Current Evidence**:
- Decision Ledger exists
- Event Store exists
- But: binding verification mechanism does not exist
- Unknown: how many orphaned decisions exist

**Gaps Identified**:
- No automated binding audit tool
- No orphan detection mechanism
- No recovery procedures
- No audit report capability
- Unknown: current orphan count

**Root Cause**:
- HG API issue (ROUTE 2) creates orphans
- No mechanism to find/recover orphans
- No binding verification implemented

**Remediation Path**:

```
Step 1: Audit Tool Design (4 hours)
  - Design binding audit algorithm
  - Cross-reference Decision Ledger with Event Store
  - Detect orphaned decisions and orphaned events
  - Generate orphan registry
  - Implement binding audit report

Step 2: Recovery Procedure Design (4 hours)
  - Design three recovery options:
    a. Automatic event creation (for Type 1 orphans)
    b. Human Gate decision (for Type 2/3 orphans)
    c. Quarantine (for investigation hold)
  - Design recovery workflow
  - Document escalation procedures

Step 3: Implementation (8 hours)
  - Implement binding audit tool
  - Implement recovery procedures (auto + HG + quarantine)
  - Implement recovery monitoring
  - Create binding audit report

Step 4: Full Ledger Audit (4 hours)
  - Run audit on entire Decision Ledger
  - Identify all orphaned decisions
  - Execute recovery procedures
  - Generate orphan audit report

Step 5: Verification (2 hours)
  - Re-run audit after recovery
  - Confirm zero orphaned decisions
  - Verify recovery records in Event Store
  - Document audit results

Total Estimate: 22 hours
```

**Verification Method**:

```
Pass Criteria:
  1. Binding audit tool implemented and tested
  2. Recovery procedures designed and implemented
  3. Full Decision Ledger audit completed
  4. Orphan audit report generated
  5. All orphaned decisions recovered (automatic or HG decision)
  6. Zero orphaned decisions remain (audit shows 0)
  7. Binding audit can run daily (monitoring in place)
  8. Alert mechanism exists (orphan > 5 triggers alert)

Verification Test:
  - Run binding audit on full Ledger
  - Verify: for each decision_id, corresponding event exists
  - Verify: all events have complete binding metadata
  - Verify: no orphaned entries
  - Result: PASS if binding audit shows 100% complete
```

**Prerequisite**: ROUTE 2 (HG API Stable) must be fixed first

**Blocking**: YES - Upstream of ROUTE 2

---

### ROUTE 4: ROLE_AUTHORITY

**Binding Standard Requirement**:
- All roles must be formally defined
- Authority must be separated from capability
- Authority matrix must specify who can decide what
- Escalation procedures must be clear

**Current Status**: FAIL

**Current Evidence**:
- 7 roles identified ad-hoc
- きむら博士 appears to be primary authority
- Informal governance pipeline references

**Gaps Identified**:
- No formal Role Definition Registry
- No authority matrix
- Capability vs Authority confusion unresolved
- Escalation procedures not formalized
- Role conflicts unhandled

**Root Cause**:
- Roles evolved ad-hoc rather than by design
- No formal governance structure for role assignment
- No separation of capability from authority

**Remediation Path**:

```
Step 1: Role Definition Registry Design (6 hours)
  - Define each role: Responsibility, Authority, Scope
  - For each role: identify what decisions this role can make
  - Document constraints: what this role cannot decide
  - Document escalation: when to escalate up

Step 2: Authority Matrix Design (4 hours)
  - Create table: Role x Decision Type -> Authority Level
  - For each decision type: who has authority?
  - Handle conflicts: if multiple roles could decide, who wins?
  - Document delegation: can authority be delegated?

Step 3: Capability Mapping (2 hours)
  - For each role: list capabilities (technical abilities)
  - Verify: no assumption that capability implies authority
  - Document: capability is implementation right, NOT decision right

Step 4: Documentation (4 hours)
  - Write Role Definition Registry document
  - Write Authority Matrix document
  - Create escalation procedure documentation
  - Document all 7 roles formally

Step 5: Verification (2 hours)
  - Review with stakeholders
  - Verify no gaps in role coverage
  - Verify escalation chain is clear
  - Obtain authority approval

Total Estimate: 18 hours
```

**Verification Method**:

```
Pass Criteria:
  1. Role Definition Registry document created
  2. All 7+ roles formally defined
  3. Authority Matrix document created
  4. For each decision type: authority defined
  5. Escalation procedures documented
  6. Capability vs Authority separation explicit
  7. Authority conflicts resolved
  8. Authority approval obtained

Verification Test:
  - For each role: verify authority is defined (not just capability)
  - For each decision type: verify authority owner specified
  - For conflicts: verify conflict resolution documented
  - Result: PASS if authority matrix complete and approved
```

**Prerequisite**: None (can proceed independently)

**Blocking**: YES - Required for Authorization Boundary (ROUTE 5)

---

### ROUTE 5: AUTHORIZATION_BOUNDARY

**Binding Standard Requirement**:
- Authorization must be enforced at defined boundaries
- Bypass prevention mechanisms must exist
- Fail-closed on authorization failure
- UNKNOWN/NOT_PROVEN must default to NO AUTHORIZATION

**Current Status**: FAIL

**Current Evidence**:
- Governance pipeline concept exists
- READ_ONLY_TOOLS fallback exists
- Decision Ledger is append-only
- GATE proxy exists

**Gaps Identified**:
- No comprehensive authorization boundary specification
- No explicit bypass prevention
- No enforcement point specification
- No fail-closed behavior for all paths
- No UNKNOWN handling documented

**Root Cause**:
- Authorization appears implicit rather than formal
- Design not captured in specification
- Enforcement mechanisms not documented

**Remediation Path**:

```
Step 1: Authority Boundary Specification (8 hours)
  - Document: where is Human Gate authority invoked?
  - Document: where can decisions be made without HG?
  - Document: any implicit authority assumptions
  - Create Authority Boundary diagram
  - Verify: no implicit authority leaks

Step 2: Runtime Enforcement Boundary (6 hours)
  - Document: how are decisions enforced?
  - Document: what prevents enforcement bypass?
  - Document: direct routes that must have checks
  - Create Enforcement Flow diagram
  - Design: enforcement points and checks

Step 3: Binding Diagrams (4 hours)
  - Decision-Evidence binding diagram
  - Decision-State binding diagram
  - Evidence chain diagram
  - Verify: all bindings documented

Step 4: Fail-Closed Specification (4 hours)
  - Document: behavior on authorization failure
  - Document: behavior on unknown authority
  - Document: recovery procedures
  - Document: escalation procedures

Step 5: Verification (2 hours)
  - Review with authority
  - Verify: specification complete
  - Verify: no ambiguous areas
  - Obtain authority approval

Total Estimate: 24 hours
```

**Verification Method**:

```
Pass Criteria:
  1. Authorization Boundary Specification document created
  2. Authority boundaries explicitly documented
  3. Enforcement boundaries explicitly documented
  4. Bypass prevention mechanisms specified
  5. Fail-closed behavior for all paths specified
  6. UNKNOWN/NOT_PROVEN handling specified
  7. Binding diagrams complete
  8. Authority approval obtained

Verification Test:
  - For each decision type: trace authorization path
  - For each enforcement point: verify check exists
  - For each error condition: verify fail-closed behavior
  - Result: PASS if specification complete and approved
```

**Prerequisite**: ROUTE 4 (Role Authority) should be completed first

**Blocking**: YES - Required for Phase 3

---

### ROUTE 6: AUDIT_TRAIL

**Binding Standard Requirement**:
- Complete audit trail for all decisions and events
- Trace from decision -> event -> state change
- No gaps in audit log
- Audit trail must be verifiable and tamper-evident

**Current Status**: FAIL

**Current Evidence**:
- Decision Ledger exists (JSONL append-only)
- Event Store exists
- Both have timestamps

**Gaps Identified**:
- No unified audit trail across all components
- No verification that audit is complete
- No tamper detection mechanism
- No audit validation procedures

**Root Cause**:
- Audit trail scattered across multiple stores
- No centralized audit view
- No verification mechanism

**Remediation Path**:

```
Step 1: Audit Trail Design (6 hours)
  - Design unified audit log structure
  - Cross-reference Decision Ledger and Event Store
  - Design audit trail completeness check
  - Document: what must be in audit trail

Step 2: Tamper Detection Design (4 hours)
  - Design hash-based verification
  - Design timestamp ordering verification
  - Design content consistency check
  - Document: how to detect tampering

Step 3: Audit Report Design (4 hours)
  - Design audit report format
  - What information to include
  - How to trace decision -> event -> state
  - Export/visualization options

Step 4: Implementation (6 hours)
  - Implement audit trail unification
  - Implement tamper detection
  - Implement audit report generation
  - Add monitoring

Step 5: Verification (2 hours)
  - Test audit trail completeness
  - Test tamper detection (create intentional corruption, verify detection)
  - Test audit report generation
  - Document results

Total Estimate: 22 hours
```

**Verification Method**:

```
Pass Criteria:
  1. Audit Trail Design document created
  2. Unified audit structure implemented
  3. Tamper detection implemented
  4. Audit report generation working
  5. Sample audit trail traced (decision -> event -> state)
  6. No gaps in audit trail
  7. Tamper detection test PASS
  8. Audit capability demonstrated

Verification Test:
  - Select random decision from Ledger
  - Trace: decision -> event in Event Store
  - Trace: event -> state change in system
  - Verify: all steps logged and timestamped
  - Result: PASS if complete chain traced with no gaps
```

**Prerequisite**: ROUTE 2 (HG API Stable), ROUTE 3 (Binding Complete)

**Blocking**: YES - Required for compliance

---

### ROUTE 7: RECOVERY

**Binding Standard Requirement**:
- Failed decisions must be recoverable
- Rollback procedures must exist and be tested
- Recovery must be audited and documented
- No data loss on recovery

**Current Status**: FAIL

**Current Evidence**:
- Decision Ledger is append-only (no direct delete)
- Recovery concepts mentioned

**Gaps Identified**:
- No formal rollback procedures
- No recovery workflow
- No recovery verification mechanism
- No tested recovery procedures

**Root Cause**:
- Recovery procedures designed but not implemented
- No testing of recovery paths
- No operational procedures

**Remediation Path**:

```
Step 1: Recovery Procedure Design (6 hours)
  - Design decision rollback procedure (create superseding decision)
  - Design state rollback procedure (revert state changes)
  - Design recovery from orphaned decisions
  - Design recovery from integrity violations

Step 2: Implementation (8 hours)
  - Implement rollback procedures
  - Implement recovery execution
  - Add safety checks (prevent unintended rollback)
  - Add audit trail for recovery

Step 3: Testing (6 hours)
  - Test each recovery procedure
  - Test concurrent recovery (multiple decisions)
  - Test partial recovery (some succeed, some fail)
  - Test idempotency (recover twice safely)

Step 4: Documentation (2 hours)
  - Write recovery procedures manual
  - Document: when to use each procedure
  - Document: approval requirements
  - Document: audit trail expectations

Step 5: Verification (2 hours)
  - Operator training (recovery procedures)
  - Test run: full recovery scenario
  - Verify: audit trail complete
  - Document results

Total Estimate: 24 hours
```

**Verification Method**:

```
Pass Criteria:
  1. Recovery Procedures document created
  2. Recovery procedures implemented
  3. All recovery paths tested
  4. Rollback test PASS (state restored correctly)
  5. Orphan recovery test PASS
  6. Integrity violation recovery test PASS
  7. Audit trail for recovery complete
  8. Operator trained and verified

Verification Test:
  - Create test decision
  - Rollback decision (create supersede)
  - Verify: decision no longer enforced
  - Verify: state reverted correctly
  - Verify: audit trail shows rollback
  - Result: PASS if all steps succeed
```

**Prerequisite**: ROUTE 2 (HG API), ROUTE 3 (Binding), ROUTE 6 (Audit)

**Blocking**: YES - Required for operational safety

---

### ROUTE 8: MONITORING

**Binding Standard Requirement**:
- Continuous verification that all C2-b requirements are maintained
- Alerts when requirements violated
- Monitoring data collected and analyzed
- Trends tracked over time

**Current Status**: FAIL

**Current Evidence**:
- Some logging exists
- No integrated monitoring

**Gaps Identified**:
- No comprehensive monitoring dashboard
- No alert definitions
- No monitoring procedures
- No SLA/metrics defined

**Root Cause**:
- Monitoring was not designed or implemented
- No alerting infrastructure

**Remediation Path**:

```
Step 1: Monitoring Design (8 hours)
  - Define metrics to track (per ROUTE requirements)
  - Define alert thresholds
  - Design monitoring dashboard
  - Define reporting requirements

Step 2: Implementation (10 hours)
  - Implement metric collection
  - Implement alert system
  - Create monitoring dashboard
  - Add reporting automation

Step 3: Testing (4 hours)
  - Test metric collection accuracy
  - Test alert triggering (threshold crossed)
  - Test dashboard updates
  - Test report generation

Step 4: Documentation (2 hours)
  - Document: what metrics mean
  - Document: alert response procedures
  - Document: dashboard interpretation
  - Document: escalation paths

Step 5: Verification (2 hours)
  - Verify: monitoring running
  - Verify: alerts working
  - Verify: dashboard accessible
  - Document results

Total Estimate: 26 hours
```

**Verification Method**:

```
Pass Criteria:
  1. Monitoring Design document created
  2. Metric collection implemented
  3. Alert system operational
  4. Monitoring dashboard live
  5. All 8 ROUTES have metrics defined
  6. Alert thresholds met
  7. Reporting automation working
  8. 24-hour monitoring period PASS

Verification Test:
  - Verify: metrics for each ROUTE displayed
  - Trigger: intentional threshold violation
  - Verify: alert fires
  - Verify: dashboard updates
  - Result: PASS if all monitoring functional
```

**Prerequisite**: ROUTE 2, 3, 5, 6, 7 (should be done before monitoring)

**Blocking**: YES - Required for Phase 3

---

## Part 3: Remediation Sequencing

### Critical Path

```
Phase 1: Foundation (can run in parallel)
  - ROUTE 1 (Clock Sync): 18 hours
  - ROUTE 4 (Role Authority): 18 hours
  - ROUTE 5 (Authorization Boundary): 24 hours
  
  Parallel estimate: 24 hours (longest path)

Phase 2: Core (sequential dependency on Phase 1)
  - ROUTE 2 (HG API Stable): 18 hours (depends on Route 4+5)
  - ROUTE 3 (Binding Complete): 22 hours (depends on Route 2)
  
  Sequential estimate: 40 hours

Phase 3: Verification (sequential dependency on Phase 2)
  - ROUTE 6 (Audit Trail): 22 hours (depends on Route 2+3)
  - ROUTE 7 (Recovery): 24 hours (depends on Route 2+3+6)
  - ROUTE 8 (Monitoring): 26 hours (depends on all others)
  
  Sequential estimate: 72 hours

Total Estimated Timeline:
  Phase 1: 24 hours (parallel work)
  Phase 2: 40 hours (sequential)
  Phase 3: 72 hours (sequential)
  
  Critical path: 24 + 40 + 72 = 136 hours (17 business days at 8 hrs/day)
```

### Blocking Dependencies

```
Graph (what must complete before what):

Clock Sync (1)
  └─→ [baseline timestamp verification]

Role Authority (4)
  └─→ Authorization Boundary (5)
      └─→ HG API Stable (2)
          └─→ Binding Complete (3)
              └─→ Audit Trail (6)
                  └─→ Recovery (7)
                      └─→ Monitoring (8)

Summary:
  - ROUTE 2 (HG API) is critical bottleneck
  - ROUTE 3 (Binding) depends on ROUTE 2
  - ROUTE 6/7/8 depend on ROUTE 2+3
  - ROUTE 4/5 can run in parallel with ROUTE 1
```

---

## Part 4: C2-b Readiness Evaluation

### C2-b Status Before Remediation
```
ROUTE 1 (Clock Sync): FAIL
ROUTE 2 (HG API Stable): FAIL (CRITICAL)
ROUTE 3 (Binding Complete): FAIL (CRITICAL)
ROUTE 4 (Role Authority): FAIL
ROUTE 5 (Authorization Boundary): FAIL
ROUTE 6 (Audit Trail): FAIL
ROUTE 7 (Recovery): FAIL
ROUTE 8 (Monitoring): FAIL

C2-b Phase 3 Status: BLOCKED (0/8 routes PASS)
```

### C2-b Status After Remediation (Projected)
```
Upon completion of all remediations:

ROUTE 1 (Clock Sync): PASS (with measurement data)
ROUTE 2 (HG API Stable): PASS (atomic semantics verified)
ROUTE 3 (Binding Complete): PASS (zero orphans, audit verified)
ROUTE 4 (Role Authority): PASS (formal registry approved)
ROUTE 5 (Authorization Boundary): PASS (enforcement verified)
ROUTE 6 (Audit Trail): PASS (complete chain verification)
ROUTE 7 (Recovery): PASS (recovery procedures tested)
ROUTE 8 (Monitoring): PASS (monitoring operational)

C2-b Phase 3 Status: READY (8/8 routes PASS)
```

---

**Document Version**: 0.1 (Design Specification, not Implementation)
**Status**: Ready for HG Review
**Co-Authored-By**: Claude Haiku 4.5 <noreply@anthropic.com>
