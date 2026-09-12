# SDR-01～04 Evidence-to-Decision Mapping

**Date**: 2026-09-12  
**Phase**: R01 Substantive Decision Execution — Evidence-to-Decision Mapping  
**Purpose**: Establish which Decision Questions can be addressed by existing Evidence, and which remain unsupported  
**Status**: MAPPING ONLY (NO DECISIONS MADE)

---

## EVIDENCE CLASSIFICATION FRAMEWORK

### E1～E8 Hierarchy
```
E1 — Existence:     対象が存在することを示すか
E2 — Definition:    formal definition を示すか
E3 — Implementation:実装されていることを示すか
E4 — Runtime Binding: runtime へ接続されているか
E5 — Scope:         対象範囲を確定するか
E6 — Authority:     誰が決定権を持つか
E7 — Verification:  correctness/completeness を検証できるか
E8 — Provenance:    Evidence lineage を再構成できるか
```

**Critical Separation Rule**:
```
Existence ≠ Definition ≠ Implementation ≠ Runtime Binding ≠ Proven
```

### Sufficiency Standard (A/B/C/D)
- **A**: SUFFICIENT FOR DECISION — Decision-level Evidence exists
- **B**: PARTIALLY SUPPORTED — Some facts supported, Decision requires more
- **C**: NOT_PROVEN — Required Evidence does not exist
- **D**: UNDEFINED — Decision target definition itself not established

**Important**: B ≠ A, C ≠ REJECTED, D ≠ FALSE

---

## SDR-01: SEMANTIC CLOSURE DEFINITION

**Authority**: HG-directed Governance Mechanism  
**Decision Domain**: CO, ActualConsequence, AuthorizedConsequence, M18-Scope relationship, Semantic Closure criteria

### SC-01: Semantic Closure — What is "closed" state?

**Evidence Found**:
- **Source**: `/home/user/MoCKA/docs/governance/o0_human_gate_semantic_terminal_v1.md`
- **Status**: DRAFT / definition only / no runtime wiring
- **Content**:
  - O0-Human Gate = terminal node of O0 observation boundary's semantic evaluation
  - Input: O0-ΔL (semantic differential evaluation) output
  - Output: closure_tag (label, not decision/permission/instruction)
  - Rule: evaluation_result ≠ execution_permission

**Evidence Type Assessment**:
- E1 (Existence): ✓ O0 Semantic Closure concept exists as draft
- E2 (Definition): ✓ Draft definition: "closure_tag = label asserting semantic difference has been observed and classified"
- E3 (Implementation): ✗ No runtime implementation
- E4 (Runtime Binding): ✗ No runtime connection
- E5 (Scope): ✓ Partial — O0 observation layer scope defined
- E6 (Authority): ✗ O0-Human Gate holds no decision authority
- E7 (Verification): ✗ No verification mechanism defined
- E8 (Provenance): ✗ No evidence lineage for M18-level closure

**What is Actually Supported**:
- O0 observation layer closure mechanism (DRAFT)
- Semantic difference classification and labeling (DRAFT)
- Isolation from decision authority (DRAFT)

**What is NOT Supported**:
- M18-level Semantic Closure (no mapping from O0 to M18)
- Runtime Semantic Closure wiring (implementation absent)
- Formal closure criteria for M18 decisions
- Authority relationship between O0 closure and M18 authority
- Closure verification at M18 scope

**Mapping Status**: **B — PARTIALLY SUPPORTED**
- O0 concept exists (DRAFT)
- M18 application = NOT_PROVEN

---

### SC-02: CO and ActualConsequence relationship

**Evidence Found**:
- **Source**: None (searched codebase and docs)
- **Status**: NOT_FOUND

**Evidence Type Assessment**:
- E1 (Existence): ✗ No "CO" definition found
- E2 (Definition): ✗ No "ActualConsequence" definition found
- E3 (Implementation): ✗ No code reference
- E4 (Runtime Binding): ✗ Not applicable
- E5 (Scope): ✗ Not applicable
- E6 (Authority): ✗ Not defined
- E7 (Verification): ✗ Not applicable
- E8 (Provenance): ✗ Not applicable

**Mapping Status**: **D — UNDEFINED**
- Term "CO" not defined
- Term "ActualConsequence" not defined
- Relationship = CANNOT_ASSESS (concepts undefined)

---

### SC-03: CO and AuthorizedConsequence relationship

**Evidence Found**:
- **Source**: None

**Evidence Type Assessment**:
- E1 (Existence): ✗ No "AuthorizedConsequence" definition found
- E2 (Definition): ✗ None
- E3-E8: ✗ Not applicable

**Mapping Status**: **D — UNDEFINED**
- Term "AuthorizedConsequence" not defined
- Relationship = CANNOT_ASSESS

---

### SC-04: M18-Scope formal relationship

**Evidence Found**:
- **Source**: None (M18 specification not found)
- **Status**: NOT_FOUND

**Evidence Type Assessment**:
- E1 (Existence): ✗ M18-Scope specification does not exist
- E2 (Definition): ✗ No formal definition
- E5 (Scope): ✗ Boundaries not specified
- E6 (Authority): ✗ Not assigned

**Mapping Status**: **D — UNDEFINED**
- M18-Scope formal boundary = UNDEFINED
- Relationship cannot be assessed without scope definition

---

### SC-05: Semantic Closure criteria

**Evidence Found**:
- **Source**: o0_human_gate_semantic_terminal_v1.md (partial)
- **Status**: Criteria for O0 exist (DRAFT); criteria for M18 not found

**Evidence Type Assessment**:
- E1 (Existence): ✓ O0 criteria exist (observation layer)
- E2 (Definition): ✓ O0 closure_tag criteria specified (DRAFT)
- E4 (Runtime Binding): ✗ Not implemented
- E5 (Scope): ✗ M18 criteria not specified
- E7 (Verification): ✗ No verification mechanism

**Mapping Status**: **B — PARTIALLY SUPPORTED**
- O0 observation layer criteria = DRAFT
- M18 closure criteria = NOT_PROVEN

---

### SC-06: Closure failure handling (UNKNOWN/UNDEFINED/NOT_PROVEN)

**Evidence Found**:
- **Source**: o0_human_gate_semantic_terminal_v1.md mentions "terminal" but no failure handling
- **Status**: Partial guidance only

**Evidence Type Assessment**:
- E1 (Existence): ✓ Closure concept exists (O0)
- E2 (Definition): ✗ Failure handling not formally defined
- E7 (Verification): ✗ No verification of incomplete closure

**Mapping Status**: **B — PARTIALLY SUPPORTED**
- O0 terminal behavior documented (DRAFT)
- Closure failure semantics = NOT_PROVEN
- UNKNOWN/UNDEFINED preservation mechanism = NOT_PROVEN

---

## SDR-01 SUMMARY

| SC | Evidence | Type | Sufficiency | Gap |
|----|----------|------|-------------|----|
| SC-01 | o0_human_gate Draft | E1,E2,E5 (partial) | B | M18 mapping missing |
| SC-02 | None | NONE | D | CO undefined |
| SC-03 | None | NONE | D | AuthorizedConsequence undefined |
| SC-04 | None | NONE | D | M18-Scope undefined |
| SC-05 | o0_human_gate Draft | E1,E2 (partial) | B | M18 criteria missing |
| SC-06 | o0_human_gate Draft | E1,E2 (partial) | B | Failure handling not defined |

**SDR-01 Mapping Status**: MIXED / B,D,B,D,B,B  
**Questions addressable by Evidence**: SC-01, SC-05, SC-06 (at O0 layer only)  
**Questions NOT_PROVEN**: SC-02, SC-03, SC-04 (concepts undefined)

---

## SDR-02: QUANTIFICATION NECESSITY

**Authority**: Human Gate  
**Decision Domain**: 15 Consequential Paths necessity, relationship to 30/109 routes, selection principle

### Critical Pre-Assessment: 109 / 30 / 15

**Evidence Matrix**:

| Object | Status | Evidence | Classification |
|--------|--------|----------|-----------------|
| **109 Flask routes** | OBSERVED | `grep "@app.route" app.py` count=109 | E1 (Existence) |
| **30 routes** | PRIOR ASSERTION | Not found in current codebase | UNVERIFIED |
| **15 Paths** | NOT_FOUND | No Evidence of existence or necessity | UNDEFINED |
| **M18-Scope universe** | UNDEFINED | No specification | D (UNDEFINED) |

**Relationship Evidence**:

| Relationship | Evidence | Status |
|---|---|---|
| 109 → 30 | Does 30 constitute M18-Scope subset of 109? | NOT_ESTABLISHED |
| 30 → 15 | Does 15 Paths come from 30 routes selection? | NOT_ESTABLISHED |
| 109 → 15 | Does 15 Paths come from 109 routes selection? | NOT_ESTABLISHED |

**Critical Rule Application**:
```
109 routes OBSERVED
    ≠
30 routes CONFIRMED

30 routes UNVERIFIED
    ≠
30 routes FALSE

15 Paths NOT_FOUND
    ≠
15 Paths UNNECESSARY
```

---

### QN-01: Should 15 Paths be adopted as requirement?

**Evidence Found**:
- **Source**: None (no specification of 15 Paths)
- **Status**: NOT_FOUND

**Evidence Type**:
- E1 (Existence): ✗ 15 Paths specification not found
- E2 (Definition): ✗ Not defined
- E5 (Scope): ✗ Not established
- E6 (Authority): ✗ No authority assignment

**Mapping Status**: **C — NOT_PROVEN**
- No Evidence that 15 Paths exists
- No Evidence of necessity
- No Authority assignment for adoption

---

### QN-02: Relationship between 30 routes and 15 Paths

**Evidence Found**:
- **Source 1**: 109 Flask routes in app.py (OBSERVED)
- **Source 2**: "30 routes" mentioned in instructions (PRIOR ASSERTION, unverified)
- **Source 3**: "15 Paths" in instructions (PRIOR ASSERTION, unverified)
- **Status**: RELATIONSHIP NOT_ESTABLISHED

**Evidence Type**:
- E1 (Existence): ✓ 109 routes exist; 30 unverified; 15 undefined
- E5 (Scope): ✗ Relationship between 30 and 15 not specified
- E8 (Provenance): ✗ No algorithm connecting 30 → 15

**Mapping Status**: **C — NOT_PROVEN**
- Numbers exist in instructions (prior assertion)
- Actual relationship = NOT_ESTABLISHED

---

### QN-03: Selection principle (30 → 15)

**Evidence Found**:
- **Source**: None
- **Status**: NOT_FOUND

**Evidence Type**:
- E1 (Existence): ✗ No selection algorithm
- E2 (Definition): ✗ No principle defined
- E5 (Scope): ✗ No universe defined

**Mapping Status**: **C — NOT_PROVEN**

---

### QN-04: Alternative quantification units

**Evidence Found**:
- **Source**: 109 Flask routes (alternative to 30)
- **Status**: EVIDENCE EXISTS but alternative not formally proposed

**Evidence Type**:
- E1 (Existence): ✓ 109 routes exist as observable unit
- E2 (Definition): ✗ "Consequential Path" definition not provided
- E5 (Scope): ✗ What constitutes quantification unit not defined

**Mapping Status**: **B — PARTIALLY SUPPORTED**
- Alternative quantity observable (109)
- Alternative principle = NOT_PROVEN

---

### QN-05: Final quantification unit

**Evidence Found**:
- None (no specification of final unit)

**Mapping Status**: **C — NOT_PROVEN**

---

### QN-06: Closure principle for quantification universe

**Evidence Found**:
- None (no universe closure specification)

**Mapping Status**: **C — NOT_PROVEN**

---

## SDR-02 SUMMARY

| QN | Evidence | Type | Sufficiency | Gap |
|----|----------|------|-------------|----|
| QN-01 | None | NONE | C | 15 Paths NOT_FOUND |
| QN-02 | 109 routes observed; 30/15 unverified | E1 (partial) | C | Relationship NOT_ESTABLISHED |
| QN-03 | None | NONE | C | Selection algorithm missing |
| QN-04 | 109 routes exist | E1 | B | Alternative principle undefined |
| QN-05 | None | NONE | C | No specification |
| QN-06 | None | NONE | C | Closure principle missing |

**SDR-02 Mapping Status**: CRITICAL GAP / C,C,C,B,C,C  
**Critical Discovery**: 109 Flask routes ≠ 30 routes (premise unverified)  
**Questions addressable**: QN-04 (only: 109 routes observable)  
**Questions NOT_PROVEN**: QN-01, QN-02, QN-03, QN-05, QN-06

---

## SDR-03: M18-SCOPE BOUNDARY

**Authority**: Human Gate  
**Decision Domain**: M18-Scope formal boundary, closure rules

### SB-01: M18-Scope boundary definition

**Evidence Found**:
- **Source**: None (M18 specification not found)
- **Status**: NOT_FOUND

**Evidence Type**:
- E1 (Existence): ✗ M18-Scope not defined
- E2 (Definition): ✗ Boundary rules not specified
- E5 (Scope): ✗ Not established
- E7 (Verification): ✗ No verification method

**Mapping Status**: **D — UNDEFINED**

---

### SB-02: route / endpoint vs operation / mutation relationship

**Evidence Found**:
- **Source 1**: 109 Flask routes (app.py) — OBSERVED
- **Source 2**: No operation/mutation specification
- **Status**: PARTIAL

**Evidence Type**:
- E1 (Existence): ✓ Routes exist (109); operations/mutations not enumerated
- E2 (Definition): ✗ Relationship between route and operation not defined
- E5 (Scope): ✗ Scope inclusion criteria not specified

**Important Separation**:
```
109 routes OBSERVED
    ≠
109 routes IN M18-SCOPE

Route EXISTS
    ≠
Route IS CONSEQUENTIAL
    ≠
Route IS IN M18-SCOPE
```

**Mapping Status**: **B — PARTIALLY SUPPORTED**
- Routes observable (109)
- Route → operation/mutation mapping = NOT_ESTABLISHED
- Scope membership = NOT_PROVEN

---

### SB-03: Database mutation inclusion criteria

**Evidence Found**:
- **Source**: None (no specification)
- **Status**: NOT_FOUND

**Mapping Status**: **D — UNDEFINED**

---

### SB-04: External side effect inclusion criteria

**Evidence Found**:
- **Source**: None
- **Status**: NOT_FOUND

**Mapping Status**: **D — UNDEFINED**

---

### SB-05: Scope completeness verification

**Evidence Found**:
- **Source**: None
- **Status**: NOT_FOUND

**Mapping Status**: **D — UNDEFINED**

---

### SB-06: Unknown/unverified object handling

**Evidence Found**:
- **Source**: None (no specification of handling strategy)
- **Status**: NOT_FOUND

**Evidence Type**:
- E2 (Definition): ✗ No handling rules defined
- E7 (Verification): ✗ No completeness verification possible

**Mapping Status**: **C — NOT_PROVEN**
- Default behavior undefined
- "NOT FOUND ≠ ABSENT" principle stated in instructions but not operationalized

---

## SDR-03 SUMMARY

| SB | Evidence | Type | Sufficiency | Gap |
|----|----------|------|-------------|----|
| SB-01 | None | NONE | D | M18-Scope undefined |
| SB-02 | 109 routes | E1 (partial) | B | Route→operation mapping missing |
| SB-03 | None | NONE | D | DB mutation criteria missing |
| SB-04 | None | NONE | D | External side effect criteria missing |
| SB-05 | None | NONE | D | Completeness verification missing |
| SB-06 | None | NONE | C | Unknown handling not defined |

**SDR-03 Mapping Status**: FOUNDATIONAL GAP / D,B,D,D,D,C  
**Addressable Questions**: SB-02 (partially: routes observable)  
**NOT_PROVEN**: SB-01, SB-03, SB-04, SB-05, SB-06

---

## SDR-04: PER-ROUTE AUTHORIZATION SEMANTICS

**Authority**: Governance / Human Gate  
**Decision Domain**: Per-route instantiation of ActualConsequence, AuthorizedConsequence, Authorization Scope

### RS-01: ActualConsequence per-route instantiation

**Evidence Found**:
- **Source**: None (ActualConsequence not defined; no per-route framework)
- **Status**: NOT_FOUND

**Evidence Type**:
- E1 (Existence): ✗ ActualConsequence not defined (see SDR-01 SC-02)
- E2 (Definition): ✗ Per-route instantiation framework not found
- E5 (Scope): ✗ Route enumeration present (109) but instantiation rules absent

**Mapping Status**: **D — UNDEFINED**
- Cannot instantiate undefined concept
- Per-route framework = NOT_FOUND

---

### RS-02: AuthorizedConsequence per-route instantiation

**Evidence Found**:
- **Source**: None
- **Status**: NOT_FOUND

**Mapping Status**: **D — UNDEFINED**

---

### RS-03: Authorization Scope per-route handling

**Evidence Found**:
- **Source 1**: Q5/Q8 Authority Boundary Clarification (R01 Decision Record)
  - Q5 = Global / Formal Semantic Decision Domain
  - Q8 = Per-route Instantiation / Application Domain
- **Source 2**: No per-route authorization semantics framework found

**Evidence Type**:
- E1 (Existence): ✓ Authority boundary assignment exists (Q8 for per-route)
- E2 (Definition): ✗ Per-route Authorization Scope definition missing
- E3 (Implementation): ✗ No framework implementation

**Mapping Status**: **B — PARTIALLY SUPPORTED**
- Authority assignment (Q8) established
- Actual Authorization Scope per-route = NOT_PROVEN

---

### RS-04: Actual vs Authorized verification relation

**Evidence Found**:
- **Source**: None (both concepts undefined; no verification framework)
- **Status**: NOT_FOUND

**Mapping Status**: **D — UNDEFINED**

---

### RS-05: Route-level Evidence requirement

**Evidence Found**:
- **Source**: None (no audit/verification framework for routes)
- **Status**: NOT_FOUND

**Mapping Status**: **C — NOT_PROVEN**

---

### RS-06: 30-route audit evidence evaluation

**Evidence Found**:
- **Source 1**: 109 Flask routes observed (not 30 as specified)
- **Source 2**: No audit framework for routes
- **Status**: DISCREPANCY + NOT_FOUND

**Evidence Type**:
- E1 (Existence): ✓ 109 routes exist
- E5 (Scope): ✗ "30 routes" specification unverified
- E7 (Verification): ✗ No audit framework

**Mapping Status**: **C — NOT_PROVEN**
- 30 routes premise unverified (109 found instead)
- Audit framework = NOT_FOUND

---

### RS-07: FAIL/UNKNOWN/NOT_PROVEN route-level handling

**Evidence Found**:
- **Source**: None (no per-route failure handling specification)
- **Status**: NOT_FOUND

**Mapping Status**: **C — NOT_PROVEN**

---

## SDR-04 SUMMARY

| RS | Evidence | Type | Sufficiency | Gap |
|----|----------|------|-------------|----|
| RS-01 | None | NONE | D | ActualConsequence undefined |
| RS-02 | None | NONE | D | AuthorizedConsequence undefined |
| RS-03 | Q8 Authority assigned | E1 (partial) | B | Per-route semantics missing |
| RS-04 | None | NONE | D | Verification relation undefined |
| RS-05 | None | NONE | C | Evidence requirement missing |
| RS-06 | 109 routes; no audit | E1 (partial) | C | Audit framework missing |
| RS-07 | None | NONE | C | Failure handling missing |

**SDR-04 Mapping Status**: FOUNDATIONAL + FRAMEWORK GAP / D,D,B,D,C,C,C  
**Addressable Questions**: RS-03 (partially: Q8 authority established)  
**NOT_PROVEN**: RS-01, RS-02, RS-04, RS-05, RS-06, RS-07

---

## CROSS-SDR EVIDENCE RELATIONSHIPS

### Observed Evidence Relationships:

```
SDR-01 (Semantic Closure DRAFT exists)
    ↕
    May inform SDR-03 (M18-Scope needs closure definition)
    Evidence Relationship = OBSERVED
    Decision Dependency = NOT_ESTABLISHED

M18-Scope universe (SDR-03)
    ↕
    May inform 15 Paths selection (SDR-02)
    Evidence Relationship = OBSERVED
    Decision Dependency = NOT_ESTABLISHED

ActualConsequence definition (SDR-01)
    ↕
    Required for per-route instantiation (SDR-04)
    Evidence Relationship = LOGICAL NECESSITY
    Decision Dependency = NOT_ESTABLISHED
```

**Critical Note**: Evidence relationships observed ≠ Decision dependencies established.  
Decision dependencies require:
1. Explicit specifications
2. Formal Decision Records
3. Authority assignments
4. Equivalent binding Evidence

**Current Status**: EVIDENCE RELATIONSHIPS OBSERVED / DECISION DEPENDENCIES NOT_ESTABLISHED

---

## MASTER EVIDENCE-TO-DECISION MATRIX

### Sufficiency Summary by SDR:

```
SDR-01 (Semantic Closure)
    SC-01: B (O0 DRAFT, M18 mapping missing)
    SC-02: D (CO undefined)
    SC-03: D (AuthorizedConsequence undefined)
    SC-04: D (M18-Scope undefined)
    SC-05: B (O0 criteria DRAFT, M18 missing)
    SC-06: B (O0 behavior DRAFT, failure handling missing)
    
    Overall: MIXED / Requires Definitions (SC-02, SC-03, SC-04)

SDR-02 (Quantification Necessity)
    QN-01: C (15 Paths NOT_FOUND)
    QN-02: C (30/15 relationship NOT_ESTABLISHED)
    QN-03: C (Selection algorithm NOT_FOUND)
    QN-04: B (109 routes observable; principle undefined)
    QN-05: C (No specification)
    QN-06: C (Closure principle missing)
    
    Overall: CRITICAL GAP / 109 routes ≠ 30 premises unverified

SDR-03 (M18-Scope Boundary)
    SB-01: D (M18-Scope undefined)
    SB-02: B (109 routes observable; mapping rules missing)
    SB-03: D (DB mutation criteria missing)
    SB-04: D (External side effect criteria missing)
    SB-05: D (Completeness verification missing)
    SB-06: C (Unknown handling not defined)
    
    Overall: FOUNDATIONAL MISSING / Scope definition required

SDR-04 (Per-route Authorization Semantics)
    RS-01: D (ActualConsequence undefined)
    RS-02: D (AuthorizedConsequence undefined)
    RS-03: B (Q8 authority; per-route framework missing)
    RS-04: D (Verification relation undefined)
    RS-05: C (Evidence requirement missing)
    RS-06: C (30-route premise unverified; framework missing)
    RS-07: C (Failure handling not defined)
    
    Overall: FOUNDATIONAL + FRAMEWORK MISSING / Concepts undefined
```

---

## KEY GAPS REQUIRING DECISION

| Gap | Affects | Status | Impact |
|-----|---------|--------|--------|
| **CO definition** | SDR-01 SC-02 | UNDEFINED | Cannot assess ActualConsequence |
| **ActualConsequence definition** | SDR-01, SDR-04 | UNDEFINED | Cannot instantiate per-route |
| **AuthorizedConsequence definition** | SDR-01, SDR-04 | UNDEFINED | Cannot instantiate per-route |
| **M18-Scope specification** | SDR-02, SDR-03, SDR-04 | UNDEFINED | Cannot determine universe |
| **30 routes verification** | SDR-02, SDR-03 | UNVERIFIED | 109 found vs 30 specified |
| **15 Paths justification** | SDR-02 | NOT_PROVEN | No algorithm for selection |
| **Per-route framework** | SDR-04 | NOT_FOUND | No instantiation mechanism |

---

## CONCLUSION

**Evidence-to-Decision Mapping Complete**

### Addressable Questions by Current Evidence:
- **SDR-01**: SC-01, SC-05, SC-06 (O0 observation layer only)
- **SDR-02**: QN-04 (109 routes observable)
- **SDR-03**: SB-02 (routes observable; mapping rules missing)
- **SDR-04**: RS-03 (Q8 authority established; framework missing)

### Foundational Gaps Preventing Full Mapping:
- **Undefined concepts**: CO, ActualConsequence, AuthorizedConsequence
- **Missing scopes**: M18-Scope, quantification universe
- **Unverified premises**: 30 routes (109 found), 15 Paths necessity
- **Absent frameworks**: Per-route authorization semantics, verification mechanisms

### Next Phase Prerequisite:
Before Substantive Decisions can be made on SDR-01～04, the following Evidence gaps must be addressed:

```
Define: CO, ActualConsequence, AuthorizedConsequence
Specify: M18-Scope formal boundary
Verify or revise: 30 routes premise (109 Flask routes currently)
Justify or revise: 15 Paths necessity (NOT_PROVEN)
Design: Per-route authorization framework (not found)
```

**Current State**: MAPPING COMPLETE / DECISION PREREQUISITE NOT MET

---

**Document State**: SEALED / READY FOR REVIEW

**Locked State Maintained**:
```
N14R Necessity       = NOT_PROVEN / LOCKED
M18 Runtime Closure  = NOT_ACHIEVED / LOCKED
C2-b                 = BLOCK / LOCKED
Implementation Auth. = NOT_GRANTED
System               = HOLD / FAIL-CLOSED
```

