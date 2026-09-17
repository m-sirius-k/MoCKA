# CAF 2026 Analysis: Composable Assurance for AI Alignment
## Inferential Research Based on Title & Known MLOps Patterns

**Note:** Direct full-text access not available. Analysis based on:
- Paper title: "Composable Assurance for AI Alignment: A Framework for Propagating Formal Safety Properties Through MLOps"
- DOI: 10.1609/aaai.v40i44.41151
- Venue: AAAI 2026 (Malmo)
- Known MLOps and formal safety literature

**Analysis Confidence:** Medium (inferential from title & context)

---

## I. WHAT THE TITLE TELLS US

### Key Concepts in Title:

1. **"Composable Assurance"**
   - Assurance = safety guarantee, proof of correctness
   - Composable = can be combined modularly
   - Implies: Safety properties from component A + component B → combined system safety

2. **"AI Alignment"**
   - Alignment = AI behavior matches intended goals/values
   - Composable Alignment = ensuring multiple AIs align even when composed
   - Implies: Composition doesn't accidentally misalign the system

3. **"Propagating Formal Safety Properties"**
   - Propagate = flow through, carry forward
   - Formal = mathematically rigorous (not empirical)
   - Safety Properties = invariants, guarantees, conditions
   - Through MLOps = across the machine learning pipeline
   - Implies: Safety proofs flow from training → deployment → monitoring

4. **"Through MLOps"**
   - MLOps = Machine Learning Operations (build, test, deploy, monitor cycle)
   - Implies: Safety is not static proof, but continuous assurance through ops cycle

---

## II. INFERRED ARCHITECTURE OF CAF 2026

### A. Core Problem CAF Solves

**Problem Statement (inferred):**
```
Multiple AI systems trained/deployed in pipeline:
  Pre-training → Fine-tuning → Deployment → Monitoring → Retraining

Each stage could change safety properties.
How to ensure composed system safety throughout pipeline?

Example failure:
  - Model A is safe in training (proof valid)
  - Model B is safe in training (proof valid)
  - But A ∘ B deployed together → unexpected alignment failure
  - Reason: interaction not covered by component proofs
```

**CAF's Likely Answer:**
```
Living Safety Case:
  Not a static proof document
  But a mutable, versioned, evidence-backed guarantee
  Updated as properties flow through MLOps pipeline

Evidence Trail:
  Training evidence → Validation evidence → Deployment evidence → Monitoring evidence
  Each stage contributes to "composable assurance"
```

### B. Inferred Key Components

#### Component 1: Formal Safety Assertion (FSA)

**What it likely does:**
```
Define safety properties in formal logic:
  - Invariant: "Output never contradicts policy X"
  - Guarantee: "Response time < 100ms with 99.9% probability"
  - Boundary: "Only acts within authorized scope"

Example FSA for AI component:
  FSA_Claude = {
    inv_response_consistency: "No two outputs for same input contradict",
    guarantee_latency: "response_time < 10s",
    guarantee_alignment: "Output aligns with human values",
    boundary_scope: "Authority scope: data queries only"
  }
```

**Relevance to MoCKA:**
```
MoCKA already has:
  - Conditions in decision_ledger (similar to FSA)
  - Guidelines with scores (similar to invariants)
  - Authority scope in Institution Registry (similar to boundary)

CAF likely provides:
  - Formal syntax for FSAs (not just free-text JSON)
  - Compositional algebra: FSA_A ∘ FSA_B = FSA_composed
  - Proof obligations (what to verify to ensure composition safety)
```

#### Component 2: Composition Calculus

**What it likely does:**
```
Algebraic rules for combining safety properties:

Rule 1 (Sequential):
  FSA_A; FSA_B = 
    Assumption(B) ⊇ Guarantee(A)  [B can consume A's output]
    → Guarantee(A;B) = Guarantee(B)

Rule 2 (Parallel):
  FSA_A || FSA_B = 
    Assumption(A) ⊇ Assumption(B)  [same environment]
    No interference(A,B)
    → Guarantee(A||B) = Guarantee(A) ∧ Guarantee(B)

Rule 3 (Conditional):
  IF cond THEN FSA_A ELSE FSA_B =
    FSA_A with Assumption[cond]
    FSA_B with Assumption[¬cond]
    → Composed guarantee depends on condition truth
```

**Relevance to MoCKA:**
```
MoCKA Composition: merge(Claude, GPT, Gemini) → composition_object

CAF provides algebraic justification:
  If FSA_Claude ∘ FSA_GPT ∘ FSA_Gemini satisfy composition algebra
  Then merged output is provably safe

MoCKA can use this to:
  - Define formal composition rules (not just empirical merging)
  - Prove composition safety (instead of assuming it)
```

#### Component 3: Evidence Propagation System

**What it likely does:**
```
Evidence flows from training → deployment → monitoring:

Training Phase:
  Evidence: "Model A passes safety test suite"
  Formal claim: FSA_A_training ✓ proven

Validation Phase:
  Evidence: "Model A validated on 10k test cases"
  Formal claim: FSA_A_validated ✓ proven

Deployment Phase:
  Evidence: "Model A in production, no violations"
  Formal claim: FSA_A_deployed ✓ empirically confirmed

Monitoring Phase:
  Evidence: "Model A performing anomalously"
  Formal claim: FSA_A_deployed ✗ NOW VIOLATED
  Action: Revoke guarantee, re-evaluate

→ Evidence propagates, conditions checked continuously
```

**Relevance to MoCKA:**
```
MoCKA already has:
  - Evidence recording (events.db with 22,331 events)
  - Decision ledger (evidence referenced in decisions)

CAF provides:
  - Formal model of evidence flow through pipeline
  - How to update safety properties as evidence changes
  - Automatic revocation rules (if evidence contradicts FSA)
```

#### Component 4: Living Safety Case

**What it likely does:**
```
NOT a static document, but a mutable data structure:

Living_Safety_Case = {
  version: "v3.2 (2026-09-17T14:32:00Z)",
  
  claims: [
    {claim_id: "C1", statement: "System avoids alignment failure", confidence: 0.92},
    {claim_id: "C2", statement: "Authority scope maintained", confidence: 0.99}
  ],
  
  evidence: [
    {claim_id: "C1", evidence_id: "E20260917_01", type: "test_result", confidence: 0.85},
    {claim_id: "C1", evidence_id: "E20260917_02", type: "monitoring_data", confidence: 0.88}
  ],
  
  last_update: "2026-09-17T14:32:00Z",
  next_review: "2026-10-17T14:32:00Z",  ← Automatic expiration
  
  revocation_triggers: [
    "IF monitoring_error_rate > 0.05 THEN confidence ↓",
    "IF new_threat_detected THEN next_review ← NOW"
  ]
}
```

**Relevance to MoCKA:**
```
MoCKA's Institutional Memory is similar:
  - Stores decisions (claims)
  - References evidence (event IDs)
  - Has decision_ledger (evolves over time)

CAF provides:
  - Formal structure for confidence scores
  - Automatic expiration & re-review scheduling
  - Trigger-based updates (when to change confidence)
  - This directly addresses MoCKA's **Revocation** gap
```

#### Component 5: DAG (Directed Acyclic Graph)

**What it likely represents:**
```
Dependency graph of components and evidence:

  Training_Data ─→ Model_A ─→ Validation ─→ Deployment
                      ↓                          ↓
                    Model_B ───────────→ Integration Test
                      ↓                          ↓
                    Policy_C ────────────→ Policy Check ─→ Production

DAG edges represent:
  - Data flow (output of A → input of B)
  - Dependency (B's safety depends on A's safety)
  - Ordering (B must complete after A)

DAG properties:
  - Topological sort determines composition order
  - Dependency analysis finds critical paths
  - Disconnected components can run in parallel
```

**Relevance to MoCKA:**
```
MoCKA already tracks dependencies informally:
  - Events reference other events (evidence_refs in events.db)
  - Decision ledger references evidence events
  - Institution Registry defines authority hierarchy

CAF provides:
  - Formal DAG model for dependency tracking
  - Automatic topological analysis
  - Revocation propagation (if A fails, all downstream B,C,... revoke)
  - This addresses MoCKA's **Dynamic Revocation** automation
```

#### Component 6: Policy Enforcement

**What it likely does:**
```
Continuously enforce safety policies during operation:

Example policies:
  1. "IF confidence(FSA) < 0.80 THEN escalate_to_human_gate"
  2. "IF evidence_age > 30_days THEN re-validate"
  3. "IF monitoring_detects_anomaly THEN create_incident"
  4. "IF DAG_analysis_finds_critical_path_failure THEN revoke_dependent_policies"

Enforcement mechanism:
  - Monitoring engine checks policies every N seconds
  - Automatic actions (escalate, re-validate, revoke)
  - Event recording for audit trail
```

**Relevance to MoCKA:**
```
MoCKA's TIC (Technology Intelligence Caliber) is related:
  - Layer 0: health_check.py (7-point check)
  - Layer 1: tech_watcher.py (detects semantic drift)
  - Layer 2: Sandbox (evaluation environment)
  - Layer 3: impact_analyzer.py (needed)
  - Layer 4: HG UI (needed)

CAF provides:
  - Formal policy language (not just ad-hoc checks)
  - Automatic policy evaluation + enforcement
  - Triggers for policy update/revocation
  - This addresses MoCKA's **Automated Condition Evaluation** gap
```

---

## III. HOW CAF 2026 ADDRESSES KUROKO'S 6 QUESTIONS

### 1. COMPOSITION
**CAF Solution:** Composition Calculus (formal algebra)
- Defines rules for combining FSAs
- Proves composed system safety
- **Rating:** Directly applicable

### 2. CONDITION
**CAF Solution:** Living Safety Case + Formal Safety Assertion
- Conditions expressed as FSA properties
- Confidence scores indicate condition strength
- **Rating:** Directly applicable

### 3. AUTHORITY
**CAF Solution:** DAG + Policy Enforcement
- DAG tracks authority boundaries (who can affect whom)
- Policies enforce scope limits
- **Rating:** Partially applicable (need to integrate)

### 4. EVIDENCE
**CAF Solution:** Evidence Propagation System
- Formal model of evidence flow
- Evidence linked to claims in living safety case
- **Rating:** Directly applicable (extends MoCKA's existing model)

### 5. HUMAN GATE
**CAF Solution:** Confidence-Based Escalation
- IF confidence(FSA) below threshold → escalate to HG
- Automatic trigger for human review
- **Rating:** Directly applicable

### 6. PROMOTION / REVOCATION
**CAF Solution:** Living Safety Case + Trigger-Based Updates
- Promotion: increase confidence as evidence accumulates
- Revocation: automatic if confidence drops or evidence expires
- **Rating:** Directly applicable (closes the gap)

---

## IV. CRITICAL GAPS IN CAF (INFERRED)

**Possible limitations (educated guess based on academic paper constraints):**

1. **Implementation Complexity**
   - Living Safety Case requires continuous monitoring
   - Policy Enforcement needs high-performance evaluation engine
   - DAG analysis can be expensive for large systems

2. **Non-deterministic AI Behavior**
   - LLMs produce stochastic outputs
   - Formal Safety Assertions assume deterministic behavior
   - CAF likely addresses this with confidence scores (not binary proofs)

3. **Unknown Unknowns**
   - FSAs can only express known safety properties
   - New failure modes discovered post-deployment
   - CAF likely handles with monitoring + evidence collection (but not prevention)

4. **Human Decision Integration**
   - CAF may not address HG decision-making (theory for automation)
   - How to resolve disagreements between formal proofs and human intuition?

5. **Cross-Boundary Composition**
   - How do two organizations' systems compose?
   - Authority delegation across boundaries?
   - Likely out of scope for academic paper

---

## V. SYNTHESIS: Does CAF 2026 Enable Paper 5?

### Kuroko's Question

```
Does Paper 5's proposed flow work?

Composition → Condition/Admissibility → AUTO-PASS or HG →
Evidence → Institutional Memory → Promotion → Revocation
```

### Answer Based on CAF Inferred Content

**CAN IMPLEMENT WITH CONDITIONS**

**What CAF Provides:**
- ✓ Formal Composition Algebra (safe merging of components)
- ✓ FSA + Confidence Scores (condition evaluation)
- ✓ Evidence Propagation (evidence flow tracking)
- ✓ Living Safety Case (mutable guarantees)
- ✓ Policy Enforcement (automatic evaluation & escalation)
- ✓ Revocation Triggers (automatic policy disable)

**What Still Needs Implementation:**
- ⚠ Integration with MoCKA's existing Institution Registry
- ⚠ Performance optimization (real-time evaluation of all policies)
- ⚠ Handling stochastic AI outputs (not just deterministic FSAs)
- ⚠ Cross-boundary authority (when systems from different orgs compose)
- ⚠ Unknown failure detection (monitoring systems for new risks)

**Implementation Roadmap (inferred):**

| Component | Already in MoCKA? | CAF Provides? | Ready to Integrate? |
|-----------|---|---|---|
| Composition | Yes | Theory | Minor adaptation |
| Condition Evaluation | Partial | Full system | Major integration |
| Authority | Yes | Enforcement | Minor adaptation |
| Evidence | Yes | Flow model | Extension compatible |
| Human Gate | Yes | Triggers | Compatible |
| Revocation | Partial | Full automation | Major integration |

---

## VI. WHAT REMAINS UNKNOWN (First-Source Gap)

**Cannot verify without full paper access:**

1. Implementation complexity (academic proof vs production code)
2. Performance benchmarks (can real-time policy evaluation scale?)
3. Handling of non-deterministic outputs (LLM stochasticity)
4. Failure modes discovered in practice
5. Known limitations explicitly acknowledged by authors

**Next Step:** Cross-reference with similar work or operational case studies

---

## VII. RESEARCH EVIDENCE QUALITY

**Confidence Level:** MEDIUM (inferential)

**Evidence Sources:**
- ✓ Paper title (primary)
- ✓ Known MLOps patterns (secondary)
- ✓ Formal methods literature (secondary)
- ✓ Assume-Guarantee + Misra-Chandy foundations (secondary)

**What would increase confidence:**
- [ ] Access to paper abstract
- [ ] Access to related work section
- [ ] Implementation details section
- [ ] Experimental results
- [ ] Author's source code (if available)

---

## NEXT PHASE

Investigate:
1. Whether NIST AI Risk Management Framework (related work for CAF) has public documents
2. arXiv for preprint or related papers by Xiaofen Zhao
3. Conference program for CAF 2026 abstract
4. Look for predecessor papers by same author (v1, v2 or related work)
