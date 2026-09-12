# SDR-04: Per-route Authorization Semantics — Substantive Decision Record

**Decision ID**: R01-SDR-04-20260912-001  
**Gate**: R01 SDR-04 Substantive Decision Execution  
**Date**: 2026-09-12  
**Session**: claude/q5-q8-authority-boundary-1xhfoh  
**Status**: DECISION RECORD — SEALED

**Authority**: Q8 / Governance / Human Gate / Per-route Instantiation / Application Domain

---

## EXECUTIVE SUMMARY

SDR-04 addresses per-route instantiation of ActualConsequence, AuthorizedConsequence, Authorization Scope, and per-route authorization verification semantics. Seven decision questions (RS-01～RS-07) evaluate per-route authorization framework establishment against evidence baseline.

**Critical Evidence Fact**:
```
Q8 Authority ASSIGNED for per-route instantiation (R01 BC Decision)
    ≠
Per-route Authorization Semantics DEFINED

Authority ownership (governance fact)
    ≠
Semantic content (specification requirement)
```

**Overall Decision Status**: FOUNDATIONAL / 4 UNRESOLVED / 3 HOLD

---

## CRITICAL SEPARATION ENFORCEMENT

**Maintained Distinctions**:

```text
Q8 Authority ASSIGNED (E6 Governance Fact — R01 BC-01 established)
    ≠
Per-route Authorization Semantics DEFINED (E2 Specification — NOT established)

Authority = WHO decides
Semantics = WHAT the decision domain contains
Framework = HOW per-route decisions are operationalized

R01 established WHO.
SDR-04 must establish WHAT.
Neither has established HOW.
```

**Forbidden Inferences**:
- Q8 authority assigned → Authorization semantics defined (REJECTED)
- Q8 authority assigned → Per-route framework implemented (REJECTED)
- Routes exist → Authorization semantics for routes (REJECTED)
- Authority assignment → Implementation authorized (REJECTED)

---

## DECISION MATRIX

### RS-01: Per-route ActualConsequence instantiation

**Decision Question**: How should ActualConsequence be formally instantiated at per-route level?

**Authority**: Q8 (Governance / Human Gate, Per-route Instantiation Domain)

**Evidence Summary**:
- **Source 1**: ActualConsequence not defined (SDR-01 SC-02 UNRESOLVED)
- **Source 2**: No per-route instantiation framework found
- **Evidence Type**: NONE (prerequisite missing)
- **Sufficiency Classification**: D — UNDEFINED
- **Observation**: Base concept (ActualConsequence) undefined at global level.

**What Evidence Supports**: NOTHING

**What Evidence Does NOT Support**:
- Per-route ActualConsequence instantiation rules
- Relationship between global definition and per-route application
- Route-specific consequence classification
- Verification mechanism for route-level consequences
- Authorization binding to route consequences

**Uncertainty**: ActualConsequence concept itself undefined; instantiation impossible.

**UNKNOWN/UNDEFINED Preservation**: Per-route ActualConsequence instantiation remains UNDEFINED.

**Decision**: **UNRESOLVED**

**Rationale**:
Cannot instantiate undefined concept. SDR-01 SC-02 explicitly leaves ActualConsequence UNRESOLVED. Per-route instantiation is logically downstream of global definition.

Requires prerequisite:
1. **SDR-01 SC-02 Resolution**: Global definition of ActualConsequence
2. **Instantiation Rules**: Framework for per-route application
3. **Consequence Classification**: Criteria for route-specific consequences
4. **Verification Method**: How to verify per-route consequences

**Implementation Impact**: NONE

**Authorization Impact**: NONE

**Conditions**: Contingent on:
1. SDR-01 ActualConsequence definition
2. Per-route instantiation framework specification

---

### RS-02: Per-route AuthorizedConsequence instantiation

**Decision Question**: How should AuthorizedConsequence be formally instantiated at per-route level?

**Authority**: Q8 (Governance / Human Gate)

**Evidence Summary**:
- **Source 1**: AuthorizedConsequence not defined (SDR-01 SC-03 UNRESOLVED)
- **Source 2**: No per-route instantiation framework found
- **Evidence Type**: NONE (prerequisite missing)
- **Sufficiency Classification**: D — UNDEFINED
- **Observation**: Base concept undefined at global level.

**What Evidence Supports**: NOTHING

**What Evidence Does NOT Support**:
- Per-route AuthorizedConsequence instantiation
- Relationship to authorization framework
- Route-specific authorization classification
- Verification mechanism

**Uncertainty**: AuthorizedConsequence concept undefined; instantiation impossible.

**UNKNOWN/UNDEFINED Preservation**: Per-route AuthorizedConsequence instantiation remains UNDEFINED.

**Decision**: **UNRESOLVED**

**Rationale**:
Cannot instantiate undefined concept. SDR-01 SC-03 leaves AuthorizedConsequence UNRESOLVED. Per-route instantiation requires global definition as prerequisite.

**Implementation Impact**: NONE

**Authorization Impact**: NONE

**Conditions**: Contingent on SDR-01 AuthorizedConsequence definition.

---

### RS-03: Per-route Authorization Scope instantiation

**Decision Question**: How should Authorization Scope be formally instantiated at per-route level?

**Authority**: Q8 (Governance / Human Gate)

**Evidence Summary**:
- **Source 1**: Q8 Authority assigned (R01 BC-01 DECIDED)
- **Source 2**: NO per-route authorization semantics framework found
- **Evidence Type**: E6 (Authority assignment—governance fact), NONE (semantics specification)
- **Sufficiency Classification**: C — NOT_PROVEN
- **Observation**: Authority ownership established; semantic content missing.

**What Evidence Supports**:
- Q8 owns per-route instantiation domain (R01 established)
- Authority structure defined (governance fact)

**What Evidence Does NOT Support**:
- Per-route Authorization Scope definition
- What per-route authorization semantics contain
- How authorization is instantiated per route
- Verification mechanism for per-route authorization
- Relationship between global Q5 framework and Q8 per-route application
- Routes-to-authorization mapping

**Critical Evidence Distinction**:
```
Authority ASSIGNED (Q8 owns per-route layer)
    = Governance Fact (E6)
    = Established by R01 BC-01

Per-route Authorization Semantics DEFINED
    = Specification Fact (E2)
    = NOT established; UNDEFINED

WHO decides ≠ WHAT the decision contains
```

**Uncertainty**: Authority structure clear; semantic content undefined.

**UNKNOWN/UNDEFINED Preservation**: Per-route authorization semantics remain UNDEFINED.

**Decision**: **HOLD / NOT_PROVEN**

**Rationale**:
R01 established WHO (Q8) decides on per-route authorization. SDR-04 must establish WHAT per-route authorization semantics are. Authority assignment is a governance fact (accomplished); semantic definition is a specification requirement (not accomplished).

Cannot instantiate per-route Authorization Scope without:

1. **Global Definition** (SDR-01): What is Authorization Scope globally?
2. **M18-Scope Definition** (SDR-03): What is the universe to which authorization applies?
3. **Per-route Framework**: Rules for instantiating global Authorization Scope at route level
4. **Verification Method**: How to verify per-route authorization
5. **Route-to-Scope Mapping**: Which routes fall under which authorization scopes

Authority ownership ≠ Semantic content.

**Implementation Impact**: NONE

**Authorization Impact**: NONE (authority assignment ≠ implementation authorization)

**Conditions**: Can be decided upon:
1. Global Authorization Scope definition (SDR-01)
2. M18-Scope boundary (SDR-03)
3. Per-route instantiation framework
4. Route classification methodology

---

### RS-04: Actual vs Authorized consequence verification

**Decision Question**: What is the formal relationship between ActualConsequence and AuthorizedConsequence at per-route level? How are they verified and balanced?

**Authority**: Q8 (Governance / Human Gate)

**Evidence Summary**:
- **Source 1**: ActualConsequence not defined (SDR-01 SC-02)
- **Source 2**: AuthorizedConsequence not defined (SDR-01 SC-03)
- **Source 3**: No verification framework found
- **Evidence Type**: NONE (prerequisites missing)
- **Sufficiency Classification**: D — UNDEFINED
- **Observation**: Both base concepts undefined; verification relationship cannot be established.

**What Evidence Supports**: NOTHING

**What Evidence Does NOT Support**:
- Verification relationship
- Conflict resolution (when Actual ≠ Authorized)
- Decision rules for mismatches
- Verification methodology
- Authority protocol when verification fails

**Uncertainty**: Both concepts undefined; relationship undeterminable.

**UNKNOWN/UNDEFINED Preservation**: Verification relationship remains UNDEFINED.

**Decision**: **UNRESOLVED**

**Rationale**:
Cannot establish relationship between undefined concepts. Both ActualConsequence and AuthorizedConsequence must be formally defined (SDR-01) before per-route verification can be designed (SDR-04).

**Implementation Impact**: NONE

**Authorization Impact**: NONE

**Conditions**: Contingent on SDR-01 definitions of both concepts.

---

### RS-05: Per-route authorization evidence requirements

**Decision Question**: What are the evidence requirements for establishing per-route authorization? What must be proven for each route?

**Authority**: Q8 (Governance / Human Gate)

**Evidence Summary**:
- **Source**: NONE (no audit or verification framework)
- **Evidence Type**: NONE
- **Sufficiency Classification**: C — NOT_PROVEN
- **Observation**: Evidence requirements for per-route authorization not specified.

**What Evidence Supports**: NOTHING

**What Evidence Does NOT Support**:
- Evidence types required per route
- Proof standards for authorization
- Audit methodology
- Verification completeness criteria
- Failure scenarios (what happens if evidence is insufficient?)

**Uncertainty**: Evidence requirements undefined; audit framework missing.

**UNKNOWN/UNDEFINED Preservation**: Per-route evidence requirements remain UNDEFINED.

**Decision**: **HOLD / NOT_PROVEN**

**Rationale**:
Cannot establish evidence requirements without:

1. **Per-route Authorization Semantics** (RS-03): What is being verified?
2. **Evidence Framework**: What types of evidence establish authorization?
3. **Sufficiency Criteria**: How much evidence is "enough"?
4. **Audit Protocol**: Formal procedure for evidence evaluation
5. **Review Trigger**: When/how are per-route authorizations reviewed?

**Implementation Impact**: NONE

**Authorization Impact**: NONE

**Conditions**: Contingent on RS-03 per-route authorization definition.

---

### RS-06: 30-route audit protocol applicability

**Decision Question**: Can the "30-route audit protocol" be adopted for per-route authorization evaluation?

**Authority**: Q8 (Governance / Human Gate)

**Evidence Summary**:
- **Source 1**: 30 routes assertion (UNVERIFIED—SDR-02 QN-05 REJECTED)
- **Source 2**: 109 Flask routes observed (OBSERVED—not 30)
- **Source 3**: No audit framework found
- **Evidence Type**: E1 (routes exist), NONE (30-route specification)
- **Sufficiency Classification**: C — NOT_PROVEN
- **Observation**: 30 routes premise unverified; audit framework absent.

**What Evidence Supports**:
- 109 routes are observable and enumerable

**What Evidence Does NOT Support**:
- 30 routes specification validity
- 30 routes subset of 109 routes
- 30-route audit protocol specification
- Why 30 routes should be audited (consequence/importance criteria)
- Audit methodology
- What "audit protocol" means operationally

**Critical Evidence Fact**:
```
30 routes assertion (PRIOR)
    vs.
109 routes OBSERVED (CURRENT)
    vs.
No audit framework specification
```

**Uncertainty**: 30 routes premise unverified; audit protocol missing.

**UNKNOWN/UNDEFINED Preservation**: 30-route protocol applicability remains UNDEFINED.

**Decision**: **HOLD / NOT_PROVEN**

**Rationale**:
SDR-02 QN-05 DECIDED/REJECTED the 30 routes assertion as unverified. Cannot adopt an unverified premise as basis for audit protocol.

Additionally:
- No audit framework specification exists
- "Which 30 of 109" is not defined
- Audit criteria not specified
- Success/failure conditions not defined

Would require:
1. **SDR-02 Resolution**: Clarification of quantification approach
2. **Audit Framework**: Formal specification of audit methodology
3. **Route Selection Criteria**: How to determine which routes to audit
4. **Verification Standards**: What evidence is required per route

**Implementation Impact**: NONE

**Authorization Impact**: NONE

**Conditions**: Can be revisited upon:
1. Quantification approach clarification (SDR-02)
2. Audit framework specification
3. Route selection methodology

---

### RS-07: FAIL / UNKNOWN / NOT_PROVEN handling per-route

**Decision Question**: How should FAIL / UNKNOWN / NOT_PROVEN authorization states be handled at per-route level?

**Authority**: Q8 (Governance / Human Gate)

**Evidence Summary**:
- **Source**: NONE (no per-route failure handling specification)
- **Evidence Type**: NONE
- **Sufficiency Classification**: C — NOT_PROVEN
- **Observation**: Default behavior for authorization failure undefined.

**What Evidence Supports**: NOTHING

**What Evidence Does NOT Support**:
- Failure handling rules
- Default behavior when authorization cannot be established
- Decision protocol for FAIL state
- Route blocking/enabling rules
- Escalation triggers
- System behavior when authorization is NOT_PROVEN

**Uncertainty**: Failure scenarios undefined; handling strategy missing.

**UNKNOWN/UNDEFINED Preservation**: Per-route failure handling remains UNDEFINED.

**Decision**: **HOLD / NOT_PROVEN**

**Rationale**:
Cannot establish failure handling without:

1. **Per-route Authorization Definition** (RS-03): What constitutes successful authorization?
2. **Failure Classification**: What are the possible failure states?
3. **Default Behavior**: What happens when authorization cannot be established?
4. **Safety Semantics**: Is default DENY (fail-closed) or ALLOW (fail-open)?
5. **Escalation Protocol**: When to escalate to Human Gate?

System behavior in failure states must be explicitly defined to ensure safety.

**Implementation Impact**: NONE

**Authorization Impact**: NONE

**Conditions**: Contingent on RS-03 per-route authorization definition and system safety requirements.

---

## SDR-04 DECISION SUMMARY

| RS | Decision Status | Decision | Evidence | Sufficiency |
|----|---|---|---|---|
| RS-01 | UNRESOLVED | Cannot instantiate undefined ActualConsequence | NONE | D |
| RS-02 | UNRESOLVED | Cannot instantiate undefined AuthorizedConsequence | NONE | D |
| RS-03 | HOLD / NOT_PROVEN | Authority assigned; semantics undefined | E6 (partial) | C |
| RS-04 | UNRESOLVED | Verification relation undefined; concepts undefined | NONE | D |
| RS-05 | HOLD / NOT_PROVEN | Evidence requirements not specified | NONE | C |
| RS-06 | HOLD / NOT_PROVEN | 30-route premise rejected; framework missing | E1 (partial) | C |
| RS-07 | HOLD / NOT_PROVEN | Failure handling specification missing | NONE | C |

**SDR-04 Overall Status**: FOUNDATIONAL / 4 UNRESOLVED / 3 HOLD

**Key Preserved Facts**:
- Q8 Authority ASSIGNED for per-route instantiation (R01 BC-01 preserved)
- ActualConsequence undefined at global level (prerequisite missing—not rejected)
- AuthorizedConsequence undefined at global level (prerequisite missing—not rejected)
- Per-route authorization semantics UNDEFINED (open for specification)
- 30-route audit premise REJECTED as unverified (SDR-02 QN-05)
- Failure handling NOT_PROVEN (not rejected—open for specification)

**Independence**: RS decisions are prerequisite-driven. RS-01/RS-02/RS-04 depend on SDR-01 resolutions. RS-03/RS-05/RS-07 depend on per-route framework specification. RS-06 depends on SDR-02 quantification clarity.

---

## CRITICAL AUDIT: AUTHORITY ≠ SEMANTICS

**Post-Decision Verification**:

```text
Q8 Authority ASSIGNED (R01 BC-01 established)
    = Governance Fact (WHO)
    = Preserved and binding

Per-route Authorization Semantics DEFINED
    = Specification Fact (WHAT)
    = NOT established; UNDEFINED

Authority assignment ≠ Semantic definition
WHO decides ≠ WHAT the decision contains
Governance structure ≠ Operational framework
```

**Safeguard**: This decision explicitly prevents inference from "Q8 has authority for per-route" to "per-route authorization semantics are defined." Authority ownership is necessary but not sufficient for semantic definition.

---

## PREREQUISITE DEPENDENCIES

```text
RS-01 ← SDR-01 SC-02 (ActualConsequence definition)
RS-02 ← SDR-01 SC-03 (AuthorizedConsequence definition)
RS-03 ← SDR-01 SC-04 + SDR-03 SB-01 (Authorization Scope + M18-Scope)
RS-04 ← RS-01 + RS-02 (both concepts must be defined)
RS-05 ← RS-03 (per-route framework must exist first)
RS-06 ← SDR-02 (quantification approach must be clarified)
RS-07 ← RS-03 (authorization definition must precede failure handling)
```

All RS decisions are downstream. No per-route instantiation can proceed until prerequisite global definitions are established.

---

## LOCKED STATE MAINTENANCE

```
N14R Necessity              = NOT_PROVEN / LOCKED
M18 Runtime Closure         = NOT_ACHIEVED / LOCKED
Authority→Runtime Binding   = BROKEN / LOCKED
C2-b                        = BLOCK / LOCKED
Implementation Authorization= NOT_GRANTED
Production Modification     = 0
System                      = HOLD / FAIL-CLOSED
```

---

## SIGNATURE & SEAL

**Decision Rendered By**: KUROKO (SDR-04 Substantive Decision Executor)  
**Session**: claude/q5-q8-authority-boundary-1xhfoh  
**Date**: 2026-09-12  
**Sealed**: YES

**No Code Modification**: 0 bytes  
**No Schema Modification**: 0 bytes  
**No Implementation**: NOT_GRANTED  

**All Locked States**: PRESERVED

---

**Document State**: SEALED / READY FOR INTEGRATION

