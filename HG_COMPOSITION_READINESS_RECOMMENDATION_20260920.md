# HUMAN GATE COMPOSITION READINESS RECOMMENDATION
## Re-prioritized after PC Audit + Decision Readiness Analysis

**Prepared:** 2026-09-20  
**Authority:** KUROKO PC (audit) + Composition Decision Readiness Matrix (analysis)  
**For:** Human Gate (Kimura Hakase)

---

## EXECUTIVE SUMMARY

**Previous Request:** 5 decisions (D1–D5) on composition boundaries  
**Re-analysis Result:** 2 blocking experiments → then 6 decisions → then implementation

**Recommendation:** Authorize experiments; defer decisions until findings ready

---

## WHAT CHANGED

### Before (PC Audit)
- "Composition boundaries are designed but not implemented"
- "5 decisions needed: state model, temporal strategy, composition rule, requalification, API"

### After (Decision Readiness Analysis)
- "Composition boundaries are designed but not implemented; most dependencies are derivable"
- "Only 2 things actually need Human judgment: temporal frequency and composition rule dimensions"
- "Everything else follows mechanically from those 2"

---

## BLOCKING DECISION POINTS

### DECISION POINT 1: Temporal Re-validation Frequency
**Question:** How often should authority be re-checked after T0 approval?

**Options:**
- A. Every 1 second (highest freshness, highest overhead)
- B. Every 10 seconds (balanced)
- C. Every 60 seconds (low overhead, staleness risk)
- D. Event-driven (no interval; only re-check on detected change)
- E. Lazy (re-check only at execution start)

**Why HG Judgment:** Trade-off between safety and performance cannot be specified a priori. Requires operational judgment.

**Evidence Needed First:** E2 Experiment (measure latency at each interval, identify breaking points)

**Consequence if Not Decided:** Staleness detection (E3) cannot be specified; all downstream Tn re-evaluation cannot proceed.

**HG Timeline:** After E2 experiment completes (~1 week)

---

### DECISION POINT 2: Composition Evaluation Dimensions
**Question:** Beyond component validity, what other dimensions must be evaluated for composition validity?

**Paper 5 Thesis:** Local Validity Is NOT Closed Under Composition  
**This Means:** AND(A.VALID, B.VALID, C.VALID) alone is insufficient. Something else breaks composition.

**Candidates (from scenarios):**
- Evidence temporal ordering (A's evidence older than B's?)
- Authority time-ordering (A approved later than B revoked?)
- Scope conflicts (A permits X, B forbids X?)
- Dependency cycles (A depends on B, B depends on A?)
- Composition timing (evaluated at same T0 or different times?)

**Why HG Judgment:** Only human can decide which dimensions are binding for governance. Technical implementation follows after.

**Evidence Needed First:** E6 Experiment (run scenarios A–E, document what breaks, what doesn't)

**Consequence if Not Decided:** Composition rule cannot be written; Current Admissibility cannot be specified; HAB/JARVIS contracts cannot be written.

**HG Timeline:** After E6 experiment completes (~1 week)

---

## WHAT DERIVES AUTOMATICALLY

Once the above 2 decisions are made, these 6 follow mechanically:

**3. Staleness Threshold** ← derives from E1 (if frequency is 60s, threshold is ~60s)  
**4. Authority Persistence Rule** ← derives from composition rule and temporal frequency  
**5. Scope Under Composition** ← derives from composition dimensions  
**6. Current Admissibility API** ← derives from composition rule + staleness + authority  
**7. HAB Handoff Contract** ← derives from Current Admissibility output format  
**8. JARVIS Execution Contract** ← derives from HAB output format  

These 6 do NOT require separate HG judgment; they are consequences.

---

## EXPERIMENTS REQUIRED

### E2: Temporal Re-validation Frequency Impact
**Objective:** Measure cost of re-validating authority at different intervals

**Sandbox Setup:**
- Implement re-validation loop: T0 approval → sleep → Tn re-check → repeat
- Vary interval: 1s, 10s, 60s, event-driven, lazy
- Measure: latency per interval, CPU/memory cost, staleness detection delay

**Success Criteria:**
- Data collected for all 5 interval strategies
- Latency/cost trade-off chart prepared
- Breaking points identified (e.g., "below 10ms latency, CPU exceeds threshold")

**Timeline:** ~1 week  
**Owner:** Implementation team (sandbox-only)  
**Report to HG:** Findings + recommendation for which interval to select

---

### E6: Composition Evaluation Dimensions
**Objective:** Identify which dimensions beyond component validity are binding

**Sandbox Setup:**
- Implement 5 test scenarios:
  - A: All components valid, but evidence from different times (old vs. new)
  - B: Scope conflict (component A allows X, component B forbids X)
  - C: Authority time-ordering mismatch (A approved after B revoked)
  - D: Dependency cycle (A→B→A)
  - E: Composition timing (A/B evaluated at T0, C evaluated at Tn)
- For each scenario: ask "Is composition VALID?"
- For each answer: document what rule makes it true/false

**Success Criteria:**
- All 5 scenarios implemented and tested
- For each scenario: formal rule identified that determines validity
- Composition specification draft written (enumerating all binding dimensions)

**Timeline:** ~2 weeks  
**Owner:** Specification team (design-focused)  
**Report to HG:** Composition Evaluation Specification + scenario test results

---

## IMMEDIATE ACTIONS (Before Experiments Start)

**For Human Gate:**
1. Approve E2 and E6 experiments (sandbox-only, no production changes)
2. Set timeline: target completion ~2026-10-04 (2 weeks)
3. Specify evidence template: what should be measured and reported

**For Implementation:**
1. Prepare sandbox environments for E2 and E6
2. Design test scenarios and measurement points
3. Schedule weekly progress check-ins with HG

**For Production:**
- **NO CHANGES** — Production firewall remains active
- All work confined to /sandbox/current_admissibility/

---

## DECISION TIMELINE (After Experiments)

### Week 3 (2026-10-07): HG Review of E2 + E6 Findings

**HG Decisions:**
1. **Approve temporal frequency** (and rationale for choice)
2. **Approve composition dimensions** (and binding rules)

### Week 4 (2026-10-14): Specification Finalization

**Derive + Approve:**
3. Staleness threshold
4. Authority persistence rule
5. Scope under composition
6. Current Admissibility API
7. HAB contract
8. JARVIS contract

### Week 5 (2026-10-21): Implementation Authorization

**Gate:** All 8 specifications approved  
**Next:** Sandbox implementation of Elements 1–5 (Tn re-validation, staleness, requalification, composition re-validation, API)

---

## WHY THIS APPROACH AVOIDS OVER-SPECIFICATION

**Traditional Approach:** HG decides 5 things → specification team implements 5 → code team writes 5  
**Risk:** Wrong assumptions propagate through all 5

**Recommended Approach:** Experiments → HG decides 2 → specification derives 6 → code team writes 8  
**Benefit:** Decisions grounded in evidence; derivations are mechanical; less rework

---

## DECISION NOT TO MAKE NOW

**NOT Recommended Now:**
- "Is composition validity three-tier (VALID/COMPOSITION_VALID/EXECUTABLE) or binary?"  
  → E1 experiment will show whether distinction is necessary
- "Should HAB always re-evaluate or just forward?"  
  → Depends on composition rule (E6); ask after E6
- "Does JARVIS need monitoring during execution?"  
  → Depends on JARVIS contract; ask after E8

**These Are Premature.** Ask after evidence.

---

## RISKS IF DECISIONS DELAYED

**No Immediate Risk:**
- Production is protected (firewall active)
- M3 continues operating normally
- Sandbox work unblocked

**Risk If Decisions Delayed Beyond ~2026-10-21:**
- HAB/JARVIS implementation cannot start
- Composition boundary work stalls
- Paper 5 "proof of concept" cannot complete

**Mitigation:** Experiments on 2-week timeline keeps schedule tight

---

## SUMMARY: WHAT WE ARE ASKING

**From Human Gate:**
1. **Approve 2 blocking experiments** (E2, E6) for sandbox
2. **Set timeline** (~2 weeks for experiments, 1 week for decisions)
3. **Specify evidence expectations** (what measurements matter most)

**In Return:**
- **2 grounded decisions** (not 5 speculative ones)
- **6 derived specifications** (mechanical, verifiable)
- **Clear path to HAB/JARVIS** implementation

**This is a better use of Human Gate authority: fewer judgments, but grounded in evidence.**

---

## FINAL RECOMMENDATION

**Proceed with E2 + E6 Experiments immediately.**  
**Defer all governance decisions until findings ready.**  
**Timeline: Final decisions by 2026-10-14.**

This keeps Composition work on track while ensuring decisions are grounded in evidence, not speculation.
