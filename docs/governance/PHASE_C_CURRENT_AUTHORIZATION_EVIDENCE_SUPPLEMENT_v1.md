# Phase C Current Authorization Evidence Supplement v1.0

**Purpose**: Evidence-based answer to Q1 and Q2 using existing Decision Records and Design Documents

**Date**: 2026-09-02

**Investigation Scope**: Human Gate Decision Records + Approved Design Documents ONLY

---

## A. Human Gate Decision Status

**Current R04 Phase C Status** (as directed):

```
AUTHORITATIVE CURRENT AUTHORIZATION SOURCE
= UNKNOWN / SPECIFICATION GAP

AUTHORIZATION IDENTIFIER / REQUEST LINKAGE
= UNKNOWN / SPECIFICATION GAP

PHASE C IMPLEMENTATION CHANGE
= PROHIBITED
```

**Investigation Finding**: Above status requires REVISION based on existing Decision Record.

---

## B. Authoritative Decision Record Evidence

### B.1 Decision Record: DC_20260713_003

**Document**: `docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md`

**Status**: **APPROVED** (by きむら博士)

**Date**: 2026-07-13

**Evidence Level**: PRIMARY (Human Gate Decision Record)

**Content**: Approved AUTO_SEAL Boundary Design v1.0, including:
- Model B adoption (Decision-based authorization)
- Auth Model specification
- Required fields for seal authorization
- GL7 role redefinition
- Migration Plan (M0-M4)

### B.2 Key Finding from DC_20260713_003

**Quote from document (Section 10 History, Line 228-239)**:

```
2026-07-13: きむら博士がModel B採用を裁定(DC_20260713_003、Approved)。確定事項:
(1) Model B(Decision単位承認)を主経路として採用。主経路 = Decision生成 -> Human承認 ->
    承認済Decision発行 -> Seal Request -> AUTO_SEAL実行 -> Anchor更新。
(2) GL7 を承認者ではなく事前境界フィルタ(危険操作検知/境界逸脱検知/承認対象分類/承認要求生成)
    として再定義。GL7自身はSeal授権者ではない。
(3) approved_by=human をAUTO_SEAL成立条件として必須化(approved_by != human は Seal不可)。
(4) Decision承認境界は scope単位を採用...
```

**Translation**:
- Model B adopted: Decision-based authorization (Decision → Human Approval → Seal Request → Execution)
- GL7 redefined as pre-filter, NOT authorization source
- **approved_by=human REQUIRED** (approved_by != human means Seal invalid)
- Decision is the authorization basis (not GL7, not parameter consistency)

---

## C. Authoritative Auth Model Specification

### C.1 Required Authorization Evidence (Section 5 of AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md)

From approved design:

| Field | Meaning | Status | Source |
|---|---|---|---|
| `seal_request_id` | Unique ID for seal request (separate from execution_id) | REQUIRED | DC_20260713_003 |
| `requester` | Request source (human identifier or system:auto_audit_loop) | REQUIRED | DC_20260713_003 |
| `decision_id` | Basis Decision (human-approved) | REQUIRED | DC_20260713_003 |
| `approved_by` | **HUMAN approver** (NOT system) | **REQUIRED** | DC_20260713_003 |
| `approval_timestamp` | When human approved | REQUIRED | DC_20260713_003 |
| `artifact_hash` | Commit hash being sealed | REQUIRED | DC_20260713_003 |
| `seal_hash` | sealed_summary_hash | REQUIRED (post-seal) | DC_20260713_003 |
| `pending_ref` | AUTO_SEAL_PENDING event_id link | REQUIRED (if AUTO source) | DC_20260713_003 |

### C.2 Critical Constraint from DC_20260713_003

```
approved_by = human をAUTO_SEAL成立条件として必須化
(approved_by != human は Seal不可)
```

Translation: **approved_by MUST equal human. If approved_by != human, Seal is INVALID.**

Current Phase C Implementation: `approved_by="system:seal_governance_gate"`

**Result**: **VIOLATES DC_20260713_003**

---

## D. Answer to Q1: Authoritative Current Authorization Source

### Q1 Question
```
Can the existing Evidence identify THE authoritative current authorization source
for validating Current Authorization at execution time?
```

### Q1 Answer: YES, IDENTIFIED

**Authoritative Source** (per DC_20260713_003, approved design):

```
AUTHORITATIVE CURRENT AUTHORIZATION SOURCE
= Decision Record (decision_id)
    with Human Approver (approved_by=human)
    in scope-bounded context
    per Model B (Decision-based authorization)
```

### Q1 Evidence Chain

1. **Primary Evidence**: DC_20260713_003 (Human Gate Decision)
   - Source: `docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md` Section 10
   - Status: APPROVED (by きむら博士)
   - Date: 2026-07-13

2. **Secondary Evidence**: Design Section 4.2 (Model Comparison)
   - Model B = "Decision単位承認" (Decision-based)
   - Rationale: "Decisionのid + 人間approved_by + artifactが揃う"
   - Alignment: "MoCKAのDecision Ledger中心思想に整合"

3. **Tertiary Evidence**: Design Section 5 (Auth Model)
   - Field specification: requires decision_id + approved_by (human)
   - Constraint: approved_by != human makes seal invalid

### Q1 Verification: Active Status

**Reference**: `docs/governance/JARVIS_RUNTIME_BETA_ARCHITECTURE_DRAFT_v0.1.md`

```
| DC_20260713_003 | Active | [継承]。変更しない |
...
| DC_20260713_003 (Active) | approved_by=human を Seal 成立条件として必須化 |
```

**Status**: ACTIVE (not superseded, not obsoleted)

---

## E. Answer to Q2: Authorization Identifier / Request Linkage

### Q2 Question
```
Does an existing identifier/request linkage mechanism exist
that uniquely links Human Gate Authorization to execution Actions?
```

### Q2 Answer: YES, SPECIFIED (Not Yet Implemented)

### Q2 Evidence: seal_request_id

**From DC_20260713_003, Section 5 (Auth Model)**:

| Field | Type | Purpose | Source |
|---|---|---|---|
| `seal_request_id` | unique ID | Identifies seal request (separate from execution_id) | REQUIRED |
| `decision_id` | reference | Links to basis Decision | REQUIRED |
| `requester` | identity | Who requested the seal | REQUIRED |
| `approved_by` | identity | Which human approved | REQUIRED |
| `approval_timestamp` | timestamp | When approval occurred | REQUIRED |

**Linkage Model**:
```
Decision (human-approved)
    ↓
decision_id
    ↓
seal_request_id (generated for each seal)
    ↓
execution_id (when seal executes)
    ↓
artifact_hash / seal_hash (proof of what was sealed)
```

### Q2 Specification: Normal Path (Section 6.1)

```
Decision(人間承認) -> seal_request_id採番 + requester記録 -> 
(GL7 abortフィルタ) -> Seal実行(anchor_update.py) -> 
Auth Model全項目を監査レコードへ記録 -> Audit Event
```

**Chain of custody**:
1. Decision is created and human-approved
2. seal_request_id is generated
3. requester is recorded
4. GL7 checks for aborts (filter, not approval)
5. Seal executes
6. All Auth Model fields are recorded in audit record

### Q2 Implementation Status: SPECIFIED, NOT IMPLEMENTED

**Design Location**: `docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md`, Section 5

**Migration Plan**: Section 8
- M1: Add fields to decision_ledger.jsonl schema
- M2: Modify MANUAL_SEAL approved_by from system to human-required
- M3: Connect PENDING and Completion via pending_ref

**Current Status**: Design APPROVED (DC_20260713_003), implementation PENDING (awaiting M1 Decision)

---

## F. Authority Chain Status

### Chain Element Analysis

```
Human Gate (DC_20260713_003)
    ↓ [VERIFIED]
Approved Design (AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md)
    ↓ [VERIFIED]
Model B: Decision-based Authorization
    ↓ [VERIFIED]
Authorization Identifier: seal_request_id + decision_id
    ↓ [VERIFIED]
Required Auth Model Fields (seal_request_id, requester, decision_id, 
approved_by=human, approval_timestamp)
    ↓ [NOT VERIFIED - Not yet implemented]
Current Authorization Retrieval (from decision_ledger by decision_id)
    ↓ [NOT VERIFIED - Mechanism not yet implemented]
SealGovernanceGate (current Phase C implementation)
    ↓ [CONFLICT - Uses approved_by=system, not human]
Execution (seal allowed only if approved_by=human)
    ↓ [NOT VERIFIED - Constraint not enforced]
```

### Status Summary

| Chain Element | Status | Evidence | Notes |
|---|---|---|---|
| Authority Source (Decision-based) | VERIFIED | DC_20260713_003 | Model B approved |
| Identifier (seal_request_id) | VERIFIED | DC_20260713_003 Section 5 | Specified in Auth Model |
| Linkage (decision_id reference) | VERIFIED | DC_20260713_003 Section 5 | Required field |
| Current Retrieval Mechanism | UNKNOWN | (Not yet designed) | Deferred to implementation |
| Phase C Implementation | CONFLICT | Compare to spec | Uses system approval, not human |

---

## G. Findings: Q1 and Q2 Resolution

### Finding 1: Authoritative Source IS Specified

**Q1 Resolution**: NO LONGER UNKNOWN

The authoritative current authorization source is **NOT** unspecified.

**Specification**: Decision-based model (Model B) with human approval, approved by DC_20260713_003

**Required Fields**: seal_request_id, decision_id, requester, approved_by (human), approval_timestamp

### Finding 2: Identifier IS Specified

**Q2 Resolution**: NO LONGER UNKNOWN

Authorization identifier mechanism is **NOT** missing.

**Specification**: seal_request_id (unique per seal request) linked to decision_id (which decision authorizes this seal)

**Generation Point**: After Decision approval, before GL7 check

**Tracking Requirement**: Stored in decision_ledger as part of Auth Model

### Finding 3: Implementation Gap

Current Phase C implementation does NOT implement the approved model:

| Requirement | DC_20260713_003 | Phase C Implementation | Status |
|---|---|---|---|
| Authorized by Decision | ✓ YES | ✗ NO | GAP |
| approved_by = human | ✓ YES | ✗ SYSTEM | VIOLATION |
| seal_request_id | ✓ YES | ✗ NO | GAP |
| decision_id basis | ✓ YES | ✗ NO | GAP |
| requester tracking | ✓ YES | ✗ NO | GAP |
| GL7 as pre-filter | ✓ YES | ✗ TREATED AS APPROVAL | VIOLATION |

---

## H. Evidence Gaps

### Not Yet Determined (Deferred to Implementation Phase)

The approved design (DC_20260713_003) specifies WHAT must be recorded and validated, but leaves the following implementation details unspecified:

1. **Mechanism for retrieving current authorization at execution time**
   - How does SealGovernanceGate query decision_ledger for current decision_id?
   - How does it verify decision_id is still valid at execution time?
   - How does it check if approval_timestamp is expired (if expiration applies)?

2. **Decision Query API or Pattern**
   - Direct decision_ledger.jsonl query?
   - New API method in Decision engine?
   - phi_os.human_gate integration?

3. **Scope boundary validation**
   - How are scope-bounded decisions enforced?
   - How does seal execution verify it falls within authorized scope?

4. **PENDING-to-Completion linkage** (pending_ref)
   - Design specifies connection but implementation pattern deferred

5. **Emergency path implementation**
   - How are emergency seals (without pre-Decision) approved?
   - How is reason + immediate human approval recorded?

**Status**: These are DESIGN DEFERRED items, not UNKNOWN SPECIFICATION GAPS.

---

## I. Non-Determinations (Intentionally Not Decided Here)

Per investigation instructions, the following were NOT determined:

1. **Exact retrieval mechanism** for current authorization at execution time
   - Could be: decision_ledger query, phi_os.human_gate, Decision API, or other
   - Decision deferred to implementation phase

2. **request_id generation specifics**
   - Pattern, format, generator component
   - Specified as "needed" but not "how"

3. **Expiration of authorizations**
   - Do seals expire if decision approval timestamp is old?
   - Not yet specified in DC_20260713_003

4. **Scope enforcement mechanism**
   - How decisions define scope
   - How seal execution validates scope compliance
   - Not yet specified

5. **Interaction with GL7**
   - After GL7 pre-filter check, how does human decision auth proceed?
   - Sequencing not yet detailed

These items are **IMPLEMENTATION DECISIONS**, not **SPECIFICATION GAPS**.

---

## J. Change Log: Investigation Results

### Specifications Updated from Previous State

**Previous (PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_v1.md)**:
```
Q1: Authoritative Current Authorization Source = UNKNOWN / SPECIFICATION GAP
Q2: Authorization Identifier / Request Linkage = UNKNOWN / SPECIFICATION GAP
```

**Current (This Supplement)**:
```
Q1: Authoritative Current Authorization Source = VERIFIED
    Source: Decision-based (Model B), per DC_20260713_003
    Authority: Human approver (approved_by=human)
    
Q2: Authorization Identifier / Request Linkage = VERIFIED
    Identifier: seal_request_id (per Auth Model specification)
    Linkage: decision_id (basis decision reference)
```

### Specifications NOT Changed

- R04 Phase C Boundary remains: Approval → Current Authorization Check → Execution
- Phase C implementation still frozen (no changes made)
- Schema unchanged
- No new mechanisms created
- No code modified

### Key Discovery

**DC_20260713_003** establishes:
- NOT a Phase C specification (Phase C is separate)
- BUT authoritative for Authorization Boundary design
- Applies to Phase 2+ implementation (Migration Plan M1-M4)
- Current Phase C implementation does NOT yet follow DC_20260713_003 (GAP)

---

## K. Final Status: Evidence Inventory

### Primary Sources (Human Gate Decisions / Approved Designs)

- [x] DC_20260713_003: AUTO_SEAL Boundary Design v1.0 (APPROVED)
- [x] docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md (Section 4.2, 5, 6.1, 8)
- [x] JARVIS_RUNTIME_BETA_ARCHITECTURE_DRAFT_v0.1.md (DC_20260713_003 status: Active)

### Secondary Sources (Supporting Design Docs)

- [x] docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md (Model comparison rationale)
- [x] docs/governance/AUTO_SEAL_M1_IMPLEMENTATION_PROPOSAL_v1.0.md (references DC_20260713_003)
- [x] docs/governance/AUTO_SEAL_M1_TERMINAL_PROCESS_PLAN_v1.0.md (Migration plan continuation)

### Tertiary Sources (Audit/Reference)

- [x] docs/governance/TODO_411_412_413_AUTO_SEAL_BOUNDARY_AUDIT_v1.0.md (audit input to design)

### Gaps in Evidence

- [ ] Actual decision_ledger.jsonl entries (directory does not exist yet)
- [ ] phi_os.human_gate entries (never used for seal authorization yet)
- [ ] Implemented retrieval mechanism (deferred to M1+)

---

## L. Conclusions

### Q1: Authoritative Current Authorization Source

**VERIFIED ANSWER**:
- Source: Human-approved Decision (decision_id)
- Authority: Human approver (approved_by=human)
- Model: Model B (Decision-based), per DC_20260713_003
- Evidence: DC_20260713_003, approved design section 5
- Status: SPECIFICATION COMPLETE (not gap)

**Why Not UNKNOWN**: DC_20260713_003 explicitly specifies the model and required fields.

### Q2: Authorization Identifier / Request Linkage

**VERIFIED ANSWER**:
- Identifier: seal_request_id (unique per seal request)
- Linkage: decision_id (reference to basis Decision)
- Generation: After Decision approval, before GL7 check
- Storage: decision_ledger.jsonl Auth Model fields
- Evidence: DC_20260713_003 Section 5 (Auth Model)
- Status: SPECIFICATION COMPLETE (not gap)

**Why Not UNKNOWN**: DC_20260713_003 explicitly defines the fields and their roles.

---

## M. Disposition

**Current R04 Phase C Status** (REVISED):

```
AUTHORITATIVE CURRENT AUTHORIZATION SOURCE
= Decision-based Model (DC_20260713_003, Model B, Approved)
= Requires: seal_request_id + decision_id + approved_by (human)
= NOT YET IMPLEMENTED IN PHASE C

AUTHORIZATION IDENTIFIER / REQUEST LINKAGE
= seal_request_id + decision_id (DC_20260713_003, Auth Model)
= Location: decision_ledger.jsonl (not yet deployed)
= NOT YET IMPLEMENTED IN PHASE C

PHASE C IMPLEMENTATION CHANGE
= PROHIBITED (frozen)
= Gap remains: Phase C uses approved_by=system (violates DC_20260713_003)
= Gap resolution: Deferred to Phase 2+ (M1+ implementation)
```

**Human Gate Re-Review Status**: AWAITING CLARIFICATION

The authoritative specification EXISTS (DC_20260713_003), but:
1. Phase C does not implement it
2. The gap is acknowledged (not a design uncertainty)
3. Implementation deferral is intentional (per design Section 9: Non Goals)

Question for Human Gate: Should Phase C be updated to align with DC_20260713_003, or should the design reference be formally separated into a future phase?

---

## References

- DC_20260713_003: `docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md`
- Phase C Implementation: `governance/seal_governance_gate.py`
- Phase C Evidence (prior): `docs/governance/PHASE_C_CURRENT_AUTHORIZATION_EVIDENCE_v1.md`
- Active Decision Status: `docs/governance/JARVIS_RUNTIME_BETA_ARCHITECTURE_DRAFT_v0.1.md`
