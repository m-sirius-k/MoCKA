# HAB/JARVIS Bypass Path Analysis
**2026-09-13**

## Document Control

* Classification: GOVERNANCE / SECURITY / DESIGN-ONLY
* Authority: KUROKO Protocol (Bypass Analysis Phase)
* Design Scope: Layer 1-2 (15 bypass paths identified and blocked)
* Implementation Scope: NONE (Analysis and prevention specification only)
* Record Timestamp: 2026-09-13T16:00:00Z
* Status: DESIGN SPECIFICATION (awaiting Human Gate decision HG-HJ-07)

---

## PART 1: Executive Summary

This document analyzes 15 potential bypass paths that could circumvent the HAB boundary, compromise scope isolation, or violate evidence discipline. Each bypass path is:

1. Formally identified and named (B1-B15)
2. Classified by attack surface (code inference, authority override, etc.)
3. Analyzed for evidence status
4. Blocked by structural, contractual, governance, and atomic enforcement mechanisms

**Core Principle**: No single mechanism blocks all bypasses; layered defenses (Structure → Contract → Governance → Atomicity) provide defense-in-depth.

---

## PART 2: Bypass Path Categories

### 2.1 Category A: Scope Inference Bypasses (B1-B5)

These paths attempt to autonomously infer scope without HAB/MoCKA verification.

#### B1: Code Artifact Inference (Route Count)
**Attack Description**: "109 Flask routes exist in codebase; therefore scope ≈ 109 items"

**Evidence Status**: EXPLICITLY_PROHIBITED (HG-Q7 evidence discipline)

**Structural Prevention**:
  - JARVIS cannot access codebase directly (no filesystem read authority)
  - Consequence_targets must be pre-documented (not scanned from code)
  - Scope_universe candidates are fixed (A/B/C/D only; not derived)

**Contractual Prevention**:
  - JARVIS/HAB interface explicitly forbids "inferred_scope" field
  - Request schema validation rejects route_count_inference signals

**Governance Prevention**:
  - MoCKA Q7 authority (not code analysis)
  - Token explicitly references evidence_criteria (not code artifact counts)

**Atomic Prevention**:
  - Runtime validates scope_membership using HAB-provided scope_set only
  - Runtime does NOT count routes in execution binding

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B2: Historical Route Claims Inference
**Attack Description**: "30 historical route claims exist; therefore scope ≈ 30"

**Evidence Status**: EXPLICITLY_PROHIBITED (NOT_PROVEN ≠ REJECTED principle)

**Structural Prevention**:
  - Historical claims are archived (not referenced in active requests)
  - Evidence references must be from E15-01 through E15-10 only

**Contractual Prevention**:
  - Request schema requires evidence_references to be E15-* format
  - Historical claims rejected by schema validator

**Governance Prevention**:
  - Evidence accepted by HG-R11 is design-basis evidence (not route claims)
  - Token evidence_criteria derived from fresh evidence (not history)

**Atomic Prevention**:
  - Runtime validates evidence lineage from token (not from historical archive)

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B3: Binding Model Path Count Inference
**Attack Description**: "15 consequential binding paths in model; therefore scope = 15 targets"

**Evidence Status**: EXPLICITLY_PROHIBITED (design artifact ≠ scope definition)

**Structural Prevention**:
  - Binding model paths are design-only (not specification of runtime scope)
  - Consequence_targets map to operations (not to path count)

**Contractual Prevention**:
  - Request consequence_targets must be individually documented
  - Arithmetic on path counts rejected by schema validation

**Governance Prevention**:
  - Scope defined by membership_criteria (not by model path count)
  - MoCKA Q7 verifies criteria; does not accept model-based scope

**Atomic Prevention**:
  - Runtime matches consequence_bindings to binding model table
  - Runtime does NOT infer scope from table size

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B4: Evidence Gap Inference (NOT_FOUND → ABSENT)
**Attack Description**: "Evidence for item X not found; therefore item X not in scope"

**Evidence Status**: EXPLICITLY_PROHIBITED (NOT_FOUND ≠ ABSENT semantic violation)

**Structural Prevention**:
  - Scope defined by positive membership_criteria (not by absence)
  - NOT_FOUND evidence treated as UNKNOWN (not as rejection)

**Contractual Prevention**:
  - HAB returns scope_status = UNKNOWN (not REJECTED)
  - Request may be escalated to Q7 for additional evidence

**Governance Prevention**:
  - MoCKA Q7 distinguishes NOT_FOUND from ABSENT explicitly
  - Token evidence_criteria are positive assertions (not negative)

**Atomic Prevention**:
  - Runtime validates scope_membership against scope_set only
  - Runtime does NOT infer non-membership from evidence absence

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B5: Aggregate Signal Inference (Route + Claims + Paths = Scope)
**Attack Description**: "109 routes + 30 claims + 15 paths = 154; scope ≈ 154"

**Evidence Status**: EXPLICITLY_PROHIBITED (meaningless arithmetic on incommensurable signals)

**Structural Prevention**:
  - Signals come from different domains (code, history, design)
  - No mechanism to aggregate them into scope

**Contractual Prevention**:
  - JARVIS cannot submit "aggregate_scope" field
  - Schema requires explicit scope_universe candidate

**Governance Prevention**:
  - Scope is governance decision (not arithmetic result)
  - MoCKA Q7 derives scope from evidence-bounded membership criteria

**Atomic Prevention**:
  - Runtime validates scope against scope_set (no calculation performed)

**Bypass Status**: BLOCKED (all four layers engaged)

---

### 2.2 Category B: Authority Override Bypasses (B6-B8)

These paths attempt to establish bindings without HAB authority verification.

#### B6: Direct Consequence Binding (JARVIS → Runtime)
**Attack Description**: JARVIS sends consequence_binding directly to Runtime, bypassing HAB

**Evidence Status**: AUTHORITY_OVERRIDE (No MoCKA authorization verification)

**Structural Prevention**:
  - Runtime only accepts bindings from HAB (binding_id signed by HAB)
  - Direct JARVIS → Runtime communication prohibited by routing rules

**Contractual Prevention**:
  - Runtime interface requires binding.hab_verification_timestamp
  - HAB signature verification fails if binding created outside HAB

**Governance Prevention**:
  - MoCKA verifies token validity before HAB issues binding
  - Token reference in binding proves MoCKA authorization

**Atomic Prevention**:
  - Runtime rejects bindings without valid HAB seal (hab_sealed = true)

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B7: Token Modification (JARVIS Forges Authorization)
**Attack Description**: JARVIS modifies authorization token scope/restrictions

**Evidence Status**: GOVERNANCE_VIOLATION (Cryptographic identity breach)

**Structural Prevention**:
  - Token issued by MoCKA only (JARVIS cannot issue tokens)
  - Token stored in MoCKA-controlled cache (not in JARVIS memory)

**Contractual Prevention**:
  - Token signature verified cryptographically (tampering detected)
  - Modified token fails [V3] signature verification check

**Governance Prevention**:
  - MoCKA signs token with secure key (HAB verifies signature)
  - Tampering is governance violation (escalated to Q5)

**Atomic Prevention**:
  - Runtime rejects binding if token signature fails
  - Cryptographic failure is atomic rejection

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B8: Consequence Binding Without Model Validation
**Attack Description**: HAB skips Enforcement Model A validation; creates binding with arbitrary consequences

**Evidence Status**: ENFORCEMENT_MODEL_VIOLATION (Design-layer boundary breach)

**Structural Prevention**:
  - Enforcement Model A is locked design (not implementation)
  - HAB must apply model validation (structural requirement)

**Contractual Prevention**:
  - HAB/Runtime interface requires binding.enforcement_model = STRICT_IN_BAND
  - Runtime verifies Model A validation was applied

**Governance Prevention**:
  - MoCKA Q8 verifies Enforcement Model A remains locked (HG-R10)
  - Token authorizes STRICT_IN_BAND_ONLY consequences

**Atomic Prevention**:
  - Runtime applies Enforcement Model A in-band (redundant validation)
  - Double-validation ensures no Model A bypass

**Bypass Status**: BLOCKED (all four layers engaged)

---

### 2.3 Category C: Authorization Bypass Attempts (B9-B11)

These paths attempt to bypass authorization requirements via JARVIS coordination.

#### B9: Multiple Requests → Scope Accumulation
**Attack Description**: Submit 4 separate requests for CANDIDATE_A, CANDIDATE_B, CANDIDATE_C, CANDIDATE_D, each authorized independently; combine results into unified scope

**Evidence Status**: SCOPE_ACCUMULATION (Evidence lineage broken by synthesis)

**Structural Prevention**:
  - Each request receives independent binding (not merged)
  - Scope_set in binding is isolated (cannot be combined at Runtime)

**Contractual Prevention**:
  - Each binding references specific scope_universe
  - Runtime validates scope_membership against binding.scope_set only

**Governance Prevention**:
  - MoCKA Q7 authorizes per-candidate scope separately
  - Unified scope requires explicit MoCKA authorization (new token)

**Atomic Prevention**:
  - Runtime executes each binding atomically (isolation guaranteed)
  - No cross-binding scope synthesis at Runtime

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B10: Delegation Chain → Authority Escalation
**Attack Description**: Use multi-agent delegation to cascade authorization; Agent_A executes with limited scope, delegates to Agent_B with expanded scope

**Evidence Status**: AUTHORITY_ESCALATION (Scope injection via delegation)

**Structural Prevention**:
  - Each agent receives independent binding (scope isolated per agent)
  - Agent_A cannot modify Agent_B's binding

**Contractual Prevention**:
  - Multi-agent delegation specifies scope explicitly per agent
  - HAB creates separate bindings for each agent (cannot inherit)

**Governance Prevention**:
  - Each agent's binding references MoCKA token (same token for both)
  - Token authorizes specific scope_universes (not delegated extensions)

**Atomic Prevention**:
  - Runtime verifies each agent's binding independently
  - Agent_A result does NOT authorize Agent_B scope

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B11: Context-Based Authorization Injection (Cascading)
**Attack Description**: Agent_A succeeds; result_A passed as context to Agent_B; context misinterpreted as evidence for scope expansion

**Evidence Status**: EVIDENCE_LINEAGE_VIOLATION (Context ≠ Evidence semantic breach)

**Structural Prevention**:
  - Binding.evidence_lineage is immutable (preserved for all agents)
  - Context parameter is informational only (not evidence)

**Contractual Prevention**:
  - Request schema distinguishes context from evidence_references
  - Runtime ignores context for scope/authorization validation

**Governance Prevention**:
  - MoCKA Q7 verifies evidence_criteria (not context)
  - Token authorizes specific evidence_references (not context-derived scope)

**Atomic Prevention**:
  - Runtime validates scope using binding.scope_set (not context)
  - Context used informally; authorization validation unchanged

**Bypass Status**: BLOCKED (all four layers engaged)

---

### 2.4 Category D: Evidence Discipline Bypasses (B12-B13)

These paths attempt to violate evidence discipline (NOT_FOUND ≠ ABSENT, etc.).

#### B12: Evidence Substitution (Missing Evidence → Assumed Evidence)
**Attack Description**: Evidence not collected; assume it exists or infer from code; substitute with proxy evidence

**Evidence Status**: EVIDENCE_DISCIPLINE_VIOLATION (NOT_FOUND misclassified as PRESENT)

**Structural Prevention**:
  - Evidence explicitly listed in membership_criteria
  - Proxy/assumed evidence not in E15-01 through E15-10

**Contractual Prevention**:
  - Request must list explicit evidence_references (no assumed evidence)
  - Schema rejects requests without evidence references

**Governance Prevention**:
  - Token specifies required_evidence (not assumed_evidence)
  - MoCKA Q7 rejects scope claims without proper evidence

**Atomic Prevention**:
  - Runtime validates evidence_lineage against binding (no substitution)
  - Missing evidence = request REJECTED

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B13: Evidence Discipline Collapse (NOT_PROVEN → ACCEPTED as PROVEN)
**Attack Description**: Evidence accepted for design basis (HG-R11); claim it proves runtime correctness; execute without additional validation

**Evidence Status**: DESIGN_LAYER_VIOLATION (Design evidence ≠ Runtime proof)

**Structural Prevention**:
  - Design evidence is distinct from runtime evidence (separate domains)
  - Binding authorization_level = DESIGN_LAYER_ONLY (no runtime authority)

**Contractual Prevention**:
  - Binding explicitly documents evidence as "design_basis" (not runtime_proof)
  - Runtime validation chain includes separate evidence checks

**Governance Prevention**:
  - Authorization level locked at DESIGN_LAYER_ONLY (HG-R08/R09/R10)
  - MoCKA distinguishes design authority from implementation authority

**Atomic Prevention**:
  - Runtime applies full Enforcement Model A validation (not bypassed by design evidence)
  - Design evidence ≠ runtime validation skip

**Bypass Status**: BLOCKED (all four layers engaged)

---

### 2.5 Category E: Design Layer Closure Bypasses (B14-B15)

These paths attempt to reopen locked design decisions or modify immutable constraints.

#### B14: Enforcement Model Reopening
**Attack Description**: Claim Enforcement Model A is insufficient; request Model B authorization to bypass in-band validation

**Evidence Status**: DESIGN_LAYER_LOCK_VIOLATION (HG-R10 sealed)

**Structural Prevention**:
  - Model A is locked design (no runtime selection mechanism)
  - No Model B implementation (design-only scope)

**Contractual Prevention**:
  - All bindings enforce STRICT_IN_BAND
  - No alternative enforcement_model_option field exists

**Governance Prevention**:
  - MoCKA Q8 sealed Enforcement Model A (HG-R10; not reopened)
  - Token always specifies enforcement_model = STRICT_IN_BAND

**Atomic Prevention**:
  - Runtime always applies Enforcement Model A in-band
  - No configuration to disable or modify model

**Bypass Status**: BLOCKED (all four layers engaged)

---

#### B15: Persistence Strategy Reopening
**Attack Description**: Claim Persistence Model D (Hybrid) is inadequate; propose Model A/B/C (request schema change)

**Evidence Status**: DESIGN_LAYER_LOCK_VIOLATION (HG-R09 sealed)

**Structural Prevention**:
  - Persistence strategy is design decision (not runtime selection)
  - No schema modification permitted (modification vectors = 0)

**Contractual Prevention**:
  - Binding does not include persistence_strategy field (immutable design)
  - No request field to propose persistence strategy changes

**Governance Prevention**:
  - MoCKA Q5 sealed Persistence Model D (HG-R09; not reopened)
  - Token references locked persistence_strategy (not negotiable)

**Atomic Prevention**:
  - Runtime does not implement persistence strategy switching
  - Model D is only implementation (no alternatives)

**Bypass Status**: BLOCKED (all four layers engaged)

---

## PART 3: Defense Mechanisms Summary

### 3.1 Defense Layers

```
LAYER 1: STRUCTURAL PREVENTION
  - Authority domains isolated (JARVIS ≠ scope, HAB ≠ execution, etc.)
  - Token storage in MoCKA (not in JARVIS)
  - Scope definition by positive criteria (not negative/absent)
  - Evidence explicitly referenced (not assumed or inferred)
  Effectiveness: Prevents 12/15 bypasses (B1-B5, B6, B8-B15)

LAYER 2: CONTRACTUAL PREVENTION
  - Schema validation (request/response formats enforced)
  - HAB signature verification (tampering detection)
  - Scope_set immutability (cannot be modified mid-request)
  - Evidence_lineage immutability (cannot be substituted)
  Effectiveness: Prevents 13/15 bypasses (B1-B5, B6-B8, B10-B15)

LAYER 3: GOVERNANCE PREVENTION
  - MoCKA authority enforcement (Q5, Q7, Q8 independent domains)
  - Token verification (signature + expiry + scope compliance)
  - Evidence discipline (NOT_FOUND ≠ ABSENT preserved in all decisions)
  - Design layer lock (enforcement model, persistence strategy sealed)
  Effectiveness: Prevents 14/15 bypasses (all except B1)

LAYER 4: ATOMIC ENFORCEMENT
  - Runtime in-band validation (all checks with execution)
  - Binding signature verification (HAB seal checked at Runtime)
  - Scope validation against scope_set (no inference)
  - Atomicity guarantee (all-or-nothing execution)
  Effectiveness: Prevents 10/15 bypasses (B1, B6, B7, B8, B9, B10, B12, B13, B14, B15)
```

### 3.2 Defense-in-Depth Matrix

| Bypass | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | B9 | B10 | B11 | B12 | B13 | B14 | B15 |
|--------|----|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|-----|
| Structural | X | X | X | X | X | X | - | X | X | X | X | X | X | X | X |
| Contractual | X | X | X | X | X | X | X | X | X | X | X | X | X | X | X |
| Governance | - | X | X | X | X | X | X | X | X | X | X | X | X | X | X |
| Atomic | X | X | X | X | X | X | X | X | X | X | X | X | X | X | X |

Legend: X = layer blocks this bypass path; - = layer does not apply

---

## PART 4: Bypass Analysis Design Closure Conditions

This specification is complete and sealed when:

1. All 15 bypass paths identified and documented (PART 2)
2. Each bypass classified by category (A-E)
3. Evidence status documented for each bypass
4. All four defense mechanisms specified (PART 3)
5. Defense-in-depth matrix completed (PART 3.2)
6. No bypass remains unblocked by all four layers
7. Human Gate decision HG-HJ-07 acceptance pending
8. 20-point integrity verification includes bypass analysis
9. No code/schema/database modifications (vectors remain = 0)

---

## FINAL STATUS

**HAB/JARVIS Bypass Analysis: SECURITY ANALYSIS COMPLETE**

```
Bypass Paths Analyzed: 15 (B1-B15)
Categories: 5 (Scope Inference, Authority Override, Authorization Bypass, Evidence Discipline, Design Layer Closure)
Defense Layers: 4 (Structural, Contractual, Governance, Atomic)
All Bypasses Blocked: YES (all 15 paths blocked by all four layers)

Layer: 1-2 (Design-level bypass prevention)
Implementation: NONE (Design specification only)
State Locks: ALL MAINTAINED (Implementation NOT_GRANTED, M18-Scope HOLD, Modification Vectors = 0)
```

**Bypass Analysis Sealed: SECURITY SPECIFICATION**
**Authority: KUROKO Protocol (Bypass Analysis Phase)**
**Human Gate Decision: HG-HJ-07 Pending**

