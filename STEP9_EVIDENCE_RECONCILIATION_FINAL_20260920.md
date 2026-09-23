---
name: step9_evidence_reconciliation_final
description: Step 9 — Evidence vs Proposed Design Separation (No Code Changes)
metadata:
  type: project
---

# Step 9 Evidence Reconciliation — Final Report

**Date:** 2026-09-20  
**Scope:** Separate EXISTING/VERIFIED evidence from PROPOSED design  
**Status:** Evidence gathering only (NO CODE CHANGES, NO IMPLEMENTATION)

---

## 1. VERIFIED Existing Identities

### 1.1 intent_id
- **Status:** EXISTING / VERIFIED ✓
- **Source:** runtime/intent_ledger.json
- **Format:** UUID v4
- **Persistence:** JSONL append-only ledger
- **Evidence:** 41 events in intent_ledger; intent IDs repeatedly referenced
- **Used for:** Intent tracking, event correlation

### 1.2 plan_id
- **Status:** EXISTING / PARTIALLY VERIFIED ⚠
- **Source:** 
  - `runtime/execution_context.py` line 21: `plan_id: Optional[str] = None`
  - `runtime/goal_to_plan.py` line 65: `plan_id = _compute_plan_id(intent_id, text, steps)`
  - Line 72: `"plan_id": plan_id` (written to plan.json)
- **Format:** `hashlib.sha256(...).hexdigest()[:16]` (deterministic hash)
- **Generation:** `_compute_plan_id(intent_id, goal_text, step_sequence)`
- **Should be persisted:** Yes (line 78-79 writes to plan.json)
- **Actually persisted:** UNCLEAR (see Section 3)
- **Used for:** Plan identification in ExecutionContext

### 1.3 action_id
- **Status:** EXISTING / PARTIALLY VERIFIED ⚠
- **Source:**
  - `runtime/execution_context.py` line 22: `action_id: Optional[str] = None  # Per-action; format: {intent_id}:{step_index}`
  - `runtime/goal_to_plan.py` line 68: `action_ids = [f"{intent_id}:{i}" for i in range(len(steps))]`
- **Format:** `{intent_id}:{step_index}` (e.g., "45ad3f68-...:0")
- **Persistence:** In plan.json as action_ids array
- **Semantic:** Action position within a plan (not execution identity)
- **7-occurrence interpretation:** See Section 4

### 1.4 decision_record_id
- **Status:** EXISTING / PARTIALLY VERIFIED ⚠
- **Source:** `runtime/execution_context.py` line 25
- **Format:** Optional string (not defined in ExecutionContext)
- **Persistence:** Stored in ExecutionContext.to_dict() (line 81)
- **Actual storage:** UNKNOWN (see Section 6)
- **Used for:** Link to governance decision

### 1.5 execution_id
- **Status:** EXISTING / VERIFIED ✓
- **Source:** `runtime/execution_context.py` line 36
- **Format:** Optional string
- **Semantics:** Unique identifier for each execution attempt
- **Persistence:** In ExecutionContext.to_dict()

### 1.6 governance_decision
- **Status:** EXISTING / VERIFIED ✓
- **Source:** `runtime/execution_context.py` line 26
- **Format:** `PASS | WARNING | FAIL`
- **Persistence:** In ExecutionContext

---

## 2. PARTIALLY VERIFIED Identities

### 2.1 hg_decision (Human Gate decision)
- **Status:** EXISTING / PARTIALLY VERIFIED ⚠
- **Source:** `runtime/execution_context.py` line 30
- **Format:** `AUTHORIZED | AUTHORIZED_WITH_CONDITIONS | DENIED`
- **Persistence:** In ExecutionContext
- **Actual usage:** UNKNOWN (no HG instance found in runtime/)
- **Issue:** Defined but no evidence of actual HG integration

### 2.2 evidence_hash
- **Status:** EXISTING / PARTIALLY VERIFIED ⚠
- **Source:** `runtime/execution_context.py` line 45
- **Format:** Hash (not defined)
- **Semantics:** Link to formal evidence record
- **Persistence:** In ExecutionContext
- **Actual computation:** UNKNOWN

---

## 3. CONFLICT: plan_id Contradiction

**The Issue:**
```
Expected: runtime/plan.json should contain plan_id (per goal_to_plan.py line 72)
Actual:   runtime/plan.json DOES NOT contain plan_id
```

**Evidence:**
- `goal_to_plan.py` line 72: `"plan_id": plan_id` is written
- `runtime/plan.json` actual content: NO plan_id field
- Last modified: 2026-04-05 12:22 (stale)

**Interpretation:**
- **A. Implementation not executed:** update_plan_from_goal() was never called after goal_to_plan.py was written
- **B. Data stale:** plan.json is outdated; actual current plan_id exists elsewhere
- **C. Code and data diverged:** goal_to_plan.py was written but plan.json was not updated

**Resolution:** EVIDENCE GAP — plan_id exists in code but not confirmed in runtime data

**Status:** CANNOT CONFIRM plan_id as "persisted identity" without seeing actual execution

---

## 4. intent_ledger 7-Occurrence Re-Analysis

### 4.1 Raw Facts
```
intent_id: 7053cfc7-f373-4dad-8a1b-002373f44f99
Count: 7 entries in intent_ledger.json
Event type: All INTENT_RECEIVED
Timestamps:
  1. 2026-03-23T01:57:43.610151Z
  2. 2026-03-23T01:58:30.823177Z  (47 seconds later)
  3. 2026-03-23T01:59:14.829698Z  (44 seconds later)
  4. 2026-03-23T01:59:55.704811Z  (41 seconds later)
  5. 2026-03-23T02:00:29.266902Z  (34 seconds later)
  6. 2026-03-23T02:03:01.153192Z  (152 seconds later)
  7. 2026-03-23T02:03:48.985988Z  (47 seconds later)
```

### 4.2 Possible Interpretations

| Interpretation | Evidence | Likelihood |
|---|---|---|
| **Same request retry** | Time gaps of 30-150 seconds suggest network retries | POSSIBLE but NOT VERIFIED |
| **User resending same intent** | No way to distinguish retry from new submission | POSSIBLE but NOT VERIFIED |
| **Plan generation loop** | Goal→Plan conversion triggered 7 times | POSSIBLE but NOT VERIFIED |
| **Bug: duplicate event logging** | No evidence of deduplication logic | POSSIBLE but NOT VERIFIED |

### 4.3 Missing Evidence for "Retry" Classification
To classify these 7 occurrences as **retry**, we would need:
- [ ] Request-level ID (HTTP request ID, JSON-RPC id, etc.)
- [ ] HTTP response codes for attempts 2-7 (if any failed)
- [ ] Application-level logs showing "retry attempt N"
- [ ] Network-level evidence (TCP retransmit timings)
- [ ] Comparison of identical tool calls with exact same arguments

**Current Status:** 7 occurrences of SAME INTENT_ID with different timestamps
**Cannot determine:** Whether this is RETRY or SEQUENTIAL_SUBMISSION

---

## 5. PROPOSED Design Elements (Not in existing implementation)

### 5.1 Request Identity
```
sha256(tool_name + sorted_args + session_id)
```
- **Status:** PROPOSED (not in existing code)
- **Rationale:** For idempotency at tool invocation level
- **Prerequisite:** Session tracking (not found in runtime/)
- **Evidence:** NO existing `session_id` in ExecutionContext

### 5.2 Authorization Identity
```
{
  tool_name,
  required_level ("READ"|"WRITE"|"DECISION"|"ADMIN"),
  decision_record_id (or NULL),
  policy_hash,
  actor_id
}
```
- **Status:** PARTIALLY IN CODE, PARTIALLY PROPOSED
- **Existing fields:** tool_name, decision_record_id
- **Proposed fields:** policy_hash, required_level, actor_id
- **Evidence:** NO policy_hash computation in existing code
- **Evidence:** NO actor_id tracking in ExecutionContext

### 5.3 Fail-Closed on Idempotency Check Failure
```
If idempotency_query fails (DB unavailable):
  status = BLOCKED / UNKNOWN
  → Do NOT execute
```
- **Status:** PROPOSED (aligns with MoCKA principle)
- **Existing equivalent:** No idempotency check exists
- **Alignment check:** MoCKA principle "Authority frozen; Evidence moves forward" ✓

---

## 6. UNKNOWN / EVIDENCE GAP

### 6.1 execution_log
- **Expected:** Mentioned in ExecutionContext docstring line 3
- **Found:** NO file matching "*execution*log*" in runtime/
- **Status:** UNKNOWN

### 6.2 Actual storage of ExecutionContext
- **Exists:** `ExecutionContext.to_dict()` method (line 75-95)
- **Stored to:** UNKNOWN (no storage code found)
- **Query:** Where are ExecutionContext objects persisted?

### 6.3 Governance decision persistence
- **Exists:** `governance_decision` field in ExecutionContext
- **Computed:** In governance_pipeline.py (GovernanceDecision)
- **Persisted:** UNKNOWN (GovernanceDecision is ephemeral)
- **Query:** Is GovernanceDecision saved to execution_log or other storage?

### 6.4 policy_hash computation
- **Proposed in Step 9:** Track when HG policy changes
- **Found in code:** NO policy versioning mechanism
- **Status:** UNKNOWN if policy hash is available

### 6.5 Request-level deduplication
- **Proposed in Step 9:** Detect retries via request_id
- **Found in code:** NO request tracking before tool execution
- **Status:** Must be implemented new (not existing)

---

## 7. Retry Evidence Gap

**What would prove "these 7 intent_id occurrences are retries":**

1. ✗ Request-level ID (absent)
2. ✗ HTTP request correlation (no HTTP-level logs visible)
3. ✗ Tool call signature comparison (no tool invocation log)
4. ✗ Failure codes triggering retry (no retry logic visible)
5. ✗ Exponential backoff pattern (inconsistent gaps: 47, 44, 41, 34, 152, 47 seconds)

**Current evidence:** Time gaps suggest possible retry behavior, but NO DEFINITIVE PROOF

---

## 8. Request Identity — Can Existing Mechanisms Be Reused?

### 8.1 Existing candidates
| Mechanism | Status | Can be used for request_id? |
|---|---|---|
| JSON-RPC `id` (mocka_mcp_server.py line 1132) | ✓ EXISTS | MAYBE (requires HTTP request logging) |
| tool_name + args hash | ✓ IMPLEMENTABLE | YES (but requires pre-compute) |
| session_id | ✗ MISSING | NO (not tracked in ExecutionContext) |
| intent_id | ✓ EXISTS | NO (too coarse; multiple tool calls per intent) |

### 8.2 Most viable existing foundation
- **Tool name** ✓ always available
- **Tool arguments** ✓ always available
- **Session tracking** ✗ NOT TRACKED
- **Request routing** ✓ MCP server has req_id

**Recommendation:** Use JSON-RPC id + tool_name + args_hash as composite key, but requires:
- Logging each request with its req_id
- Preserving req_id through execution chain
- Adding session_id to ExecutionContext

---

## 9. Are New Identities Truly Necessary?

### Analysis
1. **intent_id** — Already exists; differentiates user goals
2. **plan_id** — Partially implemented; should be persisted (not retrofitted)
3. **action_id** — Already exists; differentiates steps within plan
4. **execution_id** — Already exists; differentiates each execution attempt

**Gap:** Between request arrival and execution, **no idempotency check** exists

### Verdict
- **New identity truly needed:** Request-level ID (for deduplication)
- **Existing identities sufficient for:** Execution tracing, authorization decisions
- **Partially broken:** plan_id (defined but not persisted)

---

## 10. Step 9 FINAL STATUS

### What IS verified:
✓ intent_id persisted in intent_ledger  
✓ action_id generated from plan  
✓ ExecutionContext defined with full identity chain  
✓ governance_decision computed  
✓ hg_decision structure exists (but integration unknown)  

### What is CONFLICTED:
⚠ plan_id defined in code but NOT found in runtime/plan.json  
⚠ 7 intent_id occurrences: unclear if retry or sequential submission  

### What is MISSING:
✗ execution_log (referenced but not found)  
✗ Request-level idempotency check  
✗ Session tracking  
✗ Policy hash / policy versioning  
✗ actor_id tracking  
✗ Persistence layer for ExecutionContext  

### What is PROPOSED (Step 9):
→ Request Identity as SHA256 hash  
→ Fail-closed idempotency check  
→ Authorization Identity including policy versioning  
→ Execution trace events  

### Authorization Status
**Implementation:** NOT AUTHORIZED (awaiting conflict resolution)  
**Reason:** plan_id persistence conflict + missing execution_log  

### Blockers for Implementation
1. **Resolve plan_id conflict:** Is plan.json stale or is code not executing?
2. **Find or create execution_log:** Where should ExecutionContext be persisted?
3. **Add session tracking:** ExecutionContext lacks session_id field
4. **Implement policy versioning:** Needed for policy_hash computation
5. **Verify HG integration:** Is hg_decision actually populated?

---

## Summary

| Category | Finding | Evidence |
|----------|---------|----------|
| **Existing Identities** | intent_id ✓, plan_id ⚠, action_id ✓, execution_id ✓ | Code + partial data |
| **Proposed Identities** | request_id (NEW), authorization_identity (NEW) | Design spec only |
| **Data Conflicts** | plan_id in code but not in runtime data | Code vs runtime mismatch |
| **Missing Evidence** | How 7 intent_ids are used (retry? sequential?) | Ambiguous timestamps |
| **Implementation Ready** | NOT YET — blockers remain | Multiple evidence gaps |

**No code changes, no schema deployment, no runtime changes at this time.**

