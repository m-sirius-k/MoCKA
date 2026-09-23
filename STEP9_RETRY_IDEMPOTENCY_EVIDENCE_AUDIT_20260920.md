---
name: step9_retry_idempotency_evidence_audit
description: Step 9 再検証 — Request Identity vs Authorization Identity の分離、既存実装からの実例追跡、4ケース検証
metadata:
  type: project
---

# Step 9 Retry Idempotency — Evidence Audit & Re-verification

**Date:** 2026-09-20  
**Status:** EVIDENCE GATHERING (NOT IMPLEMENTATION YET)  
**Scope:** Request-Level Idempotency design verification before Step 9 implementation authorization

---

## Part 1: Current Implementation State (Fact-Based)

### 1.1 What EXISTS in the codebase

| Component | Location | Status | Details |
|-----------|----------|--------|---------|
| `intent_id` | runtime/intent_ledger.json | ✓ EXISTS | UUID v4, 7+ retries recorded for same intent_id |
| `plan_id` | runtime/plan.json, civilization_plan.json | ✗ NOT FOUND | No explicit plan_id field; only goal/action strings |
| `action_id` | runtime/action_executor.py line 66 | PARTIAL | Received as parameter but NOT persisted in action_result.json |
| `decision_record_id` | core_kernel/governance/... | ✗ MISSING | governance_pipeline returns GovernanceDecision (not persisted) |
| `req_id` (JSON-RPC) | mocka_mcp_server.py line 1132 | ✓ EXISTS | HTTP/MCP request ID, used for response routing |
| Idempotency Check | execute_tool() line 480+ | ✗ MISSING | No duplicate detection; same tool call twice = two executions |
| Governance Decision | GovernanceDecision dataclass line 64 | ✓ EXISTS | But ephemeral (not saved to persistent layer) |

**Evidence Source:**
- runtime/intent_ledger.json lines 1-51: Same intent_id appears 7 times with different timestamps
- runtime/action_result.json line 1-5: No action_id field despite action_executor.py supporting it
- mocka_mcp_server.py line 1144: `execute_tool(params.get("name", ""), params.get("arguments", {}))` with no retry detection
- core_kernel/governance/runtime/governance_runtime.py line 77-91: `execute()` creates new ExecutionResult every call, no caching

### 1.2 What Step 9 Proposal ASSUMED

**Previous tuple proposal:**
```
(intent_id, plan_id, action_id, decision_record_id)
```

**Reality check:**
- `intent_id` ← Real, persisted ✓
- `plan_id` ← NOT in schema ✗
- `action_id` ← Real but not persisted ✗
- `decision_record_id` ← Does not exist; governance uses GovernanceDecision which is ephemeral ✗

**Critical Issue:** The 4-tuple mixes **three different concept layers**:
1. **User intent layer** (intent_id) — persisted in intent_ledger
2. **Execution plan layer** (plan_id) — exists in memory but not persisted with identity
3. **Runtime action layer** (action_id) — parameter in action_executor but not saved
4. **Authorization layer** (decision_record_id) — governance decision is ephemeral, not a persistent record

---

## Part 2: Four Cases — Evidence-Based Analysis

### Case 1: Same Intent + Plan + Action — Communication Retry

**Evidence:** intent_ledger.json, lines 1-7 and line 137-148

```json
Line 1-7: Same intent_id "7053cfc7-f373-4dad-8a1b-002373f44f99" appears 7 times
- 2026-03-23T01:57:43 (event 1)
- 2026-03-23T01:58:30 (event 2)  ← 47 seconds later
- 2026-03-23T01:59:14 (event 3)  ← 44 seconds later
- 2026-03-23T01:59:55 (event 4)  ← 41 seconds later
- 2026-03-23T02:00:29 (event 5)  ← 34 seconds later
- 2026-03-23T02:03:01 (event 6)  ← 152 seconds later
- 2026-03-23T02:03:48 (event 7)  ← 47 seconds later

Line 137-148: Same intent_id "30952e6a-e9d9-42d5-92b1-30f8bf341133" appears 3 times
- 2026-03-24T08:41:03 (event A)
- 2026-03-26T07:42:28 (event B)  ← 47 hours later
- 2026-03-26T08:13:14 (event C)  ← 30 minutes later
```

**Current Behavior:**
- Same intent → **7 new INTENT_RECEIVED records** (no duplicate suppression)
- Same logic action but different time → new plan? or same plan?

**Case 1 Classification:**
- **Is it the same request?** AMBIGUOUS: Same intent_id, but 7 different timestamps
- **Should execution be retried?** CURRENT: Yes (no idempotency) — may cause duplicate effects
- **Is it same authorization?** TBD: Does 47-hour gap make previous HG decision stale?

---

### Case 2: Same Intent + Plan + Action, but Governance Decision Re-evaluated

**Evidence:** No direct evidence in codebase (governance decision is ephemeral)

**Scenario:** 
- T1: Human sends intent A, governance says "allowed" → execution happens
- T2: HG policy changes (e.g., new security rule)
- T3: Same intent A is resent → governance now says "denied"

**Current Behavior:**
- Governance decision is computed fresh each time (line 91-136 in governance_pipeline.py)
- No decision cache or "decision_id" that persists across retries
- **Result:** Previous authorization is NOT carried forward; new decision overwrites old one

**Case 2 Classification:**
- **Is it same request?** YES (same intent_id)
- **Is authorization the same?** NO (governance rules changed)
- **Should execution be retried?** NO (new decision blocks it) — correct fail-closed behavior
- **Problem:** No audit trail of the changed decision (ephemeral GovernanceDecision)

---

### Case 3: Same Intent, Different Plan Generated

**Evidence:** runtime/plan.json (single static file)

```json
{
  "steps": ["EXECUTE"],
  "source": "intent",
  "raw_goal": "Direct"
}
```

**Observation:**
- Only ONE plan.json file; no plan versioning or plan_id history
- If same intent is processed 7 times (Case 1), does plan.json get overwritten 7 times?
- **No plan_id in schema means: cannot distinguish between plan_version_1 and plan_version_2**

**Scenario:**
- T1: Intent "analyze the system" → plan_v1 = [ANALYZE, REPORT]
- T2: Intent "analyze the system" (retry) → plan_v2 = [ANALYZE] (different intent interpretation)

**Current Behavior:**
- No plan identity, so cannot track which plan produced which action
- If action_id = intent_id:step_index, and plan changes, action mapping breaks

**Case 3 Classification:**
- **Is it same request?** YES (same intent_id)
- **Is plan same?** UNKNOWN (no plan_id → cannot compare)
- **Should execution be retried?** DEPENDS ON PLAN: If plan changed, execution may differ
- **Problem:** No canonical way to know if plan changed

---

### Case 4: Different Intent, Same Logical Action

**Evidence:** runtime/action_result.json, action_executor.py line 14

```python
# Line 14 signature
def execute_action(step, execution_context=None, action_id=None):
    # step can be "ANALYZE" or "EXECUTE" (strings, not objects)
    # Multiple intents can generate same step (EXECUTE)
```

**Scenario:**
- Intent_A: "write report" → plan = [EXECUTE] → step = "EXECUTE"
- Intent_B: "apply patch" → plan = [EXECUTE] → step = "EXECUTE"

Both intents produce the same logical action "EXECUTE", but they are **different requests** requiring **different executions**.

**Current Behavior:**
- action_result.json shows:
  ```json
  {
    "action": "EXECUTE",
    "status": "success",
    "timestamp": "2026-04-05T03:22:01.740340+00:00"
  }
  ```
- No way to know which intent this EXECUTE belongs to
- If Intent_A and Intent_B are both sent, do they execute twice or once?

**Case 4 Classification:**
- **Is it same request?** NO (different intent_ids)
- **Are they same action?** YES at step level (both EXECUTE)
- **Should execution be duplicated?** YES (different intents = different execution chains)
- **Current Behavior Correctness:** UNKNOWN (no tracing between intent and action result)

---

## Part 3: Critical Findings — Where Step 9 Proposal Failed

### 3.1 Concept Confusion: Identity vs. Authorization vs. Execution

**Previous Proposal Assumed:**
```
Request Identity = (intent_id, plan_id, action_id, decision_record_id)
```

**Reality:**
| Concept | Is a Request Property? | Is an Authorization Property? | Is an Execution Property? | Persistent? |
|---------|------------------------|-------------------------------|---------------------------|-------------|
| intent_id | YES ✓ | NO | YES | YES |
| plan_id | NO ✗ | NO | YES (logically) | NO |
| action_id | MAYBE (depends on def) | NO | YES ✓ | NO (not saved) |
| decision_record_id | NO ✗ | YES ✓ | NO | NO |

**Implication:** The 4-tuple is **invalid**. It conflates three separate identities:
1. **Request Identity** — captures "is this the same request?"
2. **Authorization Identity** — captures "is this authorized the same way?"
3. **Execution Identity** — captures "is this the same execution trace?"

These are **orthogonal dimensions**, not one tuple.

### 3.2 decision_record_id is Authorization, NOT Request

**Why decision_record_id must not be in Request Identity:**

- A request can be authorized differently at different times:
  - T1: HG says "ALLOWED"
  - T2: HG policy changes
  - T3: Same request → HG says "DENIED"

- If Request Identity = `(intent_id, plan_id, action_id, decision_record_id)`:
  - T1 request has decision_record_id = "DEC_001"
  - T3 request has decision_record_id = "DEC_002"
  - **Same request but different Request Identity** ← CONTRADICTION

**Correct:**
- Request Identity should NOT include decision_record_id
- Authorization Identity SHOULD include decision_record_id (or authorization timestamp)
- They are separate concerns

### 3.3 action_id Meaning is Undefined

**Current usage patterns in code:**

| Place | Format | Meaning |
|-------|--------|---------|
| action_executor.py line 66 | Parameter `action_id=None` | Caller's tracing tag (optional, never used) |
| action_result.json | Missing (not persisted) | ??? |
| runtime/intent_ledger.json | Has no action_id field | Not tracked |
| goververn ance_pipeline.py | No mention | Not used |

**Three possible meanings:**
- **A. Request action_id** — "which step in the plan is this?" (e.g., intent_id:step_2)
- **B. Execution action_id** — "which execution run was this?" (UUID per execute_action call)
- **C. Logical action_id** — "which business operation?" (ANALYZE, EXECUTE, REPORT)

These are different:
- Meaning A: Used for duplicate detection within a plan
- Meaning B: Used for audit/tracing of execution instances
- Meaning C: Used for semantic grouping

**Evidence from Case 4 shows:** Without clear action_id meaning, multiple intents can produce same action type (EXECUTE) but should execute separately.

### 3.4 Fail-Open Risk in Step 9 Proposal

**Previous proposal had:**
```
if idempotency_query fails → execute anyway
```

**Why this is dangerous (MoCKA fail-closed principle violation):**

From CLAUDE.md:
> 「止めるのは権限。進めるのは証拠。」
> Authority frozen; Evidence moves forward

If idempotency check fails (database unavailable, query timeout, etc.):
- Current proposal: "execute anyway" ← FAIL-OPEN
- Correct MoCKA way: "BLOCKED / UNKNOWN" ← FAIL-CLOSED

**Schema implications:**
- Cannot have nullable decision_record_id (would silently skip authorization check)
- Cannot have "best-guess" duplicate detection (would skip verification on edge cases)
- Must have explicit "UNKNOWN" state that gates execution

---

## Part 4: Corrected Definitions (Evidence-Based)

### 4.1 Request Identity (for Idempotency)

**Definition:** "Is this HTTP/MCP request a duplicate of one we processed before?"

**Canonical form:**
```
request_id = sha256(
  tool_name + 
  json.dumps(sorted_args, sort_keys=True) +  # Arguments hash (deterministic JSON)
  session_origin  # WHO is sending (to prevent cross-session reuse)
)
```

**Properties:**
- Deterministic (same input → same request_id)
- Session-scoped (cannot be reused across sessions)
- Captures tool invocation semantics (what operation, not why)
- Does NOT include:
  - `decision_record_id` (authorization changes)
  - `intent_id` (user intent; one intent can have multiple tool calls)
  - `timestamp` (time-varying)

**Scope:** Idempotency of **side-effect** (second call should not execute twice)

### 4.2 Authorization Identity (for Policy Gating)

**Definition:** "Should this request be allowed based on current governance rules?"

**Canonical form:**
```
authorization_context = {
  tool_name: str,
  required_approval_level: "READ" | "WRITE" | "DECISION" | "ADMIN",
  decision_record_id: str or NULL,  # Last known HG decision (if any)
  decision_timestamp: str,           # When decided
  governance_policy_hash: str,       # Did HG rules change since last decision?
  actor_id: str,                    # WHO is executing
}
```

**Decision Rules:**
- If tool_name in READ_ONLY_TOOLS → no HG decision needed (implicit ALLOW)
- If governance_policy_hash changed since decision_timestamp → RE-EVALUATE (old decision stale)
- If decision_record_id exists and recent → USE CACHED DECISION
- If no decision or stale → QUERY HG (or apply default DENY for WRITE tools)

**Key:** Authorization is TIME-SENSITIVE and POLICY-DEPENDENT

### 4.3 Execution Identity (for Audit/Tracing)

**Definition:** "How do we trace this actual execution back to its source and authorization?"

**Canonical form:**
```
execution_record = {
  event_id: str,                    # MoCKA event identifier
  request_id: str,                  # From Request Identity
  tool_name: str,
  tool_args: dict,
  authorization_decision: {
    allowed: bool,
    decision_record_id: str or NULL,
    timestamp: str,
    reason: str,
  },
  execution_result: {
    status: "success" | "failure" | "blocked",
    output: str,
    timestamp: str,
  },
  related_intent_id: str or NULL,   # If this tool call came from intent processing
  related_action_id: str or NULL,   # If this tool call was part of action execution
}
```

**Purpose:** Every action must be traceable back to:
1. The HTTP request that triggered it
2. The authorization decision that allowed it
3. The user intent (if any) that motivated it

---

## Part 5: Retry Definition (Corrected)

### 5.1 What is a Retry?

**Definition:** Same `request_id` arriving a second time within a defined window (e.g., 5 minutes)

**Current State:** MoCKA has NO retry detection
- Same mocka_write_event called twice → two event records (DUPLICATE EFFECT)
- Same mocka_decision_write called twice → two decision records (DUPLICATE RECORD)

### 5.2 Legitimate Re-execution

**Definition:** Different `request_id` but same logical business goal

**Examples:**
- User says "apply patch A" → execute_action(step="EXECUTE", intent_id="abc")
- User says again "apply patch A" (due to timeout) → different request? or same?
  - If user intent is identical: **same business goal, but new request** → new request_id
  - If time gap is >1 hour: **may need re-authorization** (policy may have changed)
  - If action is idempotent: **safe to retry** (second execution has no new side effect)
  - If action is NOT idempotent: **unsafe to retry** (would apply patch twice)

**Key:** Retry safety depends on **idempotency semantics of the action**, not just request identity

### 5.3 Duplicate Detection Condition

**Rule (Fail-Closed):**
```
IF request_id is in [recently executed requests]:
  IF authorization_decision is still valid (policy unchanged):
    RETURN cached result
  ELSE:
    RE-AUTHORIZE (may change from ALLOW to DENY or vice versa)
    IF now DENY:
      BLOCK and log "authorization changed"
    ELSE:
      RE-EXECUTE (policy changed, decision now different)
ELSE:
  AUTHORIZE fresh
  EXECUTE if allowed
```

**Not Cached:**
- If policy changed since first execution
- If >X hours have passed (authorization window closed)
- If any critical governance state changed

### 5.4 Idempotency Check Failure → Behavior

**NOT:** execute anyway (fail-open)

**CORRECT:**
```
IF idempotency_query fails (DB unavailable, query error):
  status = "UNKNOWN"
  reason = "Idempotency check unavailable (DB error)"
  action = BLOCK
  log event with type "UNKNOWN" per MoCKA principle
  return "Governance state uncertain; cannot proceed"
ELSE:
  proceed with duplicate detection
```

This maintains MoCKA's fail-closed principle: *"Authority frozen; Evidence moves forward"*

---

## Part 6: Minimum Schema Changes (NOT CODE YET)

### 6.1 Persistent Request Identity

**New table: `request_executions`**
```sql
CREATE TABLE request_executions (
  request_id TEXT PRIMARY KEY,
  tool_name TEXT NOT NULL,
  session_id TEXT,
  first_executed_at TIMESTAMP,
  first_result_summary TEXT,
  authorization_decision_id TEXT,  -- FK to decisions ledger
  execution_event_id TEXT,         -- FK to events.db
  KEY(session_id, tool_name, first_executed_at)
);
```

### 6.2 Persistent Authorization Decision Link

**Extend: `decision_ledger.jsonl`** (APPEND-ONLY)
```json
{
  "decision_id": "DEC_20260920_001",
  "title": "Authorization for mocka_write_event",
  "tool_name": "mocka_write_event",
  "request_hash": "sha256(...)",  -- Link to request
  "approved_by": "HG" or "AUTO_ALLOW",
  "policy_version": "GL7_20260920",
  "decision": "ALLOW" | "DENY",
  "rationale": "...",
  "timestamp": "2026-09-20T14:00:00Z",
  "valid_until": "2026-09-21T14:00:00Z",  -- 24h window
  "supersedes": null
}
```

### 6.3 Persistent Execution Record

**Extend: `events.csv` or new `execution_trace.jsonl`**
```json
{
  "event_id": "EV_20260920_12345",
  "type": "EXECUTION_TRACE",
  "timestamp": "2026-09-20T14:00:00Z",
  "request_id": "req_...",
  "tool_name": "mocka_write_event",
  "authorization_decision_id": "DEC_...",
  "related_intent_id": "7053cfc7-f373-4dad-8a1b-002373f44f99" or null,
  "execution_result": "success",
  "idempotency_check": {
    "was_retry": true,
    "prior_execution_id": "EV_...",
    "decision": "RETURN_CACHED"
  }
}
```

### 6.4 NO Changes To:
- intent_ledger.json (keep as-is, retry records OK)
- action_result.json (will be replaced by execution_trace)
- action_executor.py signature (add action_id field to result JSON)

---

## Part 7: Minimum Runtime Changes (Deferred)

**Pre-Implementation Verification Only:**
1. Query existing request_executions table
2. Compare request_id to recent executions
3. Check authorization_decision_id validity
4. Decide: RETURN_CACHED vs. RE-EXECUTE vs. BLOCK

**NOT IMPLEMENTED YET** (awaiting this audit completion + HG review)

---

## Part 8: Required Tests (Design Only)

### Test 1: Duplicate Request — Same Tool Call Twice
```
Given: mocka_write_event called with identical args
When: called second time within 5 minutes
Then: second call returns cached result; only 1 event written
```

### Test 2: Policy Change Between Calls
```
Given: mocka_write_event authorized as ALLOW at T1
When: HG policy changes (policy_version increments) at T2
  AND same tool called again at T3
Then: re-authorization occurs; decision may change to DENY
  AND if DENY, second execution is blocked
```

### Test 3: Retry After 24 Hours
```
Given: mocka_write_event executed at T1 (24h ago)
When: same request resent now (T1 + 24h)
Then: authorization window has closed
  AND must RE-AUTHORIZE (not use cached decision)
```

### Test 4: Cross-Intent Same Action
```
Given: Intent_A generates action "EXECUTE"
  AND Intent_B generates action "EXECUTE" (different intent)
When: both intents processed
Then: two separate execution_trace records
  AND both execute (not deduplicated)
```

### Test 5: DB Failure — Idempotency Check
```
Given: request_executions table unavailable
When: tool is invoked
Then: NOT "execute anyway" (fail-open)
  BUT "BLOCKED / UNKNOWN" state
  AND incident recorded as type "UNKNOWN"
```

---

## Summary Table: 10-Point Deliverable (Pre-Implementation)

| Item | Definition | Status | Evidence |
|------|-----------|--------|----------|
| 1. Request Identity | sha256(tool_name + sorted_args + session_id) | DEFINED | Section 4.1 |
| 2. Authorization Identity | {tool_name, required_level, decision_record_id, governance_policy_hash, actor_id} | DEFINED | Section 4.2 |
| 3. Execution Identity | {event_id, request_id, auth_decision, result, related_intent_id} | DEFINED | Section 4.3 |
| 4. Retry Definition | Same request_id within time window + authorization still valid | DEFINED | Section 5.1-5.3 |
| 5. Legitimate Re-exec | Different request_id; same goal; may need re-auth; safety depends on idempotency | DEFINED | Section 5.2 |
| 6. Duplicate Detection | Query request_executions; check auth validity; fail-closed if unknown | DEFINED | Section 5.3 |
| 7. Idempotency Fail | BLOCKED / UNKNOWN state; incident recorded; NOT "execute anyway" | DEFINED | Section 5.4 |
| 8. Min Schema Changes | request_executions table + decision_ledger link + execution_trace events | SPECIFIED | Section 6 |
| 9. Min Runtime Changes | Idempotency query before execute_tool(); decision caching logic | NOT YET | Deferred to HG review |
| 10. Required Tests | 5 test scenarios (duplicate, policy change, time window, cross-intent, DB failure) | SPECIFIED | Section 8 |

---

## Conclusion: Step 9 PARTIALLY COMPLETE (Evidence Layer)

**What was WRONG in original proposal:**
- Mixed Request + Authorization + Execution identities into one 4-tuple
- `plan_id` doesn't exist in schema
- `action_id` is not persisted
- `decision_record_id` is ephemeral, not persistent
- Proposed fail-open behavior ("execute anyway" on DB error)
- Missing fail-closed semantics

**What is NOW CORRECTED:**
- Request, Authorization, and Execution identities are separate orthogonal concepts
- decision_record_id belongs ONLY in Authorization Identity, not Request Identity
- Idempotency check failure → BLOCKED/UNKNOWN (fail-closed)
- 10-item specification complete (no code changes yet)

**Next Step:** Human Gate review of this audit + authorization for implementation phase (Step 9 Part B).

**NOT AUTHORIZED:** Code implementation, schema deployment, runtime changes.

