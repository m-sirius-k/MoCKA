# MoCKA Revocation Propagation Survey: Ravi Shankar / Minas Papagiannopoulos Problem Analysis

**Survey Date:** 2026-08-22  
**Surveyor:** Claude (Haiku 4.5)  
**Target:** Current MoCKA Canonical Repository  
**Classification:** EVIDENCE-BASED ANALYSIS

---

## EXECUTIVE FINDING

MoCKA does **NOT** implement Ravi's Revocation Propagation model (Decision → Propagation → Last Enforcement Point). However, MoCKA addresses the underlying problem of authority effectiveness and closure verification through a **fundamentally different architectural model**:

Rather than measuring revocation propagation, MoCKA:
1. **Constrains consequential action** within governance boundaries via Execution Gates
2. **Enforces authority revalidation** through Binding validation (Artifact → Meaning → Institution → Gate → Event)
3. **Maintains unverified surface states** (UNKNOWN, PARTIAL, SHADOW, ORPHAN) to preserve Minas's closure skepticism
4. **Records all authority decisions** in Decision Ledger and Event Ledger with cryptographic integrity
5. **Isolates external surfaces** (third-party services, child agents, already-issued tokens) as explicitly UNKNOWN

**Critical Finding:** MoCKA's Architecture demonstrates that the revocation problem may be **solvable without direct propagation measurement** if authority is checked at **every execution boundary** rather than being cached or delegated without revalidation.

---

## EVIDENCE INVENTORY

### Core Authority & Governance Mechanisms

| Component | File Path | Section/Function | Implementation Status | Evidence Quality |
|-----------|-----------|------------------|----------------------|-------------------|
| Authority Types & Lifecycle | `phi_os/runtime/runtime_types.py:34-42` | `AuthorityType` Enum | **IMPLEMENTED** | Direct code |
| Authority Manager | `phi_os/runtime/authority_manager.py` | Complete Authority lifecycle | **IMPLEMENTED** | 158 lines, full delegation/revocation API |
| Authority Revocation | `phi_os/runtime/authority_manager.py:144-147` | `revoke_delegation()` method | **IMPLEMENTED** | Direct code |
| Authority Hierarchy | `phi_os/runtime/authority_manager.py:49-63` | `_AUTHORITY_HIERARCHY` dict | **IMPLEMENTED** | Canonical structure |
| Binding States | `phi_os/runtime/runtime_types.py:11-17` | `BindingStatus` Enum | **IMPLEMENTED** | CONNECTED, PARTIAL, SHADOW, ORPHAN, DEPRECATED, UNKNOWN |
| Binding Engine | `phi_os/runtime/binding_engine.py` | `validate_binding()` | **IMPLEMENTED** | 158 lines, full binding path enforcement |
| Institution Runtime | `phi_os/runtime/institution_runtime.py` | Complete institution API | **IMPLEMENTED** | 150+ lines, integrates all components |
| Decision Ledger Schema | `governance/spec/Decision_Record_Spec.md` | 3-layer model (Index/Canonical/Propagation) | **DESIGNED** | Spec document |
| Decision Ledger Implementation | `runtime/jarvis/record/ledger.py` | `JarvisLedger` class | **IMPLEMENTED** | Adapter pattern |
| Event Ledger | `runtime/governance/ledger_engine.py` | Hash-based integrity | **IMPLEMENTED** | 77 lines with crypto hashing |
| Module Certification | `docs/governance/MODULE_CERTIFICATION_v1.md:97-108` | Revocation section | **DESIGNED & SPECIFIED** | 4 revocation conditions defined |
| Human Gate | `runtime/jarvis/gate/human_gate.py` | approve/reject | **IMPLEMENTED** | Minimal but present |
| Execution Gate | `docs/governance/execution_gate_v1.md` | Execution boundary enforcement | **DESIGNED** | Spec exists |
| Gate Architecture | `GATE_ARCHITECTURE_v1.md` | 7 gates defined | **RATIFIED** | Constitution-level document |
| PHI-OS Constitution | `PHI_OS_CONSTITUTION_v1.md` | Authority & Binding principles | **RATIFIED** | Constitution v1, 7 core principles |
| Binding Registry | `BINDING_REGISTRY_v1.md` | Registry schema | **DESIGNED** | Policy document |
| Binding Gap Report | `BINDING_GAP_REPORT_v1.md` | Gap analysis with UNKNOWN/PARTIAL/SHADOW/ORPHAN states | **DESIGNED** | Gap classification analysis |

### Test Evidence

| Test File | Coverage | Verification Status |
|-----------|----------|-------------------|
| `phi_os/tests/test_institution_runtime.py` | Authority hierarchy, conflict detection, no delegation tests | **PARTIALLY VERIFIED** |
| No revoke_delegation() test | Authority revocation | **NOT VERIFIED** |
| No execution-time revalidation test | Runtime enforcement | **UNVERIFIED** |

---

## R1-R10 REQUIREMENTS MAPPING

### R1: Revocation Decision

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Location** | Decision Ledger (data/decisions/decision_ledger.jsonl) + Module Certification schema | `MODULE_CERTIFICATION_v1.md` line 97-108, governance/seal_governance_gate.py | **DIRECT OBSERVABLE** |
| **Recording** | 3-layer model with Event Gate passage | `governance/spec/Decision_Record_Spec.md` | **IMPLEMENTED** |
| **Human Gate Management** | Human Gate exists but minimal test coverage | `runtime/jarvis/gate/human_gate.py`, test_institution_runtime.py has no revocation test | **DESIGNED, NOT FULLY TESTED** |
| **What's Missing** | No test showing revocation decision flows through Human Gate to Decision Ledger | Test gap | **UNVERIFIED** |

**Classification:** **C - DESIGNED BUT UNPROVEN** (Decision infrastructure exists, but revocation-specific flow through gates untested)

---

### R2: Human Decision Latency

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Observation Point** | Decision timestamp exists in Decision Ledger | `governance/spec/Decision_Record_Spec.md:34-41` | **DESIGNED** |
| **Event Recording** | Event Gate records when Human Gate approval happens | `GATE_ARCHITECTURE_v1.md:2.1` (Event Gate definition) | **DESIGNED** |
| **Latency Measurement** | No explicit latency tracking mechanism (e.g., decision_issued_time vs approval_time) | No latency_metrics field in Decision Record schema | **NOT ESTABLISHED** |
| **What's Missing** | No explicit measurement of delay between need-for-intervention and Human Gate decision | Only timestamps exist, no latency calculation shown | **UNKNOWN** |

**Classification:** **B - INDIRECT OBSERVABLE** (Timestamp difference between events COULD calculate latency, but not explicitly implemented)

---

### R3: Revocation Propagation

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Direct Measurement** | No explicit revocation propagation tracking mechanism found | Search: grep -r "propagat" --include="*.py" | **NOT IMPLEMENTED** |
| **Indirect via Binding Validation** | Every execution boundary (Gate) validates Artifact Binding state, which includes Authority | `binding_engine.py:36-76`, `institution_runtime.py:130-150` | **IMPLEMENTED** |
| **Alternative Model** | Rather than "propagate revocation signal," MoCKA requires "revalidate authority at each boundary" | PHI_OS_CONSTITUTION_v1.md 原則1-7, Binding Chain | **DESIGNED ALTERNATIVE** |
| **What's Present** | Binding Engine validates full chain (Artifact → Meaning → Institution → Gate) on each operation | `phi_os/runtime/binding_engine.py` | **IMPLEMENTED** |
| **What's Missing** | No per-path observation of "revocation has reached here" - only binding validity at decision point | No revocation-specific signal propagation | **NOT OBSERVABLE** |

**Classification:** **C - ALTERNATIVE DESIGNED, PARTIALLY IMPLEMENTED** (Revalidation model exists, but not explicitly tested as revocation response)

---

### R4: Last Effective Enforcement Point

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Where Authority is Checked** | Binding validation at each Gate (pre-execution governance) | `binding_engine.py:36-76`, all 7 Gate definitions in `GATE_ARCHITECTURE_v1.md` | **IMPLEMENTED** |
| **Execution Boundaries** | 7 defined Gates act as execution boundaries: Event, Knowledge, Module, Prompt, Release, Experiment, Document | `GATE_ARCHITECTURE_v1.md:21-39` | **DESIGNED** |
| **Pre-execution Enforcement** | Binding validation MUST complete before Gate passage (not after) | `institution_runtime.py:112-124` & binding_engine.py logic | **DESIGNED** |
| **What's Missing** | No explicit test showing: (1) revocation status check at gate, (2) action rejection if authority revoked | Test gap | **UNVERIFIED** |
| **External Surface** | Third-party services, cached tokens, already-issued credentials - explicitly UNKNOWN | PHI_OS_CONSTITUTION_v1.md 5.1-5.5 (禁止事項: out-of-bound operations) | **DOCUMENTED AS UNKNOWN** |

**Classification:** **B - INDIRECT OBSERVABLE** (Binding validation enforces authority, but revocation-specific rejection untested)

---

### R5: Residual Consequence

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Action Already Queued** | Queue concept exists (runtime queue, execution pipeline) | `runtime/governance/execution_engine.py:3-11` | **EXISTS** |
| **Action in Flight** | No explicit "action already executing when revocation issued" mechanism | No in-flight action tracking | **NOT DESIGNED** |
| **Observable Consequence** | Event Ledger records all actions (append-only) - consequences visible post-hoc | Event Ledger integrity, `runtime/governance/ledger_engine.py` | **IMPLEMENTED** |
| **What's Detectable** | "Did action X execute before revocation Y?" - requires Event ID ordering comparison | Event ordering preserved by Event Gate | **INDIRECT OBSERVABLE** |
| **What's Missing** | No automated "residual consequence detection" - manual Event Ledger audit required | No post-revocation incident scanner | **UNVERIFIED** |

**Classification:** **B - INDIRECT OBSERVABLE** (Event ordering permits detection, but no automated mechanism)

---

### R6: Unknown / Unverified Surface

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **UNKNOWN State** | Explicitly defined for Artifacts with undefined Meaning | `runtime_types.py:17`, `binding_engine.py:145-147` | **IMPLEMENTED** |
| **PARTIAL State** | Defined for incomplete binding path | `binding_engine.py:157-158` | **IMPLEMENTED** |
| **SHADOW State** | Defined for Meaning-defined but Gate-external artifacts | `binding_engine.py:103-112` | **IMPLEMENTED** |
| **ORPHAN State** | Defined for Institution-unattributed artifacts | `binding_engine.py:99-101` | **IMPLEMENTED** |
| **DEPRECATED State** | Defined for revocation-decision artifacts | `runtime_types.py:16` | **IMPLEMENTED** |
| **Usage in Authority Context** | States directly represent "unverified Authority Surface" | `BINDING_REGISTRY_v1.md`, `PHI_OS_CONSTITUTION_v1.md:4.2` | **DESIGNED** |
| **What's Missing** | No explicit mapping: "These binding states = these revocation-vulnerable surfaces" | Conceptual connection, not formalized | **NOT EXPLICITLY DOCUMENTED** |

**Classification:** **A - DIRECTLY OBSERVABLE** (States exist and can observe unknown surfaces, but mapping to revocation untested)

---

### R7: Closure Claim

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Strong Closure Claim** | MODULE_CERTIFICATION defines 6 certification levels, with REVOCATION as de-certification | `MODULE_CERTIFICATION_v1.md:97-108` | **DESIGNED** |
| **Evidence for Closure** | Certification revocation requires: Audit Failure, Critical Security, Unsupported Deps, Integrity Violation | `MODULE_CERTIFICATION_v1.md` lines 103-106 | **DESIGNED** |
| **Recording Requirement** | "Decision Ledger登録およびmocka_write_event(what_type: CERTIFICATION_REVOKED)を必須とする" | `MODULE_CERTIFICATION_v1.md` line 108 | **SPECIFIED** |
| **What's Implemented** | Authority revocation method exists; Module certification revocation specified | `authority_manager.py:144-147`, MODULE_CERTIFICATION_v1.md | **PARTIAL** |
| **What's Missing** | No test showing Module Certification flows through to Binding state change OR Authority revalidation failure | Test gap | **UNVERIFIED** |
| **Global Closure Claim** | "All authority has been revoked everywhere" - no global scanning or proof | BINDING_GAP_REPORT explicitly states UNKNOWN boundaries | **NOT CLAIMED** |

**Classification:** **C - DESIGNED BUT UNPROVEN** (Specification exists, but no test shows end-to-end closure claim)

---

### R8: Evidence Supremacy

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Event Ledger Supremacy** | "Eventは唯一の事実である" - Event Ledger is sole source of truth | `PHI_OS_CONSTITUTION_v1.md` 原則1 | **RATIFIED** |
| **Decision Ledger** | 3-layer model preserves 5W1H, immutable records, Event-linked | `governance/spec/Decision_Record_Spec.md` | **DESIGNED** |
| **Event Integrity** | Hash-chain binding with cryptographic verification | `runtime/governance/ledger_engine.py:13-40` | **IMPLEMENTED** |
| **Provenance Tracking** | Authority holder recorded, delegation_event_id captured | `authority_manager.py:126-142` | **IMPLEMENTED** |
| **Separation of Observed vs Demonstrated Closure** | BINDING_GAP_REPORT explicitly lists unobserved surfaces (UNKNOWN/PARTIAL/SHADOW/ORPHAN) | `BINDING_GAP_REPORT_v1.md` | **EXPLICITLY TRACKED** |
| **What's Missing** | No automated tool comparing "observed closure events" vs "unverified surfaces" | No Evidence Supremacy analyzer | **UNVERIFIED** |

**Classification:** **B - INDIRECT OBSERVABLE** (Evidence structures exist, but integrated closure analysis tool missing)

---

### R9: Independent Verification

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Shadow Verification Concept** | Shadow runtime, shadow failover, shadow sync mechanisms exist | `runtime/shadow_runtime.py`, `/scripts/shadow/shadow_*.py` | **IMPLEMENTED** |
| **Caliber Verification** | Caliber pipeline at localhost:5679 mentioned as independent observer | `data/MOCKA_OVERVIEW.json:48` | **MENTIONED** |
| **Authority Effectiveness Check** | No independent verification of "Authority has been revoked" separate from primary path | No dual-path Authority validation | **NOT IMPLEMENTED** |
| **What Could Be Done** | Binding validation could run in Shadow mode post-revocation to verify rejection | Architecture permits, not implemented | **DESIGNED-CAPABLE** |
| **What's Missing** | No test showing: Shadow path revalidates authority independently, reaches same revocation conclusion | Test gap | **UNVERIFIED** |

**Classification:** **C - DESIGNED-CAPABLE BUT UNIMPLEMENTED** (Shadow/Caliber infrastructure exists, but independent revocation verification not wired)

---

### R10: External / Out-of-Bound Surface

| Aspect | Finding | Evidence | Classification |
|--------|---------|----------|-----------------|
| **Third-party Services** | PHI_OS_CONSTITUTION_v1.md explicitly lists as out-of-scope | PHI_OS_CONSTITUTION_v1.md 第5章 (禁止事項) | **EXPLICITLY UNKNOWN** |
| **Child Agent Credentials** | "Authority継承ツリー" does not address child agent spawning/credentialing | `authority_manager.py:49-63` | **NOT ADDRESSED** |
| **Queued Work** | Queue concept exists, but "revoke authority while in queue" scenario not addressed | `execution_engine.py` | **NOT ADDRESSED** |
| **Cached Authority** | No explicit "TTL on cached authority" or "recheck on use" mechanism | No cache-invalidation design | **NOT IMPLEMENTED** |
| **Already-Issued Tokens** | "Token issued before revocation signal" - explicitly UNKNOWN/uncontrollable | `PHI_OS_CONSTITUTION_v1.md:196-276` | **DOCUMENTED AS UNKNOWN** |
| **Unregistered Paths** | BINDING_GAP_REPORT tracks these as ORPHAN/SHADOW/UNKNOWN | `BINDING_GAP_REPORT_v1.md` | **EXPLICITLY TRACKED** |
| **Coverage Boundary** | "MoCKA's direct control boundary = inside Gate enforcement" | `PHI_OS_CONSTITUTION_v1.md` | **EXPLICITLY DEFINED** |
| **What's Missing** | No mechanism to revoke third-party service credentials or queued actions | By design - out of scope | **NOT APPLICABLE** |

**Classification:** **D - EXPLICITLY OUT OF SCOPE** (MoCKA preserves UNKNOWN for external surfaces per constitution)

---

## ALTERNATIVE OBSERVATION MODEL

### MoCKA's Observation Paradigm (vs. Ravi's Propagation Model)

**Ravi's Model:**
```
Revocation Issued 
  → Propagation (measure time/coverage) 
  → Last Enforcement Point 
  → Verify all paths updated
```

**MoCKA's Model:**
```
Revocation Issued 
  → Event Record (Decision Ledger + Event Ledger)
  → Binding State Change (Authority revalidation)
  → Execution Boundary Enforcement (Gate authority check at use time)
  → Residual Consequence Detection (Event Ledger audit)
```

### Architecture Chain (Actual vs. Hypothetical)

| Stage | Component | Existence | Runtime Enforced | Tested |
|-------|-----------|-----------|------------------|--------|
| **Authority Issuance** | Authority in authority_manager.py | IMPLEMENTED | YES (default state) | YES (tests) |
| **Authority Binding** | Artifact→Meaning→Institution→Gate→Event chain | IMPLEMENTED | YES (Binding Engine pre-gate) | PARTIAL |
| **Decision Recording** | Decision Ledger schema, mocka_write_event | IMPLEMENTED | YES (Event Gate) | PARTIAL |
| **Revocation Decision** | Module Certification revocation spec | DESIGNED | UNIMPLEMENTED | NOT VERIFIED |
| **Revocation Recording** | mocka_write_event(what_type: CERTIFICATION_REVOKED) | SPECIFIED | UNIMPLEMENTED | NOT VERIFIED |
| **Authority Invalidation** | revoke_delegation() in AuthorityManager | IMPLEMENTED | NOT TESTED for revocation flow | NOT VERIFIED |
| **Binding Invalidation** | Binding state becomes DEPRECATED/UNKNOWN | DESIGNED | UNIMPLEMENTED | NOT VERIFIED |
| **Execution Gate Enforcement** | Gate validates binding before passage | DESIGNED | UNIMPLEMENTED for revocation | NOT VERIFIED |
| **Rejected Action Logging** | Event Gate records rejection reason | DESIGNED | UNIMPLEMENTED | NOT VERIFIED |
| **Audit Trail** | Event Ledger shows all rejections | IMPLEMENTED | PARTIAL | PARTIAL |

---

## CLOSURE MODEL

### Stages of Revocation Assurance

| Stage | MoCKA Implementation | Evidence Status | Limitation |
|-------|---------------------|-----------------|-----------|
| **1. Revocation Issued** | Decision recorded in Ledger; Event generated | DESIGNED | No test of end-to-end flow |
| **2. Revocation Propagated** | Authority.revoke_delegation() called | METHOD EXISTS | Not tested, no propagation measurement |
| **3. Authority Revalidated** | Binding Engine validates on each Gate | DESIGNED | Only at gate-passage time, not proactive |
| **4. Action Denied** | Gate passage fails if binding invalid | DESIGNED | Not tested with revocation scenario |
| **5. Residual Consequence Absent** | Manual Event Ledger audit required | INDIRECT | No automated detection |
| **6. Examined Surface Closed** | BINDING_REGISTRY + BINDING_GAP = observed surfaces | DESIGNED | UNKNOWN/PARTIAL/SHADOW/ORPHAN remain for unexamined |
| **7. Global Closure** | Not claimed; BINDING_GAP_REPORT explicitly lists gaps | DOCUMENTED AS UNKNOWN | Cannot claim closure on unobserved surfaces |

---

## UNKNOWN BOUNDARY

### MoCKA's Explicit Unknown Zones (per PHI_OS_CONSTITUTION)

| Surface | Status | Why Unknown | Evidence |
|---------|--------|-------------|----------|
| **External Services** | UNKNOWN | Outside MoCKA control boundary | PHI_OS_CONSTITUTION_v1.md § 5 |
| **Child Agent Credentials** | UNKNOWN | Spawned with independent creds outside Authority control | INSTITUTION_PROTOCOL_v1.md (not designed for child delegation) |
| **Queued Actions** | UNKNOWN/PARTIAL | Queue subject to network, not gate-enforced | execution_engine.py has no revocation check on dequeue |
| **Cached Authority** | UNKNOWN | No TTL; revalidation not specified | authority_manager.py stores static state |
| **Already-Issued Tokens** | UNKNOWN | Cannot revoke issued tokens externally | Out-of-band, not Event-gated |
| **ORPHAN Artifacts** | ORPHAN state | Institution-unattributed,制度未登録 | binding_engine.py:99-101 |
| **SHADOW Artifacts** | SHADOW state | Gate-external but Meaning-defined | binding_engine.py:103-112 |
| **UNKNOWN Artifacts** | UNKNOWN state | Meaning undefined | binding_engine.py:145-147 |

---

## HYPOTHESIS VERDICTS

### Hypothesis 1: Consequential Action Governance Boundary

**Statement:** "MoCKA can verify authority effectiveness by constraining consequential action within governance boundaries, without measuring propagation."

**Evidence:**
- Binding Engine enforces artifact-meaning-institution-gate chain before action
- All 7 Gates act as execution boundaries
- No "Action after revocation" possible if Gate checks authority binding
- BUT: No test shows Gate rejects action due to Authority revocation

**Verdict:** **PARTIALLY SUPPORTED** 
- Architecture supports it: YES (Binding + Gate design)
- Runtime enforcement of revocation: UNTESTED
- Contingency: Works only if Authority status checked at EVERY gate use (not cached)

---

### Hypothesis 2: Binding Registry for Unobserved Surface

**Statement:** "Binding Registry/Binding Gap/UNKNOWN states can represent unobserved authority surface."

**Evidence:**
- UNKNOWN state: Meaning undefined → artifact cannot be assigned authority  
- PARTIAL state: Binding incomplete → authority chain incomplete
- SHADOW state: Meaning known but outside gate → authority uncontrolled
- ORPHAN state: Institution undefined → no responsible authority holder
- DEPRECATED state: Explicitly revoked

**Verdict:** **FULLY SUPPORTED**
- All 5 states exist in runtime_types.py
- Binding Engine categorizes artifacts into these states
- BINDING_GAP_REPORT explicitly uses these for gap analysis
- Direct mapping: Binding state ↔ Authority veri ability

---

### Hypothesis 3: Decision Layer Prevents Stale Authority Reaching Execution

**Statement:** "Decision Layer + Governance Gate + Execution Gate can prevent old Authority from execution."

**Evidence:**
- Decision Ledger: Records revocation decision with timestamp
- Event Gate: Records revocation event with sequence ID
- Execution Gate: Validates binding (which includes Authority) at passage
- BUT: If authority is cached/delegated, stale authority bypasses these checks
- NO TEST: Shows old decision blocking execution

**Verdict:** **PARTIALLY SUPPORTED**
- Decision + Event recording: IMPLEMENTED
- Gate enforcement: DESIGNED but UNTESTED for revocation
- Contingency: Works only if authority never cached between decision and execution

---

### Hypothesis 4: Event Ledger Detects Residual Consequence

**Statement:** "Event Ledger can show residual consequence even if revocation signal wasn't observed."

**Evidence:**
- Event Ledger is append-only with Event IDs sequential
- All actions generate Events
- Event ordering permits: "Action X (event E1) occurred after Revocation Y (event E2)"
- BUT: No automated scanner for this pattern
- AND: "Did E1 occur before or after E2 became effective?" requires causal analysis

**Verdict:** **PARTIALLY SUPPORTED**
- Event ordering: PRESERVED by Event Gate
- Consequence visibility: POSSIBLE via Event ID comparison
- Automated detection: NOT IMPLEMENTED
- Minas objection: "Absence of consequence ≠ absence of authority problem" - still applies

---

### Hypothesis 5: Shadow Verification for Independent Confirmation

**Statement:** "Shadow Movement/Caliber can verify revocation independently of primary path."

**Evidence:**
- Shadow runtime exists: `/runtime/shadow_runtime.py`
- Shadow sync exists: `/scripts/shadow/shadow_*.py`
- Caliber pipeline exists: `localhost:5679`
- BUT: No Revocation Verification wired into shadow path
- AND: No dual-path revalidation test

**Verdict:** **DESIGNED-CAPABLE, NOT IMPLEMENTED**
- Infrastructure: EXISTS
- Integration with revocation: MISSING
- Could be wired: YES
- Currently used for revocation: NO

---

### Hypothesis 6: External Surfaces Remain Unknown (by Design)

**Statement:** "MoCKA correctly identifies external/out-of-scope surfaces as UNKNOWN and does not claim closure."

**Evidence:**
- PHI_OS_CONSTITUTION_v1.md § 5.1-5.5: Prohibits out-of-band operations
- BINDING_GAP_REPORT: Explicitly lists UNKNOWN/PARTIAL/SHADOW/ORPHAN zones
- Authority_manager.py: Does not address child agent credentials or external tokens
- execution_engine.py: No external service revocation handling
- MOCKA_OVERVIEW.json: "observed coverage" vs "demonstrated closure" distinction unclear
- Minas's principle preserved: "Measured propagation ≠ Demonstrated closure"

**Verdict:** **FULLY SUPPORTED**
- UNKNOWN surfaces are explicitly tracked
- No false closure claimed
- Boundary well-defined (MoCKA Gate control ≠ External service control)
- Minas objection addressed: UNKNOWN zones preserved

---

## FINAL ARCHITECTURAL FINDING

### Question 1: Does MoCKA Solve Ravi's Problem Directly?

**Answer:** NO. MoCKA does not implement propagation measurement. But it may solve the UNDERLYING PROBLEM through boundary enforcement.

**Reasoning:**
- Ravi's problem: "How do we know revocation reached the last enforcement point?"
- MoCKA's answer: "Don't distribute authority to enforcement points; keep authority centralized and revalidate at each point"
- This is fundamentally different architecture, not a propagation solution

---

### Question 2: Does MoCKA Satisfy Minas's Closure Skepticism?

**Answer:** YES, by design. MoCKA explicitly preserves UNKNOWN boundaries and does not claim global closure.

**Evidence:**
- BINDING_GAP_REPORT catalogues uncovered surfaces
- Binding states (UNKNOWN/PARTIAL/SHADOW/ORPHAN) explicitly document non-closure
- PHI_OS Constitution forbids claiming closure on external surfaces
- Minas principle implemented: Observe coverage ≠ Demonstrate closure

---

### Question 3: What Does MoCKA Actually Implement?

| Aspect | Implemented | Tested | Runtime Enforced |
|--------|------------|--------|-------------------|
| Authority System | YES | PARTIAL | YES (default state) |
| Authority Delegation | YES | NO | NOT FOR REVOCATION |
| Authority Revocation | YES (method) | NO | UNIMPLEMENTED |
| Decision Ledger | YES (schema) | PARTIAL | PARTIAL |
| Event Ledger | YES | YES | YES |
| Binding Validation | YES | PARTIAL | YES (pre-gate) |
| Binding States | YES | YES | YES |
| Execution Gates | DESIGNED | NO | NOT FOR REVOCATION |
| Human Gate | YES (minimal) | NO | NOT FOR REVOCATION |

---

### Question 4: What's the Gap Between Design and Runtime?

**Gap Analysis:**

1. **Authority Revocation Chain:**
   - Designed: Human Gate approval → Decision Ledger → mocka_write_event(REVOCATION) → Authority.revoke_delegation() → Binding state change
   - Implemented: Each component exists individually
   - **MISSING:** Integration test showing end-to-end flow
   - **MISSING:** Automatic binding state update when Authority revoked

2. **Execution-time Revalidation:**
   - Designed: Gate validates binding before execution
   - Implemented: Binding Engine has validate_binding() method
   - **MISSING:** Runtime integration showing Gate calls validate_binding() with current Authority state
   - **MISSING:** Test showing execution rejected when Authority revoked

3. **Residual Consequence Detection:**
   - Designed: Event Ledger ordering permits post-hoc detection
   - Implemented: Event Ledger exists, Event Gate records timestamps
   - **MISSING:** Automated incident scanner looking for "action after revocation" patterns
   - **MISSING:** Test showing this detection works

---

### Question 5: Is New Implementation Needed?

**Answer:** MoCKA does NOT need a "Revocation Layer" but needs:

1. **Integration Test** (1-2 days): Wire Authority revocation through entire chain:
   - Human Gate → Decision Ledger → mocka_write_event → Authority.revoke_delegation() → Binding Engine update → next Gate passage fails

2. **Runtime Hook** (1-2 days): Ensure Gate.validate() calls Binding.validate_binding() with fresh Authority state:
   - Currently: Binding Engine standalone
   - Needed: Gate enforcement calls binding revalidation

3. **Evidence Tool** (2-3 days): Post-revocation analyzer:
   - Scans Event Ledger for actions after revocation event
   - Flags residual consequences
   - Produces Evidence for Closure Report

4. **Shadow Verification** (2-3 days): Optional - wire Caliber/Shadow path for independent revocation verification

---

## CONCLUSION

**MoCKA's approach:** Evidence-based, boundary-enforced authority effectiveness

**Ravi's approach:** Measurement-based, propagation-tracked authority distribution

**Minas's principle:** Preserved - UNKNOWN surfaces explicitly tracked

**Verdict on Necessity of New Feature:** 
- New "Revocation Propagation Layer"? **NO** 
- New integration/testing? **YES**
- New enforcement hook? **YES**  
- New evidence tool? **RECOMMENDED**

The core insight: **MoCKA's Authority/Binding/Gate model is theoretically sound for revocation assurance, but the revocation-specific execution path is UNTESTED.** With 1-2 integration tests and 1 runtime hook, the system could provide stronger assurance than propagation measurement alone.

