# STEP 19 Phase 2-C: Boundary Freeze & Existing Transaction Analysis
**Date:** 2026-09-21  
**Purpose:** Freeze existing Decision/Event transaction boundaries and identify immutable constraints  
**Authority:** HG-18 (A/A/C/A) - Sandbox implementation only

---

## 1. Decision Ledger Write Boundary: VERIFIED

### 1.1 Code Path Analysis

**Location:** mocka_mcp_server.py, mocka_decision_write function (line 1107-1168)

```python
# Line 1143: Decision Ledger append
_append_decision(record)  # Synchronous file write

# Line 1144-1166: Companion event (optional, separate)
try:
    r = requests.post(GATE_URL, json=gate_payload, timeout=5)
except Exception:
    pass  # Companion event failure does NOT rollback Decision
```

### 1.2 Transaction Boundary Characteristics

**Write Operation:**
```python
# mocka_mcp_server.py line 451-454
def _append_decision(record):
    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    with open(DECISION_LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

**Characteristics:**
- ✓ **Atomic unit:** Single file line
- ✓ **Semantics:** Append-only
- ✗ **Cross-boundary transaction:** NO
- ✗ **Rollback:** NO
- ✓ **Idempotency:** File append is idempotent (same line appended again is duplicate)

**Companion Event (Separate Transaction):**
- HTTP POST to event_gate (line 1162)
- Failure does NOT affect Decision record (line 1165-1166 suppresses exception)
- Result: Orphaned Event possible if Decision succeeds and Event fails

### 1.3 Decision Ledger Boundary Status: IMMUTABLE

```
Decision Ledger write boundary = file line (JSON)
Atomicity unit = single \n-delimited record
Cross-file transaction = NOT SUPPORTED
Rollback = NOT SUPPORTED

FROZEN: This boundary cannot be changed without changing existing semantics.
```

---

## 2. Event Write Boundary: VERIFIED

### 2.1 Code Path Analysis

**Location:** phi_os/event_gate.py, process_event function (line 116-136)

```python
def process_event(payload: dict, event_source: str = 'live', conn=None) -> dict:
    errors = validate(payload)
    if errors:
        return {'status': 'rejected', 'errors': errors}
    
    payload = dict(payload)
    payload['event_id'] = payload.get('event_id') or _next_event_id()
    payload['when_ts'] = payload.get('when_ts') or datetime.now(timezone.utc).isoformat()
    payload['event_source'] = event_source
    
    _write(payload, conn=conn)  # SQLite transaction
    
    return {'status': 'ok', 'event_id': payload['event_id']}
```

### 2.2 Write Operation: SQLite Transaction

```python
# phi_os/event_gate.py line 46-101
def _write(payload: dict, conn=None) -> None:
    row = {
        'event_id': payload.get('event_id', ''),
        'when_ts': payload.get('when_ts') or payload.get('when', ''),
        # ... 30+ fields mapped
        'request_id': payload.get('request_id'),
    }
    row = {k: (v if v != '' else None) for k, v in row.items()}
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()
    try:
        cols = list(row.keys())
        placeholders = ','.join('?' * len(cols))
        vals = [row[c] for c in cols]
        conn.execute(f'INSERT OR IGNORE INTO events ({",".join(cols)}) VALUES ({placeholders})', vals)
        
        # Phase5-2: Signature computation
        sig = integrity.sign_event(conn, row)
        
        # Update with signature/hash chain
        conn.execute('UPDATE events SET trace_id = ?, related_event_id = ? WHERE event_id = ?',
                    (sig['current_hash'], sig['previous_hash'], row['event_id']))
        
        if owns_conn:
            conn.commit()
    finally:
        if owns_conn:
            conn.close()
```

### 2.3 Event Write Boundary Characteristics

**Transaction Structure:**
```
BEGIN (implicit in SQLite)
  ├─ INSERT INTO events (...)
  ├─ SELECT (for signature computation)
  ├─ UPDATE events SET trace_id/related_event_id
  └─ COMMIT

All within single SQLite connection/transaction
```

**Characteristics:**
- ✓ **Atomic unit:** SQLite transaction (BEGIN...COMMIT)
- ✓ **Semantics:** INSERT + signature UPDATE
- ✓ **Cross-record consistency:** trace_id/related_event_id linked within transaction
- ✓ **Rollback:** Supported (SQLite ROLLBACK)
- ✓ **Idempotency:** INSERT OR IGNORE prevents duplicates

**Cross-boundary with Decision:**
- Event write is SEPARATE HTTP call from Decision write
- NO shared connection between mocka_decision_write and event_gate
- Atomicity between Decision + Event = NOT POSSIBLE without new wrapper

### 2.4 Event Write Boundary Status: IMMUTABLE

```
Event write boundary = SQLite transaction (mocka_events.db)
Atomicity unit = single event record with signature chain
Cross-file transaction = NOT SUPPORTED (separate from Decision Ledger)
Rollback = SUPPORTED within SQLite only

FROZEN: This boundary cannot be changed without restructuring event_gate.py
```

---

## 3. Decision ↔ Event Relationship: Current State

### 3.1 Workflow Sequence

```
T3: DECISION FORMED
    │
    mocka_decision_write() called
    │
    ├─ [TX1] Decision Ledger write
    │         └─ _append_decision() → JSONL file append
    │              Atomicity: file line
    │              Status: COMMITTED (irreversible)
    │
    └─ [TX2] Companion event write (optional, separate)
             └─ requests.post(GATE_URL) → HTTP
                  └─ event_gate.process_event() → SQLite TX
                       Atomicity: SQLite transaction
                       Failure: Caught, exception suppressed
                       Result: Orphaned event possible

Outcome: Two separate transactions (TX1 + TX2) with NO cross-transaction atomicity
```

### 3.2 Failure Modes

**Case A: Decision succeeds, companion event succeeds**
```
Decision = exists in decision_ledger.jsonl ✓
Event = exists in mocka_events.db ✓
Relationship = both created at same time (temporal coupling only)
Integrity = intact
```

**Case B: Decision succeeds, companion event fails**
```
Decision = exists in decision_ledger.jsonl ✓
Event = does NOT exist in mocka_events.db ✗
Relationship = broken (Decision orphaned)
Recovery = manual event creation needed
Integrity = compromised
```

**Case C: Decision fails (impossible with current code)**
```
JSONL append cannot fail unless disk full / permission error
If it fails: process exception, Decision never persisted
Companion event never attempted
```

### 3.3 Current Atomic Guarantees

**Atomicity achieved:**
- ✓ Within Decision Ledger: single line atomic
- ✓ Within mocka_events.db: full SQLite transaction
- ✓ Within event signature chain: trace_id + related_event_id linked

**Atomicity NOT achieved:**
- ✗ Across Decision Ledger + mocka_events.db
- ✗ Decision + companion event
- ✗ Rollback of Decision if Event fails

**Status: Two-phase commit NOT implemented. Sequential writes with exception suppression.**

---

## 4. Existing Record Compatibility: VERIFIED

### 4.1 What Cannot Be Changed

**Existing Decision Ledger Records:**
```json
{
  "decision_id": "DC_...",
  "title": "...",
  "context": "...",
  "decision": "...",
  "rationale": "...",
  "impact": "...",
  "related_events": ["E20260921_..."],  ← Existing field
  "related_documents": [...],           ← Existing field
  "approved_by": "...",
  "status": "Active",
  ...
}
```

**Cannot modify:** Any existing field (append-only semantics)

**Existing Event Records (mocka_events.db):**
```sql
event_id | when_ts | who_actor | what_type | ... | request_id | trace_id | related_event_id
─────────────────────────────────────────────────────────────────────────────────────────
E20260921_xxxx | ... | ... | ... | ... | req_id | hash | prev_event_id
```

**Cannot modify:** Any existing record (SQLite immutability requirement)

### 4.2 Where Evidence Can Be Added (Without Modification)

**Option A: New JSONL File**
```
data/evidence/evidence_records.jsonl  ← NEW, no existing record change
{
  "record_id": "PER_20260921_xxxx",
  "decision_record_id": "DC_20260921_nnn",
  ...
}
```

**Compatibility:** ✓ No existing record touched

**Option B: New Database Table**
```
vasai_evidence.db (NEW) or mocka_events.db (new table)
CREATE TABLE evidence_records (...)
```

**Compatibility:** Depends on choice (new DB ✓, new table in events DB ✗ modifies existing DB)

**Option C: Decision Ledger Extended Field (After existing fields)**
```json
{
  "decision_id": "...",
  ...existing fields...,
  "evidence_records": ["PER_20260921_xxxx"]  ← NEW FIELD, no existing field change
}
```

**Compatibility:** ✓ Append-only field addition to JSONL, existing records unaffected

### 4.3 Existing Compatibility Status: IMMUTABLE

```
New Evidence layer can be added via:
- NEW files (evidence_records.jsonl) ✓
- NEW DB (vasai_evidence.db) ✓
- NEW fields in Decision Ledger (append-only safe) ✓
- NEW table in NEW DB only ✓

Cannot:
- Modify existing Decision Ledger records ✗
- Modify existing Event records ✗
- Change existing field semantics ✗
- Create new table in mocka_events.db (would modify existing DB) ✗

FROZEN: Evidence layer must be added without modifying existing institutional records.
```

---

## 5. Evidence Layer Integration Points: IDENTIFIED

### 5.1 Where Decision ↔ Evidence Write Can Happen

**Current mocka_decision_write workflow:**
```
Lines 1107-1168:

Step 1 (line 1143): _append_decision(record)
                    └─ Write Decision to JSONL

Step 2 (line 1146-1168): [Optional] Create companion event
                         └─ HTTP POST to event_gate
```

**Integration point for Pre-Decision Evidence:**
Between Step 1 and Step 2, or after Step 1 (before/after companion event):

```
Step 1: _append_decision(record)
        └─ Write Decision to JSONL ← COMMITTED

Step 1.5: [NEW] _create_pre_decision_evidence(decision_id)  ← Can be added
          └─ Write Evidence to NEW file ← SEPARATE TRANSACTION

Step 2: [Existing] Companion event HTTP POST
        └─ Write Event to mocka_events.db ← SEPARATE TRANSACTION
```

### 5.2 Atomicity Constraint from Integration

**Between existing boundaries:**

```
Decision = COMMITTED (file line, irreversible)
    ↓
Pre-Decision Evidence = NEW (separate write)
    ↓
Companion Event = NEW/existing (separate write)

Result: 3 separate transactions, not atomic
```

**To achieve Decision + Evidence atomic-like behavior:**
```
Need wrapper transaction that:
1. Appends Decision to Ledger (file I/O)
2. Appends Evidence to Evidence file (file I/O)
3. Checks both succeeded
4. Marks relationship as "COMMITTED"

But: Cannot rollback file I/O. Only way is to track "broken" relationships and detect during read-back.
```

### 5.3 Integration Status: FEASIBLE WITH CONSTRAINTS

```
Can add Evidence creation within mocka_decision_write:
- NEW _create_pre_decision_evidence() function
- Call after _append_decision() ✓
- Separate file write (JSONL)
- Capture write result
- Record any failures in relationship metadata

Cannot achieve true atomicity:
- File writes are sequential, not transactional
- No rollback of previous writes
- But can detect and report failures in Evidence metadata

Strategy: Sequential writes with failure detection, not atomic transaction
```

---

## 6. Summary: Boundary Freeze & Constraints

### VERIFIED IMMUTABLE BOUNDARIES

```
1. Decision Ledger
   - Write method: File append (JSONL)
   - Atomic unit: Single line
   - Transaction: File I/O (commit = flush)
   - Rollback: NOT POSSIBLE
   - Modification: FORBIDDEN (append-only)

2. Event Database
   - Write method: SQLite transaction
   - Atomic unit: Single record + signature chain
   - Transaction: BEGIN...COMMIT
   - Rollback: POSSIBLE within SQLite
   - Modification: FORBIDDEN (immutable records)

3. Cross-Boundary
   - Decision ↔ Event: NOT ATOMIC
   - Decision ↔ Decision: APPEND-ONLY (no transaction)
   - Event ↔ Event: SQLite transaction only

4. Existing Records
   - Decision Ledger records: IMMUTABLE
   - Event records: IMMUTABLE
   - Cannot add/remove/change existing
```

### FROZEN INTEGRATION POINTS

```
mocka_decision_write() can be extended:
- After _append_decision() to add Evidence write ✓
- Before/after companion event ✓
- Cannot change existing Decision write ✓
- Cannot change existing Event write ✓
```

### HG-18-A IMPLICATION

```
"atomic を要求する" means Decision + Evidence should be recorded together.

Existing boundaries prevent true ACID atomicity.

Options:
1. Accept "sequential with failure detection" as quasi-atomic (HG-18-A-alternative)
2. Report EVIDENCE GAP: atomicity impossible without changing existing boundaries
3. Implement wrapper transaction that tracks broken relationships

Recommendation: Option 3 (wrapper with relationship status tracking)
```

---

## Conclusion: Boundary Freeze Complete

**Next Phase:** STEP B - Evidence Schema Finalization (based on these frozen boundaries)

All constraints identified. No existing transaction boundary can be modified.

---

**Status:** BOUNDARY FREEZE VERIFIED  
**Date:** 2026-09-21
