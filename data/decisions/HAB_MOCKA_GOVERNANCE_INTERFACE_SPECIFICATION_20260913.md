# HAB/MoCKA Governance Interface Specification
**2026-09-13**

## Document Control

* Classification: GOVERNANCE / CONTRACT / DESIGN-ONLY
* Authority: KUROKO Protocol (Governance Interface Design Phase)
* Design Scope: Layer 1-2 (MoCKA authorization interface, token schema, governance flow)
* Implementation Scope: NONE (Design-only; no implementation)
* Record Timestamp: 2026-09-13T15:50:00Z
* Status: DESIGN SPECIFICATION (awaiting Human Gate decision HG-HJ-05)

---

## PART 1: Executive Summary

This document specifies the formal interface between HAB (Boundary Interpretation) and MoCKA (Governance Authority). The interface covers:

1. Authorization token issuance and validation
2. Scope verification authority handoff
3. Evidence discipline enforcement
4. Appeal escalation protocol
5. Governance decision synchronization

**Core Principle**: All authority originates from MoCKA; HAB verifies and applies authority; Runtime enforces atomically.

---

## PART 2: MoCKA Authorization Token Schema

### 2.1 Complete Token Structure

```json
{
  "token_id": "AUTH-YYYYMMDD-{uuid}",
  "issuer": "mocka_q5_governance",
  "issued_at": "2026-09-13T15:50:00Z",
  "expires_at": "2026-09-13T16:00:00Z",
  "authorization_level": "DESIGN_LAYER_ONLY | LAYER_1_2_ONLY | FULL_AUTHORITY",
  "authorized_operations": [
    {
      "operation_class": "scope_membership_verification",
      "scope_universes": ["CANDIDATE_A", "CANDIDATE_B"],
      "evidence_criteria": {
        "CANDIDATE_A": {
          "required_evidence": ["E15-01", "E15-02"],
          "optional_evidence": ["E15-03"],
          "membership_criteria_description": "text description (informational)"
        },
        "CANDIDATE_B": {...}
      },
      "consequence_bindings_permitted": ["strict_in_band_only"],
      "enforcement_model": "STRICT_IN_BAND"
    },
    {
      "operation_class": "evidence_evaluation",
      "evidence_program_reference": "HG-R15_ADDITIONAL_EVIDENCE_PROGRAM",
      "evidence_range": "E15-01 through E15-10",
      "evaluation_scope": "membership_criteria_only"
    }
  ],
  "restrictions": [
    "NO_AUTONOMOUS_SCOPE_INFERENCE",
    "NO_CODE_MODIFICATION",
    "NO_SCHEMA_MODIFICATION",
    "NO_DATABASE_MODIFICATION",
    "NO_RUNTIME_BINDING_MODIFICATION",
    "NO_M18_SCOPE_REDEFINITION",
    "NO_IMPLEMENTATION_AUTHORIZATION_CHANGE"
  ],
  "scope_authority_reference": "HG-Q7_SCOPE_DECISION_20260913",
  "evidence_authority_reference": "HG-R15_ADDITIONAL_EVIDENCE_PROGRAM_20260913",
  "governance_baseline_reference": "HG-R08_R15_DECISION_RECORD_20260913",
  "signature": "mocka_cryptographic_signature",
  "signature_algorithm": "sha256_rsa_4096",
  "public_key_reference": "mocka_q5_governance_key_20260913",
  "token_version": "1.0"
}
```

### 2.2 Token Validity Checks (HAB Performs)

```
VALIDATION STEPS (in order; abort on first failure):

[V1] Token Format
  Check: token_id matches format AUTH-YYYYMMDD-{uuid}
  Fail Action: return auth_status = INVALID_TOKEN_FORMAT

[V2] Issuer Verification
  Check: issuer = "mocka_q5_governance"
  Fail Action: return auth_status = INVALID_ISSUER

[V3] Signature Verification
  Check: signature valid (using public_key_reference)
  Fail Action: return auth_status = INVALID_SIGNATURE

[V4] Expiry Check
  Check: expires_at > current_utc_time
  Fail Action: return auth_status = EXPIRED_TOKEN

[V5] Authorization Level
  Check: authorization_level ∈ [DESIGN_LAYER_ONLY, LAYER_1_2_ONLY, FULL_AUTHORITY]
  Fail Action: return auth_status = INVALID_AUTHORIZATION_LEVEL

[V6] Scope Universe Compatibility
  Check: requested scope_universe ∈ token.authorized_operations[...].scope_universes
  Fail Action: return auth_status = SCOPE_NOT_AUTHORIZED

[V7] Evidence Criteria Completeness
  Check: for requested scope_universe, membership_criteria_description exists
  Fail Action: return auth_status = EVIDENCE_CRITERIA_MISSING

[V8] Restrictions Compliance
  Check: none of token.restrictions prevent requested operation
  Fail Action: return auth_status = OPERATION_RESTRICTED

[V9] Governance Baseline Seal
  Check: governance_baseline_reference points to sealed HG-R08-R15 record
  Fail Action: return auth_status = GOVERNANCE_BASELINE_INVALID

IF all [V1-V9] pass: auth_status = VALID
ELSE: auth_status = INVALID (with specific failure reason)
```

---

## PART 3: Scope Verification Authority Handoff

### 3.1 Flow: MoCKA → HAB → Runtime

```
STEP 1: MoCKA Issues Authorization Token
  MoCKA Q7 (or Q5) creates token with:
    - Evidence criteria (membership rules for each scope universe)
    - Scope universes authorized (CANDIDATE_A, CANDIDATE_B, ...)
    - Evidence program reference (HG-R15)
    - Enforcement model (STRICT_IN_BAND)
  Action: MoCKA signs token and publishes to session cache

STEP 2: HAB Retrieves and Validates Token
  HAB action: GET /mocka/authorization/{authorization_hint}
  HAB validates token using [V1-V9] checks
  HAB extracts: evidence_criteria, authorized_scope_universes, enforcement_model
  Action: Proceed to scope verification with extracted criteria

STEP 3: HAB Performs Scope Verification
  HAB receives request: {scope_universe: "CANDIDATE_A", evidence_references: [...]}
  HAB action:
    1. Look up CANDIDATE_A in token.evidence_criteria
    2. Get required_evidence and optional_evidence from criteria
    3. Verify request evidence_references ⊆ (required + optional evidence)
    4. Verify no inference from absent evidence
    5. Return scope_status = VERIFIED (if all checks pass)

STEP 4: HAB Constructs Execution Binding
  HAB synthesizes binding with:
    - Authorization token reference
    - Verified scope set
    - Evidence criteria (from token)
    - Enforcement model (from token: STRICT_IN_BAND)
    - Full evidence lineage
  Action: Send binding to Runtime

STEP 5: Runtime Atomically Enforces
  Runtime action:
    1. Verify authorization token presence in binding
    2. Verify scope membership (using HAB-verified set)
    3. Verify consequence binding (Enforcement Model A)
    4. Verify evidence lineage (all E15-* references present)
    5. Execute atomically or reject entirely (no partial execution)
  Action: Record execution event to Event Store
  
STEP 6: MoCKA Records Execution
  MoCKA receives execution event from Event Store
  MoCKA records decision to Decision Ledger
  MoCKA updates system state (maintains M18-Scope = HOLD, Implementation Authorization = NOT_GRANTED)
```

---

## PART 4: Evidence Discipline Enforcement

### 4.1 Distinctions Preserved at Each Boundary

```
BOUNDARY: MoCKA → HAB (Token Issuance)
  [E-1] NOT_FOUND ≠ ABSENT
    Token Field: evidence_criteria.required_evidence (explicit set)
    If evidence not in set: treat as NOT_FOUND (not as rejection)
    HAB Action: Request evidence collection via HG-R15 (if scope_unknown)

  [E-2] NOT_PROVEN ≠ REJECTED
    Token Field: evidence_criteria.optional_evidence (candidates remain valid)
    If candidate evidence incomplete: return scope_status = UNVERIFIED_EVIDENCE
    HAB Action: Suggest evidence program continuation (not rejection)

  [E-3] Design ≠ Implementation
    Token Field: authorization_level = DESIGN_LAYER_ONLY
    Implication: Layer 3+ implementation prohibited
    HAB Action: Reject any operation outside Layer 1-2 scope

BOUNDARY: HAB → Runtime (Execution Binding)
  [E-4] Scope Membership ≠ Consequence Binding
    Binding Fields: scope_set (HAB-verified), consequence_bindings (Model A-validated)
    Enforcement: Runtime validates both independently
    Runtime Action: Reject if either fails (don't substitute one for the other)

  [E-5] Evidence Accepted ≠ Runtime Proof
    Binding Field: evidence_lineage (HG-R15 accepted evidence)
    Runtime implication: Evidence sufficient for design; not runtime proof
    Runtime Action: Use evidence for authorization/scope validation; not for correctness proof

BOUNDARY: Runtime → MoCKA (Execution Recording)
  [E-6] Execution Success ≠ Semantic Closure Achievement
    Event: Execution completed successfully
    MoCKA action: Record to Event Store; DO NOT change Semantic Closure status
    Semantic Closure remains: NOT_ACHIEVED / LOCKED (separate decision required)
```

### 4.2 NOT_FOUND ≠ ABSENT Protocol

```
SCENARIO 1: Evidence Reference Present in Token
  Token: evidence_criteria.required_evidence = ["E15-01", "E15-02"]
  Request: evidence_references = ["E15-01", "E15-02"]
  HAB Action: scope_status = VERIFIED (all required evidence present)

SCENARIO 2: Evidence Reference NOT in Token (Not Found)
  Token: evidence_criteria.required_evidence = ["E15-01", "E15-02"]
  Request: evidence_references = ["E15-01", "E15-02", "E15-03"]
  HAB Action: scope_status = UNVERIFIED_EVIDENCE (E15-03 not in criteria)
  JARVIS Appeal: Request Q7 reassessment to include E15-03 in criteria

SCENARIO 3: Evidence Gap (Absence is Acknowledged)
  Token: evidence_criteria.required_evidence = ["E15-01"]
  Token: evidence_criteria.optional_evidence = [] (gap acknowledged)
  Request: evidence_references = ["E15-01"] (only E15-01 available)
  HAB Action: scope_status = VERIFIED (evidence satisfies minimum criteria)
  JARVIS Action: Coordinate with HG-R15 program to collect E15-02-E15-10

SCENARIO 4: Evidence Never Collected (NOT_FOUND vs ABSENT)
  Token: evidence_criteria includes E15-03 as optional
  Reality: E15-03 was never investigated (NOT_FOUND)
  NOT: E15-03 is absent from membership (ABSENT)
  HAB Action: Treat as UNKNOWN; do NOT infer absence
  JARVIS Appeal: Request evidence collection for E15-03
```

---

## PART 5: Appeal Escalation to MoCKA

### 5.1 Appeal Types & Authority Routing

```
Appeal Type 1: SCOPE_UNKNOWN
  Trigger: HAB returns scope_status = UNKNOWN
  Reason: No membership criteria for requested scope universe
  Route To: MoCKA Q7 (Scope Authority)
  Q7 Options:
    [A] DEFINE_SCOPE (provide membership criteria, issue new token)
    [B] CONTINUE_HOLD (maintain hold, request evidence collection)
    [C] COLLECT_MORE_EVIDENCE (defer pending HG-R15 completion)

Appeal Type 2: EVIDENCE_GAP
  Trigger: HAB returns scope_status = EVIDENCE_GAP
  Reason: Requested evidence not in membership criteria
  Route To: MoCKA Q7 (Scope Authority)
  Q7 Options:
    [A] EXTEND_CRITERIA (add missing evidence to criteria)
    [B] REJECT_CANDIDATE (candidate scope not viable)
    [C] CONTINUE_HOLD (maintain hold, coordinate with HG-R15)

Appeal Type 3: AUTHORIZATION_EXPIRED
  Trigger: HAB returns auth_status = EXPIRED_TOKEN
  Reason: Authorization token validity expired
  Route To: MoCKA Q5 (Governance Authority)
  Q5 Options:
    [A] ISSUE_NEW_TOKEN (extend authorization, same criteria)
    [B] REVISE_TOKEN (modify authorization level or criteria)
    [C] DENY_OPERATION (authorization not renewed)

Appeal Type 4: EVIDENCE_DISCIPLINE_VIOLATION
  Trigger: HAB returns evidence_status = EVIDENCE_DISCIPLINE_VIOLATION
  Reason: Evidence NOT_FOUND vs ABSENT distinction violated
  Route To: MoCKA Q7 or Q5 (depending on source of violation)
  Response: MoCKA corrects evidence criteria and reissues token

Appeal Type 5: CONSEQUENCE_BINDING_FAILURE
  Trigger: HAB returns consequence_status = UNMAPPED_OPERATION
  Reason: Operation not in Enforcement Model A binding table
  Route To: MoCKA Q8 (Enforcement Verification Authority)
  Q8 Options:
    [A] ADD_BINDING (add operation to Model A table)
    [B] REVISE_MODEL (Model A update required)
    [C] REJECT_OPERATION (operation not eligible for Model A)
```

### 5.2 Appeal Flow Protocol

```
STEP 1: JARVIS Receives HAB Rejection
  HAB sends: {status: "REJECTED", rejection_reason: "scope_unknown", appeal_path: "mocka:q7_scope_reassessment"}

STEP 2: JARVIS Creates Appeal
  Appeal message = {
    "appeal_id": "APPEAL-20260913-{uuid}",
    "original_request_id": "REQ-20260913-xxxxxxxx",
    "rejection_reason": "scope_unknown",
    "target_authority": "Q7_SCOPE_AUTHORITY",
    "requested_action": "DEFINE_SCOPE | CONTINUE_HOLD | COLLECT_MORE_EVIDENCE",
    "justification": "text explanation",
    "timestamp": "2026-09-13T15:50:00Z"
  }

STEP 3: JARVIS Routes Appeal to MoCKA
  Endpoint: POST /mocka/appeals
  MoCKA Authority (Q5/Q7/Q8) receives and reviews

STEP 4: MoCKA Authority Decides
  [D1] APPROVE (with modifications)
    Action: Issue new authorization token, update evidence criteria
    JARVIS receives: new token or modified criteria
    JARVIS action: Retry coordination request
  
  [D2] DENY
    Action: Maintain current hold
    JARVIS receives: "appeal_denied"
    JARVIS action: Notify human originator, cease coordination
  
  [D3] DEFER
    Action: Await evidence collection completion
    JARVIS receives: "appeal_deferred, reassess after HG-R15 completion"
    JARVIS action: Monitor HG-R15 program, retry later

STEP 5: JARVIS Receives MoCKA Decision
  IF approved: resume coordination with new/revised token
  IF denied: escalate to human, coordination stops
  IF deferred: coordinate with HG-R15 program, retry after evidence collected
```

---

## PART 6: Governance Decision Synchronization

### 6.1 MoCKA Decision Ledger Integration

```
DECISION LEDGER RECORD (from DECISION_LEDGER_SCHEMA_v1):

{
  "decision_id": "HG-{Gate}-{YYYYMMDD}",
  "decision_type": "SCOPE_DEFINITION | AUTHORIZATION_ISSUANCE | APPEAL_RESOLUTION",
  "related_request_id": "REQ-20260913-xxxxxxxx | APPEAL-20260913-xxxxxxxx",
  "authority": "Q5_GOVERNANCE | Q7_SCOPE | Q8_ENFORCEMENT",
  "decision_text": "full decision statement",
  "alternatives_considered": ["ALT-1", "ALT-2"],
  "rationale": "decision justification",
  "timestamp": "2026-09-13T15:50:00Z",
  "executed_by": "mocka_q5_governance_authority",
  "approval_chain": [
    {"authority": "Q5", "timestamp": "2026-09-13T15:45:00Z", "status": "approved"},
    {"authority": "Human Gate", "timestamp": "2026-09-13T15:40:00Z", "status": "approved"}
  ],
  "state_changes": {
    "implementation_authorization": "NOT_GRANTED (unchanged)",
    "m18_scope": "HOLD (unchanged or HOLD_MODIFIED_CRITERIA)",
    "semantic_closure": "NOT_ACHIEVED (unchanged)",
    "modification_vectors": "all remain 0"
  },
  "verification_hash": "sha256_hash_of_decision_content"
}
```

### 6.2 Token Issuance → Decision Ledger Flow

```
STEP 1: MoCKA Q5/Q7 Creates Authorization Token
  Action: Token synthesized with evidence criteria, scope universes, restrictions

STEP 2: Token Signed by MoCKA
  Action: Cryptographic signature applied (sha256_rsa_4096)

STEP 3: Token Published to Session Cache
  Action: Token available for HAB retrieval

STEP 4: Token Metadata Recorded to Decision Ledger
  Decision Record:
    - token_id reference
    - scope_universes authorized
    - evidence_criteria_snapshot
    - restrictions_imposed
    - approval_chain (Q5/Q7 signature + Human Gate verification if required)
    - state_lock confirmation (Implementation NOT_GRANTED, M18-Scope HOLD, etc.)

STEP 5: HAB Retrieves and Validates Token
  Action: Verifies signature, expiry, authorization_level
  Action: Caches token for request processing

STEP 6: Execution Events Flow Back to MoCKA
  Runtime records execution event to Event Store
  MoCKA reads Event Store and cross-references to Decision Ledger
  MoCKA updates execution_verification field in Decision Ledger
```

---

## PART 7: State Lock Enforcement at MoCKA Boundary

### 7.1 MoCKA Authorization Scope (What Cannot Change)

```
LOCKED DURING GOVERNANCE BOUNDARY DESIGN:

[LOCK-1] Implementation Authorization
  Value: NOT_GRANTED
  Authority: HG-R14 (immutable during design)
  MoCKA Enforcement: No token issued at FULL_AUTHORITY level
  All tokens: authorization_level = DESIGN_LAYER_ONLY or LAYER_1_2_ONLY

[LOCK-2] M18-Scope Status
  Value: HOLD
  Authority: HG-Q7 (reassessment trigger active, but hold maintained)
  MoCKA Enforcement: Token includes scope_authority_reference = HG-Q7_SCOPE_DECISION
  All scope_universes: CANDIDATE_A through CANDIDATE_D only (no expanded scope)

[LOCK-3] Semantic Closure
  Value: NOT_ACHIEVED
  Authority: Separate decision required (not part of governance boundary design)
  MoCKA Enforcement: No token ever claims semantic_closure_achieved = true

[LOCK-4] Modification Vectors (All = 0)
  Code Modification: 0 (no runtime code changes)
  Schema Modification: 0 (no database schema)
  Database Modification: 0 (no table/data creation)
  Runtime Binding Modification: 0 (no execution-time binding)
  Production Deployment: 0 (no deployment changes)
  MoCKA Enforcement: All tokens include restrictions field with full list

[LOCK-5] Enforcement Model A (STRICT_IN_BAND)
  Value: STRICT_IN_BAND (Enforcement Model A locked; HG-R10 sealed)
  MoCKA Enforcement: enforcement_model = "STRICT_IN_BAND" in all tokens (not reopened)

[LOCK-6] Persistence Strategy D (HYBRID)
  Value: HYBRID (Persistence Model D locked; HG-R09 sealed)
  MoCKA Enforcement: persistence_strategy = "HYBRID" referenced in governance_baseline
  Change Prevention: MoCKA Q5 cannot issue token with different strategy
```

### 7.2 MoCKA Authorization Scope (What CAN Change With Approval)

```
MODIFIABLE (Within Design-Only Scope):

[MOD-1] Evidence Criteria
  Action: Q7 can revise membership_criteria based on evidence program findings
  Constraint: Only E15-01 through E15-10 (HG-R15 evidence range)
  Token Update: New token issued with revised criteria
  MoCKA Record: Decision Ledger entry for criteria revision

[MOD-2] Scope Universe Coverage
  Action: Q7 can extend token to authorize additional CANDIDATE universes
  Constraint: Must be one of CANDIDATE_A, CANDIDATE_B, CANDIDATE_C, CANDIDATE_D
  Token Update: New token includes additional scope_universes
  MoCKA Record: Decision Ledger entry for scope expansion

[MOD-3] Authorization Level (Within Design-Only Constraint)
  Action: Q5 can adjust authorization_level between DESIGN_LAYER_ONLY and LAYER_1_2_ONLY
  Constraint: Never exceeds LAYER_1_2_ONLY (implementation prohibited)
  Token Update: New token reissued with revised authorization_level
  MoCKA Record: Decision Ledger entry for authorization level change
```

---

## PART 8: Governance Interface Design Closure Conditions

This specification is complete and sealed when:

1. Authorization token schema fully specified (PART 2)
2. Token validity checks defined (PART 2.2)
3. Scope verification authority handoff documented (PART 3)
4. Evidence discipline enforcement at boundaries (PART 4)
5. Appeal escalation protocol complete (PART 5)
6. Decision Ledger integration specified (PART 6)
7. State lock enforcement documented (PART 7)
8. Human Gate decision HG-HJ-05 acceptance pending
9. 20-point integrity verification includes governance interface
10. No code/schema/database modifications (vectors remain = 0)

---

## FINAL STATUS

**HAB/MoCKA Governance Interface: DESIGN SPECIFICATION PHASE**

```
Interface: Authorization tokens, scope verification, appeal escalation
Layer: 1-2 (Governance Interface)
Implementation: NONE (Design-only)
State Locks: ALL MAINTAINED (Implementation NOT_GRANTED, M18-Scope HOLD, Modification Vectors = 0)
```

**Governance Interface Sealed: DESIGN SPECIFICATION**
**Authority: KUROKO Protocol (Governance Interface Design Phase)**
**Human Gate Decision: HG-HJ-05 Pending**

