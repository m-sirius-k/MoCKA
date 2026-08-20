# DI1: Approved_By Validation - Traceability Matrix

**Document ID**: DI1_TRACE_20260820  
**Phase**: Phase 4 Design Review  
**Status**: Draft  
**Created**: 2026-08-20  

---

## Overview

This matrix maps:
- **Requirements** (from Scope Definition) → 
- **Design Elements** (from Design Specification) → 
- **Test Scenarios** (from Design Specification + Test Plan) → 
- **Evidence** (to be collected during implementation)

---

## Requirement 1: Explicit Rationale Capture

| Aspect | Design Element | Test Scenario | Evidence Type | Traceability |
|--------|---|---|---|---|
| **Requirement** | Each `approved_by` entry SHALL include decision rationale (short summary) | | | Scope Definition §1 |
| **Design** | Approval Type Taxonomy (§1) + Data Schema for each type | Rationale field in JSON (max 500 chars) | | Design Spec §1, §3 |
| **Design** | Evidence Recording Method (§5) | Event Ledger records approval with rationale field | | Design Spec §5 |
| **Test: Unit** | Schema validation for rationale field | test_approval_schema_valid() checks rationale length (1-500) | Unit test result | Design Spec §6 |
| **Test: Integration** | End-to-end approval with rationale | test_end_to_end_code_review_approval() - Scenario A | JSON approval record contains rationale | Design Spec §6 |
| **Test: Local** | Scenario A: Simple file change with rationale | Approve file, verify rationale captured | Approval Registry entry shows rationale | Design Spec §6, Scenario A |
| **Evidence: Runtime** | Approval Registry contains rationale for all approved artifacts | data/approvals/approval_registry.jsonl sample | Rationale field present in 100% of records | Evidence Collection |
| **Audit** | Auditors can read approval rationale via approval_id lookup | mocka_read_approval(approval_id) returns complete record | Full approval record with rationale | Evidence Collection |

---

## Requirement 2: Scope Clarity - Distinct Approval Types

| Aspect | Design Element | Test Scenario | Evidence Type | Traceability |
|--------|---|---|---|---|
| **Requirement** | Define distinct approval types: CODE_REVIEW, DESIGN_REVIEW, SECURITY_REVIEW, GOVERNANCE_REVIEW | | | Scope Definition §2 |
| **Design** | Approval Type Taxonomy (§1) with 4 types, each with distinct schema | 4 JSON schemas defined | | Design Spec §1 |
| **Design** | Error Code mapping: approval_type → required evidence items | Error codes APPR_E001-E007 map to type-specific validation | | Design Spec §1 |
| **Test: Unit** | Type classification logic | test_approval_type_classification() - each artifact maps to correct type | Artifact → Type mapping correct | Design Spec §6 |
| **Test: Integration** | Each type executes correct validation flow | test_end_to_end_code_review_approval() + design_review + security_review | 4 separate end-to-end flows pass | Design Spec §6 |
| **Test: Local** | Type classification accuracy | Scenario A (CODE_REVIEW), B (DESIGN_REVIEW) | Correct type assigned | Design Spec §6 |
| **Evidence: Runtime** | All approval records include approval_type field | Sample of approval_registry.jsonl | Type field present in 100% | Evidence Collection |
| **Audit** | Approval type is traceable from artifact to Decision Ledger | approval_id → Decision Ledger entry shows type | Decision Ledger includes approval_type | Evidence Collection |

---

## Requirement 3: Verification Chain - Evidence Linkage

| Aspect | Design Element | Test Scenario | Evidence Type | Traceability |
|--------|---|---|---|---|
| **Requirement** | Approval SHALL link to evidence artifacts | | | Scope Definition §2 |
| **Design** | Data Handling Model (§3) - evidence_ids array in approval record | JSON schema includes evidence_ids: ["E20260820_XXXXX", ...] | | Design Spec §3 |
| **Design** | Evidence Verification (§3, Validation Check step) | Hash verification, timestamp check | | Design Spec §3 |
| **Design** | Consistency Rule 3: "Evidence IDs must exist in Event/Integrity ledgers" | Validation fails if evidence not found | | Design Spec §3 |
| **Test: Unit** | Evidence hash verification | test_evidence_hash_verification() - hash match detection | Hash comparison result | Design Spec §6 |
| **Test: Unit** | Duplicate prevention | test_duplicate_approval_prevention() - rejects duplicate approval | Rejection reason logged | Design Spec §6 |
| **Test: Integration** | Evidence chain validation | test_approval_audit_trail() - complete chain traceable | Audit log shows all links | Design Spec §6 |
| **Test: Local** | Scenario A: Evidence present and valid | File change with complete evidence | Approval issued | Design Spec §6, Scenario A |
| **Test: Local** | Scenario B: Evidence missing | File change without required evidence | Approval rejected, error logged | Design Spec §6, Scenario B |
| **Test: Local** | Scenario C: Hash mismatch | Artifact changed after evidence collected | Validation fails | Design Spec §6, Scenario C |
| **Evidence: Runtime** | All approval records link to valid evidence | data/evidence/evidence_registry.jsonl | Evidence IDs resolve correctly | Evidence Collection |
| **Audit** | Broken evidence links detected | Integrity check report | evidence_id → not found = 0 cases | Evidence Collection |

---

## Requirement 4: Auditability - Approval Decision Reconstruction

| Aspect | Design Element | Test Scenario | Evidence Type | Traceability |
|--------|---|---|---|---|
| **Requirement** | Auditors SHALL reconstruct approval decision from stored records | | | Scope Definition §2 |
| **Design** | Approval Record Schema (§3) includes approval_id, timestamp, decision_ledger_ref | JSON schema with all fields | | Design Spec §3 |
| **Design** | Bidirectional linkage: approval_id ↔ decision_ledger_ref | Approval Ledger + Decision Ledger cross-references | | Design Spec §3 |
| **Design** | Approval Registry is append-only (immutable) | No updates/deletes to approval_registry.jsonl | | Design Spec §3 |
| **Design** | Event Ledger records approval issuing (type: APPROVAL_ISSUED) | Event record created for each approval | | Design Spec §3 |
| **Test: Integration** | Complete audit trail reconstruction | test_approval_audit_trail() - full chain from artifact to evidence | Audit trail complete | Design Spec §6 |
| **Test: Local** | Scenario A: Audit trail from file change to approval | File → approval → decision → evidence | Chain unbroken | Design Spec §6, Scenario A |
| **Test: Local** | Scenario D: Approval revocation traceability | Revocation → incident report → decision | Revocation chain traceable | Design Spec §6, Scenario D |
| **Evidence: Runtime** | Approval audit trail for 100% of active approvals | Sample of 10 random approvals | All traceable | Evidence Collection |
| **Audit** | Decision path reconstruction success rate | Audit script attempts to reconstruct 10 approvals | 100% success rate | Evidence Collection |

---

## Requirement 5: Consistency - No Implicit Approval

| Aspect | Design Element | Test Scenario | Evidence Type | Traceability |
|--------|---|---|---|---|
| **Requirement** | All `approved_by` usage SHALL follow same schema | | | Scope Definition §2 |
| **Design** | mocka_write_approval() function enforces schema (§3) | Function validates against type-specific schema | | Design Spec §3 |
| **Design** | Consistency Rule 1: "No two active approvals for same artifact" | Only one approval_id per artifact at any time | | Design Spec §3 |
| **Design** | Consistency Rule 2: "All approved_by fields reference Approval Registry" | Validation check in step 3 of Validation Flow | | Design Spec §2 |
| **Design** | Consistency Rule 4: "Approval atomic with Decision Ledger entry" | Decision Ledger entry created atomically with approval | | Design Spec §2 |
| **Test: Unit** | Schema validation enforcement | test_approval_schema_valid() - invalid schemas rejected | Rejection reason | Design Spec §6 |
| **Test: Unit** | Duplicate prevention | test_duplicate_approval_prevention() | Duplicate rejected | Design Spec §6 |
| **Test: Unit** | Decision Ledger linkage | Decision Ledger entry created and linked | DC entry references approval_id | Design Spec §6 |
| **Test: Integration** | Consistency check across all approvals | Integrity check scans Approval Registry for inconsistencies | Orphan approved_by = 0 | Design Spec §6 |
| **Test: Local** | Scenario A: Single approval per artifact | Approve file A once | Only one APR record exists | Design Spec §6, Scenario A |
| **Test: Local** | Superseded approval handling | Issue second approval for same artifact | First marked "superseded", second is "active" | Design Spec §6, Scenario C |
| **Evidence: Runtime** | Consistency violations found in scan | Integrity check report | Inconsistencies = 0 | Evidence Collection |
| **Audit** | approved_by field always links to valid Approval Registry entry | Audit script checks 100% of approved_by references | Broken links = 0 | Evidence Collection |

---

## Requirement 6: Acceptance Criteria - Scope Definition Approval

| Aspect | Design Element | Test Scenario | Evidence Type | Traceability |
|--------|---|---|---|---|
| **Requirement** | Approval types clearly enumerated | | | Scope Definition §6 |
| **Design** | Approval Type Taxonomy (§1) - 4 types with distinct requirements | | Design Spec §1 | |
| **Evidence** | All 4 types documented with examples | | | Design Spec §1 |
| **Requirement** | Evidence schema defined for each type | | | Scope Definition §6 |
| **Design** | Data Schema sections for each type (§1) | | Design Spec §1 | |
| **Evidence** | Sample evidence for each type | | | Design Spec §1 |
| **Requirement** | Scope boundaries unambiguous | | | Scope Definition §6 |
| **Design** | Scope Definition (§2-4) clearly states in/out of scope | | Scope Def §2-4 | |
| **Evidence** | No ambiguous cases identified in test | | | Local Tests |
| **Requirement** | No contradictions with CONSTITUTION | | | Scope Definition §6 |
| **Design** | Design aligns with MoCKA governance principles | | Design Spec | |
| **Evidence** | Human Gate verifies no contradictions | | | Review Package |

---

## Summary: Coverage Matrix

| Requirement | Scope Def Coverage | Design Spec Coverage | Test Coverage | Evidence Collection |
|---|---|---|---|---|
| 1. Explicit Rationale | §2 | §1, §3, §5 | Unit + Integration + Local A | Runtime + Audit |
| 2. Scope Clarity | §2 | §1 | Unit + Integration + Local A,B | Runtime + Audit |
| 3. Verification Chain | §2 | §1, §2, §3 | Unit + Integration + Local A,B,C | Runtime + Audit |
| 4. Auditability | §2 | §2, §3 | Integration + Local A,D | Runtime + Audit |
| 5. Consistency | §2 | §2, §3 | Unit + Integration + Local A,C | Runtime + Audit |
| 6. Acceptance Criteria | §6 | All | All | Review Package |

**Overall Coverage**: 100% - All requirements traced to design elements and tests

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Draft | Claude (Phase 4 Design Review) | Initial traceability matrix |

