# MOCKA TOP 10 CRITICAL IMPLEMENTATION GAPS
## Executive Ranking & Action Items

**Date**: 2026-09-13  
**Classification**: Audit Summary (Read-only investigation)  
**Authorization State**: HOLD / NOT_GRANTED

---

## RANK 1: E13-E22 UNPROTECTED EXECUTION PATHS (10 paths, 66.7%)

### Issue
Ten consequential execution paths execute subprocess/state mutations WITHOUT M18 authorization guard.
These paths execute via app.py daemon threading and interface routing without verifying user/HG authorization.

### Evidence
- **Location**: M18_RUNTIME_ENFORCEMENT_VERIFICATION_FULL_REPORT_20260912.md
- **Files**: runtime/auto_runner.py (E06-E08), runtime/mocka_drift_loop.py (E09), runtime/event_watcher.py (E10-E11), runtime/error_capture_engine.py (E12), interface/civilization_bridge.py (E13), interface/essence_auto_updater.py (E14), interface/reflux.py (E15), interface/risk_interpreter.py (E16), interface/router_*.py (E17-E19), interface/router_playwright.py (E20), interface/simulation_layer.py (E21), interface/user_voice_importer.py (E22)
- **Test Result**: A10 adversarial test: FAIL (direct subprocess not blocked)
- **Coverage**: 0% protected (0/10)

### Impact
- **Severity**: CRITICAL
- **Category**: P1 - Runtime Enforcement
- **Risk**: Authorization bypass; state mutations without governance verification
- **Timeline**: Blocks kernel-wide enforcement closure
- **Evidence Gap**: Execution results not audited; no decision_id tracking

### Current State
```
Entry Point → subprocess.run/Popen() → [NO GUARD] → State Change
```

### Required Fix
```
Entry Point → M18 Guard (before_context_update) → AuthorizationResolver.resolve()
           → BLOCK if unauthorized → ALLOW → subprocess.run → Audit
```

### Implementation Scope
- Add M18 guards to ~10 subprocess entry points (3-5 LOC each)
- Add result audit logging for E06-E22 (similar to E01-E05)
- Extend AuthorizationResolver to cover new entry points
- Create integration tests for each E06-E22 path

### Estimated Effort
- Implementation: 40-60 LOC
- Testing: 200-300 LOC
- Timeline: 1-2 implementation + review cycles

---

## RANK 2: HG DECISION → SEALED OBJECT → EXECUTION CHAIN UNKNOWN

### Issue
How do Human Gate authorization decisions actually become runtime enforcement? 
The chain is not demonstrated:
1. HG Decision created → ?
2. SealedAuthorizationObject populated → ?
3. M18 guard reads sealed object → ?
4. Execution allowed/blocked → ?

### Evidence
- **Location**: M18_RUNTIME_ENFORCEMENT_VERIFICATION_FULL_REPORT_20260912.md, PHASE 4
- **Finding**: "HG → Authorization: Decision Ledger: NOT_FOUND, Sealed Object creation: NOT_FOUND in E01-E05 protected paths"
- **Code Search**: SealedAuthorizationObject instantiation not found in action_executor.py or before_context_update()
- **Ledger Status**: decision_ledger.jsonl designed; no evidence of HG writes at runtime

### Impact
- **Severity**: CRITICAL
- **Category**: P0 - Authorization Gate
- **Risk**: HG authority may not be enforced; decisions disappear in implementation
- **Timeline**: Blocks HG authority validation
- **Evidence Gap**: No decision_id field in execution audit logs; no HG decision history accessible

### Current State
```
HG Decision → [Unknown Connection] → SealedAuthorizationObject
SealedAuthorizationObject → [Unknown Reading] → M18 Guard enforcement
```

### Investigation Required
1. Trace HG decision creation entry point
2. Find where SealedAuthorizationObject is created (if at all)
3. Verify M18 guard reads from sealed object
4. Demonstrate decision_id binding to execution context

### Deliverables (HG-Required)
- [ ] Documented execution path from HG decision to M18 enforcement
- [ ] SealedAuthorizationObject instantiation point identified
- [ ] Decision_id tracking added to execution audit logs
- [ ] E-to-E test of HG decision → authorization enforcement

---

## RANK 3: M11 IN-FLIGHT REVERIFICATION NOT WIRED

### Issue
M11 code exists (phi_os/runtime/in_flight_reverification.py) but is not connected to action execution.
Long-running operations cannot reverify authorization during execution.

### Evidence
- **Code Present**: phi_os/runtime/in_flight_reverification.py (InFlightReverificationGuard class)
- **Methods**: capture_snapshot(), check_at_interval()
- **Wiring**: NOT_FOUND in execute_action() or app.py thread handlers
- **Test Status**: No evidence M11 is invoked during action execution
- **Report**: M18_RUNTIME_ENFORCEMENT_VERIFICATION_FULL_REPORT, PHASE 3 (M11 not proven wired)

### Impact
- **Severity**: HIGH
- **Category**: P1 - Runtime Enforcement
- **Risk**: Long-running operations cannot detect authorization revocation mid-execution
- **Timeline**: Blocks in-flight reverification closure
- **Evidence Gap**: No snapshots of authorization state changes in event logs

### Current State
```
M11 Code (phi_os/runtime/in_flight_reverification.py) → [NOT CALLED] → execute_action()
```

### Required Fix
1. Import M11 into execute_action() and app.py threading spawners
2. Call capture_snapshot() before long-running subprocess
3. Call check_at_interval() during operation (or as post-execution check)
4. Log reverification results (snapshot_state, auth_status_at_check, action_taken)
5. Block execution if authorization revoked

### Implementation Scope
- Import M11 in runtime/action_executor.py
- Add snapshot capture before subprocess calls
- Add interval checks for long-running operations (optional v1; required for full closure)
- Add reverification results to action_result.json

### Estimated Effort
- Implementation: 30-50 LOC
- Testing: 100-200 LOC
- Timeline: 1 implementation + review cycle

---

## RANK 4: DECISION LAYER → GL7 INTEGRATION UNVERIFIED

### Issue
Decision Layer generates risk/priority scores designed to inform GL7 (Execution Governance) actions.
Integration and actual GL7 usage is not demonstrated or tested.

### Evidence
- **Design**: DECISION_LAYER.md specifies risk_factors/risk_score as GL7 input
- **Code**: decision/decision_engine.py, decision/risk_analyzer.py
- **Integration**: No code path found where GL7 reads DecisionResult
- **Test**: No integration tests of decision → GL7 influence
- **Action Profile**: write_heavy should flag for Read-Only Tools enforcement; not verified

### Impact
- **Severity**: HIGH
- **Category**: P1 - Runtime Enforcement
- **Risk**: Decision risk scores may not influence governance execution
- **Timeline**: Blocks decision-governance closure
- **Evidence Gap**: Cannot verify GL7 acts on decision risk assessment

### Current State
```
Decision Engine (risk_score=0.8) → [Unknown Consumption] → GL7 (Dry Run / Default Deny?)
```

### Investigation Required
1. Find GL7 execution decision point
2. Verify GL7 reads DecisionResult.risk_factors
3. Verify GL7 uses risk_score in Dry Run / Default Deny logic
4. Add test case: decision (risk=high) → GL7 (throttle/deny)

### Deliverables
- [ ] GL7 entry point identified
- [ ] GL7 uses DecisionResult.risk_factors verified
- [ ] Integration test: decision risk → GL7 action
- [ ] Action profile enforcement (write_heavy → read-only tools flagging)

---

## RANK 5: ZERO INTEGRATION TESTS FOR E06-E22

### Issue
10 consequential execution paths (E06-E22) have zero integration tests.
Each path's correctness, authorization enforcement, and audit logging cannot be verified.

### Evidence
- **Test Directory**: tests/ exists; E06-E22 tests not found
- **M18 Tests**: 61/61 regression tests PASS (E01-E05 only)
- **Coverage**: 0% for E06-E22 paths
- **Adversarial Tests**: A01-A09 PASS; A10 FAILS (demonstrates E06-E22 bypass)

### Impact
- **Severity**: HIGH
- **Category**: P1 - Test Coverage
- **Risk**: Cannot verify execution correctness or enforcement
- **Timeline**: Blocks test coverage closure
- **Evidence Gap**: No way to validate enforcement changes

### Current State
```
E01-E05: 61 regression tests ✓
E06-E22: 0 tests ✗
```

### Required Fix
Create integration tests for each E06-E22 path:
- Test happy path (normal execution)
- Test authorization denial (blocked execution)
- Test state mutation audit logging
- Test error handling

### Test Matrix
```
E06 (auto_runner): 4 tests (normal, blocked, audit, error)
E07-E08 (subprocess variants): 3 tests each
E09 (drift_loop): 4 tests
E10-E11 (event_watcher): 3 tests each
E12 (error_capture): 4 tests
E13 (civilization): 4 tests
E14-E22 (remaining 9 paths): 3-4 tests each

Total: ~50-60 new integration tests
```

### Estimated Effort
- Test implementation: 1500-2000 LOC
- Setup/fixtures: 200-300 LOC
- Timeline: 2-3 implementation + review cycles

---

## RANK 6: HG DECISION LEDGER NOT POPULATED AT RUNTIME

### Issue
Decision Ledger schema designed (data/decisions/decision_ledger.jsonl) but no evidence HG decisions are written to it during execution.
Cannot audit HG decision history or verify HG→execution binding.

### Evidence
- **Ledger File**: data/decisions/decision_ledger.jsonl exists
- **CLAUDE.md Protocol**: mocka_decision_write() designed to write to ledger
- **Runtime Writes**: No evidence decision writes occur at HG decision point
- **Audit Trail**: No decision_id field in execution audit logs (action_result.json)

### Impact
- **Severity**: MEDIUM
- **Category**: P2 - Evidence / Audit Trail
- **Risk**: Cannot verify HG decisions or decision history
- **Timeline**: Required for audit completeness
- **Evidence Gap**: HG decision audit trail missing

### Current State
```
HG Decision Created → [Decision ledger write code exists] → [But not called at runtime?]
Execute Action → [No decision_id field] → action_result.json (audit log)
```

### Investigation Required
1. Find HG decision creation entry point (human_gate.py, human_gate_cli.py)
2. Verify mocka_decision_write() called after decision creation
3. Verify decision_id returned and stored
4. Add decision_id to action_result.json audit records
5. Add evidence collection test

### Deliverables
- [ ] HG decision → mocka_decision_write() chain documented
- [ ] decision_id tracking added to action_result.json
- [ ] Integration test: HG decision → ledger → execution link

---

## RANK 7: ARTICLE 6 (SINGLE ENTRY POINT) VIOLATED

### Issue
Architecture Article 6 states: "All operations via router.py"
Evidence: E06-E22 directly call subprocess.run/Popen; bypass router and governance control.

### Evidence
- **Article**: CONSTITUTION.md Article 6
- **Violation**: Direct subprocess calls in auto_runner.py, interface/*, governance/*.py
- **M18 Status**: Only E01-E05 routed through governance
- **Impact**: 10 consequential paths bypass governance architecture

### Impact
- **Severity**: HIGH
- **Category**: P1 - Governance Architecture
- **Risk**: Governance control bypassed; subprocess execution uncontrolled
- **Timeline**: Architectural violation requiring systematic fix
- **Evidence Gap**: Execution bypasses audit logging (partial)

### Current State
```
Article 6 Design: [All] → Router → [Governance] → [Execution]
Actual: E01-E05 → Router ✓; E06-E22 → [Direct subprocess] ✗
```

### Required Fix
Route all E06-E22 subprocess calls through router with M18 guards (same as Rank 1).
This is the primary implementation fix.

---

## RANK 8: ARTICLE 7 (MULTI-AUDIT) INCOMPLETE

### Issue
Article 7: "Critical decisions require orchestra (multi-audit)"
Orchestra directory minimal (2 files); no routing mechanism for high-risk decisions.

### Evidence
- **Article**: CONSTITUTION.md Article 7
- **Directory**: orchestra/ (2 files only)
- **Routing**: No code path routes write_heavy/fix intents to multi-audit
- **Integration**: Orchestra not called from decision engine

### Impact
- **Severity**: MEDIUM
- **Category**: P1 - Governance Architecture
- **Risk**: High-risk decisions (write_heavy, fix) not routed to multi-audit verification
- **Timeline**: Required for critical decision governance
- **Evidence Gap**: No evidence multi-audit occurs; no audit logs

### Current State
```
Decision (intent=write_heavy, risk=high) → [Should route to orchestra] → [Not routed]
```

### Required Fix
1. Implement orchestra routing logic
2. Route write_heavy/fix/high-risk decisions to orchestra
3. Implement multi-audit verification (multiple reviewers/systems)
4. Log multi-audit results

### Estimated Effort
- Implementation: 100-150 LOC
- Testing: 150-200 LOC
- Timeline: 2 implementation + review cycles

---

## RANK 9: A10 ADVERSARIAL TEST FAILURE

### Issue
Adversarial test A10 (direct subprocess call) FAILS: Demonstrates that authorization guards can be bypassed.
Entry points that directly call subprocess.run/Popen can execute without M18 guard.

### Evidence
- **Test**: M18_RUNTIME_ENFORCEMENT_VERIFICATION_FULL_REPORT, PHASE 5, Test A10
- **Result**: A10 FAILS; A01-A09 PASS
- **Implication**: Existing M18 guards (E01-E05) are effective, but E06-E22 patterns are not guarded

### Impact
- **Severity**: CRITICAL
- **Category**: P1 - Security / Bypass Prevention
- **Risk**: Demonstrates feasibility of authorization bypass
- **Timeline**: Must be fixed before production deployment
- **Evidence Gap**: Bypass patterns logged; mitigation not applied

### Current State
```
Direct subprocess.run() call → [M18 Guard: NOT PRESENT] → Execution succeeds without authorization
```

### Required Fix
Same as Rank 1: Add M18 guards to all E06-E22 subprocess calls.
After fix, A10 test must be re-run and PASS.

---

## RANK 10: LEARNING KERNEL FEEDBACK LOOP UNDEMONSTRATED

### Issue
Learning Kernel designed to implement incident-to-prevention feedback (part of README "civilization loop").
Execution of feedback loop not demonstrated; learning not operational.

### Evidence
- **Design**: README.md, LEARNING_KERNEL.md
- **Code**: learning_kernel/ (12 files)
- **Feedback Path**: Incident → Recurrence Registry → Prevention Rules → Decision Prevention
- **Evidence**: No demonstrated incident-to-prevention cycle
- **Test**: No tests of learning loop effectiveness

### Impact
- **Severity**: MEDIUM
- **Category**: P2 - System Maturity
- **Risk**: System cannot learn from incidents autonomously
- **Timeline**: Desirable for production maturity
- **Evidence Gap**: No learning effectiveness data

### Current State
```
Incident Detected → Recurrence Registry ✓ → Prevention Loop ✗ → Decision Adjustment ✗
```

### Investigation Required
1. Trace incident detection → recurrence registry → prevention rule creation
2. Verify prevention rules influence decision engine
3. Demonstrate incident avoidance through learning
4. Add learning loop test

### Deliverables
- [ ] Learning loop operation documented
- [ ] Incident → prevention rule chain demonstrated
- [ ] Learning effectiveness test

---

## SUMMARY RANKING TABLE

| Rank | Component | Type | Severity | Category | Blocker | Timeline |
|------|-----------|------|----------|----------|---------|----------|
| **1** | E06-E22 Unprotected | Wiring | CRITICAL | P1 Enforcement | **YES** | Phase 1 (immediate) |
| **2** | HG → Sealed Object Chain | Evidence | CRITICAL | P0 Auth Gate | **YES** | Phase 1 (immediate) |
| **3** | M11 Not Wired | Wiring | HIGH | P1 Enforcement | YES | Phase 1 |
| **4** | Decision → GL7 | Wiring | HIGH | P1 Enforcement | YES | Phase 1 |
| **5** | E06-E22 No Tests | Test | HIGH | P1 Testing | YES | Phase 1 |
| **6** | HG Ledger Not Used | Evidence | MEDIUM | P2 Audit | No | Phase 2 |
| **7** | Article 6 Violated | Architecture | HIGH | P1 Architecture | Yes (rank 1 fix) | Phase 1 |
| **8** | Article 7 Incomplete | Architecture | MEDIUM | P1 Architecture | No | Phase 2 |
| **9** | A10 Test Fails | Test | CRITICAL | P1 Security | **YES** | Phase 1 |
| **10** | Learning Loop | Design | MEDIUM | P2 Maturity | No | Phase 3 |

---

## IMPLEMENTATION TIMELINE

### PHASE 1 (M18-FULL-PROTECTION-CLOSURE) — MANDATORY
**Blockers that must be resolved before any deployment**

1. **E06-E22 M18 Guards** (Rank 1) — 40-60 LOC implementation
2. **HG → SealedObject Chain** (Rank 2) — Investigation + 50-100 LOC
3. **M11 Wiring** (Rank 3) — 30-50 LOC implementation
4. **Decision → GL7** (Rank 4) — 20-40 LOC + testing
5. **E06-E22 Tests** (Rank 5) — 1500-2000 LOC
6. **A10 Test Closure** (Rank 9) — Fixed by Rank 1; verify PASS

**Effort**: ~150-200 LOC core implementation; ~2000 LOC tests
**Timeline**: 2-3 implementation cycles + comprehensive review

### PHASE 2 (EVIDENCE-TRAIL-CLOSURE) — RECOMMENDED
**Improves audit completeness and decision tracking**

7. **HG Decision Ledger** (Rank 6) — 30-50 LOC
8. **Article 7 Multi-Audit** (Rank 8) — 100-150 LOC

**Effort**: ~150-200 LOC
**Timeline**: 2 implementation cycles

### PHASE 3 (OPERATIONAL-MATURITY) — OPTIONAL
**Improves system autonomy and learning**

10. **Learning Kernel Loop** (Rank 10) — 200-300 LOC

**Effort**: ~200-300 LOC
**Timeline**: 1-2 implementation cycles

---

## HUMAN GATE DECISIONS REQUIRED

For each rank-1 blocker, HG must decide:

1. **E06-E22 Protection**: Extend M18 to all paths, or accept partial protection?
2. **HG Authority Chain**: Demonstrate and document HG→execution binding, or accept unknown enforcement?
3. **M11 Integration**: Wire reverification to long-running ops, or accept mid-execution bypass risk?
4. **GL7 Integration**: Verify decision risk influences GL execution, or accept unused risk scores?
5. **Test Mandate**: Require 100% integration tests before deployment, or accept untested paths?

---

**AUDIT COMPLETE**

**Next Phase**: Human Gate review of blockers and timeline decisions

