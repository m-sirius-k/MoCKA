# R04 Current Authorization Specification Gap — Human Gate Decision Package v1.0

**Status**: SPECIFICATION GAP CONFIRMED / AWAITING HUMAN GATE DECISION

**Date**: 2026-09-02

**Authority Requested**: Human Gate (きむら博士) — Operative Specification Decision Only

**Scope**: R04 Phase C Current Authorization (not implementation, not design choice)

---

## Executive Summary

R04 Phase C Authorization Boundary investigation is COMPLETE. Findings:

**Specification Status**:
```
AUTHORITATIVE CURRENT AUTHORIZATION SOURCE
= UNKNOWN / SPECIFICATION GAP

AUTHORIZATION IDENTIFIER / REQUEST LINKAGE
= UNKNOWN / SPECIFICATION GAP

Reason: Current operative specification cannot be determined from existing evidence.
```

**Next Step**: Human Gate decides operative specification. Implementation design and authorization occur only after this decision.

**No implementation changes are authorized until Human Gate resolves this gap.**

---

## A. Investigation Completed — Evidence Status

### A.1 Three-Part Investigation Finished

1. **PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_v1.md**
   - Status: Evidence-based trace of current implementation
   - Finding: Authority source not externally retrieved; authority constructed in-memory
   - Date: 2026-09-02

2. **PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_SUPPLEMENT_v1.md**
   - Status: Evidence-based discovery of DC_20260713_003 design
   - Finding: Future Model B design approved but implementation pending
   - Date: 2026-09-02

3. **PHASE_C_CURRENT_AUTHORIZATION_APPLICABILITY_CHECK_v1.md**
   - Status: Verification of whether DC_20260713_003 is currently applicable
   - Finding: Design is future-scoped, not current operative specification
   - Date: 2026-09-02

### A.2 Investigation Constraints Honored

✓ No new design choices proposed
✓ No authority source selected (A/B/C decision deferred)
✓ No implementation changes made
✓ No code modifications
✓ Evidence hierarchy followed (Human Gate decisions first)
✓ UNKNOWN maintained when applicability unverified

---

## B. What Is Known

### B.1 Confirmed Facts

| Fact | Evidence | Status |
|---|---|---|
| Phase C implements approval/authorization/execution boundary | PHASE_C_CORE_CHANGE_REQUEST_v1.0.md / PHASE_C_COMPLETION_REPORT_v1.0.md | VERIFIED |
| GL7 checks scope/changes before execution | seal_governance_gate.py + tests | VERIFIED |
| Current authority source is self-constructed | PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_v1.md Section "Authority Source Options" | VERIFIED |
| DC_20260713_003 (Model B) design exists and is approved | AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md + decision record | VERIFIED |
| Model B implementation status: Phase 2 awaiting approval | AUTO_SEAL_M1_TERMINAL_PROCESS_PLAN_v1.0.md (line 263) | VERIFIED |
| RB-2 (GL7 auto-approval) is current operative model | AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md Section 3 | VERIFIED |
| phi_os.human_gate API exists and can track request state | phi_os/human_gate.py | VERIFIED |
| decision_ledger.jsonl exists with schema extensibility | data/decisions/decision_ledger.jsonl | VERIFIED |

### B.2 Design-Level Specifications (Approved but Not Implemented)

**From DC_20260713_003 (Model B Design, Approved 2026-07-13)**:

Required Auth Model fields:
- seal_request_id: Unique identifier per seal request
- decision_id: Reference to authorizing Decision
- requester: Who requested the seal
- approved_by: MUST be human (not system)
- approval_timestamp: When human approved
- artifact_hash: Commit being sealed
- seal_hash: Final summary hash
- pending_ref: Link to AUTO_SEAL_PENDING event (if auto source)

Constraint: approved_by != human → Seal is INVALID

Linkage Chain:
```
Decision (human-approved)
    ↓ decision_id
Seal Request
    ↓ seal_request_id
Execution
    ↓ execution_id
Audit Record
    ↓ artifact_hash / seal_hash
```

**Implementation Status**: Design approved. M1 implementation (schema + read/write/verify) NOT approved (Phase 2 pending).

---

## C. What Is UNKNOWN

### C.1 Current Authority Source Gap

**Question**: Which system/mechanism is authoritative for Current Authorization at execution time?

**Options Found** (not decided):

1. **phi_os.human_gate** 
   - Current State: Fully implemented but NOT connected to SealGovernanceGate
   - API: `get_state(request_id)` returns PENDING/APPROVED/REJECTED/EXPIRED/CANCELED
   - Advantage: Human Gate state machine already exists
   - Gap: Requires linkage mechanism (what is request_id?)

2. **decision_ledger.jsonl query**
   - Current State: Ledger exists, appendable, schema extensible
   - Pattern: Query for latest AUTHORIZATION_PASSED event for decision_id?
   - Advantage: Unified audit trail
   - Gap: Query API not specified; retrieval pattern not standardized

3. **GL7 (ExecutionGovernanceEngine) direct**
   - Current State: Already called for approval check
   - Usage: Scope/max_changes re-validation implemented
   - Advantage: No new integration required
   - Gap: GL7 is mechanism check, not human decision approval

4. **Other** (not identified in evidence)

**Status**: SPECIFICATION GAP — No evidence determines which is authoritative

### C.2 Authorization Identifier / Linkage Gap

**Question**: How does a seal execution trace back to its authorizing decision/request?

**Options Found** (not decided):

1. **seal_request_id + decision_id (Model B design)**
   - Specified: Yes (DC_20260713_003 Section 5)
   - Implemented: No (M1 pending approval)
   - Advantage: Complete chain from human decision → seal

2. **execution_id → audit record lookup**
   - Specified: Partially (execution_id exists in current logs)
   - Implemented: Yes (current implementation uses this)
   - Advantage: Already in use
   - Gap: Doesn't link to human decision

3. **approval_state in-memory (current)**
   - Specified: No (not in formal specification)
   - Implemented: Yes (current implementation)
   - Advantage: Works for same session
   - Gap: No persistent link, no human identity

4. **Other** (not identified in evidence)

**Status**: SPECIFICATION GAP — No evidence determines which linkage is operative

---

## D. Why Gap Exists

### D.1 Timeline Mismatch

| Date | Event | Scope | Status |
|---|---|---|---|
| 2026-07-08 | Phase C scope defined | GL7 integration for approval boundary | Completed |
| 2026-07-13 | DC_20260713_003 approved | Model B (future human decision-based) | Approved design, implementation pending |

**Finding**: Phase C was scoped and implemented (GL7 boundary) BEFORE future Model B design was approved. They are sequential phases, not concurrent.

### D.2 Current Implementation vs Future Design

**Current Phase C (Operative)**:
- Authority: GL7 dry-run cleanpass → auto-approve
- Recorded as: approved_by="system:seal_governance_gate"
- Linkage: execution_id → approval_state (in-memory)
- Risk: RB-2 (auto-approval masquerading as governance)

**Future Model B (Design Approved, Implementation Pending)**:
- Authority: Human-approved Decision
- Recorded as: approved_by=human with decision_id link
- Linkage: seal_request_id → decision_id → human approval
- Benefit: Explicit human decision trail, authorized by DC_20260713_003

**Finding**: Current and future specifications are different. No evidence determines which should be CURRENT operative.

### D.3 No Formal Current Specification

**Search Results**:
- Phase C specification: GL7 integration (defined in PHASE_C_CORE_CHANGE_REQUEST_v1.0.md)
- Future specification: Model B (defined in DC_20260713_003)
- Current operative specification: ???

**No evidence found that explicitly states**: "R04 Current Authorization shall be [option] because [authority]"

**Finding**: Specification gap confirmed. Decision required from Human Gate.

---

## E. Phase C Status — FROZEN

### E.1 Implementation Freeze

**Current State**:
- seal_governance_gate.py: Implements approval/authorization/execution boundary (M3-M6 completed)
- Behavior: GL7 approval + scope/max_changes re-check + execution
- Authority: "system:seal_governance_gate" (not human)
- Linkage: approval_state in-memory (not persistent)

**Freeze Status**: NO CHANGES AUTHORIZED

- ❌ No authority source changes
- ❌ No request_id design
- ❌ No identifier mechanism changes
- ❌ No GL7 authority escalation
- ❌ No phi_os.human_gate connection
- ❌ No decision_ledger query implementation
- ❌ No Model B features added
- ✓ Phase C boundary structure maintained as-is

### E.2 Design Decisions Deferred

All of the following remain DEFERRED until Human Gate specifies operative authority source:

- Which authority source (phi_os.human_gate vs decision_ledger vs GL7 vs other)
- Which linkage mechanism (seal_request_id vs execution_id vs other)
- Request ID generation and tracking
- Authorization retrieval pattern at execution time
- Integration point for human decision link
- Expiration policy (if any)
- Emergency/override path (if any)

---

## F. Human Gate Decision Request

### F.1 Decision Scope

**NOT ASKING**:
- How to implement Model B
- Whether Phase C implementation is good/bad
- Whether to change Phase C (that's implementation)
- Which code changes to make
- Approval for Codex implementation

**ASKING**:
One specification decision:

```
For R04 Phase C Current Authorization Boundary,
which source and linkage mechanism shall be
the OPERATIVE SPECIFICATION?

Option A: Authority source = [choice]
          Linkage = [choice]
          Reason = [rationale]

Option B: Authority source = [choice]
          Linkage = [choice]
          Reason = [rationale]

[or other options identified by Human Gate]

Decision: Adopt Option [X] as operative for R04
```

### F.2 Decision Timeline

**Phase**: SPECIFICATION RESOLUTION (not implementation)

**Gate**: Human Gate only

**Approval**: きむら博士

**After Decision**: Implementation design and authorization occur in sequence:
1. Specification decision (this package)
2. Implementation design (separate document)
3. Implementation authorization (Human Gate decision 2)
4. Codex implementation
5. KUROKO verification
6. Audit

**No implementation work proceeds until step 1 is decided.**

---

## G. Evidence Package Contents

### G.1 Official R04 Investigation Record

The following documents are now FORMAL R04 EVIDENCE:

1. **PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_v1.md**
   - What: Detailed trace of current implementation behavior
   - Status: Evidence record (completed investigation)
   - Use: For understanding current operative model

2. **PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_SUPPLEMENT_v1.md**
   - What: Discovery and analysis of DC_20260713_003
   - Status: Evidence record (completed investigation)
   - Use: For understanding approved future design

3. **PHASE_C_CURRENT_AUTHORIZATION_APPLICABILITY_CHECK_v1.md**
   - What: Verification that DC_20260713_003 is not currently operative
   - Status: Evidence record (completed investigation)
   - Use: For confirming specification gap exists

4. **R04_CURRENT_AUTHORIZATION_SPECIFICATION_GAP_HUMAN_GATE_PACKAGE_v1.md** (this document)
   - What: Gap summary and Human Gate decision request
   - Status: Decision package (awaiting Human Gate action)
   - Use: For Human Gate specification decision

### G.2 Investigation Checkpoints Verified

✓ Investigation scope: R04 Phase C authorization only (not Phase D or future)
✓ Evidence hierarchy: Human Gate decisions primary, design docs secondary, implementation code tertiary
✓ Distinction maintained: Specification ≠ Implementation ≠ Future Design
✓ Gap identified: Current operative specification undefined
✓ Phase C frozen: No changes made during investigation
✓ No design choices made: Decision deferred to Human Gate

---

## H. Non-Determinations (Intentionally Deferred)

The following are NOT determined and remain IMPLEMENTATION DECISIONS for after Human Gate specifies operative authority:

1. **Exact retrieval mechanism** for current authorization
2. **Request ID generation and format**
3. **Authorization expiration policy** (if any)
4. **Scope boundary validation** at execution
5. **PENDING-to-Completion linkage** pattern (pending_ref)
6. **Emergency/override path** authorization
7. **Interaction sequence** between GL7 (pre-filter) and human decision (if Model B adopted)
8. **Backward compatibility** requirements

---

## I. Decision Package Checkpoints

**For Human Gate Review**:

✓ Investigation complete (no open questions within scope)
✓ Evidence formalized (3 investigation documents + this package)
✓ Gap confirmed (UNKNOWN/SPECIFICATION_GAP is correct status)
✓ Phase C frozen (no implementation changes)
✓ Decision scope clear (one specification choice)
✓ Options identified (at least 3+ authority sources available)
✓ Timeline clear (specification decision required before implementation)
✓ No design choice pre-decided (alternatives not evaluated/ranked)
✓ Rationale for gap explained (current != future, timing mismatch, no formal spec)

---

## J. Next Steps After Human Gate Decision

### J.1 If Human Gate Decides Operative Authority Source

```
Human Gate Decision: "R04 Current Authorization shall be [source]"
        ↓
Implementation Design Phase
  - Design how to retrieve/verify from chosen source
  - Design linkage mechanism
  - Design integration points
        ↓
Implementation Authorization
  - Human Gate approves implementation design
        ↓
Codex Implementation
  - Code changes to seal_governance_gate.py (or equivalent)
  - Integration with chosen authority source
  - Tests covering new retrieval/verification
        ↓
KUROKO Verification
  - Verify implementation matches specification and design
  - Audit trail validation
        ↓
Final Audit
```

### J.2 If Human Gate Defers Decision

```
Human Gate Decision: "Defer to Phase D" / "Require additional information"
        ↓
R04 Phase C remains frozen at current state (GL7 auto-approval, RB-2 risk acknowledged)
        ↓
Gap status documented as deferred (not eliminated)
        ↓
Next phase specification must address this gap
```

---

## K. Decision Record Placeholder

**Awaiting Human Gate Decision**: 

```
Date: [Decision date]
Authority: Human Gate (きむら博士)
Decision: [Option A / B / C / other]
Rationale: [Reasoning for choice]
Record Location: [Decision Ledger entry DC_...]
Implementation Phase: [Authorized / Deferred / Conditional]
Scope Limits: [Any constraints on implementation]
```

---

## L. Disposition

### Current Status Summary

```
R04 Phase C Investigation       [COMPLETE]
        ↓
Evidence Formalization          [COMPLETE]
        ↓
Specification Gap Confirmed     [COMPLETE]
        ↓
Implementation Freeze           [ACTIVE]
        ↓
【HUMAN GATE DECISION REQUIRED】
        ↓
Implementation Design           [PENDING]
        ↓
Implementation Authorization    [PENDING]
        ↓
Codex Implementation            [BLOCKED]
        ↓
KUROKO Verification             [BLOCKED]
        ↓
Audit                           [BLOCKED]
```

### Phase C Status

**Implementation**: FROZEN (no changes authorized)

**Specification**: UNKNOWN / SPECIFICATION GAP (awaiting Human Gate decision)

**Authority**: CURRENT = system:seal_governance_gate (GL7 auto-approval, RB-2 risk)

**Linkage**: CURRENT = execution_id → in-memory approval_state (not persistent)

**Future Design**: DC_20260713_003 (Model B, human decision-based, approved but implementation not approved)

### Action Required

**Human Gate to decide**: Which authority source and linkage mechanism shall be operative for R04 Phase C Current Authorization?

**No implementation work proceeds until this decision is made and recorded.**

---

## References

**Investigation Documents**:
- `docs/governance/PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_v1.md`
- `docs/governance/PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_SUPPLEMENT_v1.md`
- `docs/governance/PHASE_C_CURRENT_AUTHORIZATION_APPLICABILITY_CHECK_v1.md`

**Design Documents**:
- `docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md` (DC_20260713_003)
- `docs/governance/AUTO_SEAL_M1_IMPLEMENTATION_PROPOSAL_v1.0.md`
- `docs/governance/AUTO_SEAL_M1_TERMINAL_PROCESS_PLAN_v1.0.md`

**Phase C Documentation**:
- `docs/governance/PHASE_C_CORE_CHANGE_REQUEST_v1.0.md`
- `docs/governance/PHASE_C_COMPLETION_REPORT_v1.0.md`

**Implementation**:
- `governance/seal_governance_gate.py`
- `phi_os/human_gate.py`
- `data/decisions/decision_ledger.jsonl`

