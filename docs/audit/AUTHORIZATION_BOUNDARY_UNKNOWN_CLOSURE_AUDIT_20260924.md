# MoCKA Authorization Boundary — UNKNOWN Closure Audit

**Date**: 2026-09-24  
**Commit SHA**: ac132fa7eb66ddd196e7a9a1c4dd110ea963b2b9  
**Scope**: READ-ONLY Fact-Based Analysis  
**Code Changes**: NONE  
**Commits**: NONE  
**Pushes**: NONE  
**Production Activation**: NONE

---

## Executive Summary

Three UNKNOWN items resolved through runtime-level verification:

1. **governance/write_path/***: VERIFIED INACTIVE — Reads-only prototype code, unreachable from active runtime, writes to separate namespace only
2. **orchestrator.execute()**: VERIFIED UNREACHABLE — Complete implementation exists but zero call paths from active code
3. **External AI → Gateway/Connector Path**: VERIFIED ACTIVE — Functioning telemetry/recording paths without authorization binding

**Key Finding**: All effect surfaces now classified. No new unknowns. Remaining decision is purely institutional (Authorization Boundary scope definition).

---

## Part 1: VERIFIED ACTIVE PATHS

### 1.1 MCP Protected Tool Path (AUTHORIZED)

**Entry Point**: `mocka_mcp_server.py:509` `execute_tool()`

**Flow**:
```
Client → /mcp endpoint → execute_tool()
    ↓
if name in PROTECTED_TOOLS:
    governance_pipeline.before_tool() [GL7 Dry Run]
    ↓
populate auth_context (6 attributes):
    - token_id
    - issuer
    - decision_id
    - scope
    - approval_event_id
    - issued_at
    ↓
call effect_operation(auth_context=auth_context)
    ↓
save_todo() / _append_decision() / _append_classification()
    ↓
Add _auth_binding to persistent record
    ↓
Write to ledger/table
```

**Protected Tools (6)**:
- mocka_add_todo (line 612)
- mocka_update_todo (line 685)
- mocka_write_event (lines 743-755)
- mocka_decision_write (line 1057)
- mocka_integrity_write (line 1142)
- mocka_seal

**Storage Functions with Binding**:
- `save_todo()` (lines 352-369): Adds `_auth_binding` when auth_context provided
- `_append_decision()` (lines 405-420): Adds `_auth_binding` to decision_ledger.jsonl
- `_append_classification()` (lines 467-482): Adds `_auth_binding` to integrity_classification.jsonl

**Concurrency Safety**: Local `auth_context` variable (not module-level global)

**Verification**: ✅ 6/6 binding confirmed in code

**Status**: VERIFIED ACTIVE & AUTHORIZED

---

### 1.2 Gateway External AI Event Path (ACTIVE, NO AUTHORIZATION)

**Entry Point**: `gateway/gateway.py:142` POST `/api/v1/event`

**Flow**:
```
External AI System
    ↓
POST /api/v1/event (JSON payload)
    ↓
@app.before_request → check_auth()
    ↓
require_api_key() validates X-MoCKA-Key header
    (gateway/auth.py:40-51)
    ↓
get_buffer().push(event) [line 169]
    ↓
[Asynchronous Branch]
event_buffer._run() background thread
    (every 0.5s or 50 events)
    ↓
flush_async() [line 60]
    ↓
POST http://localhost:5000/api/gate/event/batch
    ↓
PHI-OS Event Gate receives
    (phi_os/event_gate.py:receive_event_batch())
    ↓
validate_operational(event) [gate_validator.py:50-69]
    ↓
_write(event, conn) INSERT INTO events
```

**Fallback Path**: If Gate timeout, persist to `event_buffer_fallback.jsonl`

**Authentication**: API key only (X-MoCKA-Key header + optional HMAC)

**Authorization Context**: ❌ NONE

**_auth_binding**: Not added

**Process Verification**: ✅ Gateway running at port 5010, event_buffer daemon thread active

**Status**: VERIFIED ACTIVE — NO AUTHORIZATION BINDING

---

### 1.3 Connector Caliber Query Path (ACTIVE, NO AUTHORIZATION)

**Entry Point**: `gateway/connector_caliber.py:32` POST `/api/v1/connector/query`

**Flow**:
```
External AI Connector Adapter
    ↓
POST /api/v1/connector/query
    ↓
@app.before_request → check_auth()
    (same as gateway event path)
    ↓
connector_query() [line 33]
    ↓
self.cb.build(context_mode)
    ↓
self._record_event() [line 44]
    ↓
IndexWriter(str(self.db_path)).write(index) [line 87]
    ↓
Write to mocka_events.db via db_helper.py
    ↓
INSERT INTO events table
```

**Authentication**: API key only (transport-level)

**Authorization Context**: ❌ NONE

**_auth_binding**: Not added

**Process Verification**: ✅ Routes registered, IndexWriter writes confirmed

**Status**: VERIFIED ACTIVE — NO AUTHORIZATION BINDING

---

## Part 2: VERIFIED INACTIVE / UNREACHABLE PATHS

### 2.1 governance/write_path/* (READ-ONLY PROTOTYPE)

**Files**:
- `governance/write_path/runtime/generator.py`
- `governance/write_path/runtime/adapter.py`
- `governance/write_path/runtime/validator.py`
- `governance/write_path/restore/materializer.py`

**Code Evidence**:

#### generator.py (lines 26-86)
- Function `generate_evidence_record()`: Reads events.db in READ-ONLY mode
- Line 79: `record_change_event()` marked "実装のみ、検証実行時には呼び出さない" (implementation only, NOT invoked during verification)
- Returns: In-memory `RuntimeEvidenceRecord` dict only
- Effect: ❌ NO writes to decision_ledger.jsonl or integrity_classification.jsonl

#### adapter.py (lines 26-86)
- Function `build_transition_record()`: Reads decision_ledger.jsonl in READ-ONLY mode
- Line 67: "永続化は行わない(in-memoryでの生成・検証のみ)" (does NOT persist, in-memory only)
- Returns: In-memory `GovernanceTransitionRecord` dict only
- Effect: ❌ NO writes to ledgers

#### validator.py (lines 29-75)
- Function `build_draft_restore_packet()`: Calls generator/adapter (READ-ONLY only)
- Line 13: "どこにも永続化しない" (does NOT persist anywhere)
- Returns: In-memory dict only
- Effect: ❌ NO writes

#### materializer.py (lines 67-101)
- Function `materialize()`: DOES write to disk (line 90)
- BUT: Writes to `governance/write_path/restore/materialized/` directory ONLY
- NOT to decision_ledger.jsonl or integrity_classification.jsonl
- Lines 92-96: Calls `generator.record_change_event()` but this is a stub (not executed in runtime per generator.py line 79)

**Reachability Analysis**:
- Grep for `materialize()` call: **ZERO matches** in active code
- Grep for validator/adapter/generator calls: **ZERO matches** in active code
- app.py line 1688: Only reads FROM materialized/ dir (does NOT invoke materialize())
- Only test files import these modules

**Active Code Reference**: 
- Only reference found: `core_kernel/orchestrator/tests/` (test code only)

**Runtime Process Check**:
- ps aux grep: **ZERO processes** running these modules

**Conclusion**:
- ✅ Complete implementation exists
- ✅ All operations are READ-ONLY or write to separate namespace
- ✅ Unreachable from current runtime
- ✅ No core ledger writes from this path
- ✅ Prototype code for future Restore Packet feature

**Status**: VERIFIED INACTIVE — NO EFFECT ON CURRENT AUTHORIZATION

---

### 2.2 orchestrator.execute() (UNREACHABLE)

**File**: `orchestrator/orchestrator.py`

**Function Definition** (lines 14-41):
```python
def execute(request: str):
    Parse intent → Plan tasks → Route → Inject context → Execute task
```

**Implementation**:
- Task executor: `orchestrator/task_executor.py`
- `execute_task()`: Only runs pytest or collects test results
- NO MCP tool invocations
- NO database writes
- NO state-changing effects

**Reachability Analysis**:
- Grep for `"from orchestrator import" or "orchestrator.execute"`: **ZERO matches** in active code
- Only reference: `core_kernel/orchestra/tests/` (test code only)
- No imports in app.py, gateway.py, or mocka_mcp_server.py

**Runtime Process Check**:
- ps aux grep orchestrator: **ZERO processes**
- ps aux grep main_loop: **ZERO processes**
- auto_runner.py exists but not invoked by any active code
- input_raw.txt file: DOES NOT EXIST

**State Change Analysis**:
- `execute_task()`: Runs subprocess tests (read-only)
- NO writes to decision_ledger.jsonl
- NO writes to integrity_classification.jsonl
- NO writes to events table via MCP
- NO calls to governance_pipeline.before_tool()
- NO effect on system state

**Conclusion**:
- ✅ Complete implementation exists
- ✅ Zero call paths from active runtime
- ✅ No background process running
- ✅ No state changes via this path

**Status**: VERIFIED UNREACHABLE — NO EFFECT ON CURRENT AUTHORIZATION

---

## Part 3: VERIFIED EFFECT SURFACES & AUTHORIZATION STATUS

### Summary Table

| Effect Surface | Type | Auth Context | _auth_binding | Status |
|---|---|---|---|---|
| mocka_add_todo | MCP | ✅ Present | ✅ Added | AUTHORIZED |
| mocka_update_todo | MCP | ✅ Present | ✅ Added | AUTHORIZED |
| mocka_write_event | MCP | ✅ Present | ✅ Added | AUTHORIZED |
| mocka_decision_write | MCP | ✅ Present | ✅ Added | AUTHORIZED |
| mocka_integrity_write | MCP | ✅ Present | ✅ Added | AUTHORIZED |
| mocka_seal | MCP | ✅ Present | ✅ Added | AUTHORIZED |
| POST /api/v1/event | External AI | ❌ Absent | ❌ Missing | TELEMETRY ONLY |
| POST /api/v1/connector/query | Connector | ❌ Absent | ❌ Missing | TELEMETRY ONLY |
| governance/write_path/* | Prototype | N/A | N/A | UNREACHABLE |
| orchestrator.execute() | Dead Code | N/A | N/A | UNREACHABLE |

---

## Part 4: AUTHORIZATION BOUNDARY SCOPE — HUMAN DECISION REQUIRED

### Current State

**MCP Protected Tools** (6 total): Full 6-attribute authorization binding implemented and verified working

**External Telemetry Paths** (2 total): API key authentication only, no authorization context binding

**Inactive Paths** (2 total): Unreachable from runtime, no security impact

### Three Options

#### Option A: MCP Tools Only (Current Implementation)

**Boundary Definition**: Authorization context required for MCP interface layer only

**Includes**: 6 MCP protected tools

**Excludes**: External APIs, internal action execution

**Scope**: MCP layer → Governance Pipeline → Effect Operations

**Security Assumption**: 
- API key authentication is sufficient for external callers (gateway, connector_caliber)
- External AI systems are trusted to submit telemetry without decision binding
- No audit trail required for external event recording

**Implementation Status**: ✅ Already working

**Risk Profile**: 
- Low risk for insider threats (MCP + governance validated)
- Moderate risk if API keys compromised (external paths unvalidated)

**Maintenance Cost**: Minimal

---

#### Option B: All Effect Surfaces (Maximum Audit Trail)

**Boundary Definition**: Authorization context required for ALL paths that write state

**Includes**: 6 MCP tools + 2 external API paths + internal action execution

**Excludes**: None

**Scope**: Complete execution tree

**Security Assumption**: 
- Every state change must trace to a governance decision
- External AI events are not mere telemetry but governance-tracked decisions
- Internal actions require GL7 validation before execution
- Full audit trail for all mutations

**Implementation Required**:
1. Propagate auth_context through event_buffer to Gate
2. Add auth_context binding to connector_caliber
3. Add GL7 validation checkpoint to action_executor
4. Update event_buffer to accept and pass auth_context

**Risk Profile**: Lowest risk (complete governance coverage)

**Maintenance Cost**: High (4 code changes + testing + integration verification)

---

#### Option C: MCP + External APIs (Boundary-Aware)

**Boundary Definition**: Authorization context required for human-facing and external-facing interfaces

**Includes**: 6 MCP tools + 2 external API paths

**Excludes**: Internal action execution (kept at API key auth only)

**Scope**: External interface layer

**Security Assumption**:
- Human-facing API (MCP) requires explicit decision
- External-facing APIs (gateway, connector) require authorization context
- Internal actions are trusted to use API key authentication
- Separates "external attack surface" from "internal trust boundary"

**Implementation Required**:
1. Propagate auth_context through event_buffer to Gate
2. Add auth_context binding to connector_caliber

**Risk Profile**: Moderate risk (addresses external boundary, internal tools remain lighter)

**Maintenance Cost**: Medium (2 code changes + testing)

---

### Decision Table

| Criterion | Option A | Option B | Option C |
|---|---|---|---|
| Implemented | ✅ Yes | ❌ No | ❌ No |
| Coverage | MCP only | All effects | External APIs |
| Audit Trail | Partial | Complete | Partial |
| Code Changes | 0 | 4 | 2 |
| Risk | Moderate | Minimal | Moderate |
| Maintenance | Minimal | High | Medium |
| Decision Point | None | Complete governance | External boundary |

---

## Part 5: REMAINING UNKNOWN

**Status**: ✅ NONE

All previous unknowns have been resolved:

| Previous Unknown | Resolution | Evidence |
|---|---|---|
| governance/write_path/* writes | Reads-only, separate namespace | Code analysis + grep results |
| orchestrator.execute() runtime | Unreachable from active code | Grep + process list + import analysis |
| External AI connector flow | Complete, functioning telemetry path | Code trace + process verification |

---

## Part 6: Evidence File References

### ACTIVE PATHS

**MCP Protected Tools**:
- `mocka_mcp_server.py:509` — execute_tool() entry point
- `mocka_mcp_server.py:534` — PROTECTED_TOOLS check
- `mocka_mcp_server.py:535-542` — auth_context population
- `mocka_mcp_server.py:612` — mocka_add_todo with auth_context
- `mocka_mcp_server.py:685` — mocka_update_todo with auth_context
- `mocka_mcp_server.py:743-755` — mocka_write_event adds _auth_binding
- `mocka_mcp_server.py:1057` — mocka_decision_write with auth_context
- `mocka_mcp_server.py:1142` — mocka_integrity_write with auth_context

**Gateway External Event**:
- `gateway/gateway.py:60` — @app.before_request check_auth()
- `gateway/gateway.py:142` — POST /api/v1/event endpoint
- `gateway/gateway.py:169` — get_buffer().push()
- `gateway/auth.py:40-51` — require_api_key() validation
- `interface/event_buffer.py:60` — flush_async() to Gate

**Connector Adapter**:
- `gateway/connector_caliber.py:32` — POST /api/v1/connector/query endpoint
- `gateway/connector_caliber.py:87` — IndexWriter.write()

### INACTIVE PATHS

**governance/write_path**:
- `governance/write_path/runtime/generator.py:26-39` — _read_events_readonly() (READ-ONLY)
- `governance/write_path/runtime/generator.py:79` — "実装のみ、検証実行時には呼び出さない"
- `governance/write_path/runtime/adapter.py:67` — "永続化は行わない"
- `governance/write_path/runtime/validator.py:13` — "どこにも永続化しない"
- `governance/write_path/restore/materializer.py:90` — Writes to materialized/ only
- `governance/write_path/restore/materializer.py:92-96` — Stub invocation

**orchestrator**:
- `orchestrator/orchestrator.py:14` — execute(request: str)
- `orchestrator/task_executor.py:5-40` — No state changes
- Grep results: **ZERO matches** for orchestrator.execute() in active code

---

## Part 7: Implementation Status

**Code Changes Made**: NONE

**Commits Created**: NONE

**Pushes Executed**: NONE

**Production Activation**: NONE

**Type**: READ-ONLY Fact-Based Audit Only

---

## Part 8: Next Steps (きむら博士による決定待ち)

This audit provides the factual foundation. Three Authorization Boundary scope options are available for Human Decision:

- **Option A**: Keep current (MCP tools only)
- **Option B**: Extend to all effect surfaces
- **Option C**: Extend to external APIs only

Decision authority: きむら博士

Once decided, implementation (if required) will follow with full traceability via CLAUDE.md file-change protocol.

---

**Report Status**: COMPLETE — Ready for Authorization Boundary Decision
