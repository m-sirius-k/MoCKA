# MoCKA RUNTIME BINDING INVESTIGATION
## PHASE 6: FINAL BINDING STATUS & MINIMUM IMPLEMENTATION POINT
**Date:** 2026-09-21  
**Investigation Status:** COMPLETE  
**Implementation Status:** NOT AUTHORIZED (Investigation Only)

---

## FINAL RUNTIME BINDING STATUS TABLE

### Layer-by-Layer Verification

| Layer | Identity | Status | Evidence | Binding to Previous |
|-------|----------|--------|----------|-------------------|
| **1. Request** | req_id (JSON-RPC id) | VERIFIED | mcp_endpoint() line 1271: `req_id = body.get("id")` | N/A (entry point) |
| **2. Idempotency** | req_id tracking | VERIFIED | _check_request_duplicate() line 599, request_executions table | req_id → request_executions |
| **3. Decision** | decision_id (DC_...) | VERIFIED | governance_pipeline._read_decision() line 91-112, decision_ledger.jsonl | PARTIAL: args.get("decision_id") but NOT linked to req_id |
| **4. Authority** | GovernanceDecision | VERIFIED | before_tool() validates decision status line 151 | VERIFIED: decision found in ledger |
| **5. Runtime Gate** | req_id passed to before_tool() | VERIFIED | execute_tool() line 621: `before_tool(..., req_id=req_id)` | PARTIAL: req_id in context but not persisted with decision validation |
| **6. Specific Execution** | **execution_id** | NOT FOUND | N/A | MISSING: No unique identifier for THIS execution |
| **7. Execution Outcome** | event_id/decision_id/classification_id | VERIFIED | Tool handlers return result IDs | PARTIAL: result_id returned but not linked to req_id |
| **8. Event** | event_id (E...) | VERIFIED | GATE generates event_id, returned line 842 | PARTIAL: request_id in gate_payload (line 836) but persistence unverified |
| **9. Consequence** | Implicit via result re-injection | NOT FOUND | No system-level consequence chain | NOT VERIFIED: Caller must parse result and re-call with decision_id |
| **10. Next Decision** | Next req_id | UNKNOWN | Caller initiates next request | NOT VERIFIED: No traceability from execution to consequent decision |

---

## BINDING VERIFICATION MATRIX

### Cross-Layer Linkage Map

```
Layer 1 (Request)
    ↓ req_id
Layer 2 (Idempotency Check)
    ↓ req_id preserved in request_executions table
Layer 3 (Decision Lookup)
    ↓ decision_id from args (INDEPENDENT from req_id)
Layer 4 (Authority Validation)
    ↓ decision found and status checked (VERIFIED)
Layer 5 (Runtime Gate)
    ↓ req_id in before_tool context (NOT PERSISTED)
Layer 6 (Specific Execution) ← MISSING EXECUTION_ID
    ↓ EXECUTION OCCURS
Layer 7 (Execution Outcome)
    ↓ result_id (event_id/decision_id) generated
Layer 8 (Event)
    ↓ event_id persisted (request_id presence unverified)
Layer 9 (Consequence)
    ↓ NO AUTOMATIC LINKING (implicit via caller re-injection)
Layer 10 (Next Decision)
    ↓ Caller must provide decision_id again
```

### Binding Status by Direction

| Direction | Path | Status | Evidence |
|-----------|------|--------|----------|
| **Request → Idempotency** | req_id → request_executions | VERIFIED | _check_request_duplicate() and _record_request_execution() |
| **Request → Decision** | args.get("decision_id") | VERIFIED | governance_pipeline line 138 |
| **Decision → Authority** | decision_id → decision_record | VERIFIED | _read_decision() and validation line 151 |
| **Authority → Execution** | decision.allowed → tool execution | VERIFIED | execute_tool() line 622 checks allowed flag |
| **Execution → Result** | tool handler → event_id/decision_id | VERIFIED | Each tool returns result ID |
| **Request → Result** | req_id → event_id | **NOT VERIFIED** | No defined mapping in execute_tool() return path |
| **Request → Consequence** | req_id → next req_id | **NOT FOUND** | No system-level linking |
| **Overall Execution** | req_id → execution_id → result_id | **NOT VERIFIED** | execution_id does not exist |

---

## CRITICAL FINDING: MISSING EXECUTION ID

### The Binding Gap

**Current Code State:**
```
execute_tool(name, args, req_id=None)  [line 595]
  ↓ [line 599]
  is_duplicate = _check_request_duplicate(req_id)
  ↓ [line 609]
  _record_request_execution(req_id, name, "started")
  ↓ [line 621]
  decision = _governance.before_tool(name, args, req_id=req_id, session_id=SESSION_ID)
  ↓ [line 647-1260]
  [tool-specific execution → result generation]
  ↓ [line 1283 (mcp_endpoint returns)]
  return json.dumps(result)
```

**What exists:**
- req_id: Request-level identifier ✓
- decision_id: Decision-level identifier ✓
- event_id: Event-level identifier ✓
- result structure: Contains generated IDs ✓

**What is missing:**
- **execution_id**: Link between request and execution outcome ✗
- **execution_id**: Unique identifier for THIS specific invocation ✗
- **Binding record**: req_id ↔ execution_id ↔ result_id ✗

### Why execution_id is Needed

```
Scenario: Request with req_id="msg-123" calls mocka_write_event

Current state:
  req_id: msg-123
  (execution proceeds without unique execution identifier)
  result: {"event_id": "E20260921_abc123"}
  
Traceability: Cannot answer "Was THIS execution (msg-123) what generated E20260921_abc123?"

With execution_id:
  req_id: msg-123
  execution_id: exec-msg-123-001  (unique per invocation)
  result: {"event_id": "E20260921_abc123", "execution_id": "exec-msg-123-001"}
  
  Traceability: Can query: WHERE execution_id = "exec-msg-123-001" → get all linked IDs
```

---

## MINIMUM REQUIRED BINDING POINT

### Location: execute_tool() function

**File:** mocka_mcp_server.py:595-1260  
**Canonical scope:** Single function where all execution flows converge

### Changes Required (MINIMUM SCOPE)

```python
def execute_tool(name, args, req_id=None):
    try:
        # STEP 9a: EXISTING (line 599)
        is_duplicate, dup_req_id = _check_request_duplicate(req_id)
        if is_duplicate:
            return json.dumps({...})
        
        # STEP 9b: EXISTING (line 609)
        _record_request_execution(req_id, name, "started")
        
        # STEP 9c: MISSING ← MINIMUM BINDING POINT
        # Generate unique execution identifier
        # THIS IS THE MISSING BOUNDARY
        execution_id = f"exec-{req_id}-{secrets.token_hex(4)}"  # or UUID
        
        # STEP 9d: MISSING ← BIND req_id to execution_id
        # Record execution context
        # THIS IS WHERE BINDING HAPPENS
        _record_execution_binding(req_id, execution_id, name)
        
        # STEP 10-12: EXISTING (governance → tool execution → result)
        [...existing code...]
        
        # RESULT CAPTURE: MISSING ← AT RETURN POINT
        # Before returning, capture result IDs and bind to execution_id
        result_json = json.dumps({"status": "ok", "event_id": eid, ...})
        result_obj = json.loads(result_json)
        result_id = result_obj.get("event_id") or result_obj.get("decision_id") or result_obj.get("classification_id")
        
        # BINDING RECORD: MISSING ← PERSISTENCE
        if result_id:
            _record_execution_outcome(execution_id, result_id)
        
        return result_json
```

### Specific Implementation Points

| Point | File:Line | Current Code | Required Change |
|-------|-----------|--------------|-----------------|
| **Execution ID Generation** | mocka_mcp_server.py:610 | `_record_request_execution(req_id, name, "started")` | ADD: `execution_id = generate_execution_id()` |
| **Execution ID Thread** | mocka_mcp_server.py:1283 (mcp_endpoint) | Pass through (implicit) | ADD: Thread execution_id through execute_tool() return |
| **Binding Record Table** | mocka_mcp_server.py:\_get_db() (line 94) | SQLite table: `request_executions` | ADD: New table `execution_bindings(execution_id, req_id, result_id, result_type, timestamp)` |
| **Result ID Extraction** | mocka_mcp_server.py:1260 (return statement) | Each tool returns result independently | ADD: Centralized result capture before final return |
| **Binding Persistence** | mocka_mcp_server.py:1260 | No binding record | ADD: `_record_execution_outcome(execution_id, result_id)` before return |
| **Response Format** | mocka_mcp_server.py:1283 | JSON-RPC result field | ADD OPTIONAL: Include execution_id in result (backward compatible) |

---

## WHAT THIS BINDING POINT SOLVES

### 1. Request-Level Idempotency → Execution Outcome
```
Before: req_id → idempotency check ONLY
After:  req_id → execution_id → result_id (event_id/decision_id/classification_id)
```

### 2. Decision-Consequence Tracing
```
Before: decision_id read from args, execution outcome separate
After:  req_id → execution_id → decision_id_input (args) + result_id_output (event)
```

### 3. Event Consequence Linking
```
Before: event_id generated, no link to request
After:  req_id → execution_id → event_id with query capability
```

### 4. Institutional Memory Activation
```
Before: Execution logged separately (auto_log) but not unified
After:  Single execution_bindings record: (req_id, execution_id, result_type, result_id)
         Queries: "What was the event_id from request msg-123?"
                  "What request generated event E20260921_abc123?"
```

---

## WHAT THIS BINDING POINT DOES NOT SOLVE

### Out of Scope (By Design)

1. **Automatic Consequence Chain**
   - Still requires explicit decision_id in next request
   - No auto-inference of next decision from execution outcome
   - (Would require Decision Re-evaluation system)

2. **Schema Modifications to Existing Ledgers**
   - Decision Ledger remains append-only JSONL
   - Event Ledger remains SQLite events table
   - Classification Ledger remains append-only JSONL
   - (Preserves existing canonicality)

3. **Governance Enforcement Enhancement**
   - Authority validation at before_tool() unchanged
   - GL1-GL7 logic unchanged
   - (Binding is observational, not enforcement)

4. **Consequence Automatic Escalation**
   - No auto-BLOCK based on previous decision
   - No auto-REVOKE of future permissions
   - (Requires separate authority re-evaluation)

---

## SUMMARY: MISSING BOUNDARY IDENTIFIED

### Current State
```
JSON-RPC Request with id="msg-123"
  ↓ [identified by req_id]
Tool execution occurs
  [NO UNIQUE IDENTIFIER FOR THIS EXECUTION]
  ↓
Result: {"event_id": "E20260921_abc123"}
  [RESULT NOT LINKED TO REQUEST]
```

### After Minimum Binding Implementation
```
JSON-RPC Request with id="msg-123"
  ↓ [identified by req_id]
Tool execution with execution_id="exec-msg-123-abc1"
  [UNIQUE IDENTIFIER FOR THIS EXECUTION CREATED]
  ↓
Result: {"event_id": "E20260921_abc123"}
  ↓
Binding Record: (req_id=msg-123, execution_id=exec-msg-123-abc1, result_id=E20260921_abc123)
  [RESULT LINKED TO REQUEST AND EXECUTION]
```

### Minimum Implementation Scope
1. Generate execution_id in execute_tool() (line ~610)
2. Create execution_bindings table (line ~556-563 schema area)
3. Extract and store result_id before final return (line ~1260)
4. Optional: Include execution_id in response (line ~1286)

**Lines to modify:** mocka_mcp_server.py lines 556-563 (schema), 609-615 (execution_id generation), 1260 (result capture), 1283-1286 (response)

**NO CHANGES REQUIRED TO:**
- governance_pipeline.py
- Decision Ledger schema/format
- Event schema/format
- Classification schema/format
- Tool handlers (mocka_write_event, mocka_decision_write, etc.)

---

## INVESTIGATION COMPLETE

**Status:** APPROVED FOR HAND-OFF TO IMPLEMENTATION PHASE

All 6 phases complete:
- PHASE 1: Canonical Execution Path ✓ VERIFIED
- PHASE 2: ID Inventory ✓ COMPLETE
- PHASE 3: Decision → Execution ✓ PARTIAL
- PHASE 4: Execution → Event ✓ PARTIAL
- PHASE 5: Consequence Trace ✓ NOT FOUND
- PHASE 6: Minimum Binding Point ✓ IDENTIFIED

**Single implementation boundary identified:**
Location: execute_tool() function (mocka_mcp_server.py:595-1260)
Missing: Execution ID generation and outcome binding record

**No implementation changes authorized.**
Investigation documentation complete for Human Gate review.
