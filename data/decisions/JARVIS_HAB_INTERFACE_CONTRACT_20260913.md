# JARVIS/HAB Interface Contract Specification
**2026-09-13**

## Document Control

* Classification: GOVERNANCE / CONTRACT / DESIGN-ONLY
* Authority: KUROKO Protocol (Interface Design Phase)
* Design Scope: Layer 1-2 (Interface contract, schemas, error handling)
* Implementation Scope: NONE (Design-only; no implementation)
* Record Timestamp: 2026-09-13T15:45:00Z
* Status: DESIGN SPECIFICATION (awaiting Human Gate decision HG-HJ-04)

---

## PART 1: Executive Summary

This document specifies the formal interface contract between JARVIS (Coordination) and HAB (Boundary Interpretation). The contract defines:

1. Request schema (JARVIS → HAB)
2. Response schema (HAB → JARVIS)
3. Error handling protocol
4. State synchronization rules
5. Timeout and retry semantics
6. Authorization token exchange protocol

---

## PART 2: Interface Scope & Authority Boundaries

### 2.1 Interface Responsibility Allocation

```
JARVIS Responsibilities (Request Side):
  [J-1] Generate well-formed requests (conform to schema)
  [J-2] Include required fields (request_id, coordination_agent, etc.)
  [J-3] Reference valid evidence (E15-01 through E15-10 only)
  [J-4] Do NOT assume scope, authorization, or consequence binding
  [J-5] Do NOT bypass HAB (always route through formal interface)
  [J-6] Do NOT retry without exponential backoff
  [J-7] Do NOT modify requests mid-flight

HAB Responsibilities (Response Side):
  [H-1] Accept well-formed requests on published endpoint
  [H-2] Parse and normalize requests into canonical form
  [H-3] Verify authorization token validity (MoCKA signature)
  [H-4] Perform scope membership verification (evidence-bounded)
  [H-5] Establish consequence bindings (Enforcement Model A)
  [H-6] Validate evidence lineage (full chain preservation)
  [H-7] Return execution binding or detailed rejection
  [H-8] Handle timeouts gracefully (escalate to MoCKA)
  [H-9] Preserve all semantic distinctions (NOT_FOUND ≠ ABSENT, etc.)
```

---

## PART 3: Request Schema (JARVIS → HAB)

### 3.1 Core Request Structure

```json
{
  "request_id": "REQ-20260913-{uuid}",
  "coordination_agent": "string (jarvis_orchestrator_*)",
  "coordination_session_id": "SESSION-{uuid}",
  "timestamp": "2026-09-13T15:45:00Z",
  "target_agents": ["agent_id_1", "agent_id_2"],
  "coordination_type": "SCOPE_CONSEQUENCE_BINDING | MULTI_AGENT_DELEGATION | EVIDENCE_COLLECTION_REQUEST",
  "request_body": {},
  "context": {
    "authorization_hint": "AUTH-{id} | null",
    "evidence_references": ["E15-01", "E15-02"],
    "scope_universe_candidate": "CANDIDATE_A | CANDIDATE_B | CANDIDATE_C | CANDIDATE_D"
  },
  "routing": {
    "target_handler": "HAB",
    "expected_response_type": "EXECUTION_BINDING | REJECTION",
    "timeout_ms": 30000
  },
  "attributes": {
    "retry_policy": "EXPONENTIAL_BACKOFF",
    "max_retries": 4,
    "priority": "NORMAL"
  }
}
```

### 3.2 Coordination Type: SCOPE_CONSEQUENCE_BINDING

```json
{
  "coordination_type": "SCOPE_CONSEQUENCE_BINDING",
  "request_body": {
    "scope_universe": "CANDIDATE_A | CANDIDATE_B | CANDIDATE_C | CANDIDATE_D",
    "consequence_targets": [
      {
        "target_id": "route_001",
        "target_type": "ROUTE | OPERATION | STATE_TRANSITION",
        "description": "informational description"
      }
    ],
    "evidence_basis": {
      "scope_evidence": ["E15-01", "E15-02"],
      "consequence_evidence": ["E15-03"],
      "justification": "text-only explanation (not binding)"
    }
  }
}
```

### 3.3 Coordination Type: MULTI_AGENT_DELEGATION

```json
{
  "coordination_type": "MULTI_AGENT_DELEGATION",
  "request_body": {
    "delegation_pattern": "SEQUENTIAL | PARALLEL | CASCADING",
    "delegated_agents": [
      {
        "agent_id": "agent_a",
        "sub_request": {
          "scope_universe": "CANDIDATE_A",
          "consequence_target": "operation_001",
          "evidence_references": ["E15-01", "E15-02"]
        }
      }
    ],
    "aggregation_rule": "ALL_SUCCESS | FIRST_SUCCESS | MAJORITY",
    "fallback_behavior": "RETRY | ESCALATE_TO_MOCKA | FAIL_GRACEFULLY"
  }
}
```

### 3.4 Coordination Type: EVIDENCE_COLLECTION_REQUEST

```json
{
  "coordination_type": "EVIDENCE_COLLECTION_REQUEST",
  "request_body": {
    "investigation_scope": "CANDIDATE_A",
    "evidence_gap": "description of missing evidence",
    "proposed_investigation": {
      "sources": ["source_1", "source_2"],
      "methods": ["METHOD_1"],
      "expected_evidence_refs": ["E15-11?"],
      "investigation_justification": "text explanation"
    },
    "target_authority": "Q7_SCOPE_AUTHORITY | Q5_GOVERNANCE_AUTHORITY"
  }
}
```

### 3.5 Request Validation Rules (JARVIS Must Satisfy)

```
[REQ-1] request_id format: REQ-YYYYMMDD-{128-bit uuid}
[REQ-2] coordination_agent must be known JARVIS orchestrator ID
[REQ-3] coordination_session_id must be unique within session lifetime
[REQ-4] timestamp must be ≤ current UTC time
[REQ-5] target_agents must be non-empty array
[REQ-6] coordination_type must be one of: SCOPE_CONSEQUENCE_BINDING, MULTI_AGENT_DELEGATION, EVIDENCE_COLLECTION_REQUEST
[REQ-7] request_body must conform to coordination_type schema
[REQ-8] authorization_hint may be null (HAB will use current token) or valid AUTH-id format
[REQ-9] evidence_references must all be in range E15-01 through E15-10
[REQ-10] scope_universe_candidate must be one of: CANDIDATE_A, CANDIDATE_B, CANDIDATE_C, CANDIDATE_D
[REQ-11] target_handler must be "HAB" (enforces formal interface)
[REQ-12] timeout_ms must be between 5000 and 300000 (5s to 5m)
[REQ-13] No field in request_body infers scope (e.g., "inferred_scope" not permitted)
[REQ-14] No field assumes authorization (e.g., "assumed_authorization" not permitted)
[REQ-15] All string fields must be UTF-8 encoded (no cp932 contamination)
```

---

## PART 4: Response Schema (HAB → JARVIS)

### 4.1 Success Response (Execution Binding)

```json
{
  "request_id": "REQ-20260913-xxxxxxxx",
  "response_id": "RESP-20260913-{uuid}",
  "status": "AUTHORIZED",
  "timestamp": "2026-09-13T15:45:10Z",
  "execution_binding": {
    "binding_id": "BIND-20260913-{uuid}",
    "authorization_id": "AUTH-20260913-{uuid}",
    "scope_universe": "CANDIDATE_A",
    "scope_set": ["Route_X", "Route_Y"],
    "consequence_bindings": [
      {
        "operation_id": "op_001",
        "operation_type": "ROUTE | OPERATION | STATE_TRANSITION",
        "authorization_requirement": {
          "token_id": "AUTH-20260913-xxxxxxxx",
          "authorization_level": "DESIGN_LAYER_ONLY"
        },
        "scope_requirement": {
          "scope_universe": "CANDIDATE_A",
          "membership_criteria_matched": ["E15-01", "E15-02"]
        },
        "evidence_requirement": {
          "scope_evidence": ["E15-01", "E15-02"],
          "consequence_evidence": ["E15-03"],
          "full_lineage_evidence": ["E15-01", "E15-02", "E15-03"]
        },
        "validation_chain": [
          "verify_authorization",
          "verify_scope_membership",
          "verify_consequence_validity",
          "verify_evidence_lineage",
          "execute_atomic"
        ],
        "enforcement_model": "STRICT_IN_BAND"
      }
    ],
    "evidence_lineage": {
      "scope_evidence": ["E15-01", "E15-02"],
      "consequence_evidence": ["E15-03"],
      "runtime_validation_evidence": ["E15-01", "E15-02", "E15-03"]
    },
    "state": "READY_FOR_EXECUTION",
    "hab_verification_timestamp": "2026-09-13T15:45:10Z",
    "hab_sealed": true
  },
  "coordination_instructions": {
    "delegation_pattern": "SEQUENTIAL | PARALLEL",
    "target_agents": ["agent_a", "agent_b"],
    "aggregation_rule": "ALL_SUCCESS"
  }
}
```

### 4.2 Rejection Response (Request Not Authorized)

```json
{
  "request_id": "REQ-20260913-xxxxxxxx",
  "response_id": "RESP-20260913-{uuid}",
  "status": "REJECTED",
  "timestamp": "2026-09-13T15:45:10Z",
  "rejection_reason": "scope_unknown | auth_invalid | evidence_mismatch | consequence_binding_failure | evidence_discipline_violation",
  "detail": "detailed explanation of rejection",
  "scope_status": "VERIFIED | UNKNOWN | EVIDENCE_GAP | UNVERIFIED_EVIDENCE",
  "auth_status": "VALID | EXPIRED | INVALID_SIGNATURE | AUTHORIZATION_LEVEL_INSUFFICIENT",
  "evidence_status": "VALID | EVIDENCE_MISMATCH | EVIDENCE_DISCIPLINE_VIOLATION",
  "consequence_status": "ESTABLISHED | INVALID_CONSEQUENCE | UNMAPPED_OPERATION",
  "appeal_path": "mocka:q7_scope_reassessment | mocka:q5_authorization_reassessment | mocka:q8_enforcement_verification",
  "suggested_next_action": "COLLECT_MORE_EVIDENCE | REQUEST_NEW_AUTHORIZATION | REVISE_CONSEQUENCE_TARGET | RETRY_AFTER_TIMEOUT",
  "debug_info": {
    "parsing_errors": ["error_1", "error_2"],
    "validation_failures": ["failure_1", "failure_2"]
  }
}
```

### 4.3 Response Validation Rules (HAB Must Satisfy)

```
SUCCESS RESPONSE:
  [RESP-1] response_id format: RESP-YYYYMMDD-{128-bit uuid}
  [RESP-2] status = "AUTHORIZED"
  [RESP-3] execution_binding is present and fully populated
  [RESP-4] binding_id format: BIND-YYYYMMDD-{128-bit uuid}
  [RESP-5] authorization_id references valid MoCKA token
  [RESP-6] scope_set is non-empty array
  [RESP-7] consequence_bindings is non-empty array
  [RESP-8] Each consequence_binding includes complete validation_chain
  [RESP-9] evidence_lineage includes all three evidence categories
  [RESP-10] state = "READY_FOR_EXECUTION"
  [RESP-11] hab_sealed = true

REJECTION RESPONSE:
  [RESP-12] status = "REJECTED"
  [RESP-13] rejection_reason must be one of specified reasons
  [RESP-14] detail must be non-empty string
  [RESP-15] scope_status, auth_status, evidence_status, consequence_status must be populated
  [RESP-16] appeal_path must reference valid MoCKA authority (Q5, Q7, or Q8)
  [RESP-17] suggested_next_action provides actionable guidance
  [RESP-18] debug_info may be present (optional; for troubleshooting)
```

---

## PART 5: Error Handling Protocol

### 5.1 HTTP Status Codes

```
200 OK
  Status: AUTHORIZED or REJECTED
  Meaning: Request processed successfully (regardless of outcome)
  Action: JARVIS reads status field and response_body

400 Bad Request
  Meaning: Request schema violation or parsing failure
  Example: coordination_type unknown, missing required fields
  Action: JARVIS logs error, does NOT retry (request malformed)

401 Unauthorized
  Meaning: Authorization token invalid or missing
  Example: auth_invalid, expired token
  Action: HAB returns REJECTED response with auth_status
  Action: JARVIS may appeal to Q5 or request new token

403 Forbidden
  Meaning: Authorization valid but insufficient for operation
  Example: authorization_level_insufficient, scope_denied
  Action: HAB returns REJECTED response with auth_status
  Action: JARVIS may appeal to Q5

404 Not Found
  Meaning: HAB endpoint not found or HAB service unavailable
  Action: JARVIS escalates to MoCKA, logs infrastructure error

408 Request Timeout
  Meaning: HAB processing exceeded timeout_ms
  Action: HAB logs timeout, JARVIS receives error response
  Action: JARVIS may retry with exponential backoff

500 Internal Server Error
  Meaning: HAB internal error (not JARVIS fault)
  Action: JARVIS retries with exponential backoff (up to max_retries)

503 Service Unavailable
  Meaning: HAB temporarily unavailable
  Action: JARVIS retries with exponential backoff, escalates if persistent
```

### 5.2 Error Response Schema

```json
{
  "request_id": "REQ-20260913-xxxxxxxx",
  "response_id": "RESP-20260913-{uuid}",
  "status": "ERROR",
  "http_status": 500,
  "error_type": "INTERNAL_SERVER_ERROR | INFRASTRUCTURE_ERROR | TIMEOUT",
  "error_message": "descriptive error message",
  "timestamp": "2026-09-13T15:45:10Z",
  "retry_info": {
    "retryable": true,
    "suggested_retry_delay_ms": 4000,
    "max_retries_remaining": 3
  },
  "escalation": {
    "escalate_to_mocka": true,
    "escalation_reason": "description",
    "escalation_authority": "Q5_GOVERNANCE_AUTHORITY | Q7_SCOPE_AUTHORITY"
  }
}
```

---

## PART 6: Retry Protocol (JARVIS-side)

### 6.1 Exponential Backoff Algorithm

```
INITIAL ATTEMPT:
  send_request_to_hab()
  start_timer(timeout_ms from request)

RETRY LOGIC (if request_failed):
  retry_count = 1
  backoff_delays = [2000ms, 4000ms, 8000ms, 16000ms]  // 2s, 4s, 8s, 16s
  
  FOR each delay in backoff_delays:
    IF (retry_count <= max_retries) AND (failure_is_retryable):
      wait(delay)
      send_request_to_hab()
      retry_count += 1
    ELSE:
      BREAK
  
  IF all retries exhausted:
    log_failure()
    escalate_to_mocka()
    return COORDINATION_FAILED

RETRYABLE FAILURES:
  [RETRY-1] HTTP 408 (Request Timeout)
  [RETRY-2] HTTP 503 (Service Unavailable)
  [RETRY-3] HTTP 500 (Internal Server Error)
  [RETRY-4] Network error (connection reset, DNS failure, etc.)

NON-RETRYABLE FAILURES:
  [NO-RETRY-1] HTTP 400 (Bad Request) — request malformed
  [NO-RETRY-2] HTTP 401 (Unauthorized) — token issue
  [NO-RETRY-3] HTTP 403 (Forbidden) — authorization denied
  [NO-RETRY-4] REJECTED response (HAB evaluated and rejected)
```

### 6.2 Timeout Handling

```
TIMEOUT SCENARIOS:

Scenario 1: HAB Processing Exceeds timeout_ms
  Action: HAB times out, returns HTTP 408 with error response
  JARVIS Action: Treat as INFRASTRUCTURE_ERROR, retry with backoff
  
Scenario 2: JARVIS Awaiting Response Exceeds timeout_ms
  Action: JARVIS stops waiting, treats as TIMEOUT
  JARVIS Action: Log timeout, escalate to MoCKA, cease retries for this request
  
Scenario 3: MoCKA Appeal Exceeds timeout
  Action: JARVIS stops waiting for MoCKA decision
  JARVIS Action: Log timeout, notify human originator, cease coordination
```

---

## PART 7: Authorization Token Exchange Protocol

### 7.1 Token Retrieval

```
SCENARIO 1: JARVIS includes authorization_hint
  authorization_hint = "AUTH-20260913-xxxxxxxx"
  HAB Action:
    1. Look up token in MoCKA cache/current session
    2. Verify token validity (signature, expiry, authorization_level)
    3. If valid: proceed with SCOPE_VERIFICATION
    4. If invalid: return REJECTED response (auth_invalid)

SCENARIO 2: JARVIS does NOT include authorization_hint
  authorization_hint = null
  HAB Action:
    1. Use currently active authorization token (from MoCKA)
    2. Verify token validity (signature, expiry, authorization_level)
    3. If valid: proceed with SCOPE_VERIFICATION
    4. If no active token: return REJECTED response (auth_invalid)

SCENARIO 3: Token Expires During Processing
  Event: Authorization token expires after parsing but before consequence binding
  HAB Action:
    1. Detect expiry during consequence binding step
    2. Abort processing
    3. Return REJECTED response (auth_expired)
  JARVIS Action:
    1. Appeal to Q5 (Governance Authority)
    2. Request new authorization token
    3. Retry request with new token
```

### 7.2 Token Refresh Flow

```
IF HAB detects auth_expired DURING processing:
  HAB sends: {status: "REJECTED", rejection_reason: "auth_expired", appeal_path: "mocka:q5_authorization_reassessment"}
  
JARVIS receives rejection:
  JARVIS creates appeal: {target_authority: "Q5", requested_action: "ISSUE_NEW_TOKEN"}
  JARVIS sends appeal to MoCKA Q5
  
MoCKA Q5 reviews:
  Option A: APPROVE (issue new token) → JARVIS retries request
  Option B: DENY (don't issue token) → coordination fails
  Option C: DEFER (pending evidence collection) → coordination held
  
JARVIS awaits decision → resume coordination if approved
```

---

## PART 8: State Synchronization Rules

### 8.1 Binding State Lifecycle

```
HAB STATE:           JARVIS VISIBILITY:              ACTION:
────────────────────────────────────────────────────────────
PARSING              (internal HAB only)             JARVIS waits
AUTH_VALIDATION      (internal HAB only)             JARVIS waits
SCOPE_VERIFICATION   (internal HAB only)             JARVIS waits
CONSEQUENCE_BINDING  (internal HAB only)             JARVIS waits
EVIDENCE_LINEAGE     (internal HAB only)             JARVIS waits
BINDING_COMPLETE     (returned as AUTHORIZED)        JARVIS receives binding
READY_FOR_EXECUTION  (binding state = READY)         JARVIS routes to agents
                                                      Runtime executes
EXECUTION_SUCCESS    (Runtime → Event Store)         MoCKA records; JARVIS completes
EXECUTION_FAILURE    (Runtime → MoCKA)               MoCKA escalates; JARVIS notified
REJECTED             (returned as REJECTED)          JARVIS evaluates appeal
TIMEOUT              (returned as ERROR)             JARVIS retries or escalates
```

### 8.2 Event Order Guarantee

```
INVARIANT: HAB processes requests sequentially (no parallel processing)

Sequence:
  Request_1 parsing → validation → binding → response_1
  Request_2 parsing → validation → binding → response_2
  (no interleaving)

Implication:
  JARVIS can safely correlate request_id ↔ response_id
  No out-of-order responses expected
  Idempotency: same request_id always produces same response (if token unchanged)
```

---

## PART 9: Interface Design Closure Conditions

This specification is complete and sealed when:

1. All request schemas fully specified (PART 3)
2. All response schemas fully specified (PART 4)
3. Error handling protocol complete (PART 5)
4. Retry protocol specified (PART 6)
5. Authorization token exchange protocol documented (PART 7)
6. State synchronization rules defined (PART 8)
7. Human Gate decision HG-HJ-04 acceptance pending
8. 20-point integrity verification includes interface contract
9. No code/schema/database modifications (vectors remain = 0)

---

## FINAL STATUS

**JARVIS/HAB Interface Contract: DESIGN SPECIFICATION PHASE**

```
Interface: Request/Response schemas, error handling, retry protocol
Layer: 1-2 (Formal Interface Contract)
Implementation: NONE (Design-only)
State Locks: ALL MAINTAINED (Implementation NOT_GRANTED, M18-Scope HOLD, Modification Vectors = 0)
```

**Interface Contract Sealed: DESIGN SPECIFICATION**
**Authority: KUROKO Protocol (Interface Design Phase)**
**Human Gate Decision: HG-HJ-04 Pending**

