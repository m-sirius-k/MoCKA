# HG API Failure Semantics Design Specification v0.1

**Phase**: Remediation Design Specification (Post-Investigation)
**Date**: 2026-09-11
**Purpose**: Design complete API contract for mocka_decision_write including all failure paths
**System State**: HOLD / FAIL-CLOSED (maintained)

---

## Overview

This specification defines:
- Complete API contract for mocka_decision_write
- All failure paths and error conditions
- Caller-facing error semantics
- Retry behavior and backoff strategy
- Recovery and escalation procedures
- Monitoring and alerting requirements

**NOT**: Implementation code, runtime modifications, production deployment

---

## Part 1: HG API Complete Request-Response Contract

### API Endpoint: mocka_decision_write

**HTTP Method**: POST  
**Endpoint Path**: /mcp/execute  
**MCP Tool Name**: mocka_decision_write

### Request Schema

```json
{
  "tool_name": "mocka_decision_write",
  "arguments": {
    "title": "string (required, max 256)",
    "description": "string (required, max 4096)",
    "decision": "string (required, selected from alternatives)",
    "rationale": "string (required, max 2048)",
    "impact": "string (required, max 2048)",
    "approved_by": "string (required, authority name)",
    "alternatives": [
      "string (required, min 1 entry)",
      "string",
      "..."
    ],
    "evidence_location": "string (optional, URL or path)",
    "scope": "string (optional, scope of decision)",
    "priority": "string (optional, CRITICAL / HIGH / MEDIUM / LOW)"
  }
}
```

**Validation Rules**:
- title: required, non-empty, max 256 characters
- description: required, non-empty, max 4096 characters
- decision: required, must match one value in alternatives array
- rationale: required, non-empty, max 2048 characters (explain WHY this decision)
- impact: required, non-empty, max 2048 characters (what changes as result)
- approved_by: required, non-empty (authority who made decision)
- alternatives: required, array with min 1 entry (decision path taken, why others rejected)

### Response Schema (All Cases)

```json
{
  "status": "enum (ok | fail_closed | validation_error | duplicate | unknown_error)",
  "decision_id": "string or null",
  "event_id": "string or null",
  "error": "string or null",
  "error_code": "enum or null",
  "message": "string or null",
  "when": "ISO 8601 timestamp",
  "retry_after_seconds": "integer or null (only for retryable errors)"
}
```

---

## Part 2: Success Path

### Scenario: Request Valid, Decision Accepted, Event Created

**Precondition**:
- Request passes validation
- Decision Ledger write succeeds
- GATE event creation succeeds on first try

**HTTP Status**: 201 Created

**Response**:
```json
{
  "status": "ok",
  "decision_id": "DC_20260911_001",
  "event_id": "E20260911_001",
  "error": null,
  "error_code": null,
  "message": "Decision created and event binding complete",
  "when": "2026-09-11T10:00:21Z",
  "retry_after_seconds": null
}
```

**Side Effects**:
1. Decision Ledger updated: new record appended with decision_id
2. Event Store updated: new event with tag "decision_ledger,DC_20260911_001" created
3. Binding Audit Log updated: binding entry marked COMPLETE
4. audit_trail: entry added to both decision and event records

**Caller Behavior**:
- Can proceed with operations depending on this decision
- Can query decision/event using returned IDs
- Binding guaranteed complete (atomic semantics)

---

## Part 3: Input Validation Failure Paths

### Scenario 1: Missing Required Field

**Precondition**:
- Request omits required field (title, description, decision, rationale, impact, approved_by, alternatives)

**HTTP Status**: 400 Bad Request

**Response**:
```json
{
  "status": "validation_error",
  "decision_id": null,
  "event_id": null,
  "error": "missing_required_field",
  "error_code": "VALIDATION_001",
  "message": "Required field missing: 'context' (field_name varies)",
  "when": "2026-09-11T10:00:01Z",
  "retry_after_seconds": null
}
```

**Side Effects**:
- No Decision Ledger entry created
- No Event created
- No audit trail entry (pre-validation failure)

**Caller Behavior**:
- Fix validation error (add required field)
- Retry with valid input
- No state change occurred

**Automatic Retry**: NO (validation errors are not retryable)

---

### Scenario 2: Invalid Field Format

**Precondition**:
- Request contains field with invalid format/type
- Example: title exceeds max length, alternatives array is empty, etc.

**HTTP Status**: 400 Bad Request

**Response**:
```json
{
  "status": "validation_error",
  "decision_id": null,
  "event_id": null,
  "error": "invalid_field_value",
  "error_code": "VALIDATION_002",
  "message": "Field 'title' exceeds maximum length (256 chars). Provided: 512 chars.",
  "when": "2026-09-11T10:00:01Z",
  "retry_after_seconds": null
}
```

**Side Effects**:
- No Decision Ledger entry created
- No Event created

**Caller Behavior**:
- Correct field format
- Retry with valid input

**Automatic Retry**: NO

---

### Scenario 3: Invalid Decision Value

**Precondition**:
- 'decision' field value does not appear in alternatives array

**HTTP Status**: 400 Bad Request

**Response**:
```json
{
  "status": "validation_error",
  "decision_id": null,
  "event_id": null,
  "error": "invalid_decision_choice",
  "error_code": "VALIDATION_003",
  "message": "Decision 'Option C' not found in alternatives array. Available: ['Option A', 'Option B']",
  "when": "2026-09-11T10:00:01Z",
  "retry_after_seconds": null
}
```

**Side Effects**:
- No Decision Ledger entry created
- No Event created

**Caller Behavior**:
- Select valid decision from alternatives
- Retry request

**Automatic Retry**: NO

---

## Part 4: Transient Failure Paths (Retryable)

### Scenario A: GATE Timeout (5 Second)

**Precondition**:
- Request passes validation
- Decision Ledger write succeeds
- GATE request times out (request hangs > 5 seconds)
- Exception type: requests.Timeout or socket.timeout

**HTTP Status**: 500 Internal Server Error

**First Response** (Attempt 1):
```json
{
  "status": "fail_closed",
  "decision_id": null,
  "event_id": null,
  "error": "event_creation_timeout_retrying",
  "error_code": "TRANSIENT_001_RETRY",
  "message": "GATE event creation timed out. Automatic retry in progress (attempt 1/3). Do not retry manually.",
  "when": "2026-09-11T10:00:05Z",
  "retry_after_seconds": 2
}
```

**Behavior**:
- Decision Ledger entry written: TENTATIVE (marked for potential rollback)
- GATE request timed out
- Automatic retry scheduled after 2 seconds
- Caller receives response immediately (async retry)
- Caller should NOT retry manually

**Automatic Retry Logic**:
```
Attempt 1: wait 2 seconds → retry POST to GATE
  ├─ Success (201): → proceed to final response "ok"
  ├─ Timeout: → Attempt 2
  └─ Other error: → Attempt 2

Attempt 2: wait 4 seconds → retry POST to GATE
  ├─ Success (201): → proceed to final response "ok"
  ├─ Timeout: → Attempt 3
  └─ Other error: → Attempt 3

Attempt 3: wait 8 seconds → retry POST to GATE
  ├─ Success (201): → proceed to final response "ok"
  ├─ Timeout: → all retries exhausted
  └─ Other error: → all retries exhausted
```

**On Retry Success** (after attempt N):
```json
{
  "status": "ok",
  "decision_id": "DC_20260911_001",
  "event_id": "E20260911_001",
  "error": null,
  "error_code": null,
  "message": "Decision created after 2 retry attempts",
  "when": "2026-09-11T10:00:12Z",
  "retry_after_seconds": null
}
```

**On All Retries Exhausted** (after Attempt 3 timeout):
```json
{
  "status": "fail_closed",
  "decision_id": null,
  "event_id": null,
  "error": "event_creation_timeout_exhausted",
  "error_code": "TRANSIENT_001_EXHAUSTED",
  "message": "GATE event creation failed after 3 retry attempts (timeouts at 2s, 4s, 8s). Decision rolled back. Please retry the entire request.",
  "when": "2026-09-11T10:00:14Z",
  "retry_after_seconds": null
}
```

**Side Effects on Exhaustion**:
1. Decision Ledger: ROLLBACK entry removed (transaction aborted)
2. Event Store: no event created (binding incomplete by design)
3. Audit Trail: entry recorded "TIMEOUT_EXHAUSTED, decision rolled back"
4. Incident Log: incident created with timestamp, decision_id, error details

**Caller Behavior on Exhaustion**:
- Address root cause (is GATE available? network issues?)
- Retry entire request (new decision_id will be generated)
- System state returns to pre-request (fail-closed)

**Key Property**: Caller does NOT distinguish between "success" and "partial success" - either atomic success or complete rollback.

---

### Scenario B: GATE Server Error (Non-Timeout)

**Precondition**:
- Request passes validation
- Decision Ledger write succeeds
- GATE returns HTTP 4XX or 5XX (not timeout)
- Examples: 500 Internal Server Error, 503 Service Unavailable, 400 Bad Request, etc.

**HTTP Status**: 500 Internal Server Error (from mocka_decision_write perspective)

**Response** (Attempt 1):
```json
{
  "status": "fail_closed",
  "decision_id": null,
  "event_id": null,
  "error": "gate_error_retrying",
  "error_code": "TRANSIENT_002_RETRY",
  "message": "GATE returned error: 503 Service Unavailable. Automatic retry in progress (attempt 1/3).",
  "when": "2026-09-11T10:00:05Z",
  "retry_after_seconds": 2
}
```

**Automatic Retry Logic** (same as Scenario A):
- Attempt 1: 2 second wait
- Attempt 2: 4 second wait
- Attempt 3: 8 second wait

**On Retry Success**:
```json
{
  "status": "ok",
  "decision_id": "DC_20260911_001",
  "event_id": "E20260911_001",
  "error": null,
  "error_code": null,
  "message": "Decision created after 1 retry attempt",
  "when": "2026-09-11T10:00:08Z",
  "retry_after_seconds": null
}
```

**On All Retries Exhausted**:
```json
{
  "status": "fail_closed",
  "decision_id": null,
  "event_id": null,
  "error": "gate_error_exhausted",
  "error_code": "TRANSIENT_002_EXHAUSTED",
  "message": "GATE error persists after 3 retry attempts (500, 503, 503). Decision rolled back.",
  "when": "2026-09-11T10:00:14Z",
  "retry_after_seconds": 60
}
```

**Side Effects on Exhaustion**:
1. Decision Ledger: ROLLBACK (entry removed)
2. Event Store: no event (binding never established)
3. Incident Log: incident created with GATE error details
4. retry_after_seconds: suggests when to retry (60 seconds = allow GATE recovery time)

**Caller Behavior**:
- Wait suggested retry_after_seconds duration
- Retry entire request
- Or manually check GATE status first

---

## Part 5: Permanent Failure Paths

### Scenario C: Decision Ledger Write Failure

**Precondition**:
- Request passes validation
- Attempt to write to Decision Ledger fails
- Reasons: file permissions, disk full, file corruption, etc.

**HTTP Status**: 500 Internal Server Error

**Response**:
```json
{
  "status": "fail_closed",
  "decision_id": null,
  "event_id": null,
  "error": "decision_ledger_write_failed",
  "error_code": "PERMANENT_001",
  "message": "Failed to write decision to ledger: permission denied on decision_ledger.jsonl",
  "when": "2026-09-11T10:00:01Z",
  "retry_after_seconds": null
}
```

**Side Effects**:
- No Decision Ledger entry created
- No Event created (never attempted, fail-closed before GATE)
- Incident Log: CRITICAL incident created
- Alert: immediate alert to system administrator

**Caller Behavior**:
- This is a system-level failure, not caller's fault
- Wait for system administrator to resolve
- Retry later (after system recovery)

**Automatic Retry**: NO (requires manual intervention)

---

### Scenario D: Unknown Internal Error

**Precondition**:
- Unexpected exception occurs in mocka_decision_write
- Not one of the classified scenarios above
- Example: JSON serialization error, unexpected exception type, etc.

**HTTP Status**: 500 Internal Server Error

**Response**:
```json
{
  "status": "unknown_error",
  "decision_id": null,
  "event_id": null,
  "error": "internal_error_unclassified",
  "error_code": "INTERNAL_001",
  "message": "Unexpected error in mocka_decision_write: KeyError on 'decision_id'. Stack trace logged to system logs.",
  "when": "2026-09-11T10:00:01Z",
  "retry_after_seconds": null
}
```

**Side Effects**:
- System state unknown (conservative: assume potential partial write)
- Full exception stack trace logged to system logs
- Incident Log: CRITICAL incident with error details
- Alert: immediate alert to system administrator

**Caller Behavior**:
- Contact system administrator with error details
- Do not retry without confirmation of system state recovery

**Automatic Retry**: NO

---

## Part 6: Duplicate Request Handling

### Scenario E: Duplicate Request Within Deduplication Window

**Precondition**:
- Request 1 successfully created Decision (DC_20260911_001)
- Request 2 (identical) sent within 1 second
- Deduplication mechanism detects duplicate

**Detection Method**:
```
Algorithm:
1. Extract decision signature = SHA-256(title + description + decision + approved_by)
2. Search Decision Ledger for entry with same signature within 1 second window
3. If found: flag as DUPLICATE
4. If not found: proceed as normal request
```

**HTTP Status**: 200 OK (successful response, but duplicate detection)

**Response** (if duplicate rejection selected):
```json
{
  "status": "duplicate",
  "decision_id": "DC_20260911_001",
  "event_id": "E20260911_001",
  "error": null,
  "error_code": null,
  "message": "Duplicate request detected. Returning result of original request (2.3 seconds ago).",
  "when": "2026-09-11T10:00:03Z",
  "retry_after_seconds": null
}
```

**Response** (if idempotent behavior selected):
```json
{
  "status": "ok",
  "decision_id": "DC_20260911_001",
  "event_id": "E20260911_001",
  "error": null,
  "error_code": null,
  "message": "Request processed (idempotent - duplicate request returned same result)",
  "when": "2026-09-11T10:00:03Z",
  "retry_after_seconds": null
}
```

**Side Effects**:
- No second Decision Ledger entry created (single decision, single event)
- No second Event created
- Audit Trail: entry noting duplicate detection
- Duplicate registry: recorded for audit

**Caller Behavior**:
- Can use returned decision_id and event_id
- Binding is complete (from original request)
- Idempotent behavior ensures safety

---

## Part 7: Monitoring and Alerting Requirements

### Metrics to Track

**Per-Request Metrics**:
- Request timestamp
- Request processing time (latency)
- Validation result (pass/fail)
- Decision Ledger write result (success/fail/rollback)
- GATE call result (success/timeout/error)
- Retry attempt count (if any)
- Final response status

**Aggregated Metrics** (for monitoring dashboards):
- Requests per minute
- Success rate (% of requests with status="ok")
- Validation failure rate
- GATE timeout rate
- GATE error rate (4XX/5XX)
- Average retry count
- Rollback rate (% of requests rolled back)
- Decision-Event binding completeness (% of decisions with matching events)

**Alert Thresholds**:
- GATE timeout rate > 5% in last 5 minutes → ALERT (GATE may be overloaded)
- GATE error rate > 10% in last 5 minutes → ALERT (GATE unavailable or broken)
- Rollback rate > 2% in last hour → ALERT (potential data integrity issue)
- Duplicate request rate > 20% → INVESTIGATE (client retry behavior?)
- Decision-Event binding completeness < 99% → ALERT (orphaned decisions detected)

**Logging Requirements**:
- All requests logged (timestamp, arguments, result)
- All errors logged with full exception details
- All retries logged with attempt number and wait time
- All rollbacks logged with reason and evidence
- All duplicate detections logged

---

## Part 8: Recovery Procedures for Operators

### Procedure A: GATE Unavailable

**Symptom**: Timeout rate > 5% or persistent 503 errors

**Steps**:
1. Verify GATE service status: `curl http://localhost:5000/health`
2. If GATE is down:
   a. Restart GATE service
   b. Wait for ready state (health check returns 200)
   c. Monitor error rate (should drop to < 1% within 2 minutes)
3. If GATE is up but slow:
   a. Check GATE logs for errors
   b. Check system resources (CPU, memory, disk I/O)
   c. Scale GATE if needed

**During GATE Outage**:
- Incoming decision requests automatically fail-close after 3 retries
- No orphaned decisions created (rollback on failure)
- Callers must retry after GATE recovery
- No manual intervention of decisions needed

---

### Procedure B: Detected Orphaned Decisions

**Symptom**: Binding completeness audit shows < 99%

**Steps**:
1. Run binding audit: `mocka_audit_binding() -> generate binding_audit_report`
2. Identify orphaned decisions: decision_id list without corresponding events
3. For each orphan, determine recovery path:
   a. Recent (< 1 hour): attempt automatic event creation (Option A)
   b. Medium age (1-24 hours): escalate to Human Gate for decision (Option B)
   c. Old (> 24 hours): quarantine pending investigation (Option C)
4. Execute recovery actions
5. Re-run audit to verify binding completeness restored

---

### Procedure C: Hash Mismatch Detected

**Symptom**: Binding integrity verification finds mismatched hashes

**Steps**:
1. Identify affected decision_id
2. Retrieve both Decision Ledger record and Event record
3. Compare hashes and content
4. Determine root cause:
   a. Data corruption: escalate to system administrator
   b. Modification attempt: escalate to security team
   c. System bug: create incident, log to development team
5. Quarantine affected decision (mark binding as compromised)
6. Escalate to Human Gate for decision on recovery/rollback

---

## Part 9: Summary and Design Status

**API Design Selected**: Fail-Closed with Automatic Exponential Backoff Retry

**Key Properties**:
- Atomic semantics: decision and event both succeed or neither succeed
- Silent failures eliminated: caller always knows outcome (ok / fail_closed / error)
- Automatic retry: transient failures (timeout, server errors) retried with exponential backoff
- Rollback guarantee: no orphaned decisions left behind
- Complete error semantics: every error path defined with clear recovery procedure

**Error Classification**:
- Validation Errors (400): non-retryable, caller must fix request
- Transient Errors (500 with retry): automatic retry with backoff
- Permanent Errors (500 without retry): requires manual intervention
- Duplicate: detected and idempotent response returned

**Retry Strategy**:
- Exponential backoff: 2 seconds, 4 seconds, 8 seconds (total 14 seconds max)
- Maximum attempts: 3 total
- Applicable to: GATE timeout, GATE 5XX errors
- Not applicable to: validation errors, Decision Ledger failures, unknown errors

**Monitoring**:
- Per-request metrics tracked and logged
- Aggregated metrics for dashboard monitoring
- Alert thresholds defined for operational oversight
- Complete audit trail for forensics and compliance

**Not Implemented Yet**: This is design only. Implementation will follow HG review and approval.

---

**Document Version**: 0.1 (Design Specification, not Implementation)
**Status**: Ready for HG Review
**Co-Authored-By**: Claude Haiku 4.5 <noreply@anthropic.com>
