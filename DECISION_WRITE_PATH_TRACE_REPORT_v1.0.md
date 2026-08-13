# DECISION WRITE PATH TRACE REPORT v1.0

**Report Date**: 2026-08-13  
**Investigator**: KUROKO (Forensic Analysis)  
**Classification**: Phase 4 — Human Gate Review Support  
**Scope**: All possible paths that create Decision Ledger entries

---

## EXECUTIVE SUMMARY

Investigation identified **3 distinct write paths** to `data/decisions/decision_ledger.jsonl`:

1. **MCP Server Path** (Production) - `mocka_mcp_server.py:_append_decision()`
2. **SealGovernanceGate Path** (Production) - `governance/seal_governance_gate.py:_record_decision_unit()`
3. **LedgerAdapter Path** (Test/Design) - `runtime/jarvis/record/adapter/ledger_adapter.py:record()`

**Critical Finding**: Both production paths bypass LedgerStore and write directly to the file without duplicate detection.

---

## DECISION WRITE PATH ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                   Decision Origin                                │
│              (Human Gate / System / MCP Client)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                v                         v
         ┌──────────────┐        ┌─────────────────────┐
         │ MCP Request  │        │ SealGovernance      │
         │ Handler      │        │ Execute Request     │
         │ (MCP Server) │        │ (Governance Gate)   │
         └──────┬───────┘        └──────────┬──────────┘
                │                          │
                │                          │
         ┌──────v──────────────────────────v──────┐
         │                                         │
         │  Direct File Append (NO Validation)     │
         │  decision_ledger.jsonl.open("a")        │
         │                                         │
         └──────┬──────────────────────────────────┘
                │
         ┌──────v──────────────────┐
         │ Decision Ledger File    │
         │ (append-only JSONL)     │
         └─────────────────────────┘
         
NOTE: LedgerAdapter path (with duplicate prevention) is NOT shown
because it is not integrated into production write flows.
```

---

## PATH 1: MCP SERVER DECISION WRITE PATH

### Entry Point
- **Location**: `mocka_mcp_server.py:968-1029`
- **Handler**: `mocka_decision_write` MCP tool
- **Caller**: Any MCP client (e.g., Claude Code)
- **Authority Level**: MCP server processes all requests without authorization check

### Call Chain

```
MCP Client (e.g., Claude)
    │
    ├─ Call: mocka_decision_write(title, context, decision, ...)
    │
    v
mocka_mcp_server.py:handle_mcp_tool_call()
    │
    ├─ Parse input parameters (lines 969-982)
    │
    ├─ Validate schema (lines 976-985)
    │   └─ Check: title, context, decision, rationale, impact, approved_by present
    │   └─ Check: alternatives is non-empty array
    │   └─ Check: status in enum {Active, Superseded, Withdrawn}
    │
    ├─ Auto-generate decision_id if not provided (line 986)
    │   └─ Call: _next_decision_id() → DC_YYYYMMDD_NNN format
    │
    ├─ Build record dict (lines 988-1003)
    │   └─ Include all schema fields
    │   └─ Set approved_at to current UTC time
    │
    ├─ Write to ledger (line 1004)
    │   └─ Call: _append_decision(record)
    │
    ├─ Create companion event (lines 1008-1027)
    │   └─ POST to mocka_write_event for audit trail
    │   └─ (May fail silently if event service unavailable)
    │
    └─ Return success response (line 1029)
        └─ {"status": "ok", "decision_id": "...", "event_id": "..."}
```

### Validation Performed

| Validation | Check | Location |
|-----------|-------|----------|
| Field Presence | title/context/decision/rationale/impact/approved_by required | line 976 |
| Alternatives Array | Non-empty, each has option/rejected_reason | lines 978-982 |
| Status Enum | Must be Active/Superseded/Withdrawn | lines 983-985 |
| decision_id Format | AUTO-GENERATED as DC_YYYYMMDD_NNN | line 986 |
| **Duplicate Check** | **NONE** | **MISSING** |
| **Authority Check** | **NONE** | **MISSING** |

### Storage Mechanism

**Function**: `mocka_mcp_server.py:396-400` (`_append_decision`)

```python
def _append_decision(record):
    """decision_ledger.jsonlへ1行追記する（append-only、既存行は変更しない）。"""
    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DECISION_LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

**Properties**:
- Opens file in append mode (`"a"`)
- No read-before-write check
- No duplicate lookup
- **Unconditional append regardless of existing records**

### Duplicate Prevention Status

❌ **NOT IMPLEMENTED**

**Failure Scenario**:
```
Client A: mocka_decision_write(decision_id="DC_20260815_001", title="A", ...)
  └─ Writes: {"decision_id": "DC_20260815_001", "title": "A", ...}
  
Client B: mocka_decision_write(decision_id="DC_20260815_001", title="B", ...)
  └─ Writes: {"decision_id": "DC_20260815_001", "title": "B", ...}

Result:
  - File contains both entries
  - No rejection
  - No error
  - No audit trail of collision
  - Reader sees last entry as "most recent"
  - Earlier entry data is lost/obscured
```

### Authority Model

**Who can write**: Any MCP client with access to `mocka_decision_write` tool
- No approval gate before write
- No Human Gate check
- No permission verification
- Writes as "actor" determined by MCP caller

**Bypass Possibility**: ✅ TRIVIAL
- Send MCP request directly
- No intermediate validation
- No authority hierarchy
- Caller identity is external input only

---

## PATH 2: SEAL GOVERNANCE GATE PATH

### Entry Point
- **Location**: `governance/seal_governance_gate.py:64-100`
- **Handler**: `SealGovernanceGate.execute(message, scope, expected_max_changes)`
- **Caller**: Governance infrastructure (audit/seal endpoint)
- **Authority Level**: GL7 execution governance check (structural/execution_governance.py)

### Call Chain

```
Seal Request (from audit/seal endpoint)
    │
    ├─ Message: Seal operation description
    ├─ Scope: File scope or None
    └─ Expected Changes: Size constraint hint
    
    v
SealGovernanceGate.execute()
    │
    ├─ Generate execution_id (line 73)
    │   └─ Format: EXEC_YYYYMMDDHHMMS_XXXXXXXX
    │
    ├─ Capture change_start timestamp (line 74)
    │
    ├─ GL7 Governance Check (line 77)
    │   ├─ Call: self.governance.pre_execution_check(action)
    │   ├─ Returns: approval object with approved/reason/dry_run
    │   └─ If NOT approved → Record decision unit with aborts (line 86)
    │
    ├─ If Approved:
    │   │
    │   ├─ Execute seal script (line 89-90)
    │   │   └─ Call: self._run_seal_script(message)
    │   │   └─ Runs: scripts/ledger/anchor_update.py via subprocess
    │   │   └─ Captures: stdout, returncode
    │   │
    │   └─ Extract hashes from output (lines 121-123)
    │       ├─ COMMIT hash
    │       └─ SUMMARY_HASH
    │
    ├─ Record decision unit to ledger (line 99)
    │   └─ Call: self._record_decision_unit()
    │
    └─ Return result (line 100)
        └─ GateResult: approved/execution_id/reason/seal_stdout/returncode
```

### Validation Performed

| Validation | Check | Location |
|-----------|-------|----------|
| GL7 Governance Check | Pre-execution approval check | line 77 |
| Scope Validation | Via GL7 framework | line 77 |
| Change Limit Check | Via GL7 framework | line 77 |
| Seal Script Output | Parse for COMMIT/SUMMARY_HASH | lines 121-123 |
| **Duplicate Check** | **NONE** | **MISSING** |
| **Authority Re-verification** | **GL7 check only, not re-verified at write time** | **line 148** |

### Storage Mechanism

**Function**: `governance/seal_governance_gate.py:120-149` (`_record_decision_unit`)

```python
def _record_decision_unit(self, execution_id: str, change_start: str, result: GateResult) -> None:
    # ... build entry dict ...
    entry = {
        "decision_id": f"DC_{execution_id}",
        "title": "SealGovernanceGate seal request",
        "context": "Phase C-2 Governance Gate正式配置(TODO_411/412/413 Boundary対応)",
        "alternatives": [],
        "decision": "approved" if result.approved else "aborted",
        # ... more fields ...
        "execution_id": execution_id,
        "change_start": change_start,
        "change_done": datetime.now(timezone.utc).isoformat(),
        "artifact_hash": commit_hash,
        "seal_hash": summary_hash,
        "aborts": result.aborts,
    }
    self.decision_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with self.decision_ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

**Properties**:
- Generated `decision_id` from execution_id: `DC_EXEC_20260813103045_a1b2c3d4`
- Opens file in append mode (`"a"`)
- No read-before-write check
- No duplicate lookup
- Writes regardless of existing decision_id values

### Duplicate Prevention Status

❌ **NOT IMPLEMENTED**

**Failure Scenario**:
```
Seal Request A: SealGovernanceGate.execute("Seal A", ...)
  └─ GL7 Check passes
  └─ Seal script succeeds
  └─ Writes: {"decision_id": "DC_EXEC_20260813103045_a1b2c3d4", ...}

Network retry or re-submission:
Seal Request A (AGAIN): SealGovernanceGate.execute("Seal A", ...)
  └─ GL7 Check passes (again)
  └─ Seal script runs AGAIN (idempotent but writes again)
  └─ Writes: {"decision_id": "DC_EXEC_20260813103045_a1b2c3d4", ...}

Result:
  - Ledger contains duplicate decision records
  - Seal script may have been executed twice
  - No warning of duplication
  - Reader cannot distinguish from intentional supersede
```

### Authority Model

**Who can write**: Seal operation completed after GL7 approval
- GL7 governance check acts as authority gate
- But: GL7 check happens BEFORE decision_id is generated
- Gap: No re-verification at write time
- Gap: execution_id is guaranteed unique but decision_id construction is deterministic from execution_id (no collision risk from ID generation, but duplication risk from retried execution)

**Bypass Possibility**: ⚠️ REQUIRES GL7 BYPASS
- Must pass GL7 governance check
- Or must manipulate execution environment
- Direct API call would require governance approval
- But: Re-execution/retry behavior not protected

---

## PATH 3: LEDGERADAPTER PATH (Test/Design)

### Entry Point
- **Location**: `runtime/jarvis/record/adapter/ledger_adapter.py:5-14`
- **Handler**: `LedgerAdapter.record(decision_id, status)`
- **Caller**: `HumanGate` class (runtime/jarvis/gate/human_gate.py)
- **Authority Level**: HumanGate request (not integrated into production decision flow)

### Call Chain

```
HumanGate.approve(decision_id) or .reject(decision_id)
    │
    v
LedgerAdapter.record(decision_id, status)
    │
    ├─ Create DecisionRecord (lines 10-13)
    │   ├─ Pass: decision_id, status
    │   ├─ Default actor: "HUMAN_GATE"
    │   └─ Generate timestamp
    │
    ├─ Convert to dict (line 11)
    │   └─ Call: record.to_dict()
    │
    └─ Write via LedgerStore (line 14)
        └─ Call: self.store.save(record)
```

### Validation Performed

| Validation | Check | Location |
|-----------|-------|----------|
| decision_id Type | String, passed from caller | line 10 |
| status Value | String, passed from caller | line 10 |
| Actor Assignment | Default "HUMAN_GATE" | line 9 |
| Timestamp Generation | UTC datetime.now() | line 14 |
| **Duplicate Check** | **YES - Implemented in LedgerStore.save()** | **ledger_store.py:13-17** |

### Storage Mechanism

**Function**: `runtime/jarvis/record/persistence/ledger_store.py:10-22` (LedgerStore.save)

```python
def save(self, record):
    existing = self.load_all()
    
    if any(
        item.get("decision_id") == record.get("decision_id")
        for item in existing
    ):
        return record  # Silently skip write, return input record
    
    with self.path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    return record
```

**Properties**:
- ✅ Reads all existing records before write
- ✅ Checks for duplicate decision_id
- ✅ Appends only if unique
- ❌ Silently returns input if duplicate (fail-silent, not fail-closed)
- ✅ Opens in append mode only

### Duplicate Prevention Status

✅ **IMPLEMENTED (Silent Skip)**

**Behavior**:
```
Call A: ledger.record("DC_001", "WAITING")
  └─ load_all() finds 0 records
  └─ decision_id unique
  └─ Writes to file
  └─ Returns: {"decision_id": "DC_001", "status": "WAITING", "timestamp": "...", "actor": "HUMAN_GATE"}
  
Call B: ledger.record("DC_001", "APPROVED")
  └─ load_all() finds 1 record with decision_id "DC_001"
  └─ Duplicate detected
  └─ DOES NOT write
  └─ Returns: {"decision_id": "DC_001", "status": "APPROVED", "timestamp": "...", "actor": "HUMAN_GATE"}
  
Result:
  - File contains only Call A's record
  - Caller receives Call B's input back (silent failure)
  - No indication of rejection
  - No error thrown
```

### Authority Model

**Who can write**: Only HumanGate.approve() or .reject() callers
- HumanGate must be instantiated explicitly
- Not integrated into production decision flow
- Test-only in current usage

**Bypass Possibility**: ✅ TRIVIAL (but not used in production)
- Create own LedgerStore instance
- Write directly without using LedgerAdapter
- But: This path is not part of any production workflow

### Production Integration Status

❌ **NOT INTEGRATED INTO PRODUCTION**

**Usage**:
- `HumanGate` class exists at `runtime/jarvis/gate/human_gate.py`
- `JarvisEngine` instantiates HumanGate
- But: JarvisEngine is used in tests only
- Actual production decision recording: MCP server path (Path 1)

---

## CROSS-PATH COMPARISON MATRIX

| Property | MCP Server | SealGovernance | LedgerAdapter |
|----------|------------|----------------|---------------|
| **Write Mechanism** | Direct append | Direct append | LedgerStore.save() |
| **Duplicate Detection** | ❌ NO | ❌ NO | ✅ YES (silent) |
| **Duplicate Rejection** | N/A | N/A | ✅ (silent skip) |
| **Duplicate Logging** | ❌ NO | ❌ NO | ❌ NO |
| **Authority Check** | ❌ NO | ✅ GL7 | ❌ NO |
| **decision_id Generation** | Auto-generated | Deterministic from exec_id | Caller-provided |
| **Caller Identity Verification** | ❌ NO | ✅ GL7 | ❌ NO |
| **Production Use** | ✅ YES | ✅ YES | ❌ NO (tests only) |
| **Append-only File** | ✅ YES | ✅ YES | ✅ YES |
| **Historical Immutability** | ✅ YES | ✅ YES | ✅ YES |

---

## AUTHORITY BOUNDARIES

### MCP Path Authority
```
MCP Client
    │
    └─ (NO verification) ──> MCP Server decision_write handler
                                    │
                                    ├─ Schema validation
                                    └─ (NO authority check)
                                            │
                                            └─ WRITE to ledger
```

**Authority Gap**: Client-provided `approved_by` field is **not verified**. 
Any client can claim approval from "きむら博士" without verification.

### SealGovernance Path Authority
```
Seal Request
    │
    └─ GL7 Governance Check (approved/not approved)
                                    │
                        ┌───────────┴──────────┐
                        │                      │
                    (approved)             (not approved)
                        │                      │
                        v                      v
                 (Seal script runs)     (Record with aborts)
                        │                      │
                        └──────────┬───────────┘
                                   │
                        (Write decision_id without re-verification)
                                   │
                                   v
                            WRITE to ledger
```

**Authority Continuity Issue**: GL7 check happens before decision_id generation. 
If decision_id value changes or if write is retried, no re-verification occurs.

### LedgerAdapter Path Authority
```
HumanGate.approve/reject(decision_id)
    │
    ├─ (Authority: HumanGate object only)
    │
    └─ LedgerStore.save() with duplicate prevention
```

**Authority**: Limited to HumanGate class instantiation (not production-integrated).

---

## RISK SUMMARY BY WRITE PATH

### Path 1 (MCP): HIGH RISK
- No duplicate prevention
- No authority verification
- Client-provided approved_by is unverified
- Can create unlimited duplicate decision_ids

### Path 2 (SealGovernance): MEDIUM RISK
- GL7 check provides authority gate
- But: No re-verification at write time
- Re-execution/retry can create duplicates
- execution_id unique but decision_id deterministic (collision risk from policy)

### Path 3 (LedgerAdapter): LOW RISK
- Duplicate prevention implemented
- Not production-integrated (test-only)
- Silent failure mode (fail-silent, not fail-closed)

---

## LEGACY & MIGRATION ANALYSIS

### Legacy Paths
- ❌ No legacy decision_write paths found in codebase
- ❌ No migration scripts that create decision entries
- ✅ Only current 2 production paths identified

### Test Paths
- `tests/jarvis/test_ledger_store.py` - uses LedgerStore.save()
- `tests/jarvis/test_ledger_adapter.py` - uses LedgerAdapter.record()
- `tests/jarvis/test_decision_ledger.py` - uses JarvisLedger (in-memory, no persistence)
- No production tests create actual decision_ledger.jsonl entries

---

## FINDINGS

### Verified Facts

1. **Two Active Write Paths**: MCP server and SealGovernanceGate both write directly
2. **No Duplicate Prevention in Production**: Both bypass LedgerStore
3. **Silent Duplication Possible**: No checks, no rejections, no logging
4. **Unverified Authority**: MCP path allows unverified approved_by claims
5. **Append-Only Maintained**: Both paths use append mode only
6. **Historical Immutability**: Existing records cannot be modified
7. **LedgerStore Unused**: Duplicate prevention code exists but not integrated
8. **No Read-Before-Write**: Production paths do not verify decision_id uniqueness

### Boundary Crossings Identified

| Crossing | Path | Severity |
|----------|------|----------|
| No duplicate check | MCP | HIGH |
| No duplicate check | SealGov | MEDIUM |
| Unverified approved_by | MCP | HIGH |
| GL7 authority not re-verified | SealGov | MEDIUM |
| Silent duplication | MCP | HIGH |
| Design/Production gap | LedgerStore | HIGH |

---

## CONCLUSION

The Decision Ledger has **two distinct write paths**, neither with production-grade duplicate prevention. The designed protection (LedgerStore) exists but is not integrated into the actual decision-recording flows.

**Critical Gap**: Production can write duplicate decision_id entries with no detection, rejection, or audit trail.

**Next Analysis**: TASK 2 - LedgerStore Authority Boundary Analysis

---

**Report Status**: FORENSIC TRACE COMPLETE  
**Evidence Source**: Code analysis only (no execution)  
**Verification Method**: grep, read operations, architectural trace  
**Modifications Made**: NONE (read-only audit)
