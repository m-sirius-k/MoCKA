# KUROKO WEB — ROUND 3
# FORMAL CLAIM BOUNDARY STRIKE

**Date**: 2026-09-17  
**Phase**: Round 3 — Claim-by-Claim Formal Boundary Analysis  
**Principle**: Coverage mapping; no novelty verdicts; boundaries only  

---

## PAPER 4 CLAIMS

### CLAIM P4-C1: Authorization-to-Effect Chain

**CLAIM DEFINITION** (inferred from formalization context):

MoCKA asserts that authorization decisions can be formalized as a complete chain:

```
Evidence → Decision → Authorization → Execution State
```

where each link is formally defined, verifiable, and temporally bound. Authorization is not merely a permission grant, but a traceable state transition that connects input evidence through decision logic to execution effects.

---

#### A. MOCKA CLAIM

A formal proof object demonstrating:
1. Evidential sufficiency for a specific decision
2. That decision produces an authorization state
3. That authorization state determines available execution dispositions
4. Execution effects are traceable back to authorization source

Claim scope: **single formal chain with preserved provenance**

---

#### B. PRIMARY SOURCES

**Source S20260604-001**
- **TITLE**: Governed Auditable Decisioning Under Uncertainty: Synthesis and Agentic Extension
- **AUTHORS**: [Research team, ArXiv coordination]
- **YEAR**: 2026 (April)
- **URL**: https://arxiv.org/pdf/2604.19112
- **PRIMARY SOURCE**: YES

**Source S20260604-002**
- **TITLE**: Decision Trace Schema for Governance Evidence in Real-Time Risk Systems
- **AUTHORS**: [Research team, ArXiv]
- **YEAR**: 2026 (April)
- **URL**: https://arxiv.org/pdf/2604.09296
- **PRIMARY SOURCE**: YES

**Source S20260606-001**
- **TITLE**: A Five-Plane Reference Architecture for Runtime Governance of Production AI Agents
- **AUTHORS**: [Academic team, ArXiv]
- **YEAR**: 2026 (June)
- **URL**: https://arxiv.org/pdf/2606.12320
- **PRIMARY SOURCE**: YES

---

#### C. EXACT EXISTING SCOPE

**S20260604-001** establishes:
- Decision trace schema (six properties: decision context, logic, boundary, quality, human override, temporal metadata)
- Evidence sufficiency as measurable property
- **Does NOT establish**: formal chain connecting all six properties into single proof object; formal semantics of chain transitions

**S20260604-002** establishes:
- Temporal evidence via cryptographic ordering (hash chains, Merkle trees)
- Timestamping with NTP + cryptographic proof
- **Does NOT establish**: formal proof that all chain elements are necessarily connected; semantics of chain integrity

**S20260606-001** establishes:
- Five-plane separation: reasoning plane (decision point) + four enforcement planes
- Policy decision point (PDP) evaluation against composite principals
- **Does NOT establish**: formal proof object representing entire chain; semantics of transitions between decision and enforcement planes

---

#### D. NON-COVERAGE

**Gap 1: Chain Formalization**
- Existing sources provide **components** (traces, timestamps, decision points)
- Existing sources do NOT provide **formal semantics** of how these components form a single verifiable chain
- Existing sources do NOT define what makes a chain "complete" or "valid"

**Gap 2: Provenance Preservation**
- Existing sources track provenance (hash chains, timestamps)
- Existing sources do NOT formally define **chain integrity as a provable property**
- Existing sources do NOT define mechanism to prove "this execution matches this authorization"

**Gap 3: Authorization → Execution Binding**
- Five-Plane separates decision (PDP) from execution (PEP)
- Existing sources do NOT formally bind authorization decision to execution state
- Existing sources do NOT define state transitions from authorization to execution effects

---

#### E. RELATION TO MOCKA

**Classification**: DIRECT OVERLAP (components) + UNRESOLVED (integration)

**Reasoning**:
- Decision traces (S20260604-001/002) are DIRECT OVERLAP on evidence representation
- Five-Plane architecture (S20260606-001) is DIRECT OVERLAP on decision/execution separation
- **But**: integration of these into a single formal chain with proof of provenance is UNRESOLVED in existing literature
- Existing work treats components separately; MoCKA appears to formalize their conjunction

---

#### F. BOUNDARY

**Existing Research**: Defines decision trace components and architectural separation of decision from execution.

**MoCKA Boundary**: Formalizes these components as a single proof object with formally-defined chain integrity and provenance preservation properties.

**Unresolved**: Whether this formalization exists in literature under different terminology.

---

#### G. EVIDENCE CONFIDENCE

**HIGH** on component overlap (decision traces, PDP/PEP separation well-established)

**MEDIUM** on formal chain integration (no literature found; but absence does not confirm novelty)

**Access constraints**: ArXiv PDFs blocked; analysis from abstracts and linked content only

---

### CLAIM P4-C2: Standing Matrix

**CLAIM DEFINITION** (inferred):

MoCKA defines "Standing" as a composite predicate capturing authorization admissibility. Standing combines:
- Applicable agent/principal
- Meaningful action context
- Goal alignment with request
- Safety constraints satisfied

Standing is formally distinct from permission (can I?) and is expressed as a compound predicate over authorization state.

---

#### A. MOCKA CLAIM

A formal predicate:
```
Standing(agent, action, goal, safety_constraints) → Boolean
```

Where:
- Authorization alone does NOT imply Standing
- Standing requires simultaneous satisfaction of context, meaning, goal, and safety
- Standing can be formally verified and proven

---

#### B. PRIMARY SOURCES

**Source S20260606-001** (Five-Plane)
- Composite principals with capability attenuation
- Policy evaluation against "composite principal and session state"
- **Does NOT**: Define "standing" as compound admissibility predicate

**Source S20260606-002** (Compositional Authorization)
- Overlaying governance for delegation and scope
- **Does NOT**: Define multi-dimensional admissibility; treats scope/delegation separately

**Source: Policy-as-Code literature (OPA, Cedar, XACML)**
- Policy decision points evaluate conditions
- **Does NOT**: Define "standing" as formal composite predicate; XACML uses attribute-based access control (ABAC), not standing

---

#### C. EXACT EXISTING SCOPE

Five-Plane evaluates:
- Whether principal has capability (YES/NO)
- Whether session state permits action (YES/NO)

Policy-as-Code evaluates:
- Whether conditions match rules (ALLOW/DENY)
- No formal definition of "standing" as composite predicate

Classical authorization logic (S20060000-001):
- Defines authorization logic with state
- Admits cut as metatheoretic property
- **Does NOT**: Define "standing" or compound admissibility predicates

---

#### D. NON-COVERAGE

**Gap 1: Standing as Formal Predicate**
- Existing work evaluates individual conditions (can I? am I authorized? does policy permit?)
- No literature defines standing as a **compound admissibility predicate** requiring simultaneous satisfaction

**Gap 2: Standing vs. Authorization**
- Existing work does not formally distinguish "authorization" from "standing"
- No formal definition of why authorization alone is insufficient

**Gap 3: Standing Proof Rules**
- No literature provides proof rules for deriving Standing from component predicates

---

#### E. RELATION TO MOCKA

**Classification**: NO MATERIAL OVERLAP

**Reasoning**:
- "Standing" does not appear in authorization or governance literature (search results zero)
- Composite predicate evaluation exists (policy engines, ABAC)
- **But**: Standing as a formally-defined composite authorization admissibility predicate does not appear

---

#### F. BOUNDARY

**Existing Research**: Evaluates individual policy conditions; treats authorization and policy evaluation as stateless or semi-stateful decision points.

**MoCKA Boundary**: Defines Standing as a formal compound predicate unifying context, meaning, goal, and safety; requires simultaneous satisfaction.

**Unresolved**: Whether this predicate is equivalent to existing "policy evaluation with state" under different formulation.

---

#### G. EVIDENCE CONFIDENCE

**MEDIUM** on component existence (policy evaluation, state tracking well-known)

**LOW** on formal Standing predicate (not found in literature; but may exist under different name)

---

### CLAIM P4-C3: CSAG Composite Predicate

**CLAIM DEFINITION** (inferred):

CSAG = Composite State Authorization Gate

MoCKA claims that authorization admissibility is computed from a composite predicate unifying:
- **C**: Context (scope, domain, resource)
- **S**: State (previous authorization state, session state, system state)
- **A**: Authority (capability, delegation chain, principal identity)
- **G**: Goal (intended effect, action semantics, business purpose)

---

#### A. MOCKA CLAIM

```
CSAG(context, state, authority, goal) → AuthorizationAdmissible
```

Each dimension is independently evaluable but jointly necessary. Admissibility requires:
- All four dimensions consistent
- State transitions respect authority bounds
- Goal does not contradict standing

---

#### B. PRIMARY SOURCES

**Source S20260606-001** (Five-Plane)
- Composite principals
- Session state tracking
- **Does NOT**: Define four-dimensional composite predicate; evaluates decision as single point

**Source: XACML / Policy-as-Code**
- Attribute-based access control (ABAC)
- Evaluates multiple attributes
- **Does NOT**: Define CSAG structure; attributes are flat list, not composite predicate

**Source S20260606-002** (Compositional Authorization)
- Delegation scope overlay
- **Does NOT**: Define composite predicate; focuses on delegation chain only

---

#### C. EXACT EXISTING SCOPE

XACML / ABAC:
- Evaluates policies over attributes (subject, resource, action, environment)
- Attributes evaluated conjunctively: (subject.role ∧ resource.type ∧ action.permission ∧ environment.time)
- **Scope**: Flat attribute list; no hierarchical structure; no formal CSAG

Policy-as-Code (OPA/Rego):
- Evaluates rules over multiple dimensions
- **Scope**: Rule evaluation; no formal composite predicate definition

---

#### D. NON-COVERAGE

**Gap 1: CSAG Structure**
- ABAC evaluates flat attribute lists
- CSAG appears to structure dimensions hierarchically (context ∋ scope; state ∋ previous authorization; etc.)
- No literature provides this structured composite predicate

**Gap 2: CSAG Proof Rules**
- No formal proof rules for deriving CSAG admissibility
- No method to prove "all four dimensions are consistent"

**Gap 3: CSAG State Semantics**
- No definition of how CSAG transforms under state transitions
- No formal semantics of "state respects authority bounds"

---

#### E. RELATION TO MOCKA

**Classification**: PARTIAL OVERLAP (ABAC components) + UNRESOLVED (structured composite predicate)

**Reasoning**:
- ABAC evaluates multiple dimensions (PARTIAL)
- CSAG structures these dimensions formally with semantics (UNRESOLVED in literature)
- May be equivalent to ABAC under different formulation (requires verification)

---

#### F. BOUNDARY

**Existing Research**: Evaluates authorization as conjunction of independent attributes (ABAC); no formal structure for composite dimensions.

**MoCKA Boundary**: Structures authorization as formal composite predicate with four named dimensions; adds proof rules for joint consistency.

**Unresolved**: Relationship to ABAC under reinterpretation.

---

#### G. EVIDENCE CONFIDENCE

**MEDIUM** on ABAC existing (well-established)

**LOW** on CSAG structure (not found; but may be equivalent to parameterized ABAC)

---

### CLAIM P4-C4: Execution Disposition States

**CLAIM DEFINITION** (inferred):

Authorization decision produces multiple possible execution dispositions (not just ALLOW/DENY). Possible states:
- AUTHORIZED_ALLOWED: can execute
- AUTHORIZED_PENDING: requires human review
- AUTHORIZED_SCOPED: allowed with constraints
- AUTHORIZED_DENIED: authorization granted but execution blocked
- DENIED: no authorization

Each disposition is formally derived from authorization state.

---

#### A. MOCKA CLAIM

```
Authorize(evidence, gate_decision) → ExecutionDisposition ∈ {ALLOWED, PENDING, SCOPED, DENIED}
```

Execution disposition is formally computed from authorization state; not all authorized actions result in ALLOWED disposition.

---

#### B. PRIMARY SOURCES

**Source S20260606-001** (Five-Plane)
- Policy decision points return: ALLOW / DENY / REQUIRE_APPROVAL / MASK
- **Does NOT formally**: Define what happens AFTER these decisions; no execution disposition semantics

**Source: Policy enforcement literature**
- Policy decision points: ALLOW / DENY
- Policy enforcement points: enforce decision
- **Does NOT**: Define multiple dispositions post-authorization

**Source S20260604-001** (Governed Auditable Decisioning)
- Evidence → Decision → Authorization
- **Does NOT**: Define disposition states; stops at authorization

---

#### C. EXACT EXISTING SCOPE

Five-Plane returns:
- ALLOW / DENY / REQUIRE_APPROVAL / MASK (four outcomes)
- These are **policy decision outcomes**, not execution dispositions
- No formal semantics of what each means for actual execution

Policy enforcement:
- Enforces decision (block / permit / throttle)
- **Does NOT** track "execution disposition" as separate formal object

---

#### D. NON-COVERAGE

**Gap 1: Disposition as Formal State**
- Policy decisions exist; execution dispositions as formal state do not appear

**Gap 2: AUTHORIZED_DENIED Distinction**
- No literature distinguishes "authorization granted but execution denied"
- This appears to be MOCKA-specific concept

**Gap 3: Disposition-to-Execution Semantics**
- No literature defines how execution disposition determines execution effects
- No formal mapping from disposition to actual system behavior

---

#### E. RELATION TO MOCKA

**Classification**: ANALOGOUS (similar outcomes) + UNRESOLVED (formal disposition semantics)

**Reasoning**:
- Five-Plane produces four outcomes (ANALOGOUS)
- MoCKA formalizes these as execution dispositions with formal semantics (UNRESOLVED)
- May be equivalent under reinterpretation (requires verification)

---

#### F. BOUNDARY

**Existing Research**: Policy decisions produce outcomes (ALLOW/DENY/REQUIRE_APPROVAL/MASK); these are enforcement directives, not formal execution states.

**MoCKA Boundary**: Formalizes execution outcomes as disposition states with formal semantics; distinguishes authorization state from execution disposition.

---

#### G. EVIDENCE CONFIDENCE

**MEDIUM** on policy outcomes existing

**LOW** on formal disposition semantics (not found in literature)

---

### CLAIM P4-C5: Authorization Existence ⇏ Standing

**CLAIM DEFINITION** (inferred):

A formal claim that authorization state existing (∃ Authorization) does not imply Standing.

```
∃ Authorization(agent, action) ⇏ Standing(agent, action, context, goal, safety)
```

Authorization is necessary but not sufficient for standing.

---

#### A. MOCKA CLAIM

Authorization (permission, capability) is distinct from standing (admissibility). An agent can be authorized without standing if:
- Standing predicate fails on context
- Standing fails on goal alignment
- Standing fails on safety constraints

---

#### B. PRIMARY SOURCES

**Source S20260606-001** (Five-Plane)
- Distinguishes authorization (PDP decision) from enforcement (PEP action)
- **Does NOT**: Formalize why authorization alone is insufficient
- **Does NOT**: Define standing as separate predicate

**Source: Principle of Least Authority (POLA)**
- Capability attenuation
- **Does NOT**: Formalize authorization vs. standing distinction

**Source: Classical authorization logic (S20060000-001)**
- Defines authorization as formal object
- **Does NOT**: Define standing or reason why authorization is insufficient

---

#### C. EXACT EXISTING SCOPE

Five-Plane separates authorization from enforcement, but:
- Both are treated as parts of same decision/enforcement pipeline
- No formal claim that authorization ⇏ standing

Classical authorization logic:
- Defines what can be authorized
- Does not address admissibility beyond authorization

---

#### D. NON-COVERAGE

**Gap 1: Formal Separation**
- No literature formally claims authorization alone is insufficient
- No formal counterexample showing authorization without standing

**Gap 2: Standing as Formal Predicate**
- Without formal standing predicate (P4-C2), this claim cannot be formalized

**Gap 3: Proof Rules**
- No literature provides proof rules for "authorization ⇏ standing"

---

#### E. RELATION TO MOCKA

**Classification**: UNRESOLVED (depends on Standing formalization)

**Reasoning**:
- Five-Plane separates decision/enforcement (ANALOGOUS)
- Formal claim that authorization is insufficient (UNRESOLVED)
- Depends on formal standing definition

---

#### F. BOUNDARY

**Existing Research**: Treats authorization as necessary and sufficient (or passes to enforcement tier).

**MoCKA Boundary**: Formally distinguishes authorization from standing; proves authorization alone is insufficient.

---

#### G. EVIDENCE CONFIDENCE

**MEDIUM** on authorization existing

**LOW** on formal separation from standing

---

### CLAIM P4-C6: Valid Authorization ⇏ Executed

**CLAIM DEFINITION** (inferred):

A formal claim distinguishing authorization from execution:

```
∃ ValidAuthorization(agent, action) ⇏ Executed(agent, action)
```

An action can be authorized but not executed due to:
- Execution disposition state (SCOPED, PENDING, DENIED)
- Runtime constraints
- Subsequent policy changes
- Human override

---

#### A. MOCKA CLAIM

Authorization state and execution state are formally distinct. Existence of valid authorization does not guarantee execution will occur.

---

#### B. PRIMARY SOURCES

**Source S20260606-001** (Five-Plane)
- Separates reasoning plane (authorization) from enforcement planes (execution)
- **Does NOT formally**: Define why authorized actions may not execute
- **Does NOT**: Provide proof that authorization ⇏ execution

**Source: Runtime verification literature**
- Monitors execution against specification
- **Does NOT**: Address authorization-to-execution gap formally

---

#### C. EXACT EXISTING SCOPE

Five-Plane:
- Separates decision from enforcement (ARCHITECTURAL SEPARATION)
- Does not formalize why separation matters (no proof)
- No formal semantics of "authorized but not executed"

---

#### D. NON-COVERAGE

**Gap 1: Formal Proof**
- No literature formally proves authorization ⇏ execution

**Gap 2: Execution Failure Cases**
- No formal enumeration of why authorized actions don't execute

**Gap 3: Proof Rules for Execution**
- No rules for deriving Executed from ValidAuthorization + ExecutionDisposition

---

#### E. RELATION TO MOCKA

**Classification**: ANALOGOUS (architectural separation) + UNRESOLVED (formal proof)

**Reasoning**:
- PDP/PEP separation acknowledges the gap (ANALOGOUS)
- Formal proof that authorization ⇏ execution (UNRESOLVED)

---

#### F. BOUNDARY

**Existing Research**: Acknowledges decision/execution separation as architectural pattern; no formal semantics.

**MoCKA Boundary**: Formalizes this separation with proof that authorization is insufficient for execution.

---

#### G. EVIDENCE CONFIDENCE

**MEDIUM** on architectural separation

**LOW** on formal proof

---

### CLAIM P4-C7: Authority Domain Separation

**CLAIM DEFINITION** (inferred):

Different domains (e.g., identity authority, policy authority, execution authority) are formally separated. Actions requiring authority in one domain may be invalid in another.

```
AuthorizedIn(domain1) ⇏ AuthorizedIn(domain2)
```

---

#### A. MOCKA CLAIM

Formal claim that authority is domain-specific and domains are formally distinct.

---

#### B. PRIMARY SOURCES

**Source S20260606-020** (Sovereign Execution Broker)
- Certificate-bound authority in specific control planes
- **Does NOT**: Define domain separation formally; focuses on delegation chain

**Source: Capability-based security literature**
- Capabilities are restricted to specific domains
- **Does NOT**: Formally define domain separation as proof requirement

---

#### C. EXACT EXISTING SCOPE

Capability-based systems:
- Restrict capabilities to specific objects/domains
- **Does NOT** formalize cross-domain authority separation proofs

Certificate systems:
- Bind certificates to specific purposes/domains
- **Does NOT** formalize why cross-domain authority is invalid

---

#### D. NON-COVERAGE

**Gap 1: Formal Domain Definition**
- No literature formally defines what constitutes a "domain"

**Gap 2: Cross-Domain Separation Proofs**
- No formal proof rules preventing cross-domain authority

**Gap 3: Domain Composition Rules**
- No rules for when domains can/cannot be composed

---

#### E. RELATION TO MOCKA

**Classification**: PARTIAL OVERLAP (domain concepts exist) + UNRESOLVED (formal separation)

---

#### F. BOUNDARY

**Existing Research**: Uses domains informally (per-object capabilities, certificate purposes); no formal separation proof.

**MoCKA Boundary**: Formalizes domain separation with proof rules preventing cross-domain authority transfer.

---

#### G. EVIDENCE CONFIDENCE

**LOW** (limited sources found on this specific claim)

---

### CLAIM P4-C8: Bounded Automation of Gate Reasoning

**CLAIM DEFINITION** (inferred):

Gate reasoning can be partially automated within formally-defined bounds. Human authorization remains necessary for:
- Novel situations (outside learned patterns)
- High-impact decisions
- Conflicts between rule and context

Automation itself is bounded (cannot exceed authority of automated decision system).

---

#### A. MOCKA CLAIM

Formal framework defining:
1. What gate reasoning can be automated
2. When human gate is required
3. How automation bounds are verified

---

#### B. PRIMARY SOURCES

**Source S20260604-003** (Bounded Autonomy)
- Behavioral specification, retry budgets, circuit breakers
- **Does NOT**: Formalize gate reasoning specifically
- **Does NOT**: Define bounds on automation of authorization decisions

**Source S20260604-001** (Governed Auditable Decisioning)
- Identifies when governance fails in agentic systems
- **Does NOT**: Formalize bounded automation of gate reasoning

**Source: Formal methods for autonomous systems literature**
- Runtime enforcement
- **Does NOT**: Address authorization decision automation bounds

---

#### C. EXACT EXISTING SCOPE

Bounded autonomy:
- Defines execution bounds (retry limits, timeouts)
- **Does NOT**: Define automation bounds for authorization reasoning

Governance literature:
- Identifies governance failures
- **Does NOT**: Formalize what CAN be automated vs. requires human gate

---

#### D. NON-COVERAGE

**Gap 1: Formal Definition of "Gate Reasoning"**
- No literature formally defines gate reasoning as distinct from policy evaluation

**Gap 2: Automation Bounds**
- No formal specification of what can/cannot be automated in gate context

**Gap 3: Proof Rules for Bounded Automation**
- No rules proving authorization automation respects bounds

---

#### E. RELATION TO MOCKA

**Classification**: ANALOGOUS (bounded autonomy exists) + UNRESOLVED (gate reasoning automation)

**Reasoning**:
- Bounded autonomy for execution (ANALOGOUS)
- Bounded automation specifically for gate reasoning (UNRESOLVED)

---

#### F. BOUNDARY

**Existing Research**: Bounds execution behavior (retries, timeouts); no formal treatment of authorization reasoning automation.

**MoCKA Boundary**: Formalizes which aspects of gate reasoning can be automated and which require human judgment; proves automation respects authority bounds.

---

#### G. EVIDENCE CONFIDENCE

**MEDIUM** on bounded autonomy existing

**LOW** on gate reasoning automation (not found)

---

## PAPER 5 CLAIMS

### CLAIM P5-C1: UJC — Universal Joint Constraint

**CLAIM DEFINITION** (inferred):

UJC is a formal constraint object representing a joint point in an authorization composition where:
- Multiple authorization domains meet
- Authority must be coordinated
- Constraint enforcement prevents invalid authority combinations

---

#### A. MOCKA CLAIM

```
UJC(domain1, domain2, ..., domainN) → Constraint
```

Formal object representing coordination point; can be verified, composed, and enforced.

---

#### B. PRIMARY SOURCES

**SEARCH RESULT**: No literature found using "UJC" in authorization/governance context.

Mechanical engineering literature found (universal joints for mechanical systems), but:
- Not applicable to authorization
- Different domain (mechanical vs. formal systems)

---

#### C. EXACT EXISTING SCOPE

No existing scope in authorization/governance literature.

---

#### D. NON-COVERAGE

**Complete**: No relevant literature covers UJC-like formal object for authorization composition.

---

#### E. RELATION TO MOCKA

**Classification**: UNRESOLVED (term not found; cannot verify without MoCKA formalization)

**Reasoning**:
- Term does not appear in authorization literature
- Cannot assess whether concept exists under different name without MoCKA definition
- Mechanical engineering universal joints are structurally different (different domains)

---

#### F. BOUNDARY

**Existing Research**: No corresponding concept found.

**MoCKA Boundary**: Introduces UJC as formal constraint object for authorization composition coordination.

**Unresolved**: Cannot verify whether this is novel or equivalent to existing concept under different name.

---

#### G. EVIDENCE CONFIDENCE

**HIGH** on "not found in authorization literature"

**LOW** on "does not exist elsewhere" (absence ≠ non-existence)

---

### CLAIM P5-C2: CSG — Constraint State Graph

**CLAIM DEFINITION** (inferred):

CSG represents the state space of authorization constraints. Nodes represent valid authorization states; edges represent valid state transitions. CSG enforces:
- Only valid transitions allowed
- Cross-domain constraint satisfaction
- State invariants maintained through transitions

---

#### A. MOCKA CLAIM

```
CSG = (States, Transitions, Invariants)

Where:
- States ⊆ all possible constraint configurations
- Transitions ⊆ valid state changes
- Invariants = properties true in all states
```

---

#### B. PRIMARY SOURCES

**SEARCH RESULT**: No literature found using "CSG" in authorization/governance context.

Graph-based state representations exist in general:
- Finite state machines
- Model checking state spaces
- Markov chains

But no literature titled "Constraint State Graph" for authorization found.

---

#### C. EXACT EXISTING SCOPE

State-based verification (general):
- State machines represent system states
- **Does NOT**: Specifically address authorization constraint states

Compositional verification (S20151506-001):
- Uses component and interaction invariants
- **Does NOT**: Define constraint state graphs for authorization

---

#### D. NON-COVERAGE

**Gap 1: CSG Formalization**
- No literature formalizes authorization constraint state spaces as graphs

**Gap 2: CSG Transition Semantics**
- No formal rules for valid transitions between authorization constraint states

**Gap 3: CSG Invariant Preservation**
- No proof rules showing invariants preserved across constraint transitions

---

#### E. RELATION TO MOCKA

**Classification**: UNRESOLVED (terminology not found; concept partially analogous to state machines)

**Reasoning**:
- General state graphs exist (ANALOGOUS)
- CSG specifically for authorization constraints (UNRESOLVED)
- Cannot assess novelty without MoCKA formalization

---

#### F. BOUNDARY

**Existing Research**: State-based verification and finite state machines are established; no specific formalization for authorization constraint state graphs.

**MoCKA Boundary**: Formalizes authorization constraints as state graphs with formal transition semantics and invariant preservation.

---

#### G. EVIDENCE CONFIDENCE

**HIGH** on "not found with CSG terminology"

**LOW** on "novel concept" (state machines analogous)

---

### CLAIM P5-C3: System Admissibility

**CLAIM DEFINITION** (inferred):

System admissibility is a formal property of authorization systems where:
1. All authorization decisions are verifiable
2. All decisions are traceable to evidence
3. System state is predictable given evidence
4. No "hidden" authorization decisions exist

Admissibility is formally verifiable property, distinct from compliance or safety.

---

#### A. MOCKA CLAIM

```
SystemAdmissible(system) ↔ 
  ∀decision ∈ decisions(system) . 
    ∃evidence . Traceable(decision, evidence) ∧ Predictable(state, evidence)
```

---

#### B. PRIMARY SOURCES

**Source: ONTOS VII**
- Mentions "admissibility architecture"
- "Admissibility-relevant structure must be fully visible to verification"
- **Does NOT**: Formally define system admissibility

**Source S20260604-001** (Governed Auditable Decisioning)
- Identifies governance gaps (decision diffusion, evidence fragmentation)
- **Does NOT**: Define system admissibility formally

**Source: Formal methods literature**
- System safety, liveness, fairness properties
- **Does NOT**: Define admissibility as formal property

---

#### C. EXACT EXISTING SCOPE

ONTOS:
- Admissibility as design principle
- Requires visibility to verification, unavailability to system
- **Does NOT formalize** as verifiable property

Formal methods:
- Define safety (bad things never happen), liveness (good things eventually happen)
- **Does NOT**: Define admissibility

---

#### D. NON-COVERAGE

**Gap 1: Formal Definition**
- No literature formally defines system admissibility as property

**Gap 2: Verification Procedure**
- No method to verify system admissibility given authorization logs

**Gap 3: Admissibility Invariants**
- No formal invariants characterizing admissible systems

---

#### E. RELATION TO MOCKA

**Classification**: PARTIAL OVERLAP (admissibility principle exists) + UNRESOLVED (formal property)

**Reasoning**:
- ONTOS mentions admissibility (PARTIAL)
- MoCKA formalizes as verifiable property (UNRESOLVED)

---

#### F. BOUNDARY

**Existing Research**: Treats admissibility as design principle; no formal definition of verifiable property.

**MoCKA Boundary**: Formalizes system admissibility as property over authorization state, evidence, and trace completeness.

---

#### G. EVIDENCE CONFIDENCE

**MEDIUM** on principle existence

**LOW** on formal property definition

---

### CLAIM P5-C4: Composition Trace

**CLAIM DEFINITION** (inferred):

Composition trace records decision-making sequence through composed authorization systems. Trace captures:
- Authority transitions between components
- Constraints checked at composition boundaries
- Evidence accumulated through composition chain

Formally verifiable as complete and unbroken record.

---

#### A. MOCKA CLAIM

```
CompositionTrace = Sequence<CompositionEvent>

Where CompositionEvent includes:
- Source authority
- Target authority
- Constraints checked
- Evidence state
- Timestamp
```

Trace integrity is formally verifiable.

---

#### B. PRIMARY SOURCES

**Source S20151506-001** (Compositional Verification)
- Component invariants and interaction invariants
- Traces as sequences of states over timesteps
- **Does NOT**: Define composition traces for authorization

**Source S20260603-001** (Supply Chain Security for AI Skills)
- Chain-of-custody for skill composition
- **Does NOT formalize**: composition trace as verifiable object

**Source S20260606-002** (Compositional Authorization)
- Delegation through authorization composition
- **Does NOT**: Define formal composition trace with verification

---

#### C. EXACT EXISTING SCOPE

Compositional verification:
- Uses traces of component states
- **Does NOT**: Apply to authorization composition specifically
- **Does NOT**: Formalize trace verification for authority

Supply chain verification:
- Tracks skill provenance
- **Does NOT formalize**: composition trace as authorization concept

---

#### D. NON-COVERAGE

**Gap 1: Authorization Composition Traces**
- No literature defines composition traces specifically for authorization

**Gap 2: Trace Integrity Verification**
- No formal method to verify composition trace completeness and integrity

**Gap 3: Trace-to-Authority Mapping**
- No formal semantics linking trace events to authority state changes

---

#### E. RELATION TO MOCKA

**Classification**: DIRECT OVERLAP (compositional verification) + UNRESOLVED (authorization application)

**Reasoning**:
- Compositional verification uses traces (DIRECT)
- Authorization composition traces (UNRESOLVED)

---

#### F. BOUNDARY

**Existing Research**: Compositional verification uses component state traces; no application to authorization composition.

**MoCKA Boundary**: Formalizes composition traces for authorization domain with formal verification of trace integrity.

---

#### G. EVIDENCE CONFIDENCE

**HIGH** on compositional verification existing

**MEDIUM** on authorization application (not found; but conceptually related)

---

### CLAIM P5-C5: Authority Invariant

**CLAIM DEFINITION** (inferred):

Authority invariant is a formal property of authorization systems where authority bounds are maintained through all state transitions:

```
∀state₁, state₂ ∈ AuthorizationStates .
  state₁ --transition--> state₂ ⇒ 
    Authority(state₁) ≥ Authority(state₂)
```

Authority never increases through system transitions; only decreases or stays same.

---

#### A. MOCKA CLAIM

Authority bounds (capability sets, delegation scope) form an invariant that is:
1. Formally definable
2. Verifiable through state transitions
3. Preserved under composition
4. Proof-checkable

---

#### B. PRIMARY SOURCES

**Source: Temporal invariants literature (S20000807-001)**
- Temporal invariants as properties always true
- **Does NOT**: Define authority invariants specifically

**Source S20260606-001** (Five-Plane)
- Authority is "intersection of capability sets along delegation chain"
- **Does NOT formalize**: authority invariant through transitions

**Source S20260620-001** (Sovereign Execution Broker)
- Capability attenuation in delegation chains
- **Does NOT**: Formalize authority invariant as temporal property

---

#### C. EXACT EXISTING SCOPE

Temporal invariants:
- General framework for "always true" properties
- **Does NOT**: Apply to authority domain

Capability attenuation:
- Progressively narrows scope through delegation
- **Does NOT formalize** as invariant property with proof rules

---

#### D. NON-COVERAGE

**Gap 1: Authority as Verifiable Invariant**
- No literature formalizes authority bounds as temporal invariant

**Gap 2: Proof Rules for Authority Preservation**
- No rules proving authority invariant across transitions

**Gap 3: Authority Composition Invariants**
- No rules proving invariant preserved under component composition

---

#### E. RELATION TO MOCKA

**Classification**: ANALOGOUS (temporal invariants exist) + UNRESOLVED (authority application)

**Reasoning**:
- Temporal invariants are established concept (ANALOGOUS)
- Authority invariants as formal property (UNRESOLVED)

---

#### F. BOUNDARY

**Existing Research**: Temporal invariants framework is general; authority domain is not specifically addressed.

**MoCKA Boundary**: Formalizes authority as temporal invariant; provides proof rules for preservation through transitions and composition.

---

#### G. EVIDENCE CONFIDENCE

**HIGH** on temporal invariants existing

**LOW** on authority-specific invariant (not found)

---

### CLAIM P5-C6: Decision-Evidence Binding

**CLAIM DEFINITION** (inferred):

Decision-evidence binding formally connects a specific authorization decision to specific evidence through a verifiable link:

```
Binding(decision, evidence) → BindingProof

Where BindingProof includes:
- Evidence sufficiency (evidence is complete)
- Evidence relevance (evidence applies to decision)
- Causality link (evidence logically entails decision)
```

Binding itself is verifiable, not merely recorded.

---

#### A. MOCKA CLAIM

Authorization decisions are not just recorded with evidence; they are formally bound where:
1. Binding can be verified
2. Binding proves evidence necessitated the decision
3. Breaking binding is detectable
4. Bindings compose (decision chains preserve binding)

---

#### B. PRIMARY SOURCES

**Source S20260604-001** (Governed Auditable Decisioning)
- Decision trace schemas with evidence properties
- **Does NOT**: Formalize binding as verifiable proof object

**Source S20260604-002** (Decision Trace Schema)
- Captures six properties including evidence
- **Does NOT**: Define evidence-decision binding formally

**Source S20260605-002** (Decision Evidence Maturity Model)
- Measures evidence sufficiency
- **Does NOT**: Formalizes binding itself

---

#### C. EXACT EXISTING SCOPE

Decision trace schemas:
- Records evidence alongside decisions
- **Does NOT**: Define binding as formal object
- **Does NOT**: Formalize what makes binding valid

Evidence sufficiency measurement:
- Measures whether enough evidence exists
- **Does NOT**: Formalize binding proof

---

#### D. NON-COVERAGE

**Gap 1: Binding as Formal Object**
- No literature defines decision-evidence binding as proof object

**Gap 2: Binding Verification**
- No method to verify that binding is sound (evidence actually entails decision)

**Gap 3: Binding Preservation Under Composition**
- No rules for maintaining binding through decision chains

**Gap 4: Binding Breaking Detection**
- No formal way to detect when binding has been compromised

---

#### E. RELATION TO MOCKA

**Classification**: DIRECT OVERLAP (decision traces, evidence sufficiency) + UNRESOLVED (binding formalization)

**Reasoning**:
- Components exist (traces, evidence measurement) (DIRECT)
- Formal binding object and verification (UNRESOLVED)

---

#### F. BOUNDARY

**Existing Research**: Records evidence with decisions; measures evidence sufficiency; does not formalize binding as verifiable proof.

**MoCKA Boundary**: Formalizes decision-evidence binding as proof object; provides verification procedure; proves binding preserved through composition.

---

#### G. EVIDENCE CONFIDENCE

**HIGH** on evidence recording and measurement existing

**MEDIUM** on formal binding (not found; but components exist)

---

### CLAIM P5-C7: Authority-Aware Composition

**CLAIM DEFINITION** (inferred):

Authority-aware composition means authorization constraints are formally considered when composing authorization subsystems:

```
Compose(system1, system2, constraints) → system₁₂

Where constraints include:
- Authority boundary conditions
- Scoping rules at composition boundary
- Invariant preservation requirements
```

Composition results in new system whose authority properties are formally verified.

---

#### A. MOCKA CLAIM

When authorization systems are composed:
1. Authority of composed system is formally derived from components
2. Constraints at composition boundary are formally specified
3. Authority invariants are provably preserved
4. New system authority is ≤ component authorities

---

#### B. PRIMARY SOURCES

**Source S20260606-002** (Compositional Authorization Framework)
- Overlaying governance for delegation and scope
- **Does NOT formalize**: how authority properties compose

**Source S20260620-001** (Sovereign Execution Broker)
- Delegation chain with authority attenuation
- **Does NOT formalize**: authority-aware composition rules

**Source S20151506-001** (Compositional Verification)
- Component and interaction invariants
- **Does NOT**: Apply to authority domain

**Source S20260603-001** (Supply Chain Security)
- Verifies skill composition chains
- **Does NOT formalize**: authority composition rules

---

#### C. EXACT EXISTING SCOPE

Compositional verification:
- Proves properties are preserved under composition
- **Does NOT**: Apply to authority properties

Delegation frameworks:
- Chain delegation with scoping
- **Does NOT formalize**: composition rules for authority verification

---

#### D. NON-COVERAGE

**Gap 1: Authority Composition Rules**
- No formal rules for deriving composed system authority from components

**Gap 2: Constraint Specification at Boundary**
- No formal language for specifying composition constraints

**Gap 3: Invariant Preservation Proof**
- No proof rules ensuring authority invariants persist through composition

**Gap 4: Authority Minimality**
- No formal requirement or proof that composed authority is minimal

---

#### E. RELATION TO MOCKA

**Classification**: ANALOGOUS (compositional verification exists) + UNRESOLVED (authority application)

**Reasoning**:
- General composition frameworks exist (ANALOGOUS)
- Authority-specific composition rules (UNRESOLVED)

---

#### F. BOUNDARY

**Existing Research**: Compositional verification framework is general; authority properties are not specifically considered in composition.

**MoCKA Boundary**: Formalizes how authority properties are preserved and composed; provides verification rules for authority-aware composition.

---

#### G. EVIDENCE CONFIDENCE

**HIGH** on compositional verification existing

**LOW** on authority-specific composition (not found)

---

## CROSS-CLAIM MATRICES

### PAPER 4 CLASSIFICATION SUMMARY

| Claim | Term | Classification | Confidence | Status |
|-------|------|-----------------|-----------|---------|
| P4-C1 | Authorization-to-Effect Chain | DIRECT OVERLAP + UNRESOLVED | MEDIUM | Components exist; integration unresolved |
| P4-C2 | Standing Matrix | NO MATERIAL OVERLAP | LOW | Term not found; analogous patterns exist |
| P4-C3 | CSAG Composite Predicate | PARTIAL OVERLAP + UNRESOLVED | MEDIUM | ABAC exists; structured composite unresolved |
| P4-C4 | Execution Disposition States | ANALOGOUS + UNRESOLVED | MEDIUM | Policy outcomes exist; formal disposition unresolved |
| P4-C5 | Authorization ⇏ Standing | UNRESOLVED | LOW | Depends on Standing definition |
| P4-C6 | Valid Authorization ⇏ Executed | ANALOGOUS + UNRESOLVED | MEDIUM | PDP/PEP separation; formal proof unresolved |
| P4-C7 | Authority Domain Separation | PARTIAL OVERLAP + UNRESOLVED | LOW | Domain concepts exist; formal separation unresolved |
| P4-C8 | Bounded Automation of Gate Reasoning | ANALOGOUS + UNRESOLVED | MEDIUM | Bounded autonomy exists; gate reasoning automation unresolved |

---

### PAPER 5 CLASSIFICATION SUMMARY

| Claim | Term | Classification | Confidence | Status |
|-------|------|-----------------|-----------|---------|
| P5-C1 | UJC | UNRESOLVED | HIGH | No literature found in authorization domain |
| P5-C2 | CSG | UNRESOLVED | HIGH | No literature found; state machines analogous |
| P5-C3 | System Admissibility | PARTIAL OVERLAP + UNRESOLVED | MEDIUM | Principle exists; formal property unresolved |
| P5-C4 | Composition Trace | DIRECT OVERLAP + UNRESOLVED | MEDIUM | Compositional verification exists; authorization application unresolved |
| P5-C5 | Authority Invariant | ANALOGOUS + UNRESOLVED | LOW | Temporal invariants exist; authority application unresolved |
| P5-C6 | Decision-Evidence Binding | DIRECT OVERLAP + UNRESOLVED | HIGH | Components exist; formal binding unresolved |
| P5-C7 | Authority-Aware Composition | ANALOGOUS + UNRESOLVED | MEDIUM | Compositional verification exists; authority-specific rules unresolved |

---

## SPECIAL TEST RESULTS

### TEST 1: Authorization-to-Effect Chain

**Test Objective**: Does existing literature formalize Evidence → Decision → Authorization → Execution as single formal chain?

**Result**: NO

**Finding**:
- Evidence → Decision: Decision trace schemas exist (S20260604-001/002)
- Decision → Authorization: Policy decision points exist (S20260606-001)
- Authorization → Execution: PEP enforcement exists (policy-as-code literature)
- **But**: No literature formalizes these as single integrated chain with proof of provenance preservation

**Conclusion**: Components exist separately; integration as formal chain is UNRESOLVED

---

### TEST 2: Standing / CSAG Compound Predicate

**Test Objective**: Does existing literature define authorization admissibility as compound predicate requiring simultaneous satisfaction of multiple orthogonal conditions?

**Result**: NO

**Finding**:
- ABAC evaluates multiple attributes conjunctively
- **But**: No formal definition of "standing" as admissibility predicate
- **But**: No formalization requiring simultaneous satisfaction with semantics for failure modes

**Conclusion**: Component evaluation exists; formal compound admissibility predicate is UNRESOLVED

---

### TEST 3: Execution Disposition

**Test Objective**: Does existing literature derive multiple execution dispositions (not just ALLOW/DENY) formally from authorization state?

**Result**: NO

**Finding**:
- Five-Plane returns four outcomes (ALLOW/DENY/REQUIRE_APPROVAL/MASK)
- **But**: These are enforcement directives, not formal execution states
- **But**: No formal semantics of "execution disposition" or how disposition determines actual behavior

**Conclusion**: Outcomes exist; formal disposition semantics is UNRESOLVED

---

### TEST 4: Authorization ⇏ Execution

**Test Objective**: Does existing literature formally separate authorization state from execution state and prove authorization is insufficient?

**Result**: NO

**Finding**:
- Five-Plane acknowledges separation (architectural)
- **But**: No formal proof that authorization alone cannot guarantee execution
- **But**: No formal definition of why execution is non-deterministic given authorization

**Conclusion**: Architectural separation exists; formal proof is UNRESOLVED

---

### TEST 5: UJC / CSG

**Test Objective**: Do existing sources treat composition constraint, constraint state, cross-component admissibility, state transitions, and joint decisions as single formal object?

**Result**: NO

**Finding**:
- No literature uses term "UJC" or "CSG"
- Constraint satisfaction literature exists (separate domain)
- State machines exist (separate framework)
- **But**: No unified formalization for authorization composition constraints

**Conclusion**: Related concepts exist separately; unified UJC/CSG formalization is UNRESOLVED

---

### TEST 6: System Admissibility

**Test Objective**: Does existing literature define "system admissibility" as formal property distinct from safety, compliance, and policy satisfaction?

**Result**: NO

**Finding**:
- ONTOS mentions admissibility as design principle
- **But**: No formal property definition
- **But**: No verification procedure
- **But**: Not distinguished from safety/compliance in formal treatment

**Conclusion**: Principle exists; formal system admissibility property is UNRESOLVED

---

### TEST 7: Authority Invariant

**Test Objective**: Does existing literature formalize authority bounds as temporal invariant preserved through state transitions and composition?

**Result**: NO

**Finding**:
- Temporal invariants are established (general)
- Capability attenuation is implemented (practical)
- **But**: Authority is not treated as temporal invariant
- **But**: No proof rules for invariant preservation through authorization transitions

**Conclusion**: Components exist separately; formal authority invariant is UNRESOLVED

---

### TEST 8: Decision-Evidence Binding

**Test Objective**: Does existing literature define decision-evidence binding as proof object where binding itself can be verified?

**Result**: NO

**Finding**:
- Decision traces record evidence (exist)
- Evidence sufficiency measured (exists)
- **But**: Binding itself is not formal object
- **But**: No verification procedure for binding soundness
- **But**: No semantics for "evidence entails decision"

**Conclusion**: Recording exists; formal binding proof object is UNRESOLVED

---

## SYNTHESIS: DIRECT OVERLAP CATEGORY

### Paper 4 Direct Overlaps

1. **Evidence schema and representation**: S20260604-001, S20260604-002
   - Literature covers: how to represent decision evidence
   - MoCKA extends to: formal binding of evidence to authorization proof

2. **Policy decision points**: S20260606-001, policy-as-code literature
   - Literature covers: architectural separation of decision from enforcement
   - MoCKA extends to: formal semantics of authorization admissibility

3. **Temporal evidence and cryptographic ordering**: S20260604-002
   - Literature covers: how to timestamp and order evidence
   - MoCKA extends to: using temporal evidence to prove authorization chains

---

### Paper 5 Direct Overlaps

1. **Compositional verification methodology**: S20151506-001
   - Literature covers: component invariants, interaction invariants, trace-based verification
   - MoCKA extends to: authorization composition with formal invariant preservation

2. **Decision trace schemas with evidence properties**: S20260604-001, S20260604-002
   - Literature covers: what evidence properties to record
   - MoCKA extends to: formal proof that recorded evidence is sufficient for authorization

3. **Capability attenuation in delegation**: S20260606-001, S20260620-001
   - Literature covers: how capabilities narrow through delegation
   - MoCKA extends to: formal invariant proving authority never increases

---

## SYNTHESIS: PARTIAL OVERLAP CATEGORY

### Paper 4 Partial Overlaps

1. **CSAG and ABAC**: Attribute-based access control literature
   - Literature covers: evaluating multiple attributes conjunctively
   - Boundary: ABAC treats attributes as flat list; CSAG structures as formal composite predicate with semantics

2. **Authority domain concepts**: Capability-based security literature
   - Literature covers: restricting capabilities to specific domains
   - Boundary: No formal proof rules for cross-domain separation

3. **System admissibility principle**: ONTOS VII
   - Literature covers: admissibility as design principle
   - Boundary: No formal property definition or verification procedure

---

### Paper 5 Partial Overlaps

1. **System admissibility**: ONTOS VII, formal methods literature
   - Literature covers: architectural principle of visibility/unavailability
   - Boundary: No formal definition as verifiable property

2. **Policy evaluation against state**: Five-Plane, policy-as-code literature
   - Literature covers: evaluating authorization against composite principal + session state
   - Boundary: No formal semantics of "system admissible" distinct from "policy permits"

---

## SYNTHESIS: ANALOGOUS CATEGORY

### Paper 4 Analogous

1. **Authorization vs. execution separation**: Conceptually similar to formal specification vs. implementation (acknowledged gap in autonomous systems literature)

2. **Bounded automation patterns**: Engineering patterns exist (retry budgets, circuit breakers); no formal definition of what makes automation "bounded" in authorization context

3. **Execution outcomes (ALLOW/DENY/REQUIRE_APPROVAL/MASK)**: Structurally similar to execution dispositions; but policy outcomes, not formal execution states

---

### Paper 5 Analogous

1. **Temporal invariants**: General framework exists; authority application is not addressed

2. **Compositional verification**: Framework exists; authority-specific composition rules are not formalized

3. **State machines and graphs**: Existing technology; constraint state graphs specifically for authorization are not formalized

---

## SYNTHESIS: NO MATERIAL OVERLAP CATEGORY

### Paper 4 No Material Overlap

1. **Standing as compound authorization admissibility predicate**: No term, no concept in literature; related policy evaluation exists but not formalized as "standing"

---

### Paper 5 No Material Overlap

1. **UJC (Universal Joint Constraint)**: No literature in authorization domain; mechanical engineering concept not applicable

---

## SYNTHESIS: UNRESOLVED CATEGORY

### Unresolved (Cannot Verify Without MoCKA Formalization)

**Paper 4**:
- P4-C1: Formal chain integration
- P4-C2: Standing formalization (depends on MoCKA definition)
- P4-C5: Standing logical relationship
- P4-C6: Formal proof of authorization insufficiency
- P4-C7: Formal domain separation proofs
- P4-C8: Bounded automation formalization

**Paper 5**:
- P5-C1: UJC formalization (term not found; cannot verify whether novel without definition)
- P5-C2: CSG formalization (state machines analogous; cannot verify structure without definition)
- P5-C3: System admissibility as formal property (principle exists; property unresolved)
- P5-C4: Composition trace for authorization (compositional verification analogous; application unresolved)
- P5-C5: Authority invariant formalization (temporal invariants exist; authority application unresolved)
- P5-C6: Binding as formal proof object (components exist; integration unresolved)
- P5-C7: Authority-aware composition rules (compositional verification exists; authority-specific rules unresolved)

---

## PAPER 4 BOUNDARY MAP

### Fully Established in Literature
- Evidence schema and representation
- Decision trace recording
- Policy decision point architecture
- Cryptographic temporal ordering

### Partially Established (Components Exist; Integration Missing)
- Authorization-to-effect chain (components separate; integration unresolved)
- Execution outcomes (existing outcomes; formal disposition semantics missing)
- Authorization/execution separation (architectural; formal proof missing)

### Not Found in Literature (Cannot Verify Without MoCKA Definition)
- Standing as compound admissibility predicate
- CSAG as formal composite predicate
- Bounded automation of gate reasoning
- Authority domain formal separation

### Architectural Patterns (No Formal Semantics)
- PDP/PEP separation
- Composite principals
- Capability attenuation

---

## PAPER 5 BOUNDARY MAP

### Fully Established in Literature
- Compositional verification methodology
- Temporal invariants framework
- Capability attenuation through delegation
- Decision trace recording with evidence

### Partially Established (Components Exist; Formalization Missing)
- System admissibility (principle exists; formal property missing)
- Composition traces (compositional verification traces exist; authorization application missing)
- Authority through composition (capability attenuation exists; formal composition rules missing)

### Not Found in Literature (Cannot Verify Without MoCKA Definition)
- UJC (term not found in authorization literature)
- CSG (terminology not found; state machines analogous)
- Authority invariant (authority as temporal invariant not formalized)
- Decision-evidence binding (as formal proof object not found)

### Research Concepts Emerging (Early/Nascent)
- Evidence sufficiency measurement (DEMM 2605.04093)
- Governed auditable decisioning (2604.19112)
- Runtime governance of agents (2606.12320)

---

## CLAIMS REQUIRING PRIMARY-SOURCE VERIFICATION

**When ArXiv access is restored, verify:**

1. **S20260606-001** (Five-Plane Reference Architecture)
   - Exact formal semantics of policy decision point evaluation
   - Definition of "effective authority" and whether it addresses authorization invariants

2. **S20260606-002** (Compositional Authorization Framework)
   - Whether "standing" or equivalent term is defined
   - Formal semantics of delegation overlay

3. **S20260604-001** (Governed Auditable Decisioning)
   - Whether "cascade of uncertainty" has formal counterpart
   - Definition of "structural breaks" in authorization context

4. **S20260605-002** (Decision Evidence Maturity Model)
   - Exact formalization of evidence sufficiency
   - Whether binding semantics are addressed

5. **S20260603-001** (Formal Analysis and Supply Chain Security)
   - How formal analysis is defined for skill composition
   - Whether authority composition rules are formalized

6. **S20260620-001** (Sovereign Execution Broker)
   - Formal proof rules for delegation chain verification
   - Whether this addresses authority invariants

---

## CLAIMS WHOSE FORMAL DEFINITION SHOULD BE REFINED

**Recommendations for MoCKA clarification:**

### Paper 4

1. **P4-C1 (Authorization-to-Effect Chain)**
   - Explicitly formalize the chain semantics
   - Provide proof rules showing chain integrity is preserved
   - Define what "complete chain" means formally

2. **P4-C2 (Standing)**
   - Formally define Standing predicate with clear semantics
   - Show how Standing differs from "authorization exists" formally
   - Provide decision procedure for Standing evaluation

3. **P4-C3 (CSAG)**
   - Formally define composite predicate structure
   - Show how this differs from ABAC under reinterpretation
   - Provide semantics for component interaction within CSAG

4. **P4-C5 & P4-C6 (Authorization Insufficiency)**
   - These depend on formal definitions above
   - Provide formal proofs of non-implication

5. **P4-C8 (Bounded Automation)**
   - Define what aspects of gate reasoning can be automated
   - Provide proof rules showing automation respects bounds

### Paper 5

1. **P5-C1 (UJC) & P5-C2 (CSG)**
   - Clearly define formal structure
   - Distinguish from mechanical engineering concepts
   - Show connection to authorization composition

2. **P5-C3 (System Admissibility)**
   - Formally define as verifiable property
   - Distinguish from safety/compliance/policy satisfaction
   - Provide verification procedure

3. **P5-C4 (Composition Trace)**
   - Formally apply compositional verification trace methodology to authorization
   - Show trace integrity verification

4. **P5-C5 (Authority Invariant)**
   - Formally define authority as temporal property
   - Provide proof rules for invariant preservation
   - Show connection to temporal invariants literature

5. **P5-C6 (Decision-Evidence Binding)**
   - Formally define binding as proof object
   - Provide verification procedure
   - Show binding preservation through composition

6. **P5-C7 (Authority-Aware Composition)**
   - Provide formal composition rules for authority
   - Proof that composed authority is well-defined and minimal
   - Show these rules extend existing compositional verification

---

## FINAL ASSESSMENT

### What Is Confirmed to Exist

**Architectural and Operational**:
- Decision trace recording with evidence
- Policy decision points and policy enforcement points
- Capability attenuation through delegation
- Compositional verification methodology
- Temporal invariants framework
- Evidence sufficiency measurement (emerging)

**Cannot Be Formalized Without Existence**:
- Any formal proof system requires existing components
- MoCKA appears to take existing components and formalize their properties

### What Is Unresolved (Requires MoCKA Specification)

**14 major gaps identified**:
1. Formal chain integration (P4-C1)
2. Standing formalization (P4-C2)
3. CSAG composite predicate (P4-C3)
4. Execution disposition semantics (P4-C4)
5. Authorization insufficiency proof (P4-C5, P4-C6)
6. Authority domain separation proof (P4-C7)
7. Bounded automation formalization (P4-C8)
8. UJC definition (P5-C1)
9. CSG formalization (P5-C2)
10. System admissibility property (P5-C3)
11. Authority invariant formalization (P5-C5)
12. Decision-evidence binding proof (P5-C6)
13. Authority-aware composition rules (P5-C7)
14. Composition trace application (P5-C4)

### Terminology Status

**Terms Found in Literature**:
- Decision traces
- Evidence sufficiency
- Policy decision points
- Composition trace (general)
- Temporal invariants
- Authority (in delegation context)

**Terms Not Found in Authorization Literature**:
- Standing (as authorization admissibility predicate)
- CSAG (composite state authorization gate)
- UJC (Universal Joint Constraint, in authorization domain)
- CSG (Constraint State Graph, in authorization domain)
- Bounded automation (in authorization gate context)

**Architectural Patterns Found**:
- PDP/PEP separation
- Capability attenuation
- Compositional verification

---

## NEXT PHASE RECOMMENDATIONS

### Immediate (Before Paper Submission)

1. **Clarify each claim's formal definition**
   - Provide precise mathematical notation
   - Show relationship to existing concepts where applicable

2. **Verify unresolved claims**
   - Restore ArXiv access and read full papers
   - Check whether claims are addressed in literature under different terminology

3. **Distinguish formalization from engineering**
   - Clearly separate what is new formal system vs. new engineering approach
   - Acknowledge existing architectural patterns

### Medium-term (Before Final Publication)

1. **Literature coverage verification**
   - Ensure all 6 primary sources are fully reviewed
   - Search for additional literature under alternative terminology

2. **Formal definition publication**
   - Paper 4: Publish formal definitions of Standing, CSAG, bounded automation
   - Paper 5: Publish formal definitions of UJC, CSG, System Admissibility

3. **Positioning statement**
   - Clearly position MoCKA relative to existing work
   - State what is formalization of existing concepts vs. new concepts

---

## FINAL PRINCIPLE ADHERENCE

**✓ Phase 1 Frozen State**: Unchanged; no modifications to A-J canonical definitions

**✓ No Novelty Verdicts**: Used only "confirmed existing," "unresolved," "not found in literature"

**✓ No Absence-Based Conclusions**: Stated "not found" but never "therefore novel"

**✓ Component/System Distinction**: Distinguished architecture from formal property throughout

**✓ Evidence Confidence**: Rated HIGH/MEDIUM/LOW on each assessment

---

**Report Status**: ROUND 3 COMPLETE — Ready for gap verification phase

**Next Action**: Restore ArXiv access and verify 6 primary sources; update unresolved claims accordingly
