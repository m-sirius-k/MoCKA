# SYSTEM-LEVEL COMMITMENT HG AUDIT
## KUROKO PC 第5弾 提出前監査
**Date:** 2026-09-21  
**Audit Status:** REVIEW ONLY (No Implementation)  
**Source Documents:**
- MOCKA_RUNTIME_BINDING_INVESTIGATION_20260921_PHASE6_FINAL.md
- MOCKA_BINDING_DESIGN_DECISION_INPUT_20260921.md

---

## PHASE 1: EVIDENCE CONSISTENCY CHECK

### Commitment Identity (req_id)

| Element | Status | Evidence | Classification |
|---------|--------|----------|-----------------|
| Generation | VERIFIED | mocka_mcp_server.py:1271 `req_id = body.get("id")` | VERIFIED |
| Storage (idempotency) | VERIFIED | request_executions table created line 556-563 | VERIFIED |
| Lifecycle | VERIFIED | _record_request_execution() line 609 | VERIFIED |
| Persistence (execution-level) | PARTIAL | req_id in before_tool() context (line 621), but not returned | PARTIAL |

**Finding:** req_id exists as request-level identifier but is NOT persisted with execution outcome.

---

### Decision Identity (decision_id)

| Element | Status | Evidence | Classification |
|---------|--------|----------|-----------------|
| Generation | VERIFIED | _next_decision_id() format DC_YYYYMMDD_NNN | VERIFIED |
| Storage | VERIFIED | decision_ledger.jsonl append-only JSONL | VERIFIED |
| Authority Reference | VERIFIED | governance_pipeline._read_decision() line 91-112 | VERIFIED |
| Execution Link | NOT FOUND | No decision_id ↔ execution_id record | NOT VERIFIED |
| Event Link | PARTIAL | Companion event created (optional, line 1144-1168), decision_id in tags | PARTIAL |

**Finding:** Decision records exist and are validated, but execution binding is missing.

---

### Event Identity (event_id)

| Element | Status | Evidence | Classification |
|---------|--------|----------|-----------------|
| Generation | VERIFIED | event_gate._next_event_id() line 34-43 format E{YYYYMMDD}_{micros}{random} | VERIFIED |
| Storage | VERIFIED | events table (SQLite) | VERIFIED |
| Request Link | PARTIAL | request_id in gate_payload (mocka_mcp_server line 836), but persistence unverified | PARTIAL |
| Decision Link | PARTIAL | Companion event mechanism, not automatic | PARTIAL |

**Finding:** Event persistence is verified, but request_id persistence in SQLite is unverified.

---

### Authority Validation

| Element | Status | Evidence | Classification |
|---------|--------|----------|-----------------|
| Decision Ledger Lookup | VERIFIED | governance_pipeline._read_decision() | VERIFIED |
| Status Check | VERIFIED | Line 151 "status != Active" | VERIFIED |
| Block Recording | VERIFIED | _record_governance_block() creates event | VERIFIED |
| Execution Binding | NOT FOUND | Block event not linked back to decision_id | NOT VERIFIED |

**Finding:** Authority enforcement exists, but failure recording is not bound to decision.

---

## PHASE 2: CONCEPT SEPARATION AUDIT

### Three Concepts: Approval, Decision, Commitment

| Concept | Current Implementation | Separated? |
|---------|------------------------|-----------|
| **Approval** | HG decision → Decision Ledger entry (approved_by, approved_at fields) | YES |
| **Decision** | decision_ledger.jsonl record (alternatives, rationale, decision field) | YES |
| **Commitment** | System-level: req_id → decision → execution → event | PARTIAL |

**Analysis:**

- **Approval:** VERIFIED - Human Gate provides approved_by/approved_at to Decision record
- **Decision:** VERIFIED - Decision Ledger captures decision logic (alternatives, rationale)
- **Commitment:** PARTIAL - Request binds to decision (via args.get("decision_id")), but execution outcome is not bound back

**Status:** PARTIAL - All three concepts exist separately, but Commitment lacks execution binding.

---

## PHASE 3: IDENTIFIER BOUNDARY AUDIT

### ID Cross-Reference Map

| ID Type | Owner | Storage | Lifecycle | Cross-Ref | CRITICAL |
|---------|-------|---------|-----------|-----------|----------|
| req_id | JSON-RPC client | request_executions | T_request only | → before_tool only | ✗ Not returned |
| decision_id | System | decision_ledger.jsonl | Persistent | ← args input; → tags | ⚠ One-way only |
| event_id | System | events table | Persistent | ← generated; → result | ✓ |
| execution_id | **MISSING** | **N/A** | **N/A** | **N/A** | ✗✗ CRITICAL |
| trace_id | integrity layer | events.trace_id | Persistent (hash chain) | ← sig; → related_event_id | ⚠ Event-chain only |
| tool_call_id | **NOT FOUND** | **N/A** | **N/A** | **N/A** | **N/A** |

### Must NOT Be Confused

```
DO NOT confuse:
  - decision_id (authority source) ↔ event_id (audit trail)
    They are independent unless manually linked via related_events[]
  
  - req_id (request) ↔ execution_id (MISSING)
    They should be 1:1 but no binding mechanism exists
  
  - event_id (singular) ↔ trace_id (chain)
    trace_id links events chronologically but contains no decision context
```

**Finding:** ID namespace is mostly clean, but execution_id absence creates ambiguity.

---

## PHASE 4: RUNTIME IMPACT BOUNDARY

### Potential Impact Points (No Implementation Proposed)

| Component | Current State | Potential Impact Zone | Evidence |
|-----------|---------------|-----------------------|----------|
| **before_tool()** | Validates decision_id from args | Would need to receive execution_id from caller or generate it | governance_pipeline.py:114-193 |
| **execute_tool()** | No execution_id generation | Adding execution_id generation here (line ~610) affects: idempotency table, result binding, response format | mocka_mcp_server.py:595-1260 |
| **governance_pipeline** | Records decision_id only | If execution binding added, would need decision_id ↔ execution_id mapping | governance_pipeline.py:198 after_tool() |
| **Event Writer (GATE)** | request_id in payload (unverified storage) | If execution_id added, would need to flow through gate_payload | event_gate.py:75, 836 |
| **Decision Writer** | Companion event (optional) | If execution binding added, companion event should link to execution_id | mocka_mcp_server.py:1144-1168 |

### Boundaries NOT Crossed (By Design)

- No changes to Decision Ledger schema
- No changes to Event Ledger schema
- No changes to Integrity Classification schema
- No changes to governance policy enforcement logic
- All bindings are **observational** (audit), not **enforcement** (blocking)

---

## PHASE 5: HUMAN GATE READINESS JUDGMENT

### Overall Status

**READY WITH CONDITIONS**

### Conditions for Approval

**Condition 1:** Execution Binding Scope Clarification
- Is binding for "traceability" (audit log) or "enforcement" (auto-escalate)?
- **Evidence Needed:** Clarify intended use case
- **Current State:** Gap exists, but unclear if critical for current phase

**Condition 2:** Request_ID Persistence Verification (Critical)
- **Question:** Is request_id actually stored in SQLite events table?
- **Evidence Needed:** Execute: `SELECT request_id FROM events WHERE event_id = 'E20260705_001'`
- **Impact if Unverified:** Options B & C for binding design are weakened; Option A becomes mandatory

**Condition 3:** Commitment Definition Boundary
- **Question:** Does "System-level Commitment" include consequential decision binding?
- **Evidence Needed:** Clarify scope: Decision → Execution → Event only, or Event → Next Decision also?
- **Current State:** Event → Consequence is NOT automatic (caller re-injects decision_id)

**Condition 4:** Companion Event Linking Policy
- **Question:** Should companion events (created by mocka_decision_write) include request_id?
- **Evidence Needed:** Rationale for current design (request_id currently NOT in companion event payload)
- **Current State:** Gap exists at mocka_mcp_server.py:1148-1161

### Not Ready For

❌ **Implementation without design decision:**
- Which binding option (A/B/C from MOCKA_BINDING_DESIGN_DECISION_INPUT_20260921.md)?
- Implementation authority boundary (before_tool vs. execute_tool vs. event_gate)?

❌ **Ledger schema change without approval:**
- request_id field in events table needs verification before assuming
- decision_id in events table requires explicit schema change decision

❌ **Consequence automation without specification:**
- Automatic consequence linking (Event → Next Decision) is NOT currently designed

---

## CRITICAL GAPS SUMMARY

### Unresolved Identities

| Identity | Current | Needed | Blocker? |
|----------|---------|--------|----------|
| execution_id | MISSING | REQUIRED for traceability | YES for Options A/B |
| request_id persistence | IN PAYLOAD | VERIFICATION | YES for Options B/C |
| companion_event request_id | NOT INCLUDED | CLARIFICATION | NO (optional) |
| consequence_link | NOT AUTOMATIC | CLARIFICATION | NO (design choice) |

### Unresolved Boundaries

| Boundary | Current | Question | Blocker? |
|----------|---------|----------|----------|
| Decision → Execution | ONE-WAY (args input only) | Should HG provide execution_id back? | YES |
| Execution → Event | PARTIAL (request_id unverified) | Reverse lookup design? | YES |
| Event → Consequence | NO AUTOMATIC LINK | Scope of "System-level Commitment"? | CONDITIONAL |
| Companion Event | OPTIONAL | Include request_id? | NO (enhancement) |

---

## RECOMMENDATION FOR HUMAN GATE

**Status:** EVIDENCE-READY FOR DECISION  
**Requirement:** Answer Condition 1-4 above before implementation

**Proposed HG Decision Points:**

1. **Binding Strategy:** Select Option A/B/C (from MOCKA_BINDING_DESIGN_DECISION_INPUT_20260921.md)
2. **Scope:** Decision → Execution → Event only, or include consequence linking?
3. **Verification:** Confirm request_id SQLite persistence before finalizing design
4. **Authority Boundary:** Which phase/phase component owns execution_id generation?

---

**Audit Complete:** Investigation → Design Input → Readiness → HG Decision  
**Investigation Status:** ✅ COMPLETE  
**Implementation Status:** ⏸️ AWAITING HG DECISION  
**Human Gate Readiness:** 🟡 READY WITH CONDITIONS

