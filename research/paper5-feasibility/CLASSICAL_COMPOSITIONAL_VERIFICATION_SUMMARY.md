# Classical Compositional Verification: Theory Summary
## Foundations for Paper 5 Implementation Analysis

---

## I. MISRA–CHANDY: Component Networks (1981)

### A. WHAT THEY BUILT

**Type:** Formal theory (mathematical foundation)

**Problem Addressed:** How to verify large concurrent systems by breaking them into components

**Core Insight:** Component network verification = component verification + network connection rules

### B. WHAT ACTUALLY WORKS

**Proven:**
- Component invariants are sufficient for network invariants under certain conditions
- Compositional reasoning reduces verification burden exponentially
- Works for synchronous and asynchronous concurrent systems

**Limitations:**
- Requires strong preconditions on component interfaces
- Assumes components are "well-behaved" (no hidden dependencies)
- Network structure changes → re-verification required
- Does not handle dynamic component addition/removal

### C. HOW IT WORKS

**Key Principle:** Network Invariant Theorem

```
IF   each component i maintains invariant inv_i
AND  network connections satisfy P(inv_1, inv_2, ..., inv_n)
AND  P is constructed correctly
THEN network maintains invariant I_network
```

**Conditions for Composition:**
1. **Separation:** Component state spaces are disjoint (no hidden sharing)
2. **Invariant Stability:** inv_i is preserved even under interference from other components
3. **Connection Rule:** P must guarantee no component "breaks" another's invariant

**Verification Process:**
- Prove each component's inv_i independently
- Verify that network connections obey P
- Conclude I_network holds

### D. DATA STRUCTURES & NOTATION

- Component C_i: state space S_i, invariant inv_i
- Network connection predicate: P(inv_1, ..., inv_n)
- Component communication: message channels or shared variables
- Ordering: synchronous composition (strict sequencing) vs asynchronous (concurrent)

### E. APPLICABLE TO MOCKA

**Direct Application:**
- MoCKA's parallel evidence collection (Claude + GPT + Gemini in parallel) → component network
- Each AI component has invariant: "produces consistent output format"
- Network connection rule: "all components finish before composition"
- Composition object is network invariant

**Rating:** **Directly usable** — MoCKA already uses component network model

**Implementation Already In Use:**
```python
# In app.py / orchestrator:
components = [claude_ai, gpt_ai, gemini_ai]
results = [run_component(c) for c in components]
# Check: all results have invariant "valid_format"
composition = merge(results)  # Network connection rule applied
```

### F. KNOWN LIMITATIONS FOR MOCKA

**Challenge 1: Dynamic Component Addition**
- Current: AI roster is fixed (Claude, GPT, Gemini, Copilot)
- Future: "Add new AI capability X" without re-verification
- Misra-Chandy: requires full re-proof
- **Implication:** MoCKA needs additional mechanism (rolling updates, capability gates)

**Challenge 2: Hidden Dependencies**
- Misra-Chandy assumes component state spaces are disjoint
- Reality: Multiple AIs drawing on same knowledge base (papers, data)
- **Implication:** MoCKA must track shared state explicitly in events.db

**Challenge 3: Network Reconfiguration**
- Misra-Chandy: static network structure
- MoCKA: decision at HG might exclude AI-C from next composition
- **Implication:** Requires dynamic network rules, not static P

---

## II. JONES / RELY–GUARANTEE REASONING (1981–)

### A. WHAT THEY BUILT

**Type:** Formal specification + proof methodology

**Problem Addressed:** Multi-threaded systems where components interfere with each other

**Core Insight:** Don't assume components are isolated; explicitly model mutual interference

### B. WHAT ACTUALLY WORKS

**Proven:**
- Compositional proof of concurrent programs
- Can handle arbitrary interference
- Scales to complex multi-process systems
- Formally sound

**Limitations:**
- Interference specifications (rely/guarantee) must be exact — over-specification blocks composition
- Proof construction is manual and difficult (not automated)
- Real systems often have non-deterministic interference (hard to specify)
- Requires strong mathematical skill to use correctly

### C. HOW IT WORKS

**Core Concepts:**

For each component C_i:
- **Rely(C_i):** What interference C_i is willing to tolerate from other components
- **Guarantee(C_i):** What C_i promises about its own interference with others

**Composition Rule:**
```
FOR all components C_i, C_j in network:
  IF Guarantee(C_i) ⊆ Rely(C_j)     [C_i's interference acceptable to C_j]
  AND Guarantee(C_j) ⊆ Rely(C_i)    [C_j's interference acceptable to C_i]
  AND all pairwise combinations satisfy above
THEN network is safe (safe interference semantics)
```

**Proof Structure:**
```
Assume   Rely(C_i)           [assume interference matches specification]
Prove    Guarantee(C_i)      [prove C_i maintains its contract]
Conclude C_i is safe under Rely
```

**Example (MoCKA context):**
```
Component: Claude AI
  Rely:      "Inputs come from app.py router within 5 seconds"
             "No external modification of its memory"
  Guarantee: "Output is consistent JSON within 10 seconds"
             "No writes to shared database without event_gate approval"

Composition: Claude + GPT + Gemini
  Check:     Does each component's Guarantee ⊆ others' Rely?
             E.g., Claude's "consistent JSON" ⊆ router's Rely ✓
```

### D. APPLICABLE TO MOCKA

**Direct Application:**
- MoCKA's HG (Human Gate) decisions based on understanding "What can this AI guarantee under these conditions?"
- Rely-Guarantee naturally maps to MoCKA's Assumption-Guarantee model
- Paper 5's "Admissibility Check" is essentially a Rely-Guarantee verification

**Rating:** **Directly usable** — This is the mathematical foundation of MoCKA's condition-based gates

**Implementation Mapping:**
```
MoCKA Admissibility Check ≈ Rely-Guarantee Verification

Condition Check = Rely-Guarantee Compatibility Check
  ✓ Condition holds → components' guarantees match → AUTO-PASS
  ✗ Condition unknown → interference unspecified → HG required
```

### E. KNOWN LIMITATIONS FOR MOCKA

**Challenge 1: Non-deterministic Interference**
- Rely-Guarantee assumes interference can be precisely specified
- Reality: Claude might occasionally timeout, network latency varies, AI outputs vary stochastically
- **Implication:** MoCKA conditions must include "expected variance," not just binary pass/fail

**Challenge 2: Assumption Changes**
- Rely-Guarantee: assumptions are static
- MoCKA: "This AI's interference spec is no longer valid (new version released)"
- **Implication:** Need revocation mechanism when Rely/Guarantee conditions change

**Challenge 3: Learning from Violations**
- Classical Rely-Guarantee: if violation occurs, proof is invalid
- MoCKA: violations happen, record in events.db, potentially revoke automation
- **Implication:** Need "evidence-based revocation" beyond classical theory

---

## III. ASSUME–GUARANTEE FRAMEWORK (1995–)

### A. WHAT THEY BUILT

**Type:** Compositional verification methodology (synthesis of Misra–Chandy + Jones RG)

**Problem Addressed:** Large systems decomposed into modules, each verified under module-local assumptions

**Core Insight:** "You can assume X about the environment, and I guarantee Y about my behavior"

### B. WHAT ACTUALLY WORKS

**Proven:**
- Modular verification of complex systems
- Assumption propagation through hierarchy
- Works with circular dependencies (under conditions)
- Sound and complete (in restricted settings)

**Limitations:**
- Assumption specifications must be non-circular (direct cycles need special handling)
- Automatic assumption inference is NP-complete (must be manual)
- Real systems often have implicit assumptions (hard to enumerate)

### C. HOW IT WORKS

**Core Framework:**

Each module M has:
- **Assumption:** Env(M) — properties environment must satisfy
- **Guarantee:** Mod(M) — properties module maintains
- **Contract:** (Env(M), Mod(M))

**Verification Rule:**
```
Module M is correct under Env(M) IF:
  Assuming Env(M) holds
  Then Mod(M) is proven (via standard proof methods)

Composition of M1, M2:
  IF Guarantee(M1) ⊇ Assumption(M2)    [M1's output satisfies M2's assumption]
  AND Guarantee(M2) ⊇ Assumption(M1)   [M2's output satisfies M1's assumption]
  THEN composition is valid
  AND Guarantee(M1 ∘ M2) = Guarantee(M1) ∩ Guarantee(M2)
```

**Graphical Representation:**
```
Module M1          Module M2
  Env(M1) ────────> Assumption(M2)
  Guarantee(M1)         ✓
  Guarantee(M1) ────────> Assumption(M2)
                        verified!
```

### D. APPLICABLE TO MOCKA

**Direct Application — HG Decision Making:**

Each AI component has:
- **Assumption:** "Input data is valid, decision authority is intact"
- **Guarantee:** "Output is consistent, follows safety protocols"
- **Decision Gate:** HG verifies Assumptions before AUTO-PASS

**MoCKA Mapping:**
```
Assumption (Env)     ← Admissibility Conditions
  e.g., "Data source is trusted"
        "No recent security incidents"
        "Authority scope unchanged"

Guarantee (Mod)      ← AI's trained behavior
  e.g., "Consistent JSON output"
        "No contradictions with policy"
        "Reasons are traceable"

Composition Gate     ← AUTO-PASS or HG?
  IF all Assumptions hold
  THEN Guarantee applies → AUTO-PASS
  ELSE HG required to approve Guarantee
```

**Rating:** **Directly usable** — This is the exact structure MoCKA uses for admissibility checking

### E. KNOWN LIMITATIONS FOR MOCKA

**Challenge 1: Assumption Inference**
- Assume-Guarantee requires explicit assumptions
- MoCKA: "What are the implicit assumptions about 'trustworthy data'?"
- **Implication:** HG must make assumptions explicit before automation

**Challenge 2: Assumption Degradation Over Time**
- Theory: Assumptions are static
- Reality: "This assumption was true in 2024, but not now (new threat)"
- **Implication:** Institutional Memory must track assumption expiration

**Challenge 3: Circular Guarantees**
- Assume-Guarantee: "I assume X, you assume Y" → potential circularity
- Handled in theory via ranking functions
- MoCKA: "Claude assumed GPT's output, GPT assumed Claude's output" → deadlock risk
- **Implication:** Composition ordering (who decides first?) must be explicit

---

## IV. McMILLAN / COMPOSITIONAL MODEL CHECKING (1998–)

### A. WHAT THEY BUILT

**Type:** Automated verification algorithm (abstraction + refinement)

**Problem Addressed:** Model checking state explosion: 2^n states for n variables

**Core Insight:** Verify abstract models, then refine; don't verify full system directly

### B. WHAT ACTUALLY WORKS

**Proven:**
- Can verify systems exponentially larger than monolithic checking
- Compositional abstraction reduces state space dramatically
- Used in industry (chip design, protocol verification)
- Automated tool support available

**Limitations:**
- Module interfaces must be precisely defined (hard in practice)
- Refinement proofs can be expensive
- Not all systems have good abstractions
- Abstraction must be sound (over-abstract = false negatives)

### C. HOW IT WORKS

**Three-Step Process:**

**Step 1: Abstraction**
```
Full System S with n components, 2^n state space
           ↓
         (abstract)
           ↓
Abstract Model A with k components, 2^k state space (k << n)
           ↓
        (verify)
           ↓
Verification Result: Formal property holds in A
```

**Step 2: Refinement Check**
```
Property P holds in abstract A
           ↓
Does A refine S?  (i.e., is A an overapproximation of S?)
           ↓
  If YES: Property P also holds in S (sound)
  If NO:  Refinement counterexample found → revise A
```

**Step 3: Iterative Refinement**
```
Loop:
  1. Create/refine abstraction A
  2. Verify A against property P
  3. If counterexample found (false positive):
       - Analyze counterexample
       - Refine A to exclude it
       - Retry
  4. If verification succeeds → DONE
```

**Key Data Structure: Abstraction Maps**
```
Concrete state s_concrete --maps-to--> abstract state s_abstract
  where s_abstract represents set of possible s_concrete
  
Abstraction is sound if:
  every transition in s_concrete is covered by transitions in s_abstract
```

### D. APPLICABLE TO MOCKA

**Application: System-Wide Safety Checking**

MoCKA system architecture:
- Concrete: All 22,000+ events, all decisions, all state transitions
- Abstract: High-level policy layers (HG, Institutional Memory, Bounded Automation)
- Verification target: "All decisions satisfy authority bounds"

**MoCKA Mapping:**
```
Concrete MoCKA     Abstract MoCKA Policy Layer
  events.db ────────> Policy statements only
  all transitions ──> Authority transitions only
  22k events ──────> 100s of policy rules
       ↓
    (verify)
       ↓
   Abstract verification passes
       ↓
   Refinement check: Does abstract policy refine actual system?
       ↓
   Counterexample check: Any concrete violation not caught by abstract?
```

**Rating:** **Concept only** — McMillan's automated approach, but MoCKA likely uses manual/semi-automated refinement

### E. KNOWN LIMITATIONS FOR MOCKA

**Challenge 1: Abstraction Construction**
- McMillan: automated in limited domains (finite-state systems)
- MoCKA: events are complex (JSON, references, temporal) → hard to abstract
- **Implication:** MoCKA may need human-guided abstraction (HG review)

**Challenge 2: Refinement Automation**
- McMillan: Counterexample-guided abstraction refinement (CEGAR)
- MoCKA: "Counterexample = violation of authority bound"
- **Implication:** Need to map policy violations → abstraction refinements

**Challenge 3: Dynamic Refinement**
- McMillan: verification is offline (compute once, verify)
- MoCKA: new decisions arrive constantly
- **Implication:** Can't re-verify full system every event → incremental verification needed

---

## V. COMPARISON TABLE: Applicability to MoCKA Paper 5

| Aspect | Misra–Chandy | Jones RG | Assume–Guarantee | McMillan |
|--------|------|------|---------|----------|
| **Maturity** | Foundational (1981) | Foundational (1981) | Synthesis (1995) | Implemented (1998) |
| **Proven** | Component networks | Concurrent interference | Modular verification | State explosion reduction |
| **Already Used in MoCKA** | Yes (AI parallels) | Yes (HG decision) | Yes (conditions) | Partial (manual) |
| **Easy to Apply** | Moderate | Difficult | Moderate | Difficult |
| **Automation Level** | None | Manual proofs | Semi-automated | Automated (in limited cases) |
| **Scalability** | Good | Moderate | Good | Exponential in principle, linear in practice |
| **Applicable to Composition** | YES | YES | YES | YES |
| **Applicable to Conditions** | YES | YES | YES | NO (verification, not condition-setting) |
| **Applicable to Authority** | NO | YES | YES | Limited |
| **Applicable to Evidence** | Partial | NO | NO | YES (abstraction evidence) |
| **Applicable to HG Escalation** | NO | Limited | YES | Partial (abstraction refinement) |
| **Applicable to Revocation** | Partial | YES (Rely change) | YES (Assumption change) | Limited |

---

## VI. SYNTHESIS: What These Theories Tell MoCKA

### Core Message

**All four theories say:** "Composition requires explicit conditions and interface contracts"

**Specific Findings:**

1. **Composition** ← Misra-Chandy: Component networks with invariants work
2. **Conditions** ← Assume-Guarantee: Explicit assumptions + guarantees; verify intersection
3. **Authority** ← Jones RG: Mutual guarantee enforcement (what you can interfere with)
4. **Evidence** ← McMillan: Abstraction proves policy conformance
5. **Human Gate** ← Assume-Guarantee: Verify conditions before automation
6. **Revocation** ← Jones RG: When Rely/Guarantee changes, revert to manual verification

### What Remains Unsolved

1. **Dynamic Network Topology** — add/remove AIs without full re-verification
2. **Stochastic Interference** — conditions on probabilistic behavior
3. **Learning & Adaptation** — systems that improve over time while maintaining guarantees
4. **Real-time Revocation** — detecting assumption violations and reverting instantly
5. **Cross-boundary Authority** — when two organizations' systems compose

---

## VII. NEXT STEPS

- [ ] Map each theory to MoCKA's current implementation
- [ ] Identify which theories solve which of Kuroko's 6 questions
- [ ] Check CAF 2026 for novel approaches to unsolved problems
- [ ] Synthesize into implementation feasibility verdict
