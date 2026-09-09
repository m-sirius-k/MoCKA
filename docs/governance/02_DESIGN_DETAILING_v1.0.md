# Design Detailing v1.0 — Phase 1 Normative Baseline Concretization

**Stream 2 Completion**  
**Investigation Date:** 2026-09-09  
**Basis:** Route Inventory (Stream 1) + Phase 1 Human Gate Decisions  
**Scope:** 12 design elements translating Phase 1 baseline into concrete specifications  
**Authorization:** HG-PHASE3-PREREQUISITE-WORK-AUTHORIZATION  

---

## Design Element 1: Approval Confirmation State — Operational Definition

**Phase 1 Baseline:** "承認確定に到達する全経路" (all routes reaching approval confirmation state)

**Concrete Definition:**
An operation reaches "approval confirmation state" when it causes a durable state change in the events database (mocka_events.db) or decision ledger (decision_ledger.jsonl). This includes:
- Event insertion into events table (any write_sqlite() call)
- Event buffering for Gate ingestion (any get_buffer().push() call)
- Decision ledger entry (any mocka_decision_write() call)
- Integrity classification (any mocka_integrity_write() call)
- Audit task creation (cross_audit.create_task() call)
- Proposal recording (proposal_schema.record() call)

**Evidence Basis:** Route Inventory sections B, C, EventBuffer Mechanism, Decision Ledger & Approval Confirmation identify all write paths. Each constitutes "approval confirmation" (state transition that requires authorization).

**NOT Included:** In-memory operations (buffer queue append), read-only HTTP responses, logging-only operations, computations without DB persistence.

---

## Design Element 2: Route B Enforcement Insertion Points — Specific Functions & Line Ranges

**Phase 1 Baseline:** "Flask/Application routes must have pre-execution authorization check before state-changing operations"

**Concrete Enforcement Locations (8 Flask Routes):**

| Route ID | File | HTTP Route | Entry Function | State-Change Call | Insert Line | Enforcement Point |
|---|---|---|---|---|---|---|
| B1 | interface/handshake.py | POST /api/handshake | handshake_post() | get_buffer().push() | 164 | Before line 164 |
| B2 | interface/ai_session.py | GET /api/session/start | start_session() | get_buffer().push() | 128 | Before line 128 |
| B3 | interface/reflection_engine.py | POST /reflection/generate | generate_reflection() | get_buffer().push() | 123 | Before line 123 |
| B4 | interface/commission_manager.py | GET /commission/list | list_commissions() | get_buffer().push() | 81 | Before line 81 |
| B5 | interface/context_composer.py | GET /context/compose | compose_context() | get_buffer().push() | 146 | Before line 146 |
| B6 | interface/essence_resolver.py | (embedded) | resolve_essence() | get_buffer().push() | 55 | Before line 55 |
| B7 | interface/cross_audit.py | POST /cross_audit/task | _record_to_main_db() | get_buffer().push() | 298 | Before line 298 |
| B8 | interface/proposal_schema.py | N/A (library) | _write_to_event_ledger() | get_buffer().push() | 167 | Before line 167 |

**Enforcement Pattern:**
```
Route entry (Flask handler or internal function)
  → Authorization decision check (before state-change)
    → Proceed with operation
    → Record authorization linkage (decision_id → event_id)
  → Or DENY with error
```

**Decision Rule:** If authorization is DENIED or UNKNOWN, event must not be pushed to buffer. Fail-closed model applies.

---

## Design Element 3: Route C Architecture Decision — Detailed Design (C-1 / C-2 / C-3)

**Phase 1 Baseline:** "Direct DB write path must have authorization enforcement"

**Current State:** write_sqlite() (router.py:112-127) has zero authorization checks.

**Design Alternatives (Phase 1 determined in HG-C14):**

| Option | Name | Authorization | Mechanism | Audit Trail | 
|---|---|---|---|---|
| C-1 | GL7 Guard Wrap | Pre-write | Check before sqlite3.connect() | write_sqlite logs decision_id |
| C-2 | Gate Redirect | Post-write | write_sqlite() → Gate.process_event() before commit | Gate classification + decision link |
| C-3 | EventBuffer Unification | Pre-write | Eliminate write_sqlite(); route all writes through EventBuffer | Single enforcement point (GL7 on buffer push) |

**Phase 1 Decision (HG-C14):** "All three are technically feasible. Phase 3 must specify which, with tradeoffs."

**Concrete Selection (recommended for Phase 4):**
- **Recommended:** C-3 (EventBuffer Unification) — eliminates dual path, reduces complexity
- **Rationale:** write_sqlite() direct calls (4 sites: lines 157, 189, 213, 232) duplicate EventBuffer's purpose. Single enforcement point via EventBuffer → GL7 is more maintainable than adding guards at 4+ locations
- **Trade-off:** Requires refactoring write_safe_csv() and _record_integrity_incident() to use EventBuffer instead of write_sqlite(). Eliminates synchronous SQLite writes; all writes become async. Risk: temporary loss of durability guarantee if EventBuffer ingestion fails.

---

## Design Element 4: Authorization Granularity Model

**Phase 1 Baseline:** "Authorization must be enforceable before approval confirmation state is reached"

**Granularity Decision:**
- **Level:** Operation-level (not route-level)
- **Scope:** Each call to get_buffer().push() or write_sqlite() is one authorization decision point
- **Decision Basis:** Request context (actor, operation_type, target_class, risk_level)
- **Enforcement:** GL7 _governance.before_tool() or equivalent wrapper

**Example Flows:**

1. **Route B (Flask handshake):**
   ```
   POST /api/handshake
     → Extract request context (actor, endpoint, method)
     → Call _governance.before_tool("route_handshake", request_context)
     → If ALLOWED: proceed to get_buffer().push()
     → If DENIED: return 403 Forbidden (no state change)
   ```

2. **Route C (write_safe_csv → EventBuffer):**
   ```
   write_safe_csv(row)
     → validate_input_integrity(row)
     → If integrity OK: 
       → Call _governance.before_tool("write_event_log", row_context)
       → If ALLOWED: get_buffer().push(event_dict)
       → If DENIED: return None (no state change, log incident)
   ```

---

## Design Element 5: Authorization Record Binding Mechanism

**Phase 1 Baseline:** "Authorization decisions must be linkable to approval confirmation events"

**Current Gap:** events table has no decision_id field; decision_ledger.jsonl is not linked to events table

**Concrete Binding Design:**

**Schema Extension (events table):**
Add column: `authorization_decision_id TEXT`

**GL7 Extension (GovernanceDecision object):**
Add field: `decision_record_id` (UUID or DECISION_YYYYMMDD_NNN format)

**Linkage Flow:**
```
_governance.before_tool(operation, context)
  → Returns GovernanceDecision{allowed=True/False, decision_record_id="DC_20260909_001", reason="..."}

If allowed:
  → Call mocka_write_event(event_dict)
  → Store decision_record_id in event["authorization_decision_id"]
  → Write to events table WITH decision_record_id
  → Also write to Decision Ledger with reverse reference (event_id list)
```

**Verification Query:**
```sql
SELECT e.event_id, e.who_actor, e.what_type, e.authorization_decision_id, d.allowed, d.reason
  FROM events e
  LEFT JOIN decision_ledger d ON e.authorization_decision_id = d.decision_id
  WHERE e.event_id = 'E20260909_123'
```

**Result:** Auditor can trace any event back to its authorization decision, and any decision back to events it authorized.

---

## Design Element 6: EventBuffer Authorization Semantics

**Phase 1 Baseline:** "EventBuffer.push() must not silently allow bypasses"

**Current Gap:** event_buffer.py push() method has no authorization check; assumes ALLOW by default

**Concrete Design:**

**Option A (GL7 Wrapper):**
```python
class EventBuffer:
    def push(self, event, authorization_decision=None):
        if authorization_decision is None:
            raise ValueError("EventBuffer.push() requires authorization_decision")
        if not authorization_decision.allowed:
            raise RuntimeError("Push denied by authorization")
        self.queue.append({**event, "authorization_decision_id": authorization_decision.decision_record_id})
```

**Option B (Single Authority):**
```python
def authorized_push(event_dict, actor, operation_type, context):
    decision = _governance.before_tool(operation_type, {**context, "actor": actor})
    if decision.allowed:
        buffer.push({**event_dict, "authorization_decision_id": decision.decision_record_id})
    else:
        raise AuthorizationDenied(decision.reason)
```

**Recommended:** Option B (single authorized_push wrapper) — centralizes authorization logic, prevents accidental unguarded push() calls.

**Fail-Closed Enforcement:**
Any call to EventBuffer.push() without going through authorized_push() wrapper must fail at runtime (e.g., via type checking or runtime exception).

---

## Design Element 7: Bypass Closure Layer Selection & Method

**Phase 1 Baseline:** "All Routes B & C must have authorization enforcement inserted; no silent bypasses"

**Concrete Implementation Strategy:**

**Layer:** Between Flask blueprint handler and state-changing operation (get_buffer().push() or write_sqlite())

**Method A (Decorator-based):**
```python
@require_authorization("write_event")
@app.route("/api/handshake", methods=["POST"])
def handshake_post():
    # Decorator inserts authorization check before function body
    # If DENIED, decorator raises 403 before reaching get_buffer().push()
    get_buffer().push({...})
```

**Method B (Middleware-based):**
Route-level authorization middleware that:
- Intercepts all Flask requests
- Extracts authorization-relevant context (actor, endpoint, method)
- Calls GL7 decision engine
- If DENIED, returns 403 before Flask handler executes
- If ALLOWED, stores decision_record_id in request context for handler to reference

**Method C (Wrapper function):**
```python
def safe_buffer_push(event_dict, operation_context):
    decision = _governance.before_tool("push_event", operation_context)
    if decision.allowed:
        get_buffer().push({**event_dict, "authorization_decision_id": decision.decision_record_id})
        return decision.decision_record_id
    else:
        raise AuthorizationDenied(f"Push denied: {decision.reason}")
```

**Recommended:** Method C (wrapper function) + audit of all 8 Route B locations to replace direct get_buffer().push() with safe_buffer_push().

---

## Design Element 8: Fail-Closed and UNKNOWN Handling — Code Patterns

**Phase 1 Baseline:** "Missing or unknown authorization must result in DENY, not ALLOW"

**Concrete Code Pattern:**

```python
def _governance.before_tool(operation, context):
    """Fail-closed authorization decision engine"""
    try:
        # Check decision ledger for precedent
        decision_record = decision_ledger.lookup_precedent(operation, context)
        if decision_record and decision_record.status == "DECIDED":
            return GovernanceDecision(
                allowed=decision_record.allowed,
                reason=f"Precedent: {decision_record.id}",
                decision_record_id=decision_record.id
            )
        
        # Check checklist (trust checklist > trust nothing)
        if not checklist_ok(operation, context):
            return GovernanceDecision(
                allowed=False,
                reason="Checklist incomplete",
                thinking_mode="FAIL_CLOSED"
            )
        
        # Unknown or error path: DENY
        return GovernanceDecision(
            allowed=False,
            reason="UNKNOWN: No decision record or precedent found",
            thinking_mode="FAIL_CLOSED",
            dry_run_aborts=[...]
        )
    except Exception as e:
        # Exception during authorization = DENY
        return GovernanceDecision(
            allowed=False,
            reason=f"Authorization error: {str(e)}",
            thinking_mode="FAIL_CLOSED_ERROR"
        )
```

**UNKNOWN Pattern (for partially-known operations):**
- If operation_type is NEW (not in decision ledger), return DENY with dry_run_aborts list of what needs to be decided
- If context is INCOMPLETE (missing required fields), return DENY with reason
- If precedent exists but checklist_ok() returns False, return DENY (don't assume precedent applies to new context)

---

## Design Element 9: Audit & Provenance Reconstruction Queries

**Phase 1 Baseline:** "All authorization and execution events must be auditable together"

**Concrete Query Patterns:**

**Query 1: Full Audit Trail for One Event**
```sql
SELECT 
  e.event_id, e.when, e.who_actor, e.what_type,
  e.authorization_decision_id,
  d.decision_id, d.decision_at, d.allowed, d.reason,
  d.thinking_mode, d.checklist_ok, d.dry_run_aborts
FROM events e
LEFT JOIN decision_ledger d ON e.authorization_decision_id = d.decision_id
WHERE e.event_id = ?
ORDER BY d.decision_at DESC
LIMIT 1
```

**Query 2: All Events from One Decision**
```sql
SELECT e.event_id, e.when, e.who_actor, e.what_type, e.risk_level
FROM events e
WHERE e.authorization_decision_id = ?
ORDER BY e.when DESC
```

**Query 3: All Denials (Events That Did NOT Execute)**
```sql
SELECT d.decision_id, d.when, d.actor, d.reason,
  COUNT(e.event_id) as events_executed
FROM decision_ledger d
LEFT JOIN events e ON e.authorization_decision_id = d.decision_id
WHERE d.allowed = FALSE
GROUP BY d.decision_id
ORDER BY d.when DESC
```

**Query 4: Integrity Incidents (Failed Validation)**
```sql
SELECT e.event_id, e.when, e.who_actor, e.title,
  e.short_summary, e.free_note
FROM events e
WHERE e.what_type = 'incident'
  AND e.title LIKE '[INTEGRITY_VIOLATION]%'
ORDER BY e.when DESC
```

**Index Recommendation:**
```sql
CREATE INDEX idx_events_auth_decision_id ON events(authorization_decision_id);
CREATE INDEX idx_events_what_type ON events(what_type);
CREATE INDEX idx_decision_ledger_decision_id ON decision_ledger(decision_id);
```

---

## Design Element 10: Schema Impact Assessment

**Phase 1 Baseline:** "Authorization binding requires minimal schema changes; no breaking changes"

**Required Additions:**

**Table: events**
- New column: `authorization_decision_id TEXT` (nullable for legacy events)
- Migration: `ALTER TABLE events ADD COLUMN authorization_decision_id TEXT DEFAULT NULL;`
- Backward compatibility: Existing events remain queryable; new writes will populate this field

**Table: decision_ledger** (already exists)
- Add field (if not present): `event_ids TEXT` (JSON array of linked event_id values)
- Example: `{"event_ids": ["E20260909_001", "E20260909_002"]}`
- Purpose: Reverse linkage (decision → events it authorized)

**New Table: authorization_exceptions** (optional, Phase 5+)
- Purpose: Track operations that required manual override or exception approval
- Fields: exception_id, operation_type, context, actor, approved_by, approved_at, reason
- Phase 3 scope: Document structure only; no creation yet

**No Changes Required:**
- events table primary key (event_id) remains unchanged
- decision_ledger.jsonl format remains unchanged (backward compatible append)
- EventBuffer in-memory structure (no persistence changes)

**Migration Impact:**
- Zero downtime: ALTER TABLE is online in SQLite (modern versions)
- Rollback: `DROP COLUMN authorization_decision_id` (recovers pre-change state)
- Safety: No data loss; only adds new optional field

---

## Design Element 11: Rollback & Recovery Procedures

**Phase 1 Baseline:** "Any failed authorization implementation must not corrupt event ledger"

**Recovery Levels:**

**Level 1: Single Failed Event Push**
```
Symptom: Event X was pushed but authorization check was missed
Recovery:
  1. Verify in events table: SELECT * FROM events WHERE event_id = 'X';
  2. If authorization_decision_id is NULL: Mark as "unverified" in free_note
     UPDATE events SET free_note = CONCAT(free_note, ' [UNVERIFIED_AUTH]') WHERE event_id = 'X';
  3. OR: Delete and re-push with authorization:
     DELETE FROM events WHERE event_id = 'X';
     Call safe_buffer_push() with correct authorization_decision_id
```

**Level 2: Batch Bypass (Multiple Events Without Authorization)**
```
Symptom: Route B handler had authorization check removed/broken; 100+ events pushed unverified
Recovery:
  1. Identify time window: SELECT MIN(when), MAX(when) FROM events WHERE authorization_decision_id IS NULL AND when > '2026-09-09';
  2. Create incident record:
     INSERT INTO events (event_id, when, what_type, title) VALUES 
     ('INCIDENT_ROLLBACK_001', NOW(), 'ROLLBACK', 'Batch bypass recovery: 100+ events');
  3. For each event, create decision record retroactively (dry_run_aborts):
     INSERT INTO decision_ledger (decision_id, allowed, reason, thinking_mode) VALUES
     ('RETRO_DC_20260909_*', FALSE, 'Retroactive DENY for bypass period', 'FAIL_CLOSED_RECOVERY');
  4. Link events to retroactive decisions:
     UPDATE events SET authorization_decision_id = 'RETRO_DC_...' WHERE event_id IN (...);
  5. Notify audit: Produce audit report of what was recovered
```

**Level 3: Data Corruption (authorization_decision_id points to non-existent decision)**
```
Symptom: Event links to decision_id that doesn't exist in decision_ledger
Recovery:
  1. Identify orphaned events:
     SELECT e.event_id FROM events e
     WHERE e.authorization_decision_id NOT IN (SELECT decision_id FROM decision_ledger);
  2. Create investigation record:
     INSERT INTO events (what_type, title) VALUES ('INTEGRITY_INCIDENT', 'Orphaned authorization links detected');
  3. For each orphan, determine if:
     a) Decision record should be created retroactively (if operation was legitimate)
     b) Event should be marked as unverified (if decision was lost)
  4. Apply corresponding fix
```

**Prevention:**
- Foreign key constraint (optional, SQLite supports it): `FOREIGN KEY (authorization_decision_id) REFERENCES decision_ledger(decision_id)`
- Validation query (pre-production): Check for orphaned links before deployment

---

## Design Element 12: Production Safety Procedures

**Phase 1 Baseline:** "Authorization enforcement must not block legitimate operations; safety verification required before go-live"

**Pre-Production Safety Checklist:**

**Functional Safety (Operations Must Work):**
- [ ] All 8 Route B handlers tested: request → authorization → buffer.push() → Gate ingestion
- [ ] Route C write_sqlite() refactored to EventBuffer; test write_safe_csv() → buffer → Gate
- [ ] Authorization decision ledger populated with 50+ precedent decisions (test data)
- [ ] GL7 checklist_ok() returns True for all 50+ test precedents
- [ ] Fail-closed: Test that unknown operation_type returns DENY

**Integrity Safety (Data Must Be Correct):**
- [ ] Sample 1000 events: verify authorization_decision_id matches decision_ledger
- [ ] Sample 100 decisions: verify reverse linkage (event_ids field) matches events table
- [ ] Orphan check: `SELECT e.event_id FROM events e WHERE e.authorization_decision_id NOT IN (SELECT decision_id FROM decision_ledger)`
- [ ] Integrity validation script passes: `python verify_authorization_integrity.py`

**Performance Safety (System Must Not Slow Down):**
- [ ] Query latency for "get event with authorization" < 10ms (50th percentile)
- [ ] Gate ingestion throughput >= 1000 events/sec (existing baseline)
- [ ] EventBuffer push() < 1ms (in-memory operation)
- [ ] Decision ledger lookup < 5ms (local JSON query)

**Rollback Safety (Must Be Able to Recover):**
- [ ] Backup: Full copy of mocka_events.db taken before rollout
- [ ] Rollback script exists: `python rollback_authorization.py --restore-from=backup.db`
- [ ] Rollback tested: Restore from backup, verify data consistency
- [ ] Time-to-rollback < 5 minutes (documented procedure)

**Monitoring Safety (Must Know If Something Breaks):**
- [ ] Alert: If any push to EventBuffer returns error, log to monitoring
- [ ] Alert: If authorization_decision_id is NULL for new events (indicates bypass)
- [ ] Alert: If GL7 checklist_ok() returns False more than N times/hour (indicates decision gap)
- [ ] Dashboard: Show authorization decision rate, denial rate, enforcement coverage

**Go-Live Procedure:**
1. Run all 12 safety checklists in staging environment
2. Get sign-off from authorized reviewer (not automated)
3. Deploy to production (blue-green or canary)
4. Monitor alerts for 24 hours
5. If no critical alerts, mark as "production-safe"
6. If critical alert: execute rollback procedure within 15 minutes

---

## Summary: Stream 2 Design Detailing Complete

This document concretizes 12 design elements required by Phase 1 Normative Baseline:

1. **Approval Confirmation State** — Operational definition: all writes to events/decisions/audit tables
2. **Route B Enforcement Points** — 8 Flask routes with GL7 check insertion before get_buffer().push()
3. **Route C Architecture** — C-3 (EventBuffer Unification) recommended; write_sqlite() elimination candidate
4. **Authorization Granularity** — Operation-level (each buffer.push() is one decision point)
5. **Record Binding** — events.authorization_decision_id ↔ decision_ledger.decision_id linkage
6. **EventBuffer Semantics** — authorized_push() wrapper enforces GL7 check at push time
7. **Bypass Closure** — Method C (wrapper function) for all 8 Route B + write_sqlite() sites
8. **Fail-Closed Patterns** — UNKNOWN/MISSING authorization returns DENY, not ALLOW
9. **Audit Queries** — 4 SQL patterns for full traceability (event → decision, decision → events)
10. **Schema Impact** — Minimal: add authorization_decision_id to events; no breaking changes
11. **Rollback Recovery** — 3-level procedures for single/batch/corruption scenarios
12. **Production Safety** — 6-category checklist (functional/integrity/performance/rollback/monitoring/go-live)

**Governance Constraints Maintained:**
- No implementation code written
- No schema migration created
- No code/test modifications
- C2-b BLOCK immutable
- UNKNOWN/NOT_PROVEN preserved where design alternatives remain open

---

**Status:** Stream 2 (Design Detailing) COMPLETE

**Next:** Stream 3 (Specification Creation) — Formalize design decisions into executable specifications (implementation pseudocode, migration scripts, validation queries, configuration).

**Then:** Stream 4 (Verification Planning) — Define test cases, audit procedures, compliance verification.

**Final Deliverable:** 16-item Authorization Readiness Package to Human Gate for Phase 4 review and implementation authorization decision.
