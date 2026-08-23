# UP-TEST-003: V3.2 Gap Classification Record

## Document Header

**Classification Date:** 2026-08-23

**Related Validation:** UP_TEST_003_V3_2_EVIDENCE_RECORDING_VALIDATION.md

**Classification Status:** FORMAL RECORD

**Decision Scope:** Evidence State Management Infrastructure Readiness

---

## Executive Summary

The V3.2 validation identified 4 critical test failures across evidence state management. This document formally classifies those failures into gap categories and assesses impact on UP-TEST-003 execution.

**Primary Classification:** B - Runtime Implementation Gap

**Secondary Classification:** C - Observation Tooling Gap

**Decision Position:** V3.2 = NOT READY; UP-TEST-003 = "V3改善判断待ち" (awaiting V3 improvement decision, NOT HOLD)

---

## Gap Classification Framework

### Category A: Framework Design Gap
**Definition:** Requirements exist, design is incomplete or conflicting

**Characteristics:**
- Schema/contract defined but incomplete
- Design contradicts implementation
- Architectural decision pending

### Category B: Runtime Implementation Gap
**Definition:** Design exists, code is missing or incomplete

**Characteristics:**
- API defined but no implementation
- Functions called but not implemented
- Data structures exist but no logic

### Category C: Observation Tooling Gap
**Definition:** Implementation exists, monitoring/testing infrastructure absent

**Characteristics:**
- Code runs but no instrumentation
- No metrics/logs to verify behavior
- Testing harness missing

### Category D: Test Preparation Gap
**Definition:** Feature works, but test cases are incomplete

**Characteristics:**
- Implementation passes manual checks
- Automated test suite incomplete
- Edge cases untested

---

## Gap Analysis by Test Item

### Test E1: Evidence State Representation

#### Finding (発見事項)
Evidence state transitions (PARTIAL → VERIFIED → UNKNOWN) cannot be recorded because:
1. Current schema defines only binary validation_evidence: {scope: bool}
2. No state enum (PARTIAL/VERIFIED/UNKNOWN) exists
3. No state_history tracking mechanism
4. No transition reason/timestamp recording

#### Classification
**Primary: B - Runtime Implementation Gap**

**Rationale:** WP-Schema-01 design exists (governance/write_path/evidence/schema.py), but state machine runtime is unimplemented.

Existing structures:
```python
RuntimeEvidenceRecord (schema defined)
  - record_id
  - source_event_range
  - hash
  - generated_at
  - immutable
```

Missing structures:
```python
EvidenceStateRecord (NOT DEFINED)
  - evidence_id
  - state: Enum[PARTIAL, VERIFIED, UNKNOWN]
  - state_history: List[StateTransition]
  - blocking_evidence: List[str]
  - transition_timestamp
  - transition_reason
```

#### Impact Scope (影響範囲)

**Direct Impact:**
- core_kernel/governance/self_verification/evidence.py:collect_evidence()
- governance/write_path/evidence/fixtures.py (test data)

**Indirect Impact:**
- Any feature depending on evidence state queries
- Governance audit trails (cannot timestamp state changes)
- Dependency resolution (cannot check "is Evidence-B UNKNOWN?")

**Systems Affected:**
- TIC Layer 1 (tech_watcher.py) - cannot track "UNKNOWN dependency" state
- PHI-OS Event Gate - cannot filter by evidence state
- Governance runtime - cannot enforce state invariants

#### UP-TEST-003 Impact (UP-TEST-003への影響)

**Blocking:** CRITICAL

UP-TEST-003 Procurement domain test cannot:
- Record evidence state transitions
- Validate UNKNOWN preservation invariant
- Query "what state is Evidence-B?"
- Block invalid transitions (UNKNOWN → VERIFIED without source)

**Cannot Proceed Without:** State machine runtime implementation

#### Workaround Possibility (回避可能性)

**Feasibility:** LOW

Potential workarounds:
1. Use AuditRecord event_type to encode state (hacky, not type-safe)
   - Encoding: event_type="evidence_state_PARTIAL", event_type="evidence_state_VERIFIED"
   - Problem: No schema validation; state not queryable
   - Risk: False state reports from audit log parsing errors

2. Use governance_event.validation_evidence dict as state proxy
   - Encoding: {"_state": "UNKNOWN", "scope1": False, "scope2": True}
   - Problem: Mixes data types; no state_history
   - Risk: Transitions not recorded; cannot audit who changed state

3. Store state in separate JSON file outside event system
   - Problem: Breaks immutable append-only invariant
   - Risk: State drifts from audit log; not recoverable

**Recommendation:** None of these workarounds acceptable. Require proper implementation.

#### Human Gate Decision Required (Human Gate判断必要性)

**Yes - CRITICAL**

Decision needed on:
1. Whether to implement EvidenceStateRecord as separate table or extend RuntimeEvidenceRecord
2. Whether to add state_history to audit flow or maintain separate ledger
3. Timeline for implementation (blocks UP-TEST-003)

---

### Test E2: UNKNOWN Preservation

#### Finding (発見事項)

Invariant "UNKNOWN state must not disappear" cannot be enforced because:
1. No persistent UNKNOWN state exists
2. No enforcement mechanism to prevent unsourced VERIFIED transitions
3. No bidirectional dependency tracking to detect missing evidence

#### Classification

**Primary: B - Runtime Implementation Gap**

**Secondary: C - Observation Tooling Gap**

**Rationale:**
- Implementation gap: No enforcement logic exists
- Observation gap: No monitoring to detect invariant violations

#### Impact Scope (影響範囲)

**Direct Impact:**
- Evidence state machine (missing)
- Dependency resolver (missing)
- Transition validator (missing)

**Indirect Impact:**
- Governance seal computation (cannot validate state invariants)
- Audit compliance (cannot prove "UNKNOWN never disappeared")
- Incident detection (cannot flag invalid state changes)

**Processes Affected:**
- UP-F002 UNKNOWN Preservation pattern enforcement
- Procurement evidence validation workflow
- Dependency resolution flow

#### UP-TEST-003 Impact (UP-TEST-003への影響)

**Blocking:** CRITICAL

Cannot test:
- "Evidence-B remains UNKNOWN after mutation"
- "Evidence-A stays VERIFIED while Evidence-B = UNKNOWN"
- Invariant: "Open Dependency maintains consistency"

#### Workaround Possibility (回避可能性)

**Feasibility:** VERY LOW

Manual enforcement:
1. Implement invariant checks in test harness only
   - Limitation: Not production-enforced; test-only protection
   - Risk: Production code may violate invariant

2. Add defensive checks in evidence query APIs
   - Limitation: Catches violations late, doesn't prevent
   - Risk: Silent data corruption possible if checks bypassed

**Recommendation:** Require proper invariant enforcement before testing.

#### Human Gate Decision Required (Human Gate判断必要性)

**Yes - CRITICAL**

Decision needed on:
1. Invariant enforcement level: prevent (transactions) vs. detect (monitoring)
2. Error handling: fail transaction vs. emit alert vs. both
3. Recovery strategy if invariant violated

---

### Test E3: Open Dependency Tracking

#### Finding (発見事項)

Dependency graph cannot be traversed across depth levels because:
1. No DependencyEdge relation/table exists
2. No transitive closure computation
3. No cycle detection algorithm
4. No bidirectional link maintenance

#### Classification

**Primary: B - Runtime Implementation Gap**

**Secondary: C - Observation Tooling Gap**

**Rationale:**
- Implementation gap: No dependency graph data structure
- Observation gap: No graph traversal APIs

#### Impact Scope (影響範囲)

**Direct Impact:**
- Dependency tracking system (missing)
- Transitive closure computation (missing)
- Cycle detection (missing)

**Indirect Impact:**
- Blocking dependency detection
- Impact analysis (cannot compute affected items)
- Evidence validation flow (cannot follow chains)

**Systems Affected:**
- TIC Layer 3 (impact_analyzer.py) - requires dependency graph
- Governance runtime - cannot follow blocking chains
- Incident detection - cannot trace root cause through dependencies

#### UP-TEST-003 Impact (UP-TEST-003への影響)

**Blocking:** CRITICAL

Cannot test:
- Depth 1 → Depth 2 → Depth 3 path preservation
- Transitive dependency resolution
- Cycle detection in procurement chains
- "resolve_chain(EVI-001) = [EVI-001, EVI-002, EVI-003, EVI-004]"

#### Workaround Possibility (回避可能性)

**Feasibility:** LOW

Limited workarounds:
1. Store dependency chain as JSON array in evidence record
   - Limitation: Static snapshot, not dynamic graph
   - Risk: Manual updates; inconsistency possible

2. Use governance_event fields to encode dependencies
   - Limitation: No graph structure; hard to query
   - Risk: Parsing errors; performance poor

3. Run external graph analysis tool (offline)
   - Limitation: Not integrated; eventual consistency
   - Risk: Stale data; not queryable in runtime

**Recommendation:** Require proper graph implementation.

#### Human Gate Decision Required (Human Gate判断必要性)

**Yes - CRITICAL**

Decision needed on:
1. Graph storage: separate DependencyEdge table vs. embedded in evidence record
2. Update semantics: immediate vs. eventually consistent
3. Cycle detection: blocking vs. warning

---

### Test E4: Evidence Record Reproduction

#### Finding (発見事項)

Final state cannot be reconstructed from initial state + transitions because:
1. No state_apply(state, event) → new_state function
2. No state_at(timestamp) query function
3. No transition_log indexed by evidence_id
4. No replay engine

#### Classification

**Primary: B - Runtime Implementation Gap**

**Secondary: C - Observation Tooling Gap**

**Rationale:**
- Implementation gap: Replay logic missing
- Observation gap: No indexed transition log

#### Impact Scope (影響範囲)

**Direct Impact:**
- Evidence replay system (missing)
- State reconstruction (missing)
- Temporal state queries (missing)

**Indirect Impact:**
- Audit trail verification (cannot replay)
- Governance seal validation (cannot check historical state)
- Incident forensics (cannot time-travel state)

**Processes Affected:**
- Evidence audit compliance
- Root cause analysis
- State history verification

#### UP-TEST-003 Impact (UP-TEST-003への影響)

**Blocking:** CRITICAL

Cannot test:
- "Final State = Initial State + Transitions + Decision Points"
- Replay sequence from log
- Verify state reproduction matches expected

#### Workaround Possibility (回避可能性)

**Feasibility:** VERY LOW

Pseudo-workarounds:
1. Store final state snapshot separately
   - Limitation: Cannot verify correctness; no replay
   - Risk: Snapshot stale; not reproducible

2. Manual verification of log entries
   - Limitation: Not automated; human error prone
   - Risk: Unscalable; not testable

**Recommendation:** Require proper replay implementation.

#### Human Gate Decision Required (Human Gate判断必要性)

**Yes - CRITICAL**

Decision needed on:
1. State storage: immutable snapshots vs. computed from log
2. Replay execution: lazy (on-demand) vs. eager (precomputed)
3. Consistency guarantee: strong (always correct) vs. eventual

---

## Summary: Gap Classification Table

| Test | Primary | Secondary | Severity | UP-TEST-003 Impact | Human Gate |
|------|---------|-----------|----------|-------------------|------------|
| E1: State Repr | B-Runtime | - | CRITICAL | BLOCKING | REQUIRED |
| E2: UNKNOWN Pres | B-Runtime | C-Tooling | CRITICAL | BLOCKING | REQUIRED |
| E3: Dependency | B-Runtime | C-Tooling | CRITICAL | BLOCKING | REQUIRED |
| E4: Replay | B-Runtime | C-Tooling | CRITICAL | BLOCKING | REQUIRED |

---

## Overall Status Assessment

### V3.2 Evidence Recording System

**Framework Maturity:** Design-Complete, Implementation-Incomplete

**Component Status:**
```
Schema Design (WP-Schema-01):           DONE
Evidence Collection (collect_evidence): DONE
State Machine Runtime:                  NOT DONE
Dependency Graph:                       NOT DONE
Replay Engine:                          NOT DONE
Invariant Enforcement:                  NOT DONE
Observation Tooling:                    NOT DONE
```

**Readiness Matrix:**
```
Architecture:   [=====] 100% (design complete)
Implementation: [==   ] 30% (collection only)
Testing:        [     ] 0% (blocked by implementation)
Operations:     [     ] 0% (blocked by implementation)
```

---

## Decision Record

### Current Position

**V3.2 Status:** NOT READY

**UP-TEST-003 Position:** NOT A HOLD CANDIDATE

**Classification:** "V3改善判断待ち" (Awaiting V3 Improvement Decision)

### Rationale

1. **Not HOLD:** HOLD assumes feature may be revived at current scope. V3.2 requires architectural changes, not minor fixes.

2. **V3改善判断待ち:** Requires decision on:
   - Whether to extend current WP-Schema-01 or redesign
   - Whether to add state machine to governance runtime
   - Timeline for implementation
   - Resource allocation

3. **Blocking Issues:** All 4 tests blocked by missing runtime implementation (B-type gaps). No workarounds acceptable for production governance system.

### Next Gate

**Human Gate Decision Required On:**

1. Architectural Decision
   - Extend WP-Schema-01 with state_machine field, OR
   - Create separate EvidenceStateRecord table

2. Implementation Timeline
   - Phase 1: State Machine (required before ANY testing)
   - Phase 2: Dependency Graph
   - Phase 3: Replay Engine
   - Phase 4: Observation Tooling

3. Resource Allocation
   - Estimated: 2-4 weeks for Phases 1-3
   - Estimated: 1-2 weeks for Phase 4

4. UP-TEST-003 Rescheduling
   - Cannot proceed until Phase 1 complete
   - Recommend deferral to next development cycle

---

## Appendix A: Gap Category Definitions (Reference)

### A - Framework Design Gap
Feature design incomplete; architectural decision pending.

**Examples:**
- Schema defined but contradicts implementation
- API contract unclear on edge cases
- Design review incomplete

**Resolution:** Complete design phase; human gate approval

### B - Runtime Implementation Gap
Design complete; implementation code missing or incomplete.

**Examples:**
- API defined; function stub missing implementation
- Data structure defined; initialization logic missing
- Algorithm designed; not coded

**Resolution:** Implement code; unit test; code review

### C - Observation Tooling Gap
Code exists and works; monitoring/testing infrastructure missing.

**Examples:**
- Function implemented; no test cases
- System runs; no logs/metrics
- Feature complete; no integration tests

**Resolution:** Add tests; add instrumentation; add monitoring

### D - Test Preparation Gap
Feature works; test suite incomplete for edge cases.

**Examples:**
- Happy path tested; error paths not tested
- Single-user scenario tested; multi-user not tested
- Normal operation tested; failure modes not tested

**Resolution:** Expand test suite; edge case coverage

---

## Appendix B: Impact Analysis Detail

### Scope of Implementation Required

**Minimum Viable Implementation (MVI) for UP-TEST-003:**

```
1. EvidenceStateRecord Table
   Columns:
   - evidence_id (FK to RuntimeEvidenceRecord)
   - current_state: Enum[PARTIAL, VERIFIED, UNKNOWN]
   - previous_state: Enum[PARTIAL, VERIFIED, UNKNOWN]
   - changed_at: datetime
   - changed_by: string (actor)
   - reason: string
   - blocking_evidence: List[evidence_id]

2. DependencyEdge Table
   Columns:
   - dependency_id: string (unique)
   - source_evidence: string (FK)
   - target_evidence: string (FK)
   - status: Enum[OPEN, RESOLVED]
   - created_at: datetime
   - resolved_at: datetime (nullable)
   - resolution_evidence: string (FK, nullable)

3. StateTransition Function
   Signature: apply_transition(state, event) -> new_state
   Logic: Enforce valid transitions; record reason

4. DependencyTraversal Function
   Signature: transitive_dependencies(evidence_id) -> [evidence_id]
   Logic: Depth-first or breadth-first closure

5. ReplayEngine Function
   Signature: state_at(evidence_id, timestamp) -> state
   Logic: Replay events up to timestamp; return state
```

**Estimated Implementation Effort:**
- Schema design & migration: 2-3 days
- Runtime functions: 3-5 days
- Unit tests: 2-3 days
- Integration tests: 2-3 days
- **Total: 10-15 days**

---

## Document History

| Date | Version | Status |
|------|---------|--------|
| 2026-08-23 | 1.0 | Initial gap classification |

---

## Approval Gate

**This document awaits Human Gate review before:**
1. Committing to UP-TEST-003 rescheduling
2. Allocating resources to V3 implementation
3. Proceeding with evidence state feature development

**Required Approval Sign-off:**
- [ ] Architecture Review (design feasibility)
- [ ] Resource Planning (timeline & effort)
- [ ] UP-TEST-003 Rescheduling Decision

---

**End of Document**
