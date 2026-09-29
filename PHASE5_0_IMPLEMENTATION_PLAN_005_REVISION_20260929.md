# IP-005: Orchestra → HAB Authorization
## REVISED IMPLEMENTATION PLAN (Design Phase)
## Date: 2026-09-29
## HG Decision: B (Plan Revision & Re-Approval Required)
## Status: DESIGN REVISION / HG RE-APPROVAL PENDING
## Authority: Human Gate (final)

---

## EXECUTIVE SUMMARY

### Original Plan Premise
```
IP-005 was approved with the assumption:
"Reuse existing Authorization mechanism to connect Orchestra → HAB"

Design: Orchestra → [existing authorization path] → HAB
Scope: Minimal adapter layer (no new authorization scheme)
```

### Current Finding
```
Re-investigation (2026-09-29) traced four connection paths (A/B/C/D).
Result: All four paths show NOT FOUND / NOT CONNECTED in active execution.

Code EXISTS (ExecutionGate, event_gate, human_gate, HAB)
    ≠
Code CALLED (no callers from Orchestra execution path)
    ≠
CONNECTED (no end-to-end flow)
```

### Design Consequence
```
The "existing Authorization Path" assumed by the original Plan
does not exist in currently traced active execution flow.

Therefore:
Original Plan Scope: "Reuse existing Authorization"
Cannot Be Implemented As Approved

HG Decision B:
Accept finding → Redesign IP-005 Scope → Design NEW Authorization Path
→ HG Re-Approval Required → THEN Implementation
```

---

## REVISED SCOPE

### Problem Statement

```
OBJECTIVE (unchanged):
  Establish direct interface between Orchestra execution requests 
  and Human Authority Boundary (HAB) decision layer, ensuring all 
  Orchestra-initiated execution requires explicit HAB authorization 
  before proceeding to AI runtime.

CONSTRAINT FROM ORIGINAL PLAN:
  Use existing Authorization mechanism (no new scheme)

FINDING:
  Existing Authorization mechanism NOT FOUND in active execution path

REVISED OBJECTIVE:
  Design NEW Authorization connection path that:
  ✓ Maintains Human Gate as final authority
  ✓ Implements fail-closed governance
  ✓ Does not introduce AI self-authorization
  ✓ Preserves existing component boundaries
  ✓ Enables runtime verification via Event Store
```

### Revised Design Principle

```
Human Gate (FINAL AUTHORITY)
        ↓
Authorization Decision (must be traceable)
        ↓
runtime_scope (Human Gate approved, immutable)
        ↓
Orchestra Request Processing
        ↓
HAB Gateway (AI socket layer, NOT authority)
        ↓
AI Provider

Governance:
- Authorization source: runtime_scope (HG-approved)
- Authorization decision: explicit APPROVED/REJECTED/DEFERRED
- Default: DENIED (fail-closed)
- Scope match: EXACT MATCH REQUIRED
- Authority reverification: NOT PERMITTED
```

---

## DESIGN: NEW AUTHORIZATION CONNECTION PATH

### Design Architecture

#### [A] Authorization Entry Point (PROPOSED DESIGN)

```
Status: PROPOSED DESIGN
        Requires HG approval for implementation

Source: Human Gate (final authority - EXISTING GOVERNANCE PRINCIPLE)

Proposed Structure: runtime_scope
(NOTE: runtime_scope as Authorization Scope source is PROPOSED, not confirmed)

Definition (PROPOSED):
  runtime_scope = {
    "provider": str,          # gpt / claude / gemini
    "model": str,             # specific model
    "operations": list,       # approved operations
    "resource_scope": str,    # affected resources
    "constraints": dict,      # HG-defined constraints
    "approved_by": str,       # HG signature
    "approval_ts": str        # ISO8601 timestamp
  }

Proposed Source of Truth:
  Loaded from governance layer at initialization
  NOT cached, NOT re-authorized during execution
  
IMMUTABILITY (PROPOSED REQUIREMENT):
  PROPOSED: runtime_scope cannot be modified during execution
  STATUS: Requires HG approval
  Question: Should runtime_scope remain immutable once initialized?
```

#### [B] Authorization Decision Engine (PROPOSED DESIGN)

```
Status: PROPOSED DESIGN OPTION
        NOT EXISTING FACT
        HG APPROVAL REQUIRED

Component: authorization.py (PROPOSED NEW MODULE)
Responsibility: HAB authorization decision generator
NOT an Authority engine (authority is Human Gate via runtime_scope)

NOTE: This represents a NEW AUTHORIZATION ENGINE
      Implementation NOT authorized until HG approval received
      See: Part 7 - New Authorization Engine Proposal

Input:
  orchestra_request = {
    "request_id": str,       # unique request identifier
    "provider": str,         # AI provider
    "model": str,            # model identifier
    "operation": str,        # requested operation
    "scope": str,            # resource scope
    "who_actor": str,        # user/session requesting
    "session_id": str,       # Orchestra session ID
    "when_ts": str           # ISO8601 timestamp
  }

Processing:
  1. Fetch runtime_scope (IMMUTABLE SOURCE)
  2. Validate: provider match (runtime_scope.provider == request.provider)
  3. Validate: model match (runtime_scope.model == request.model)
  4. Validate: operation in approved list (request.operation IN runtime_scope.operations)
  5. Validate: scope match (request.scope == runtime_scope.resource_scope)
  
Decision Logic:
  IF all validations pass:
    approval_status = APPROVED
  ELSE:
    approval_status = REJECTED
  
  IF cannot fetch/parse runtime_scope:
    approval_status = REJECTED (fail-closed)
    reason = "Authorization source unavailable"

Output:
  authorization_result = {
    "request_id": str,            # echo from request
    "approval_status": str,       # APPROVED / REJECTED / DEFERRED
    "authority": "Human Gate",    # immutable designation
    "decision_reason": str,       # why approved/rejected
    "event_id": str,              # Event Store record ID
    "trace_id": str,              # signature chain ID
    "timestamp": str              # ISO8601 decision time
  }
```

#### [C] Event Store Integration (PROPOSED)

```
Status: PROPOSED DESIGN (for HG approval)

Component: event_gate.process_event() (EXISTING - used for logging)
Proposed Responsibility: Persist authorization decisions
(NOTE: Current use is data migration only; integration with active execution is PROPOSED)

Proposed Event Schema:
  {
    "event_id": str,              # unique UUID
    "what_type": "hab_authorization",
    "request_id": str,            # Orchestra request ID (cross-reference)
    "approval_status": str,       # APPROVED / REJECTED / DEFERRED
    "authority": "Human Gate",    # source designation
    "who_actor": str,             # who made the request
    "where_component": "authorization",
    "provider": str,              # AI provider
    "model": str,                 # model identifier
    "operation": str,             # requested operation
    "scope": str,                 # resource scope
    "decision_reason": str,       # why approved/rejected
    "trace_id": str,              # signature chain reference
    "when_ts": str,               # ISO8601 decision timestamp
    "session_id": str             # Orchestra session ID
  }

Proposed Persistence Flow:
  1. event_gate.process_event(auth_event) → INSERT into events table
  2. integrity.sign_event(event_id) → UPDATE trace_id / signature
  3. COMMIT → Write recorded
  
IMMUTABILITY (PROPOSED REQUIREMENT):
  PROPOSED: Authorization decision records are immutable (no update/delete)
  STATUS: NOT VERIFIED in current Event Store implementation
  Question: Does current Event Store guarantee immutability?
           Should immutability be enforced as contract?
```

#### [D] Orchestra Integration (PROPOSED ARCHITECTURE)

```
Status: PROPOSED DESIGN
        Current: Orchestra → HAB (NOT CONNECTED)
        Proposed: Orchestra → Authorization → HAB

Current State: NOT IMPLEMENTED
  orchestra_request flows directly to HAB
  No authorization check in active execution path

Proposed Connection Point: Orchestra dispatcher (gateway.py)

Proposed Integration Pattern (REQUIRES IMPLEMENTATION):
  orchestra_request = parse_request()
  
  # BEFORE execution, AFTER request validation
  auth_result = authorization.check_hab_approval(orchestra_request)
  
  IF auth_result.approval_status == APPROVED:
    # Log approval event
    event_gate.process_event({
      "what_type": "hab_approval_granted",
      "request_id": orchestra_request.request_id,
      ...
    })
    # Proceed to execution
    return execute_orchestra_request(orchestra_request)
  
  ELSE:
    # Log denial event
    event_gate.process_event({
      "what_type": "hab_approval_denied",
      "request_id": orchestra_request.request_id,
      "reason": auth_result.decision_reason,
      ...
    })
    # Return denial to caller
    return denial_response(auth_result.event_id)

QUESTION FOR HG:
Should Orchestra execution requests be routed through authorization check
before reaching HAB gateway?
```

#### [E] HAB Gateway Role (NOT Authority)

```
Component: HAB Gateway (:5010)
Role: AI socket layer, request routing
NOT: Authorization Authority

Responsibilities:
  - Route approved requests to AI providers
  - Execute approved operations
  - Capture lineage (vendor/model/runtime/source) [IP-007]
  - Return results to Orchestra

What HAB Gateway Does NOT Do:
  - Make authorization decisions
  - Re-evaluate scope
  - Override Human Gate decisions
  - Cache authorization tokens
```

---

## AUTHORIZATION CONTRACT (PROPOSED FOR HG APPROVAL)

### EXISTING (Human Gate Governance Foundation)

```
AUTHORITY STRUCTURE:
  = Human Gate (sole authority)
  [EXISTING: MoCKA governance principle]

SELF-AUTHORIZATION PROHIBITIONS:
  AI_SELF_AUTHORIZATION = FORBIDDEN
  JARVIS_SELF_AUTHORIZATION = FORBIDDEN
  HAB_SELF_AUTHORIZATION = FORBIDDEN
  ORCHESTRA_SELF_AUTHORIZATION = FORBIDDEN
  [EXISTING: MoCKA governance principle]

SCOPE_EXPANSION_DURING_EXECUTION:
  = FORBIDDEN
  [EXISTING: MoCKA governance principle]
```

### PROPOSED (For HG Approval - New Authorization Path)

```
AUTHORIZATION_REQUIRED = TRUE
  [PROPOSED: in new path, not verified in current execution]
  Question: Should Orchestra → HAB require explicit authorization?

AUTHORIZATION_SOURCE:
  = runtime_scope (HG-approved at startup)
  [PROPOSED: assumes runtime_scope is HG source of truth]
  Question: Is runtime_scope the correct source?

DECISION_OPTIONS:
  = APPROVED / REJECTED / DEFERRED
  [PROPOSED: decision model]
  Question: Are these three options sufficient?

DEFAULT_DECISION:
  = DENIED (fail-closed)
  [PROPOSED REQUIREMENT]
  Question: Should default be DENIED (reject on missing/unknown)?

SCOPE_MATCHING:
  = EXACT MATCH REQUIRED
  = provider MUST match runtime_scope.provider
  = model MUST match runtime_scope.model
  = operation MUST be in runtime_scope.operations
  = resource_scope MUST match runtime_scope.resource_scope
  [PROPOSED REQUIREMENT: no inference, no completion]
  Question: Should exact match be enforced?
           Which dimensions require exact match?

AUTHORIZATION_RE_VERIFICATION:
  = FORBIDDEN (authority remains Human Gate)
  [PROPOSED REQUIREMENT: once approved, cannot re-verify]
  Question: Should re-verification be prohibited?

SCOPE_INFERENCE_OR_COMPLETION:
  = FORBIDDEN (missing scope = REJECTED)
  [PROPOSED REQUIREMENT: no scope completion logic]
  Question: Should missing scope automatically reject?

FAIL_OPEN:
  = FORBIDDEN
  [PROPOSED REQUIREMENT]
  Question: Should fail-open be explicitly prohibited?

FAIL_CLOSED:
  = REQUIRED
  = Any error → REJECTED
  = Missing component → REJECTED
  = Missing scope → REJECTED
  [PROPOSED REQUIREMENT]
  Question: Should fail-closed be the default behavior?

IMMUTABILITY (PROPOSED REQUIREMENTS):
  runtime_scope immutability = PROPOSED
    (cannot modify runtime_scope during execution)
  Authorization_decision immutability = PROPOSED
    (cannot modify/delete authorization decision records)
  Event evidence immutability = PROPOSED
    (Event Store decisions are permanent)
  [Question: Which immutability requirements should be enforced?]
```

---

## SCOPE BINDING

### Authorization Source

```
Source: runtime_scope (stored in governance layer)

Immutability Guarantee:
  - Cannot be modified by AI/JARVIS/HAB
  - Cannot be modified by Orchestra
  - Can only be modified by Human Gate with explicit decision record
  - Modification requires HG re-approval before execution resumes

Propagation:
  Human Gate
    ↓ (startup initialization)
  governance layer storage
    ↓ (loaded at initialization)
  authorization.py (read-only access)
    ↓ (used for every decision)
  validation result
    ↓ (APPROVED / REJECTED)
  Event Store (immutable record)
```

### Decision Propagation

```
Human Gate Decision
    ↓
runtime_scope (immutable source)
    ↓
Authorization Check
    ↓
approval_status (APPROVED/REJECTED)
    ↓
Event Store (immutable record with trace_id)
    ↓
Orchestra Response (approval or denial)

Boundary Enforcement:
  - If approval_status != APPROVED → execution blocked
  - If approval_status MATCHES scope → proceed
  - If scope undefined → REJECTED
  - If scope mismatch → REJECTED
  - If event_id missing → REJECTED (no Event Store record)
```

---

## COMPARISON: OLD PLAN vs. REVISED PLAN

| Aspect | Original Plan | Revised Plan |
|--------|---------------|--------------|
| **Premise** | Reuse existing Auth path | Design new Auth path |
| **Existing Path** | Assumed connected | Confirmed NOT CONNECTED |
| **Design Approach** | Minimal adapter layer | New connection design |
| **Authorization Source** | Existing (assumed) | runtime_scope (explicit) |
| **Decision Engine** | Existing + adapter | authorization.py (new) |
| **Event Store** | Via existing path | Explicit integration |
| **Authority** | Human Gate (via existing) | Human Gate (explicit) |
| **Fail-Closed** | Yes (assumed) | Yes (explicit contract) |
| **IP-007 Boundary** | Preserved | Preserved |
| **IP-009 Dependency** | Soft | Soft (unchanged) |

---

## DEPENDENCIES

### Upstream (IP-005 requires)
```
- runtime_scope initialized by Human Gate
  Status: Assumed to exist in governance layer
  Required: YES
  
- event_gate.process_event() functional
  Status: Exists (phi_os/event_gate.py)
  Required: YES
  
- integrity signature mechanism available
  Status: Exists
  Required: YES
```

### Downstream (IP-005 provides)
```
- Authorization decision events for Event Store
  Consumer: IP-009 (optional, for Memory sync)
  
- Authorization trace_id for lineage tracking
  Consumer: IP-007 (optional, for readback)
```

### Parallel Implementation
```
IP-005 (Authorization) and IP-007 (Lineage) can run in parallel
- No data flow between them at design level
- Both feed Event Store independently
- No sync dependency
```

---

## FORBIDDEN CHANGES (ABSOLUTE)

```
IMPLEMENTATION CONSTRAINTS:

× Create new Authority engine
× Create new governance mechanism
× Modify Human Gate authority structure
× Modify HAB Gateway core logic
× Modify Orchestra request structure
× Modify runtime_scope schema without HG approval
× Implement AI self-authorization
× Implement JARVIS self-authorization
× Implement HAB self-authorization
× Implement Orchestra self-authorization
× Cache authorization decisions
× Implement TTL-based token validity
× Modify PHI-OS core startup sequence
× Skip authorization for any request
× Implement scope inference/completion
× Implement fail-open logic
× Start IP-009 implementation
× Activate production deployment
× Expand scope beyond this design
× Deploy without Event Store immutability guarantee
```

---

## IMPLEMENTATION PRECONDITIONS (BEFORE CODE STARTS)

```
REQUIRED (already exist):
  ✓ runtime_scope initialization mechanism
  ✓ event_gate.process_event() functional
  ✓ integrity.sign_event() functional
  ✓ Orchestra request dispatcher (gateway.py)

REQUIRED (from HG):
  ✓ Explicit authorization to proceed with NEW path design
  ✓ Confirmation that runtime_scope is HG's source of truth
  ✓ Confirmation that Event Store immutability is enforced
  ✓ Confirmation that fail-closed is non-negotiable

REQUIRED (from design review):
  ✓ This plan is approved as DESIGN only (not implementation)
  ✓ Runtime verification will be required after implementation
  ✓ Implementation authorization is separate from design approval
```

---

## PLAN SELF-AUDIT CHECKLIST

```
AUDIT STATUS: FAIL / REQUIRES HG CLARIFICATION

NOTE: This is NOT a code quality failure.
      This indicates that design proposals contain unresolved items
      requiring explicit HG judgment.

Governance Foundation (EXISTING - NO HG RE-APPROVAL NEEDED):
  [✓] Human Gate remains sole authority
  [✓] No AI self-authorization path exists
  [✓] No JARVIS self-authorization path exists
  [✓] No HAB self-authorization path exists
  [✓] No Orchestra self-authorization path exists
  [✓] Scope expansion is prohibited
  
Design Proposals (PROPOSED - REQUIRES HG APPROVAL):
  [?] runtime_scope as authorization source
      Status: PROPOSED / REQUIRES HG APPROVAL
  
  [?] runtime_scope immutability
      Status: PROPOSED / REQUIRES HG APPROVAL
      Question: Should runtime_scope be immutable during execution?
  
  [?] Authorization decisions are immutable (Event Store)
      Status: PROPOSED / NOT VERIFIED in current implementation
      Question: Should authorization decisions be immutable?
  
  [?] Exact scope match required (no inference/completion)
      Status: PROPOSED / REQUIRES HG APPROVAL
      Question: Which dimensions require exact match?
  
  [?] Default decision is DENIED (fail-closed)
      Status: PROPOSED / REQUIRES HG APPROVAL
      Question: Should default be DENIED on missing/error?
  
  [?] Fail-closed logic
      Status: PROPOSED / REQUIRES HG APPROVAL
      Question: Should all errors result in REJECTED?
  
  [?] authorization.py as new decision engine
      Status: PROPOSED NEW AUTHORIZATION ENGINE
      Question: Should new Authorization Engine be created?
              Or should existing mechanisms be adapted?
  
Design Components (PROPOSED - REQUIRES HG APPROVAL):
  [?] event_gate integration with authorization
      Status: PROPOSED / CURRENT STATE: NOT CONNECTED
      Question: Should event_gate be integrated with authorization?
  
  [?] HAB Gateway role (NOT authority)
      Status: PROPOSED / REQUIRES HG APPROVAL
  
  [?] Orchestra → Authorization → HAB connection
      Status: PROPOSED / CURRENT STATE: NOT CONNECTED
      Question: Should Orchestra be routed through authorization?
  
Boundaries & Dependencies (VERIFIED - NO CHANGES):
  [✓] IP-007 boundary preserved
  [✓] IP-009 not started
  [✓] No new governance mechanism created
  [✓] Design is NOT claiming implementation complete
  [✓] Runtime verification is NOT claimed
  [✓] Production activation NOT authorized

HG Decisions Pending (REQUIRED BEFORE IMPLEMENTATION):
  [PENDING] New Authorization Engine creation approval
  [PENDING] runtime_scope source-of-truth confirmation
  [PENDING] Fail-closed requirement confirmation
  [PENDING] Exact scope match requirement confirmation
  [PENDING] Immutability requirement confirmations
  [PENDING] Orchestra authorization integration approval
  [PENDING] Design Approval (all proposals)
  [PENDING] Implementation Authorization (separate from Design)
```

---

## STATUS

```
IP-007 = CLOSED / STATIC VERIFIED (RUNTIME NOT VERIFIED)
         [IMMUTABLE: Not modified in this revision]

IP-005 = HG DECISION B ACCEPTED
         (Planning / Scope Revision Approved)
         
         REVISED PLAN DESIGN: COMPLETE (THIS DOCUMENT)
         STATUS: PROPOSED DESIGN
         Contains: 8+ unresolved items requiring HG judgment
         
         AWAITING HG RE-APPROVAL ON:
         - New Authorization Engine
         - runtime_scope governance
         - fail-closed policy
         - exact scope matching
         - immutability guarantees
         - Orchestra authorization routing
         - (see Part 16: HG Decision Required)

IP-009 = NOT STARTED
         (Outside current implementation scope)

AUTHORIZATION ENGINE = NOT IMPLEMENTED
                      (PROPOSED for HG judgment)

ORCHESTRA → HAB = NOT CONNECTED
                (PROPOSED for HG judgment)

CODE CHANGES = 0
COMMITS = 0
RUNTIME ACTIVATION = 0
PRODUCTION = NOT AUTHORIZED

IMPLEMENTATION BLOCKED UNTIL HG RE-APPROVAL RECEIVED
```

---

## NEXT STEP: HG RE-APPROVAL

This revised plan requires Human Gate approval before implementation begins.

See: `HG_RE_APPROVAL_REQUEST_IP-005_20260929.md`

Approval Sought:
1. Is this revised design acceptable as NEW Authorization Path?
2. Is Human Gate authority maintained?
3. Are governance principles preserved?
4. May implementation proceed upon approval?

```
READY FOR HG REVIEW
2026-09-29 DESIGN REVISION COMPLETE
```
