# DI2: GATE Silent Failure Handling - Scope Definition

**Document ID**: DI2_SCOPE_20260820  
**Phase**: Phase 4 Controlled Development  
**Status**: Draft  
**Created**: 2026-08-20  
**Authority**: Human Gate Final Decision 2026-08-20  

---

## 1. Problem Definition

### The Silent Failure Problem

A "silent failure" occurs when a critical governance gate (approval, validation, authorization) FAILS but the failure is not communicated to dependent systems or stakeholders. The dependent system then proceeds as if the gate PASSED, creating a state mismatch:

**Reality**: Gate failed (e.g., approval was rejected, validation produced errors)  
**Perceived**: Gate passed (approval accepted, validation succeeded)

This gap creates integrity risks, especially in cascading decision chains where one gate failure should block downstream decisions.

### Historical Examples from MoCKA

1. **E20260621_378795484b70f (Extension Canonical Paths)**
   - File was changed in wrong location
   - Change made without referencing MOCKA_OVERVIEW.json extension_canonical_paths
   - Decision made without realizing the change was to a non-canonical path
   - Result: Change was not reflected in production (silent failure of change propagation)

2. **E20260705_732301073f4bd (MCP Tool Registry Drift)**
   - mocka_decision_write tool was requested
   - Tool was not present in MCP session (capability drift)
   - Tool call returned error
   - But the error was not properly handled - Decision Ledger might have received partial data
   - Result: Uncertain whether decision was actually recorded

3. **TODO_382 (Git Rebase Safety)**
   - User executed git rebase on working directory with uncommitted changes
   - Pre-rebase hook failed to block because state was unexpected
   - Changes were silently lost in rebase conflict resolution
   - Result: Verified changes disappeared without warning

4. **IC_20260705_018 (MCP Schema Hash Drift)**
   - Server schema was updated
   - Session did not update its tool registry
   - Session continued using stale tool list
   - Result: New tools were not available; old tools caused unexpected behavior

### Common Pattern

All these share the pattern:
- **Gate Executed**: Some validation/check/gate ran
- **Gate Failed**: Gate returned error or negative result
- **Error Not Propagated**: Error was not surfaced to decision-makers
- **Decision Proceeded**: Dependent system assumed gate passed and continued
- **Harm**: Integrity was compromised downstream

---

## 2. Current State

### Gates in MoCKA System

**Decision Gate** (`Decision Ledger`)
- Issues: None currently documented
- Assumption: Always succeeds

**Approval Gate** (related to DI1)
- Issues: May fail but not communicate failure (silent_failure_handling not yet implemented)
- Assumption: approved_by field is present and valid

**Validation Gate** (`integrity_check`, `health_check`)
- Issues: May detect errors but not block operations
- Assumption: Validation results are always reviewed before proceeding

**Authorization Gate** (TODO_325: PHI-OS Trust Boundary)
- Issues: Access control not yet formalized
- Assumption: Windows ACL is sufficient (TBD)

**File Operation Gate** (Write/Edit tools)
- Issues: File operations may fail silently if encoding issues occur (CP932 risks, despite TODO_333)
- Assumption: Write operations always succeed if no exception is raised

**Git Operation Gate** (git commands in runtime)
- Issues: May return error codes that are not checked (see TODO_382)
- Assumption: Git operations always succeed

**MCP Tool Availability Gate** (IC_20260705_018)
- Issues: Tool may be unavailable but session doesn't detect this
- Assumption: Tool list is always current

### Current Failure Handling

- **No standardized mechanism** for detecting silent failures
- **Ad-hoc detection** through post-operation audits (not real-time)
- **No recovery automatic** - requires manual intervention and investigation

---

## 3. Target State

### Integrated Silent Failure Detection System

**Core Principle**: Every gate execution SHALL produce an explicit result (PASS/FAIL with evidence), and this result SHALL propagate to all downstream decision points.

**Goals**:

1. **Explicit Gate Status**
   - Each gate execution records pass/fail status in Event Ledger
   - No operation is considered "passed" if its gate returned failure
   - Failure status blocks dependent operations

2. **Propagation Chain**
   - If Gate A fails, Gate B (which depends on A) is NOT executed
   - If Gate B would execute anyway, this is logged as an integrity violation
   - Operators are notified immediately of blocked chains

3. **Recovery Options**
   - For recoverable failures: Automatic recovery action (retry, fallback)
   - For unrecoverable failures: Clear notification and manual intervention
   - Recovery is NOT silent - recovery actions are logged as events

4. **Audit Trail**
   - Every gate execution is recorded
   - Every propagation decision is recorded
   - Every recovery action is recorded
   - Failure history is preserved (not deleted after recovery)

5. **Operator Visibility**
   - Dashboard/alert mechanism shows blocked chains in real-time
   - Operators can drill into failure details
   - Recovery status is transparent

---

## 4. Failure Scenario Classification

### Scenario A: Approval Gate Fails Silently

**Trigger**: `approved_by` validation fails (from DI1) but operation continues  
**Root Cause Examples**:
- Approval evidence is missing, approval rejected, but artifact is still published
- Approval is revoked (from Approval Registry) but cached approval status is not refreshed
- Decision Ledger entry references invalid approval ID but operation continues

**Impact**: Published artifacts lack required approval, trust boundary broken  
**Detection Method**: Verify approval against Approval Registry before publishing

---

### Scenario B: Validation Error Not Surfaced

**Trigger**: Health check or integrity validation detects error but doesn't stop operation  
**Root Cause Examples**:
- Validation runs as background process; error is logged but not communicated to operator
- Multiple validators run in parallel; one fails but overall operation completes
- Validation error is suppressed because it's classified as "warning" not "error"

**Impact**: System operates in degraded/inconsistent state  
**Detection Method**: Central validation result aggregation; operation blocked until all validators pass

---

### Scenario C: Authorization Gate Not Enforced

**Trigger**: Operation requires authorization but proceeds without it  
**Root Cause Examples**:
- Authorization check exists but returns boolean; caller doesn't check return value
- Authorization check is skipped in error path (e.g., cleanup code bypasses auth)
- Authorization rule is defined but not implemented in actual code path

**Impact**: Unauthorized operations execute; audit trail lacks context  
**Detection Method**: Wrapping authorization calls in transaction that blocks operation on failure

---

### Scenario D: Tool Availability Gate Fails

**Trigger**: Tool is not available but code assumes it is (e.g., MCP tool drift)  
**Root Cause Examples**:
- MCP tool list is cached and not refreshed when server updates
- Tool gracefully degrades (returns default) instead of failing
- Tool is not installed in current session environment

**Impact**: Operations silently use stale data or default behavior  
**Detection Method**: Tool availability check before each use; explicit failure if tool not available

---

### Scenario E: File Operation Fails Silently

**Trigger**: File write operation fails due to encoding/permission/disk space  
**Root Cause Examples**:
- Exception is caught and silently logged instead of re-raised
- Write operation succeeds partially (truncated file written)
- File system quota exceeded but operation reports success

**Impact**: Data loss, corruption, or inconsistent state  
**Detection Method**: Hash verification after write; read-back comparison

---

### Scenario F: Git Operation Fails Silently

**Trigger**: Git operation returns error code but is not checked  
**Root Cause Examples**:
- Script calls `git rebase` without checking exit code
- Git merge conflict is left unresolved but script continues
- Branch is not pushed (network error) but script assumes it is pushed

**Impact**: Repository state diverges from assumed state  
**Detection Method**: Explicit verification after each git operation (git rev-parse, git status)

---

## 5. Detection Boundary

### What We Will Detect

1. **Explicit Gate Failures**: When a gate function returns FAIL status
2. **Propagation Violations**: When operation proceeds despite upstream gate failure
3. **Tool Unavailability**: When requested tool is not available in session
4. **State Mismatches**: When assumed state differs from actual state (hash comparison, file verification)
5. **Authorization Bypasses**: When authorized operation tries to access protected resource

### What We Will NOT Detect (Out of Scope)

1. **Logic Errors in Gates**: If a gate has a bug that causes incorrect PASS verdict (gate logic validation is separate)
2. **Malicious Approvals**: If authorizer intentionally approves something they shouldn't (policy enforcement, not technical)
3. **Network Timing Issues**: Transient network glitches that momentarily make tool unavailable (retry/retry_logic)
4. **Legacy Code Paths**: Paths that predate silent failure handling (only new/modified paths covered)

---

## 6. Recovery Boundary

### Recovery Actions Implemented

1. **Retry with Exponential Backoff**
   - For transient failures (tool unavailable, network timeout)
   - Max 3 retries with delays: 1s, 2s, 4s
   - Log each retry; stop if max retries exceeded

2. **Fallback Mode**
   - If primary gate unavailable, use fallback (e.g., local validation instead of remote)
   - Log fallback activation
   - Require explicit approval before using fallback

3. **Abort and Notify**
   - If gate failure is unrecoverable (e.g., missing required approval)
   - Abort operation
   - Notify operator with specific failure reason
   - Provide remediation steps

4. **Cache Refresh**
   - If tool list or configuration is stale (MCP drift)
   - Force refresh from source (mcp_schema_hash.json)
   - Retry operation with fresh state

### Recovery Actions NOT Implemented (Manual Only)

1. **Automatic Rollback**: If operation partially completes before gate failure detected
   - Manual rollback required; operator reviews before proceeding
2. **Policy Override**: If gate fails due to policy (approval missing)
   - Human Gate must explicitly override
3. **Data Repair**: If silent failure leaves corrupted data
   - Manual audit and repair required

---

## 7. Non-Goals

- **Not changing gate logic itself**: Silent failure handling wraps gates, doesn't change their decision criteria
- **Not implementing new gates**: Only affects existing gates in scope
- **Not changing authorization policy**: Authorization rules remain unchanged; only enforcement mechanism is improved
- **Not retroactive detection**: Only detects failures in new/modified code paths
- **Not real-time alerting UI**: Alert mechanism is event-based, not live dashboard (live dashboard is future work)

---

## 8. Acceptance Criteria

The Scope Definition SHALL be accepted when:

- [ ] All failure scenarios are clearly enumerated and stakeholders agree
- [ ] Detection boundary is unambiguous (what will/won't be detected)
- [ ] Recovery boundary is clear (what will/won't be automatically recovered)
- [ ] Non-goals are confirmed
- [ ] Interfaces to DI1 (Approval Gate) and DI3 (Architecture Evaluation) are documented
- [ ] No contradictions with existing CONSTITUTION or INSTITUTION architecture

### Success Metrics for Implementation Phase

- [ ] All identified failure scenarios have detection mechanisms
- [ ] Recovery logic is tested for each scenario
- [ ] Zero unhandled exceptions in critical paths (all exceptions have handlers)
- [ ] Event Ledger shows 100% of gate executions and failures logged
- [ ] Operator can trace any integrity violation back to root cause

---

## 9. Next Steps

Once this Scope Definition is approved:

1. **DI2 Error Model Specification Draft** will detail:
   - Error category taxonomy
   - State transition diagram for each error type
   - Reporting and logging requirements
   - Recovery flow (decision tree for which recovery action applies)
   - Local test scenarios

2. **Failure Scenario Test Plan** will verify:
   - Each failure scenario can be artificially triggered
   - Detection catches the failure in real-time
   - Recovery action is appropriate
   - Operation is safe after recovery

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Draft | Claude (Phase 4 Execution) | Initial scope definition |

