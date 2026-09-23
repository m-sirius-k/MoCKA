---
name: step9_request_boundary
description: Step 9 — Request Boundary Investigation (Existing Mechanisms Only)
metadata:
  type: project
---

# Step 9 Request Boundary Investigation

**Date:** 2026-09-20  
**Scope:** Identify where requests arrive and what existing values can be used for request identity  
**No code changes, no new identifiers proposed**

---

## 1. Request Arrival Point

**VERIFIED:** `/mcp` endpoint in `mocka_mcp_server.py` line 1126-1151

```python
@app.route("/mcp", methods=["GET", "POST"])
def mcp_endpoint():
    body = request.get_json()          # ← REQUEST ARRIVES HERE
    method = body.get("method", "")
    req_id = body.get("id")            # ← JSON-RPC id extracted
    params = body.get("params", {})
    
    # ... (lines 1137-1143: method dispatch)
    
    elif method == "tools/call":
        result = {"content": [
            {"type": "text", 
             "text": execute_tool(params.get("name", ""), 
                                 params.get("arguments", {}))}
        ], "isError": False}
```

**Request Arrival Boundary:** Line 1130 `request.get_json()`

---

## 2. Actual Call Chain

```
mcp_endpoint (line 1126)
    │
    ├─ request.get_json() [line 1130]
    │   └─ Extract: method, req_id, params
    │
    ├─ Route based on method (line 1141-1143)
    │   └─ tools/call: params.get("name"), params.get("arguments")
    │
    └─ execute_tool(tool_name, args) [line 1144]
        │
        ├─ before_tool(tool_name, args) [governance_pipeline.py line 492]
        │   ├─ tool_name → required
        │   └─ args → required
        │   └─ NO req_id, NO intent_id
        │
        └─ Tool-specific implementation (line 509+)
            ├─ mocka_write_event: args contain {title, description, tags, author, ...}
            ├─ mocka_get_overview: args empty
            └─ ... (other tools)
```

**Key Observation:**
- **req_id is extracted at line 1132 but NOT passed to execute_tool()**
- **req_id is only used for response construction (line 1147)**
- **execute_tool() receives only tool_name and args**

---

## 3. Existing Request Identity Candidates

### Table: What's available at request arrival vs execution

| Candidate | At Arrival? | Before Execution? | Same on Retry? | Different on Legit Re-exec? | Persisted? | Evidence |
|-----------|-------------|------------------|--------|-----|-----------|----------|
| **JSON-RPC id** | ✓ YES (line 1132) | ✗ NO (not passed) | ? UNKNOWN | ? UNKNOWN | ✗ NO | Extracted but not propagated |
| **tool_name** | ✓ YES (line 1143) | ✓ YES (line 1144) | ✓ SAME | ✗ DIFFERENT | ✓ YES | Passed to execute_tool() |
| **arguments** | ✓ YES (line 1133) | ✓ YES (line 1144) | ✓ SAME | ✗ DIFFERENT | ✓ YES (in events) | Passed to execute_tool() |
| **intent_id** | ✗ NO | ✗ NO | ? N/A | ? N/A | ✗ UNCLEAR | Not in tool args; might be in goal.json |
| **action_id** | ✗ NO | ✗ NO | ? N/A | ? N/A | ✗ UNCLEAR | Not in tool args; defined in execution_context.py |
| **plan_id** | ✗ NO | ✗ NO | ? N/A | ? N/A | ✗ CONFLICT | Defined in code but not in plan.json |
| **decision_record_id** | ✗ NO | ✗ NO (ephemeral) | ? N/A | ? N/A | ✗ UNCLEAR | Computed fresh each call |
| **execution_id** | ✗ NO | ✗ NO | ? N/A | ? N/A | ✗ UNCLEAR | Defined in ExecutionContext but storage unknown |

### Critical Findings:
1. **JSON-RPC id:** EXISTS but NOT ACCESSIBLE inside execute_tool()
2. **tool_name + args:** ACCESSIBLE and STABLE across retries
3. **intent_id/action_id:** NOT ACCESSIBLE at request level (only in execution context)
4. **decision_record_id:** NOT PERSISTENT (ephemeral GovernanceDecision)

---

## 4. Duplicate Check Insertion Point

**Current execution flow:**
```
mcp_endpoint() line 1126
    → governance.before_tool() line 492
    → execute_tool() continues: line 509+ (actual tool execution)
```

**Where underlying action actually executes:**
- For `mocka_write_event`: line 569 in execute_tool() `save_todo(data)`
- For `mocka_get_overview`: line 511 `json.loads(OVERVIEW_PATH.read_text(...))`
- For `mocka_decision_write`: line ~1216 (database write)

**Minimum insertion point for duplicate check:**
**Line 1144 in mocka_mcp_server.py, inside mcp_endpoint(), BEFORE calling execute_tool()**

This is the ONLY place where both req_id and tool execution details are available.

**Constraint:** Would require modifying execute_tool() signature to accept req_id, or creating a wrapper.

---

## 5. JSON-RPC id Behavior Confirmation

### Can we determine if JSON-RPC id is stable across retries?

**HTTP/MCP retry behavior:** NOT CONFIRMED in existing code

**Evidence needed but missing:**
- [ ] HTTP client implementation (how does client retry?)
- [ ] Whether client re-sends same JSON-RPC id on retry
- [ ] Whether server tracks JSON-RPC id across calls
- [ ] mcp_endpoint() behavior on duplicate req_id

**Current implementation:** 
- Extracts req_id at line 1132
- Uses req_id in response at line 1147
- **But no mechanism to track or compare previous req_ids**

**Status:** JSON-RPC id is AVAILABLE but **UNUSED for idempotency**

---

## 6. tool_name + args Combination Validation

### Can same tool + same args distinguish between retry and legitimate re-execution?

**NO. Same tool + same args CAN represent different user intents:**

**Example case (VERIFIED from intent_ledger.json):**
```
Event 1: intent_id=7053cfc7-... (2026-03-23 01:57:43)
Event 2: intent_id=7053cfc7-... (2026-03-23 01:58:30) ← same UUID, 47 seconds later
Event 3: intent_id=7053cfc7-... (2026-03-23 01:59:14) ← same UUID, 44 seconds later
```

All three could have:
- tool_name = "mocka_write_event"
- args = {title: "...", description: "...", author: "Claude"}

**But are they:**
- A. Retry of Event 1?
- B. Three separate user submissions of same intent?
- C. Loop generating duplicate events?

**Answer:** CANNOT DETERMINE without request-level ID

**Why tool_name + args is insufficient:**
- No way to know if args came from retry or new user action
- No way to know if user sent same tool twice intentionally
- No correlation with network-level request identity

---

## 7. A/B/C Judgment

### Can Request Identity be built from existing mechanisms?

**A. Existing mechanism sufficient?** ✗ NO

**B. Existing mechanism insufficient?** ✓ YES

**C. New identifier needed?** ✓ LIKELY YES, but conditional

### Detailed verdict:

**What CAN be done with existing code:**
- Use tool_name + args_hash as "semantic action identity" (what action was requested)
- This distinguishes between different tool calls
- But CANNOT distinguish retry from new identical request

**What CANNOT be done with existing code:**
- Detect network-level retries (JSON-RPC id not propagated)
- Detect if user sent same tool twice intentionally
- Track request through execution pipeline (no request ID in ExecutionContext)

**What WOULD BE NEEDED:**
1. Propagate JSON-RPC id through execute_tool() and governance chain
2. OR add session_id to ExecutionContext (but session not tracked)
3. OR persist request attempt records (request_executions table) - but this is schema change

---

## 8. Minimum Implementation to Support Request Identity

### Without code changes:
- [ ] Cannot implement request deduplication
- [ ] Cannot distinguish retry from sequential submission

### With minimal changes:
1. **Propagate JSON-RPC req_id to execute_tool():**
   ```python
   # Change line 1144
   result = {"content": [{"type": "text", 
                          "text": execute_tool(
                              params.get("name", ""), 
                              params.get("arguments", {}),
                              req_id=req_id  # ← ADD THIS
                          )}], "isError": False}
   
   # Change execute_tool signature line 480
   def execute_tool(name, args, req_id=None):  # ← ADD PARAM
   ```

2. **Store execution attempt:**
   ```python
   # Inside execute_tool, before actual execution
   if req_id and name not in READ_ONLY_TOOLS:
       # Log this request attempt (would need persistent storage)
       # Check if same req_id was executed before
       # If yes: return cached result
       # If no: proceed with execution
   ```

3. **Persist where:**
   - Option A: in-memory dict (lost on restart)
   - Option B: SQLite table (requires schema change)
   - Option C: execution_log file (but location unknown)

---

## 9. Step 9 Status

### Current State: PARTIALLY COMPLETE

**Verified:**
✓ Request arrival point identified (mcp_endpoint line 1130)
✓ Call chain traced (arrival → governance → execution)
✓ Existing values available: tool_name, args, JSON-RPC req_id
✓ Duplicate check insertion point identified (line 1144)
✓ Limitation confirmed: Cannot distinguish retry from re-execution with existing values alone

**Blockers for Implementation:**
1. JSON-RPC id is extracted but NOT PROPAGATED to execute_tool()
2. No persistent request execution history
3. intent_id / action_id not accessible at request level
4. No session tracking in ExecutionContext

**Path Forward:**
- **Option A:** Propagate JSON-RPC id + add in-memory deduplication (simple, session-scoped)
- **Option B:** Propagate JSON-RPC id + add SQLite request_executions table (persistent)
- **Option C:** Wait for execution context to include request-level metadata

**Recommendation:** Option A (minimal change, solves immediate idempotency within session)

---

## Summary

| Item | Finding | Evidence | Next Action |
|------|---------|----------|------------|
| **Request arrival** | `/mcp` endpoint line 1130 | Code verified | - |
| **Available at arrival** | method, req_id, tool_name, args | Code verified | - |
| **Available at execution** | tool_name, args | req_id NOT passed | Propagate req_id |
| **Can detect retry?** | NO with current code | Req_id not persisted | Add request log |
| **Retry vs re-exec?** | CANNOT distinguish | Same args ≠ retry ID | Need request-level ID |
| **Minimum schema change** | request_executions table OR in-memory dict | Option B needs migration | Choose Option A/B |
| **Implementation blocker** | JSON-RPC id propagation | Currently dead-end | Modify line 480, 1144 |

---

## Scope Out (NOT INVESTIGATED)

- [ ] policy_hash versioning
- [ ] session_id new design
- [ ] New request_executions table deployment
- [ ] HG policy architecture
- [ ] Paper 5 formalization
- [ ] Live HTTP E2E testing
- [ ] UI changes
- [ ] Unrelated TODOs

These will be re-evaluated once request boundary is stabilized.

