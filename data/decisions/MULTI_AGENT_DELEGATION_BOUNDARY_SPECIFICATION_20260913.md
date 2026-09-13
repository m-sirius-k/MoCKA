# Multi-Agent Delegation Boundary Specification
**2026-09-13**

## Document Control

* Classification: GOVERNANCE / ARCHITECTURE / DESIGN-ONLY
* Authority: KUROKO Protocol (Multi-Agent Design Phase)
* Design Scope: Layer 1-2 (Delegation model, cascading authorization, evidence propagation)
* Implementation Scope: NONE (Design-only; no implementation)
* Record Timestamp: 2026-09-13T15:55:00Z
* Status: DESIGN SPECIFICATION (awaiting Human Gate decision HG-HJ-06)

---

## PART 1: Executive Summary

Multi-agent delegation extends the HAB/JARVIS/MoCKA/Runtime architecture to handle coordination across multiple agents. This specification defines:

1. Delegation patterns (SEQUENTIAL, PARALLEL, CASCADING)
2. Authority isolation between delegated agents
3. Evidence propagation rules
4. Aggregation semantics
5. Failure handling and rollback

**Core Principle**: Each delegated agent operates under same HAB boundary; no agent bypasses authorization or scope verification.

---

## PART 2: Delegation Patterns

### 2.1 SEQUENTIAL Delegation

```
Pattern: One agent executes after another completes successfully

Flow:
  JARVIS → HAB (SCOPE_CONSEQUENCE_BINDING request, agents=[A, B, C])
  HAB → Runtime (execution binding for agent A scope)
  Runtime → Agent_A (execute with binding)
  Agent_A completes
  Runtime → Agent_B (execute with binding)
  Agent_B completes
  ...
  
Authority Isolation:
  [ISO-1] Each agent receives independent execution binding
  [ISO-2] Each binding includes complete evidence lineage (same for all agents)
  [ISO-3] Each agent verifies authorization independently (all tokens same)
  [ISO-4] Failure in Agent_A prevents Agent_B execution (sequential guarantee)

Aggregation:
  Result = Agent_A.result AND Agent_B.result AND ... (all must succeed)
  Failure Mode: If any agent fails, delegation fails immediately
  Rollback: Previous agent results rolled back or isolated (architecture-dependent)
```

### 2.2 PARALLEL Delegation

```
Pattern: Multiple agents execute simultaneously

Flow:
  JARVIS → HAB (SCOPE_CONSEQUENCE_BINDING request, agents=[A, B, C], pattern=PARALLEL)
  HAB → Runtime (execution binding for each agent)
  Runtime → Agent_A, Agent_B, Agent_C (execute in parallel)
  Wait for all to complete (or timeout)
  
Authority Isolation:
  [ISO-1] Each agent receives independent execution binding
  [ISO-2] All bindings signed independently (same token, different request_ids)
  [ISO-3] Each agent verifies authorization independently
  [ISO-4] No agent assumes prior agent success (race condition prevention)

Aggregation (Configurable):
  Option 1: ALL_SUCCESS (all agents must succeed)
    Result = Agent_A AND Agent_B AND Agent_C
    Failure: If any agent fails, delegation fails
  
  Option 2: FIRST_SUCCESS (first agent to succeed wins)
    Result = Agent_A OR Agent_B OR Agent_C
    Failure: All agents must fail to trigger rollback
  
  Option 3: MAJORITY (majority of agents must succeed)
    Result = ⌈(n agents)/2⌉ must succeed
    Failure: If fewer than majority succeed
  
Rollback:
  If delegation fails and aggregation_rule = ALL_SUCCESS:
    Rollback all Agent_X results
  If aggregation_rule = FIRST_SUCCESS or MAJORITY:
    Keep successful agent results; discard failed agent results
```

### 2.3 CASCADING Delegation

```
Pattern: First agent's result informs second agent's execution

Flow:
  JARVIS → HAB (request for Agent_A)
  HAB → Runtime (execution binding for Agent_A)
  Agent_A executes, returns result_A
  
  JARVIS evaluates result_A:
    IF result_A satisfies success_criteria:
      → Coordination complete
    ELSE:
      → Create secondary request for Agent_B (using result_A as context)
  
  HAB → Runtime (execution binding for Agent_B with context=result_A)
  Agent_B executes using context (evidence preserved)
  
Authority Isolation:
  [ISO-1] Agent_A receives binding for its scope
  [ISO-2] Agent_B receives binding for its scope (may be different from A)
  [ISO-3] Both scopes must be verified independently by HAB
  [ISO-4] Context passing must preserve evidence lineage

Aggregation:
  Result = Agent_A result OR (if failed) Agent_B result
  Failure: If both agents fail, delegation fails
  
Evidence Propagation:
  Agent_A result → context parameter → Agent_B binding
  Evidence lineage must be preserved (no inference from context alone)
```

---

## PART 3: Authority Isolation Between Delegated Agents

### 3.1 Independent Authorization Per Agent

```
CONSTRAINT: Each agent must receive independent authorization verification

For SEQUENTIAL Delegation:
  Step 1: HAB receives {agents=[A, B, C], scope_universe=X}
  Step 2: HAB creates execution_binding_A with token_reference
  Step 3: Agent_A executes with binding_A
  Step 4: Runtime verifies token, scope, consequence for Agent_A
  Step 5: Agent_A completes; now proceed to Agent_B
  
  Step 6: HAB creates execution_binding_B with same token_reference
          (but separate binding object; Binding_A ≠ Binding_B)
  Step 7: Runtime verifies token, scope, consequence for Agent_B independently
  Step 8: Agent_B completes; proceed to Agent_C
  
  Guarantee: Agent_B never inherits Agent_A's authorization
            (each binding verified independently)

For PARALLEL Delegation:
  Step 1: HAB receives {agents=[A, B, C], scope_universe=X, pattern=PARALLEL}
  Step 2: HAB creates execution_binding_A (signed, unique binding_id)
  Step 3: HAB creates execution_binding_B (signed, unique binding_id)
  Step 4: HAB creates execution_binding_C (signed, unique binding_id)
  Step 5: All bindings sent to Runtime simultaneously
  Step 6: Runtime verifies each binding independently (race condition safe)
  Step 7: Agents A, B, C execute (may interfere, but authorization verified independently)
  
  Guarantee: No agent can bypass authorization by exploiting parallel execution
```

### 3.2 Scope Isolation Between Delegated Agents

```
RULE: Each agent may operate on different scope subsets

Example:
  Request: {scope_universe=CANDIDATE_A, agents=[Agent_A, Agent_B]}
  HAB_Action:
    - Verify CANDIDATE_A membership for Agent_A's consequence targets
    - Verify CANDIDATE_A membership for Agent_B's consequence targets
    - BOTH operations must pass same scope verification
  
  Rationale: Agents may operate on different Route IDs/Operations,
             but both must be within same verified scope universe

If Agents Need Different Scopes:
  Request: {scope_universes=[CANDIDATE_A, CANDIDATE_B], agents=[Agent_A, Agent_B]}
  HAB_Action:
    - Create two separate binding requests (one per scope universe)
    - Agent_A gets binding for CANDIDATE_A
    - Agent_B gets binding for CANDIDATE_B
    - Each binding independently verified
  
  Guarantee: Scope isolation maintained
```

---

## PART 4: Evidence Propagation Rules

### 4.1 Evidence Lineage Through Delegation

```
ORIGINAL REQUEST:
{
  "evidence_references": ["E15-01", "E15-02"],
  "scope_universe": "CANDIDATE_A"
}

EXECUTION_BINDING (from HAB):
{
  "binding_id": "BIND-20260913-xxxxxxxx",
  "evidence_lineage": {
    "scope_evidence": ["E15-01", "E15-02"],
    "consequence_evidence": ["E15-03"],
    "runtime_validation_evidence": ["E15-01", "E15-02", "E15-03"]
  }
}

PROPAGATION TO AGENT_A:
  Agent_A receives: execution_binding (complete lineage preserved)
  Agent_A action: Execute within scope/consequence/evidence constraints
  Agent_A does NOT: Modify evidence lineage, add new evidence, drop evidence

PROPAGATION TO AGENT_B (Sequential):
  Agent_B receives: execution_binding_B (same evidence lineage as Agent_A)
  Agent_B action: Execute within same scope/consequence/evidence constraints
  Agent_B does NOT: Modify evidence lineage based on Agent_A's context

CASCADING CASE (Context-Based):
  Agent_A executes, returns result_A
  result_A used as context (informational, not evidence)
  Agent_B receives: execution_binding_B + context={result_A}
  Agent_B does NOT infer new evidence from result_A
  Agent_B executes: Same evidence lineage from binding_B (not from result_A)
  
  Rule: Context ≠ Evidence (context is informational; evidence is governance-bound)
```

### 4.2 Evidence Discipline Preserved Through Delegation

```
PRESERVATION RULES:

[P-1] NOT_FOUND ≠ ABSENT (preserved in all agents)
  Rule: If evidence not in binding.evidence_lineage, treat as NOT_FOUND
  Action: All agents respect this (no inference from absence)

[P-2] NOT_PROVEN ≠ REJECTED (preserved in all agents)
  Rule: If consequence not fully proven, not rejected (candidates remain valid)
  Action: All agents continue execution under same Model A binding

[P-3] Evidence Lineage Immutability (preserved in all agents)
  Rule: Evidence_lineage in binding cannot be modified by any agent
  Action: All agents receive same binding; none can rewrite evidence chain

[P-4] Scope Membership Immutability (preserved in all agents)
  Rule: Scope_set in binding cannot be modified mid-delegation
  Action: If delegation needs to change scope, new request+new binding required

VIOLATION DETECTION:
  If any agent attempts to:
    - Add evidence not in binding
    - Remove evidence from lineage
    - Modify scope_set
    - Infer scope from result_A
  Action: Runtime detects violation, rejects atomically (no partial execution)
```

---

## PART 5: Failure Handling & Rollback

### 5.1 Failure Modes

```
FAILURE TYPE 1: Single Agent Fails (Sequential)
  Agent_A executes successfully
  Agent_B fails (returns error or crashes)
  
  Handling:
    [ROLLBACK] If aggregation_rule = ALL_SUCCESS:
      Undo Agent_A results (architecture-dependent)
      Return delegation status = FAILED
    [CONTINUE] If aggregation_rule allows partial success:
      Undo only Agent_B results
      Return delegation status = PARTIAL_SUCCESS

FAILURE TYPE 2: Partial Failure (Parallel)
  Agent_A succeeds, Agent_B fails, Agent_C succeeds
  
  Handling:
    [ROLLBACK] If aggregation_rule = ALL_SUCCESS:
      Undo A and C results
      Return delegation status = FAILED
    [KEEP] If aggregation_rule = MAJORITY (2 of 3 succeeded):
      Keep A and C results; undo only B
      Return delegation status = PARTIAL_SUCCESS (majority satisfied)

FAILURE TYPE 3: Authorization Failure (Any Agent)
  Any agent's execution binding verification fails
  
  Handling:
    [IMMEDIATE_STOP] Stop all delegated agents (cascading halt)
    [ESCALATE] Escalate to MoCKA (authorization failure is governance failure)
    [UNDO] Undo any prior agent results
    Return delegation status = AUTHORIZATION_FAILED

FAILURE TYPE 4: Evidence Lineage Violation (Any Agent)
  Any agent attempts to modify evidence lineage or infer scope
  
  Handling:
    [IMMEDIATE_STOP] Runtime detects violation, stops execution
    [REJECT] Reject entire delegation (atomicity guarantee)
    [ESCALATE] Escalate to MoCKA (governance boundary violation)
    Return delegation status = GOVERNANCE_BOUNDARY_VIOLATION
```

### 5.2 Atomicity Guarantee

```
PRINCIPLE: Delegation is all-or-nothing (except where aggregation rule permits partial)

For aggregation_rule = ALL_SUCCESS:
  If Agent_A succeeds and Agent_B fails:
    Rollback Agent_A (if possible)
    Return status = FAILED (not partial success)
    Undo any side effects
  
  Guarantee: Either all agents succeed and all changes persist,
             or delegation fails and no changes persist

For aggregation_rule = MAJORITY or FIRST_SUCCESS:
  If Agent_A succeeds and Agent_B fails:
    Keep Agent_A changes (success criteria met)
    Undo Agent_B changes
    Return status = PARTIAL_SUCCESS
  
  Guarantee: Once aggregation rule satisfied, those results persist;
             other results rolled back independently
```

---

## PART 6: State Synchronization in Delegation

### 6.1 State Sharing Between Agents

```
ALLOWED (Read-Only State Sharing):
  [SHARE-1] Execution binding (each agent receives copy)
  [SHARE-2] Evidence lineage (immutable reference)
  [SHARE-3] Scope set (immutable reference)
  [SHARE-4] Authorization token ID (for verification only)
  [SHARE-5] Context parameter (in cascading delegation; informational only)

NOT ALLOWED (No State Mutation Sharing):
  [NO-SHARE-1] Agent_A modifying execution_binding for Agent_B
  [NO-SHARE-2] Agent_A injecting new evidence for Agent_B
  [NO-SHARE-3] Agent_A changing scope_set for Agent_B
  [NO-SHARE-4] Agent_A modifying authorization token
  [NO-SHARE-5] Agent_A side-effects affecting Agent_B's verification

ISOLATION MECHANISM:
  Each agent receives independent binding copy
  Binding updates by one agent do not affect other agents
  Runtime verifies each binding independently (copy-on-read semantics)
```

### 6.2 Event Recording for Delegated Execution

```
EVENT RECORDING:

For SEQUENTIAL delegation:
  Event_1: Delegation initiated with {agents=[A, B, C], delegation_id=X}
  Event_2: Agent_A execution binding created (binding_id=B_A)
  Event_3: Agent_A execution successful (result=R_A)
  Event_4: Agent_B execution binding created (binding_id=B_B)
  Event_5: Agent_B execution successful (result=R_B)
  Event_6: Agent_C execution binding created (binding_id=B_C)
  Event_7: Agent_C execution failed (error=E_C)
  Event_8: Delegation rollback initiated (due to aggregation=ALL_SUCCESS)
  Event_9: Delegation complete (status=FAILED)

For PARALLEL delegation:
  Event_1: Delegation initiated with {agents=[A, B, C], pattern=PARALLEL}
  Event_2-4: Three bindings created (B_A, B_B, B_C)
  Event_5-7: Three executions initiated simultaneously
  Event_8: Agent_A completes (success)
  Event_9: Agent_B completes (failure)
  Event_10: Agent_C completes (success)
  Event_11: Aggregation rule applied (MAJORITY → success)
  Event_12: Delegation complete (status=PARTIAL_SUCCESS)

All events recorded to Event Store with:
  - event_id (unique)
  - timestamp
  - delegation_id (reference)
  - agent_id
  - binding_id
  - result or error
  - evidence_lineage (immutable snapshot)
```

---

## PART 7: Multi-Agent Delegation Design Closure Conditions

This specification is complete and sealed when:

1. All delegation patterns specified (PART 2)
2. Authority isolation rules defined (PART 3)
3. Evidence propagation rules documented (PART 4)
4. Evidence discipline preservation confirmed (PART 4.2)
5. Failure handling and rollback specified (PART 5)
6. Atomicity guarantee maintained (PART 5.2)
7. State synchronization rules defined (PART 6)
8. Human Gate decision HG-HJ-06 acceptance pending
9. 20-point integrity verification includes multi-agent constraints
10. No code/schema/database modifications (vectors remain = 0)

---

## FINAL STATUS

**Multi-Agent Delegation Boundary: DESIGN SPECIFICATION PHASE**

```
Patterns: SEQUENTIAL, PARALLEL, CASCADING
Authority: Isolated per agent (no authority inheritance)
Evidence: Propagated immutably (lineage preserved)
Layer: 1-2 (Delegation Model, State Synchronization)
Implementation: NONE (Design-only)
State Locks: ALL MAINTAINED (Implementation NOT_GRANTED, M18-Scope HOLD, Modification Vectors = 0)
```

**Delegation Boundary Sealed: DESIGN SPECIFICATION**
**Authority: KUROKO Protocol (Multi-Agent Design Phase)**
**Human Gate Decision: HG-HJ-06 Pending**

