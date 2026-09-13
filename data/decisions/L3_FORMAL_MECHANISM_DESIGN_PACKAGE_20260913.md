# L3 Formal Mechanism Design Package — Consequence Mechanism Representation

**Date:** 2026-09-13  
**Authority Basis:** HG-R02, HG-R03, HG-R04, HG-R05 (Human Gate Decision Record HG03_CONSEQUENCE_MECHANISM_REASSESSMENT_HG_DECISION_20260913.md)  
**Scope:** Design-only; implementation NOT authorized  
**Classification:** DESIGN / NOT_IMPLEMENTED

---

## PART 1: AUTHORIZATION BASIS

This design package is authorized under Human Gate decisions:

| Decision | Authorization | Constraint |
|----------|----------------|-----------|
| HG-R01 | AUTHORIZE | Use L2 Formal Design as immutable basis |
| HG-R02 | AUTHORIZE WITH CONDITIONS | D1-D6 design-only, no implementation |
| HG-R03 | AUTHORIZE DESIGN | Persistence representation specification, no activation |
| HG-R04 | AUTHORIZE | Authorization->Consequence formal model, no binding |
| HG-R05 | AUTHORIZE BOTH EVIDENCE AND DESIGN | Parallel evidence collection, separate verification |

Design scope: Formal specification of missing mechanism representations (D1-D6).

Non-scope: Implementation, runtime binding, production deployment, M18-Scope inference.

---

## PART 2: DESIGN SCOPE AND CONSTRAINTS

**Scope Boundary:**

```
AUTHORIZED: Formal specification of semantic representations
AUTHORIZED: Design documentation of mechanism relationships
AUTHORIZED: Comparison of persistence strategy candidates
AUTHORIZED: Formal linking of Authorization to Consequence

NOT AUTHORIZED: Code implementation
NOT AUTHORIZED: Schema change
NOT AUTHORIZED: Database modification
NOT AUTHORIZED: Runtime binding
NOT AUTHORIZED: M18-Scope inference
NOT AUTHORIZED: Semantic Closure promotion
```

**Design Assumptions:**

1. L2 Formal Semantics (ActualConsequence, AuthorizedConsequence, CO) are authoritative
2. Layer 3 Design builds on Layer 2 definitions without modification
3. Evidence observations (from concurrent E1-E14 collection) are provided separately
4. Design represents INTENDED mechanism, not IMPLEMENTED state
5. Runtime feasibility is determined by separate Human Gate decision

**Semantic Closure Boundary:**

```
Semantic Closure = NOT_ACHIEVED / LOCKED
This design does NOT change closure status.
Runtime evidence is required for closure promotion.
```

---

## PART 3: L2 SEMANTIC FOUNDATION

*Reference: L2_FORMAL_SEMANTIC_DESIGN_PACKAGE.md*

### ActualConsequence (L2 Definition)

Formal definition from L2:

```
ActualConsequence:
  = consequence that objectively occurred as result of execution
  = observable/measurable state change, side effect, or outcome
  = independent of authorization or observation
  semantic identity = consequence_id (unique per execution)
  temporal semantics = [start_time, end_time, affected_version]
  scope = system components affected
  causality = execution trace to consequence
  persistence = recorded in evidence store (yes/no/partial)
```

**L3 Extension Requirement:**

Layer 3 must formalize:
- How consequence_id is assigned
- How state change is represented
- How causality linkage is captured
- How persistence is achieved

**Layer 3 Must NOT:**
- Redefine consequence_id semantics
- Change scope definition
- Override causality requirements

### AuthorizedConsequence (L2 Definition)

Formal definition from L2:

```
AuthorizedConsequence:
  = consequence explicitly permitted by authorization rule
  = subset of conceivable consequences from authorized action
  semantic identity = authorization_id + consequence_class
  authorization scope = {actions, targets, conditions}
  constraints = limitations on permitted consequences
  expiration = authorization validity window
  supersession = authority for replacement/revocation
  evidence reference = link to authorization decision
  UNKNOWN handling = what if consequence not recognized?
```

**L3 Extension Requirement:**

Layer 3 must formalize:
- How AuthorizedConsequence is instantiated from authorization rule
- How consequence_class is mapped to specific observable consequences
- How constraint enforcement is verified
- How expiration is checked at decision time

**Layer 3 Must NOT:**
- Assume authorization implies consequence automatically occurred
- Override UNKNOWN preservation requirement
- Treat absence of evidence as evidence of authorization

### CO (Consequential Outcome) (L2 Definition)

Formal definition from L2:

```
CO:
  = observable outcome of authorization + consequence + decision context
  = authorization_id + action_id + execution_context + actual_consequence
  + authorized_consequence + verification_status
  temporal semantics = decision_point + execution_time + observation_time
  outcome_type = {AUTHORIZED, PROHIBITED, COLLATERAL, UNKNOWN}
  compliance_status = {COMPLIANT, VIOLATION, UNVERIFIED, UNDECIDABLE}
  evidence_lineage = {authorization_evidence, execution_evidence, observation_evidence}
```

**L3 Extension Requirement:**

Layer 3 must formalize:
- How CO is constructed from its components
- How outcome_type is determined
- How compliance_status is computed
- How evidence_lineage is traced

**Layer 3 Must NOT:**
- Infer outcome_type from incomplete evidence
- Treat UNVERIFIED as COMPLIANT
- Mix decision-time with runtime verification

---

## PART 4: D1 — ACTUALCONSEQUENCE FORMAL REPRESENTATION

### Design Question

How should ActualConsequence (objectively-occurred consequence) be formally represented at Layer 3?

### Semantic Identity

```
ActualConsequence Instance:
  consequence_id           [UUID or sequential identifier]
  execution_id             [link to execution context]
  observation_timestamp    [when consequence was observed]
  state_change_type        [type classification: DATA | STATE | BEHAVIOR | SIDE_EFFECT | EXCEPTION]
  affected_components      [list of system components changed]
  before_state            [pre-change state representation]
  after_state             [post-change state representation]
  state_delta             [minimal representation of change]
  causality_path          [execution trace linking action to consequence]
  scope_membership         [which M18 scope entities affected]
  verification_status     [OBSERVED | INFERRED | HEARSAY | UNKNOWN]
  evidence_references     [pointers to observing evidence]
  persistence_status      [WHERE_STORED | MEMORY_ONLY | NOT_CAPTURED]
```

### Representation Format

**Primary Representation** (canonical form):

```json
{
  "type": "ActualConsequence",
  "consequence_id": "<uuid>",
  "execution_id": "<execution_context_id>",
  "timestamp": "2026-09-13T12:00:00Z",
  "state_change": {
    "type": "<type>",
    "affected_component": "<component_path>",
    "before_value": "<canonical_representation>",
    "after_value": "<canonical_representation>",
    "delta": "<minimal_change_description>"
  },
  "causality": {
    "action_id": "<action_identifier>",
    "execution_trace": ["step1", "step2", ...],
    "root_cause": "<originating_action>"
  },
  "scope": {
    "m18_routes_affected": ["route_id_1", "route_id_2"],
    "m18_paths_affected": ["path_id_1"],
    "scope_membership": {
      "route": "m18_route_xyz",
      "path": "m18_path_abc",
      "moment": "2026-09-13T12:00:00Z"
    }
  },
  "verification": {
    "status": "<OBSERVED|INFERRED|HEARSAY|UNKNOWN>",
    "confidence": "0.0-1.0",
    "observation_evidence": ["<evidence_ref_1>", "<evidence_ref_2>"]
  },
  "persistence": {
    "recorded": true,
    "location": "<persistence_mechanism>",
    "immutable": true,
    "audit_trail": ["write_1", "read_1", ...]
  }
}
```

### What Layer 3 Design Specifies (Not Implements)

1. **Identifier Assignment:**
   - Specification: consequence_id MUST be assigned at observation time
   - Specification: consequence_id MUST be immutable
   - Specification: consequence_id MUST be globally unique per execution
   - **Implementation Decision:** Deferred (UUID vs sequential vs composite)

2. **State Representation:**
   - Specification: before_state and after_state MUST be comparable
   - Specification: delta MUST be minimal sufficient change representation
   - Specification: state representations MUST handle UNKNOWN (partial observation)
   - **Implementation Decision:** Deferred (JSON diff vs custom format vs other)

3. **Causality Linking:**
   - Specification: execution trace MUST link action to consequence
   - Specification: causality MUST be reconstructible from logs
   - Specification: multiple consequences MAY share execution trace segment
   - **Implementation Decision:** Deferred (stack trace vs event correlation vs other)

4. **Persistence Contract:**
   - Specification: ActualConsequence MUST be persisted before CO determination
   - Specification: Persistence MUST be immutable (append-only)
   - Specification: Persistence MUST preserve temporal order
   - **Implementation Decision:** Deferred (which mechanism in Part 9)

5. **Scope Membership:**
   - Specification: ActualConsequence MUST identify affected M18 routes/paths
   - Specification: Scope membership assignment MUST use authoritative M18-Scope
   - Specification: Scope membership is observable fact (not inference)
   - **Implementation Decision:** Deferred (depends on M18-Scope definition)

### Evidence Requirements

For runtime verification of ActualConsequence representation:

- **E1a:** State change evidence (logs, audit trails, snapshots)
- **E1b:** Causality evidence (execution traces, event chains)
- **E1c:** Persistence evidence (where stored, access logs, write proofs)
- **E1d:** Temporal evidence (timestamps, clock synchronization)

---

## PART 5: D2 — AUTHORIZEDCONSEQUENCE FORMAL REPRESENTATION

### Design Question

How should AuthorizedConsequence (consequence explicitly permitted by authorization) be formally represented?

### Semantic Identity

```
AuthorizedConsequence Instance:
  authorization_id         [link to authorizing decision]
  consequence_class        [classification of consequence type]
  permitted_scope          [constraints on where consequence may occur]
  permitted_components     [which system components may be affected]
  forbidden_components     [explicit prohibitions]
  permitted_values         [range of acceptable consequence values]
  temporal_window          [time window within which consequence is authorized]
  expiration_date          [when authorization expires]
  supersession_rule        [how authorization may be replaced/revoked]
  co_reference            [evidence of authorization decision]
  unknown_handling        [how to treat unrecognized consequences]
  consequence_constraints  [additional constraints]
```

### Representation Format

```json
{
  "type": "AuthorizedConsequence",
  "authorization_id": "<authorization_source>",
  "consequence_class": "<type_classification>",
  "scope": {
    "permitted_targets": ["target_1", "target_2"],
    "permitted_components": ["comp_1", "comp_2"],
    "forbidden_components": ["restricted_comp"],
    "scope_constraints": {
      "route": "m18_route_xyz",
      "path": "m18_path_abc",
      "moment_range": ["2026-09-13T00:00:00Z", "2026-09-14T00:00:00Z"]
    }
  },
  "constraints": {
    "value_range": {
      "min": "<minimum>",
      "max": "<maximum>"
    },
    "state_transition": "from->to",
    "side_effects": "permitted|prohibited|unknown",
    "exceptions": ["exception_1", "exception_2"]
  },
  "authorization": {
    "source_decision": "<decision_id>",
    "authority": "<authority_id>",
    "rationale": "<why_this_consequence_is_authorized>",
    "conditions": ["condition_1", "condition_2"]
  },
  "lifecycle": {
    "effective_from": "2026-09-13T00:00:00Z",
    "expires_at": "2026-10-13T00:00:00Z",
    "superseded_by": null,
    "revocation": null
  },
  "unknown_handling": {
    "if_consequence_unrecognized": "REJECT|ESCALATE|DEFER",
    "if_consequence_partial": "ACCEPT_PARTIAL|REQUIRE_COMPLETE",
    "if_consequence_missing": "OK|ERROR"
  }
}
```

### What Layer 3 Design Specifies (Not Implements)

1. **Consequence Class Mapping:**
   - Specification: consequence_class MUST map to observable consequence types
   - Specification: Mapping MUST be reversible (class -> instance and instance -> class)
   - Specification: UNKNOWN consequences MUST be handled per unknown_handling rule
   - **Implementation Decision:** Deferred (taxonomy definition)

2. **Scope Binding:**
   - Specification: AuthorizedConsequence scope MUST constrain ActualConsequence observation scope
   - Specification: permitted_components MUST reference M18 route/path entities
   - Specification: forbidden_components MUST create hard constraints
   - **Implementation Decision:** Deferred (enforcement mechanism)

3. **Constraint Verification:**
   - Specification: Constraints MUST be verifiable against ActualConsequence
   - Specification: value_range constraints MUST have defined comparison operators
   - Specification: state_transition constraints MUST specify exact allowed transitions
   - **Implementation Decision:** Deferred (evaluation framework)

4. **Authorization Evidence:**
   - Specification: AuthorizedConsequence MUST reference authorizing decision
   - Specification: Authorization chain MUST be traceable to governance record
   - Specification: Authorization MUST specify "unknown handling" explicitly
   - **Implementation Decision:** Deferred (evidence storage)

5. **Lifecycle Management:**
   - Specification: Expiration MUST be checked at runtime (not at design)
   - Specification: Supersession MUST be recorded before revocation takes effect
   - Specification: Historical authorization states MUST remain queryable
   - **Implementation Decision:** Deferred (versioning scheme)

### Evidence Requirements

For runtime verification of AuthorizedConsequence representation:

- **E2a:** Authorization decision evidence (governance records)
- **E2b:** Constraint definition evidence (specifications, tests)
- **E2c:** Supersession/revocation evidence (change records)
- **E2d:** Unknown handling verification (test cases, decision logic)

---

## PART 6: D3 — CO FORMAL REPRESENTATION

### Design Question

How should CO (Consequential Outcome: auth + action + actual consequence) be formally represented?

### Semantic Identity

```
CO Instance:
  co_id                    [unique identifier]
  authorization_id         [which authorization led to this]
  action_id                [which action was taken]
  execution_context        [when/where action executed]
  actual_consequence_id    [which consequence actually occurred]
  authorized_consequence_id [which consequence was authorized]
  outcome_type            [AUTHORIZED|PROHIBITED|COLLATERAL|UNKNOWN]
  compliance_status       [COMPLIANT|VIOLATION|UNVERIFIED|UNDECIDABLE]
  authorization_evidence  [evidence of authorization decision]
  execution_evidence      [evidence action was taken]
  consequence_evidence    [evidence consequence occurred]
  evidence_completeness   [COMPLETE|PARTIAL|MINIMAL|UNKNOWN]
  temporal_semantics      [{decision_time, execution_time, observation_time}]
  scope_moment            [M18-Scope state at CO determination time]
```

### Representation Format

```json
{
  "type": "CO",
  "co_id": "<uuid>",
  "components": {
    "authorization_id": "<auth_ref>",
    "action_id": "<action_ref>",
    "execution_id": "<exec_ref>",
    "actual_consequence_id": "<actual_cons_ref>",
    "authorized_consequence_id": "<auth_cons_ref>"
  },
  "outcome": {
    "type": "AUTHORIZED|PROHIBITED|COLLATERAL|UNKNOWN",
    "compliance": "COMPLIANT|VIOLATION|UNVERIFIED|UNDECIDABLE",
    "reason": "<explanation_of_outcome>",
    "decision_time": "2026-09-13T12:00:00Z",
    "decision_confidence": "0.0-1.0"
  },
  "evidence_chain": {
    "authorization_evidence": {
      "source": "<evidence_id>",
      "status": "VERIFIED|ASSUMED|INFERRED|MISSING"
    },
    "execution_evidence": {
      "source": "<evidence_id>",
      "status": "VERIFIED|ASSUMED|INFERRED|MISSING"
    },
    "consequence_evidence": {
      "source": "<evidence_id>",
      "status": "VERIFIED|ASSUMED|INFERRED|MISSING"
    },
    "completeness": "COMPLETE|PARTIAL|MINIMAL|UNKNOWN"
  },
  "temporal": {
    "authorization_time": "2026-09-13T10:00:00Z",
    "execution_time": "2026-09-13T11:30:00Z",
    "observation_time": "2026-09-13T12:00:00Z",
    "co_determination_time": "2026-09-13T12:05:00Z"
  },
  "scope": {
    "m18_scope_at_decision": "<scope_id>",
    "m18_routes_involved": ["route_1"],
    "m18_paths_involved": ["path_1"]
  }
}
```

### What Layer 3 Design Specifies (Not Implements)

1. **CO Identification:**
   - Specification: CO_id MUST uniquely identify authorization + consequence pair
   - Specification: CO_id MUST enable reverse lookup (which authorizations led to this consequence?)
   - Specification: CO construction MUST be deterministic from components
   - **Implementation Decision:** Deferred (composite vs generated)

2. **Outcome Type Determination:**
   - Specification: outcome_type MUST be determined from 3-way comparison (auth | actual | constraint)
   - Specification: PROHIBITED requires enforcement evidence (attempted but blocked)
   - Specification: COLLATERAL requires evidence consequence not in authorized set
   - Specification: UNKNOWN requires evidence of missing information
   - **Implementation Decision:** Deferred (decision algorithm)

3. **Compliance Status Computation:**
   - Specification: COMPLIANT = (actual consequence in authorized set AND within constraints)
   - Specification: VIOLATION = (actual consequence outside authorized set OR violates constraints)
   - Specification: UNVERIFIED = (evidence insufficient to determine)
   - Specification: UNDECIDABLE = (evidence contradictory or incompletely observed)
   - **Implementation Decision:** Deferred (computation framework)

4. **Evidence Chain Integrity:**
   - Specification: CO MUST reference all three evidence types (auth, execution, consequence)
   - Specification: Missing evidence MUST be explicitly recorded (not assumed)
   - Specification: Completeness assessment MUST account for temporal gaps
   - **Implementation Decision:** Deferred (lineage tracking mechanism)

5. **Temporal Ordering:**
   - Specification: decision_time >= authorization_time
   - Specification: execution_time >= authorization_time
   - Specification: observation_time >= execution_time
   - Specification: co_determination_time >= observation_time
   - **Implementation Decision:** Deferred (clock skew handling)

### Evidence Requirements

For runtime verification of CO representation:

- **E3a:** CO construction evidence (how components linked)
- **E3b:** Outcome type determination evidence (decision logic applied)
- **E3c:** Compliance status evidence (constraints evaluated)
- **E3d:** Evidence chain completeness (what information was available at decision time)

---

## PART 7: D4 — CONSEQUENCE CAPTURE MECHANISM

### Design Question

How should the logical chain from execution action to persisted evidence be formally represented?

### Execution Chain Specification

```
Execution -> Action Result -> State Change -> Consequence Detection ->
Consequence Capture -> Representation -> Persistence -> Evidence
```

### Chain Edge Design

**Edge 1: Execution -> Action Result**

```
Input:  Execution context (what code ran)
Output: Action result (return value, side effects, state changes)

Specification:
  - Action result MUST capture all observable effects
  - Action result MUST preserve execution context (stack, variables)
  - Action result includes {return_value, state_modifications, exceptions}
  - Implementation: Deferred (instrumentation strategy)
```

**Edge 2: Action Result -> State Change**

```
Input:  Action result
Output: Atomic state change (before/after)

Specification:
  - State change MUST be observable from data store
  - State change MUST preserve causality (execution -> state)
  - State change includes {component, before, after, delta}
  - Implementation: Deferred (observation mechanism)
```

**Edge 3: State Change -> Consequence Detection**

```
Input:  State change observation
Output: Identified consequence (recognized as meaningful)

Specification:
  - Detection MUST classify state change as consequence type
  - Detection MUST link to authorization context
  - Detection includes {state_change_id, consequence_class, confidence}
  - Implementation: Deferred (classification framework)
```

**Edge 4: Consequence Detection -> Consequence Capture**

```
Input:  Detected consequence
Output: Captured consequence record

Specification:
  - Capture MUST create ActualConsequence representation
  - Capture MUST assign consequence_id
  - Capture MUST record temporal markers
  - Implementation: Deferred (representation mechanism)
```

**Edge 5: Consequence Capture -> Representation**

```
Input:  Consequence capture
Output: Formal representation (per Part 4: D1)

Specification:
  - Representation MUST be queryable
  - Representation MUST be immutable
  - Representation MUST preserve evidence lineage
  - Implementation: Deferred (format and storage)
```

**Edge 6: Representation -> Persistence**

```
Input:  Formal representation
Output: Persisted evidence record

Specification:
  - Persistence MUST be append-only
  - Persistence MUST be durable (survives restart)
  - Persistence MUST be queryable (by any field)
  - Implementation: Deferred (persistence mechanism, see Part 9)
```

**Edge 7: Persistence -> Evidence**

```
Input:  Persisted record
Output: Queryable evidence (available for CO determination)

Specification:
  - Evidence MUST be retrievable with minimal latency
  - Evidence MUST include source timestamp
  - Evidence MUST include audit trail (who accessed it)
  - Implementation: Deferred (query framework)
```

### Failure State Design

For each edge, Layer 3 specifies failure handling (not implements):

```
Edge 1 failure: Action raises exception
  Specification: Exception MUST be captured in Action result
  Specification: State may be partially modified (rollback policy TBD)

Edge 2 failure: State change not observable
  Specification: MISSING consequence marker placed in record
  Specification: Request for human review / manual capture

Edge 3 failure: Consequence not recognized
  Specification: State change marked as UNKNOWN consequence type
  Specification: Escalation for review

Edge 4 failure: Capture mechanism fails
  Specification: CAPTURE_FAILURE recorded in evidence
  Specification: Manual recovery procedure activated

Edge 5 failure: Representation fails
  Specification: Fallback to raw capture (unstructured record)
  Specification: Consistency check needed at query time

Edge 6 failure: Persistence fails
  Specification: Fallback to in-memory queue
  Specification: Async retry with exponential backoff
  Specification: Incident escalation if queue exceeds limit

Edge 7 failure: Evidence unavailable at query time
  Specification: CO determination uses MISSING evidence marker
  Specification: Outcome = UNVERIFIED (not UNDECIDABLE)
```

### UNKNOWN State Design

For each edge, Layer 3 specifies UNKNOWN handling:

```
Edge 1 UNKNOWN: Action result uncertain (exception swallowed?)
  Specification: Query logs for evidence
  Specification: Mark as ASSUMED if inferred

Edge 2 UNKNOWN: State change timing uncertain
  Specification: Use last observed state or temporal window
  Specification: Mark completeness as PARTIAL

Edge 3 UNKNOWN: Consequence type unclassified
  Specification: Create UNKNOWN consequence class
  Specification: Flag for governance review

Edge 4-7 UNKNOWN: Handled per chain edge specifications above
```

### Evidence Requirements

For runtime verification of Consequence Capture mechanism:

- **E4a:** Action result capture (instrumentation evidence)
- **E4b:** State change observation (audit log evidence)
- **E4c:** Consequence detection (classification logs)
- **E4d:** Capture mechanism execution (invocation logs)
- **E4e:** Persistence proof (write logs, checksums)

---

## PART 8: D5 — AUTHORIZATION TO CONSEQUENCE FORMAL BINDING

### Design Question

How should the formal relationship from Authorization decision -> Consequence -> CO be designed?

### Binding Chain Specification

```
Authorization Decision
  |
  v
Authorization Scope (which actions, targets, conditions)
  |
  v
AuthorizedConsequence (which consequences are permitted)
  |
  v
Action (execute within authorized scope)
  |
  v
ActualConsequence (consequence objectively occurs)
  |
  v
CO (determination: is actual consequence authorized?)
  |
  v
Evidence Record (recorded with full lineage)
```

### Binding Semantics

**Part A: Authorization -> Scope Binding**

```json
{
  "authorization": {
    "id": "<auth_id>",
    "decision_id": "<decision_ref>",
    "authority": "<authority_id>"
  },
  "scope": {
    "permitted_actions": ["action_1", "action_2"],
    "permitted_targets": ["target_1"],
    "conditions": ["condition_1"],
    "constraints": {
      "time_window": ["2026-09-13T00:00:00Z", "2026-09-14T00:00:00Z"],
      "rate_limit": "N per minute",
      "retry_limit": "M retries"
    }
  },
  "correlation_id": "<auth_instance_id>"
}
```

**Part B: Scope -> AuthorizedConsequence Binding**

```json
{
  "scope_id": "<scope_ref>",
  "authorized_consequences": [
    {
      "consequence_class": "DATA_MODIFICATION",
      "affected_entity": "entity_1",
      "constraints": {
        "value_range": ["min", "max"],
        "state_transition": "from->to"
      }
    }
  ],
  "consequence_correlation_id": "<consequence_instance_id>"
}
```

**Part C: AuthorizedConsequence -> Action Binding**

```json
{
  "authorized_consequence_id": "<auth_cons_ref>",
  "action": {
    "action_id": "<action_id>",
    "execution_context": "<exec_ref>",
    "performed_by": "<actor_id>",
    "timestamp": "2026-09-13T12:00:00Z"
  },
  "binding_status": "LINKED|INFERRED|PARTIAL|UNKNOWN"
}
```

**Part D: Action -> ActualConsequence Binding**

```json
{
  "action_id": "<action_ref>",
  "actual_consequences": [
    {
      "consequence_id": "<actual_cons_ref>",
      "causality_confidence": "0.0-1.0",
      "execution_evidence": "<evidence_ref>"
    }
  ],
  "causality_binding_status": "DIRECT|INDIRECT|PROBABILISTIC|UNKNOWN"
}
```

**Part E: ActualConsequence -> CO Binding**

```json
{
  "actual_consequence_id": "<actual_cons_ref>",
  "authorized_consequence_id": "<auth_cons_ref>",
  "comparison_result": {
    "matches_class": true|false,
    "within_constraints": true|false,
    "temporal_valid": true|false,
    "scope_valid": true|false
  },
  "outcome_type": "AUTHORIZED|PROHIBITED|COLLATERAL|UNKNOWN",
  "compliance_status": "COMPLIANT|VIOLATION|UNVERIFIED|UNDECIDABLE"
}
```

### Binding Verification Preconditions

For each binding step, Layer 3 specifies verification requirements:

```
Binding Step 1 Verification:
  Required Evidence:
    - Authorization decision recorded
    - Scope definition available
    - Authority legitimacy verifiable
  Failure Handling: MISSING -> CO = UNVERIFIED

Binding Step 2 Verification:
  Required Evidence:
    - AuthorizedConsequence instances linked to scope
    - Consequence constraints documented
    - Conflict resolution rules defined
  Failure Handling: CONFLICTING -> CO = UNDECIDABLE

Binding Step 3 Verification:
  Required Evidence:
    - Action performed (execution logs)
    - Action within authorized scope
    - Scope validity at action time
  Failure Handling: OUT_OF_SCOPE -> CO = VIOLATION

Binding Step 4 Verification:
  Required Evidence:
    - ActualConsequence detected and recorded
    - Causality path from action to consequence
    - Consequence captured before observation delay
  Failure Handling: NO_CAUSALITY -> CO = COLLATERAL

Binding Step 5 Verification:
  Required Evidence:
    - All constraints evaluated
    - Evaluation order deterministic
    - Evaluation time recorded
  Failure Handling: UNEVALUATED -> CO = UNVERIFIED
```

### Binding Identifier Specification

Layer 3 specifies (not implements) what identifiers enable binding:

```
Possible Correlation Identifiers:
  1. Explicit: CO contains {auth_id, action_id, cons_id}
  2. Implicit: CO computed from components at query time
  3. Reference: CO linked via event_id or timestamp correlation
  4. Composite: CO uses multi-level key (route+path+moment+cons_class)

Design Requirement:
  - Binding MUST be reversible (forward and backward queries)
  - Binding MUST handle temporal gaps (async event systems)
  - Binding MUST account for multiple consequences per action
  - Binding MUST NOT assume deterministic ordering
```

### Evidence Requirements

For runtime verification of Authorization->Consequence binding:

- **E5a:** Authorization decision evidence (governance records)
- **E5b:** Scope binding evidence (action logs)
- **E5c:** Consequence detection evidence (observation logs)
- **E5d:** Correlation evidence (how binding was established)
- **E5e:** Binding verification evidence (evaluation results)

---

## PART 9: D6 — CONSEQUENCE PROPAGATION MODEL

### Design Question

How should the multi-stage propagation of consequences through system components be formally represented?

### Propagation Chain Specification

*From HG-03 Investigation Report, E6 Consequence Propagation findings:*

```
Chain Incomplete (3 of 6 edges NOT_FOUND):

Stage 1: Direct Execution Consequence
  Edge 1: Authorization -> Action VERIFIED
  Result: ActualConsequence_1 (e.g., database record created)

Stage 2: Governance Layer Consequence
  Edge 2: ActualConsequence_1 -> GL7 Binding PARTIAL (design exists, runtime NOT_FOUND)
  Result: ActualConsequence_2 (e.g., dry-run check performed)

Stage 3: Relay Propagation
  Edge 3: ActualConsequence_2 -> Relay Notification NOT_FOUND
  Result: ActualConsequence_3 (would be: external system notified)

Stage 4: Orchestra Consequence
  Edge 4: ActualConsequence_3 -> Orchestra Action NOT_FOUND
  Result: ActualConsequence_4 (would be: distributed state synced)

Stage 5: Evidence Aggregation
  Edge 5: ActualConsequence_4 -> Evidence Recording PARTIAL (in-memory only)
  Result: ActualConsequence_5 (e.g., event recorded in memory)

Stage 6: Decision Propagation
  Edge 6: ActualConsequence_5 -> Decision Record NOT_FOUND
  Result: ActualConsequence_6 (would be: governance decision recorded)
```

### Missing Edge Specification (Design-Only)

**Edge 3: ActualConsequence_2 -> Relay Notification**

```
Layer 3 Design Specification (not implementation):

Required Mechanism:
  - Detect ActualConsequence_2 (GL7 check executed)
  - Match consequence type to Relay trigger conditions
  - Format consequence data for Relay API
  - Send notification with correlation_id
  - Record send attempt (success/failure/unknown)

Formal Specification:
  Input: ActualConsequence_2 {
    consequence_id, execution_id, state_change, verification_status
  }
  
  Processing:
    1. Query: Is this consequence type Relay-relevant?
       -> If NO: Edge 3 result = SKIPPED
       -> If YES: Continue to step 2
    
    2. Extract: Consequence data for Relay
       -> target_system: "relay"
       -> event_type: <consequence_class>
       -> payload: <consequence representation>
       -> correlation_id: <auth_id or cons_id>
    
    3. Invoke: Relay notification
       -> Method: POST /relay/notify (hypothetical)
       -> Payload: {event_type, payload, correlation_id, timestamp}
       -> Expected result: {success|failure|timeout}
    
    4. Record: Propagation attempt
       -> Outcome: NOTIFIED | FAILED | TIMEOUT | SKIPPED
       -> Timestamp: when attempt made
       -> Evidence: receipt confirmation (if any)
    
    5. Return: ActualConsequence_3 (if successful)
       -> Type: RELAY_NOTIFICATION_SENT
       -> Status: VERIFIED | ASSUMED (depending on receipt)

Failure Handling:
  - TIMEOUT: Retry with exponential backoff
  - FAILED: Log failure, mark as PROPAGATION_BLOCKED
  - UNKNOWN: Log uncertainty, require manual review

Unknown Handling:
  - If target system (Relay) unavailable: PROPAGATION_SUSPENDED
  - If payload format uncertain: PROPAGATION_DEFERRED
  - If correlation uncertain: PROPAGATION_UNVERIFIED
```

**Edge 6: ActualConsequence_5 -> Decision Record**

```
Layer 3 Design Specification (not implementation):

Required Mechanism:
  - Detect ActualConsequence_5 (evidence recorded)
  - Determine CO (authorization compliance check)
  - If CO outcome is VIOLATION or significant: Trigger decision record
  - Format CO with full evidence lineage
  - Write decision record (immutable append)
  - Return pointer to decision record

Formal Specification:
  Input: ActualConsequence_5 {
    consequence_id, authorization_id, outcome_type, evidence_chain
  }
  
  Processing:
    1. Determine CO outcome (see Part 6 computation)
       -> outcome_type: COMPLIANT | VIOLATION | ...
       -> compliance_status: COMPLIANT | VIOLATION | UNVERIFIED | ...
    
    2. Evaluate: Should this CO be recorded in decision ledger?
       -> Rule: All VIOLATIONs -> Record
       -> Rule: All UNDECIDABLEs -> Record
       -> Rule: Sample of COMPLIANT cases -> Record (audit trail)
       -> Result: RECORD | SKIP
    
    3. Format: CO record with full lineage
       -> co_id: <uuid>
       -> authorization_id: <ref>
       -> actual_consequence_id: <ref>
       -> outcome: <outcome_type>
       -> compliance: <compliance_status>
       -> evidence: {auth_evidence, exec_evidence, cons_evidence}
       -> timestamp: <when_recorded>
    
    4. Write: Decision record (immutable append)
       -> Target: Decision Ledger (or equivalent)
       -> Operation: APPEND (never UPDATE/DELETE)
       -> Durability: Must survive restart
       -> Auditability: Write timestamp, writer ID, checksum
    
    5. Return: ActualConsequence_6 (decision recorded)
       -> Type: DECISION_RECORD_WRITTEN
       -> Status: VERIFIED (write succeeded) or FAILED
       -> Reference: decision_ledger_entry_id

Failure Handling:
  - LEDGER_UNAVAILABLE: Queue in memory, retry async
  - WRITE_FAILED: Escalate incident, mark as DECISION_LOST
  - VALIDATION_FAILED: Record with note, mark as DECISION_INCOMPLETE

Unknown Handling:
  - If outcome undecidable: Record with UNDECIDABLE status
  - If evidence incomplete: Record with evidence_status=PARTIAL
  - If timestamp uncertain: Use system clock, mark as CLOCK_UNCERTAIN
```

### Propagation Chain Representation

```json
{
  "propagation_chain": {
    "chain_id": "<uuid>",
    "root_authorization": "<auth_id>",
    "root_action": "<action_id>",
    "stages": [
      {
        "stage_number": 1,
        "name": "Direct Execution Consequence",
        "input": "Authorization",
        "output": "ActualConsequence_1",
        "edge_status": "VERIFIED",
        "evidence": "<evidence_ref>"
      },
      {
        "stage_number": 2,
        "name": "Governance Layer Consequence",
        "input": "ActualConsequence_1",
        "output": "ActualConsequence_2",
        "edge_status": "PARTIAL",
        "evidence": "design_exists, runtime_not_found"
      },
      {
        "stage_number": 3,
        "name": "Relay Propagation",
        "input": "ActualConsequence_2",
        "output": "ActualConsequence_3",
        "edge_status": "NOT_FOUND",
        "design_specification": "<ref_to_edge3_design>",
        "evidence": "not_implemented"
      },
      {
        "stage_number": 4,
        "name": "Orchestra Consequence",
        "input": "ActualConsequence_3",
        "output": "ActualConsequence_4",
        "edge_status": "NOT_FOUND",
        "evidence": "not_implemented"
      },
      {
        "stage_number": 5,
        "name": "Evidence Aggregation",
        "input": "ActualConsequence_4",
        "output": "ActualConsequence_5",
        "edge_status": "PARTIAL",
        "evidence": "in_memory_only"
      },
      {
        "stage_number": 6,
        "name": "Decision Propagation",
        "input": "ActualConsequence_5",
        "output": "ActualConsequence_6",
        "edge_status": "NOT_FOUND",
        "design_specification": "<ref_to_edge6_design>",
        "evidence": "not_implemented"
      }
    ]
  }
}
```

### Evidence Requirements

For runtime verification of Consequence Propagation:

- **E6a:** Edge 1-2 evidence (direct + GL7 execution)
- **E6b:** Edge 3 evidence (Relay integration)
- **E6c:** Edge 4 evidence (Orchestra syncing)
- **E6d:** Edge 5 evidence (memory recording)
- **E6e:** Edge 6 evidence (decision ledger)

---

## PART 10: PERSISTENCE REPRESENTATION SPECIFICATION

### Design Question

How should consequence evidence be persisted for durable, immutable, queryable storage?

### Persistence Strategy Candidates (Design Comparison)

**Candidate A: Event Store Pattern**

```
Characteristics:
  - Append-only log of all consequences
  - Immutable writes, read-only historical access
  - Queryable by timestamp, consequence_id, authorization_id
  - Supports temporal reconstruction (replay)
  - Supports audit trail (all access logged)

Advantages:
  + Immutability guaranteed by design
  + Temporal integrity (causality preserved)
  + Full audit trail possible
  + Supports replayability
  + Failure resilience (durable append)

Disadvantages:
  - Query performance (may require indexing)
  - Storage efficiency (no compression)
  - Correlation complexity (manual linking required)
  - Schema evolution (versioning required)

Traceability: FULL (every write recorded)
Immutability: GUARANTEED (append-only)
Temporal Integrity: EXCELLENT
Correlation: MANUAL
Auditability: EXCELLENT
UNKNOWN Preservation: YES (explicit NOT_FOUND markers)
Replayability: YES
Failure Handling: QUEUE+RETRY
```

**Candidate B: Decision Ledger Pattern**

```
Characteristics:
  - Structured decision records with evidence references
  - Each record links authorization, consequence, CO, outcome
  - References point to external evidence (event logs, etc.)
  - Queryable by decision_id, outcome_type, compliance_status
  - Supports governance review and audit

Advantages:
  + Decision-centric structure
  + Clear compliance tracking
  + Governance-friendly format
  + Supports escalation workflow
  + Outcome summary queryable

Disadvantages:
  - Requires external evidence storage (not self-contained)
  - Reference integrity risk (dangling references)
  - No native temporal reconstruction
  - Requires reconciliation with source evidence

Traceability: PARTIAL (references external evidence)
Immutability: APPEND-ONLY (ledger itself immutable)
Temporal Integrity: DEPENDENT (on source evidence integrity)
Correlation: DIRECT (explicit links)
Auditability: GOOD (decisions logged)
UNKNOWN Preservation: YES (explicit status fields)
Replayability: CONDITIONAL (depends on external source)
Failure Handling: QUEUE+RETRY
```

**Candidate C: Relational Representation**

```
Characteristics:
  - Normalized schema with tables for consequences, authorizations, COs
  - ACID transactions for consistency
  - SQL queryable
  - Index support for performance

Advantages:
  + Query performance (indexed)
  + Normalized storage (no duplication)
  + Transaction support
  + Flexible querying
  + Standard tooling (SQL)

Disadvantages:
  - Immutability requires application-level enforcement
  - Temporal integrity requires versioning tables
  - Schema changes require migrations
  - Update/delete risk (requires careful controls)

Traceability: APPLICATION-DEPENDENT
Immutability: APPLICATION-ENFORCED (not guaranteed)
Temporal Integrity: VERSIONING-REQUIRED
Correlation: FOREIGN KEY
Auditability: AUDIT TRIGGER REQUIRED
UNKNOWN Preservation: CAREFUL HANDLING REQUIRED
Replayability: VERSION TABLE REQUIRED
Failure Handling: TRANSACTION ROLLBACK
```

**Candidate D: Hybrid Representation**

```
Characteristics:
  - Event Store for primary consequence records (append-only)
  - Decision Ledger for CO summaries (references to event store)
  - Relational views for query performance (materialized views)
  - Periodic snapshots for fast recovery

Advantages:
  + Combines immutability + queryability + performance
  + Event source truth, ledger for summaries
  + View supports complex queries
  + Snapshots enable fast recovery

Disadvantages:
  - Complexity (multiple systems to coordinate)
  - Consistency challenges (view staleness)
  - Schema changes propagate across layers
  - Failure recovery complex

Traceability: MULTI-LAYER (events + ledger + views)
Immutability: GUARANTEED (event core immutable)
Temporal Integrity: EXCELLENT (event order preserved)
Correlation: DIRECT + INDEXED
Auditability: EXCELLENT (all layers auditable)
UNKNOWN Preservation: YES (events preserve uncertainty)
Replayability: YES (event core enables replay)
Failure Handling: GRACEFUL DEGRADATION
```

### Layer 3 Design Decision (Not Implementation)

**Specification for Persistence Layer:**

```
Persistence MUST satisfy:
  1. Immutability: Once written, consequences cannot be modified
     Mechanism: TBD (append-only vs versioning vs cryptographic)
  
  2. Durability: Consequences survive system restart
     Mechanism: TBD (DB commit vs fsync vs replication)
  
  3. Queryability: Consequences retrievable by {consequence_id, authorization_id, outcome_type, timestamp}
     Mechanism: TBD (index strategy, schema design)
  
  4. Correlation: Authorization -> Consequence linking preserved
     Mechanism: TBD (foreign key vs explicit ID vs inference)
  
  5. Auditability: All access to consequences logged
     Mechanism: TBD (database audit log vs application log)
  
  6. UNKNOWN Preservation: Missing/partial evidence explicitly marked
     Mechanism: TBD (nullable fields vs sentinel values vs status codes)
  
  7. Replayability: Consequences can be re-evaluated from state
     Mechanism: TBD (event replay vs snapshot + deltas)
  
  8. Failure Resilience: Failed writes don't lose data
     Mechanism: TBD (queue + retry vs eventual consistency)

Implementation Preconditions (deferred to future phase):
  - Choose persistence candidate (A/B/C/D)
  - Define schema (if relational) or format (if event store)
  - Implement immutability controls
  - Implement query indexes
  - Implement audit logging
  - Implement failure handling
  - Implement consistency checks
```

---

## PART 11: EVIDENCE CONTRACT

### Definition

The "Evidence Contract" specifies what evidence must be produced and preserved to validate each component of the Consequence Mechanism design.

### Evidence Requirements by Design Component

**For D1 (ActualConsequence Representation):**

```
Required Evidence:
  E1a: State change evidence
    - Log entries showing before/after state
    - Audit trail of modifications
    - Checksums or content hashes
    - Required precision: Sufficient to reconstruct state

  E1b: Causality evidence
    - Execution trace (call stack, event sequence)
    - Thread/process ID linking action to effect
    - Temporal markers (monotonic ordering)
    - Required precision: Sufficient to establish causation

  E1c: Persistence evidence
    - Write confirmation (DB ACK, log flush)
    - Storage location (which persistence layer)
    - Immutability proof (read-back verification)
    - Required precision: Sufficient to verify durability

  E1d: Temporal evidence
    - Synchronized timestamps
    - Clock skew bounds
    - Temporal ordering verification
    - Required precision: Microsecond+ accuracy
```

**For D2 (AuthorizedConsequence Representation):**

```
Required Evidence:
  E2a: Authorization decision evidence
    - Governance record (decision ID, authority)
    - Decision timestamp
    - Authorized consequence specification
    - Required precision: Exact content of authorization

  E2b: Constraint definition evidence
    - Written specification of constraints
    - Version/revision information
    - Supersession history
    - Required precision: All constraints explicitly stated

  E2c: Supersession/revocation evidence
    - Change records (who, when, why)
    - Effective dates
    - Backward compatibility notes
    - Required precision: Exact effective timestamps
```

**For D3 (CO Representation):**

```
Required Evidence:
  E3a: CO construction evidence
    - Log showing CO components combined
    - Timestamp of CO determination
    - Decision logic applied
    - Required precision: Step-by-step construction

  E3b: Outcome type determination evidence
    - Comparison results (auth vs actual)
    - Constraint evaluations
    - Evidence completeness assessment
    - Required precision: All evaluations recorded

  E3c: Compliance status evidence
    - Constraint violations (if any)
    - Authorization scope checks
    - Evidence adequacy assessment
    - Required precision: Which constraints failed/passed
```

**For D4 (Consequence Capture Mechanism):**

```
Required Evidence:
  E4a: Action result capture
    - Instrumentation points where capture occurs
    - Captured data (return value, state changes)
    - Failure/exception handling
    - Required precision: No data loss

  E4b: State change observation
    - Before/after snapshots
    - Change detection method
    - Observation latency
    - Required precision: All significant changes observed

  E4c: Consequence detection
    - Classification algorithm applied
    - Confidence scores (if any)
    - Manual review flags
    - Required precision: Classification rationale

  E4d: Capture mechanism execution
    - Invocation logs (when capture called)
    - Processing duration
    - Success/failure outcome
    - Required precision: Audit trail of execution

  E4e: Persistence proof
    - Write operations logged
    - Checksums/signatures (if any)
    - Storage confirmation
    - Required precision: Proof of durable write
```

**For D5 (Authorization->Consequence Binding):**

```
Required Evidence:
  E5a: Authorization evidence
    - Decision records linking action to scope
    - Timestamp of authorization
    - Authority legitimacy
    - Required precision: Exact authorization content

  E5b: Scope binding evidence
    - Action performed (execution logs)
    - Action parameters (target, context)
    - Scope validation results
    - Required precision: Action within scope verified

  E5c: Consequence detection evidence
    - Observation logs (when consequence detected)
    - Classification (consequence type)
    - Confidence/certainty (if applicable)
    - Required precision: Detection fully documented

  E5d: Correlation evidence
    - How authorization linked to consequence
    - Intermediate steps (if any)
    - Correlation confidence
    - Required precision: Linking mechanism clear

  E5e: Binding verification evidence
    - Constraint evaluations
    - Outcome determination
    - Evidence completeness
    - Required precision: All verifications recorded
```

**For D6 (Consequence Propagation):**

```
Required Evidence:
  E6a-E6e: (per Part 9 edge specifications)
    - For each edge: input captured, processing logged, output recorded
    - Failure outcomes documented
    - Unknown states explicitly marked
    - Required precision: Per-edge complete trace
```

### Evidence Validation Preconditions

Before CO can be determined, evidence contract requires:

```
Validation Preconditions:

  1. AUTHORIZATION EVIDENCE AVAILABLE
     - Authorization decision recorded
     - Scope explicitly defined
     - Authority legitimacy verifiable

  2. ACTION EVIDENCE AVAILABLE
     - Action execution documented
     - Action parameters recorded
     - Scope validity confirmed

  3. CONSEQUENCE EVIDENCE AVAILABLE
     - Consequence captured/recorded
     - Consequence classification done
     - Persistence verified

  4. EVIDENCE COMPLETENESS ASSESSED
     - All required evidence located or marked MISSING
     - Evidence timestamps consistent
     - Evidence chain intact

  5. EVIDENCE INTEGRITY VERIFIED
     - No unauthorized modifications
     - Checksums/signatures valid (if applicable)
     - Audit trail complete

If any precondition fails:
  -> CO outcome = UNVERIFIED (not UNDECIDABLE)
  -> Evidence status = INCOMPLETE
  -> Escalation for review required
```

---

## PART 12: FAILURE & UNKNOWN HANDLING SPECIFICATION

### Failure States

**Definition:** System state where component cannot execute as specified.

**Failure Categories:**

1. **TRANSIENT FAILURES**
   - Network timeout (Relay unavailable)
   - Database temporarily locked
   - Recovery: Retry with exponential backoff
   - Evidence: RETRY_ATTEMPTED, EVENTUALLY_SUCCEEDED or PERMANENTLY_FAILED

2. **PERMANENT FAILURES**
   - Invalid authorization (revoked)
   - Schema violation (data doesn't match spec)
   - Recovery: Manual intervention or fallback
   - Evidence: PERMANENT_FAILURE, ROOT_CAUSE, ESCALATION

3. **PARTIAL FAILURES**
   - Some consequences captured, others missed
   - Some constraints evaluated, others unavailable
   - Recovery: Record state as PARTIAL
   - Evidence: PARTIAL_CAPTURE, MISSING_EVIDENCE

### Unknown States

**Definition:** Information missing or insufficient to determine outcome with certainty.

**Unknown Categories:**

1. **NOT_FOUND**
   - Evidence searched for but not located
   - Example: Relay notification not in logs (edge 3 not executed)
   - Handling: Record explicitly as NOT_FOUND (not as ABSENT)
   - Evidence: SEARCH_PERFORMED, LOCATION_SPECIFIED, RESULT_NOT_FOUND

2. **NOT_VERIFIED**
   - Evidence exists but not yet confirmed
   - Example: Consequence possibly captured but not yet audited
   - Handling: Record as TENTATIVE, require verification later
   - Evidence: VERIFICATION_PENDING, CONFIDENCE_THRESHOLD_NOT_MET

3. **NOT_PROVEN**
   - Evidence insufficient to establish fact
   - Example: Causality suspected but not proven
   - Handling: Record as INFERRED, mark confidence level
   - Evidence: INFERENCE_BASIS, CONFIDENCE_SCORE

4. **UNKNOWN**
   - No information available
   - Example: System unavailable at critical moment
   - Handling: Record explicitly as UNKNOWN (not guessed)
   - Evidence: OBSERVATION_IMPOSSIBLE, TIMESTAMP_RANGE

### Semantic Distinctions (MUST Be Preserved)

```
NOT_FOUND  ≠ ABSENT    (searched, not located ≠ not present)
NOT_VERIFIED ≠ FALSE   (not confirmed yet ≠ proven false)
NOT_PROVEN ≠ REJECTED  (insufficient evidence ≠ evidence of rejection)
UNKNOWN    ≠ FALSE     (no information ≠ known to be false)
PARTIAL    ≠ FAILURE   (some success ≠ total failure)
```

**Specification:** Every consequence record MUST distinguish these states explicitly.

---

## PART 13: VERIFICATION PRECONDITIONS

### Pre-Runtime Verification

Before consequence mechanism can transition from DESIGN to IMPLEMENTATION, the following must be verified (by Human Gate or authorized reviewer):

**V1: Design Internal Consistency**
- D1-D6 representations are mutually consistent
- No contradictions in constraint specifications
- Evidence requirements are satisfiable
- No circular dependencies

**V2: Evidence Contract Satisfiability**
- All evidence types (E1-E14) can be collected from running system
- No evidence requirements contradict operational constraints
- Observation latency acceptable
- Durability guarantees achievable

**V3: Failure Mode Coverage**
- All identified failure categories have handling specified
- Unknown state categories have explicit preservation specified
- No silent failures (all failures logged)
- Escalation procedures defined for each failure type

**V4: Authorization->Consequence Binding Feasibility**
- Binding mechanism can be implemented without modifying L2 semantics
- Correlation identifiers can be injected without breaking causality
- Evidence chain can be maintained without performance degradation
- M18-Scope assumptions don't contradict binding design

**V5: Persistence Specification Completeness**
- Chosen persistence mechanism (TBD) satisfies all 8 requirements
- Failure handling compatible with chosen mechanism
- Unknown state representation supported by mechanism
- Schema (if applicable) can express all representation components

**V6: Propagation Chain Completeness**
- All 6 edges have formal specifications
- Missing edges (3 and 6) have design specified but implementation deferred
- No gaps in chain that would lose consequences
- Failure at any edge leads to explicit consequence (not silent loss)

### Implementation Preconditions (Deferred to Later HG Decision)

These requirements must be satisfied BEFORE implementation authorization:

**Pre-I1: Design Review Completion**
- All 18 parts of L3 Design Package reviewed by Human Gate
- Design approval formally recorded
- Any modifications required by HG addressed
- Design baseline locked

**Pre-I2: Evidence Collection Completion**
- All E1-E14 evidence collected and analyzed
- Gaps documented (NOT_FOUND ≠ ABSENT)
- Evidence report reviewed by Human Gate
- Missing evidence acknowledged as blockers or acceptable gaps

**Pre-I3: Semantic Closure Readiness**
- Current closure status = NOT_ACHIEVED (remains LOCKED)
- Preconditions for promoting closure explicitly stated
- Evidence required for closure explicitly enumerated
- Closure readiness assessed in separate HG decision

**Pre-I4: M18-Scope Resolution**
- M18-Scope status = HOLD (remains LOCKED in current cycle)
- Scope assumptions in design explicitly documented
- Scope impact on implementation prioritized
- Scope definition deferred to independent HG (Q7 authority)

**Pre-I5: Implementation Authorization Decision**
- HG-R07 decision inverted: IMPLEMENTATION NOT AUTHORIZED -> AUTHORIZED
- All implementation preconditions satisfied
- Risk assessment and mitigation documented
- Implementation plan reviewed and approved

---

## PART 14: DESIGN ASSUMPTION REGISTRY

### Assumptions Made in This Design

**A1: L2 Semantics are Authoritative**
- Assumption: ActualConsequence, AuthorizedConsequence, CO definitions in L2 are correct and will not change
- Basis: L2 Design approved by Human Gate (HG-R01 AUTHORIZE)
- Risk: If L2 changes, design must be revised
- Mitigation: L2 and L3 designs locked together; any L2 change requires new HG decision

**A2: Consequence Capture is Possible**
- Assumption: System can capture all consequential state changes as they occur
- Basis: Execution layer has visibility into state changes (code instrumentation possible)
- Risk: If consequences are ephemeral or non-observable, capture fails
- Mitigation: Evidence collection (E4) will verify feasibility; if NOT_FOUND, design revisited

**A3: Persistence is Achievable**
- Assumption: System can persist consequence records durably and immutably
- Basis: System has persistent storage layer available
- Risk: If storage layer fails or is insufficiently isolated, persistence fails
- Mitigation: Persistence mechanism design (Part 10) chosen based on available infrastructure

**A4: Authorization Scope is Known**
- Assumption: Authorization decisions can be precisely specified with action, target, conditions
- Basis: Authorization mechanism exists and is well-defined
- Risk: If authorization is vague or implicit, binding fails
- Basis: Evidence collection (E5) will verify authorization precision

**A5: M18-Scope is Stable**
- Assumption: M18-Scope definition will not change during consequence mechanism implementation
- Basis: HG-R06 MAINTAIN HOLD (scope locked in current cycle)
- Risk: If scope changes, design must accommodate scope evolution
- Mitigation: Scope membership is stored as observable fact (not inferred); changes tracked

**A6: Semantic Closure is Deferred**
- Assumption: Consequence mechanism can be implemented and demonstrated before Semantic Closure is promoted
- Basis: HG-R05 separates design + evidence from closure determination
- Risk: If closure requirements are discovered to be unsatisfiable, mechanism invalidated
- Mitigation: Each design component explicitly notes what evidence would satisfy closure for that component

**A7: Implementation is Deferred**
- Assumption: Design alone is sufficient authority; implementation requires separate HG decision
- Basis: HG-R02/R03/R04/R05 authorize DESIGN-ONLY, not implementation
- Risk: If design is approved but implementation later found infeasible, sunk cost
- Mitigation: Implementation preconditions (Part 13) must be satisfied before authorization

---

## PART 15: IMPLEMENTATION PRECONDITIONS

*(Detailed specifications for future implementation phase)*

### IP1: Code Architecture

*What implementation must accomplish (not how):*

- Consequence capture mechanism must hook into execution layer
- Capture must occur before return from action
- Capture must not block action execution (async if needed)
- Capture must preserve causality (execution context linkage)

### IP2: Schema Specification

*What data structures must be defined:*

- ActualConsequence record schema (Part 4 formal representation)
- AuthorizedConsequence record schema (Part 5)
- CO record schema (Part 6)
- Persistence schema (Part 10 chosen mechanism)
- Index strategy for queryability

### IP3: Integration Points

*Where code must be modified/inserted:*

- Authorization decision layer (inject AuthorizedConsequence creation)
- Action execution layer (inject capture instrumentation)
- State mutation points (inject detection)
- Decision determination layer (inject CO computation)
- Governance layer (inject decision recording)

### IP4: Testing Strategy

*What must be verified before production:*

- Unit tests: Each edge (Part 9) independently
- Integration tests: Full chain (authorization -> consequence -> CO -> decision)
- Failure mode tests: Each failure type (Part 12)
- Unknown state tests: Each unknown category (Part 12)
- Evidence contract tests: Each E1-E14 requirement (Part 11)
- Temporal tests: Ordering, latency, skew handling
- Load tests: Capture and persistence under load
- Audit tests: Evidence integrity, immutability, auditability

### IP5: Operational Requirements

*What must be present at runtime:*

- Consequence queue (if async)
- Persistence layer health monitoring
- Evidence accessibility (query performance)
- Audit logging infrastructure
- Incident escalation procedures
- Manual intervention procedures (for failures)

---

## PART 16: HUMAN GATE REASSESSMENT QUESTIONS

*To be asked at next HG cycle (after design + evidence package completed)*

### Q1: Design Acceptance

**Question:** Does L3 Formal Mechanism Design Package (D1-D6) meet the semantic requirements specified in L2?

**What HG Will Decide:**
- ACCEPT (design approved as-is)
- ACCEPT WITH REVISIONS (design acceptable pending specified changes)
- REQUEST REVISIONS (design requires significant rework)
- DEFER (design needs further evidence before decision)

**Required Response:**
- HG specifies any required revisions
- HG confirms design baseline locked
- Design becomes immutable for implementation phase

---

### Q2: Persistence Mechanism Selection

**Question:** Which persistence strategy (A/B/C/D from Part 10) should be used for consequence records?

**Options:**
- A: Event Store (append-only log)
- B: Decision Ledger (structured records with references)
- C: Relational (normalized schema)
- D: Hybrid (combination)
- E: OTHER (specify)

**Required Response:**
- HG selects mechanism
- HG documents selection rationale
- Implementation must follow chosen mechanism

---

### Q3: Authorization->Consequence Binding Implementation

**Question:** Is the formal binding model (Part 8) sufficient for runtime implementation?

**What HG Will Decide:**
- YES (binding model authorizes implementation)
- CONDITIONAL (binding model OK only if specific conditions verified)
- NO (model requires revision before implementation)
- DEFER (more evidence needed)

**Required Response:**
- HG specifies any conditions
- If conditions specified, implementation must verify before proceeding

---

### Q4: Evidence Sufficiency for Mechanism Activation

**Question:** Do the E1-E14 evidence findings provide sufficient basis for confidence in mechanism design?

**What HG Will Decide:**
- SUFFICIENT (evidence supports design)
- PARTIAL (evidence sufficient for design; runtime verification required)
- INSUFFICIENT (evidence gaps block implementation)
- DEFER (request additional evidence collection)

**Required Response:**
- HG specifies confidence level
- HG documents any gaps requiring monitoring at runtime

---

### Q5: Semantic Closure Readiness

**Question:** Can Semantic Closure (currently NOT_ACHIEVED) be promoted to COMPLETE based on design + evidence?

**What HG Will Decide:**
- YES (closure promoted to COMPLETE)
- CONDITIONAL (promoted only if implementation verification succeeds)
- NO (closure remains NOT_ACHIEVED, blocking implementation)
- DEFER (additional evidence required)

**Required Response:**
- If YES/CONDITIONAL: Document closure achievement evidence
- If NO: Document gaps preventing closure
- Closure status locked until next HG decision

---

### Q6: M18-Scope Readiness

**Question:** Should M18-Scope be defined, or remain on HOLD for independent HG authority (Q7)?

*Note: This is a question for Q7-authority (independent domain). HG-R06 = MAINTAIN HOLD.*

**What HG Will Decide:**
- DEFINE NOW (override Q7 independence; scope defined in this cycle)
- DEFER TO Q7 (maintain separation; Q7 authority defines scope later)
- MAINTAIN HOLD (scope remains locked; defer both to later cycle)

**Required Response:**
- If DEFINE NOW: Violation of Q7 authority (should be escalated)
- If DEFER TO Q7: Scope remains as input to Q7 decision
- If MAINTAIN HOLD: M18-Scope = HOLD / LOCKED continues

---

### Q7: Implementation Authorization

**Question:** Should Consequence Mechanism implementation be authorized?

**What HG Will Decide:**
- AUTHORIZE (implementation may begin)
- AUTHORIZE WITH CONDITIONS (implementation OK only if conditions met)
- DEFER (implementation deferred pending further work)
- NOT AUTHORIZE (implementation remains prohibited)

**Required Response:**
- If AUTHORIZE/WITH CONDITIONS: Implementation authorization granted
- If DEFER/NOT AUTHORIZE: Reasons documented; timeline for re-evaluation specified
- Implementation remains NOT_AUTHORIZED until explicit HG decision reverses this

---

## PART 17: CANONICAL STATE PRESERVATION

### State During Design Phase

```
BEFORE DESIGN:
  HG-R01 = AUTHORIZE (locked)
  HG-R02 = AUTHORIZE WITH CONDITIONS (locked)
  HG-R03 = AUTHORIZE DESIGN (locked)
  HG-R04 = AUTHORIZE (locked)
  HG-R05 = AUTHORIZE BOTH EVIDENCE AND DESIGN (locked)
  HG-R06 = MAINTAIN HOLD (locked)
  HG-R07 = IMPLEMENTATION NOT AUTHORIZED / HOLD (locked)

  Semantic Closure = NOT_ACHIEVED / LOCKED
  M18-Scope = HOLD / LOCKED
  Implementation Authorization = NOT_GRANTED / LOCKED

  L3 Design = NOT_CREATED
  L3 Evidence = NOT_COLLECTED

DURING DESIGN:
  All above states remain UNCHANGED
  Design documents created but not yet sealed
  Evidence documents created but not yet sealed

AFTER DESIGN/EVIDENCE COMPLETION AND SEALING:
  All above states remain UNCHANGED (still locked)
  L3 Design = CREATED / REVIEW_READY
  L3 Evidence = CREATED / REVIEW_READY
  Design Seal = INTEGRITY VERIFIED / GIT COMMITTED
  Evidence Seal = INTEGRITY VERIFIED / GIT COMMITTED

EXPECTED (not changed):
  HG-R01 through HG-R07 all remain in original state
  Semantic Closure remains NOT_ACHIEVED / LOCKED
  M18-Scope remains HOLD / LOCKED
  Implementation Authorization remains NOT_GRANTED / LOCKED
  Code modifications = 0
  Schema modifications = 0
  Database modifications = 0
  Runtime modifications = 0
  Production modifications = 0
```

### Modification Counters

```
Code Modification Counter
  Before: 0
  During Design: 0 (no implementation)
  After Design: 0
  Verification: git diff --stat shows no .py changes (except comments/docs)

Schema Modification Counter
  Before: 0
  During Design: 0 (no schema)
  After Design: 0
  Verification: no .json schema changes in data/ or structural/

Database Modification Counter
  Before: 0
  During Design: 0 (no DB)
  After Design: 0
  Verification: no DB operations logged

Runtime Modification Counter
  Before: 0
  During Design: 0 (no binding)
  After Design: 0
  Verification: no runtime changes

Production Modification Counter
  Before: 0
  During Design: 0 (no deployment)
  After Design: 0
  Verification: no changes to production systems
```

---

## PART 18: DESIGN INTEGRITY & SEALING

### Validation Checklist

Before this design package is sealed, the following MUST be verified:

- [ ] UTF-8 validation PASS (no forbidden characters: down-arrow, right-arrow, brackets)
- [ ] Internal consistency check PASS (D1-D6 mutually consistent)
- [ ] Evidence requirements check PASS (all E1-E14 satisfiable)
- [ ] Failure mode coverage check PASS (no silent failures)
- [ ] Authorization boundary check PASS (Q5/Q7/Q8 independence maintained)
- [ ] Canonical state check PASS (all locked states preserved)
- [ ] Git diff check PASS (no code/schema/database changes)
- [ ] No evidence of implementation (git shows design-only files)
- [ ] Decision record sealed (HG03_CONSEQUENCE_MECHANISM_REASSESSMENT_HG_DECISION_20260913.md created and committed)
- [ ] Evidence report sealed (L3_FORMAL_MECHANISM_EVIDENCE_REPORT_20260913.md created and committed)

### Sealing Status

**Status:** NOT_YET_SEALED (awaiting git operations)

**Expected After Sealing:**
- File: `data/decisions/L3_FORMAL_MECHANISM_DESIGN_PACKAGE_20260913.md`
- Git Commit: (to be recorded)
- Integrity: VERIFIED (all checksums match)
- Authority: DESIGN_ONLY (no implementation authorization)
- Next Phase: Await Human Gate reassessment (HG-R08 onwards)

---

**END OF L3 FORMAL MECHANISM DESIGN PACKAGE**

*This design package represents the Layer 3 formal specification of Consequence Mechanism representations (D1-D6). It is design-only; no implementation is authorized. All locked states are preserved. Evidence collection is conducted in parallel and documented separately in L3_FORMAL_MECHANISM_EVIDENCE_REPORT_20260913.md. Both packages will be sealed and submitted to Human Gate for HG-R08 through HG-R13 decisions.*

*Generated: 2026-09-13 | Authority Basis: HG-R01 through HG-R05 | Status: DESIGN / NOT_IMPLEMENTED / REVIEW_READY*
