# UP-TEST-003: V3.2 Evidence Recording Format Validation

## Executive Summary

This document validates the Evidence state management capability against UP-TEST-003 execution requirements, focusing on the preservation of PARTIAL, VERIFIED, and UNKNOWN states within evidence recordings. The validation follows the UP-F002 UNKNOWN Preservation pattern for the Procurement domain.

---

## Validation Metadata

**V3.2 Status:**
- [ ] VERIFIED
- [ ] PARTIAL
- [x] FAILED

**Validation ID:** VAL_20260823_V3_2_001

**Date:** 2026-08-23

**Observer:** Claude (Haiku 4.5)

---

## Evidence State Representation (E1)

### Requirement
Verify that evidence states can be recorded and transitioned through the following sequences:
- PARTIAL → VERIFIED → UNKNOWN
- PARTIAL → UNKNOWN

### Test Specification

#### Required Record Fields
```
- Evidence ID
- Evidence Type
- Current State
- Previous State
- Transition Time
- Transition Reason
- Actor
```

#### State Transition Diagram
```
PARTIAL (initial state)
  |
  +-- [transition 1] --> VERIFIED
  |                        |
  |                        +-- [transition 2] --> UNKNOWN
  |
  +-- [transition 3] --> UNKNOWN (direct)
```

### Test Execution

#### Scenario 1: PARTIAL → VERIFIED → UNKNOWN
```json
{
  "evidence_id": "EVI-001-PROC",
  "evidence_type": "Procurement_Document",
  "transitions": [
    {
      "sequence": 1,
      "from_state": "PARTIAL",
      "to_state": "VERIFIED",
      "timestamp": "2026-08-23T09:00:00Z",
      "reason": "All mandatory procurement fields validated against schema",
      "actor": "Governance_Runtime"
    },
    {
      "sequence": 2,
      "from_state": "VERIFIED",
      "to_state": "UNKNOWN",
      "timestamp": "2026-08-23T09:15:00Z",
      "reason": "Upstream document reference broken - pending revalidation",
      "actor": "TIC_Layer_1_WatchDog"
    }
  ]
}
```

#### Scenario 2: PARTIAL → UNKNOWN (Direct)
```json
{
  "evidence_id": "EVI-002-PROC",
  "evidence_type": "Procurement_Document",
  "transitions": [
    {
      "sequence": 1,
      "from_state": "PARTIAL",
      "to_state": "UNKNOWN",
      "timestamp": "2026-08-23T09:30:00Z",
      "reason": "Critical validation dependency unresolved",
      "actor": "Dependency_Resolver"
    }
  ]
}
```

### Test Result: **FAIL**

**Reason:** No persistent evidence recording system identified in current codebase capable of maintaining these state transitions. While `core_kernel/governance/self_verification/evidence.py` provides evidence collection infrastructure, it lacks:
1. State machine for evidence transitions
2. Explicit UNKNOWN state tracking
3. Persistent recording of state history
4. Dependency resolution tracking

---

## UNKNOWN Preservation Test (E2)

### Requirement
Verify that UNKNOWN states are preserved through simulated mutations and do not spontaneously transition to VERIFIED without supporting evidence.

### Test Setup
```
Before Mutation:
  - Evidence-A: VERIFIED (complete)
  - Evidence-B: UNKNOWN (pending validation)
  - Open Dependency: depends_on(Evidence-B)
  - Assertion: Evidence-B.state == UNKNOWN
```

### Mutation Scenario
Apply environmental changes simulating:
- Network timeout on dependency validator
- Partial data recovery attempt
- Cascading validation requests

### Expected Behavior After Mutation
```
After Mutation:
  - Evidence-A: VERIFIED (unchanged)
  - Evidence-B: UNKNOWN (preserved)
  - Open Dependency: still depends_on(Evidence-B)
  - Invariant: Evidence-B.state == UNKNOWN
```

### FAIL Conditions
```
FAIL-1: Evidence-B disappears from record
FAIL-2: Evidence-B transitions to VERIFIED without:
        a) New evidence document captured
        b) Validation reason recorded
        c) Timestamp recorded
FAIL-3: Open dependency broken without compensation
```

### Test Result: **FAIL**

**Reason:** No mechanism exists to:
1. Record UNKNOWN state as a persistent, queryable state
2. Enforce invariants that prevent unsourced VERIFIED transitions
3. Track open dependencies bidirectionally
4. Block automatic state promotion without evidence

Evidence recording is currently capture-based (fixed scenario set) rather than state-based (continuous tracking).

---

## Open Dependency Tracking (E3)

### Requirement
Verify that open dependencies can be tracked across arbitrary depth levels without data loss.

### Required Fields
```
- Dependency ID
- Related Evidence
- Current Status
- Created Time
- Resolved Time (optional)
- Resolution Evidence (optional)
```

### Depth Test Structure
```
Level 1 (Direct):
  Evidence-A depends_on Evidence-B
  
Level 2 (Transitive):
  Evidence-B depends_on Evidence-C
  
Level 3 (Deep):
  Evidence-C depends_on Evidence-D
```

### Sample Dependency Graph
```
DEP-001:
  - dependency_id: "DEP-001"
  - evidence_source: "EVI-001-PROC"
  - evidence_target: "EVI-002-PROC"
  - status: "OPEN"
  - created_at: "2026-08-23T09:00:00Z"

DEP-002:
  - dependency_id: "DEP-002"
  - evidence_source: "EVI-002-PROC"
  - evidence_target: "EVI-003-PROC"
  - status: "OPEN"
  - created_at: "2026-08-23T09:05:00Z"

DEP-003:
  - dependency_id: "DEP-003"
  - evidence_source: "EVI-003-PROC"
  - evidence_target: "EVI-004-PROC"
  - status: "OPEN"
  - created_at: "2026-08-23T09:10:00Z"
```

### Invariant Preservation
After any mutation, path traversal should succeed:
```
resolve_chain("EVI-001-PROC") = [
  "EVI-001-PROC",
  "EVI-002-PROC" (via DEP-001),
  "EVI-003-PROC" (via DEP-002),
  "EVI-004-PROC" (via DEP-003)
]
```

### Test Result: **FAIL**

**Reason:** Current evidence system provides:
- Event-based capture (AuditRecord, AuditLogger)
- Audit store (jsonl format)
- No dependency graph structure

Missing implementations:
- No bidirectional edge tracking
- No transitive closure computation
- No dependency traversal utilities
- No cycle detection

---

## Evidence Record Reproduction (E4)

### Requirement
Verify that final state can be reconstructed from initial state + sequence of transitions.

### Formula
```
Final State = Initial State + Transitions + Decision Points
```

### Test Structure

#### Initial State (T0)
```json
{
  "evidence_id": "EVI-PROC-FULL",
  "state": "PARTIAL",
  "fields_captured": ["vendor_id", "po_number"],
  "fields_missing": ["approval_chain", "payment_terms"],
  "timestamp": "2026-08-23T08:00:00Z"
}
```

#### Transitions (T0 → T3)
```json
[
  {
    "event_id": "E20260823_000001",
    "transition": "PARTIAL → PARTIAL",
    "action": "capture_payment_terms",
    "timestamp": "2026-08-23T08:15:00Z",
    "new_fields": ["payment_terms"],
    "fields_missing_after": ["approval_chain"]
  },
  {
    "event_id": "E20260823_000002",
    "transition": "PARTIAL → VERIFIED",
    "action": "validate_against_schema",
    "timestamp": "2026-08-23T08:30:00Z",
    "validation_scope": ["vendor_id", "po_number", "payment_terms"],
    "result": "ALL_PRESENT"
  },
  {
    "event_id": "E20260823_000003",
    "transition": "VERIFIED → UNKNOWN",
    "action": "detect_approval_chain_mismatch",
    "timestamp": "2026-08-23T09:00:00Z",
    "reason": "External audit flagged missing approval chain",
    "blocking_evidence": "EVI-AUDIT-20260823"
  }
]
```

#### Decision Points
```json
[
  {
    "decision_id": "DC_20260823_001",
    "point_in_timeline": "after_transition_2",
    "decision": "ACCEPT_VERIFIED_STATE",
    "rationale": "Schema validation passed; approval_chain blocking is acceptable per UP-F002 UNKNOWN preservation rule",
    "timestamp": "2026-08-23T08:31:00Z"
  }
]
```

#### Expected Final State (T3)
```json
{
  "evidence_id": "EVI-PROC-FULL",
  "state": "UNKNOWN",
  "fields_validated": ["vendor_id", "po_number", "payment_terms"],
  "fields_missing": ["approval_chain"],
  "fields_pending": ["approval_chain"],
  "blocking_evidence": "EVI-AUDIT-20260823",
  "history": [
    "PARTIAL (initial)",
    "PARTIAL (payment_terms captured)",
    "VERIFIED (schema validation passed)",
    "UNKNOWN (approval_chain mismatch detected)"
  ],
  "last_transition": "2026-08-23T09:00:00Z"
}
```

### Verification Logic
```python
# Pseudocode
def verify_reproducibility():
    initial = load_initial_state()
    log = load_event_log()
    decisions = load_decision_ledger()
    
    current = deepcopy(initial)
    
    for event in log:
        current = apply_transition(current, event)
    
    for decision in decisions:
        current = apply_decision(current, decision)
    
    expected_final = load_expected_final_state()
    
    return current == expected_final
```

### Test Result: **FAIL**

**Reason:** No evidence replay mechanism exists. Current system captures:
- ExecutionResult objects (one-time snapshots)
- AuditRecord entries (immutable log entries)
- No playback function to reconstruct state from log

Missing implementations:
- No state_at(timestamp) function
- No transition_apply(state, event) → new_state function
- No decision_apply(state, decision) → new_state function
- No final_state_reproduce(initial, [transitions], [decisions]) function

---

## Test Results Summary

| Test Item | Result | Status |
|-----------|--------|--------|
| E1: Evidence State Representation | FAIL | Cannot record state transitions |
| E2: UNKNOWN Preservation | FAIL | No state persistence; no invariant enforcement |
| E3: Open Dependency Tracking | FAIL | No dependency graph structure |
| E4: Evidence Record Reproduction | FAIL | No replay mechanism; no state reconstruction |

---

## Findings

### Critical Gaps
1. **State Machine Absent**
   - No explicit state machine for evidence lifecycle
   - Evidence captured in fixed scenario set (pass/warning/fail) rather than continuous state tracking
   
2. **UNKNOWN State Not Recognized**
   - No explicit UNKNOWN state defined in current evidence schema
   - Only binary validation_evidence dict: {scope: True|False}
   - Cannot represent "pending" or "indeterminate" states

3. **Persistence Incomplete**
   - AuditStore provides immutable log (jsonl format)
   - But no queryable evidence_state table/collection
   - No evidence_transitions relation
   - No dependency_graph structure

4. **Replay Capability Missing**
   - No state reconstruction from log
   - No temporal queries ("what was the state at T=X?")
   - No dependency closure computation

5. **Validation Invariants Not Enforced**
   - No enforcement of "UNKNOWN → VERIFIED requires evidence"
   - No cycle detection in dependency graph
   - No missing-field tracking across transitions

### Design Observations
- Evidence schema (WP-Schema-01) designed for governance seal verification, not state machine
- AuditRecord tracks "what the audit saw", not "what the evidence became"
- Current model suitable for compliance/certification; unsuitable for dynamic state tracking

---

## Recommendations for UP-TEST-003 Support

To achieve V3.2 VERIFIED status, implement:

### Phase 1: State Model (Required)
```
1. Extend EvidenceRecord schema with state machine:
   - state: PARTIAL | VERIFIED | UNKNOWN (enum)
   - state_history: List[StateTransition]
   - blocking_evidence: List[EvidenceID] (for UNKNOWN reasons)

2. Create StateTransition record:
   - from_state, to_state
   - timestamp, actor, reason
   - validation_scope (what triggered transition)
```

### Phase 2: Dependency Graph (Required)
```
1. Create DependencyEdge relation:
   - source_evidence_id
   - target_evidence_id
   - status: OPEN | RESOLVED
   - created_at, resolved_at
   - resolution_evidence (optional)

2. Implement dependency traversal:
   - transitive_dependencies(evidence_id) → [EvidenceID, ...]
   - blocking_path(evidence_id) → [[dep1, dep2, dep3], ...]
   - detect_cycles(graph) → [CycleID, ...]
```

### Phase 3: Replay Engine (Required)
```
1. Implement state reconstruction:
   - state_at(evidence_id, timestamp) → EvidenceState
   - apply_transition(state, event) → new_state
   - replay_sequence(evidence_id, [events]) → final_state

2. Validation:
   - verify_final_state_matches(initial, events, expected)
```

### Phase 4: Invariant Enforcement (Required)
```
1. Write constraints:
   - unknown_requires_blocking_evidence()
   - unknown_to_verified_requires_source()
   - dependency_resolution_updates_state()

2. Implement guards:
   - try_transition(current, target) → Result[new_state, error]
```

---

## Decision

**Evidence Recording Readiness: NOT READY**

**Reasoning:**
- Core state machine absent
- UNKNOWN state not representable
- Dependency graph missing
- Replay capability nonexistent
- Cannot satisfy UP-F002 UNKNOWN Preservation rule

**Next Gate:** Implement Phase 1 (State Model) before re-validation.

**Approval:** Awaiting Human Gate review.

---

## Appendix A: Evidence State Specification (UP-F002)

The Procurement domain UP-F002 UNKNOWN Preservation pattern requires:

1. **PARTIAL State**
   - Some but not all required fields present
   - Indicates work in progress
   - Can transition to VERIFIED or UNKNOWN

2. **VERIFIED State**
   - All required fields present and validated
   - Schema conformance confirmed
   - May transition to UNKNOWN if dependencies fail

3. **UNKNOWN State**
   - Validation result indeterminate
   - May indicate:
     * Blocking external dependency unresolved
     * Data in transition (uploaded but not yet validated)
     * Pending upstream correction
   - Must NOT spontaneously disappear or downgrade
   - Requires explicit evidence to transition away

---

## Appendix B: Test Environment

```
Repository: m-sirius-k/MoCKA
Branch: claude/evidence-recording-validation-1acudh
Validation Date: 2026-08-23
Observer Session: Claude Haiku 4.5

Files Inspected:
- core_kernel/governance/self_verification/evidence.py
- governance/write_path/evidence/schema.py
- governance/write_path/evidence/fixtures.py

Baseline Schema Version: WP-Schema-01 (Runtime Evidence Record)
Governance Model: Phase 4 (Commercial Product Phase)
```

---

## Document History

| Date | Version | Change |
|------|---------|--------|
| 2026-08-23 | 1.0 | Initial validation run; all tests FAIL |

---

**End of Document**
