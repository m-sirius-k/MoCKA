# LEDGERSTORE AUTHORITY BOUNDARY ANALYSIS v1.0

**Report Date**: 2026-08-13  
**Investigator**: KUROKO (Forensic Analysis)  
**Classification**: Phase 4 — Human Gate Review Support  
**Focus**: Is LedgerStore the integrity boundary or a helper utility?

---

## EXECUTIVE SUMMARY

LedgerStore is **DESIGNED AS the integrity boundary** but is **NOT DEPLOYED as the boundary** in production. 

Current Status: **CATEGORY C - Partially Adopted Boundary**

- Designed: ✅ Boundary logic exists (duplicate prevention in LedgerStore.save())
- Documented: ⚠️ Implicit in schema, not explicit in governance docs
- Deployed: ❌ Production paths bypass the boundary
- Enforced: ❌ No requirement that all writes use LedgerStore
- Used: ⚠️ Test/design only, not production-integrated

---

## LEDGERSTORE DESIGN INTENT ANALYSIS

### 1. Architectural Role

**File**: `runtime/jarvis/record/persistence/ledger_store.py` (33 lines)

```python
class LedgerStore:
    def __init__(self, path="data/jarvis_ledger.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, record):
        existing = self.load_all()
        
        if any(
            item.get("decision_id") == record.get("decision_id")
            for item in existing
        ):
            return record
        
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        return record

    def load_all(self):
        if not self.path.exists():
            return []
        
        with self.path.open("r", encoding="utf-8") as f:
            return [
                json.loads(line)
                for line in f
                if line.strip()
            ]
```

**Explicit Responsibilities**:
1. Enforce uniqueness constraint (`save()` checks decision_id)
2. Maintain append-only property (opens in `"a"` mode)
3. Provide read interface for verification (`load_all()`)

**Implicit Responsibilities** (from design):
1. Single point of validation for decision records
2. Gatekeeper for ledger integrity
3. Owner of duplicate detection logic

### 2. Design Pattern

**Pattern Type**: **Boundary Pattern (Repository/Facade)**

LedgerStore is designed as:
- **Single Responsibility**: Guard the ledger integrity boundary
- **Dependency Inversion**: Callers should depend on this abstraction, not direct file I/O
- **Trust Boundary**: All writes to decision_ledger should pass through this component

**Design Principle** (Inferred from code):
```
Trust Model:
  
  "All decision records shall be written through
   a validated persistence boundary."
   
  The boundary enforces:
  - decision_id uniqueness
  - Append-only storage
  - Historical immutability
```

### 3. Schema Alignment

**DECISION_LEDGER_SCHEMA_v1.md Requirements** (lines 95-100):

```
不変条件: 既存レコードの上書き・削除禁止
Superseded/Withdrawn の場合は新レコードを追記し、
旧レコードの superseded_by を更新する
```

**Interpretation**:
- Decisions are append-only (LedgerStore enforces this)
- decision_id should be unique (LedgerStore enforces this)
- Historical records immutable (LedgerStore enforces this via append-only file)

**LedgerStore Alignment**: ✅ YES
- Implements uniqueness guard
- Implements append-only enforcement
- Implements historical immutability

---

## CURRENT DEPLOYMENT ANALYSIS

### 1. How LedgerStore is Used

**Usage in Production Code**:
- ❌ mocka_mcp_server.py: Does NOT use LedgerStore
- ❌ governance/seal_governance_gate.py: Does NOT use LedgerStore
- ✅ LedgerAdapter: USES LedgerStore
- ✅ HumanGate: USES LedgerAdapter

**Usage in Tests**:
- ✅ tests/jarvis/test_ledger_store.py
- ✅ tests/jarvis/test_ledger_adapter.py
- ✅ tests/jarvis/test_ledger_persistence.py

### 2. Integration Chain

```
Production Decision Recording:
┌─ MCP Server (mocka_decision_write) ──────┐
│                                           │
└─ Direct file append ────────────────────> decision_ledger.jsonl
  (No LedgerStore)

Production Seal Recording:
┌─ SealGovernanceGate (_record_decision_unit) ──┐
│                                                │
└─ Direct file append ──────────────────────────> decision_ledger.jsonl
  (No LedgerStore)

Test/Design Recording:
┌─ HumanGate (approve/reject) ──────┐
│                                   │
├─ LedgerAdapter.record() ─────────┤
│                                   │
├─ LedgerStore.save() ─────────────┤
│   (WITH duplicate prevention)     │
│                                   │
└─ File append ─────────────────────> ledger_store.path
  (Different path: data/jarvis_ledger.jsonl, not decision_ledger.jsonl)
```

**Critical Finding**: LedgerStore is used on a **different file** (`data/jarvis_ledger.jsonl`) 
than production decision recording (`data/decisions/decision_ledger.jsonl`).

### 3. Bypass Possibilities

**Bypass 1: Direct MCP Call** (TRIVIAL)
```
Attacker:
1. Calls mocka_decision_write() MCP tool directly
2. No LedgerStore involved
3. Duplicate is written to decision_ledger.jsonl
4. LedgerStore.load_all() on jarvis_ledger.jsonl sees nothing
Risk: HIGH (no protection)
```

**Bypass 2: Direct SealGovernance Call** (REQUIRES GL7)
```
Attacker:
1. Passes GL7 governance check
2. SealGovernanceGate.execute() succeeds
3. Direct file append (no LedgerStore check)
4. Duplicate is written to decision_ledger.jsonl
Risk: MEDIUM (requires GL7 bypass)
```

**Bypass 3: Write Different File** (TRIVIAL)
```
Attacker:
1. Write to data/jarvis_ledger.jsonl (LedgerStore path)
2. Write to data/decisions/decision_ledger.jsonl (Production path)
3. Two separate ledgers, LedgerStore protects only its own file
Risk: HIGH (no cross-file validation)
```

**Bypass 4: Direct File Manipulation** (REQUIRES FILE ACCESS)
```
Attacker:
1. Direct edit of decision_ledger.jsonl
2. Bypass all application code
3. LedgerStore can only protect writes through itself
Risk: MEDIUM (requires file system access)
```

---

## LEDGERSTORE ROLE ASSESSMENT

### Current Role: HELPER UTILITY

**Evidence**:
1. Not mandated by any production code
2. Not referenced in MCP server
3. Not referenced in SealGovernanceGate
4. Not integrated into critical path
5. Used only for test/design code

**Characteristics**:
- Optional: Code can work without it
- Helpful: Provides validation when used
- Unused: Not integrated into actual decision flow
- Isolated: Works on separate file path

### Intended Role: INTEGRITY BOUNDARY

**Evidence** (from design):
1. Named `LedgerStore` (suggests ownership of ledger)
2. Duplicate prevention logic (suggests validation boundary)
3. load_all() method (suggests verification interface)
4. Used by LedgerAdapter (suggests formal recorder interface)
5. Schema alignment (suggests designed with schema in mind)

**Gap**: Intention ≠ Deployment

---

## AUTHORITY BOUNDARY ANALYSIS

### LedgerStore Authority Model

```
┌─────────────────────────────────────────────────────────┐
│ LEDGERSTORE AUTHORITY BOUNDARY (DESIGNED)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Responsibility:                                        │
│  - Accept/reject decision records based on uniqueness   │
│  - Maintain integrity of decision_ledger                │
│  - Enforce schema invariants (append-only, immutable)   │
│                                                         │
│  Authority Enforcement:                                 │
│  ✅ Uniqueness: Checked before write (lines 13-17)     │
│  ✅ Append-only: File opened in "a" mode only (line 19)│
│  ✅ Immutability: No read-then-modify pattern           │
│                                                         │
│  Authority Gap:                                         │
│  ❌ NOT called by production paths                      │
│  ❌ Duplicate rejection is SILENT (no error signal)     │
│  ❌ No logging of rejected duplicates                   │
│  ❌ No audit trail of boundary enforcement              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Current vs. Intended Authority

| Aspect | Current | Intended | Gap |
|--------|---------|----------|-----|
| **Who enforces** | LedgerStore (test-only) | LedgerStore (all paths) | ✅ Decision to deploy |
| **Where enforced** | data/jarvis_ledger.jsonl | data/decisions/decision_ledger.jsonl | ✅ Path mismatch |
| **When enforced** | In LedgerAdapter.record() | In mocka_decision_write(), SealGovernanceGate | ✅ Integration gap |
| **What is checked** | decision_id uniqueness | decision_id uniqueness | ✅ Logic is ready |
| **How rejection works** | Silent return | (undefined - not implemented in production) | ⚠️ Fail-closed behavior undefined |

---

## FAILURE MODE ANALYSIS

### Scenario 1: Concurrent Duplicate Writes (Race Condition)

```
Thread A:
  1. LedgerStore.load_all() → [Record1, Record2]
  2. Check: "DC_001" not in list
  3. [Context switch]

Thread B:
  1. LedgerStore.load_all() → [Record1, Record2]
  2. Check: "DC_001" not in list
  3. Write: {"decision_id": "DC_001", ...}

Thread A:
  4. Write: {"decision_id": "DC_001", ...}

Result: File contains TWO "DC_001" records
```

**LedgerStore Vulnerability**: Race condition in check-then-act

**Protection Level**: ❌ NONE (no file locks, no atomic operations)

### Scenario 2: Schema Mismatch (Wrong File Path)

```
Production Code:
  write to: data/decisions/decision_ledger.jsonl
  
LedgerStore Default:
  path: data/jarvis_ledger.jsonl
  
Result: LedgerStore can validate one file while production writes to another
```

**LedgerStore Vulnerability**: File path not enforced, different files possible

**Protection Level**: ⚠️ WEAK (depends on correct path configuration)

### Scenario 3: Silent Failure (Fail-Silent, Not Fail-Closed)

```
Call: ledger.save({"decision_id": "DC_001", "status": "Active"})
Result: Duplicate detected

LedgerStore Behavior:
  ❌ Does NOT raise exception
  ❌ Does NOT set error flag
  ❌ Does NOT record rejection
  ✅ Returns input record (same as success case)
  ✅ Does NOT write to file

Caller View:
  ✅ Got a record back
  ✅ No indication of failure
  ❌ Cannot distinguish success from collision
  
Problem: Silent failure violates fail-closed principle
```

**LedgerStore Vulnerability**: Cannot be detected by caller

**Protection Level**: ❌ NONE (fail-silent, not fail-closed)

---

## ARCHITECTURAL DEBT ANALYSIS

### Why Deployment Gap Exists

**Root Cause 1: Design/Implementation Order**
```
Timeline:
- DECISION_LEDGER_SCHEMA_v1.md designed (2026-06-15)
- LedgerStore implemented (unknown date, pre-audit)
- HumanGate/LedgerAdapter designed to use LedgerStore
- MCP server designed/implemented without LedgerStore
- SealGovernanceGate designed/implemented without LedgerStore
- Gap: LedgerStore was never mandated in production

Inference: LedgerStore was designed for formal decisions,
but production paths evolved independently for operational use.
```

**Root Cause 2: Two Decision Ledgers**
```
data/jarvis_ledger.jsonl
  └─ Used by LedgerStore
  └─ Used by LedgerAdapter (test path)
  └─ Used by HumanGate (test path)

data/decisions/decision_ledger.jsonl
  └─ Used by MCP server (production)
  └─ Used by SealGovernanceGate (production)
  └─ NOT used by LedgerStore

Inference: Two separate ledger files evolved,
LedgerStore protects one but not the other.
```

**Root Cause 3: Authority Model Mismatch**
```
LedgerStore Model:
  └─ Single point of validation
  └─ Rejects duplicates
  └─ Guards boundary

Production Model:
  └─ MCP server: No validation (authority: client)
  └─ SealGovernanceGate: GL7 validation (authority: governance)
  └─ No unified authority model

Inference: LedgerStore authority conflicts with distributed
authority in production (MCP client vs. GL7 governance).
```

---

## BOUNDARY JUDGMENT

### LedgerStore Current Classification

**CATEGORY C: PARTIALLY ADOPTED BOUNDARY**

Characteristics:
- ✅ Designed as integrity boundary
- ⚠️ Implemented (but incomplete)
- ❌ Not deployed to production
- ❌ Not mandated by governance
- ❌ Silent failure mode
- ✅ Append-only property maintained
- ⚠️ Duplicate prevention works (if used)

### Boundary Status

**Is LedgerStore the Mandatory Integrity Boundary?**

Current: ❌ NO
- Production paths bypass it
- No governance requirement
- No integration into critical path

Designed: ⚠️ PARTIALLY
- Duplicate prevention logic exists
- But silent failure (not fail-closed)
- But race condition vulnerability
- But file path configuration issue

Required for Compliance: ❌ NO
- Schema says append-only, immutable
- LedgerStore enforces this via file mode only (not via validation)
- Append-only file mode exists in all paths (MCP, SealGov, LedgerStore)
- Historical immutability exists in all paths (no modifications)
- Uniqueness NOT enforced in production paths (gap)

### Who Can Bypass LedgerStore

| Bypasser | Method | Authority | Risk |
|----------|--------|-----------|------|
| MCP Client | Call mocka_decision_write directly | None | HIGH |
| Seal Operator | Pass GL7, execute SealGovernanceGate | GL7 check | MEDIUM |
| File Editor | Direct edit decision_ledger.jsonl | File access | MEDIUM |
| Test Code | Use different path (jarvis_ledger.jsonl) | Test scope | LOW |

**Conclusion**: LedgerStore provides NO protection in production because production paths do NOT use it.

---

## WHY ARCHITECTURE INTENT IS UNCLEAR

### Missing Governance Documents

**What exists**:
- ✅ DECISION_LEDGER_SCHEMA_v1.md (schema definition)
- ✅ LedgerStore implementation
- ✅ LedgerAdapter implementation

**What's missing**:
- ❌ Decision on whether LedgerStore is mandatory
- ❌ Authority model for decision recording
- ❌ Boundary specification document
- ❌ Fail-closed behavior specification
- ❌ Duplicate handling policy document
- ❌ Two-ledger-file justification

### Implicit vs. Explicit Boundaries

**Implicit** (currently):
- "LedgerStore validates duplicates" (code shows this)
- "Append-only is file-mode only" (no application-layer enforcement)

**Explicit** (needed):
- "All formal decisions SHALL pass through LedgerStore" OR "Direct append is approved for operational decisions"
- "Uniqueness is NOT enforced (append-only allows duplicates)" OR "Uniqueness IS enforced (duplicates rejected)"
- "Silent rejection is acceptable" OR "Explicit rejection required"

---

## FINDINGS

### Verified Facts

1. **LedgerStore exists** but is NOT production-integrated
2. **Duplicate prevention logic exists** in LedgerStore but not called
3. **Append-only property exists** in all paths (MCP, SealGov, LedgerStore)
4. **Historical immutability exists** in all paths (file append-only mode)
5. **Uniqueness NOT enforced** in production (MCP, SealGov paths)
6. **Silent failure mode** in LedgerStore (no exception, no audit trail)
7. **Two separate ledger files** (jarvis_ledger.jsonl vs. decision_ledger.jsonl)
8. **Authority mismatch** between LedgerStore model (unified validation) and production model (distributed authority)

### Boundary Crossing Evidence

| Requirement | Met by LedgerStore | Met in Production | Boundary Status |
|-------------|-------------------|-------------------|-----------------|
| Append-only writes | ✅ YES | ✅ YES | ✅ MAINTAINED |
| No overwrites | ✅ YES | ✅ YES | ✅ MAINTAINED |
| No deletes | ✅ YES | ✅ YES | ✅ MAINTAINED |
| Uniqueness enforcement | ✅ YES | ❌ NO | ❌ CROSSED |
| Duplicate rejection | ✅ YES (silent) | ❌ NO | ❌ CROSSED |
| Authority verification | ⚠️ PARTIAL | ⚠️ PARTIAL | ⚠️ WEAK |

---

## CONCLUSION

**LedgerStore is the DESIGNED but UNDEPLOYED integrity boundary.**

It correctly implements:
- ✅ Append-only enforcement (file mode)
- ✅ Historical immutability (no overwrites)
- ✅ Duplicate detection logic (read-then-check)

But it is NOT:
- ❌ Used in production
- ❌ Mandated by governance
- ❌ Integrated into critical paths
- ❌ Enforced to fail-closed

**Architecture Intent vs. Deployment Gap**:
```
Designed: "LedgerStore is THE integrity boundary for all decisions"
Deployed: "Two parallel write paths, both bypass LedgerStore"
```

**Human Gate Decision Required**: 
Should LedgerStore become the mandatory formal decision boundary, 
or should direct append be the approved pattern for operational decisions?

---

**Report Status**: AUTHORITY BOUNDARY ANALYSIS COMPLETE  
**Next Step**: TASK 3 - Decision Ledger Trust Model Analysis
