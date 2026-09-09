# Implementation Sketches for Central Runtime Loop Closure (D6-D12)

## Document Purpose

This document provides **Design/Planning Phase sketch outlines** for implementing D6-D12 Closure Design. These are NOT implementation authorization yet (DP-3), but rather "construction blueprints" to inform Human Gate DP-1 (Design Adoption) judgment.

**Status**: Design/Planning Phase → Support Material for DP-1 Decision

---

## IS-1: Governance → Memory Binding Implementation Sketch

### Code Change Locations (Static Path Review)

**1. /collect Endpoint (app.py:1009-1072)**

Current code (line 1062):
```python
kernel_result = _get_relay_kernel().ingest(_relay_normalized)
# return value DISCARDED
```

Required change sketch:
```python
kernel_result = _get_relay_kernel().ingest(_relay_normalized)
action = kernel_result.get("action", {})

# NEW: Capture policy decision
policy_decision = kernel_result.get("policy", {})

# NEW: Create CanonicalDecisionRecord
gov_decision = {
    "canonical_id": f"GD_{int(time.time())}_{hash(str(policy_decision))[:8]}",
    "source_policy_id": "policy-v1",
    "source_event_id": normalized.get("event_id"),
    "governance_version": "2026-09-09",
    
    "decision_status": policy_decision.get("decision", "unknown"),
    "confidence": policy_decision.get("confidence", 0.0),
    "reasoning": policy_decision.get("reason", ""),
    
    "authorization_status": "PENDING_HUMAN_REVIEW",  # Must be explicit
    "authorizing_actor": None,
    "authorization_timestamp": None,
    
    "persistence_status": "NOT_WRITTEN",
    "written_to_events_db": False,
    "event_id_in_db": None,
    
    "unknown_preservation": has_unknown_state(normalized),
    "not_proven_preservation": False,
}

# NEW: Write governance decision to events.db via EventBuffer
try:
    operational_event = {
        "what_type": "governance_decision_event",
        "where_component": "relay",
        "why_purpose": f"Governance decision from policy.evaluate()",
        "who_actor": "relay_kernel",
        "raw": gov_decision,
    }
    get_buffer().push(operational_event)
    gov_decision["persistence_status"] = "WRITTEN"
except Exception as e:
    return {"status": "governance_bind_failed", "error": str(e)}

# CONTINUE: existing action routing logic
if action["action"] == "STORE_EVENT":
    # ... existing code ...
```

**Impact**: RelayKernel.ingest() return value → CanonicalDecisionRecord → events.db (typed governance_decision_event)

---

**2. MCPBridge Activation (relay/mcp_bridge.py:13-50)**

Current state: Dead code (never instantiated)

Required change sketch:
```python
# Uncomment and activate in app.py or relay_kernel.py

mcp_bridge = MCPBridge()

# In handle() method, add:
if kernel_result.get("policy"):
    gov_decision = _create_canonical_decision_record(kernel_result["policy"], source_event_id)
    result = mcp_bridge.handle("relay_kernel", {
        "kernel_result": kernel_result,
        "governance_decision": gov_decision,
    })
```

**Impact**: Alternative pathway for governance decision persistence (ensures idempotency via MCPBridge.process_buffered_event())

---

**3. MemoryContext.load() Enhancement (phi_os/context/memory_context.py:88-200)**

Current code (line 107-119):
```python
rows = conn.execute(
    "SELECT event_id, what_type, why_purpose, who_actor FROM events "
    "ORDER BY rowid DESC LIMIT ?", (limit_events,)
).fetchall()
```

Required change sketch:
```python
# Replace string search with typed event structure
def _load_governance_decisions(self, limit=10) -> None:
    if not _DB_PATH.exists():
        return
    try:
        conn = sqlite3.connect(str(_DB_PATH))
        conn.row_factory = sqlite3.Row
        
        # NEW: Query by what_type='governance_decision_event'
        rows = conn.execute(
            "SELECT event_id, raw_json FROM events "
            "WHERE what_type = 'governance_decision_event' "
            "ORDER BY rowid DESC LIMIT ?",
            (limit,)
        ).fetchall()
        
        self.governance_decisions = []
        for r in rows:
            try:
                decision_record = json.loads(r["raw_json"])
                self.governance_decisions.append({
                    "event_id": r["event_id"],
                    "decision_status": decision_record.get("decision_status"),
                    "authorization_status": decision_record.get("authorization_status"),
                    "confidence": decision_record.get("confidence"),
                    "reasoning": decision_record.get("reasoning"),
                    "unknown_preservation": decision_record.get("unknown_preservation"),
                    "timestamp": r["event_id"][:12],
                })
            except json.JSONDecodeError:
                pass
        
        conn.close()
    except Exception:
        pass
```

**Impact**: Memory reads typed governance_decision_event from events.db (not string search)

---

### Idempotency Implementation

**Sketch**: Keyed by (source_event_id, governance_version)

```sql
-- NEW: Create unique index for idempotency
CREATE UNIQUE INDEX IF NOT EXISTS idx_governance_decision_idempotency
ON events(json_extract(raw_json, '$.source_event_id'), json_extract(raw_json, '$.governance_version'))
WHERE what_type = 'governance_decision_event';

-- Check before insert
SELECT COUNT(*) FROM events
WHERE what_type = 'governance_decision_event'
AND json_extract(raw_json, '$.source_event_id') = ?
AND json_extract(raw_json, '$.governance_version') = ?
```

**Impact**: Duplicate governance decisions prevented (same source_event + version = skip write)

---

## IS-2: WorkingContext Assembly Implementation Sketch

### Code Insertion Point: phi_os/context/working_context.py (NEW FILE)

```python
class WorkingContext:
    def __init__(self, memory: MemoryContext):
        self.memory = memory
        self.five_w1h = memory.five_w1h
        self.recent_decisions = memory.governance_decisions[:5]  # Latest 5
        
        # CRITICAL: Separate authorized from pending
        self.authorized_actions = [
            d for d in self.recent_decisions
            if d.get("authorization_status") == "APPROVED"
        ]
        self.pending_reviews = [
            d for d in self.recent_decisions
            if d.get("authorization_status") == "PENDING_HUMAN_REVIEW"
        ]
        self.unknown_preservation_alerts = [
            d for d in self.recent_decisions
            if d.get("unknown_preservation") == True
        ]
    
    def can_execute_action(self, action_type: str) -> bool:
        # FAIL-CLOSED: If ANY pending or unknown preservation, return False
        if self.pending_reviews or self.unknown_preservation_alerts:
            return False
        if not self.authorized_actions:
            return False
        return True
    
    def get_active_authorization(self) -> dict | None:
        return self.authorized_actions[0] if self.authorized_actions else None
```

**Impact**: Memory → WorkingContext → AI Execution decision point enforces fail-closed semantics

---

## IS-3: Outcome → New Event → Re-entry Implementation Sketch

### Code Insertion Point: interface/outcome_recorder.py (NEW FILE)

```python
class OutcomeRecorder:
    def record_outcome(self, action_id: str, action_type: str, result_code: int, result_data: dict) -> dict:
        outcome_event = {
            "what_type": "action_outcome_event",
            "where_component": "outcome_recorder",
            "why_purpose": f"Outcome of action {action_id}",
            "who_actor": f"AI:{self.system_id}",
            "raw": {
                "action_id": action_id,
                "action_type": action_type,
                "result_code": result_code,
                "result_data": result_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        }
        
        # NEW: Re-entry to /collect (E6a: closing the loop)
        response = requests.post(
            "http://localhost:5000/collect",
            json=outcome_event,
            timeout=5,
        )
        
        if response.status_code != 200:
            return {"status": "reentry_failed", "error": response.text}
        
        # NEW: Return value re-enters Relay.ingest() → policy.evaluate() → new governance decision
        return {
            "status": "reentry_success",
            "outcome_event_id": outcome_event.get("event_id"),
            "new_governance_decision": response.json().get("policy"),
        }
```

**Impact**: E5 (Outcome) → E6 (New Event) → E6a (Re-entry) cycle closes Central Runtime Loop

---

## IS-4: Events.db Schema Extension Sketch

### NEW Table/Column Additions

```sql
-- Extend events table to support typed governance decisions
ALTER TABLE events ADD COLUMN IF NOT EXISTS what_type TEXT;  -- Already exists
ALTER TABLE events ADD COLUMN IF NOT EXISTS raw_json TEXT;   -- For JSON storage

-- Create governance_decision_event index for O(1) reads
CREATE INDEX IF NOT EXISTS idx_governance_decision_type
ON events(what_type) WHERE what_type = 'governance_decision_event';

-- Create idempotency index
CREATE UNIQUE INDEX IF NOT EXISTS idx_governance_decision_idempotency
ON events(
    json_extract(raw_json, '$.source_event_id'),
    json_extract(raw_json, '$.governance_version')
)
WHERE what_type = 'governance_decision_event';

-- Create authorization status index for fast query of pending reviews
CREATE INDEX IF NOT EXISTS idx_governance_authorization_status
ON events(json_extract(raw_json, '$.authorization_status'))
WHERE what_type = 'governance_decision_event';
```

**Impact**: Efficient typed event storage + fast queries for governance decisions

---

## IS-5: Fail-Closed Rule Implementation Sketch

### Rule 1-7 Enforcement Points

**Rule 1: UNKNOWN Preservation**
```python
def preserve_unknown_state(upstream_state: dict) -> bool:
    has_unknown = any(v == "UNKNOWN" for v in upstream_state.values())
    return has_unknown

decision_record["unknown_preservation"] = preserve_unknown_state(normalized)
# If True, MUST remain True in downstream processing
```

**Rule 3: Persistence Failure Blocks**
```python
try:
    get_buffer().push(governance_decision_event)
except Exception as e:
    # DO NOT retry silently
    # DO NOT default to "accept"
    return {"status": "governance_bind_failed", "error": str(e), "escalate": True}
    # Escalate to Human Gate
```

**Rule 7: Authorization Record Before Execution**
```python
# Write authorization record to decision_ledger BEFORE executing action
if working_context.get_active_authorization():
    decision_ledger.record({
        "action_id": action_id,
        "authorization_timestamp": datetime.now(timezone.utc).isoformat(),
        "authorizing_actor": "AI:{system}",
    })
else:
    # DO NOT execute if no authorized_actions
    return {"status": "execution_blocked_no_authorization"}
```

---

## IS-6: C1-C16 Verification Instrumentation Sketch

### Instrumentation Points for Runtime Verification

**C1: Immutable canonical_id**
```python
# At decision creation:
ASSERT decision_record["canonical_id"].startswith("GD_")
ASSERT len(decision_record["canonical_id"]) == 32  # GD_ + timestamp + hash

# In test: verify immutability
original_id = decision_record["canonical_id"]
# ... various operations ...
ASSERT decision_record["canonical_id"] == original_id
```

**C2: Idempotency by (source_event_id, governance_version)**
```python
# Test scenario:
event1 = create_event(id="E123")
decision1 = policy.evaluate()
decision1_db = query_events("governance_decision_event")

# Same event re-processed
decision2 = policy.evaluate()
decision2_db = query_events("governance_decision_event")

ASSERT len(decision1_db) == len(decision2_db)  # No duplicate
```

**C6: Governance decision initiates from policy.evaluate()**
```python
# Instrument policy.evaluate() entry/exit
@instrument_decision_source
def evaluate(self, state: dict) -> dict:
    log.info("DECISION_SOURCE: policy.evaluate() invoked")
    result = self._decide(state)
    log.info(f"DECISION_SOURCE: policy.evaluate() returned {result['decision']}")
    return result
```

**C16: Loop re-entry within 5sec**
```python
# At outcome_recorder.record_outcome():
reentry_time_start = time.time()
response = requests.post("http://localhost:5000/collect", ...)
reentry_time_elapsed = time.time() - reentry_time_start

ASSERT reentry_time_elapsed < 5.0, "Re-entry exceeded 5sec RT window"
log.info(f"Loop re-entry: {reentry_time_elapsed:.2f}sec")
```

---

## Risk Assessment (Design/Planning Horizon)

### RA-1: Return Value Capture Risk
**Risk**: If app.py:1062 return value capture fails, governance decision lost.
**Mitigation**: MCPBridge as backup pathway (fallback if /collect pathway fails).
**Implementation Effort**: LOW (already coded, just needs activation).

### RA-2: Events.db Schema Compatibility
**Risk**: Adding governance_decision_event type could conflict with existing what_type values.
**Mitigation**: Schema migration script with backward-compatibility check.
**Implementation Effort**: MEDIUM (schema migration, index creation).

### RA-3: Idempotency Key Collisions
**Risk**: Hash collision in canonical_id (GD_{timestamp}_{hash}).
**Mitigation**: Use SHA256(policy_decision + source_event_id) instead of simple hash.
**Implementation Effort**: LOW (cryptographic hash function).

### RA-4: Memory Load Performance
**Risk**: Querying 10+ governance decisions on every MemoryContext.load() could be slow.
**Mitigation**: Pagination + caching (load only latest 5, cache in session).
**Implementation Effort**: LOW (standard pagination pattern).

### RA-5: Authorization Status Race Condition
**Risk**: Between decision write and action execution, authorization could change.
**Mitigation**: Read authorization_status immediately before execution; fail if PENDING.
**Implementation Effort**: LOW (simple timestamp check).

---

## Rollback Strategy (Design/Planning Horizon)

### Rollback Scenario 1: Governance Decision Persistence Failure

**Trigger**: Events.db write fails; workflow blocked.

**Rollback Steps**:
1. Revert /collect endpoint code change (restore line 1062 to original)
2. MCPBridge remains disabled (no governance decision writes)
3. MemoryContext.load() reverts to string search (original behavior)
4. Central Runtime Loop closure attempt paused pending DP-1 rejection or redesign

**Effort**: LOW (code revert only, no migration needed)

---

### Rollback Scenario 2: Events.db Schema Migration Failure

**Trigger**: ALTER TABLE fails; governance_decision_event column not created.

**Rollback Steps**:
1. SQL migration script detects failure; stops
2. No changes persisted (atomic transaction)
3. Original events.db schema unchanged
4. Designer notifies Human Gate of schema incompatibility

**Effort**: MEDIUM (schema recovery; may require backup restore)

---

### Rollback Scenario 3: Authorization Loop Creates Infinite Recursion

**Trigger**: Outcome → New Event → Re-entry creates new governance decision → triggers new action → loop never ends.

**Rollback Steps**:
1. Set max_loop_depth = 3 (prevent recursion > 3 cycles)
2. If depth exceeded, escalate to Human Gate
3. Disable outcome_recorder re-entry temporarily
4. Manual review of decision logic required

**Effort**: MEDIUM (loop detection code; requires manual analysis)

---

## Next Steps After DP-1 Approval

| Decision Point | Triggered By | Next Deliverable |
|---|---|---|
| DP-1: Design Adoption | Human Gate approval | Implementation Planning (DP-2) |
| DP-2: Implementation Planning | DP-1 ADOPT | IS-1 through IS-6 → Detailed Code Changes |
| DP-3: Implementation Authorization | DP-2 AUTHORIZE | Pull Request with C1-C16 instrumentation |
| DP-4: Deployment Authorization | DP-3 AUTHORIZE | Test environment deployment + logs |
| DP-5: Loop Closure Verification | DP-4 AUTHORIZE + evidence | C1-C16 runtime verification report |

---

## Document Status

**Purpose**: Design/Planning Phase support material for DP-1 (Design Adoption) decision
**Completeness**: Sketch-level (NOT implementation authorization)
**Approval**: Awaiting Human Gate DP-1 decision
**Next Gate**: If DP-1 APPROVED → Implementation Planning authorization (DP-2)

---

**Version**: v1.0
**Finalized**: 2026-09-09
**Prepared for**: Human Gate DP-1 Decision Support
