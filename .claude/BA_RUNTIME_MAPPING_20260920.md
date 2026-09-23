# BINDING AUTHORITY RUNTIME MAPPING

**Based on:** Human Gate decisions BA-01 through BA-05  
**Date:** 2026-09-20  
**Status:** MAPPING ONLY (No implementation)

---

## A. EXISTING RUNTIME MAPPING

### Point 1: decision_id INPUT (BA-01 Implementation)

**Current flow:**
```
MCP Request
  ├─ params.arguments = { "decision_id": "DC_20260920_001", ... }
  ↓
mocka_mcp_server.py:1220 dispatch
  ├─ params.get("arguments") → args dict
  ↓
mocka_mcp_server.py:541 execute_tool(name, args, req_id)
  ├─ args passed without modification
  ↓
mocka_mcp_server.py:567 _governance.before_tool(name, args)
  ├─ args dict received
  ├─ [HERE: decision_id could be extracted]
  ↓
structural/governance_pipeline.py:91 before_tool()
  ├─ args passed but NOT EXAMINED
  ├─ [CODE WOULD EXTRACT HERE: args.get("decision_id")]
```

**File/Line where decision_id can be received:**
- **PRIMARY:** `mocka_mcp_server.py:567` (call site)
- **SECONDARY:** `structural/governance_pipeline.py:91` (function)
- **TERTIARY:** `structural/governance_pipeline.py:100-104` (args logged to working memory)

**Status:** EXISTING - args dict flows through; NO EXTRACTION YET

---

### Point 2: Canonical Runtime Boundary (BA-04 Validation)

**Current location:**
```
structural/governance_pipeline.py:91-136
  ├─ Line 91: def before_tool(self, tool_name: str, args: dict)
  ├─ Line 96: grounding = self._refresh_grounding()
  ├─ Line 98: mode = self.tm.detect_mode(tool_name, args)
  ├─ Line 100-104: wm.update() with args
  ├─ Line 106: checklist = self.reasoning.enforce_pre_answer_checklist()
  ├─ Line 109-120: GL7 dry_run checks (non-READ_ONLY tools)
  ├─ Line 122: allowed = (not aborts) and checklist.ok
  ├─ Line 123-128: reason assignment
  ├─ [HERE: BA-04 validation would inject before line 122]
  ├─ Line 130-136: return GovernanceDecision()
```

**BA-04 validation insertion point:**
```
Line ~115-120 (before line 122 allow calculation):
  
# [NEW] BA-04 Binding Authority Validation
if tool_name not in READ_ONLY_TOOLS:
    decision_id = args.get("decision_id")
    if decision_id:
        # Perform BA-04 validation:
        # 1. Decision exists
        # 2. Decision status = Active
        # 3. approved_by exists
        # 4. Authority valid
        # 5. Execution exists (req_id)
        # 6. Tool matches
        # 7. Scope matches
        # 8. Signature valid
        # 9. Temporal valid
        # 10. Fresh enough
        # 11. revocation_status
        # 12. immutable_hash_match
        if validation_fails:
            aborts.append("BA04_VALIDATION_FAILED")
```

**Status:** EXISTING - before_tool() is unified authority point; VALIDATION NOT YET IMPLEMENTED

---

## B. BA-03 FIELD MAPPING (Identity Fields)

### Where each required field can be obtained:

| Field | Source | File/Line | Existing? | Accessible? |
|-------|--------|-----------|-----------|-------------|
| **decision_id** | args.get("decision_id") | [Caller provides] | N | YES - in args |
| **req_id** | execute_tool() param | mocka_mcp_server.py:541 | Y | **NO** - not passed to before_tool() |
| **tool_name** | execute_tool(name) | mocka_mcp_server.py:541 | Y | YES - before_tool(tool_name) |
| **session_id** | Global SESSION_ID | mocka_mcp_server.py:88 | Y | **NO** - not passed to before_tool() |
| **actor identity** | args.get("author") | mocka_mcp_server.py:751 | Y | YES - in args for mocka_write_event |
| **approved_by** | decision_ledger.jsonl | data/decisions/ | Y | **NO** - must lookup via decision_id |
| **execution_target** | Not in schema | N/A | N | MISSING |
| **scope** | Not in decision schema | N/A | N | MISSING |
| **binding_timestamp** | System time | Runtime | Y | YES - can generate at validation |
| **binding_signature** | Can compute | HMAC(fields) | N | YES - can generate at validation |
| **chain_sequence_id** | Not in system | N/A | N | MISSING |
| **parent_binding_id** | Not in system | N/A | N | MISSING |
| **policy_version** | Not in system | N/A | N | MISSING |

**Field Gap Analysis:**
- ✓ **EXISTING in args:** decision_id, tool_name, actor identity (partial)
- ✓ **EXISTING in context:** req_id, session_id, execution_timestamp
- ✗ **NOT PASSED TO before_tool:** req_id, session_id
- ✗ **MISSING FROM SCHEMA:** execution_target, scope
- ✗ **NOT IN SYSTEM:** chain_sequence_id, parent_binding_id, policy_version

---

## C. BA-04 VALIDATION MAPPING

### Where each validation can be performed:

| Validation | Check Type | Where | Existing | Implementation |
|-----------|-----------|-------|----------|---|
| **Decision exists** | Lookup | `_read_decision(decision_id)` | YES | Add call to governance/write_path/runtime/adapter.py:26 |
| **Status = Active** | Field check | decision.status | YES | Check record["status"] == "Active" |
| **approved_by exists** | Field check | decision.approved_by | YES | Check record["approved_by"] |
| **Authority valid** | Policy check | N/A | NO | MISSING - no authority policy defined |
| **Execution exists** | Lookup | request_executions table | YES | Add SQL query in execute_tool or before_tool |
| **Tool matches** | Field check | record["target_tool"] == tool_name | NO | MISSING - target_tool not in schema |
| **Scope matches** | Field check | decision.scope contains tool | NO | MISSING - scope not in schema |
| **Signature valid** | Crypto check | HMAC verify | NO | MISSING - signature not generated |
| **Temporal validity** | Time range | approved_at <= now <= expiry | PARTIAL | expiry not in schema |
| **Temporal freshness** | Age check | now - approved_at < MAX_AGE | PARTIAL | MAX_AGE not defined |
| **revocation_status** | Field check | record["revocation_status"] | NO | MISSING - field not in schema |
| **immutable_hash_match** | Hash verify | HMAC(identity_fields) | NO | MISSING - hash not computed |

**Implementation readiness:**
- ✓ **Can implement immediately:** Decision exists, Status, approved_by
- ⚠ **Can implement with req_id passing:** Execution exists
- ✗ **Requires schema changes:** target_tool, scope, revocation_status
- ✗ **Requires new computation:** Signature, immutable_hash
- ✗ **Requires policy definition:** Authority validation

---

## D. BA-05 IMMUTABILITY MAPPING

### How Immutable/Mutable fields can be enforced:

| Field | Category | How to enforce | Where | Existing |
|-------|----------|---|---|---|
| **decision_id** | Immutable | Primary key in binding record | Binding Ledger | N/A - new table |
| **req_id** | Immutable | Primary key in binding record | Binding Ledger | N/A - new table |
| **tool_name** | Immutable | Part of immutable_hash | Binding signature | NO |
| **approved_by** | Immutable | Part of immutable_hash | Binding signature | NO |
| **execution_target** | Immutable | Part of immutable_hash | Binding signature | NO |
| **scope** | Immutable | Part of immutable_hash | Binding signature | NO |
| **binding_timestamp** | Immutable | Set at binding creation | Binding Ledger | N/A - new table |
| **binding_signature** | Immutable | Can't be regenerated | Binding Ledger | N/A - new table |
| **execution_status** | Mutable | Updated in execution log | request_executions | YES - already mutable |
| **retry_count** | Mutable | Incremented per attempt | Binding Ledger | N/A - new table |
| **last_verified_at** | Mutable | Updated each verification | Binding Ledger | N/A - new table |

**Enforcement mechanism:**
- Immutable fields: stored in immutable_hash at binding creation
- Mutable fields: stored separately, can be updated without breaking binding
- Invalidation: if immutable_hash doesn't match current state, binding is INVALID

---

## E. MISSING COMPONENTS

### Components required by BA-03/BA-04/BA-05 but not existing:

**1. Data Structure for Binding Record**
```
Required fields (from BA-03):
  - decision_id (from args)
  - req_id (from execute_tool param)
  - tool_name (known)
  - session_id (from runtime)
  - actor_identity (from args or default)
  - approved_by (from decision_ledger)
  - execution_target (NOT IN SCHEMA)
  - scope (NOT IN SCHEMA)
  - binding_timestamp (system generated)
  - binding_signature (HMAC computed)
  - chain_sequence_id (NOT DEFINED)
  - parent_binding_id (NOT DEFINED)
  - policy_version (NOT DEFINED)

Storage: BINDING LEDGER (NEW TABLE NEEDED)
```

**2. Decision Schema Additions**
```
Current decision_ledger.jsonl fields:
  - decision_id ✓
  - title, context, decision ✓
  - alternatives, rationale, impact ✓
  - approved_by, approved_at ✓
  - status ✓
  - related_events, related_documents ✓
  - supersedes, superseded_by ✓

Missing (for BA-04 validation):
  - execution_target (which tool/action this authorizes)
  - scope (what subset of executions)
  - revocation_status (can be revoked?)
  - expiry_date (temporal limit)
  - immutable_hash (for tamper detection)
  - policy_version (which policy governs this)
```

**3. Binding Signature Computation**
```
Required by BA-05 (immutable_hash_match):
HMAC-SHA256(
  "DC_BINDING_v1" +
  decision_id +
  req_id +
  tool_name +
  approved_by +
  execution_target +
  scope +
  binding_timestamp
)
Currently: NOT COMPUTED ANYWHERE
```

**4. Authority Policy Definition**
```
Required by BA-04 (Authority validation):
Policy for determining if approved_by is authoritative.
Currently: NO POLICY EXISTS
Options:
  A. Hardcoded list of authorized approvers
  B. Role-based (approver has "authority" role)
  C. Delegation chain (approver was approved by someone)
  D. Dynamic (lookup in separate authority ledger)
```

**5. req_id Transport to before_tool()**
```
Currently: req_id available in execute_tool() but NOT passed to before_tool()
Required by: BA-03 field mapping, BA-04 execution validation
Solution: Pass req_id as parameter or store in context
```

---

## F. MINIMAL IMPLEMENTATION BOUNDARY

### Single point where all BA-01~BA-05 can be implemented:

**Location:** `structural/governance_pipeline.py:91-136`  
**Function:** `GovernancePipeline.before_tool(tool_name: str, args: dict)`

**What needs to happen:**
```python
def before_tool(self, tool_name: str, args: dict) -> GovernanceDecision:
    # Lines 96-120: Existing GL1-GL7 checks (unchanged)
    
    # [NEW BA-01/BA-04/BA-05 INJECTION POINT]
    # Line ~115 (before line 122 allow calculation)
    
    # BA-01: Extract decision_id from args (Caller selection input)
    decision_id = args.get("decision_id") if tool_name not in READ_ONLY_TOOLS else None
    
    # BA-04: Validate decision binding
    if decision_id:
        validation_result = self._validate_binding_authority(
            decision_id=decision_id,
            tool_name=tool_name,
            args=args,
            req_id=???  # <-- PROBLEM: not available here
        )
        if not validation_result.approved:
            aborts.append(f"BA_VALIDATION_FAILED: {validation_result.reason}")
    
    # BA-05: Immutability enforcement (implicit in validation_result.signature_valid)
    
    # Line 122: Original allow calculation (unchanged)
    allowed = (not aborts) and checklist.ok
```

**Constraint:** req_id is not currently passed to before_tool()  
**Required change:** Signature modification OR context injection

---

## G. EXISTING CODE CHANGES REQUIRED

### What must be modified vs. what can be added:

| Component | Change type | File | Line | Scope | Justification |
|-----------|---|---|---|---|---|
| **before_tool() signature** | MODIFY | structural/governance_pipeline.py | 91 | Add req_id param | BA-04 requires req_id to validate execution exists |
| **execute_tool() call** | MODIFY | mocka_mcp_server.py | 567 | Pass req_id | To supply req_id to before_tool() |
| **GovernanceDecision** | EXTEND | structural/governance_pipeline.py | 64 | Add binding_id field | To return binding record ID for logging |
| **_validate_binding_authority()** | ADD | structural/governance_pipeline.py | ~200 | New function | BA-04 validation logic |
| **_lookup_decision()** | ADD | structural/governance_pipeline.py | ~150 | New function | Decision lookup from ledger |
| **Binding Ledger table** | CREATE | data/ | new | request_binding_ledger.jsonl | Storage for BA-02 binding records |
| **Decision schema** | EXTEND | docs/ | DECISION_LEDGER_SCHEMA_v1.md | Add 6 fields | execution_target, scope, revocation_status, expiry_date, immutable_hash, policy_version |
| **GL7 executor** | UNCHANGED | structural/execution_governance.py | 222 | No change | BA-04 validation separate layer |
| **READ_ONLY_TOOLS** | UNCHANGED | structural/governance_pipeline.py | 33 | No change | BA-01 skips READ_ONLY by design |

**Minimal changes approach:**
- ✓ **Can add new functions without changing existing GL layers**
- ✓ **Can create new Binding Ledger parallel to existing Decision Ledger**
- ✓ **Can extend GovernanceDecision to include binding metadata**
- ✗ **Cannot avoid: passing req_id to before_tool()** (requires signature change)
- ✗ **Cannot avoid: extending decision schema** (BA-04 validation requires target/scope/revocation fields)

---

## SUMMARY: MINIMAL IMPLEMENTATION BOUNDARY

**Single point of enforcement:** `structural/governance_pipeline.py:91 before_tool()`

**Execution flow:**
```
User submits MCP request with:
  args["decision_id"] = "DC_20260920_001"
  
↓ (BA-01: Caller selection input captured)

execute_tool(name, args, req_id="REQ-...")
  ├─ Pass req_id to before_tool()
  
↓ (BA-02: Runtime receives both selection + execution ID)

before_tool(tool_name, args, req_id)
  ├─ Extract decision_id from args
  ├─ Call _validate_binding_authority(decision_id, req_id, ...)
  │  ├─ Check BA-04 all 12 validation points
  │  ├─ If ALL valid: generate binding signature (BA-05 immutable)
  │  ├─ If ANY invalid: fail
  ├─ If valid: record to Binding Ledger (BA-02 generation)
  ├─ If valid: return allowed=True (or add to aborts)

↓ (BA-03/BA-04/BA-05 satisfied in single function)

execute_tool continues to actual tool execution
```

**VERIFICATION REQUIRED BEFORE IMPLEMENTATION:**
1. BA-03 field mapping complete (all 12 fields obtainable)
2. BA-04 validation logic defined (all 12 checks specified)
3. BA-05 immutability enforcement chosen (signature vs. other)
4. req_id passing design approved
5. Decision schema extension approved
6. Binding Ledger design approved
7. Authority policy defined (how to validate approved_by)

