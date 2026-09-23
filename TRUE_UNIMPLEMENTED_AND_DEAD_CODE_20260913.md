# TRUE UNIMPLEMENTED VS. IMPLEMENTED BUT UNUSED
## GROUP A & GROUP B Classification

**Date**: 2026-09-13  
**Purpose**: Distinguish completely absent features from dead/unused code

---

## GROUP A: TRULY NOT IMPLEMENTED (No code found)

| Component | Why Missing | Impact | Path Affected | Fix Scope |
|-----------|-------------|--------|---|---|
| **HG → SealedObject Binding** | No code creates SealedAuthorizationObject at runtime | HG decisions don't enforce | E01-E22 | HIGH |
| **GL1: execution_order_engine** | Designed in spec; not found in codebase | Execution order not controlled | All | HIGH |
| **GL2: meta_audit_engine** | Designed in spec; not found in codebase | Meta-audit not performed | All | HIGH |
| **GL4: preventive_rule_engine** | Designed in spec; not found | Preventive rules not implemented | All | MEDIUM |
| **File Classification Gate (Article 1)** | No pre-create classification mechanism | File classification governance missing | Implementation paths | MEDIUM |
| **M11 Runtime Integration** | Code exists but NOT CALLED at runtime | In-flight reverification not enforced | E01-E22 (esp. long-running) | HIGH |
| **RFC3161 Timestamp Authority** | No external TSA integration found | No cryptographic timestamps | Audit/seal | LOW |
| **Multi-Audit Orchestration (Article 7)** | Orchestra directory minimal (2 files); routing not implemented | Critical decisions not multi-audited | E01-E22 (write_heavy) | MEDIUM |
| **Decision Registry → GL7 Binding** | Designed but not wired; GL7 doesn't read DecisionResult | Risk/priority scores unused | Decision→Action | HIGH |
| **Past Decision History Feedback** | Designed; not implemented | System cannot learn from history | Decision scoring | MEDIUM |

**Total**: 10 truly absent components

---

## GROUP B: IMPLEMENTED BUT NOT WIRED (Dead code / Unused)

### B1. M11 InFlightReverificationGuard (CRITICAL)

**Status**: Code exists; not called at runtime

**Evidence**:
- File: `phi_os/runtime/in_flight_reverification.py`
- Class: `InFlightReverificationGuard`
- Methods: `capture_snapshot()`, `check_at_interval()`
- **NOT FOUND** in:
  - execute_action() import chain
  - app.py threading handlers
  - Any E01-E22 execution path

**Impact**: Long-running operations cannot reverify authorization mid-execution

**Closure**: Import M11 into execute_action() and thread spawners; call before/during/after long operations

---

### B2. Orchestra Multi-Audit System (INCOMPLETE)

**Status**: Directory exists; 2 files only; routing logic not found

**Evidence**:
- Directory: `orchestra/`
- Files: 2 Python files
- Routing logic: **NOT FOUND**
- Called from decision engine: **NO**

**Expected**: Route write_heavy/fix decisions to multi-audit verification

**Actual**: No routing mechanism; orchestra not called

**Impact**: High-risk decisions not routed to multi-audit

**Closure**: Implement orchestra routing in decision engine

---

### B3. seal_governance_gate.py (PARTIAL)

**Status**: File exists; integration unclear

**Evidence**:
- File: `phi_os/seal_governance_gate.py`
- Called by: **UNKNOWN**
- Integration with M18/HG: **UNKNOWN**

**Impact**: Seal enforcement unclear; may be dead code

**Closure**: Verify integration with M18/HG; document or remove

---

### B4. seal_auth_record.py (PARTIAL)

**Status**: File exists; HG binding not demonstrated

**Evidence**:
- File: `phi_os/seal_auth_record.py`
- HG decision binding: **NOT_DEMONSTRATED**
- Runtime usage: **UNKNOWN**

**Impact**: Authorization sealing not verified

**Closure**: Demonstrate or implement HG→sealed object binding

---

### B5. Learning Kernel Feedback Loop (PARTIAL)

**Status**: Directory exists (12 files); feedback mechanism not demonstrated

**Evidence**:
- Directory: `learning_kernel/`
- Files: 12 Python files
- Feedback execution: **NOT_DEMONSTRATED**
- Incident→prevention chain: **UNKNOWN**

**Expected**: Incident → RecurrenceRegistry → PreventionRules → DecisionAdjustment

**Actual**: Loop mechanism not demonstrated

**Impact**: System cannot learn from incidents autonomously

**Closure**: Demonstrate incident-to-prevention feedback cycle with tests

---

### B6. GL1-GL4 Governance Engines (PARTIAL)

**Status**: Designed in spec; implementations unclear

**Evidence**:
- GL1 (execution_order_engine): **NOT_FOUND**
- GL2 (meta_audit_engine): **NOT_FOUND**
- GL3 (dispatcher): Partial (router.py serves this role)
- GL4 (preventive_rule_engine): **NOT_FOUND**

**Impact**: Governance layer design not fully implemented

**Closure**: Clarify which engines are implemented where; complete missing ones

---

### B7. decision_ledger.json/jsonl (UNUSED)

**Status**: Schema designed; not populated at runtime

**Evidence**:
- File: `data/decisions/decision_ledger.jsonl`
- **Empty or stale**
- HG decision writes: **NOT_FOUND**
- mocka_decision_write() usage: **NOT_FOUND at HG decision point**

**Impact**: Cannot audit HG decision history

**Closure**: Implement HG decision → ledger write at decision creation point

---

### B8. decision_id Tracking (MISSING)

**Status**: Designed; not implemented in audit logs

**Evidence**:
- Expected field: `decision_id` in action_result.json
- Found: **NOT_FOUND**
- Ledger→execution binding: **NOT_IMPLEMENTED**

**Impact**: Cannot link execution to originating decision

**Closure**: Add decision_id field to execution audit records

---

## CLASSIFICATION SUMMARY

### GROUP A: Truly Not Implemented (10 items)
- **Severity**: P0/P1
- **Closure**: Implement from design specification
- **Timeline**: 3-5 implementation cycles
- **Examples**: HG→SealedObject binding, GL1/GL2/GL4, preventive rules

### GROUP B: Implemented But Not Wired (8 items)
- **Severity**: P1/P2
- **Closure**: Wire to runtime paths + test
- **Timeline**: 1-3 implementation cycles
- **Examples**: M11, Orchestra, Learning kernel, GL engines

---

## COMBINED A+B SUMMARY

| Item | Category | Severity | Closure |
|------|----------|----------|---------|
| HG→SealedObject | A | P0 | Implement binding + HG integration |
| GL1/GL2/GL4 | A | P1 | Implement or clarify where merged |
| M11 Runtime Wire | B | P1 | Import + call + test |
| Orchestra Routing | B | P1 | Implement routing + test |
| Decision Ledger Use | B | P1 | Wire HG→mocka_decision_write() |
| Decision_id Tracking | B | P1 | Add field + populate |
| Learning Feedback | B | P2 | Demonstrate + test |
| File Classification | A | P2 | Implement pre-create gate |
| RFC3161 TSA | A | P3 | Low priority |

---

**TOTAL**: 18 gaps across GROUP A (truly not implemented) and GROUP B (implemented but not wired/used)

