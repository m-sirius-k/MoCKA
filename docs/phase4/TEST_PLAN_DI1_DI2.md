# DI1/DI2: Comprehensive Test Plan

**Document ID**: TEST_PLAN_20260820  
**Phase**: Phase 4 Design Review  
**Status**: Draft  
**Created**: 2026-08-20  

---

## Purpose

This document defines the complete testing strategy for DI1 (Approved_By Validation) and DI2 (GATE Silent Failure Handling) implementation. Testing occurs across three phases: Unit, Integration, and Local/Acceptance.

---

## Testing Scope

### In Scope
- All requirements from DI1 Scope Definition and Design Specification
- All requirements from DI2 Scope Definition and Error Model Specification
- Integration between DI1 (approval validation) and DI2 (failure handling)
- Local environment testing (before production deployment)

### Out of Scope
- Production deployment testing (separate Change Management process)
- Performance/load testing (future phase)
- UI/UX testing (future phase, if UI added)
- Third-party tool testing (assume tools are working correctly)

---

## Test Execution Environment

**Environment**: Local development environment (Linux, Python, SQLite)

**Tools**:
- Unit Testing: pytest
- Integration Testing: pytest (with fixtures for Event/Decision Ledgers)
- Local Testing: Manual + automated scripts

**Database**: SQLite (same as production)

**Data**: Test data from sample scenarios (non-production fixtures)

---

## Phase 1: Unit Tests

### Unit Test 1.1: DI1 - Approval Schema Validation

**Test Name**: `test_approval_schema_valid()`  
**Objective**: Verify approval record schema is valid for all approval types

**Test Cases**:
1. CODE_REVIEW approval with all required fields → PASS
2. DESIGN_REVIEW approval with all required fields → PASS
3. SECURITY_REVIEW approval with all required fields → PASS
4. GOVERNANCE_REVIEW approval with all required fields → PASS
5. Approval missing required field (approval_type) → FAIL
6. Approval with invalid approval_type value → FAIL
7. Rationale field exceeds max length (500 chars) → FAIL
8. Rationale field within length limit → PASS

**Expected Result**: All 8 cases pass

**Pass Criteria**: Schema validation correctly accepts valid records and rejects invalid ones

---

### Unit Test 1.2: DI1 - Evidence Hash Verification

**Test Name**: `test_evidence_hash_verification()`  
**Objective**: Verify hash comparison detects evidence tampering

**Test Cases**:
1. Artifact hash matches evidence hash → PASS
2. Artifact hash differs from evidence hash → FAIL
3. Evidence hash is corrupted (non-hex string) → FAIL
4. Hash comparison is case-insensitive (SHA256 hex) → PASS
5. Null hash handled correctly → FAIL

**Expected Result**: All 5 cases pass

**Pass Criteria**: Hash verification correctly identifies matching/mismatched hashes

---

### Unit Test 1.3: DI1 - Approval Type Classification

**Test Name**: `test_approval_type_classification()`  
**Objective**: Verify artifacts are correctly classified to approval types

**Test Cases**:
1. Python file (core system) → CODE_REVIEW
2. Architecture document → DESIGN_REVIEW
3. Security-sensitive file (auth, crypto) → SECURITY_REVIEW
4. CONSTITUTION change → GOVERNANCE_REVIEW
5. Multi-category file (security + core) → returns ordered list [SECURITY, DESIGN, CODE]
6. Unknown artifact type → raises exception / undefined

**Expected Result**: All 6 cases handled correctly

**Pass Criteria**: Classification logic maps artifacts to correct type(s)

---

### Unit Test 1.4: DI2 - Error Code Enumeration

**Test Name**: `test_error_code_enumeration()`  
**Objective**: Verify all error codes are defined and unique

**Test Cases**:
1. APPR_E001-E007 all defined and unique
2. VALD_E001-E006 all defined and unique
3. AUTH_E001-E005 all defined and unique
4. TOOL_E001-E005 all defined and unique
5. FILE_E001-E006 all defined and unique
6. GIT_E001-E006 all defined and unique
7. No duplicate error codes across categories
8. Error code → message mapping exists for all codes

**Expected Result**: All 8 cases pass

**Pass Criteria**: Error code registry is complete and consistent

---

### Unit Test 1.5: DI2 - Recovery Action Mapping

**Test Name**: `test_recovery_action_mapping()`  
**Objective**: Verify error code → recovery action mapping is complete

**Test Cases**:
1. APPR_E001-E007 each map to specific recovery action
2. VALD_E001-E006 each map to specific recovery action
3. AUTH_E001-E005 each map to ABORT_AND_NOTIFY_SECURITY (no variation)
4. TOOL_E001-E005 map to retry/refresh/fallback (varies by code)
5. FILE_E001-E006 map to appropriate recovery action
6. GIT_E001-E006 map to appropriate recovery action
7. All error codes have exactly one recovery action (no ambiguity)
8. Recovery actions defined in allowed set: {RETRY, FALLBACK, ABORT_AND_NOTIFY, ABORT_AND_ESCALATE, MANUAL_REVIEW, FIX_AND_RETRY, ABORT_AND_NOTIFY_SECURITY}

**Expected Result**: All 8 cases pass

**Pass Criteria**: Error → recovery mapping is complete, unambiguous, and safe

---

## Phase 2: Integration Tests

### Integration Test 2.1: DI1 - End-to-End CODE_REVIEW Approval

**Test Name**: `test_end_to_end_code_review_approval()`  
**Objective**: Verify complete CODE_REVIEW approval workflow succeeds

**Preconditions**:
- Test file exists: `test_artifacts/sample_router.py`
- Evidence items available: code diff, test results

**Test Steps**:
1. Classify artifact → CODE_REVIEW
2. Gather required evidence (code diff, test results)
3. Verify evidence (hash check, timestamp check)
4. Create approval record with schema
5. Create Decision Ledger entry
6. Create Event record (APPROVAL_ISSUED)
7. Verify bidirectional linkage (approval ↔ decision ledger)

**Expected Result**: All 7 steps succeed

**Assertions**:
- Approval Registry contains new APR record
- Decision Ledger entry references APR record
- Event Ledger shows APPROVAL_ISSUED event
- All timestamps in correct order

**Pass Criteria**: Complete workflow executes without error

---

### Integration Test 2.2: DI1 - End-to-End DESIGN_REVIEW Approval

**Test Name**: `test_end_to_end_design_review_approval()`  
**Objective**: Verify complete DESIGN_REVIEW approval workflow succeeds

**Similar structure to test 2.1, using DESIGN_REVIEW-specific data**

---

### Integration Test 2.3: DI1 - Duplicate Approval Prevention

**Test Name**: `test_duplicate_approval_prevention()`  
**Objective**: Verify system prevents duplicate active approvals

**Test Steps**:
1. Issue approval APR-001 for artifact A
2. Attempt to issue second approval APR-002 for same artifact A
3. System should reject or supersede

**Expected Result**: Either rejection or supersession (handled gracefully)

**Assertions**:
- No two active approvals for same artifact
- If superseded: APR-001 marked "superseded", APR-002 marked "active"
- Both entries preserved in Approval Registry

**Pass Criteria**: Duplicate prevention works correctly

---

### Integration Test 2.4: DI2 - Approval Gate Failure Blocks Operation

**Test Name**: `test_approval_gate_failure_blocks_operation()`  
**Objective**: Verify approval gate failure prevents downstream operation

**Test Steps**:
1. Attempt operation on artifact without approval
2. Gate checks for approval
3. Approval not found (APPR_E004)
4. Gate failure event created
5. Operation aborted (not executed)

**Expected Result**: Operation aborted, gate failure recorded

**Assertions**:
- APPR_E004 error event in Event Ledger
- Operation status: FAILED_GATES_BLOCKED
- Operator notification sent

**Pass Criteria**: Gate failure prevents operation

---

### Integration Test 2.5: DI2 - Error Category Detection

**Test Name**: `test_error_category_detection()`  
**Objective**: Verify all 6 error categories can be detected

**Test Steps** (one per category):
1. APPROVAL_GATE_FAILURE: Approval missing
2. VALIDATION_GATE_FAILURE: Encoding error
3. AUTHORIZATION_GATE_FAILURE: User not authorized
4. TOOL_AVAILABILITY_FAILURE: MCP tool missing
5. FILE_OPERATION_FAILURE: Disk full
6. GIT_OPERATION_FAILURE: Merge conflict

**Expected Result**: Each category detected with correct error code

**Assertions**:
- Event record shows correct error_category
- Error code assigned correctly
- Recovery action determined correctly

**Pass Criteria**: All categories detectable

---

## Phase 3: Local Tests (Acceptance Tests)

### Local Test 3.1 (DI1 Scenario A): Simple File Change with Complete Evidence

**Scenario**: Approve a file change with all required evidence present

**Test Steps**:
1. Create test file: `docs/test_file.md`
2. Prepare evidence: code diff, review checklist
3. Issue CODE_REVIEW approval with evidence references
4. Verify approval record created with all fields
5. Verify Decision Ledger entry created
6. Verify Event Ledger shows APPROVAL_ISSUED

**Expected Result**:
- Approval issued (APR-20260820-NNN)
- Artifact marked with approval_id
- Complete audit trail exists

**Pass Criteria**: All 6 steps succeed

---

### Local Test 3.2 (DI1 Scenario B): Reject Approval Due to Missing Evidence

**Scenario**: Attempt approval without required evidence

**Test Steps**:
1. Create test file
2. Attempt CODE_REVIEW approval with incomplete evidence
3. Gate detects missing evidence item
4. Approval rejected (no APR record created)
5. Error event created
6. Operator notified with remediation steps

**Expected Result**: Approval rejected, error logged

**Pass Criteria**: Missing evidence detected and blocked

---

### Local Test 3.3 (DI1 Scenario C): Hash Mismatch Detection

**Scenario**: Artifact changed after evidence was collected

**Test Steps**:
1. Collect evidence for artifact (hash: ABC123)
2. Modify artifact (hash becomes: XYZ789)
3. Attempt approval with old evidence
4. Validation detects hash mismatch
5. Approval rejected

**Expected Result**: Mismatch detected, approval blocked

**Pass Criteria**: Hash verification prevents stale evidence

---

### Local Test 3.4 (DI1 Scenario D): Approval Revocation

**Scenario**: Revoke previously issued approval

**Test Steps**:
1. Issue approval APR-001 for artifact A
2. Request approval revocation (incident triggered)
3. Human Gate issues revocation decision
4. Mark APR-001 as "REVOKED" in Approval Registry
5. Create Decision Ledger entry for revocation
6. Mark artifact as APPROVAL_REVOKED

**Expected Result**: Approval revoked, artifact marked as no longer approved

**Pass Criteria**: Revocation blocks subsequent operations

---

### Local Test 3.5 (DI2 Scenario 1): Approval Gate Failure Detection and Notification

**Scenario**: Approval gate fails, failure is detected and reported

**Test Steps**:
1. Attempt operation on artifact without approval
2. Gate checks Approval Registry
3. Approval not found (APPR_E004 error)
4. Event record created: type=GATE_FAILURE, category=APPROVAL_GATE_FAILURE
5. Decision Ledger updated: status=BLOCKED_BY_GATE_FAILURE
6. Operator notification sent with remediation: "Approval missing for artifact X"

**Expected Result**: Failure detected, operator notified, operation blocked

**Pass Criteria**: Silent failure prevented

---

### Local Test 3.6 (DI2 Scenario 2): Validation Gate Retry Success

**Scenario**: Validation fails on first attempt, auto-fix applied, retry succeeds

**Test Steps**:
1. Attempt file write with encoding error (CP932 contamination)
2. Validation gate detects VALD_E006 error
3. Auto-fix applied: remove CP932 bytes, save UTF-8
4. Retry validation (second attempt)
5. Second attempt succeeds (hash verification passes)
6. Operation continues

**Expected Result**: Recovery attempted, operation succeeds after fix

**Pass Criteria**: Automatic recovery effective

---

### Local Test 3.7 (DI2 Scenario 3): Tool Availability with Schema Drift

**Scenario**: Tool unavailable due to MCP schema change, detected and recovered

**Test Steps**:
1. Call mocka_decision_write tool
2. Tool not in current session registry (TOOL_E001)
3. Detect schema hash mismatch (current != expected)
4. Refresh tool registry (re-fetch from server)
5. Schema hash updated
6. Retry tool call (succeeds)

**Expected Result**: Tool becomes available after refresh, operation succeeds

**Pass Criteria**: Schema drift handled gracefully

---

### Local Test 3.8 (DI2 Scenario 4): Authorization Gate Failure (No Retry)

**Scenario**: User unauthorized, operation blocked, no recovery attempted

**Test Steps**:
1. User without authorization attempts core system modification
2. Authorization gate checks permissions
3. User not authorized (AUTH_E001)
4. Recovery action: ABORT_AND_NOTIFY_SECURITY
5. NO retry (security failures don't retry)
6. Security incident logged

**Expected Result**: Operation blocked immediately, security incident recorded

**Pass Criteria**: Authorization failure never retried

---

### Local Test 3.9 (DI2 Scenario 5): File Operation Rollback

**Scenario**: File write succeeds but verification fails, rollback applied

**Test Steps**:
1. Write file to disk
2. Read-back verification (hash check)
3. Hash mismatch detected (FILE_E005)
4. Recovery action: ABORT_AND_FIX_ENCODING
5. Restore previous file version
6. Log rollback action

**Expected Result**: File rolled back to consistent state

**Pass Criteria**: Rollback prevents data corruption

---

### Local Test 3.10 (DI2 Scenario 6): Git Merge Conflict Detection

**Scenario**: Merge conflict detected, operation aborted, repo left clean

**Test Steps**:
1. Attempt merge of conflicting branch
2. Git merge returns conflict (GIT_E001)
3. Recovery action: ABORT_AND_REQUIRE_MANUAL
4. Merge not completed (repository left in merge state? NO - aborted)
5. Conflicting files identified
6. Operator notified with conflict list

**Expected Result**: Conflict detected, manual resolution required, repo safe

**Pass Criteria**: Merge conflicts handled safely

---

## Phase 4: Regression Tests (After Implementation)

### Regression Test 4.1: Existing Approval Validation Still Works

**Objective**: Ensure DI1 implementation doesn't break existing approval validation

**Test**: Run test suite on existing approved artifacts

**Expected**: 100% of existing approvals remain valid

---

### Regression Test 4.2: Existing Gate Execution Still Succeeds

**Objective**: Ensure DI2 implementation doesn't break normal (non-error) gate execution

**Test**: Run 10 normal operations through all gates

**Expected**: All operations succeed without errors (when gates should pass)

---

## Test Execution Schedule

**Phase 1 (Unit Tests)**: Before Integration Phase
- Expected duration: 2 weeks
- Owner: Implementation team
- Artifacts: Unit test code, test results report

**Phase 2 (Integration Tests)**: During Integration Phase
- Expected duration: 3 weeks
- Owner: Implementation team
- Artifacts: Integration test code, test results, coverage report

**Phase 3 (Local Tests)**: After Integration Phase
- Expected duration: 2 weeks
- Owner: Implementation team + Human Gate reviewer
- Artifacts: Local test scripts, evidence collection, test evidence

**Phase 4 (Regression Tests)**: Before Production Deployment
- Expected duration: 1 week
- Owner: QA team
- Artifacts: Regression test report

---

## Pass/Fail Criteria

### Phase 1 Unit Tests
- **Pass**: All test cases pass
- **Fail**: Any test case fails (must be fixed before moving to Phase 2)

### Phase 2 Integration Tests
- **Pass**: All integration tests pass, 100% code coverage for critical paths
- **Fail**: Any integration test fails OR coverage < 95%

### Phase 3 Local Tests
- **Pass**: All 10 scenarios complete successfully, operator confirmation
- **Fail**: Any scenario fails OR Human Gate has concerns

### Phase 4 Regression Tests
- **Pass**: 100% of existing operations unaffected
- **Fail**: Any existing operation breaks

---

## Test Evidence Archival

All test evidence (logs, error messages, recovered files, etc.) shall be archived in:
- `data/evidence/test_phase1/` (unit tests)
- `data/evidence/test_phase2/` (integration tests)
- `data/evidence/test_phase3/` (local tests)
- `data/evidence/test_phase4/` (regression tests)

Evidence preserved for audit trail and post-mortem analysis.

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Draft | Claude (Phase 4 Design Review) | Initial test plan |

