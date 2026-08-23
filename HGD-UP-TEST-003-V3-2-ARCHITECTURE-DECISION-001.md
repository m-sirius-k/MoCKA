# HGD-UP-TEST-003-V3-2-ARCHITECTURE-DECISION-001
## Human Gate Decision Package: V3.2 Evidence Recording Architecture Direction

**Document Classification:** DECISION GATE SUBMISSION

**Issue ID:** HGD-UP-TEST-003-V3-2-ARCHITECTURE-DECISION-001

**Authority:** Kimura Human Gate

**Status:** AWAITING DECISION

**Decision Date Required:** [HUMAN GATE DECISION]

**Submitted By:** Claude (Haiku 4.5)

**Submission Date:** 2026-08-23

---

## Executive Summary for Human Gate

V3.2 Evidence Recording validation identified fundamental runtime implementation gaps. This package presents architectural direction options for Human Gate decision.

**Key Issue:** All 4 validation tests (E1-E4) fail due to missing Evidence State Machine runtime, not design defects.

**Decision Required On:** Whether to extend current V3 architecture (Option B) or redesign (Option C), or accept observation-only mode (Option A).

**Recommendation by Analyst:** Option B (Evidence Runtime Extension) - achieves UP-TEST-003 execution in ~10-15 days with contained scope.

---

## Part 1: V3.2 Validation Results Summary

### Test Execution Results

| Test | Title | Result | Severity |
|------|-------|--------|----------|
| E1 | Evidence State Representation | FAIL | CRITICAL |
| E2 | UNKNOWN Preservation Test | FAIL | CRITICAL |
| E3 | Open Dependency Tracking | FAIL | CRITICAL |
| E4 | Evidence Record Reproduction | FAIL | CRITICAL |

### Pass Criteria
```
V3.2 VERIFIED requires:
  [✓] All Evidence States Recordable              → FAILED
  [✓] UNKNOWN Preserved                          → FAILED
  [✓] Open Dependency Maintained                 → FAILED
  [✓] State Transition Replay Possible           → FAILED
```

### Final Verdict
**V3.2 Status: NOT READY**

**Readiness:** 30% (Design only; runtime unimplemented)

**Current Architecture Capability:**
```
Schema Design (WP-Schema-01):           DONE
Evidence Collection:                    DONE
State Machine Runtime:                  MISSING
Dependency Graph:                       MISSING
Replay Engine:                          MISSING
Invariant Enforcement:                  MISSING
Observation Tooling:                    MISSING
```

---

## Part 2: Gap Classification Summary

### Primary Classification
**Type B - Runtime Implementation Gap**

All 4 test failures trace to missing code, not design defects.

### Secondary Classification
**Type C - Observation Tooling Gap**

Monitoring and testing infrastructure absent.

### Gap Details by Test

#### E1: Evidence State Representation
- **Schema:** DEFINED (governance/write_path/evidence/schema.py)
- **Runtime:** MISSING
- **Missing:** State enum, state_history tracking, transition recording
- **Severity:** CRITICAL - blocks all downstream tests

#### E2: UNKNOWN Preservation
- **Schema:** DEFINED (partial - no UNKNOWN state)
- **Runtime:** MISSING
- **Missing:** Invariant enforcement, state validation
- **Severity:** CRITICAL - governance compliance requirement

#### E3: Open Dependency Tracking
- **Schema:** NOT DEFINED
- **Runtime:** NOT IMPLEMENTED
- **Missing:** DependencyEdge table, traversal APIs, cycle detection
- **Severity:** CRITICAL - dependency resolution broken

#### E4: Evidence Record Reproduction
- **Schema:** NOT DEFINED
- **Runtime:** NOT IMPLEMENTED
- **Missing:** Replay engine, state_at(timestamp), transition application
- **Severity:** CRITICAL - audit trail verification broken

### Impact Scope

**Systems Unable to Operate:**
- TIC Layer 1 (tech_watcher.py) - cannot track UNKNOWN dependencies
- TIC Layer 3 (impact_analyzer.py) - requires dependency graph
- PHI-OS Event Gate - cannot filter by evidence state
- Governance runtime - cannot enforce state invariants
- Audit compliance - cannot verify state history

**Workaround Feasibility:** NONE ACCEPTABLE
- All proposed workarounds violate governance system requirements
- Evidence state management is foundational - cannot hack around

---

## Part 3: Current Architecture Shortfalls

### Architecture Model (Current State)

```
Current V3 Architecture Layers:
┌─────────────────────────────────┐
│  Governance Runtime (audit)     │  ← Can log events
├─────────────────────────────────┤
│  Evidence Collection             │  ← Can capture scenarios
├─────────────────────────────────┤
│  WP-Schema-01 (Evidence Schema)  │  ← Fixed scenario schema
├─────────────────────────────────┤
│  AuditStore (jsonl)              │  ← Immutable log storage
└─────────────────────────────────┘
```

### Missing Layers (Required for V3.2)

```
Required but Missing:
┌─────────────────────────────────┐
│  State Machine Runtime           │  ← apply_transition()
├─────────────────────────────────┤
│  Dependency Graph Manager        │  ← traversal, cycle detection
├─────────────────────────────────┤
│  Evidence Replay Engine          │  ← state_at(timestamp)
├─────────────────────────────────┤
│  Invariant Enforcement           │  ← transition validation
├─────────────────────────────────┤
│  Extended Evidence Schema        │  ← state_history field
└─────────────────────────────────┘
```

### Architectural Gaps

**Gap 1: No State Machine**
- Current: Binary validation_evidence: {scope: bool}
- Required: State enum + state_history tracking
- Impact: Cannot represent PARTIAL/VERIFIED/UNKNOWN transitions

**Gap 2: No Dependency Graph**
- Current: Evidence records independent; no links
- Required: DependencyEdge table + traversal APIs
- Impact: Cannot track blocking dependencies

**Gap 3: No Replay Engine**
- Current: AuditStore provides immutable log only
- Required: state_at(timestamp), apply_transition() functions
- Impact: Cannot reconstruct state from history

**Gap 4: No Invariant Enforcement**
- Current: No validation of state transitions
- Required: Transition guard logic + blocking rules
- Impact: Cannot enforce UNKNOWN preservation rule

**Gap 5: No Observation Tooling**
- Current: No automated test suite for evidence state
- Required: Unit tests, integration tests, compliance checks
- Impact: Cannot verify correctness at scale

---

## Part 4: Decision Options Presented

### Option A: V3.2 Observation Only Mode
**Also Known As:** "Design Verification Without Execution"

#### Scope
- Validate UP-TEST-003 requirements against current design
- Document architectural capabilities vs. requirements
- Accept evidence recording as "design-verified" without runtime
- Change UP-TEST-003 scope to exclude state machine tests

#### Implementation Effort
- **Design Review:** 2-3 days
- **Documentation:** 1-2 days
- **Scope Negotiation:** 1 day
- **Total:** ~4-5 days

#### Conditions
```
[✓] No implementation work
[✓] Design verification only
[✓] UP-TEST-003 scope reduction (remove E2, E3, E4)
[✓] Mark V3.2 as "Design-Verified, Execution Deferred"
```

#### Outcomes
```
V3.2 Status:        DESIGN VERIFIED
UP-TEST-003:        PARTIAL (E1 only)
Governance Impact:  State machine NOT enforced; compliance gap
Incident Risk:      HIGH - evidence state not protected
Timeline:           4-5 days to completion
```

#### Trade-offs

**Advantages:**
- Quickest path to "V3.2 DONE" (4-5 days)
- No implementation risk
- Design quality validated independently

**Disadvantages:**
- State machine never implemented → governance gap persists
- UP-TEST-003 cannot fully execute
- Dependency tracking remains broken
- Audit compliance unverified
- Incident detection cannot track UNKNOWN states
- Production risk: UNKNOWN states may disappear undetected

#### Risk Assessment
```
Risk Level:         HIGH
Justification:      Governance core (state invariants) not enforced
Mitigation:         None (design-only mode)
Escalation Path:    Issue flagged to architecture review
```

---

### Option B: Evidence Runtime Extension
**Also Known As:** "Targeted Runtime Implementation"

#### Scope
Implement missing runtime layers while maintaining current architecture:

**Phase 1: State Machine (3-5 days)**
```
New Data Structure: EvidenceStateRecord
  - evidence_id (FK)
  - current_state: Enum[PARTIAL, VERIFIED, UNKNOWN]
  - state_history: List[StateTransition]
  - blocking_evidence: List[evidence_id]
  - changed_at, changed_by, reason

New Function: apply_transition(state, event) -> Result[new_state, error]
  - Enforce valid transitions
  - Record transition reason
  - Update state_history

Migration: Backfill state_history from AuditStore
```

**Phase 2: Dependency Graph (3-4 days)**
```
New Data Structure: DependencyEdge
  - dependency_id (unique)
  - source_evidence, target_evidence (FK)
  - status: Enum[OPEN, RESOLVED]
  - resolution_evidence (optional)

New Function: transitive_dependencies(evidence_id) -> [evidence_id]
  - Depth-first closure computation
  - Cycle detection

New Function: blocking_path(evidence_id) -> [[dep1, dep2, ...], ...]
  - Find all chains blocking resolution
```

**Phase 3: Replay Engine (2-3 days)**
```
New Function: state_at(evidence_id, timestamp) -> EvidenceState
  - Replay all transitions up to timestamp
  - Return computed state

New Function: replay_sequence(evidence_id, [events]) -> final_state
  - Apply sequence of transitions
  - Verify final matches expected

Validation: verify_state_reproducibility(initial, events, expected)
  - Assertion function for tests
```

**Phase 4: Invariant Enforcement (1-2 days)**
```
New Function: validate_transition(current_state, target_state, reason)
  - Enforce: UNKNOWN only with blocking_evidence
  - Enforce: No promotion without evidence source
  - Enforce: Dependency consistency

New Function: try_transition(state, target) -> Result[new_state, error]
  - Atomic operation with validation
  - Rollback on error
```

#### Implementation Effort
```
Phase 1 (State Machine):         3-5 days
Phase 2 (Dependency Graph):      3-4 days
Phase 3 (Replay Engine):         2-3 days
Phase 4 (Invariant Enforcement): 1-2 days
Unit Testing:                    2-3 days
Integration Testing:             2-3 days
Code Review & Fixes:             1-2 days
──────────────────────────────────────────
TOTAL:                           17-22 days (conservative)
OPTIMISTIC:                      12-15 days

Timeline to Execution:           ~2-3 weeks
```

#### Conditions
```
[✓] Extend current V3 architecture
[✓] Add 4 new layers (State Machine, Dependency, Replay, Invariant)
[✓] Maintain AuditStore immutability
[✓] Preserve existing EvidenceCollection behavior
[✓] All new code tested with unit & integration tests
```

#### Outcomes
```
V3.2 Status:        VERIFIED (all 4 tests pass)
UP-TEST-003:        EXECUTABLE (full scope)
Governance Impact:  State machine enforced; compliance achieved
Incident Risk:      LOW - evidence state protected
Timeline:           2-3 weeks to completion + re-validation
```

#### Trade-offs

**Advantages:**
- Completes V3.2 fully (all 4 tests pass)
- Enables UP-TEST-003 full execution
- Achieves governance compliance for state invariants
- Moderate implementation scope (17-22 days)
- Low architectural risk (extends current model)
- Fits within normal development sprint

**Disadvantages:**
- Requires 2-3 weeks engineering effort
- New code introduces testing burden
- Requires code review process
- May uncover edge cases requiring iteration

#### Risk Assessment
```
Risk Level:         MODERATE
Technical Risk:     LOW (straightforward implementation)
Schedule Risk:      MODERATE (2-3 weeks elapsed time)
Quality Risk:       LOW (testable implementation)

Mitigation Strategies:
  1. Implement in phases (Phase 1 unblocks tests)
  2. Unit test each phase before proceeding
  3. Code review required before merge
  4. Integration tests before re-validation
```

---

### Option C: Architecture Redesign
**Also Known As:** "Core System Overhaul"

#### Scope
Comprehensive redesign addressing architectural fundamentals:

**Redesign Targets:**
```
Core Layer (7 components):
  1. Governance Event model (add state tracking)
  2. Evidence collection (add state machine)
  3. Audit logging (add temporal queries)
  4. Runtime execution (add replay capability)
  5. Schema management (add dependency schema)
  6. Validation framework (add invariant enforcement)
  7. Store implementation (add query optimization)

Meta Layer (6 components):
  1. Governance runtime (redesign architecture)
  2. TIC integration (redesign for state)
  3. PHI-OS event gating (redesign filters)
  4. Incident detection (redesign for UNKNOWN states)
  5. Audit compliance (redesign verification)
  6. Governance seal (redesign state inclusion)

Outer Layer (2 components):
  1. Evidence API (new state query endpoints)
  2. Dependency API (new graph traversal endpoints)
```

#### Implementation Effort
```
Architecture Design:             2-3 weeks
Schema Redesign:                 2-3 weeks
Core Implementation:             4-6 weeks
Integration & Testing:           3-4 weeks
Code Review & Iteration:         2-3 weeks
──────────────────────────────────────────
TOTAL:                           13-19 weeks (3-4.5 months)

Timeline to Execution:           ~1 quarter
```

#### Conditions
```
[✓] Redesign 7 core, 6 meta, 2 outer components
[✓] New governance architecture with state machine
[✓] Comprehensive testing at all layers
[✓] Architecture review & approval required
[✓] Full integration with existing systems
```

#### Outcomes
```
V3.2 Status:        REDESIGNED (new architecture)
UP-TEST-003:        EXECUTABLE (new design)
Governance Impact:  State machine native to architecture
Incident Risk:      VERY LOW - robust system design
Timeline:           ~13-19 weeks to completion
```

#### Trade-offs

**Advantages:**
- Comprehensive architectural solution
- Likely more elegant/scalable design
- Addresses root causes, not symptoms
- Better long-term maintainability
- Stronger governance foundation

**Disadvantages:**
- Very long timeline (~3-4.5 months)
- High implementation complexity
- High risk of regressions
- Requires extensive testing
- Delays UP-TEST-003 execution significantly
- Uncertain scope (design may uncover issues)
- Resource-intensive (blocks other work)

#### Risk Assessment
```
Risk Level:         HIGH
Technical Risk:     HIGH (large-scope redesign)
Schedule Risk:      HIGH (3-4 month timeline)
Quality Risk:       MODERATE (extensive testing, but high complexity)
Resource Risk:      HIGH (blocks other development)

Mitigation Required:
  1. Architecture review before implementation
  2. Phased rollout with integration gates
  3. Extensive regression testing
  4. Incremental validation (not all-at-once)
```

---

## Part 5: Comparative Analysis

### Timeline Comparison

```
Option A (Observation Only):    4-5 days to completion
Option B (Runtime Extension):   2-3 weeks to execution
Option C (Architecture Redesign): ~3-4 months to execution
```

### Effort Comparison

```
Option A: ~20 person-days (design review + docs)
Option B: ~40-50 person-days (implementation + testing)
Option C: ~300-400 person-days (redesign + implementation)
```

### Risk Profile Comparison

```
                    Architectural  Schedule  Quality  Governance
                    Risk           Risk      Risk     Coverage
Option A            LOW            LOW       LOW      INCOMPLETE
Option B            LOW            MODERATE  LOW      COMPLETE
Option C            HIGH           HIGH      MODERATE COMPLETE
```

### UP-TEST-003 Impact

```
Option A: PARTIAL (E1 only; scoped-down test)
Option B: FULL EXECUTION (all 4 tests pass)
Option C: FULL EXECUTION (redesigned system)
```

### Governance Compliance

```
Option A: NOT COMPLIANT (state machine unimplemented)
Option B: COMPLIANT (state machine implemented)
Option C: COMPLIANT (native architecture)
```

---

## Part 6: Analyst Recommendation

### Recommended Path: Option B (Evidence Runtime Extension)

**Rationale:**

1. **Achieves All Objectives**
   - Completes V3.2 validation (all 4 tests pass)
   - Enables UP-TEST-003 full execution
   - Implements governance state machine
   - Maintains governance compliance

2. **Reasonable Timeline**
   - 2-3 weeks to execution-ready
   - Fits within normal development cycle
   - Allows parallel work on other components

3. **Controlled Risk**
   - Extends current architecture (low architectural risk)
   - Straightforward implementation (well-defined requirements)
   - Testable at each phase (quality assurance)
   - No redesign rework (contained scope)

4. **Cost-Benefit**
   - Modest effort (40-50 person-days)
   - High value (complete governance system)
   - Justifiable resource allocation
   - Clear ROI (enables UP-TEST-003 execution)

### Not Recommended: Option A
- Defers implementation without solving the problem
- Leaves governance gap unaddressed
- Scope reduction for UP-TEST-003 is unsatisfying
- Technical debt accumulates (state machine always needed)

### Not Recommended: Option C
- Over-engineered for current scope
- Extremely long timeline (3-4 months)
- High complexity increases risk
- Better addressed after V3 completion if architectural review identifies need

---

## Part 7: Next Steps (Conditional on Decision)

### If Option A Selected: Observation Only Mode
```
1. Prepare design verification report (2 days)
2. Negotiate UP-TEST-003 scope reduction (1 day)
3. Document architecture-to-requirements mapping (2 days)
4. Submit V3.2 as "Design-Verified, Execution Deferred" (1 day)
5. Begin planning V3 Architecture Review (TBD)

Timeline: 4-5 days to V3.2 completion
Next Gate: V3 Architecture Review (separate decision)
```

### If Option B Selected: Runtime Extension
```
Phase 1: State Machine Implementation (3-5 days)
  ├─ Define EvidenceStateRecord schema
  ├─ Implement apply_transition() function
  ├─ Unit tests
  └─ Code review

Phase 2: Dependency Graph (3-4 days)
  ├─ Define DependencyEdge schema
  ├─ Implement traversal APIs
  ├─ Cycle detection
  └─ Unit tests

Phase 3: Replay Engine (2-3 days)
  ├─ Implement state_at() function
  ├─ Implement replay_sequence()
  └─ Unit tests

Phase 4: Invariant Enforcement (1-2 days)
  ├─ Implement transition validation
  ├─ Guard logic
  └─ Unit tests

Testing & Review (4-5 days)
  ├─ Integration tests
  ├─ Code review
  └─ Fixes

Re-validation (2-3 days)
  ├─ Re-run V3.2 tests
  └─ Verify all pass

Timeline: 2-3 weeks to V3.2 VERIFIED + UP-TEST-003 execution
Next Gate: V3.3 Validation (upon completion)
```

### If Option C Selected: Architecture Redesign
```
Step 1: Architecture Design (2-3 weeks)
  ├─ Design review meetings
  ├─ Draft proposals
  ├─ Stakeholder feedback
  └─ Final approval

Step 2: Implementation (7-10 weeks)
  ├─ Core layer (4-6 weeks)
  ├─ Meta layer (2-3 weeks)
  ├─ Outer layer (1-2 weeks)
  └─ Integration (ongoing)

Step 3: Testing & Validation (3-4 weeks)
  ├─ Unit testing
  ├─ Integration testing
  ├─ Regression testing
  └─ V3.2 re-validation

Step 4: Review & Deployment (1-2 weeks)
  ├─ Code review
  ├─ Architecture review
  └─ Deployment planning

Timeline: ~3-4 months to redesigned V3.2 + UP-TEST-003 execution
Next Gate: Architecture review before implementation
```

---

## Part 8: Decision Gate Information

### Decision Authority
**Kimura Human Gate**

### Decision Required On
1. Which option (A, B, or C)?
2. If Option B: approval to proceed with phased implementation?
3. If Option B: resource allocation for 2-3 week timeline?
4. If Option A or C: rationale for selection and next steps?

### Supporting Documentation
- ✓ UP_TEST_003_V3_2_EVIDENCE_RECORDING_VALIDATION.md (test results)
- ✓ UP_TEST_003_V3_2_GAP_CLASSIFICATION.md (gap analysis)
- ✓ This package (decision options)

### Information Required for Decision
```
[✓] Test results (provided)
[✓] Gap analysis (provided)
[✓] Option analysis (provided)
[✓] Timeline comparison (provided)
[✓] Risk assessment (provided)
[✓] Effort estimates (provided)
[✓] Analyst recommendation (provided)
```

### Timeline for Decision
**Required:** Before proceeding with any path

**Suggested:** Within 2-3 business days to maintain project momentum

### Escalation Path
If unclear: Request clarification from Analyst (Claude)

---

## Part 9: Sequence Upon Decision

### If Decision Made For Option A or B: Proceed Immediately
```
1. Record decision in Decision Ledger
2. Begin Phase 1 (if Option B)
3. Continue with planned timeline
```

### If Decision Made For Option C: Hold for Architecture Review
```
1. Record decision in Decision Ledger
2. Schedule Architecture Design phase
3. Suspend Option B work pending design completion
```

### If Decision Deferred: Status Hold
```
1. Record "AWAITING DECISION" status
2. Maintain current timeline readiness (Option B-ready)
3. Escalate to decision authority if overdue
```

---

## Appendix A: Implementation Checklist (Option B)

```
Phase 1: State Machine
[ ] Define EvidenceStateRecord TypedDict
[ ] Create state_history field schema
[ ] Implement StateTransition record type
[ ] Write apply_transition(state, event) function
[ ] Add transition validation logic
[ ] Unit tests (positive + negative cases)
[ ] Code review & approval
[ ] Merge to development

Phase 2: Dependency Graph
[ ] Define DependencyEdge TypedDict
[ ] Create dependency_graph table schema
[ ] Implement transitive_dependencies() function
[ ] Implement cycle_detection() algorithm
[ ] Add bidirectional edge maintenance
[ ] Unit tests (depth 1-3 paths)
[ ] Code review & approval
[ ] Merge to development

Phase 3: Replay Engine
[ ] Implement state_at(timestamp) function
[ ] Implement replay_sequence(events) function
[ ] Add temporal query support
[ ] Implement state reconstruction logic
[ ] Unit tests (replay correctness)
[ ] Code review & approval
[ ] Merge to development

Phase 4: Invariant Enforcement
[ ] Implement validate_transition() function
[ ] Add UNKNOWN preservation check
[ ] Add evidence source requirement check
[ ] Add dependency consistency check
[ ] Unit tests (invariant violations)
[ ] Code review & approval
[ ] Merge to development

Testing & Validation
[ ] Integration test suite
[ ] End-to-end evidence flow test
[ ] Re-run V3.2 test scenarios (E1-E4)
[ ] All 4 tests PASS verification
[ ] Code coverage review (>90%)
[ ] Performance baseline established

Final Review
[ ] Architecture review (code structure)
[ ] Compliance review (governance requirement)
[ ] Security review (no data leaks)
[ ] Documentation review (design docs)
```

---

## Appendix B: Resource Requirements (Option B)

```
Role: Senior Developer (Architecture-aware)
Hours: 160-200 hours (4-5 weeks @ 40 hrs/week)

Skills Required:
- Python/Schema design
- State machine patterns
- Graph algorithms
- Test-driven development
- Code review practices

Parallel Support:
- Code reviewer: 20-30 hours
- QA tester: 10-15 hours
- Tech lead oversight: 10-15 hours

Total: 200-270 hours (5-7 weeks of effort, 2-3 weeks elapsed)
```

---

## Document Approval Gate

**This document requires Human Gate decision before proceeding.**

**Awaiting signature/approval:**
- [ ] Kimura Human Gate - Option Selection & Timeline Approval
- [ ] Architecture Review - If Option C selected
- [ ] Resource Allocation - If Option B selected

---

**End of Human Gate Decision Package**

---

## Document History

| Date | Version | Status |
|------|---------|--------|
| 2026-08-23 | 1.0 | Submitted for Human Gate Decision |

**Submission Authority:** Claude (Haiku 4.5)
**Related Decision Gate:** HGD-UP-TEST-003-V3-2-ARCHITECTURE-DECISION-001
