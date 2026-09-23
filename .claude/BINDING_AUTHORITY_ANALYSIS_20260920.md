# BINDING AUTHORITY ANALYSIS

## PHASE 1: DECISION AUTHORITY ORIGIN

### Who creates Human Gate Decision?

**Tool:** `mocka_decision_write()` (MCP tool)  
**Caller:** Any MCP client

**Authority fields:**
```python
# Line 1050: mocka_mcp_server.py
approved_by = args.get("approved_by", "").strip()
```

**Critical finding: NO AUTHORITY VALIDATION**
- approved_by is taken directly from MCP args
- NO check that caller has right to claim this authority
- NO validation of approved_by identity
- NO session authentication
- Default: _DEFAULT_ACTOR = "Claude-code-sonnet-4-6"

**What gets stored:**
- ✓ decision_id (DC_YYYYMMDD_NNN)
- ✓ approved_by (from args, unchecked)
- ✓ approved_at (system timestamp)
- ✓ status (from args)
- ✓ title, context, decision, rationale, impact
- ✗ scope (NOT in schema)
- ✗ target_tool (NOT in schema)
- ✗ target_action (NOT in schema)

**Authority gap:** ANY MCP caller can write ANY approved_by value

---

## PHASE 2: EXECUTION AUTHORITY ORIGIN

### Who initiates MCP Execution?

**Flow:**
```
MCP Protocol (HTTP POST)
  ↓
/mcp endpoint (mocka_mcp_server.py:1202-1227)
  ├─ body.get("id") → req_id (JSON-RPC id)
  ├─ body.get("params.name") → tool_name
  ├─ body.get("params.arguments") → args dict
  ↓
execute_tool(name, args, req_id)  [line 541]
  ├─ No session authentication
  ├─ No user identification
  ├─ req_id used for idempotency only
  ↓
Tool execution begins
```

**Session tracking:**
```python
# Line 88: Per-process session ID (not per-user)
SESSION_ID = "SESSION_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Line 89: Default actor if not specified
_DEFAULT_ACTOR = "Claude-code-sonnet-4-6"
```

**Request tracking (line 521-532):**
```python
def _record_request_execution(req_id, tool_name, status="started"):
    # Stores in request_executions table:
    # - req_id (PRIMARY KEY, from MCP id field)
    # - executed_at (timestamp)
    # - tool_name
    # - status
    
    # NO LINK to decision_id
```

**Authority gap:** 
- No authentication of MCP caller
- No verification of caller identity
- SESSION_ID is per-process, not per-user
- Anyone can submit MCP request

---

## PHASE 3: EXISTING AUTHORITY BINDING

### Is there any link between Decision and Execution?

**Search results for decision_id ↔ req_id:**

| Location | Pattern | Result |
|----------|---------|--------|
| request_executions table | decision_id field | NOT PRESENT |
| execute_tool() | decision lookup | NOT PERFORMED |
| before_tool() | decision check | NOT PERFORMED |
| mocka_mcp_server.py | args["decision_id"] | NOT EXTRACTED |
| mocka_decision_write | req_id link | NOT PRESENT |
| MCP tools/call dispatch | decision binding | NOT PRESENT |

**Separate (disconnected) systems:**

1. **mocka_decision_write** (seal_governance_gate.py:126)
   - Generates decision_id = f"DC_{execution_id}"
   - Used ONLY in seal_governance system
   - NOT connected to MCP execution

2. **MCP execution** (mocka_mcp_server.py)
   - Uses req_id (JSON-RPC id field)
   - Stored in request_executions table
   - NO reference to decision_ledger.jsonl

**Existing Binding:** NONE FOR MCP PATH

---

## PHASE 4: DECISION SELECTOR — Who chooses which decision?

### Four possible authority models:

**A. Human Gate selects decision and binds to execution**
- Status: NOT IMPLEMENTED
- Would require: HG knowing req_id at decision-write time
- Problem: Decision written before execution happens

**B. MCP client provides decision_id in tool args**
- Status: THEORETICALLY POSSIBLE
- Implementation: args.get("decision_id")
- Problem: Client can specify ANY decision_id (no validation)
- Security: CRITICAL TRUST BOUNDARY ISSUE

**C. AI/tool specifies decision_id during execution**
- Status: NOT IMPLEMENTED
- Would require: Tool author knowing decision_id
- Problem: Circular (tool shouldn't know its own decision)

**D. Runtime auto-selects decision from context**
- Status: NOT IMPLEMENTED
- Would require: Scope/target fields in decision schema
- Problem: No scoping mechanism exists

**Current state:** NONE OF THE ABOVE

---

## PHASE 5: TRUST BOUNDARY — Can execution requester control decision?

### If Decision selection were via args["decision_id"]:

```
MCP Caller (untrusted)
  ↓
args = {"decision_id": "DC_20260920_001", ...}
  ↓
execute_tool(name, args, req_id)
  ↓
before_tool() reads args["decision_id"]
  ↓
Looks up decision_id in decision_ledger
  ↓
Allows/Denies execution based on decision
```

**CRITICAL ISSUE: Execution requester can:**
- Choose which decision to invoke
- Bypass other decisions
- Speculate on valid decision_id values
- Replay decisions

**Who prevents this?**
- ✗ NOT: Authentication (no user identification)
- ✗ NOT: Authorization checks (no scope validation)
- ✗ NOT: Decision ownership (no target_tool field)
- ✗ NOT: Binding signature (no integrity)

**VULNERABILITY: CRITICAL - BINDING BYPASS POSSIBLE**

---

## PHASE 6: MINIMUM MISSING CONTRACT

| Element | Status | Note |
|---------|--------|------|
| Decision Identity | EXISTS | DC_YYYYMMDD_NNN format |
| Execution Identity | EXISTS | req_id + tool_name |
| Decision Authority | EXISTS | approved_by field |
| Execution Authority | MISSING | No caller authentication |
| Binding Selector | MISSING | No decision selection mechanism |
| Binding Authority | MISSING | No authority for selection |
| Binding Validator | MISSING | No permission check |
| Binding Persistence | MISSING | No decision_id ↔ req_id storage |
| Binding Integrity | MISSING | No signature/hash verification |
| Scope Definition | MISSING | No target_tool/target_action in schema |
| Trust Boundary | MISSING | Requester can select own decision |

---

## PHASE 7: AUTHORITY CLASSIFICATION

### Final analysis:

**Who authorizes Decision creation?**
→ **MCP caller** (unchecked, unvalidated)

**Who authorizes Execution?**
→ **MCP client** (no authentication)

**Who links Decision to Execution?**
→ **NOBODY** (no mechanism exists)

**Who prevents attack (Decision bypass)?**
→ **NOBODY** (no validation, no scope, no binding)

**Authority chain:**
```
MCP Caller (untrusted)
  → Writes Decision (approved_by unchecked)
  → Initiates Execution (req_id standalone)
  → [NO LINK BETWEEN THEM]
  → Execution proceeds
```

---

## PHASE 8: FINAL CLASSIFICATION

```
═══════════════════════════════════════════════════════════

CLASSIFICATION: 3. BINDING AUTHORITY GAP

═══════════════════════════════════════════════════════════
```

### Evidence:

**Why NOT option 1?**
- No binding authority exists to be "already in place"
- Decisions and executions are separate, unlinked

**Why NOT option 2?**
- There is no unused binding authority to speak of
- Authority relationship itself is missing

**Why NOT option 4?**
- Only one authority model is attempted (both tools call args)
- No conflicting paths, just one broken path

**Why NOT option 5?**
- It's not that binding authority is "unverified"
- It's that binding authority does NOT EXIST

**Why OPTION 3?**
- Decision authority: who approved_by? UNCHECKED
- Execution authority: who is MCP caller? UNAUTHENTICATED
- Binding authority: who links them? NO MECHANISM
- Selection authority: who chooses decision? NOT DEFINED
- Trust boundary: breachable by caller manipulation

### Authority gaps identified:

1. **Decision Authority Gap**
   - approved_by from unchecked MCP args
   - No validation of authority

2. **Execution Authority Gap**
   - No MCP caller authentication
   - No user identification

3. **Binding Authority Gap**
   - No mechanism to link decision → execution
   - No permission to bind

4. **Selection Authority Gap**
   - No one/nothing selects decision for execution
   - If client-provided, trust boundary broken

5. **Validation Authority Gap**
   - No validation of decision→execution match
   - No scope/target checking

**VERDICT: BINDING AUTHORITY GAP - CRITICAL**
