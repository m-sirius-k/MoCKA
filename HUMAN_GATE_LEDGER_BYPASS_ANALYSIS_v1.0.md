# HUMAN GATE → LEDGER BYPASS ANALYSIS v1.0

**Report Date**: 2026-08-13  
**Investigator**: KUROKO (Forensic Analysis)  
**Classification**: Phase 4 — Human Gate Review Support

---

## BYPASS PATHS SUMMARY

| Bypass Route | Entry Point | Bypasses HG? | Bypasses LedgerAdapter? | Creates Ledger Entry? | Risk |
|---|---|---|---|---|---|
| **MCP Direct** | mocka_decision_write | ✅ YES | ✅ YES | ✅ decision_ledger.jsonl | HIGH |
| **SealGov Direct** | SealGovernanceGate.execute | ✅ YES | ✅ YES | ✅ decision_ledger.jsonl | MEDIUM |
| **File Write Direct** | Direct I/O | ✅ YES | ✅ YES | ✅ possible | HIGH |
| **Test Path** | Jarvis HumanGate | ❌ NO | ❌ NO | ⚠️ jarvis_ledger.jsonl | LOW |
| **PHI-OS Native** | phi_os human_gate | ✅ LedgerAdapter bypass | ✅ YES | ❌ NO (mocka_events.db) | N/A |

---

## BYPASS 1: MCP DIRECT WRITE

**Entry Point**: `mocka_mcp_server.py:mocka_decision_write` handler

**Bypass Chain**:
```
MCP Client
  └─ Call: mocka_decision_write(decision_id, title, context, ...)
        └─ Handler: mocka_mcp_server.py:968-1029
            ├─ NO Human Gate check
            ├─ NO HumanGate instantiation
            ├─ NO LedgerAdapter call
            └─ Direct call: _append_decision(record)
                └─ File append: decision_ledger.jsonl
```

**Bypasses**:
- ✅ Human Gate authority (no check)
- ✅ Human Gate approval workflow (no workflow)
- ✅ LedgerAdapter validation (no call)
- ✅ Duplicate prevention (no check)

**Creates Entry In**:
- ✅ data/decisions/decision_ledger.jsonl (production Decision Ledger)

**Risk Assessment**:
- Any MCP client can create decisions
- No authority verification
- No Human Gate approval required
- Duplicates allowed
- **Risk Level: HIGH**

---

## BYPASS 2: SEAL GOVERNANCE DIRECT WRITE

**Entry Point**: `governance/seal_governance_gate.py:_record_decision_unit`

**Bypass Chain**:
```
Seal Operation
  └─ SealGovernanceGate.execute()
        ├─ GL7 governance check (pre-write)
        ├─ Seal script execution
        └─ _record_decision_unit()
            ├─ NO LedgerAdapter call
            └─ Direct file append: decision_ledger.jsonl
```

**Bypasses**:
- ✅ Human Gate authority (not in flow)
- ✅ LedgerAdapter validation (no call)
- ✅ Duplicate prevention at write time (GL7 check is pre-execution, not at write)

**Authority Present**:
- ✅ GL7 governance check (before execution)
- ✅ execution_id uniqueness
- ❌ But: No re-verification at write time

**Creates Entry In**:
- ✅ data/decisions/decision_ledger.jsonl (production Decision Ledger)

**Risk Assessment**:
- Requires GL7 governance check to pass
- GL7 check is structural, not Human Gate approval
- Re-execution/retry possible without re-check
- **Risk Level: MEDIUM**

---

## BYPASS 3: DIRECT FILE I/O

**Entry Point**: Any code with file system access

**Bypass Chain**:
```
Attacker with file access
  └─ Open file: data/decisions/decision_ledger.jsonl
        ├─ Mode: "a" (append only)
        └─ Write JSON line directly
            └─ Bypasses: All application logic
```

**Bypasses**:
- ✅ MCP/SealGov logic (file-level write)
- ✅ LedgerAdapter (not invoked)
- ✅ LedgerStore (not invoked)
- ✅ All validation (bypassed at OS level)

**Authority Present**:
- ❌ None (file-level access)

**Creates Entry In**:
- ✅ data/decisions/decision_ledger.jsonl (directly)

**Risk Assessment**:
- Requires file system access (elevated privilege)
- Can create any decision_id, any content
- No audit trail unless file is monitored
- **Risk Level: MEDIUM** (privilege requirement reduces likelihood)

---

## BYPASS 4: TEST PATH (JARVIS)

**Entry Point**: `runtime/jarvis/gate/human_gate.py:HumanGate.approve`

**Bypass Chain**:
```
Test Code
  └─ HumanGate.approve(decision_id)
        ├─ Sets status = "APPROVED"
        ├─ Calls LedgerAdapter.record()
        │   └─ LedgerStore.save() (with duplicate prevention)
        └─ Writes to: data/jarvis_ledger.jsonl
            (NOT data/decisions/decision_ledger.jsonl)
```

**Bypasses**:
- ❌ Does NOT bypass LedgerAdapter (uses it)
- ✅ Decision Ledger (different file entirely)
- ✅ Production authority model (test-only)

**Creates Entry In**:
- ❌ data/decisions/decision_ledger.jsonl (different file)
- ✅ data/jarvis_ledger.jsonl (test file)

**Risk Assessment**:
- Test-only code path
- Duplicate prevention implemented
- Does NOT affect production Decision Ledger
- **Risk Level: LOW** (isolated to test data)

---

## BYPASS 5: PHI-OS NATIVE (PRODUCTION HUMAN GATE)

**Entry Point**: `phi_os/human_gate.py:approve` Flask endpoint

**Bypass Chain**:
```
PHI-OS Human Gate
  └─ approve(request_id, approver)
        ├─ Validation: State transition check
        ├─ NO LedgerAdapter call
        └─ Direct event insert: mocka_events.db.human_gate_events
            (NOT decision_ledger.jsonl)
```

**Bypasses**:
- ✅ LedgerAdapter (not in design)
- ✅ Decision Ledger (different storage)
- ❌ Human Gate authority (is the Human Gate)

**Creates Entry In**:
- ❌ data/decisions/decision_ledger.jsonl (not created)
- ✅ mocka_events.db.human_gate_events (event table)

**Gap**:
- Human Gate approvals go to mocka_events.db
- Decision Ledger records come from MCP/SealGov
- **No path from Human Gate → Decision Ledger**

**Risk Assessment**:
- PHI-OS Human Gate decisions are not recorded in Decision Ledger
- Disconnected from formal decision recording
- **Risk Level: MEDIUM** (architectural gap, not security issue)

---

## AUTHORITY PRESERVATION BY BYPASS PATH

| Bypass | Authority Check | Authority Stored | Verifiable |
|--------|---|---|---|
| MCP Direct | ❌ NONE | ⚠️ Client claim (unverified) | ❌ NO |
| SealGov Direct | ✅ GL7 (pre-execution) | ⚠️ "system:seal_governance_gate" | ⚠️ Via GL7 state |
| File I/O Direct | ❌ NONE | ❌ None | ❌ NO |
| Jarvis Test | ❌ NONE | ❌ Hardcoded "HUMAN_GATE" | ❌ NO |
| PHI-OS Native | ✅ State transition | ⚠️ Caller-provided approver | ❌ Unverified |

---

## UNIFIED DECISION LIFECYCLE GAP

```
Human Gate Decisions (PHI-OS)
  │
  ├─ Storage: mocka_events.db
  ├─ Authority: Approver name (unverified)
  └─ NOT in: data/decisions/decision_ledger.jsonl

MCP Decisions
  │
  ├─ Storage: data/decisions/decision_ledger.jsonl
  ├─ Authority: approved_by field (unverified)
  └─ Bypasses: Human Gate entirely

SealGov Decisions
  │
  ├─ Storage: data/decisions/decision_ledger.jsonl
  ├─ Authority: GL7 governance check + execution_id
  └─ Bypasses: Human Gate entirely

LedgerAdapter Path (Jarvis Test)
  │
  ├─ Storage: data/jarvis_ledger.jsonl
  ├─ Authority: None (hardcoded "HUMAN_GATE")
  └─ NOT in production

Result:
  ❌ No unified authority model
  ❌ No guaranteed path from Human Gate to Decision Ledger
  ❌ Three parallel systems (mocka_events, decision_ledger, jarvis_ledger)
```

---

## FINDINGS

### Bypass Summary

1. **MCP Direct**: OPEN (any client can write)
2. **SealGov Direct**: GATED (requires GL7 approval)
3. **File I/O**: PROTECTED (requires file access)
4. **Jarvis Test**: ISOLATED (test-only, not production)
5. **PHI-OS**: DISCONNECTED (doesn't create Decision Ledger entries)

### Authority Erosion

**Intended**:
- Human Gate authority → LedgerAdapter → Decision Ledger

**Actual**:
- MCP client authority → Decision Ledger (no Human Gate)
- GL7 authority → Decision Ledger (no Human Gate)
- Human Gate authority → mocka_events.db (not Decision Ledger)

### Risk Conclusion

**High-Risk Bypasses**:
- MCP Direct Write (any client can create decisions)

**Medium-Risk Bypasses**:
- SealGov Direct (GL7 required, but no re-verification)
- File I/O Direct (requires elevated access)
- PHI-OS Disconnection (authority exists, but not in Decision Ledger)

**Low-Risk Bypasses**:
- Jarvis Test Path (test-only, isolated)

---

**Report Status**: BYPASS ANALYSIS COMPLETE  
**Next Step**: TASK 6 - Decision Unit Preparation
