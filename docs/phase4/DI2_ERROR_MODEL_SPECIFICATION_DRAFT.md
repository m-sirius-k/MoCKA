# DI2: GATE Silent Failure Handling - Error Model Specification Draft

**Document ID**: DI2_ERROR_MODEL_20260820  
**Phase**: Phase 4 Controlled Development  
**Status**: Draft for Review  
**Created**: 2026-08-20  
**Authority**: Human Gate Final Decision 2026-08-20  

---

## 1. Error Category Taxonomy

### Category 1: APPROVAL_GATE_FAILURE

**Description**: Approval gate execution failed (from DI1 validation)  
**Root Causes**:
- Evidence is missing
- Evidence hash mismatch with artifact
- Approval evidence contradicts itself
- Approval was revoked
- Approval record not found in Approval Registry

**Severity**: CRITICAL  
**Propagation**: Blocks all downstream operations  

**Error Code Schema**:
```
APPR_E001: Evidence missing for artifact
APPR_E002: Evidence hash mismatch
APPR_E003: Contradictory evidence detected
APPR_E004: Approval not found in registry
APPR_E005: Approval revoked
APPR_E006: Approval expired (timestamp check)
APPR_E007: Approval scope mismatch (approval type != required type)
```

**Data Schema**:
```json
{
  "error_category": "APPROVAL_GATE_FAILURE",
  "error_code": "APPR_E001",
  "timestamp": "2026-08-20T12:30:00Z",
  "artifact": "path/to/artifact",
  "approval_id": "APR-20260820-001",
  "message": "Evidence missing: E20260820_XXXXX not found in ledger",
  "severity": "CRITICAL",
  "recovery_action": "ABORT_AND_NOTIFY",
  "event_id": "E20260820_XXXXX"
}
```

---

### Category 2: VALIDATION_GATE_FAILURE

**Description**: Integrity validation or health check detected errors  
**Root Causes**:
- Schema violation detected
- Integrity check failed
- Health check reported error
- Dependency validation failed
- Security scan reported vulnerability

**Severity**: CRITICAL or HIGH (depending on error type)  
**Propagation**: Blocks operations in strict mode; may be overrideable in warning mode

**Error Code Schema**:
```
VALD_E001: Integrity check failed - {reason}
VALD_E002: Health check failed - {component}
VALD_E003: Dependency validation failed - {dependency}
VALD_E004: Schema validation failed - {field}
VALD_E005: Security scan found vulnerability - {severity}
VALD_E006: UTF-8 validation failed
```

**Data Schema**:
```json
{
  "error_category": "VALIDATION_GATE_FAILURE",
  "error_code": "VALD_E001",
  "timestamp": "2026-08-20T12:30:00Z",
  "component": "file_system_integrity",
  "message": "Integrity check failed: File hash mismatch for docs/phase4/DI1_SCOPE_DEFINITION.md",
  "severity": "CRITICAL",
  "recovery_action": "RETRY_AND_VERIFY",
  "event_id": "E20260820_XXXXX"
}
```

---

### Category 3: AUTHORIZATION_GATE_FAILURE

**Description**: Authorization check failed (access not permitted)  
**Root Causes**:
- User not authorized for operation
- Resource access permission denied
- Trust boundary violation attempted
- Authorization rule not satisfied

**Severity**: HIGH  
**Propagation**: Blocks operation; logs security incident

**Error Code Schema**:
```
AUTH_E001: User not authorized for operation - {operation}
AUTH_E002: Resource access denied - {resource}
AUTH_E003: Trust boundary violation
AUTH_E004: Authorization rule not satisfied - {rule}
AUTH_E005: Missing required role
```

**Data Schema**:
```json
{
  "error_category": "AUTHORIZATION_GATE_FAILURE",
  "error_code": "AUTH_E001",
  "timestamp": "2026-08-20T12:30:00Z",
  "user": "unknown_user",
  "operation": "write_core_system_file",
  "resource": "mocka_mcp_server.py",
  "message": "Authorization denied: User role insufficient for core system modification",
  "severity": "HIGH",
  "recovery_action": "ABORT_AND_NOTIFY_SECURITY",
  "event_id": "E20260820_XXXXX"
}
```

---

### Category 4: TOOL_AVAILABILITY_FAILURE

**Description**: Required tool is not available in session (MCP drift, tool not installed, etc.)  
**Root Causes**:
- MCP tool list is stale (schema hash changed)
- Tool was removed from session
- Tool not installed in environment
- Tool server is down

**Severity**: MEDIUM or HIGH (depending on tool criticality)  
**Propagation**: Blocks operation; triggers refresh attempt

**Error Code Schema**:
```
TOOL_E001: Tool not found in MCP registry - {tool_name}
TOOL_E002: Tool schema is stale (hash mismatch)
TOOL_E003: Tool server unreachable
TOOL_E004: Tool timeout (no response)
TOOL_E005: Tool returned unexpected error - {error}
```

**Data Schema**:
```json
{
  "error_category": "TOOL_AVAILABILITY_FAILURE",
  "error_code": "TOOL_E001",
  "timestamp": "2026-08-20T12:30:00Z",
  "tool_name": "mocka_decision_write",
  "tool_type": "mcp",
  "message": "Tool mocka_decision_write not found in MCP session registry",
  "severity": "HIGH",
  "recovery_action": "REFRESH_TOOL_REGISTRY_AND_RETRY",
  "event_id": "E20260820_XXXXX",
  "schema_hash_current": "a1b2c3d4",
  "schema_hash_expected": "x9y8z7w6"
}
```

---

### Category 5: FILE_OPERATION_FAILURE

**Description**: File write/read operation failed or produced unexpected state  
**Root Causes**:
- Encoding error (CP932 contamination, BOM presence)
- File permission denied
- Disk space exhausted
- File is locked by another process
- Write succeeded but read-back verification failed

**Severity**: CRITICAL  
**Propagation**: Blocks operation; triggers rollback if possible

**Error Code Schema**:
```
FILE_E001: File permission denied - {path}
FILE_E002: Encoding error detected - {encoding}
FILE_E003: Disk space exhausted
FILE_E004: File is locked by another process - {path}
FILE_E005: Write succeeded but verification failed - hash mismatch
FILE_E006: File partially written (truncated)
```

**Data Schema**:
```json
{
  "error_category": "FILE_OPERATION_FAILURE",
  "error_code": "FILE_E002",
  "timestamp": "2026-08-20T12:30:00Z",
  "file_path": "docs/phase4/DI1_SCOPE_DEFINITION.md",
  "operation": "write",
  "message": "Encoding error: Non-UTF-8 character detected (CP932 contamination)",
  "severity": "CRITICAL",
  "recovery_action": "ABORT_AND_FIX_ENCODING",
  "event_id": "E20260820_XXXXX",
  "detected_bytes": "0xA4 0xB3 (CP932 'shi')"
}
```

---

### Category 6: GIT_OPERATION_FAILURE

**Description**: Git operation failed or returned unhandled error  
**Root Causes**:
- Merge conflict not resolved
- Rebase failed
- Push to remote failed (network/permission)
- Branch operation failed
- Commit failed (pre-commit hook)

**Severity**: HIGH  
**Propagation**: Blocks git-dependent operations; may require manual resolution

**Error Code Schema**:
```
GIT_E001: Merge conflict - {files}
GIT_E002: Rebase failed - {reason}
GIT_E003: Push failed - {reason}
GIT_E004: Branch operation failed - {operation}
GIT_E005: Commit failed - {reason} (hook?)
GIT_E006: Repository state corrupted
```

**Data Schema**:
```json
{
  "error_category": "GIT_OPERATION_FAILURE",
  "error_code": "GIT_E001",
  "timestamp": "2026-08-20T12:30:00Z",
  "operation": "merge",
  "branch_from": "main",
  "branch_to": "claude/phase4-controlled-development-xwzju9",
  "message": "Merge conflict in docs/phase4/DI1_SCOPE_DEFINITION.md (3 conflicts)",
  "severity": "HIGH",
  "recovery_action": "ABORT_AND_REQUIRE_MANUAL_RESOLUTION",
  "event_id": "E20260820_XXXXX",
  "conflicting_files": ["docs/phase4/DI1_SCOPE_DEFINITION.md"]
}
```

---

## 2. Error State Transition Diagram

```
Initial State: Operation Requested

     ↓
┌─────────────────────┐
│ Execution Starts    │
└─────────────────────┘
     ↓
┌─────────────────────┐
│ Gate 1 Executes     │
│ (Approval Gate)     │
└─────────────────────┘
     ↓
  Gate 1 Passes? ──── YES ──→ Gate 2 Executes
     │                           ↓
     │                       (similar check)
     │
  NO ↓
┌──────────────────────────────┐
│ Error Detected               │
│ Category: APPROVAL_GATE_...  │
│ Severity: CRITICAL           │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│ Log Error Event              │
│ Record in Event Ledger       │
│ Event Type: GATE_FAILURE     │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│ Determine Recovery Action    │
│ (from error_code mapping)    │
└──────────────────────────────┘
     ↓
  Recovery Action?
  ├─ ABORT_AND_NOTIFY
  ├─ RETRY_AND_VERIFY
  ├─ FALLBACK_MODE
  └─ MANUAL_REVIEW_REQUIRED


ABORT_AND_NOTIFY path:
     ↓
┌──────────────────────────────┐
│ Operation Aborted            │
│ Status: FAILED               │
│ Reason: Gate failure         │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│ Notify Stakeholders          │
│ (Event Ledger, log file)     │
└──────────────────────────────┘
     ↓
┌──────────────────────────────┐
│ Remediation Steps Provided   │
│ (What operator should do)    │
└──────────────────────────────┘
     ↓
Final State: OPERATION_FAILED_GATES_BLOCKED


RETRY_AND_VERIFY path:
     ↓
┌──────────────────────────────┐
│ Retry Count = 0              │
│ Max Retries = 3              │
└──────────────────────────────┘
     ↓
  While Retry Count < Max:
     ├─ Increment Retry Count
     ├─ Wait exponential backoff (2^count seconds)
     ├─ Refresh state (cache, tool list, etc.)
     ├─ Re-execute Gate
     ├─ If Success: Continue to next gate
     └─ If Failure: Log retry failure, loop
        ↓
     If Max Retries Exceeded:
     ├─ Log final failure
     └─ Execute ABORT_AND_NOTIFY
```

---

## 3. Error Reporting Requirements

### Event Ledger Recording

Every gate failure SHALL generate an Event Ledger entry:

```python
event = {
  "event_id": "E20260820_XXXXX",  # Auto-generated
  "timestamp": "2026-08-20T12:30:00Z",
  "type": "GATE_FAILURE",
  "gate_category": "APPROVAL_GATE_FAILURE",
  "error_code": "APPR_E001",
  "severity": "CRITICAL",
  "artifact": "path/to/artifact",
  "message": "Evidence missing: E20260820_XXXXX not found",
  "recovery_action": "ABORT_AND_NOTIFY",
  "tags": ["gate_failure", "approval", "phase4"]
}
```

### Operator Notification

Gate failures of severity CRITICAL or HIGH SHALL trigger notification:

**Notification Channel**:
- Event Ledger (immediate)
- Event Log file (`data/events.log`)
- COMMAND CENTER dashboard (if available)
- Email alert (if severity CRITICAL)

**Notification Content**:
```
From: MoCKA Governance System
Subject: GATE FAILURE - Phase 4 Operation Blocked

Severity: CRITICAL
Gate: Approval Gate
Error: Evidence missing for artifact

Artifact: docs/phase4/DI1_SCOPE_DEFINITION.md
Approval ID: APR-20260820-001
Missing Evidence: E20260820_XXXXX

Remediation Steps:
1. Verify artifact has been approved
2. Check Approval Registry for approval ID
3. Locate missing evidence item
4. Retry operation

Event ID for reference: E20260820_XXXXX
```

### Decision Ledger Recording

If operation involves decision, gate failure SHALL update Decision Ledger:

```json
{
  "decision_id": "DC_20260820_001",
  "status": "BLOCKED_BY_GATE_FAILURE",
  "gate_failure_event": "E20260820_XXXXX",
  "gate_error_code": "APPR_E001",
  "attempted_at": "2026-08-20T12:30:00Z",
  "blocked_at": "2026-08-20T12:30:05Z",
  "remediation_required": true
}
```

---

## 4. Evidence Requirements for Error Handling

### What Constitutes Evidence of Gate Failure

1. **Approval Gate Failure Evidence**:
   - Approval Registry lookup result (approval not found)
   - Evidence item hash verification result
   - Contradictory evidence items with timestamps
   - Decision Ledger entry showing approval revocation

2. **Validation Gate Failure Evidence**:
   - Validation check output log
   - Schema violation details
   - Dependency graph showing broken link
   - Security scan report

3. **Authorization Gate Failure Evidence**:
   - Authorization rule file
   - User/role permission matrix
   - Requested operation details
   - Trust boundary definition

4. **Tool Availability Failure Evidence**:
   - Tool schema hash comparison (current vs expected)
   - Tool registry dump at time of failure
   - Tool server health check result
   - Session MCP connection log

5. **File Operation Failure Evidence**:
   - File encoding analysis report
   - Disk space check result
   - File permission matrix
   - Read-back hash comparison

6. **Git Operation Failure Evidence**:
   - Git error message/exit code
   - Merge conflict file content
   - Pre-commit hook output
   - Repository status at time of failure

### Evidence Preservation

All evidence SHALL be preserved:
- Stored in `data/evidence/gate_failures/{date}/`
- Indexed in `data/evidence/gate_failure_index.jsonl`
- Retained for minimum 90 days
- Never deleted without explicit approval

---

## 5. Recovery Flow (Decision Tree)

```
Gate Failure Detected
    ↓
Classify Error Category
    ↓
Lookup Error Code → Recovery Action Mapping
    ↓
┌─────────────────────────────────────────────────────┐
│ Recovery Action Decision Tree                       │
└─────────────────────────────────────────────────────┘

Is it APPROVAL_GATE_FAILURE?
├─ YES: Can evidence be obtained?
│   ├─ YES: RETRY_AND_VERIFY
│   │   Action: Request evidence from upstream, retry
│   │   Timeout: 5 minutes (then escalate to MANUAL_REVIEW)
│   └─ NO: ABORT_AND_NOTIFY
│       Action: Abort operation, notify operator with required evidence
│
├─ Is it VALIDATION_GATE_FAILURE?
│   ├─ YES: Is it recoverable?
│   │   ├─ YES (e.g., encoding): FIX_AND_RETRY
│   │   │   Action: Fix issue, retry operation
│   │   │   Timeout: 2 retries (then abort)
│   │   └─ NO (e.g., data corruption): ABORT_AND_ESCALATE
│   │       Action: Abort, log incident, escalate to operators
│   └─
│
├─ Is it AUTHORIZATION_GATE_FAILURE?
│   ├─ YES: ABORT_AND_NOTIFY_SECURITY
│   │   Action: Abort immediately, log security event, no retry
│   └─
│
├─ Is it TOOL_AVAILABILITY_FAILURE?
│   ├─ YES: Is tool critical?
│   │   ├─ YES (e.g., mocka_decision_write): 
│   │   │   ├─ REFRESH_TOOL_REGISTRY_AND_RETRY
│   │   │   │   Action: Refresh schema hash, reload tools, retry (max 2)
│   │   │   └─ If still unavailable: ABORT_AND_ESCALATE
│   │   │
│   │   └─ NO (optional tool): FALLBACK_OR_SKIP
│   │       Action: Use fallback if available, else skip
│   └─
│
├─ Is it FILE_OPERATION_FAILURE?
│   ├─ YES: What failed?
│   │   ├─ Encoding error: FIX_ENCODING_AND_RETRY
│   │   ├─ Permission denied: ABORT_AND_ESCALATE
│   │   ├─ Disk full: ABORT_AND_ESCALATE
│   │   └─ Verification failed: RETRY_WITH_ROLLBACK
│   └─
│
└─ Is it GIT_OPERATION_FAILURE?
    ├─ YES: What failed?
    │   ├─ Merge conflict: ABORT_AND_REQUIRE_MANUAL
    │   ├─ Push failed: RETRY_WITH_EXPONENTIAL_BACKOFF
    │   └─ Hook failed: ABORT_AND_ESCALATE
    └─

Final Actions:
- Log outcome (success of recovery, or final failure)
- Update Decision Ledger if applicable
- Notify stakeholders if escalated
- Archive evidence for audit
```

---

## 6. Local Test Requirements

### Test Scenario 1: Approval Gate Failure Detection

**Setup**:
- Create artifact with approval requirement
- Don't provide required approval

**Execution**:
1. Attempt to publish artifact
2. Gate checks for approval
3. Approval not found in registry

**Expected Result**:
- [ ] APPR_E004 error generated
- [ ] Event Ledger records GATE_FAILURE
- [ ] Operation aborted
- [ ] Operator notified with remediation steps

**Verification**:
- Event Ledger contains `"gate_category": "APPROVAL_GATE_FAILURE"`
- Error code is "APPR_E004"
- Recovery action is "ABORT_AND_NOTIFY"

---

### Test Scenario 2: Validation Gate Retry Success

**Setup**:
- Create file with temporary encoding error
- Configure retry mechanism (max 3 retries)

**Execution**:
1. Write file (encoding error on first attempt)
2. Gate detects encoding error
3. Auto-fix encoding
4. Retry (2nd attempt succeeds)

**Expected Result**:
- [ ] VALD_E006 error on first attempt
- [ ] Recovery action: RETRY_AND_VERIFY
- [ ] Auto-fix applied
- [ ] Retry succeeds
- [ ] Operation continues

**Verification**:
- Event Ledger shows 2 attempts (first failed, second succeeded)
- Auto-fix evidence captured
- Overall operation status is SUCCESSFUL

---

### Test Scenario 3: Tool Availability Gate with Schema Drift

**Setup**:
- Simulate MCP tool becoming unavailable
- Simulate schema hash change

**Execution**:
1. Attempt to call mocka_decision_write
2. Tool not in session registry
3. Detect schema hash mismatch
4. Refresh tool registry
5. Retry operation

**Expected Result**:
- [ ] TOOL_E001 error on first attempt
- [ ] Schema hash comparison detects drift
- [ ] Tool registry refreshed
- [ ] Retry succeeds
- [ ] Operation continues

**Verification**:
- Event Ledger shows drift detection
- Schema hash was updated
- Tool became available after refresh

---

### Test Scenario 4: Authorization Gate Failure (No Retry)

**Setup**:
- Create operation requiring authorization
- User has insufficient permissions

**Execution**:
1. Attempt operation
2. Authorization gate checks permissions
3. User not authorized

**Expected Result**:
- [ ] AUTH_E001 error generated
- [ ] Recovery action: ABORT_AND_NOTIFY_SECURITY
- [ ] NO retry attempt (authorization failures don't retry)
- [ ] Operation aborted immediately
- [ ] Security event logged

**Verification**:
- Event Ledger contains security-relevant metadata
- No retry attempts in logs
- Operation status is FAILED

---

### Test Scenario 5: File Operation Rollback

**Setup**:
- Create file write that partially succeeds
- Verification detects corruption

**Execution**:
1. Write file
2. Read-back verification fails (hash mismatch)
3. Rollback recovery triggered

**Expected Result**:
- [ ] FILE_E005 error detected
- [ ] Recovery action: ABORT_AND_FIX_ENCODING
- [ ] File rolled back to previous version
- [ ] Operator notified
- [ ] Evidence captured (both corrupted and corrected versions)

**Verification**:
- Event Ledger shows rollback action
- File hash matches expected value after recovery
- Both versions preserved in audit trail

---

### Test Scenario 6: Git Operation Merge Conflict

**Setup**:
- Create branch with conflicting changes
- Attempt to merge to main

**Execution**:
1. Attempt merge
2. Merge conflict detected
3. Gate aborts operation

**Expected Result**:
- [ ] GIT_E001 error generated
- [ ] Recovery action: ABORT_AND_REQUIRE_MANUAL
- [ ] Repository left in safe state (merge not completed)
- [ ] Conflicting files identified
- [ ] Operator notified with conflict details

**Verification**:
- Event Ledger shows merge conflict
- Conflicting files listed
- Repository is clean (no partial merge state)

---

## 7. Implementation Notes

### Design Assumptions

- All gate failures are logged to Event Ledger immediately
- Recovery actions are attempted automatically only for transient failures
- Authorization/approval failures never retry (security-sensitive)
- Operator is always notified of critical failures

### Dependencies

- Event Ledger must be writable at time of gate failure
- Error codes must be universally unique (no duplicates across categories)
- Recovery action mappings must be maintained in configuration

### Integration Points

- Approval Gate (DI1) feeds into error categorization
- Decision Ledger is updated with gate failure status
- Event Ledger is primary audit trail for all failures

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Draft | Claude (Phase 4 Execution) | Initial error model specification |

