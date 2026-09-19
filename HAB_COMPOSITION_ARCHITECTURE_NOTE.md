# HAB COMPOSITION ARCHITECTURE NOTE
## Mapping Paper 5 Composition Assurance to Human-AI Bridge

**Date:** 2026-09-19  
**Objective:** Design document for integrating Paper 5 theory into HAB (Human-AI Bridge) architecture.  
**Scope:** Theory-to-architecture connection; implementation planning excluded.

---

## PART 1: THE PROBLEM

### Why Composition Assurance Matters

**Observation:** Multiple AIs producing individually correct outputs does not guarantee composed system admissibility.

**Example:**
```
Agent A (GPT):     "Recommendation: approve loan X"    [correct per scope]
Agent B (Gemini):  "Risk assessment: 0.3% default"     [correct per scope]
Agent C (Claude):  "Policy boundary: approve if <5%"   [correct per scope]

Composed system output: APPROVE loan X
Human authority: ?

Problem: Even if A, B, C are all correct individually,
what is responsible for the COMPOSED decision?
```

**Paper 5 Answer:** Without explicit composition assurance:
- Individual correctness does not transfer
- Authority becomes ambiguous
- Failure modes are undetectable until consequences occur

**HAB Role:** Build architecture where composition is explicit, authority is clear, failures are detectable.

---

## PART 2: PAPER 5 FRAMEWORK MAPPED TO HAB LAYERS

### High-Level Architecture

```
Application Layer
  |
  v
Agent Layer (GPT, Gemini, Claude, ...)
  |
  v
Evidence Layer (capture decision + rationale for each agent)
  |
  v
Composition Layer (combine evidence into composition object)
  |
  v
Authority Layer (human gate: review + decide)
  |
  v
Decision Layer (record decision + consequence)
  |
  v
Execution Layer (act on decision; monitor consequence)
  |
  v
Memory Layer (institutional record; enable recurrence detection)
```

### Layer Definitions (mapped to M1-M5)

**Agent Layer (M1 responsibility)**
- Input: Task / question / problem statement
- Process: Each AI generates output + internal reasoning
- Output: Recommendation + confidence metadata
- Responsibility: Agent is accountable for its output correctness within scope
- Guarantee: None (agent may hallucinate, misunderstand, be out-of-date)
- Enforcement: Agent's training/validation is agent's responsibility

**Evidence Layer (M2 responsibility)**
- Input: Outputs from Agent Layer
- Process: Structured capture of:
  - WHAT was decided (output value)
  - WHY it was decided (reasoning trace)
  - WHEN (timestamp)
  - WHO (which agent, which model/version)
  - WHERE (system context)
  - HOW (method/prompt used)
- Output: Evidence Object for each agent
- Responsibility: System is accountable for evidence completeness
- Guarantee: Evidence is complete if and only if Evidence Layer executes fully
- Enforcement: Schema validation + write-gate enforcement

**Composition Layer (M3 responsibility)**
- Input: Evidence Objects from all Agent Layer participants
- Process: Structural combination into Composition Object:
  ```
  Composition Object = {
    decision_request: <problem statement>,
    agent_evidence: [Evidence_A, Evidence_B, Evidence_C],
    alternatives_considered: [alt1, alt2, alt3],
    conflict_resolution: <method used if agents disagree>,
    recommendation: <combined recommendation>,
    confidence_distribution: <per-agent + composite>,
    evidence_chain_hash: <cryptographic hash for integrity>,
    created_at: <timestamp>,
    created_by: <system identifier>
  }
  ```
- Output: Composition Object (structured, immutable snapshot)
- Responsibility: System is accountable for composition object validity (schema conformance)
- Guarantee: Composition Object is valid if structured correctly; does NOT guarantee composed recommendation is good
- Enforcement: Schema validation gate

**Authority Layer (M4 responsibility)**
- Input: Composition Object from Composition Layer
- Process: Human decision-maker (not automated) reviews Composition Object and decides:
  - Accept recommendation → authorizes action
  - Modify recommendation → inputs authority override
  - Reject recommendation → provides rationale for rejection
- Output: Authority Decision Object:
  ```
  Authority Decision = {
    composition_object_id: <reference>,
    human_decision_id: <unique identifier>,
    human_decision: <accept | modify | reject>,
    human_rationale: <why human decided this>,
    human_authority_id: <who made decision>,
    approval_timestamp: <when>,
    approval_signature: <cryptographic proof>
  }
  ```
- Responsibility: Human authority is accountable for their decision
- Guarantee: Decision is recorded, auditable, and attributable to human
- Enforcement: No automation in this layer; human review is non-delegable

**Execution Layer (follows Authority Decision)**
- Input: Authority Decision Object
- Process: If Authority Decision = "accept" or "modify":
  - Execute the authorized action
  - Record execution event
  - Monitor for immediate consequences
- Output: Execution Record:
  ```
  Execution Record = {
    authority_decision_id: <reference>,
    action_taken: <what was executed>,
    execution_timestamp: <when>,
    execution_consequence: <immediate outcome>,
    success: <true | false>,
    error_log: <if failed>
  }
  ```
- Responsibility: System is accountable for faithful execution (matching authorized action)
- Guarantee: Execution matches authorization (if system functions correctly)
- Enforcement: Execution gate + consequence logging

**Memory Layer (M5 responsibility)**
- Input: Execution Records (collected over time)
- Process: Pattern analysis:
  - Recurrence detection: "This failure pattern has occurred N times"
  - Drift detection: "Success rate declining over time"
  - Anomaly classification: "This failure is new type"
- Output: Institutional Memory:
  ```
  Institutional Memory = {
    event_id: <unique>,
    event_type: <success | failure | anomaly>,
    event_pattern: <category>,
    recurrence_count: <N occurrences>,
    trend: <stable | degrading>,
    recommended_action: <for human gate>,
    memory_timestamp: <when recorded>
  }
  ```
- Responsibility: System is accountable for detection accuracy
- Guarantee: Detection is reactive (post-hoc) not predictive
- Enforcement: Pattern engine validates + human gate can act on alerts

---

## PART 3: ROLE SEPARATION IN HAB

### Three Distinct Roles

**Role 1: AI (Agent Layer)**
- Generates recommendations
- Responsibility: Output correctness within declared scope
- Non-responsibility: Judging if recommendation should be acted on
- Authority: ZERO — cannot execute decisions
- Accountability: Transparent reasoning + evidence trail

**Role 2: System (Evidence + Composition + Execution + Memory Layers)**
- Structures evidence, composes decisions, executes, monitors
- Responsibility: Procedural correctness (does it follow protocol?)
- Non-responsibility: Deciding if recommendation is good
- Authority: NONE — only enforces procedures
- Accountability: Process audit trail

**Role 3: Human (Authority Layer)**
- Reviews Composition Object, makes final decision
- Responsibility: Decision authority (judging if recommendation is good)
- Non-responsibility: AI correctness (that's agent's burden), procedural execution (that's system's burden)
- Authority: ABSOLUTE for that decision instance
- Accountability: Decision recorded + attributable + auditable

### Critical Separation: Authority ≠ Recommendation

```
AI says:     "I recommend X"
System says: "Here is evidence for X, here is why AI recommended X"
Human says:  "I authorize Y" (accepts, rejects, modifies)
```

- If human says YES → human is responsible for that decision
- If human says NO → human is responsible for that decision  
- In BOTH cases, decision is recorded and auditable

**HAB guarantee:** Whoever made the decision is clear, always.

---

## PART 4: BOUNDARY CONDITIONS

### What HAB Does NOT Claim

1. **Autonomous Safety**
   - HAB does not claim AI can safely compose without human
   - Human gate is non-negotiable, not optional
   - Authority Gate is a safety boundary, not automated

2. **Correctness Guarantee**
   - Even with HAB, human can make wrong decision
   - HAB does not prevent human error
   - HAB enables detection and learning from error

3. **Prevention of Failures**
   - HAB detects failures (M5) but does not prevent them (that's M1-M3)
   - If all agents are hallucinating, HAB will record that, not fix it
   - Recurrence detection happens AFTER consequence

4. **Scalability Guarantee**
   - HAB scales procedurally (more decisions, more records)
   - HAB does not claim composition is easier with more agents
   - With 10 agents instead of 3, human authority burden increases

### What HAB Does Guarantee

1. **Transparency**
   - Every decision is recorded with full evidence chain
   - Authority is always attributable
   - Silence is prohibited (all decisions are recorded)

2. **Auditability**
   - Any decision can be reconstructed from records
   - Evidence chain is cryptographically protected
   - Tamper attempts are detectable

3. **Institutional Memory**
   - Failures are recorded and analyzed
   - Recurrence patterns are detected
   - System improves through incident learning

4. **Human Authority Preservation**
   - Humans remain decision-makers, not executors
   - No automatic action without human authorization
   - Authority Gate is non-bypassable

---

## PART 5: IMPLEMENTATION ARCHITECTURE

### Data Flow Diagram

```
┌─────────────┐
│   Agent A   │ (GPT) → Output A + Reasoning A
├─────────────┤
│   Agent B   │ (Gemini) → Output B + Reasoning B
├─────────────┤
│   Agent C   │ (Claude) → Output C + Reasoning C
└─────────────┘
        |
        v (M2: Evidence Capture)
┌─────────────────────────┐
│   Evidence Layer        │
│  ┌─────────────────────┐│
│  │ Evidence Object A   ││
│  │ Evidence Object B   ││
│  │ Evidence Object C   ││
│  └─────────────────────┘│
└─────────────────────────┘
        |
        v (M3: Composition)
┌─────────────────────────┐
│  Composition Layer      │
│  ┌─────────────────────┐│
│  │ Composition Object  ││
│  │ - all evidence      ││
│  │ - alternatives      ││
│  │ - conflict res.     ││
│  │ - integrated view   ││
│  └─────────────────────┘│
└─────────────────────────┘
        |
        v (M4: Authority)
┌─────────────────────────┐
│  Authority Layer        │
│  ┌─────────────────────┐│
│  │  HUMAN REVIEW       ││
│  │  (non-automated)    ││
│  │  → Decision         ││
│  │  → Rationale        ││
│  │  → Signature        ││
│  └─────────────────────┘│
└─────────────────────────┘
        |
        v (if authorized)
┌─────────────────────────┐
│   Execution Layer       │
│   - Execute action      │
│   - Record outcome      │
│   - Monitor consequence │
└─────────────────────────┘
        |
        v (M5: Memory)
┌─────────────────────────┐
│   Memory Layer          │
│  ┌─────────────────────┐│
│  │ Pattern Detection   ││
│  │ - Recurrence        ││
│  │ - Drift             ││
│  │ - Anomaly           ││
│  │ → Alert / Learn     ││
│  └─────────────────────┘│
└─────────────────────────┘
```

### Critical Implementation Notes

**M1 (Agent) Enforcement:**
- Do NOT modify agent outputs
- Do NOT replace agent reasoning
- Record AS-IS for evidence chain
- Expectation: Agent is responsible for its quality

**M2 (Evidence) Enforcement:**
- Write-gate: All evidence required before proceeding to M3
- Schema validation: Every field must conform
- Hash protection: Evidence cannot be altered once recorded

**M3 (Composition) Enforcement:**
- Structural merge only (combine, don't modify)
- Conflict resolution method is recorded (not hidden)
- Composition Object is immutable snapshot

**M4 (Authority) Enforcement:**
- NO automatic approval
- NO default acceptance
- Human reviews FULL Composition Object, not summary
- Human rationale is required (not optional)
- Signature proves human identity + intent

**M5 (Memory) Enforcement:**
- Pattern detection is reactive (post-event)
- Alerts go to Authority Layer for human decision
- No automatic remediation without human gate

---

## PART 6: INTEGRATION POINTS

### HAB with Paper 5 Protocol

| Paper 5 Element | HAB Layer | Implementation |
|-----------------|-----------|---|
| M1 Agent Responsibility | Agent Layer | Agent outputs recorded as-is; agent declares scope |
| M2 Evidence Boundary | Evidence Layer | Schema enforcement; write-gate validation |
| M3 Composition Object | Composition Layer | Structural merge; immutable record |
| M4 Authority Gate | Authority Layer | Human-only, non-delegable approval |
| M5 Recurrence Detection | Memory Layer | Pattern engine + alert to M4 |

### HAB with Institutional Memory

| MoCKA Element | HAB Role |
|---|---|
| Event Ledger | Evidence + Execution records |
| Decision Ledger | Authority Decision records |
| Integrity Classification | Anomaly detection in M5 |
| Recurrence Registry | Pattern database for M5 |

---

## PART 7: DEPLOYMENT PHASES

### Phase 1: Paper 5 Protocol Foundation (current)
- Document theory (M1-M5)
- Design Evidence + Composition layers
- Specify Authority Gate requirements

### Phase 2: HAB Layer Implementation
- Implement Evidence Layer schema
- Implement Composition Object structure
- Implement Authority Gate workflow
- Integrate with MoCKA ledgers

### Phase 3: Role-Based Enforcement
- Implement Agent Layer recording
- Implement Execution Layer monitoring
- Implement Memory Layer (M5) detection
- Implement human authority bypass protection

### Phase 4: Institutional Integration
- Connect to MoCKA Event Ledger
- Connect to MoCKA Decision Ledger
- Connect recurrence detection
- Implement institutional learning feedback

### Phase 5: External Deployment
- Validate HAB with external AI providers
- Test composition with diverse agent populations
- Verify authority preservation under load
- Conduct independent security audit

---

## PART 8: SUCCESS METRICS (not claims)

### Design-Level Success (Phases 1-3)

- [ ] M1-M5 are implemented as specified layers
- [ ] Authority Layer enforces non-delegable human review
- [ ] Evidence Layer captures complete decision rationale
- [ ] Composition Object structure handles 3+ agents
- [ ] Memory Layer detects recurrence patterns

### Operational Success (Phases 4-5)

- [ ] Zero unrecorded decisions in HAB-protected paths
- [ ] 100% of Authority decisions are human-made (no bypass)
- [ ] Institutional memory enables >80% anomaly detection
- [ ] External audit confirms transparency property
- [ ] HAB composes with GPT, Gemini, Claude without modification

### Institutional Success (Phase 5+)

- [ ] Knowledge accumulation enables operational improvement
- [ ] Failure analysis reduces recurrence rates
- [ ] Human authorities report increased confidence in composed decisions
- [ ] Institutional memory becomes asset, not liability

---

## CONCLUSION

**HAB is the operational embodiment of Paper 5 theory.**

Paper 5 provides the theoretical framework and guarantees.  
HAB provides the architectural layers and implementation roadmap.

Together they answer the composition problem:
- Individual AI responsibility (M1)
- Evidence completeness (M2)
- Composed decision structuring (M3)
- Human authority preservation (M4)
- Institutional learning (M5)

Next step: PHASE 4 — JARVIS connection design.

---

**END PHASE 3 DOCUMENT**

Status: ARCHITECTURE BRIDGE COMPLETE
