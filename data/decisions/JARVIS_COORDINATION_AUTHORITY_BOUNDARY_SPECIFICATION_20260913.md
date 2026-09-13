# JARVIS Coordination Authority Boundary Specification
**2026-09-13**

## Document Control

* Classification: GOVERNANCE / ARCHITECTURE / DESIGN-ONLY
* Authority: KUROKO Protocol (JARVIS Design Phase)
* Design Scope: Layer 1-2 (JARVIS coordination model, non-authority locks, request protocol)
* Implementation Scope: NONE (Design-only; no code/database modifications)
* Record Timestamp: 2026-09-13T15:40:00Z
* Status: DESIGN SPECIFICATION (awaiting Human Gate decision HG-HJ-03)

---

## PART 1: Executive Summary

JARVIS (Judgment-Aware Request & Value Interpreted System) is the multi-agent coordination layer that routes requests through HAB for interpretation and enforcement. JARVIS has NO autonomous authority to:

* Define scope
* Create authorization
* Interpret consequence binding
* Execute decisions

JARVIS MAY:
* Propose coordination patterns across agents
* Aggregate multi-agent responses
* Route requests through formal HAB boundary
* Request evidence collection from bound sources

---

## PART 2: JARVIS Core Principle

**Coordination Without Authority**

```
All JARVIS actions flow THROUGH HAB before any authority is assumed.
All JARVIS proposals are REQUESTS to HAB, not autonomous decisions.
All JARVIS routing is FORMAL (via contracts), not informal (direct agent calls).
```

---

## PART 3: JARVIS Authority Constraints (Locked)

### 3.1 Explicit JARVIS Permissions

JARVIS MAY:
1. Send coordination requests to HAB (per interface contract)
2. Specify target agents for coordination
3. Propose scope universes (A/B/C/D; per available evidence)
4. Reference evidence from HG-R15 program (E15-01 through E15-10)
5. Aggregate responses from multiple agents
6. Request evidence collection or investigation
7. Appeal scope/authorization decisions to MoCKA (Q7/Q5)
8. Implement internal coordination state machine (layer 3+, if authorized)

### 3.2 Explicit JARVIS Non-Authorities (Immutable)

JARVIS MUST NOT:
1. Assume scope definition autonomously
2. Infer scope from code artifacts (109 Flask routes, etc.)
3. Infer scope from historical claims (30 route claims, etc.)
4. Infer scope from binding model paths (15 consequential paths, etc.)
5. Infer scope from evidence gaps (NOT_FOUND ≠ ABSENT; absence ≠ rejection)
6. Create authorization tokens
7. Override authorization verification
8. Bind consequences without HAB (Enforcement Model A application)
9. Execute decisions directly (must route through HAB → Runtime)
10. Re-interpret Enforcement Model A or Persistence Strategy D
11. Modify M18-Scope status (HOLD maintained per HG-Q7)
12. Change Implementation Authorization status (NOT_GRANTED per HG-R14)
13. Modify any modification vectors (all remain = 0)
14. Make governance decisions (MoCKA Q5/Q7/Q8 authority only)

---

## PART 4: JARVIS Request Protocol

### 4.1 JARVIS Coordination Request Format

```
REQUEST STRUCTURE:
{
  "request_id": "REQ-20260913-[uuid]",
  "originating_agent": "jarvis_orchestrator_[id]",
  "coordination_type": "SCOPE_CONSEQUENCE_BINDING | MULTI_AGENT_DELEGATION | EVIDENCE_COLLECTION_REQUEST",
  "target_agents": ["agent_a", "agent_b", "agent_c", ...],
  "payload": {
    // Type-specific payload (see 4.2-4.4)
  },
  "context": {
    "authorization_hint": "token_reference | null",
    "evidence_references": ["E15-01", "E15-02", ...],
    "scope_universe_candidate": "CANDIDATE_A | CANDIDATE_B | CANDIDATE_C | CANDIDATE_D"
  },
  "routing": {
    "target_handler": "HAB",
    "expected_response_type": "EXECUTION_BINDING | REJECTION | TIMEOUT"
  }
}

INVARIANTS (Enforced by JARVIS):
  [INV-1] request_id is unique within coordination session
  [INV-2] originating_agent is valid JARVIS orchestrator ID
  [INV-3] target_agents are all bound/known agents
  [INV-4] payload is well-formed per coordination_type
  [INV-5] evidence_references exist in HG-R15 program (E15-01-E15-10)
  [INV-6] scope_universe_candidate is one of {A, B, C, D}
  [INV-7] target_handler is always "HAB" (no bypassing)
  [INV-8] No assumption of scope definition in payload
```

### 4.2 Coordination Type: SCOPE_CONSEQUENCE_BINDING

```
PAYLOAD:
{
  "coordination_type": "SCOPE_CONSEQUENCE_BINDING",
  "scope_universe": "CANDIDATE_A | CANDIDATE_B | CANDIDATE_C | CANDIDATE_D",
  "consequence_targets": [
    {
      "target_id": "route_001 | operation_002 | ...",
      "target_type": "ROUTE | OPERATION | STATE_TRANSITION",
      "description": "human-readable description (informational only)"
    }
  ],
  "evidence_basis": {
    "scope_evidence": ["E15-01", "E15-02", ...],
    "consequence_evidence": ["E15-03", ...],
    "justification": "text explanation (informational; not binding)"
  },
  "request_attributes": {
    "urgency": "NORMAL | HIGH | CRITICAL",
    "retry_policy": "EXPONENTIAL_BACKOFF | IMMEDIATE_FAIL",
    "timeout_ms": 30000
  }
}

JARVIS RESPONSIBILITY (Scope/Consequence Binding):
  [J-1] Request is well-formed and parseable
  [J-2] Evidence references are valid (exist in HG-R15)
  [J-3] Scope universe is one of {A, B, C, D}
  [J-4] Consequence targets are documented (not inferred)
  [J-5] No autonomous scope inference
  [J-6] Authorization verification delegated to HAB
  [J-7] Consequence binding delegated to HAB (Enforcement Model A)

HAB RESPONSIBILITY (from JARVIS request):
  [H-1] Parse and normalize request
  [H-2] Verify authorization token presence/validity
  [H-3] Verify scope membership (evidence-bounded)
  [H-4] Establish consequence bindings (Model A)
  [H-5] Validate evidence lineage
  [H-6] Return execution binding or rejection
```

### 4.3 Coordination Type: MULTI_AGENT_DELEGATION

```
PAYLOAD:
{
  "coordination_type": "MULTI_AGENT_DELEGATION",
  "delegation_pattern": "SEQUENTIAL | PARALLEL | CASCADING",
  "delegated_agents": [
    {
      "agent_id": "agent_a",
      "sub_request": {
        "scope_universe": "CANDIDATE_A",
        "consequence_target": "operation_001",
        "evidence_references": ["E15-01", "E15-02"]
      }
    },
    {
      "agent_id": "agent_b",
      "sub_request": {...}
    }
  ],
  "aggregation_rule": "ALL_SUCCESS | FIRST_SUCCESS | MAJORITY | CUSTOM",
  "fallback_behavior": "RETRY | ESCALATE_TO_MOCKA | FAIL_GRACEFULLY"
}

JARVIS RESPONSIBILITY (Delegation):
  [J-1] Delegation pattern is valid
  [J-2] Each sub_request is well-formed
  [J-3] No circular delegation
  [J-4] Each agent is authorized to receive sub_request
  [J-5] Aggregation rule is deterministic

HAB RESPONSIBILITY (from delegation request):
  [H-1] Normalize each sub_request independently
  [H-2] Verify authorization for each agent+scope combination
  [H-3] Establish bindings for all sub_requests
  [H-4] Apply aggregation rule
  [H-5] Return aggregated execution binding or rejection
```

### 4.4 Coordination Type: EVIDENCE_COLLECTION_REQUEST

```
PAYLOAD:
{
  "coordination_type": "EVIDENCE_COLLECTION_REQUEST",
  "investigation_scope": "CANDIDATE_A | CANDIDATE_B | CANDIDATE_C | CANDIDATE_D",
  "evidence_gap": "DESCRIPTION OF MISSING EVIDENCE",
  "proposed_investigation": {
    "sources": ["source_1", "source_2", ...],
    "methods": ["METHOD_1", "METHOD_2", ...],
    "expected_evidence_refs": ["E15-11?", "E15-12?", ...],
    "investigation_justification": "text explanation"
  },
  "target_authority": "Q7_SCOPE_AUTHORITY | Q5_GOVERNANCE_AUTHORITY"
}

JARVIS RESPONSIBILITY (Evidence Collection Request):
  [J-1] Investigation is read-only (HG-R15 constraint)
  [J-2] Does not modify system state
  [J-3] Target authority is appropriate (Q7 or Q5)
  [J-4] Justification is evidence-based, not speculative

HAB RESPONSIBILITY (Evidence Collection Request):
  [H-1] Validate request format
  [H-2] Verify this is investigation-only (no authorization implications)
  [H-3] Route to MoCKA (not to Runtime)
  [H-4] Return acknowledgment + reference to HG-R15 program authority
```

---

## PART 5: JARVIS State Machine

### 5.1 States

```
IDLE
  ↓
COORDINATION_INITIATED (coordination request created)
  ↓
REQUEST_PREPARATION (prepare request for HAB)
  ├─ VALIDATION (check invariants; [INV-1] through [INV-8])
  │  ├─ VALIDATION_FAILED → REQUEST_INVALID (escalate to human; return to IDLE)
  │  └─ VALIDATION_SUCCESS ↓
  └─
  ↓
ROUTING_TO_HAB (send request to HAB via formal interface)
  ├─ ROUTING_ERROR → ROUTING_FAILED (retry with backoff)
  └─ ROUTING_SUCCESS ↓

AWAITING_HAB_RESPONSE (wait for execution binding or rejection)
  ├─ HAB_ACCEPTS (execution binding received)
  │   ↓
  │   RECEIVING_BINDING
  │   ↓
  │   DELEGATION_TO_AGENTS (forward execution binding to target agents)
  │   ├─ DELEGATION_SUCCESS → EXECUTING
  │   └─ DELEGATION_ERROR → DELEGATION_FAILED (escalate to HAB/MoCKA)
  │
  ├─ HAB_REJECTS (rejection reason received)
  │   ↓
  │   RECEIVING_REJECTION
  │   ↓
  │   EVALUATING_APPEAL
  │   ├─ APPEAL_ELIGIBLE (rejection reason suggests evidence/scope reassessment)
  │   │   ↓
  │   │   APPEAL_TO_MOCKA (send appeal to Q7/Q5)
  │   │   ↓
  │   │   AWAITING_MOCKA_RESPONSE
  │   │   ├─ MOCKA_ACCEPTS → COORDINATION_RESUMED (return to ROUTING_TO_HAB)
  │   │   ├─ MOCKA_REJECTS → APPEAL_DENIED (return to IDLE)
  │   │   └─ MOCKA_TIMEOUT → TIMEOUT (return to IDLE)
  │   │
  │   └─ APPEAL_INELIGIBLE (rejection is definitive)
  │       ↓
  │       COORDINATION_FAILED (notify originating human; return to IDLE)
  │
  └─ HAB_TIMEOUT (no response within timeout_ms)
      ↓
      TIMEOUT_ESCALATION (escalate to MoCKA)
      ↓
      COORDINATION_FAILED (return to IDLE)

EXECUTING (agents executing the binding)
  ├─ EXECUTION_SUCCESS (all target agents report success)
  │   ↓
  │   COORDINATION_COMPLETE (return to IDLE)
  │
  ├─ EXECUTION_PARTIAL_FAILURE (some agents fail; aggregation rule determines outcome)
  │   ├─ AGGREGATION_SATISFIED → COORDINATION_COMPLETE (return to IDLE)
  │   └─ AGGREGATION_FAILED → EXECUTION_FAILED (escalate to MoCKA; return to IDLE)
  │
  └─ EXECUTION_FAILURE (execution binding fails at Runtime)
      ↓
      EXECUTION_ERROR (escalate to MoCKA; return to IDLE)
```

### 5.2 State Transition Rules

```
Transition: IDLE → COORDINATION_INITIATED
  Trigger: Coordination request created by JARVIS orchestrator
  Action: Log request, assign request_id
  Next: REQUEST_PREPARATION

Transition: COORDINATION_INITIATED → REQUEST_PREPARATION
  Trigger: Request creation acknowledged
  Action: Validate invariants [INV-1] through [INV-8]
  Error: VALIDATION_FAILED → REQUEST_INVALID → IDLE
  Next: VALIDATION

Transition: VALIDATION → ROUTING_TO_HAB
  Trigger: All invariants satisfied
  Action: Serialize request, sign (if required), prepare for HAB
  Next: ROUTING_TO_HAB

Transition: ROUTING_TO_HAB → AWAITING_HAB_RESPONSE
  Trigger: Request successfully sent to HAB
  Action: Start timeout timer (from request_attributes.timeout_ms)
  Error: ROUTING_ERROR (retry exponential backoff: 2s, 4s, 8s, 16s; then fail)
  Next: AWAITING_HAB_RESPONSE

Transition: AWAITING_HAB_RESPONSE → RECEIVING_BINDING
  Trigger: HAB returns execution binding (status = AUTHORIZED)
  Action: Validate binding schema, verify HAB signature (if present)
  Next: DELEGATION_TO_AGENTS

Transition: AWAITING_HAB_RESPONSE → RECEIVING_REJECTION
  Trigger: HAB returns rejection (status = REJECTED)
  Action: Log rejection reason, extract appeal_path
  Next: EVALUATING_APPEAL

Transition: AWAITING_HAB_RESPONSE → TIMEOUT_ESCALATION
  Trigger: No response from HAB within timeout_ms
  Action: Log timeout, send escalation to MoCKA
  Next: COORDINATION_FAILED → IDLE

Transition: RECEIVING_BINDING → DELEGATION_TO_AGENTS
  Trigger: Execution binding validated
  Action: Forward binding to all target_agents
  Error: DELEGATION_ERROR (escalate to HAB/MoCKA)
  Next: EXECUTING | DELEGATION_FAILED

Transition: DELEGATION_TO_AGENTS → EXECUTING
  Trigger: All target agents acknowledge binding receipt
  Action: Agents begin execution (Runtime enforces Strict In-Band model)
  Next: (wait for execution completion)

Transition: EXECUTING → COORDINATION_COMPLETE
  Trigger: All agents report execution_success (or aggregation rule satisfied)
  Action: Log completion, record execution event
  Next: IDLE

Transition: EXECUTING → EXECUTION_FAILED
  Trigger: Execution failure or aggregation rule not satisfied
  Action: Log failure details, escalate to MoCKA
  Next: IDLE

Transition: RECEIVING_REJECTION → EVALUATING_APPEAL
  Trigger: Rejection reason extracted
  Action: Determine if appeal eligible (scope_unknown, evidence_gap, etc.)
  Next: APPEAL_TO_MOCKA | COORDINATION_FAILED

Transition: EVALUATING_APPEAL → APPEAL_TO_MOCKA
  Trigger: Appeal eligible (rejection suggests reassessment needed)
  Action: Send appeal to MoCKA (Q7 for scope, Q5 for authorization)
  Next: AWAITING_MOCKA_RESPONSE

Transition: AWAITING_MOCKA_RESPONSE → COORDINATION_RESUMED
  Trigger: MoCKA accepts appeal and revises authorization/scope
  Action: Log MoCKA decision, return to ROUTING_TO_HAB with revised context
  Next: ROUTING_TO_HAB

Transition: AWAITING_MOCKA_RESPONSE → APPEAL_DENIED
  Trigger: MoCKA rejects appeal
  Action: Log MoCKA decision, inform JARVIS originator
  Next: IDLE

Transition: EVALUATING_APPEAL → COORDINATION_FAILED
  Trigger: Appeal ineligible (rejection is definitive)
  Action: Log decision, notify JARVIS originator
  Next: IDLE
```

---

## PART 6: JARVIS Responsibility Matrix

| Function | JARVIS Ownership | HAB/Runtime Ownership | Notes |
|----------|------------------|----------------------|-------|
| Request initiation | YES | - | JARVIS proposes coordination |
| Request validation | YES | - | JARVIS verifies invariants |
| Scope assumption | NO | MoCKA (Q7) | JARVIS cannot infer scope |
| Authorization verification | NO | HAB (via MoCKA token) | HAB verifies token |
| Consequence binding | NO | HAB (Model A) | HAB enforces Enforcement Model A |
| Evidence lineage validation | NO | HAB | HAB validates evidence chain |
| Execution binding | NO | HAB | HAB synthesizes binding |
| Agent delegation | YES | - | JARVIS routes to target agents |
| Multi-agent aggregation | YES | - | JARVIS applies aggregation rule |
| Execution enforcement | NO | Runtime (Strict In-Band) | Runtime enforces atomicity |
| Appeal to MoCKA | YES | - | JARVIS initiates, MoCKA decides |
| Timeout handling | YES | - | JARVIS escalates after timeout |
| Error handling | YES (routing) | HAB/MoCKA (authority) | JARVIS propagates; MoCKA decides |

---

## PART 7: Semantic Discipline Preserved by JARVIS

### 7.1 Scope Non-Inference Rules

```
JARVIS MUST NOT INFER SCOPE FROM:

[NO-1] Code Artifact Count
  Example: "109 Flask routes exist, therefore scope ≈ 109 items"
  Why Wrong: Code count ≠ scope membership (route may be multi-operation)
  JARVIS Action: Reference E15-01 through E15-10 only; do NOT infer from routes

[NO-2] Historical Route Claims
  Example: "30 historical route claims exist, therefore scope = 30"
  Why Wrong: Historical claims ≠ evidence-bounded criteria (claims may be stale)
  JARVIS Action: Request evidence re-evaluation via HG-R15 program; do NOT assume

[NO-3] Binding Model Consequential Paths
  Example: "15 binding model paths exist, therefore scope has 15 targets"
  Why Wrong: Binding paths ≠ scope membership (paths may be unused or hypothetical)
  JARVIS Action: Verify consequence binding via HAB (Model A); do NOT infer

[NO-4] Evidence Gaps
  Example: "Evidence for item X is not found, therefore item X not in scope"
  Why Wrong: NOT_FOUND ≠ ABSENT (absence of evidence ≠ evidence of absence)
  JARVIS Action: Report evidence gap to HG-R15; do NOT conclude exclusion

[NO-5] Aggregate Signals
  Example: "Routes + claims + paths = 109 + 30 + 15 = 154; scope = 154"
  Why Wrong: Arithmetic on signal counts ≠ scope definition (meaningless)
  JARVIS Action: Request Q7 scope definition; do NOT calculate
```

### 7.2 Evidence-Bounded Authority Chain Preserved

```
JARVIS MUST MAINTAIN:

[P-1] Evidence Lineage: HG-R15 Program → E15-01-E15-10 → Membership Criteria → Scope Definition
  Action: Reference only E15-01 through E15-10 in requests
  
[P-2] Scope Membership Criteria Immutability
  Action: Do NOT modify criteria mid-coordination
  Escalation: If criteria need revision, appeal to Q7

[P-3] NOT_PROVEN ≠ REJECTED
  Action: If scope candidate not yet proven, do NOT reject it
  Escalation: Request additional evidence via HG-R15

[P-4] NOT_FOUND ≠ ABSENT
  Action: If evidence not found, do NOT infer absence
  Escalation: Request evidence search via HG-R15
```

---

## PART 8: JARVIS Appeal Authority (Q7 / Q5 Escalation)

### 8.1 Appeal Types & Escalation Paths

```
Appeal Type 1: SCOPE_UNKNOWN
  Rejection Reason: scope_status = UNKNOWN (no membership criteria)
  Appeal Path: MoCKA Q7 (Scope Authority)
  Appeal Content: "Request evidence-bounded membership criteria for [scope_universe]"
  Q7 Options: DEFINE_SCOPE (with evidence) | CONTINUE_HOLD | COLLECT_MORE_EVIDENCE

Appeal Type 2: EVIDENCE_GAP
  Rejection Reason: Evidence reference not in membership criteria
  Appeal Path: MoCKA Q7 (Scope Authority)
  Appeal Content: "Request evidence collection for [specific_evidence_need]"
  Q7 Options: AUTHORIZE_EVIDENCE_PROGRAM | REJECT_SCOPE_CANDIDATE | CONTINUE_HOLD

Appeal Type 3: AUTHORIZATION_INVALID
  Rejection Reason: auth_status = INVALID (token expired, invalid signature, etc.)
  Appeal Path: MoCKA Q5 (Governance Authority)
  Appeal Content: "Request new authorization token for [operation_class]"
  Q5 Options: ISSUE_NEW_TOKEN | DENY_OPERATION | CONDITION_TOKEN

Appeal Type 4: CONSEQUENCE_BINDING_FAILURE
  Rejection Reason: consequence binding not in Model A table
  Appeal Path: MoCKA Q5 or Q8 (depending on whether Model A needs revision)
  Appeal Content: "Request Model A binding update for [operation_id]"
  Q5/Q8 Options: ADD_BINDING_TO_MODEL_A | REJECT_OPERATION | REVISE_MODEL_A

Appeal Type 5: EVIDENCE_DISCIPLINE_VIOLATION
  Rejection Reason: Evidence validation failed (evidence ≠ scope evidence)
  Appeal Path: MoCKA Q7 or Q5
  Appeal Content: "Request evidence re-evaluation for [scope_universe]"
  Q7 Options: REVISE_MEMBERSHIP_CRITERIA | COLLECT_MORE_EVIDENCE
```

### 8.2 JARVIS Appeal Protocol

```
STEP 1: JARVIS receives rejection from HAB
  rejection = {
    "request_id": "REQ-20260913-xxxxxxxx",
    "status": "REJECTED",
    "rejection_reason": "scope_unknown | auth_invalid | ...",
    "appeal_path": "mocka:q7_scope_reassessment | mocka:q5_authorization_reassessment",
    ...
  }

STEP 2: JARVIS evaluates appeal eligibility
  IF rejection_reason ∈ [SCOPE_UNKNOWN, EVIDENCE_GAP, EVIDENCE_DISCIPLINE_VIOLATION]
    THEN appeal_eligible = true, target_authority = Q7
  ELSE IF rejection_reason ∈ [AUTHORIZATION_INVALID, CONSEQUENCE_BINDING_FAILURE]
    THEN appeal_eligible = true, target_authority = Q5 | Q8
  ELSE
    THEN appeal_eligible = false, report to human and STOP

STEP 3: JARVIS sends appeal to MoCKA
  appeal = {
    "appeal_id": "APPEAL-20260913-xxxxxxxx",
    "original_request_id": "REQ-20260913-xxxxxxxx",
    "rejection_reason": rejection.rejection_reason,
    "target_authority": "Q7 | Q5 | Q8",
    "appeal_justification": "text explanation",
    "requested_action": "DEFINE_SCOPE | ISSUE_NEW_TOKEN | ...",
    "timestamp": "2026-09-13T15:40:00Z"
  }

STEP 4: JARVIS awaits MoCKA decision
  IF MoCKA decision = APPROVED (with revisions)
    THEN resume coordination with revised context
  ELSE IF MoCKA decision = DENIED
    THEN report denial to human and STOP
  ELSE
    THEN timeout and escalate
```

---

## PART 9: JARVIS Deployment Constraints (Layer 1-2 Design)

JARVIS specification is design-only (Layer 1-2). No implementation artifacts:

```
NOT INCLUDED (Layer 3+):
  - Code repository structure
  - Agent implementation details
  - Database schema for coordination state
  - Runtime orchestration engine
  - Configuration files

INCLUDED (Layer 1-2):
  - Coordination model (no autonomous authority)
  - Request protocol specification
  - State machine specification
  - Responsibility matrix
  - Appeal escalation paths
  - Semantic discipline rules
```

---

## PART 10: JARVIS Design Closure Conditions

This specification is complete and sealed when:

1. All JARVIS authority constraints documented (PART 3)
2. Request protocol fully specified (PART 4)
3. State machine fully specified (PART 5)
4. Responsibility matrix complete (PART 6)
5. Semantic discipline preservation confirmed (PART 7)
6. Appeal authority and escalation paths documented (PART 8)
7. Human Gate decision HG-HJ-03 acceptance pending
8. 20-point integrity verification includes all JARVIS constraints
9. No code/schema/database modifications permitted (vectors remain = 0)

---

## FINAL STATUS

**JARVIS Coordination Authority Boundary Specification: DESIGN SPECIFICATION PHASE**

```
Authority: Coordination Only (NO scope definition, NO authorization, NO execution)
Layer: 1-2 (Responsibility Separation, Request Protocol, State Machine)
Implementation: NONE (Design-only)
State Locks: ALL MAINTAINED (Implementation NOT_GRANTED, M18-Scope HOLD, Modification Vectors = 0)
```

**Specification Sealed: DESIGN SPECIFICATION**
**Authority: KUROKO Protocol (JARVIS Design Phase)**
**Human Gate Decision: HG-HJ-03 Pending**

