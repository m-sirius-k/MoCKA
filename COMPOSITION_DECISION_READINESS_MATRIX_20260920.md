# COMPOSITION DECISION READINESS MATRIX
## Re-classification of PC Audit Findings

**Date:** 2026-09-20  
**Basis:** PC Composition Boundary Audit + Paper 5 thesis + HG Sept 20 decision  
**Purpose:** Separate "what HG must decide NOW" from "what needs Specification/Experiment first"

---

## 1. State / Semantic Distinction: VALID ≠ COMPOSITION_VALID ≠ EXECUTABLE

| Aspect | Detail |
|--------|--------|
| **Why Needed** | Paper 5 core: local validity ≠ composition validity. Runtime must distinguish states to implement Tn re-validation correctly. |
| **Current Evidence** | No distinction in code (governance_runtime.py treats all as binary: decision → commit). PAPER5_COMPOSITION_TRACE_SAMPLE.md uses terminology but implementation model missing. |
| **Specification Gap** | CRITICAL: Is COMPOSITION_VALID a runtime state? Observable state? Cached state? How does EXECUTABLE differ from COMPOSITION_VALID? |
| **HG Now?** | **NO** — needs specification work first. Cannot decide state model without defining what each state means for runtime behavior. |
| **Experiment First?** | **YES** — propose: implement minimal state model in sandbox, run scenario D (temporal revocation), observe whether three-tier distinction was necessary or binary suffices. |
| **Decision Trigger** | After sandbox experiment confirms/refutes three-tier model, THEN bring to HG. |

---

## 2. Temporal Re-validation: Tn Element (HG Element 1)

| Aspect | Detail |
|--------|--------|
| **Why Needed** | Without Tn re-validation, authority stale at Tn but execution proceeds. M3 closes at T0; Tn is the gap. |
| **Current Evidence** | HG decision Element 1 registered but NOT IMPLEMENTED. No code path from T0 decision to Tn revisit. |
| **Specification Gap** | CRITICAL: Re-validation is WHEN? (interval, event-driven, lazy?). By WHOM? (GL7, HAB, JARVIS?). Consequence of stale authority? |
| **HG Now?** | **NO** — EXPERIMENT FIRST is mandatory. Cannot specify re-validation without knowing cost (latency, frequency). |
| **Experiment First?** | **YES (BLOCKING)** — HG decision specifies "Performance Impact Analysis" as evidence requirement. Proposal: implement interval-based re-validation in sandbox, measure latency at various frequencies (1s, 10s, 60s, etc.), present findings to HG. |
| **Decision Trigger** | HG decides frequency/cost trade-off AFTER experiment. Then implementation can proceed. |

---

## 3. Evidence Freshness: Staleness Threshold (HG Element 2)

| Aspect | Detail |
|--------|--------|
| **Why Needed** | Staleness detection (HG Element 2) requires threshold. Without it, "evidence is stale" is undefined. |
| **Current Evidence** | MOCKA_OVERVIEW.json tracks staleness_note (self-reported), but no enforcement mechanism. Threshold is UNKNOWN/UNDEFINED. |
| **Specification Gap** | CRITICAL: Freshness = age? Authority change? Evidence-sourced data change? Different thresholds per evidence type? |
| **HG Now?** | **NO** — depends on E2 (Temporal re-validation frequency). Cannot set staleness threshold until re-validation interval is known. |
| **Experiment First?** | **YES** — follow-on from E2. Once re-validation frequency is decided, staleness threshold inverse-derives from it. |
| **Decision Trigger** | After E2 frequency is set, HG specifies staleness_threshold = re_validation_interval (or multiple thereof). |

---

## 4. Authority Persistence: T0→Tn Chain

| Aspect | Detail |
|--------|--------|
| **Why Needed** | If authority A valid at T0 but revoked at Tn, Tn execution must not proceed. Authority persistence is the rule that connects T0 decision to Tn execution. |
| **Current Evidence** | No formal rule. HG-M3 audit: "once authorized, no mechanism to revert." GL7 checks current state but NOT "was this revoked after T0?". |
| **Specification Gap** | CRITICAL: Is revocation the ONLY reason for rejection at Tn? Or are there other grounds (scope change, evidence change, etc.)? |
| **HG Now?** | **NO** — depends on all other elements (E2, E3, E5, E6). Must specify composition re-validation rules first. |
| **Experiment First?** | **YES** — temporal revocation scenario (Paper 5 D). Implement, run actual authority revocation at Tn, verify execution blocks. |
| **Decision Trigger** | After composition re-validation rule is specified (E6), bring authority persistence rule to HG. |

---

## 5. Scope Persistence: Scope Under Composition

| Aspect | Detail |
|--------|--------|
| **Why Needed** | Composed system: does scope expand? Shrink? Stay fixed? If scope shrinks, does shrunk-out component become unexecutable? |
| **Current Evidence** | No scope tracking in composition. HG decision Element 4 mentions "composition re-validation" but scope implication unspecified. |
| **Specification Gap** | CRITICAL: Scope = intersection? Union? Narrowest component? When scope changes at Tn, what is the re-validation consequence? |
| **HG Now?** | **NO** — depends on E6 (composition rule). Scope is part of composition logic, not separate. |
| **Experiment First?** | **YES** — use scenario with composed authorities of different scopes, observe behavior under composition. |
| **Decision Trigger** | After E6 composition rule specification, E5 scope rule derives from it. |

---

## 6. Composition Evaluation Rule: Component Validity + What Else? (HG Element 4)

| Aspect | Detail |
|--------|--------|
| **Why Needed** | Paper 5 thesis: local validity ≠ composition validity. Therefore composition rule ≠ simple AND(components). Must specify what ELSE is evaluated. |
| **Current Evidence** | No composition evaluation code. PAPER5_COMPOSITION_TRACE_SAMPLE.md scenario D shows "Dependency Analysis" but rule not formalized. Current code just ANDs validation/compliance/policy vertically, not horizontally across composed components. |
| **Specification Gap** | **CRITICAL (Core of Paper 5):** Beyond component VALID states, must evaluate: evidence synchrony? Authority time-ordering? Scope conflicts? Temporal ordering? Which are binding? |
| **HG Now?** | **NO (SPECIFICATION REQUIRED FIRST)** — This is the core specification work itself. Cannot ask HG to choose AND/OR without knowing what dimensions exist. |
| **Experiment First?** | **YES (FOUNDATIONAL)** — Implement test scenarios: (A) all components valid but evidence stale, (B) scope conflict, (C) temporal misorder, (D) authority subset revokes, (E) different Tn states. Observe what breaks. Document findings. |
| **Specification Work** | Based on E6 experiment, write formal "Composition Evaluation Specification" enumerating all dimensions and their binding rules. THEN bring to HG. |
| **Decision Trigger** | After spec is written and experiments confirm it, HG approves composition rule as governance decision. |

---

## 7. Current Admissibility: T0→Tn Cross-Boundary Query (HG Element 5)

| Aspect | Detail |
|--------|--------|
| **Why Needed** | Integrates all other decisions into single runtime query: "Is this currently admissible?" Must connect Evidence + Authority + Scope + Temporal + State boundaries. |
| **Current Evidence** | HG decision Element 5 registered, but API and semantics NOT SPECIFIED. Interdependent on E1–E6. |
| **Specification Gap** | CRITICAL: Cannot specify until E1–E6 are resolved. Current Admissibility = logical AND of six boundaries' Tn conditions? Or composite rule? |
| **HG Now?** | **NO** — waits on E1–E6 resolution. |
| **Experiment First?** | **YES** — once E1–E6 experimented, implement E7 as proof-of-concept query and test against all scenarios. |
| **Decision Trigger** | After E1–E6 approved by HG, E7 specification is algorithmic (derives from E1–E6 rules). Minimal HG decision needed (approval of E7 API shape). |

---

## 8. HAB Handoff Condition: Delegation Decision Ready?

| Aspect | Detail |
|--------|--------|
| **Why Needed** | HAB role: "Can we hand this decision to the next judge?" Requires clear answer format from Tn re-validation chain. |
| **Current Evidence** | HAB_COMPOSITION_ARCHITECTURE_NOTE.md exists but no executable contract. No test of HAB handing off Tn re-validation result. |
| **Specification Gap** | HAB input = (T0 decision + Tn state)? HAB output = APPROVED / REVOKE / ESCALATE? No specs for either. Also: does HAB re-evaluate or just forward? |
| **HG Now?** | **NO** — depends on E1–E7. HAB contract depends on what Tn re-validation outputs. |
| **Experiment First?** | **YES** — implement minimal HAB stub that accepts (T0 decision, Tn state) and outputs APPROVED/REVOKE/ESCALATE, run through scenarios E1–E6. |
| **Decision Trigger** | After E7 (Current Admissibility) is specified, HAB contract derives from it. HG approval of HAB contract is SMALL (contract is mechanical). |

---

## 9. JARVIS Execution Condition: Execute Safe?

| Aspect | Detail |
|--------|--------|
| **Why Needed** | JARVIS role: "Is this safe/admissible to execute NOW?" Is the YES from HAB + Current Admissibility sufficient? Or additional checks needed? |
| **Current Evidence** | JARVIS runtime/jarvis/core/engine.py is 224 bytes (skeleton). No execution policy. |
| **Specification Gap** | JARVIS input = HAB output? Additional re-checks? Re-validation at execution start? Monitoring during execution? Rollback on evidence change? |
| **HG Now?** | **NO** — depends on HAB contract (E8) and Current Admissibility (E7). |
| **Experiment First?** | **YES** — implement JARVIS stub that: (1) receives HAB approval, (2) optionally re-validates Tn at execution start, (3) executes or blocks, (4) monitors during execution. Test whether steps 2 and 4 are necessary. |
| **Decision Trigger** | After HAB contract approved, JARVIS execution policy (steps 2 and 4 necessary or not?) becomes HG decision. |

---

## 10. Cross-Boundary Dependency Ordering

| Aspect | Detail |
|--------|--------|
| **Why Needed** | Current Admissibility chains: Evidence → Authority → Scope → Temporal → State → Execution. Is this order correct? Can State be evaluated before Authority? Dependencies matter. |
| **Current Evidence** | No formal ordering. HG decision lists 5 elements but no prerequisite graph. Current code has no explicit ordering enforcement. |
| **Specification Gap** | Dependency graph: which element gates which? E4 (Authority) → E7 (Current Admissibility)? Or parallel? Circular? |
| **HG Now?** | **NO** — derives from E1–E9 specifications and experiments. |
| **Experiment First?** | **YES** — use composition scenarios, observe natural ordering. Does Authority always gate Evidence? Or sometimes evidence gates authority? |
| **Decision Trigger** | After E1–E9 experiments complete, bring dependency graph to HG for canonical ordering. |

---

## SUMMARY TABLE: What Needs What Before Proceeding

| Item | Needs Experiment? | Needs Specification? | Needs HG? | Prerequisite | Blocking? |
|------|-----|---|---|---|---|
| E1 (State distinction) | YES | After experiment | After spec | None | NO (informational) |
| E2 (Temporal frequency) | YES | After experiment | YES | None | **YES (blocks E3–E7)** |
| E3 (Staleness threshold) | Derives from E2 | YES | YES | E2 | YES (blocks staleness enforcement) |
| E4 (Authority persistence) | YES | After experiment | Defer | E6 | NO (derives from E6) |
| E5 (Scope under composition) | YES | After experiment | Defer | E6 | NO (derives from E6) |
| E6 (Composition rule) | **YES (FOUNDATIONAL)** | **YES (REQUIRED)** | YES | None | **YES (blocks E4, E5, E7, E8, E9)** |
| E7 (Current Admissibility) | YES | After E1–E6 | Minimal | E1–E6 | NO (derives from E1–E6) |
| E8 (HAB contract) | YES | After E7 | Minimal | E7 | NO (mechanical) |
| E9 (JARVIS contract) | YES | After E8 | Minimal | E8 | NO (mechanical) |
| E10 (Dependency order) | YES | After E1–E9 | NO | E1–E9 | NO (informational) |

---

## CRITICAL PATH: What Actually Blocks Implementation

### Phase 0: Experiments (Blocking)
- **E2 Temporal Re-validation Frequency:** Measure latency at different intervals
- **E6 Composition Evaluation Rule:** Identify all dimensions beyond component validity, test scenarios

### Phase 1: Specification (Conditional on Phase 0)
- **E6 Composition Specification:** Formalize rule based on Phase 0 findings
- **E1 State Model:** Confirm three-tier or binary suffices

### Phase 2: HG Decisions (Conditional on Phase 1)
1. **HG-E2:** Approve re-validation frequency
2. **HG-E3:** Approve staleness threshold (derives from E2)
3. **HG-E6:** Approve composition evaluation rule
4. **HG-E7:** Approve Current Admissibility API (derives from E6)
5. **HG-E8:** Approve HAB contract (derives from E7)
6. **HG-E9:** Approve JARVIS contract (derives from E8)

### Phase 3: Implementation (Conditional on Phase 2)
- **Sandbox:** Elements 1–5 (Current Admissibility)
- **HAB/JARVIS:** Contracts depend on Phase 2 decisions

---

## Key Insight: Not "5 Decisions" But "2 Blocking Experiments"

**PC reported:** D1–D5 decisions needed  
**Re-classified:** Only 2 experiments actually block implementation:

1. **E2 Experiment:** Temporal re-validation frequency (cost/benefit)
2. **E6 Experiment:** Composition evaluation rule (what breaks under composition)

Everything else derives from or depends on these two.

---

## Recommendation to Human Gate

**DO NOT** issue 5 separate governance decisions on D1–D5.

**INSTEAD:**

1. **Authorize Experiments:** E2 and E6 sandbox experiments
2. **Define Timeline:** When should experiments complete? (recommend: ~2 weeks)
3. **Specify Evidence:** What should experiments measure? (recommend: scenario matrix + latency + rule validation)
4. **Defer Decisions:** E1, E3, E4, E5, E7–E10 decisions until experiments yield findings

**This reduces decision fatigue and prevents over-specification.**
