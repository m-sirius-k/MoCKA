# DI1: Approved_By Validation - Design Specification Draft

**Document ID**: DI1_DESIGN_20260820  
**Phase**: Phase 4 Controlled Development  
**Status**: Draft for Review  
**Created**: 2026-08-20  
**Authority**: Human Gate Final Decision 2026-08-20  

---

## 1. Approval Type Taxonomy

### Type 1: CODE_REVIEW

**Scope**: Changes to core system files, critical infrastructure  
**Triggers**: Commit to main, change to `is_core_system_file()` inventory  
**Approver**: Human Gate (博士)  

**Evidence Requirements**:
- [ ] Code diff reviewed for security/integrity issues
- [ ] Dependency analysis performed (breaking changes identified)
- [ ] Test results available (if applicable)
- [ ] UTF-8 validation completed (for Python/JS)
- [ ] Decision Ledger entry created with rationale

**Data Schema**:
```json
{
  "approval_type": "CODE_REVIEW",
  "target": "file_path or commit_hash",
  "approved_by": "nsjpkimura@gmail.com",
  "approved_at": "2026-08-20T12:00:00Z",
  "rationale": "Brief explanation of why changes are acceptable",
  "evidence_ids": ["E20260820_XXXXX", "E20260820_YYYYY"],
  "decision_ledger_ref": "DC_20260820_NNN",
  "previous_version_hash": "sha256(...)",
  "new_version_hash": "sha256(...)"
}
```

---

### Type 2: DESIGN_REVIEW

**Scope**: Architecture decisions, major design documents, system contracts  
**Triggers**: TODO status change to "完了", new ARCHITECTURE_CONTRACT entry  
**Approver**: Human Gate (博士)  

**Evidence Requirements**:
- [ ] Design document reviewed for clarity and completeness
- [ ] Trade-offs and alternatives documented
- [ ] Risk analysis performed
- [ ] Stakeholder feedback incorporated
- [ ] Decision Ledger entry created with design rationale

**Data Schema**:
```json
{
  "approval_type": "DESIGN_REVIEW",
  "target": "design_document_path or architecture_id",
  "approved_by": "nsjpkimura@gmail.com",
  "approved_at": "2026-08-20T12:00:00Z",
  "rationale": "This design satisfies requirements X, Y, Z by approach A",
  "evidence_ids": ["E20260820_XXXXX"],
  "decision_ledger_ref": "DC_20260820_NNN",
  "supersedes": "old_design_id (if applicable)",
  "validity_period": "permanent | until:date"
}
```

---

### Type 3: SECURITY_REVIEW

**Scope**: Security-sensitive changes (auth, crypto, data access, external integrations)  
**Triggers**: Manual request, automated detection of sensitive file changes  
**Approver**: Human Gate (博士)  

**Evidence Requirements**:
- [ ] Security threat model reviewed
- [ ] Vulnerability scan results available
- [ ] Penetration test results (if applicable)
- [ ] Cryptography review (if applicable)
- [ ] Decision Ledger entry created with security analysis

**Data Schema**:
```json
{
  "approval_type": "SECURITY_REVIEW",
  "target": "file_path or feature",
  "approved_by": "nsjpkimura@gmail.com",
  "approved_at": "2026-08-20T12:00:00Z",
  "rationale": "No critical vulnerabilities detected. Risk level: LOW",
  "evidence_ids": ["E20260820_SCAN", "E20260820_REVIEW"],
  "decision_ledger_ref": "DC_20260820_NNN",
  "threat_level": "LOW | MEDIUM | HIGH",
  "conditions": "Conditional approval (if list of conditions applies)"
}
```

---

### Type 4: GOVERNANCE_REVIEW

**Scope**: Changes to CONSTITUTION, INSTITUTION, governance rules, Decision Ledger entries  
**Triggers**: Change to docs/governance/, modification to operation mode  
**Approver**: Human Gate (博士) or specified Authority  

**Evidence Requirements**:
- [ ] Governance impact analysis performed
- [ ] Consistency check with existing constitution
- [ ] Stakeholder notification plan identified
- [ ] Rollback plan documented
- [ ] Decision Ledger entry created

**Data Schema**:
```json
{
  "approval_type": "GOVERNANCE_REVIEW",
  "target": "governance_document or policy_id",
  "approved_by": "nsjpkimura@gmail.com",
  "approved_at": "2026-08-20T12:00:00Z",
  "rationale": "Change is consistent with MoCKA principles and improves institutional stability",
  "evidence_ids": ["E20260820_IMPACT", "E20260820_CONSISTENCY"],
  "decision_ledger_ref": "DC_20260820_NNN",
  "effective_date": "2026-08-21",
  "sunset_date": null,
  "notification_plan": "Documented in E20260820_NOTIFY"
}
```

---

## 2. Validation Flow

### Flow Diagram

```
Artifact/Change → Classify Type → Gather Evidence → Validation Check → 
Validation OK? 
  ├─ YES → Record approval → Update Decision Ledger → Mark Complete
  └─ NO  → Log rejection reason → Notify owner → Request corrections
```

### Detailed Steps

**Step 1: Classify Approval Type**
- Determine which type applies based on artifact category
- If multiple types apply, execute in order: SECURITY > DESIGN > CODE > GOVERNANCE
- If type is unclear, escalate to Human Gate for classification

**Step 2: Gather Evidence**
- Check Evidence Registry for existing evidence items
- If evidence incomplete, list missing items
- Request owner/reviewer to provide missing evidence
- Verify evidence timestamps are recent (within 30 days)

**Step 3: Validation Check**
- For each evidence item, verify:
  - Evidence exists and is readable
  - Evidence is linked to correct artifact (via hash/ID)
  - Evidence is not contradicted by other evidence
  - If CODE_REVIEW: verify SHA256 hashes match
- Confirm all required evidence types are present

**Step 4: Record Approval**
- If validation passes:
  - Create approval record with schema matching approval type
  - Generate approval ID: APR-{DATE}-{SEQUENCE}
  - Record in Approval Registry (JSON file)
  - Create Decision Ledger entry linking to approval
  - Create Event record for audit trail
- If validation fails:
  - Create rejection record with specific failure reasons
  - Do NOT create approval record
  - Notify requestor with remediation steps

**Step 5: Update Artifact**
- Update target artifact with `approved_by` field
- Link back to approval ID
- Update all related metadata (MOCKA_OVERVIEW.json if needed)

---

## 3. Data Handling Model

### Storage

**Approval Registry** (`data/approvals/approval_registry.jsonl`)
- Append-only log of all approval records (accepted or rejected)
- One JSON object per line
- Indexed by approval_id for fast lookup

**Decision Ledger**
- Each approval generates a Decision Ledger entry (DC_XXXXXX)
- Decision Ledger entry references approval_id
- Bidirectional linkage for auditability

**Event Log**
- Approval event recorded in Event Ledger
- Event type: "APPROVAL_ISSUED" or "APPROVAL_REJECTED"
- Links to approval_id and artifact

### Access Control

- **Read**: All AIassistants can read approval records (needed for validation)
- **Write**: Only mocka_write_approval() function can create approval records
  - Function validates approval schema
  - Function verifies evidence presence
  - Function prevents duplicate approvals
- **Audit**: Approval Registry is immutable (append-only, no updates or deletes)

### Consistency Rules

- Rule 1: No two active approvals for same artifact (only one can be current)
  - Older approval is marked "superseded" when new approval issued
  - Superseded approval is retained for audit trail
- Rule 2: All `approved_by` fields must reference a corresponding Approval Registry entry
  - Orphan `approved_by` fields are flagged during integrity checks
- Rule 3: Evidence IDs in approval record must exist in Event/Integrity ledgers
  - Validation fails if evidence is deleted
- Rule 4: Approval cannot be issued without corresponding Decision Ledger entry
  - Decision Ledger entry is created atomically with approval

---

## 4. Failure Conditions and Recovery

### Failure Condition 1: Missing Evidence

**Symptom**: Evidence Registry lookup returns empty  
**Detection**: Validation Check step, immediately rejects  
**Recovery**:
1. Log rejection with specific missing evidence items
2. Notify requestor: "Evidence missing: [list]"
3. Requestor provides evidence
4. Retry validation (evidence gathering step)

**Prevention**: Evidence Collection Plan should ensure evidence is available BEFORE approval is requested

---

### Failure Condition 2: Evidence Hash Mismatch

**Symptom**: Artifact SHA256 hash does not match evidence record  
**Detection**: Validation Check step, before final approval  
**Recovery**:
1. Log rejection: "Artifact has changed since evidence was captured"
2. Notify requestor: "Re-validate evidence after changes"
3. Request owner re-run validation tests
4. Retry validation

**Prevention**: Timestamp checks ensure evidence is recent (within 30 days)

---

### Failure Condition 3: Contradictory Evidence

**Symptom**: Two evidence items support contradictory conclusions  
**Detection**: Manual review during Validation Check (not automated)  
**Recovery**:
1. Log rejection with both evidence references
2. Escalate to Human Gate for manual adjudication
3. Human Gate issues binding decision
4. Update approval with adjudication note
5. Issue approval based on Human Gate decision

**Prevention**: Evidence Classification Plan specifies which evidence takes precedence

---

### Failure Condition 4: Approver Unavailable

**Symptom**: Approver (Human Gate/博士) is unreachable  
**Detection**: Timeout during approval issuing (no response for 72 hours)  
**Recovery**:
1. Log pending approval request
2. Designate fallback approver (if constitution defines one)
3. Fallback approver reviews and issues approval
4. Document fallback in Decision Ledger entry (rationale="fallback_approver")
5. If no fallback exists, mark approval as "PENDING_APPROVER"

**Prevention**: Establish SLA for approval turnaround time in INSTITUTION

---

### Failure Condition 5: Approval Revocation Request

**Symptom**: Approval is later found to be invalid or based on faulty evidence  
**Detection**: Via incident report or manual audit  
**Recovery**:
1. Create incident report with evidence of invalidity
2. Escalate to Human Gate
3. Human Gate issues revocation decision
4. Create new Decision Ledger entry (status=REVOKED, links to incident)
5. Mark original approval as "REVOKED" in Approval Registry
6. Notify all dependent artifacts that approval is no longer valid
7. Artifacts are marked as "APPROVAL_REVOKED" until re-approved

**Prevention**: Regular audit cycle checks for approval validity

---

## 5. Evidence Recording Method

### During Approval Process

**When Evidence is Generated**:
1. Evidence is automatically recorded as Event record
   - Event type: "EVIDENCE_GENERATED"
   - Tags: "approval_evidence", approval_type
   - Includes reference to target artifact

2. Evidence is indexed in Evidence Registry
   - Evidence ID: linked to Event ID
   - Hash: SHA256 of evidence content
   - Type: CODE_REVIEW, SECURITY_SCAN, etc.
   - Timestamp: when evidence was generated

3. Evidence is stored persistently
   - Code diffs → Git commit history (via git show)
   - Security scans → data/evidence/security_scans/
   - Design reviews → Linked to design document repo
   - Test results → data/evidence/test_results/

### Approval Record Generation

When approval is issued:

```python
approval_record = {
  "approval_id": "APR-20260820-001",
  "approval_type": "CODE_REVIEW",
  "target": "interface/router.py",
  "approved_by": "nsjpkimura@gmail.com",
  "approved_at": "2026-08-20T12:30:00Z",
  "rationale": "Router changes are backward compatible and improve error handling",
  "evidence_ids": ["E20260820_CODE", "E20260820_TEST"],
  "decision_ledger_ref": "DC_20260820_042",
  "status": "ACTIVE"
}
```

Approval record is appended to `data/approvals/approval_registry.jsonl`

---

## 6. Test Requirements

### Unit Tests

- [ ] `test_approval_schema_valid()` - Schema validation works correctly
- [ ] `test_evidence_hash_verification()` - Hash verification detects tampering
- [ ] `test_approval_type_classification()` - Classification logic correct
- [ ] `test_duplicate_approval_prevention()` - Cannot issue duplicate approval
- [ ] `test_decision_ledger_linkage()` - Approval correctly links to Decision Ledger

### Integration Tests

- [ ] `test_end_to_end_code_review_approval()` - Full CODE_REVIEW workflow succeeds
- [ ] `test_end_to_end_design_review_approval()` - Full DESIGN_REVIEW workflow succeeds
- [ ] `test_missing_evidence_rejection()` - Missing evidence causes rejection
- [ ] `test_approval_audit_trail()` - Complete audit trail is traceable
- [ ] `test_approval_revocation()` - Revocation correctly marks approval as invalid

### Local Test Scenarios

1. **Scenario A**: Approve a simple file change with complete evidence
   - Input: file, evidence items, rationale
   - Expected: Approval issued, Decision Ledger entry created
   - Verification: Approval Registry contains new record

2. **Scenario B**: Reject approval due to missing evidence
   - Input: file, incomplete evidence list
   - Expected: Rejection issued, no approval record created
   - Verification: Approval Registry unchanged, Event log shows rejection

3. **Scenario C**: Detect hash mismatch during validation
   - Input: artifact hash changed after evidence was collected
   - Expected: Validation fails, approval rejected
   - Verification: Rejection reason logged with hash details

4. **Scenario D**: Revoke previously issued approval
   - Input: Incident report showing approval was invalid
   - Expected: Approval marked as REVOKED
   - Verification: Approval Registry shows REVOKED status, new Decision Ledger entry

---

## 7. Implementation Notes

### Design Assumptions

- Approval authority remains Human Gate (博士), not delegated
- Approval is binary (YES/NO), not conditional
- Once issued, approval is persistent (cannot be silently changed)
- Approval is artifact-specific, not blanket approval

### Known Constraints

- Requires Evidence Registry to be available and reliable
- Decision Ledger must be accessible during approval process
- May block operation if approval cannot be issued (need fallback mechanism)

### Dependencies

- Decision Ledger (DC_XXXXX) system must be operational
- Event Ledger must accept APPROVAL_ISSUED events
- Evidence Registry must be queryable

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Draft | Claude (Phase 4 Execution) | Initial design specification |

