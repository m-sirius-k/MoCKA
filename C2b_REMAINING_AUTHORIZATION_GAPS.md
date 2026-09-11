# C2-b Remaining Authorization Gaps & Decision Requirements

**Document Number:** EBGA-C2B-GAPS-001
**Date:** 2026-09-12 07:15 UTC
**Status:** PRE-DECISION ANALYSIS
**Session:** claude/kuroko-c2b-route-audit-n51wgf

---

## Executive Summary

This document identifies the 4 critical authorization gaps that must be addressed before C2-b can achieve READY status. Each gap requires either design completion (within Implementation Authorization) or Human Gate Decision (for policy/logic changes).

**Total Gaps:** 4
**Can Proceed Without Human Gate:** 2 (Gaps #2, #4)
**Require Human Gate Decision:** 2 (Gaps #1, #3)

---

## GAP #1: ROUTE 4 — Role Authority Registry (HUMAN GATE DECISION)

### Identification

**Audit Finding:** Role definitions and authority mapping are partially documented. No comprehensive role registry exists.

**Affected ROUTE:** ROUTE 4 (Role Authority & Escalation)

**Current State:**
- Human Gate decision authority defined (きむら博士)
- GL7 Execution Kernel role mentioned in `execution_governance.py`
- KUROKO Monitor implicit in event system
- Event Validator, Integrity Engine, Audit Trail Manager roles not formally defined

**Missing Artifact:** Formal 7-role × 8-attribute Role Registry

### What Needs to Be Decided

| Decision | Current | Required | Authority |
|----------|---------|----------|-----------|
| **D-1** | How many distinct roles should system define? | Minimum 6; possibly 7+ | Human Gate |
| **D-2** | What is the identity of each role? | Clear unique identifier + name | Human Gate |
| **D-3** | What capability does each role have? | Specific, bounded capability list | Human Gate |
| **D-4** | What is the authority level of each role? | Ranked authority with decision rights | Human Gate |
| **D-5** | What is the scope of each role? (which operations) | Bounded to specific files/components | Human Gate |
| **D-6** | Who has decision rights for each operation? | Clear decision matrix | Human Gate |
| **D-7** | Who has execution rights for each operation? | Clear execution matrix | Human Gate |
| **D-8** | What is the escalation procedure for each role? | Clear escalation paths | Human Gate |

### What CAN Be Done Without Human Gate

✓ Compile existing role mentions from codebase
✓ Extract implicit role boundaries from existing code
✓ Draft proposed role registry based on code analysis
✓ Identify conflicts or ambiguities for Human Gate review
✓ Propose role hierarchy options (A, B, C candidates)

### What CANNOT Be Done Without Human Gate

❌ Finalize role definitions
❌ Establish official authority levels
❌ Create binding role registry
❌ Implement automatic escalation based on roles
❌ Modify any authorization logic based on new roles

### Estimated Effort

| Activity | Effort | Dependent On |
|----------|--------|---|
| Code role extraction | 2 hours | None (can proceed now) |
| Draft registry proposal | 2 hours | Code extraction |
| Conflict analysis | 1 hour | Draft proposal |
| Candidate options (A/B/C) | 2 hours | Conflict analysis |
| **Subtotal (Pre-Decision)** | **7 hours** | Can proceed now |
| Human Gate Decision | - | Depends on proposal |
| Registry implementation | 2 hours | Human Gate approval |
| **Total** | **9 hours** | |

### Recommendation

**Immediate Action (Implementation Authorization):**
1. Extract all role mentions from codebase (2 hrs)
2. Analyze current role capabilities from code (2 hrs)
3. Identify gaps and conflicts (1 hr)
4. Draft 2-3 candidate role registries (2 hrs)
5. Submit candidates to Human Gate for decision (0 hrs)

**Post-Decision:**
- Implement approved role registry
- Update authorization checks to use registry
- Test role-based access control

---

## GAP #2: ROUTE 5 — Authorization Boundary Verification (IMPLEMENTATION AUTHORIZATION)

### Identification

**Audit Finding:** Authorization boundaries exist (5 enforcement points) but verification procedures are incomplete.

**Affected ROUTE:** ROUTE 5 (Authorization Boundary Enforcement)

**Current State:**
- EP-1 (API Entry): Validation gate exists, authorization unclear
- EP-2 (Ledger Write): Single write path established, role check missing
- EP-3 (Event Creation): Validation exists, decision linkage missing
- EP-4 (State Transition): Implementation unclear
- EP-5 (Audit Trail): Signing present, bypass test missing

### What Needs to Be Verified

| Enforcement Point | Current | Required | Work Type |
|---|---|---|---|
| **EP-1 API Entry** | Validation gate | Explicit role check + decision binding | Code review + possible small fix |
| **EP-2 Ledger Write** | Single path + commit | Authorization check before write | Code review + possible small fix |
| **EP-3 Event Creation** | Validation | Decision-to-event linkage verification | Code review + possible small fix |
| **EP-4 State Transition** | ? | Authorization check before state change | Investigation + implementation |
| **EP-5 Audit Trail** | Signing + hash chain | Bypass path testing + tamper detection | Test design |

### What CAN Be Done Without Human Gate

✓ Audit all 5 enforcement points in code
✓ Document current authorization checks
✓ Identify missing verification steps
✓ Design verification test cases
✓ Create bypass path inspection procedures
✓ Document fail-closed behavior requirements

### What CANNOT Be Done Without Human Gate

❌ Modify authorization logic without review
❌ Add authorization checks that affect decision-making
❌ Change ledger write behavior
❌ Implement new authorization boundaries

### Estimated Effort

| Activity | Effort | Authority |
|----------|--------|-----------|
| EP-1 verification audit | 1 hour | Implementation |
| EP-2 verification audit | 1 hour | Implementation |
| EP-3 verification audit | 1 hour | Implementation |
| EP-4 investigation | 2 hours | Implementation |
| EP-5 test design | 2 hours | Implementation |
| Bypass path inspection | 2 hours | Implementation |
| Fail-closed verification | 1.5 hours | Implementation |
| **Total** | **10.5 hours** | Can proceed now |

### Recommendation

**Immediate Action (Implementation Authorization):**
1. Audit each of 5 enforcement points (5 hrs)
2. Identify missing authorization steps (1 hr)
3. Design verification procedures (2.5 hrs)
4. Document bypass paths and fail-closed requirements (2 hrs)
5. Summarize findings in EP verification matrix

**Post-Audit:**
- Implement authorization checks if gaps found
- Execute bypass path testing
- Verify fail-closed behavior

---

## GAP #3: ROUTE 7 — Recovery Procedures (HUMAN GATE DECISION)

### Identification

**Audit Finding:** No formal recovery procedures defined for 9 failure scenarios.

**Affected ROUTE:** ROUTE 7 (Recovery & Rollback)

**Current State:**
- Idempotency support exists (INSERT OR IGNORE)
- Hash chain enables detection (via integrity.py)
- No timeout handling found
- No retry mechanism found
- No rollback procedures found
- No recovery validation procedures found

### Failure Scenarios Requiring Decision

| Scenario | Current Behavior | Required Behavior | Decision |
|---|---|---|---|
| **Event timeout** | Unknown | Retry N times, then escalate | Design needed |
| **Event write failure** | Unknown | Retry with backoff, escalate on exhaustion | Design needed |
| **Decision write failure** | Unknown | Escalate immediately | Design needed |
| **Partial write** | Detected (trace_id NULL) | Forward-roll or rollback? | Decision needed |
| **Retry exhaustion** | Not handled | Escalate to Human Gate | Design needed |
| **Orphan creation** | Not detected | Detection procedure + recovery | Design needed |
| **Rollback** | Partial capability | Full rollback to consistent state | Design needed |
| **Recovery failure** | Not handled | Alert and escalate | Design needed |
| **Recovery verification** | Possible (hash chain) | Automated verification procedure | Design needed |

### What CAN Be Done Without Human Gate

✓ Analyze current idempotency support
✓ Document potential failure modes
✓ Design detection procedures for each scenario
✓ Propose recovery strategies (candidates A/B/C)
✓ Estimate recovery time bounds
✓ Design test harnesses for failure scenarios

### What CANNOT Be Done Without Human Gate

❌ Finalize recovery procedures (affects authorization semantics)
❌ Implement automatic rollback
❌ Define escalation triggers
❌ Change retry behavior affecting decisions
❌ Implement recovery validation that affects authorization

### Estimated Effort

| Activity | Effort | Authority |
|----------|--------|-----------|
| Failure mode analysis | 2 hours | Implementation |
| Current idempotency audit | 1.5 hours | Implementation |
| Detection procedure design | 2 hours | Implementation |
| Recovery strategy candidates (A/B/C) | 3 hours | Implementation |
| Time bound estimation | 1.5 hours | Implementation |
| Test harness design (9 scenarios) | 4 hours | Implementation |
| **Subtotal (Pre-Decision)** | **14 hours** | Can proceed now |
| Human Gate Decision | - | Recovery procedure selection |
| Implementation | 4-8 hours | After decision |
| **Total** | **18-22 hours** | |

### Recommendation

**Immediate Action (Implementation Authorization):**
1. Analyze each failure scenario (2 hrs)
2. Audit current idempotency mechanisms (1.5 hrs)
3. Design detection procedures (2 hrs)
4. Propose 2-3 recovery strategies per scenario (3 hrs)
5. Estimate recovery time bounds (1.5 hrs)
6. Design test harnesses for all scenarios (4 hrs)
7. Submit recovery strategy candidates to Human Gate

**Post-Decision:**
- Implement approved recovery procedures
- Test all 9 scenarios with failure injection
- Verify recovery time bounds
- Document recovery validation procedures

---

## GAP #4: ROUTE 8 — Monitoring Framework (IMPLEMENTATION AUTHORIZATION)

### Identification

**Audit Finding:** No monitoring framework exists to observe ROUTE status values without creating authorization bypass.

**Affected ROUTE:** ROUTE 8 (Monitoring & Observability)

**Current State:**
- Event records exist (observable if authorized)
- Integrity signatures exist (verifiable if authorized)
- State reconstruction capability exists
- No aggregating monitoring system
- No ROUTE status metrics
- No monitoring authorization boundary

### What Needs to Be Designed

| Capability | Current | Required | Work Type |
|---|---|---|---|
| **Route 1 Status** | No aggregator | Timestamp ordering metric | Design |
| **Route 2 Status** | No aggregator | Persistence verification metric | Design |
| **Route 3 Status** | No aggregator | Decision-event binding metric | Design |
| **Route 4 Status** | No auditor | Role authority usage audit | Design |
| **Route 5 Status** | No auditor | Enforcement point invocation audit | Design |
| **Route 6 Status** | No auditor | Trace linkage verification audit | Design |
| **Route 7 Status** | No auditor | Recovery success rate metric | Design |
| **Route 8 Status** | No meta-monitor | Monitoring system health metric | Design |
| **Status distinction** | No logic | PASS vs FAIL vs UNKNOWN vs NOT_PROVEN | Design |
| **Monitoring authorization** | Unknown risk | Monitoring ≠ Authorization bypass | Design + verification |

### What CAN Be Done Without Human Gate

✓ Design monitoring metric definitions for each ROUTE
✓ Design status aggregation procedures
✓ Audit authorization boundaries in monitoring code
✓ Propose monitoring system architecture (A/B/C candidates)
✓ Identify false positive/negative scenarios
✓ Design monitoring test harnesses

### What CANNOT Be Done Without Human Gate

❌ Implement monitoring system
❌ Collect status metrics automatically
❌ Create monitoring dashboards or reports
❌ Grant monitoring access to unauthorized parties

### Estimated Effort

| Activity | Effort | Authority |
|----------|--------|-----------|
| ROUTE status metric definitions | 2 hours | Implementation |
| Aggregation procedure design | 2 hours | Implementation |
| Authorization boundary analysis | 2 hours | Implementation |
| Monitoring system architecture design | 2 hours | Implementation |
| False positive/negative assessment | 1 hour | Implementation |
| Test harness design | 2 hours | Implementation |
| **Total** | **11 hours** | Can proceed now |

### Recommendation

**Immediate Action (Implementation Authorization):**
1. Define ROUTE status metrics (2 hrs)
2. Design aggregation procedures (2 hrs)
3. Audit authorization boundaries in monitoring (2 hrs)
4. Propose monitoring system architectures (2 hrs)
5. Assess false positive/negative risks (1 hr)
6. Design test harnesses (2 hrs)

**Post-Design:**
- Submit monitoring system design for review
- Implement if approved
- Test authorization boundary preservation
- Verify no monitoring bypass paths

---

## Summary Table: All 4 Gaps

| Gap # | ROUTE | Issue | Authority Required | Pre-Decision Work (hrs) | Total Effort (hrs) |
|-------|-------|-------|---|---|---|
| #1 | 4 | Role registry | **Human Gate** | 7 | 9 |
| #2 | 5 | EP verification | Implementation | 10.5 | 10.5 |
| #3 | 7 | Recovery procedures | **Human Gate** | 14 | 18-22 |
| #4 | 8 | Monitoring design | Implementation | 11 | 11 |
| | | | | **42.5 hours** | **48.5-52.5 hours** |

---

## Decision Readiness Summary

### What Can Proceed Immediately (Implementation Authorization)

**Gaps #2 & #4** (21.5 hours of work)
- ROUTE 5 enforcement point verification
- ROUTE 8 monitoring framework design

### Awaiting Human Gate Decision

**Gaps #1 & #3** (dependent on decisions)
- ROUTE 4 role authority decision
- ROUTE 7 recovery procedures decision

### Recommended Sequence

1. **Now:** Complete Gaps #2 & #4 pre-decision work (21.5 hrs)
2. **Then:** Submit Gap #1 role registry candidates to Human Gate
3. **Then:** Submit Gap #3 recovery procedure candidates to Human Gate
4. **If Approved:** Implement all 4 gaps (8-10 hrs)
5. **Then:** Execute full test harnesses and collect evidence
6. **Finally:** Submit to Human Gate for C2-b READY decision

---

**Audit Authority:** Implementation Authorization (Pre-Decision Phase)
**Custodian:** KUROKO Monitor (Claude-Haiku-4.5)
**Event ID:** E20260912_511275716f9af
**Next Step:** Gap Resolution & Evidence Collection

