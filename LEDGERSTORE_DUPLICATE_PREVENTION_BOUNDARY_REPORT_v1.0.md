# LEDGERSTORE DUPLICATE PREVENTION BOUNDARY REPORT v1.0

**Report Date**: 2026-08-13  
**Auditor**: KUROKO (READ-ONLY VERIFICATION)  
**Scope**: LedgerStore duplicate prevention mechanism  
**Classification**: Phase 4 — Human Gate Preparation Support  

---

## EXECUTIVE SUMMARY

The LedgerStore duplicate prevention mechanism is **DESIGN-ONLY**. The designed protection exists in code (`runtime/jarvis/record/persistence/ledger_store.py`) but is **NOT ACTIVELY USED** in the production decision-recording code path. 

**Critical Gap**: Production Decision Ledger writes via `mocka_mcp_server.py:_append_decision()` bypass the LedgerStore entirely and provide **NO duplicate prevention**.

---

## 1. DECISION_ID UNIQUENESS HANDLING

### 1.1 Designed Mechanism (LedgerStore)

**Location**: `runtime/jarvis/record/persistence/ledger_store.py:10-22`

```python
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
```

**Verification**:
- ✅ Unique constraint exists: `any()` check scans ALL existing records
- ✅ Matching criterion: exact `decision_id` string equality
- ❌ **Detection is implicit**: No exception, no error flag, no explicit rejection

### 1.2 Production Mechanism (MCP Server)

**Location**: `mocka_mcp_server.py:396-400` (`_append_decision`)

```python
def _append_decision(record):
    """decision_ledger.jsonlへ1行追記する（append-only、既存行は変更しない）。"""
    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DECISION_LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

**Verification**:
- ❌ **NO uniqueness check**
- ❌ **NO duplicate detection**
- ⚠️ Unconditional append regardless of existing decision_id values

**Impact**: Production can write duplicate decision_id entries to `data/decisions/decision_ledger.jsonl`

---

## 2. APPEND-ONLY INTEGRITY

### 2.1 Design Requirement

**Source**: `docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md:95-100`

```
不変条件: 既存レコードの上書き・削除禁止
Superseded/Withdrawn の場合は新レコードを追記し、
旧レコードの superseded_by を更新する
```

### 2.2 LedgerStore Enforcement

**Verification**:
- ✅ File opened in append mode only: `"a"` (read: line 19)
- ✅ No seek/truncate operations: **PASS**
- ✅ No UPDATE/DELETE patterns: **PASS**
- ✅ Historical records remain immutable: **PASS** (append-only file)

**Existing Decision Protection**:
- ✅ Once written, cannot be modified
- ✅ Immutability is enforced by OS file operations, not application logic

### 2.3 MCP Server Enforcement

**Verification**:
- ✅ File opened in append mode: `"a"` (read: line 399)
- ✅ Append-only preserved at storage layer: **PASS**
- ⚠️ **BUT**: Duplicate supersede records can be written without marking original as superseded
  
**Risk**: MCP server can write `{"decision_id": "DC_20260615_001", "status": "Active", ...}` followed by `{"decision_id": "DC_20260615_001", "status": "Superseded", ...}` WITHOUT updating the first record's `superseded_by` field to point to the second. This violates the schema requirement.

---

## 3. COLLISION DETECTION

### 3.1 LedgerStore Collision Handling

**Mechanism**: Inline within `save()` method

```python
if any(item.get("decision_id") == record.get("decision_id") for item in existing):
    return record  # Silently return without writing
```

**Verification**:
- ❌ **No explicit collision indicator**: Returns same record object as input
- ❌ **No state change**: Caller cannot distinguish success from collision
- ❌ **No logging/recording**: Collision event is silent
- ⚠️ **Caller confusion risk**: Function returns `record` in both success and collision cases

**Example failure scenario**:
```python
store = LedgerStore()
result1 = store.save({"decision_id": "DC_001", "status": "Active"})
result2 = store.save({"decision_id": "DC_001", "status": "Modified"})
# result2 == result2_input (collision occurred)
# But result1 == result2 is False, and caller sees no error
```

### 3.2 MCP Server Collision Handling

**Current State**: No collision detection exists

**Evidence**: `mocka_mcp_server.py:968-1004` (_decision_write implementation)
- No `_read_decisions()` check before `_append_decision(record)`
- No decision_id lookup
- Direct append without verification

**Production Risk**: Duplicate decision_id entries can be created silently

---

## 4. FAIL-CLOSED BEHAVIOR

### 4.1 LedgerStore Fail Mode

**Current Behavior**: FAIL-SILENT (NOT fail-closed)

```
Input: Duplicate decision_id
Expected (Fail-Closed): Raise exception, log error, explicitly reject
Actual (Fail-Silent): Return record silently, append is skipped
Caller View: "save() returned OK, status={...}"
Actual State: Record was NOT written to file
Discrepancy: Caller has no way to detect this occurred
```

**Specification Violation**:
- ❌ Does NOT fail explicitly when constraint violated
- ❌ Does NOT record rejection event
- ❌ Decision authority has no audit trail of rejected duplicate

### 4.2 MCP Server Fail Mode

**Current Behavior**: FAIL-PASS (NOT fail-closed, allows all writes)

```
Input: Duplicate decision_id
Expected (Fail-Closed): Reject with error, return 400/409 status
Actual: Append succeeds, returns {"status": "ok"}
Caller View: "decision_write succeeded"
Actual State: Duplicate entry created in ledger
```

---

## 5. EXISTING DECISION PROTECTION

### 5.1 LedgerStore Protection

**Mechanism**:
1. Append-only file prevents physical overwrite
2. `load_all()` reads entire file (line 24-32)
3. Lookup checks all existing records for duplicate decision_id

**Verification**:
- ✅ Existing records cannot be modified: Yes (append-only file)
- ✅ Existing records cannot be deleted: Yes (append-only file)
- ⚠️ **BUT**: Protection fails at conceptual level
  - If duplicate is submitted, it is silently rejected
  - Original decision_id's record is protected but authority has no notification
  - Schema requirement (superseded_by update) cannot be enforced

### 5.2 MCP Server Protection

**Current**: None at application layer

**Append-only file** protects existing bytes from overwrite, but:
- ❌ No uniqueness constraint at write time
- ❌ No notification mechanism
- ❌ No rejection logging

---

## 6. TEST COVERAGE ANALYSIS

### 6.1 LedgerStore Tests

**File**: `tests/jarvis/test_ledger_store.py`

```python
def test_ledger_store_save_load(tmp_path):
    # Creates & saves ONE record
    # Verifies save/load cycle
    # MISSING: Duplicate scenario test
```

**Finding**: 
- ❌ No `test_ledger_store_duplicate_rejection`
- ❌ No `test_ledger_store_collision_detection`
- ❌ No `test_ledger_store_duplicate_returns_unwritten_record`

### 6.2 Related Tests

**test_decision_state_transition.py**:
- Tests same decision_id appended twice **with different status values**
- Uses in-memory `JarvisLedger`, NOT `LedgerStore`
- JarvisLedger has NO duplicate prevention (allows all appends)

**Test Gap**: No test verifies that `LedgerStore.save()` actually prevents physical file writes for duplicates.

---

## 7. CODE PATH ANALYSIS

### 7.1 Production Decision Recording Flow

```
mocka_mcp_server.py:mocka_decision_write handler
    ↓
mocka_mcp_server.py:_append_decision(record)
    ↓
DECISION_LEDGER_PATH.open("a") → Direct file append
    ↓
No LedgerStore.save() call
No LedgerAdapter.record() call
No duplicate prevention
```

### 7.2 Test/Design Flow

```
test_ledger_adapter.py:test_ledger_adapter_record()
    ↓
LedgerAdapter.record(decision_id, status)
    ↓
LedgerStore.save(record)
    ↓
Duplicate check applied
```

**Critical Finding**: The code path with duplicate prevention (LedgerStore) is NOT used in production.

### 7.3 Usage Matrix

| Component | Uses LedgerStore | Uses MCP _append_decision | Production |
|-----------|------------------|--------------------------|------------|
| LedgerAdapter | ✅ YES | ❌ NO | ❌ NO (tests only) |
| HumanGate | ✅ uses LedgerAdapter | ❌ NO | ⚠️ Defined but unused |
| MCP Server | ❌ NO | ✅ YES | ✅ YES (production) |

---

## 8. SCHEMA COMPLIANCE AUDIT

### 8.1 DECISION_LEDGER_SCHEMA_v1 Requirements

| Requirement | LedgerStore | MCP Server | Status |
|-------------|-------------|-----------|--------|
| Append-only writes | ✅ Yes | ✅ Yes | **PASS** |
| No record deletion | ✅ Yes | ✅ Yes | **PASS** |
| No record overwrite | ✅ Yes | ✅ Yes | **PASS** |
| decision_id uniqueness | ✅ Checked | ❌ NOT checked | **FAIL (Production)** |
| Duplicate rejection | ✅ Silent skip | ❌ No check | **FAIL (Production)** |
| superseded_by updates for supersede | ⚠️ Not enforced | ❌ Not enforced | **WEAK** |
| Collision logging | ❌ None | ❌ None | **WEAK** |

---

## 9. BOUNDARY JUDGMENT

### 9.1 Verified Protections

1. **Append-only File Integrity**: ✅ **STRONG**
   - Both code paths use `"a"` (append) mode
   - OS-level protection prevents truncate/overwrite
   - Historical records remain immutable

2. **Physical Immutability**: ✅ **STRONG**
   - Existing records cannot be modified in place
   - Decision data integrity at storage layer: **PASS**

### 9.2 Remaining Risks

1. **Production Duplicate Prevention**: ❌ **MISSING**
   - MCP server allows duplicate decision_id writes
   - No application-layer check before append
   - Duplicate entries can exist in ledger
   - **Risk Level**: HIGH
   - **Boundary**: Crossed (production can violate uniqueness requirement)

2. **Collision Recording**: ❌ **MISSING**
   - No audit trail when duplicate is attempted
   - No event recorded in mocka event system
   - Decision authority unaware of rejection
   - **Risk Level**: MEDIUM
   - **Boundary**: Crossed (silent failure violates CLAUDE.md recording requirements)

3. **Supersede Integrity**: ⚠️ **WEAK**
   - Schema requires `superseded_by` field update on old record
   - Both code paths write new record but don't update existing
   - Requires reader-side logic to find latest version
   - **Risk Level**: MEDIUM
   - **Boundary**: Crossed (schema intention not enforced)

4. **Fail-Closed Semantics**: ❌ **MISSING**
   - LedgerStore silently skips duplicates (fail-silent)
   - MCP server has no check (fail-open)
   - Neither enforces explicit rejection
   - **Risk Level**: MEDIUM
   - **Boundary**: Crossed (violates safety principle of explicit rejection)

### 9.3 Human Gate Relevance

**For Human Gate Review**:

1. **Design vs. Implementation Gap**: 
   - Designed protection (LedgerStore) does NOT run in production
   - Production path (MCP _append_decision) has NO protection
   - Review required: Accept design debt OR implement production protection

2. **Two-Path Problem**:
   - If decision recording should use LedgerStore: Refactor MCP server to call it
   - If direct append is intended: Remove LedgerStore code, document as intentional open ledger

3. **Boundary Crossing Events**:
   - Event 1: Duplicate decision_id submitted → No collision detection → Ledger contains duplicates
   - Event 2: Schema requires `superseded_by` update → Not enforced → Reader confusion
   - Event 3: Rejection occurs (LedgerStore silent skip) → Not recorded → No audit trail

---

## 10. EVIDENCE REFERENCE

### Code Artifacts
- `runtime/jarvis/record/persistence/ledger_store.py` (lines 10-22)
- `mocka_mcp_server.py` (lines 364-400, 968-1029)
- `docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md` (lines 95-100)

### Test Artifacts
- `tests/jarvis/test_ledger_store.py` (single record test, no duplicate test)
- `tests/jarvis/test_ledger_adapter.py` (adapter-level test, no duplicate test)
- `tests/jarvis/test_decision_state_transition.py` (state test, uses JarvisLedger, not LedgerStore)

### Specification References
- `docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md` (schema definition)
- `docs/mocka3/EVENT_FOUNDATION_v1.md` (append-only principles)
- `.claude/CLAUDE.md` (recording requirements: TODO_354, TODO_361)

---

## 11. RECOMMENDATIONS FOR HUMAN GATE

### Boundary Status: **CROSSED**

**Crossing Definition Met**:
- ❌ Uniqueness is NOT enforced in production code
- ❌ Collision is NOT rejected or logged
- ❌ Silent failures occur without audit trail
- ✅ Append-only property is maintained (physical level)
- ✅ Existing records remain protected (file layer)

### Required Decision

**Option A: Design Acceptance (Status Quo)**
- Accept that decision_id uniqueness is advisory, not enforced
- Update DECISION_LEDGER_SCHEMA_v1.md to document this
- Require reader-side deduplication logic
- Document MCP server as canonical path

**Option B: Production Implementation (Strengthen)**
- Refactor `mocka_mcp_server.py:_append_decision()` to call `LedgerStore.save()`
- Implement explicit rejection for duplicates (raise exception, return 409)
- Add duplicate detection test case
- Update mocka event to record collision attempts

**Option C: Hybrid (Split by Purpose)**
- Keep LedgerStore for formal decisions (via LedgerAdapter)
- Keep MCP direct append for draft/working decisions (document as intent)
- Separate decision_ledger into two files by confidence level

---

## AUDIT CONCLUSION

**Phase 4 Gate Status**: READY FOR HUMAN GATE REVIEW

The LedgerStore duplicate prevention boundary is **DEFINED but NOT ENFORCED** in the production code path. The system's append-only property is verified and strong, but the uniqueness constraint (a schema requirement) relies on design-only code (LedgerStore) that is not integrated into the production MCP decision-writing path.

**Clearance for Human Gate**: Boundary crossing is **CONFIRMED AND DOCUMENTED**. Human judgment required on acceptance vs. enforcement strategy.

---

**Report End**  
**Verification Mode**: READ-ONLY AUDIT (No modifications made)  
**Next Action**: Awaiting Human Gate decision on boundary acceptance vs. enforcement
