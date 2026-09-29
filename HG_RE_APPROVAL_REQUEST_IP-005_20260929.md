# HG Re-Approval Request: IP-005 Revised Scope
## Date: 2026-09-29
## Authority: Human Gate
## Decision Required: Approval of Revised IP-005 Plan & Design

---

## EXECUTIVE SUMMARY

**Situation:**
- IP-005 was originally approved with premise: "Reuse existing Authorization mechanism"
- Pre-implementation audit (2026-09-29) confirmed that existing path is NOT CONNECTED in active execution
- Per HG Decision B, we are requesting re-approval for a REVISED IP-005 scope

**What Changed:**
- Scope changed from "Reuse existing Auth path" to "Design new Auth path"
- Design approach changed from "Minimal adapter layer" to "New connection design"
- Authority designation changed from "Existing (assumed)" to "runtime_scope (explicit)"

**What Stayed the Same:**
- Objective: Orchestra → HAB authorization (unchanged)
- Authority: Human Gate remains final authority (strengthened, now explicit)
- Principle: Fail-closed, no AI self-authorization (now formalized)
- Boundary: IP-007 lineage tracking preserved
- Status: DESIGN ONLY (no implementation, no code changes)

---

## PART 1: WHY ORIGINAL PLAN CANNOT PROCEED

### Original Approval (2026-09-29 morning)

```
IP-005 Implementation Plan: 
  "Establish direct interface between Orchestra execution requests 
   and Human Authority Boundary (HAB) decision layer"
   
Approved Approach: 
  "Use existing Authorization mechanism (no new scheme)"
  
Implication: 
  Existing path from Human Gate → Authorization → runtime_scope → Orchestra → HAB
  is already implemented and wired. IP-005 implementation adds minimal adapter layer.
```

### Pre-Implementation Audit Findings (2026-09-29)

**Investigation Scope:** Four connection paths traced (A/B/C/D)

```
[A] Human Gate → existing Authorization → runtime_scope
    Status: NOT CONNECTED
    Finding: ExecutionGate exists but not called from active execution path
    
[B] Orchestra → HAB :5010
    Status: NOT CONNECTED
    Finding: event_gate.process_event() exists but gateway.py does not call it
    
[C] Authorization result → HAB request
    Status: NOT CONNECTED
    Finding: human_gate.get_state() exists but not called from active execution
    
[D] Authorization Decision - Producer, Storage, Propagation
    Status: NOT CONNECTED
    Finding: ExecutionGate.check() and ExecutionGate.run() exist but have zero callers
```

**Classification:**

```
CODE EXISTS:
  ✓ ExecutionGate (phi_os/context/execution_context.py)
  ✓ event_gate.process_event() (phi_os/event_gate.py)
  ✓ human_gate state machine (phi_os/human_gate.py)
  ✓ HAB (phi_os/hab/)

CODE CALLED FROM ACTIVE EXECUTION:
  ✗ Zero callers of ExecutionGate.run()
  ✗ Zero callers of ExecutionGate.check()
  ✗ gateway.py does not import or call event_gate
  ✗ Active execution path does not call human_gate.get_state()

END-TO-END CONNECTION:
  ✗ No active execution path connects all four components
```

### Why Original Plan Cannot Proceed

```
Original Plan Assumption: "Reuse existing Authorization mechanism"
  ↓
Assumption Validation Result: Existing path NOT FOUND / NOT CONNECTED
  ↓
Logical Consequence: Cannot "reuse" something that is not connected
  ↓
Risk of Proceeding Anyway:
  - Code layer would construct NEW path despite "no new scheme" constraint
  - Design assumption would diverge from implementation reality
  - Plan approval would become misaligned with code changes
  ↓
HG Decision B: REVISE SCOPE
  - Accept that existing path cannot be reused
  - Redesign as "new connection path" instead
  - Get re-approval before implementation
```

### Key Principle Maintained

```
NOT FOUND / NOT CONNECTED  ≠  ABSENT

Our Finding:
  "Existing Authorization Path is NOT FOUND in traced active execution flow"
  
We are NOT claiming:
  "Existing Authorization Path does not exist in entire codebase"

Distinction:
  - NOT FOUND: May exist elsewhere, not discovered in this trace
  - ABSENT: Confirmed nonexistent anywhere
  
Governance:
  - We acknowledge the distinction
  - We accept we cannot reuse something we cannot find in active flow
  - We propose to design new rather than continue uncertain search
```

---

## PART 2: REVISED IP-005 PLAN SUMMARY

### New Design: Authorization Connection Path

```
STRUCTURE:

Human Gate (FINAL AUTHORITY)
    ↓
runtime_scope (immutable, HG-approved)
    ↓
authorization.py (decision engine - NEW)
    ↓
Event Store (immutable records)
    ↓
Orchestra (decision respected)
    ↓
HAB (AI socket, NOT authority)
    ↓
AI Provider
```

### Components

**[A] Authorization Source**
```
Component: runtime_scope (existing in governance layer)
Role: Immutable source of authorization decisions
Scope: provider, model, operations, resource_scope, constraints
Initialization: At startup, loaded from governance layer
Updates: Only by Human Gate with explicit decision record
Caching: NOT PERMITTED (queried each request)
```

**[B] Authorization Decision Engine**
```
Component: authorization.py (NEW MODULE - NOT an Authority engine)
Responsibility: Execute exact-match validation against runtime_scope
Input: Orchestra request (provider, model, operation, scope, actor, session_id)
Output: APPROVED / REJECTED / DEFERRED
Logic: Exact match (provider, model, operation, scope) OR REJECTED
Fail-Closed: Missing/mismatch/unavailable source = REJECTED
Authority Designation: Decisions signed as "Human Gate" (via runtime_scope)
Self-Authorization: FORBIDDEN
```

**[C] Event Store Integration**
```
Component: event_gate.process_event() (EXISTING)
Purpose: Immutable persistence of authorization decisions
Event Schema: hab_authorization with approval_status, authority, decision_reason
Signature: trace_id chain for readback verification
Immutability: INSERT enforced, no modification allowed
```

**[D] Orchestra Integration**
```
Connection: In Orchestra dispatcher (gateway.py)
Trigger: After request validation, BEFORE execution
Flow: orchestra_request → authorization.check_hab_approval() → APPROVED/REJECTED
If APPROVED: Proceed to execution
If REJECTED: Block execution, log denial event
```

**[E] HAB Gateway (Unchanged Role)**
```
Role: AI socket layer, request routing
Responsibility: Execute approved operations, capture lineage
NOT Responsibility: Make authorization decisions, override Human Gate
```

### Governance Principles Maintained

```
1. Human Gate is sole authority
   - runtime_scope source: Human Gate
   - Authorization delegation: Via immutable runtime_scope, not re-authorization
   - Override capability: Human Gate only

2. Fail-closed
   - Default decision: DENIED
   - Any error: REJECTED (never implicit approval)
   - Missing component: REJECTED
   
3. No AI self-authorization
   - authorization.py does NOT make decisions (only executes policy)
   - Decision authority always attributed to Human Gate
   - No HAB self-authorization, no JARVIS self-authorization

4. Scope exactness
   - Exact match required: provider, model, operation, scope
   - No scope inference, no completion
   - Mismatch → REJECTED

5. Immutability
   - runtime_scope immutable (HG updates only)
   - Authorization decisions immutable (Event Store)
   - trace_id signatures for verification

6. Boundary preservation
   - IP-007 (lineage) boundary unchanged
   - IP-009 (memory sync) optional, not blocked
   - No schema migrations without HG approval
```

---

## PART 3: AUTHORIZATION CONTRACT (EXISTING vs. PROPOSED)

### EXISTING (Human Gate Governance - NO RE-APPROVAL NEEDED)

```
AUTHORITY:
  = Human Gate (sole authority per MoCKA governance)

SELF-AUTHORIZATION PROHIBITIONS:
  AI_SELF_AUTHORIZATION = FORBIDDEN
  JARVIS_SELF_AUTHORIZATION = FORBIDDEN
  HAB_SELF_AUTHORIZATION = FORBIDDEN
  Orchestra_SELF_AUTHORIZATION = FORBIDDEN

SCOPE_EXPANSION:
  = FORBIDDEN
```

### PROPOSED (For HG Approval - New Authorization Path)

```
AUTHORIZATION REQUIRED = TRUE
  PROPOSED: in new connection path
  CURRENT STATE: NOT VERIFIED in active execution

AUTHORIZATION_SOURCE:
  = runtime_scope (HG-approved, assumed immutable)
  STATUS: PROPOSED / Requires HG confirmation

DECISION:
  = APPROVED / REJECTED / DEFERRED
  STATUS: PROPOSED

DEFAULT:
  = DENIED (fail-closed)
  STATUS: PROPOSED / Requires HG confirmation

SCOPE_MATCH:
  = EXACT MATCH REQUIRED (provider, model, operation, scope)
  STATUS: PROPOSED / Requires HG confirmation

AUTHORITY_RE_VERIFICATION:
  = FORBIDDEN (authority remains Human Gate throughout)
  STATUS: PROPOSED

FAIL_OPEN:
  = FORBIDDEN
  STATUS: PROPOSED

FAIL_CLOSED:
  = REQUIRED (all errors → REJECTED)
  STATUS: PROPOSED / Requires HG confirmation

IMMUTABILITY (PROPOSED - REQUIRES VERIFICATION):
  Event Store decisions immutable
    STATUS: PROPOSED / NOT VERIFIED in current Event Store
    Question: Does current Event Store support immutability?
  
  runtime_scope immutable
    STATUS: PROPOSED / NOT VERIFIED in current governance
    Question: Can runtime_scope be locked during execution?
```

---

## PART 4: SCOPE BINDING (FOR HG CONFIRMATION)

**Question 1: Authorization Source**
```
Is Human Gate confirming that runtime_scope is the authorized source
for Orchestra → HAB authorization decisions?

Answer Required: YES / NO / CONDITIONAL

If CONDITIONAL:
  Please specify what conditions must be met.
```

**Question 2: Exact Scope Matching**
```
Is Human Gate confirming that exact match is required for:
  - provider (must match runtime_scope.provider)
  - model (must match runtime_scope.model)
  - operation (must be in runtime_scope.operations)
  - resource_scope (must match runtime_scope.resource_scope)

Answer Required: YES / NO / PARTIAL

If PARTIAL:
  Please specify which dimensions require exact match.
```

**Question 3: Fail-Closed Default**
```
Is Human Gate confirming that default decision is DENIED?
  - Missing scope → REJECTED
  - Missing event_id → REJECTED
  - Authorization source unavailable → REJECTED
  - Any validation error → REJECTED

Answer Required: YES / NO / CONDITIONAL

If CONDITIONAL:
  Please specify exceptions.
```

**Question 4: Authority Designation**
```
Is Human Gate confirming that all authorization decisions shall be
designated as "Human Gate" authority (via runtime_scope), NOT as a new
authority engine?

Answer Required: YES / NO / CONDITIONAL

If CONDITIONAL:
  Please clarify authority structure.
```

---

## PART 5: HG DECISION REQUIRED (9 EXPLICIT QUESTIONS)

**Human Gate to provide explicit YES/NO/CONDITIONAL on each:**

```
QUESTION 1: Architecture Acceptance
  Is the design change from "reuse existing Authorization path"
  to "design NEW Authorization connection path" accepted?
  
  Answer: YES / NO / CONDITIONAL

QUESTION 2: Human Gate Authority
  Do you confirm that Human Gate remains SOLE AUTHORITY
  in the new Authorization path design?
  (Runtime_scope source, no AI re-authorization, no override by HAB)
  
  Answer: YES / NO / CONDITIONAL

QUESTION 3: runtime_scope as Source of Truth
  Do you approve runtime_scope (HG-initialized, immutable) as the
  SOLE SOURCE OF TRUTH for Authorization decisions?
  
  Answer: YES / NO / CONDITIONAL

QUESTION 4: Fail-Closed Policy
  Do you require that authorization defaults to DENIED when:
  - Scope is missing
  - Scope does not match exactly
  - Authorization source is unavailable
  - Any validation error occurs
  
  Answer: YES / NO / CONDITIONAL

QUESTION 5: Exact Scope Matching
  Do you require EXACT MATCH (not inference/completion) for:
  - provider matches runtime_scope.provider
  - model matches runtime_scope.model
  - operation is in runtime_scope.operations list
  - resource_scope matches runtime_scope.resource_scope
  
  Answer: YES / NO / CONDITIONAL
  If CONDITIONAL: Which dimensions require exact match?

QUESTION 6: Immutability Requirements
  Do you approve these immutability requirements:
  a) runtime_scope cannot be modified during execution
  b) Authorization decision records cannot be modified/deleted
  c) Event Store evidence is permanent
  
  Answer: YES / NO / PARTIAL
  If PARTIAL: Which immutability requirements should be enforced?

QUESTION 7: NEW Authorization Engine
  Do you approve creation of a NEW Authorization Engine (authorization.py)
  as a decision executor (not authority)?
  
  OR do you prefer existing ExecutionGate/Authorization mechanisms
  to be adapted as thin adapter layer?
  
  Answer: NEW ENGINE ACCEPTABLE / REQUEST ADAPTER / OTHER

QUESTION 8: Orchestra → Authorization → HAB Routing
  Do you approve this new connection architecture:
  Orchestra Request
    → Authorization Check
    → runtime_scope validation
    → APPROVED/REJECTED decision
    → Event Store record
    → Orchestra response
    → (if approved) HAB execution
  
  Current state: Orchestra → HAB (NOT CONNECTED to authorization)
  
  Answer: YES / NO / ALTERNATIVE
  If ALTERNATIVE: Propose alternative connection design

QUESTION 9: Approval Separation
  Is "Design Approval" separate from "Implementation Authorization"?
  
  Proposed Sequence:
    Stage 1: DESIGN APPROVAL (you approve architecture design)
    Stage 2: IMPLEMENTATION AUTHORIZATION (you authorize code writing)
  
  Do you want both decisions now, or Stage 1 only?
  
  Answer: BOTH NOW / DESIGN ONLY / STAGED

SUMMARY QUESTIONS:

Q10: Conditions or Modifications?
  Are there additional conditions, modifications, or requirements
  for the revised IP-005 design?
  
  Answer: [free text]
```

---

## PART 6: GOVERNANCE AUDIT RESULTS

**Revised Plan Governance Audit:**

```
AUDIT STATUS: FAIL / REQUIRES HG CLARIFICATION

NOTE: "FAIL" indicates unresolved design items requiring HG judgment,
      NOT a code quality failure or rejected state.
      
      This is the correct gate: design proposals must receive HG approval
      before moving to implementation.

GOVERNANCE FOUNDATIONS (VERIFIED - PASSING):
  [✓] Human Gate remains sole authority
  [✓] No AI self-authorization path
  [✓] No JARVIS self-authorization path
  [✓] No HAB self-authorization path
  [✓] No Orchestra self-authorization path
  [✓] No unauthorized scope expansion
  [✓] MoCKA governance principles maintained
  
BOUNDARIES (VERIFIED - PASSING):
  [✓] IP-007 boundary preserved (not modified)
  [✓] IP-009 not started
  [✓] No schema migrations attempted
  [✓] No production activation
  [✓] No code changes made (design only)

UNRESOLVED DESIGN PROPOSALS (FAILING - REQUIRES HG APPROVAL):
  [?] authorization.py as NEW Authorization Engine
      Status: PROPOSED / Awaiting HG judgment (Q7)
  
  [?] runtime_scope as immutable source of truth
      Status: PROPOSED / Awaiting HG confirmation (Q3)
  
  [?] fail-closed as default behavior
      Status: PROPOSED / Awaiting HG confirmation (Q4)
  
  [?] exact scope matching requirement
      Status: PROPOSED / Awaiting HG confirmation (Q5)
  
  [?] Immutability guarantees
      Status: PROPOSED / NOT VERIFIED in current implementation
      Awaiting HG judgment (Q6)
  
  [?] Event Store integration with authorization
      Status: PROPOSED / Current state NOT CONNECTED
      Awaiting HG judgment (Q8)
  
  [?] Orchestra → Authorization → HAB routing
      Status: PROPOSED / Current state NOT CONNECTED
      Awaiting HG judgment (Q8)

AUDIT CONCLUSION:

  Design Phase: COMPLETE
  Documentation: COMPLETE & READY FOR HG REVIEW
  
  Governance Gate: HOLDING (correctly)
  - Design proposals identified
  - Unresolved items enumerated (7+ items)
  - HG decision questions prepared (9 questions)
  - Ready for HG to provide explicit YES/NO/CONDITIONAL on each
  
  Next Action: Awaiting HG responses to Questions 1-10 (Part 5)
  
CRITICAL PRINCIPLE MAINTAINED:
  "Design proposed" ≠ "Design approved" ≠ "Design implemented"
  
  Current status: Design proposed, awaiting HG approval
  
  Implementation BLOCKED until HG provides explicit approval
  on each unresolved item.
```

---

## PART 7: WHAT HAPPENS NEXT (IF APPROVED)

### Upon HG Re-Approval

```
1. This revised plan becomes the AUTHORIZED SCOPE for IP-005

2. Implementation team receives:
   - Approved design (this document)
   - Implementation authorization
   - Governance constraints (fail-closed, HG authority, etc.)
   - Testing requirements (readback validation)
   
3. Implementation Sequence:
   a. Create authorization.py (decision engine)
   b. Implement scope validation logic
   c. Integrate with event_gate.process_event()
   d. Integrate Orchestra dispatcher → authorization check
   e. Implement fail-closed error handling
   f. Add trace_id signature generation
   g. Create readback validation queries
   
4. Testing:
   - APPROVED request → Event Store record
   - REJECTED request → Event Store denial record
   - Missing scope → REJECTED
   - Authorization unavailable → REJECTED
   - Readback validates approval_status and authority
   
5. Runtime Verification (after implementation):
   - Confirm Event Store immutability
   - Confirm fail-closed behavior
   - Confirm HG authority designation
   - Confirm trace_id signature chain
   
6. IP-009 Consideration:
   - Authorization decisions feed Event Store
   - IP-009 Memory sync is optional (not required)
   - If IP-009 proceeds, authorization events are synced
```

### If Additional Investigation Required

```
If HG wishes to continue searching for existing Authorization Path:
  1. Identify additional code areas to trace
  2. Conduct extended investigation (read-only)
  3. Report findings to HG
  4. Continue with Option A / Option B / Option C decision
```

### If Scope Revisions Needed

```
If HG requires modifications to this design:
  1. Specify required changes
  2. Revise plan accordingly
  3. Conduct self-audit of changes
  4. Resubmit for approval
```

---

## PART 8: GOVERNANCE PRINCIPLE STATEMENT

**MoCKA Governance Maintained:**

```
Evidence
  ↓
Design
  ↓
HG Approval  ← WE ARE HERE (requesting re-approval for revised design)
  ↓
Implementation
  ↓
Static Verification
  ↓
Runtime Authorization
  ↓
Runtime Evidence
  ↓
Actual Consequence
  ↓
Institutional Memory

Current Status:
- Evidence collected (re-investigation audit)
- Design revised (this document)
- Awaiting HG re-approval (next step)
- Implementation blocked until approval
- No code changes until approval received
- No commits until approval received
- No runtime changes until approval received
```

---

## SUMMARY: PROPOSED vs. EXISTING

| Item | Original Plan | Revised Plan | Classification |
|------|---------------|--------------|-----------------|
| Scope | Reuse existing Auth path | Design new Auth path | CHANGED / PROPOSED |
| Authority | Human Gate (assumed) | Human Gate (explicit) | EXISTING PRINCIPLE |
| New Engine | None assumed | authorization.py | PROPOSED / HG DECISION Q7 |
| runtime_scope | Assumed available | Proposed source of truth | PROPOSED / HG DECISION Q3 |
| fail-closed | Yes (assumed) | Yes (explicit contract) | PROPOSED / HG DECISION Q4 |
| exact match | Not specified | Exact match required | PROPOSED / HG DECISION Q5 |
| Immutability | Not specified | Multiple requirements | PROPOSED / HG DECISION Q6 |
| IP-007 Boundary | Preserved | Preserved | UNCHANGED / EXISTING |
| IP-009 Dependency | Soft | Not started | UNCHANGED / NOT STARTED |
| Code Changes | 0 (planned) | 0 (design only) | UNCHANGED |
| Status | Ready to implement | Awaiting HG approval | BLOCKED |

---

## REQUEST TO HUMAN GATE

**Re-Approval Sought For:**

We have completed Plan Revision per HG Decision B.
The revised IP-005 design is ready for HG judgment.

**Critical Clarification:**

HG Decision B approved: "Revise Plan/Scope and seek re-approval"

This decision authorized:
- ✓ Change from "reuse existing" to "design new path"
- ✓ Prepare revised design for HG approval

This decision did NOT authorize:
- ✗ Implementation of new Authorization Engine
- ✗ Implementation of new Authorialization path
- ✗ Any code changes

**We Request HG Decision On:**

1. Design change: From "reuse existing" to "design new path" — ACCEPTABLE?
2. New Authorization Engine — ACCEPTABLE?
3. runtime_scope as authorization source — ACCEPTABLE?
4. Fail-closed policy — ACCEPTABLE?
5. Exact scope matching — ACCEPTABLE?
6. Immutability requirements — ACCEPTABLE?
7. Orchestra → Authorization → HAB routing — ACCEPTABLE?
8. Design vs. Implementation separation — Approve both now or stage?
9. Any conditions or modifications — REQUIRED?

**Reference Documents:**
- Revised Design Plan: PHASE5_0_IMPLEMENTATION_PLAN_005_REVISION_20260929.md
- Audit Findings: IP-005_RE_INVESTIGATION_FINAL_20260929.md
- Original Decision: HG_DESIGN_DECISION_IP-005_20260929.md

---

## STATUS

```
DOCUMENT: HG_RE_APPROVAL_REQUEST_IP-005_20260929.md
DATE: 2026-09-29
AUTHORITY: Human Gate
DECISION REQUIRED: YES (9 explicit questions / Part 5)

GOVERNANCE AUDIT: FAIL / REQUIRES HG CLARIFICATION
  (Correctly identifying that design proposals need HG judgment)

IMPLEMENTATION BLOCKED: YES (pending HG approval of all 9 questions)

CODE CHANGES: 0
COMMITS: 0
RUNTIME: NOT ACTIVATED

DESIGN PHASE: COMPLETE
DESIGN APPROVAL: PENDING HG RESPONSE

READY FOR HG REVIEW
```
