# E2/E6 SANDBOX EXPERIMENT SPECIFICATION
## Minimal Definition (Experiment-Ready)

**Authority:** HG-COMPOSITION-EXP-20260920  
**Date:** 2026-09-20  
**Scope:** Sandbox-only, no production code

---

## E2: TEMPORAL RE-VALIDATION FREQUENCY IMPACT

### Objective
Measure the cost (latency, CPU, memory) of re-validating authority at different time intervals after T0 approval.

### Hypothesis (Measurement, Not Causal)
Different re-validation intervals have different performance profiles. There exists an interval that balances safety (staleness detection) and cost (overhead).

### Experimental Setup

#### Test Harness
```
1. T0: Create authority approval decision (record timestamp)
2. Tn loop (repeat 100 times):
   a. Sleep for interval (1s, 10s, 60s, event-trigger, or lazy)
   b. Call re-validation check: "Is original authority still valid?"
   c. Record: latency, CPU%, memory delta, result (VALID/REVOKED)
3. Analyze: latency distribution, cost trend, detection delay
```

#### Intervals to Measure
- **Interval A:** Fixed 1-second re-validation
- **Interval B:** Fixed 10-second re-validation
- **Interval C:** Fixed 60-second re-validation
- **Interval D:** Event-driven (measure only when authority state changes in system)
- **Interval E:** Lazy (measure only at execution start, not periodic)

**Note:** E and D require definition of "event trigger" and "execution start" in sandbox. Use mock events.

#### Measurements (Per Interval)
| Metric | Unit | Tool |
|--------|------|------|
| Latency per check | milliseconds | time.perf_counter() |
| CPU usage | % of core | psutil.cpu_percent() |
| Memory delta | MB | psutil.Process().memory_info() |
| Detection delay | seconds | (revocation_time - check_time) |
| Throughput | checks/sec | total_checks / elapsed_time |

#### Data Collection
- **Output format:** JSON (one line per iteration)
- **Location:** `/sandbox/composition_experiments_20260920/e2_measurements/`
- **Filename:** `interval_[A|B|C|D|E]_run_001.jsonl`

#### Success Criteria
✓ Data collected for all 5 intervals  
✓ ≥100 iterations per interval  
✓ Latency distribution computed (mean, p50, p95, p99)  
✓ Trade-off chart: latency vs. CPU% (showing Pareto frontier)  
✓ Breaking points identified (e.g., "Interval A: CPU > 80% at 1000 checks/sec")  

#### Decision Input to HG
"Based on measurements, recommend Interval X because [latency acceptable AND cpu < threshold AND detection delay < tolerance]"

---

## E6: COMPOSITION EVALUATION DIMENSIONS

### Objective
Identify which dimensions beyond component validity are necessary for composition validity. Determine which dimensions are "binding" (failure blocks composition).

### Hypothesis (Observational, Not Causal)
Composition validity requires more than AND(component.VALID). Some combination of:
- Evidence synchrony (timestamps alignment)
- Authority time-ordering (approval/revocation sequence)
- Scope conflicts (permission mismatches)
- Dependency cycles (circular component dependencies)
- Composition timing (evaluated at same vs. different times)

### Experimental Setup

#### Test Scenarios (A-E)
Each scenario has:
1. **Setup:** Create 2-3 composed components with specific properties
2. **Question:** "Is this composition VALID?"
3. **Ground Truth:** Predict validity based on candidate rule
4. **Observation:** Run in MoCKA runtime, observe actual decision
5. **Outcome:** Match/Mismatch vs. prediction

---

#### Scenario A: Evidence Temporal Mismatch
**Components:**
- Component X: authority decision at 2026-09-20 10:00:00 (evidence from 2026-09-20 09:00:00)
- Component Y: authority decision at 2026-09-20 10:00:00 (evidence from 2026-09-20 08:00:00)
- Component Z: authority decision at 2026-09-20 10:00:00 (evidence from 2026-09-20 11:00:00 — future)

**Question:** Is composition (X ∧ Y ∧ Z) VALID?

**Candidate Rules to Test:**
- Rule A1: AND(X.valid, Y.valid, Z.valid) → always YES (ignores evidence age)
- Rule A2: "all evidence within 1 hour" → YES (if age < 3600s)
- Rule A3: "evidence must be newer than oldest component" → depends on Z (future evidence)

**Predicted Outcome:** [TBD after implementation observes behavior]

**Measurement:**
- Record: predicted validity, actual MoCKA decision
- Dimension affected: Evidence freshness/temporal ordering

---

#### Scenario B: Scope Conflict
**Components:**
- Component X: approved for scope {API, Database} (permits both read/write)
- Component Y: approved for scope {API} (permits read only)
- Component Z: approved for scope {Database} (permits write only)

**Question:** Is composition (X ∧ Y ∧ Z) for action (read API + write DB) VALID?

**Candidate Rules to Test:**
- Rule B1: AND(X.valid, Y.valid, Z.valid) → YES (ignores scope)
- Rule B2: "scope = intersection" → NO (intersection is empty)
- Rule B3: "scope = all actions needed" → NO (no single component covers both)

**Predicted Outcome:** [TBD after implementation observes behavior]

**Measurement:**
- Record: predicted validity, actual MoCKA decision
- Dimension affected: Scope conflict

---

#### Scenario C: Authority Time-Ordering Mismatch
**Components:**
- Component X: approved by HG_AUTHORITY at 2026-09-20 10:00:00
- Component Y: approved by HG_AUTHORITY at 2026-09-20 09:00:00 (BEFORE X)
- Component Z: revoked by HG_AUTHORITY at 2026-09-20 10:30:00 (AFTER X approval)

**Question:** Is composition (X ∧ Y ∧ Z) VALID? (Z is revoked after X approved)

**Candidate Rules to Test:**
- Rule C1: AND(X.valid, Y.valid, Z.valid) → NO (Z is revoked)
- Rule C2: "must all be approved after oldest revocation" → NO (X approved before Z revoked)
- Rule C3: "evaluate at T0 only, ignore future revocations" → YES (Z was valid at T0)

**Predicted Outcome:** [TBD after implementation observes behavior]

**Measurement:**
- Record: predicted validity, actual MoCKA decision
- Dimension affected: Authority time-ordering / Temporal revocation

---

#### Scenario D: Dependency Cycle
**Components:**
- Component X: depends on Y (X valid only if Y executes first)
- Component Y: depends on Z (Y valid only if Z executes first)
- Component Z: depends on X (Z valid only if X executes first)

**Question:** Is composition (X ∧ Y ∧ Z) VALID?

**Candidate Rules to Test:**
- Rule D1: AND(X.valid, Y.valid, Z.valid) → YES (ignores cycles)
- Rule D2: "no circular dependencies" → NO (X→Y→Z→X)
- Rule D3: "detect and resolve cycles" → DEPENDS ON RESOLUTION STRATEGY

**Predicted Outcome:** [TBD after implementation observes behavior]

**Measurement:**
- Record: predicted validity, actual MoCKA decision
- Dimension affected: Dependency graph structure

---

#### Scenario E: Composition Timing (T0 vs. Tn)
**Components:**
- Component X: approved at T0 (2026-09-20 10:00:00)
- Component Y: approved at T0 (2026-09-20 10:00:00)
- At Tn (2026-09-20 10:30:00): Component X authority revoked

**Question 1:** Is composition (X ∧ Y) VALID at T0?  
**Question 2:** Is composition (X ∧ Y) VALID at Tn (after X revoked)?

**Candidate Rules to Test:**
- Rule E1: "validity at T0" → both YES (both valid at T0)
- Rule E2: "validity at Tn" → first YES, second NO (X revoked at Tn)
- Rule E3: "current admissibility" → first YES (historical), second NO (current)

**Predicted Outcome:** [TBD after implementation observes behavior]

**Measurement:**
- Record: T0 composition validity, Tn composition validity
- Dimension affected: Temporal boundary between T0 and Tn

---

### Data Collection

#### Scenario Execution
For each scenario (A-E):
1. Set up components in sandbox (mock governance runtime)
2. Run composition check
3. Record: scenario_id, component_states, predicted_validity, actual_mco_result, dimension

#### Output Format
```json
{
  "scenario": "A",
  "timestamp": "2026-09-20T...",
  "components": {
    "X": {"authority": "valid", "evidence_time": "..."},
    "Y": {"authority": "valid", "evidence_time": "..."},
    "Z": {"authority": "valid", "evidence_time": "..."}
  },
  "candidate_rules": ["A1", "A2", "A3"],
  "predicted": {"rule": "A2", "validity": true},
  "actual": {"mco_result": "VALID", "reason": "..."},
  "match": true
}
```

#### Output Location
- `/sandbox/composition_experiments_20260920/e6_scenarios/`
- Filenames: `scenario_[A|B|C|D|E]_run_001.json`

#### Success Criteria
✓ All 5 scenarios implemented  
✓ ≥3 candidate rules tested per scenario  
✓ Predicted vs. actual recorded for each  
✓ Dimension captured for each scenario  
✓ Composition Evaluation Specification (draft) written with findings  

#### Decision Input to HG
"Based on scenarios A-E, the binding dimensions for composition validity are: [enumerated list], and the composition rule is: [formal specification]"

---

## EXPERIMENT RESOURCES

### Dependencies
- Sandbox test harness (isolated from production)
- MoCKA governance runtime (mock or test instance)
- Measurement tools (psutil, time, json)
- Scenario code (Python or equivalent)

### Team Assignment
- **E2 Lead:** Implementation team (measurement engineering)
- **E6 Lead:** Specification team (scenario design + documentation)
- **Both:** Weekly sync with HG (progress check-ins)

### Timeline (PROVISIONAL TARGETS)
- **2026-09-20 (Today):** Approval + specification freeze
- **2026-09-21 (conditional):** Experiments BEGIN *only after infrastructure gate passed*
- **2026-09-27 (target Week 1):** E2 harness operational, E6 scenarios A-B done — *subject to resource availability*
- **2026-10-04 (target Week 2):** E2 data complete, E6 scenarios A-E complete — *target, not guaranteed*
- **2026-10-07 (target):** HG review findings and make decisions — *contingent on data ready*

**Note:** Actual timeline depends on infrastructure readiness and resource commitment. Delays do not change decision sequence.

---

## CRITICAL CONSTRAINTS

### During Experiment (Do Not Cross)
❌ NO production code modification  
❌ NO production activation  
❌ NO M3 changes  
❌ NO implementation of experimental findings (until 2026-10-21)  
❌ NO new phases or architecture changes  
❌ NO new large TODO lists  

### During Experiment (Allowed)
✓ Sandbox code and test harness  
✓ Measurement and observation  
✓ Scenario design and documentation  
✓ Data collection and analysis  

---

## NEXT MILESTONE: EXPERIMENT START GATE (2026-09-20 end of day)

Before experiments proceed (Day 1), confirm:
- [ ] Sandbox infrastructure available
- [ ] E2 measurement harness skeleton ready (time/psutil integration)
- [ ] E6 scenario skeleton ready (5 test case stubs A-E)
- [ ] Data output directories created
- [ ] HG weekly check-in scheduled (2026-09-27, 2026-10-04)

**If any blocker found:** Stop here and report to HG.

**If all clear:** Proceed with experiments.

---

**Status:** READY FOR EXPERIMENT GATE REVIEW  
**Authority:** HG-COMPOSITION-EXP-20260920  
**Next Step:** Experiment start gate (end of 2026-09-20)
