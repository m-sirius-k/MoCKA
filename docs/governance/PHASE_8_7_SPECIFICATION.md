# PHASE 8-7: Execution → Decision → Event → Institutional Memory

**Status**: IMPLEMENTED / VERIFIED (in isolation)  
**Branch**: `claude/lucid-allen-3cics5`  
**Baseline**: `da4d4db` (Phase 8-6 GL7-UNENFORCED-CONDITIONS-BUG)  
**Date**: 2026-09-26

---

## Objective

Close the end-to-end governance chain by connecting Execution results to canonical Decision/Event/Memory paths:

```
HUMAN
  ↓ (user request)
JARVIS
  ↓ (intent extraction)
HAB
  ↓ (decision generation)
Execution Provider (LocalProvider)
  ↓ (execution_id / status / output / error)
--- PHASE 8-7 CONNECTOR ---
  ↓
Decision Ledger (canonical: data/decisions/decision_ledger.jsonl)
  ↓ (companion event auto-generated)
Event Store (canonical: sqlite via GATE endpoint)
  ↓
Institutional Memory (canonical: MemoryStore)
```

---

## Contract Compliance

**Governance Semantics (non-negotiable)**:
- `EXECUTION ≠ AUTHORIZATION` - Recording execution result does NOT mean it's approved
- `RECORDED ≠ USED` - Written to ledger for audit trail only, not validated yet
- `UNKNOWN ≠ VERIFIED` - MCP server unavailable → status is UNVERIFIED, not failed
- No AI auto-approval or scope bypass
- Human Gate remains independent arbiter

**No Scope Creep**:
- Does NOT modify existing canonical paths (Decision, Event, Memory)
- Does NOT create parallel Decision/Event/Memory stores
- Does NOT change GL7 governance engine
- Does NOT change BA04 authorization model
- Does NOT implement new AI approval mechanism

---

## Implementation

### Core Components

#### 1. `governance/execution_decision_connector.py`

**Main class**: `ExecutionDecisionConnector`

Entry point:
```python
connector = ExecutionDecisionConnector(mcp_endpoint="http://localhost:5002")

result = connector.connect_execution_to_canonical_paths(
    execution=ExecutionResult(...),
    decision_context={
        "title": "...",
        "rationale": "...",
        "impact": "..."
    }
)
```

**Flow**:
1. Takes ExecutionResult from Execution Provider
2. Calls `mocka_decision_write` via MCP endpoint (canonical Decision path)
3. mocka_decision_write auto-generates companion event (canonical Event path)
4. Calls `MemoryWriter.write_event` (canonical Memory path)
5. Returns trace with all IDs linked via correlation_id

**ID Chain**:
```
correlation_id
  ↓ (passed through)
task_id
  ↓ (passed through)
hab_request_id
  ↓ (passed through)
execution_id
  ↓ (recorded in decision)
decision_id
  ↓ (auto-generated event)
event_id
  ↓ (written to memory)
memory_id
```

#### 2. `governance/phase8_7_verification.py`

Verification harness that tests:
- Canonical path audit (read-only)
- Execution result creation with IDs
- Connection attempt to MCP server
- Trace chain preservation
- Failure isolation (failure status not masked)

#### 3. `tests/test_phase8_7_connector.py`

Unit tests using mocked HTTP:
- Execution result factory
- Decision write success/failure
- MCP server error handling
- Memory write integration
- Correlation ID preservation
- Governance semantics enforcement

---

## Canonical Paths Used (Read-Only Audit)

### Decision Write (mocka_mcp_server.py:968-1029)

- **Tool**: `mocka_decision_write`
- **Endpoint**: `POST /agent/mocka_decision_write` (via MCP server at :5002)
- **Persistence**: `data/decisions/decision_ledger.jsonl` (append-only JSONL)
- **Companion Event**: Auto-generated with tags `decision_ledger,{decision_id},{status}`
- **Schema**: DECISION_LEDGER_SCHEMA_v1.md (docs/mocka3/)

### Event Write (mocka_mcp_server.py:666-738)

- **Tool**: `mocka_write_event`
- **Endpoint**: `POST /agent/mocka_write_event` (via MCP server at :5002)
- **Gateway**: HTTP POST to `http://localhost:5000/api/gate/event` (PHI-OS GATE)
- **Fallback**: `phi_os.event_gate.process_event()` (in-process if GATE down)
- **Storage**: SQLite (`data/mocka_events.db`) via GATE processing
- **Signature**: Validated hash chain maintained

### Institutional Memory Write (memory/memory_writer.py)

- **Class**: `MemoryWriter`
- **Method**: `write_event(event, memory_type=EPISODIC, source=GOVERNANCE)`
- **Storage**: MemoryStore (configured per memory_registry)
- **Retention**: EPISODIC memory policy
- **Source Tag**: `Source.GOVERNANCE`
- **Indexing**: Via `memory_id`, tags-based searchable

---

## Verification Matrix

| Component | Status | Evidence | Notes |
|-----------|--------|----------|-------|
| **Canonical Path Audit** | VERIFIED | Found all 3 canonical paths | Read-only inspection only |
| **Connector Instantiation** | VERIFIED | `ExecutionDecisionConnector()` creates cleanly | Core logic works in isolation |
| **ExecutionResult Factory** | VERIFIED | All IDs auto-generated correctly | Correlation chain preserved |
| **ID Chain Preservation** | VERIFIED | `correlation_id` threaded through all stages | Test harness confirms structure |
| **Decision Write (isolated)** | VERIFIED | Mock HTTP test shows correct payload | Requires MCP server for actual persistence |
| **MCP Server Endpoint** | UNVERIFIED | localhost:5002 unreachable in test env | Flask/MCP server not running |
| **GATE Endpoint** | UNVERIFIED | localhost:5000 unreachable in test env | GATE server not running |
| **Decision Persistence** | UNVERIFIED | Cannot verify without running MCP server | Would write to decision_ledger.jsonl if server active |
| **Event Persistence** | UNVERIFIED | Cannot verify without running GATE | Would write to mocka_events.db if GATE active |
| **Companion Event** | UNVERIFIED | Auto-generation mechanism exists in mocka_decision_write | Would test with server |
| **Memory Write** | UNVERIFIED | MemoryWriter.write_event available but MemoryStore state unknown | Optional integration, graceful fallback |
| **Failure Isolation** | VERIFIED | Test shows failure status NOT masked as success | Connector logic correct |
| **Governance Semantics** | VERIFIED | No auto-approval, no scope bypass | Code structure enforces contract |
| **Restart/Read-Back** | UNVERIFIED | Requires persistent servers to restart and verify IDs recoverable | Post-implementation verification |

---

## Test Results

### Unit Tests (VERIFIED)
```
TEST 1: Create execution result - PASS
  ✓ Status assignment
  ✓ Correlation ID preservation
  ✓ Execution ID auto-generation
  ✓ Task ID auto-generation
  ✓ HAB Request ID auto-generation

TEST 2: Create failure result - PASS
  ✓ Failure status recorded
  ✓ Error message stored

TEST 3: Auto-generated IDs - PASS
  ✓ All 4 IDs auto-generated with correct prefixes
  ✓ ISO timestamps set

TEST 4: Connector instantiation - PASS
  ✓ MCP endpoint configured
  ✓ MemoryWriter available (or gracefully None)
```

### Integration Tests (MCP Server Required)
```
Failure: MCP server not running (localhost:5002 unreachable)
Expected behavior verified via mock tests

Status: PARTIAL
  - Connector logic: VERIFIED
  - Canonical paths: VERIFIED (structure, not runtime)
  - Server integration: UNVERIFIED (requires servers)
```

### End-to-End Trace (Simulated)
```
Human Input
  ↓ correlation_id=CORR_TEST_20260926003159
JARVIS Intent
  ↓ task_id=TASK_PYTEST_20260926003159
HAB Decision
  ↓ hab_request_id=HAB_PYTEST_20260926003159
Execution Provider
  ↓ execution_id=EXEC_20260926003159_18eac485
Phase 8-7 Connector
  ↓ [MCP Server Unreachable]
  → decision_id=WOULD_BE_DC_20260926_NNN (UNVERIFIED)
  → event_id=WOULD_BE_EV_20260926_NNN (auto-generated, UNVERIFIED)
  → memory_id=WOULD_BE_MEM_NNN (UNVERIFIED)
```

---

## Governance Check

**GL7 Enforcement**: ✓ Preserved  
- ExecutionGovernanceEngine unchanged
- Dry Run/Abort conditions unchanged
- Does not bypass pre_execution_check

**BA04 Authorization Model**: ✓ Preserved  
- No auto-approval
- Human Gate remains independent
- `approved_by` field recorded, not auto-filled

**Scope Binding**: ✓ Preserved  
- No scope expansion
- No new AI decision authority
- Recording only, not authorization

**Decision/Event/Memory Schemas**: ✓ Unchanged  
- Existing structures used as-is
- New fields only via append mechanism
- Backward compatible

---

## Known Limitations

1. **Flask Application Runtime**: GATE server (`app.py`) and MCP server (`mocka_mcp_server.py`) must be running for full verification
   - Current test environment: servers not active
   - Resolution: Start servers, re-run verification script
   - Designation: UNVERIFIED (not failed, pending environment)

2. **MemoryWriter Availability**: Institutional Memory store location depends on `memory_registry` configuration
   - Current implementation: graceful fallback if unavailable
   - Not blocking to Decision/Event recording
   - Designation: OPTIONAL (non-blocking)

3. **Persistence Verification**: Cannot re-read from Decision/Event/Memory stores without running servers
   - Would require `mocka_decision_get`, `mocka_read_event`, and Memory API calls
   - Test harness prepared; needs server availability

---

## Next Steps (Post-Phase-8-7)

1. **Runtime Verification**: Start MCP + GATE servers, re-run `governance/phase8_7_verification.py`
   - Expected: all "UNVERIFIED" → "VERIFIED"

2. **Restart/Read-Back**: Verify persistence across restart
   - Stop services → Start services → Read IDs from stores
   - Confirm correlation_id chain unbroken

3. **Failure Scenarios**: Test with actual execution failures
   - Execution timeout → should record as failure
   - Execution crash → should record as halted
   - Memory write failure → should not block Decision/Event

4. **Integration with HAB**: Wire actual HAB output to connector
   - Currently standalone; needs HAB request handler to call connector

5. **JARVIS Integration**: Add execution tracing from intent → HAB → Execution → Decision

---

## Files Changed (Phase 8-7)

```
+ governance/execution_decision_connector.py (NEW)
+ governance/phase8_7_verification.py (NEW)
+ tests/test_phase8_7_connector.py (NEW)
+ docs/governance/PHASE_8_7_SPECIFICATION.md (NEW)
```

**Modified**: None (preserves existing canonical paths)

---

## Commit Message

```
Phase 8-7: Close Execution to Institutional Memory governance chain

- Add ExecutionDecisionConnector to bridge Execution → Decision → Event → Memory
- Implement using canonical mocka_decision_write, mocka_write_event, MemoryWriter
- Add verification harness showing ID chain preservation and failure isolation
- Add unit tests with mocked HTTP (actual server optional)
- Preserve all existing GL7/BA04/authorization semantics
- No parallel stores, no scope creep, no auto-approval

Verification Status:
  Connector logic: VERIFIED
  Canonical paths: VERIFIED (structure audit)
  Server integration: UNVERIFIED (requires Flask/MCP runtime)

correlation_id threading: VERIFIED through all 4 ID layers
Failure isolation: VERIFIED (status not masked)
Governance semantics: VERIFIED (no auto-approval)
```

---

## References

- `CLAUDE.md` - MoCKA Protocol v1.0
- `governance/seal_governance_wrapper.py` - Decision Unit recording (Phase 8-6)
- `mocka_mcp_server.py` - Canonical tool implementations
- `docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md` - Decision format specification
- `phi_os/event_gate.py` - GATE event processing
