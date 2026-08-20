# DI1: Approved_By Validation - Scope Definition

**Document ID**: DI1_SCOPE_20260820  
**Phase**: Phase 4 Controlled Development  
**Status**: Draft  
**Created**: 2026-08-20  
**Authority**: Human Gate Final Decision 2026-08-20  

---

## 1. Problem Definition

### Current Issue

The `approved_by` field appears throughout MoCKA governance structures (Decision Ledger, Integrity Records, Event Classifications) to indicate authorization or acceptance. However, the current implementation exhibits the following gaps:

1. **Rationale Disconnection**: `approved_by` records the authorizer but NOT the decision rationale, acceptance criteria, or evidence base
2. **Scope Ambiguity**: It is unclear what "approval" means in different contexts (Decision Ledger vs. Integrity vs. Event validation)
3. **Verification Void**: There is no mechanism to verify that the approval was based on actual review of the target artifact
4. **Evidence Linkage Missing**: No explicit connection between `approved_by` and supporting evidence (Decision Ledger entries, Incident reports, verification results)
5. **Auditability Gap**: Auditors cannot reconstruct WHY a given approval was issued or trace its decision path

### Impact

- **Governance Risk**: Claimed approvals cannot be independently verified
- **Record Integrity Risk**: approved_by values could be inconsistent with actual review history
- **Certification Risk**: Published artifacts (papers, public repos) claim Human Gate approval but lack traceable evidence chain
- **Trust Boundary Weakness**: DI2 (silent failure handling) cannot properly validate approval state if approval itself lacks verification

---

## 2. Current State

### Existing Implementation

```
approved_by locations:
- Decision Ledger: approved_by (string)
- Integrity Records: approved_by (string, optional)
- Event Records: Sometimes implicit in tags
- MOCKA_OVERVIEW.json: Various approval statements (e.g., "Human Gate承認済み")
```

### Current Validation Approach

- **None formally defined**: Approval is accepted at face value
- **No verification layer**: No checklist or evidence requirement before approval is recorded
- **No tracking**: No audit trail of approval process

### Related Prior Incidents

- E20260621: ChatGPT upper-cased content without approval flow
- TODO_154: File edit rule mentions approval but does not specify approval validation
- IC_20260705_018: Tool absence detected but approval of fix not formalized

---

## 3. Target State

### Validation Framework Goals

1. **Explicit Rationale Capture**
   - Each `approved_by` entry SHALL include decision rationale (short summary)
   - Evidence references (event IDs, decision ledger entries, verification results)

2. **Scope Clarity**
   - Define distinct approval types: CODE_REVIEW, DESIGN_REVIEW, SECURITY_REVIEW, GOVERNANCE_REVIEW
   - Each type has specific requirements and evidence expectations

3. **Verification Chain**
   - `approved_by` SHALL link to evidence artifacts
   - Approval SHALL only be issued after evidence review is complete
   - Evidence SHALL be independently retrievable

4. **Auditability**
   - Auditors SHALL be able to reconstruct the approval decision from stored records
   - Decision path SHALL be traceable from artifact -> approval record -> decision rationale -> evidence

5. **Consistency**
   - All `approved_by` usage SHALL follow the same schema
   - No implicit or informal approval
   - Approval SHALL be atomic (decide yes/no, not conditional approval)

---

## 4. Boundary Definition

### In Scope

- Decision Ledger `approved_by` field validation
- Integrity Record `approved_by` field validation
- Public artifact approval (paper submissions, public repo releases)
- Governance-level approvals (CONSTITUTION changes, INSTITUTION changes)
- Design review approvals (Architecture decisions, major refactors)

### Out of Scope

- Individual commit approvals (handled by Git PR review)
- Tool-level permissions (handled by RBAC)
- Routine operational decisions (logged as events, not approvals)
- Retroactive approval of past events (only forward-looking validation)

### Interfaces to Other DIs

- **DI2 Connection**: DI2 silent failure handling depends on reliable approval validation
  - If approval cannot be verified, DI2 cannot determine whether a critical gate passed
- **DI3 Connection**: DI3 Architecture Evaluation may reference approved designs
  - Approval must be traceable to evaluation report

---

## 5. Non-Goals

- **Not changing approval authority**: Still Human Gate (博士), not expanding approvers
- **Not retroactive audit**: Not auditing past approvals, only establishing forward validation
- **Not approval workflow changes**: Not implementing approval request/queue/workflow UI
- **Not extending to all decisions**: Only decisions that are explicitly marked `approved_by`

---

## 6. Acceptance Criteria

The Scope Definition SHALL be accepted when:

- [ ] Approval types and their distinct requirements are clearly enumerated
- [ ] Evidence schema for each approval type is defined (what qualifies as sufficient evidence)
- [ ] Scope boundaries are unambiguous and stakeholders agree
- [ ] Non-goals are confirmed and documented
- [ ] Interfaces to DI2 and DI3 are identified and documented
- [ ] No contradictions with existing CONSTITUTION or INSTITUTION architecture

### Success Metrics for Implementation Phase

- [ ] All Decision Ledger entries have decision rationale captured
- [ ] All published artifacts have approval chain traceable to evidence
- [ ] Zero "approved_by" records with missing or invalid evidence references
- [ ] Audit log shows 100% of approval decisions can be independently verified

---

## 7. Next Steps

Once this Scope Definition is approved:

1. **DI1 Design Specification Draft** will detail:
   - Approval type taxonomy
   - Evidence schema for each type
   - Validation flow (who validates, when, based on what criteria)
   - Data handling model (how approval data is stored, accessed, modified)
   - Failure conditions and recovery actions
   - Test specification

2. **Evidence Collection Plan** will define:
   - How approval evidence is captured during normal operation
   - How past approvals are retroactively verified (if applicable)
   - Reporting requirements (what auditors need to see)

3. **Local Test Plan** will verify:
   - Approval validation logic is sound
   - Evidence chain is complete for sample approvals
   - No existing approvals are inadvertently invalidated

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Draft | Claude (Phase 4 Execution) | Initial scope definition |

