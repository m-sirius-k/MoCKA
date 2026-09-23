# TARGET-1 REMEDIATION DESIGN
**Objective:** Recover TARGET-1 to PASS while maintaining existing schema

**Constraint:** Must satisfy all 8 mandatory conditions without changing existing architecture

---

## PROBLEM STATEMENT

Current implementation:
```python
def _next_decision_id():
    micros_of_day = time.time_ns() // 1000 % 1_000_000_000
    return f'DC_{d}_{micros_of_day:09d}{secrets.token_hex(2)}'
```

Issues:
1. Violates schema (format DC_YYYYMMDD_TTTTTTTTXX instead of NNN)
2. Collisions possible (~0.0001%)
3. Modulo bug (1e9 ≠ 86.4e9)
4. Not atomic as claimed
5. Not fail-closed for clock adjustments

**Required outcome:** Generate DC_YYYYMMDD_NNN format safely without race conditions

---

## DESIGN CANDIDATES

### CANDIDATE A: File-based Locking + max(used)+1

**Mechanism:**
- Lock decision_ledger.jsonl with fcntl.flock() (Unix) or msvcrt.locking() (Windows)
- Read all existing IDs atomically
- Calculate max(used) + 1
- Release lock
- Write to ledger

**Evaluation:**

| Criterion | Status | Notes |
|-----------|--------|-------|
| Schema compatible | ✓ | Maintains DC_YYYYMMDD_NNN |
| Thread safety | ✓ | File lock prevents concurrent reads |
| Process safety | ✓ | File locks work across processes |
| Restart safety | ✓ | Reads from persistent ledger |
| Crash safety | ✓ | Append-only, lock released on crash |
| Fail-closed | ✓ | Lock failure raises exception |
| Ledger impact | ✓ | No change to existing records |
| Files changed | 1 | mocka_mcp_server.py only |
| Rollback | ✓ | Revert single function |

**Pros:**
- Minimal change
- Proven pattern (POSIX standard)
- Absolutely no collisions
- No new dependencies

**Cons:**
- Lock contention if many concurrent writers
- File locking behavior differs Windows vs Unix
- May fail on network filesystems

---

### CANDIDATE B: SQLite Atomic Counter Table

**Mechanism:**
- Create table: `decision_id_counters(date TEXT, counter INTEGER PRIMARY KEY)`
- Use SQLite transaction + SELECT FOR UPDATE
- Atomically increment counter
- Generate ID from date + counter

**Evaluation:**

| Criterion | Status | Notes |
|-----------|--------|-------|
| Schema compatible | ✓ | NNN from SQLite counter |
| Thread safety | ✓ | ACID transactions |
| Process safety | ✓ | SQLite handles locks |
| Restart safety | ✓ | Counter persisted |
| Crash safety | ✓ | Transactions rolled back |
| Fail-closed | ✓ | Transaction failure rolls back |
| Ledger impact | ✓ | No change to decision_ledger.jsonl |
| Files changed | 1 | mocka_mcp_server.py only |
| Rollback | ✓ | Single function change |

**Pros:**
- Already using SQLite in mocka_mcp_server.py
- No additional file locking complexity
- Cross-platform reliable
- Transactions guarantee atomicity
- No counter drift possible

**Cons:**
- One additional DB table
- Counter table initialization needed
- Migration from empty state

---

### CANDIDATE C: In-Memory Lock + Read Ledger

**Mechanism:**
- Use threading.Lock() (already used in app.py, interface/event_buffer.py)
- Hold lock during read + calculate + return
- Within single process, ensures no race

**Evaluation:**

| Criterion | Status | Notes |
|-----------|--------|-------|
| Schema compatible | ✓ | NNN format maintained |
| Thread safety | ✓ | Lock prevents concurrent access |
| Process safety | ✗ | Lock doesn't span processes |
| Restart safety | ✓ | Reads from ledger |
| Crash safety | ✓ | Lock released on exception |
| Fail-closed | ✓ | Exception on lock failure |
| Ledger impact | ✓ | No change |
| Files changed | 1 | mocka_mcp_server.py only |
| Rollback | ✓ | Single function |

**Pros:**
- Minimal code change
- Already used pattern in codebase

**Cons:**
- Does NOT handle process concurrency
- mocka_mcp_server is HTTP service (single process)
- But if launched multiple times: race condition risk

---

## EXISTING ARCHITECTURE ANALYSIS

Current state of mocka_mcp_server.py:

```
Line 94-102:   _get_db()           ← SQLite connection factory
Line 343-350:  _sanitize()         ← Input validation
Line 450-457:  _append_decision()  ← Append-only write
Line 425-435:  _read_decisions()   ← Read all decisions
Line 436-451:  _next_decision_id() ← BROKEN (needs fix)
```

**SQLite Tables already present:**
- `claude_sessions` (line 98)
- `request_executions` (line 559)

**Locking patterns already used:**
- app.py: `_intent_lock = threading.Lock()`
- interface/event_buffer.py: `self._lock = threading.Lock()`

---

## RECOMMENDATION

**CANDIDATE B: SQLite Atomic Counter** is recommended

**Rationale:**

1. **Existing dependency:** SQLite already used in mocka_mcp_server.py
2. **No new files:** Single mocka_mcp_server.py change
3. **Absolute guarantees:** ACID transactions guarantee no collisions
4. **Process-safe:** Works across multiple server instances
5. **Restart-safe:** Counter persists in DB
6. **Fail-closed:** Transaction rollback on any error
7. **Schema preserved:** Generates DC_YYYYMMDD_NNN format exactly
8. **Rollback simple:** One function replaced

---

## IMPLEMENTATION DELTA

**File: mocka_mcp_server.py**

### Change 1: Add table initialization to _get_db()

**Location:** After line 102 (after claude_sessions table creation)

**Addition:**
```python
con.execute("""CREATE TABLE IF NOT EXISTS decision_id_counters (
    date TEXT PRIMARY KEY,
    counter INTEGER DEFAULT 0
)""")
```

**Lines changed:** +4

### Change 2: Replace _next_decision_id() function

**Location:** Lines 436-451 (current broken implementation)

**New implementation sketch:**
```python
def _next_decision_id():
    today = datetime.date.today().strftime("%Y%m%d")
    con = _get_db()
    
    try:
        con.execute("BEGIN IMMEDIATE")  # Exclusive lock
        
        # Atomically increment counter for today
        con.execute(
            "INSERT OR IGNORE INTO decision_id_counters (date, counter) VALUES (?, 0)",
            (today,)
        )
        con.execute(
            "UPDATE decision_id_counters SET counter = counter + 1 WHERE date = ?",
            (today,)
        )
        
        # Retrieve incremented value
        row = con.execute(
            "SELECT counter FROM decision_id_counters WHERE date = ?",
            (today,)
        ).fetchone()
        
        con.commit()
        
        next_num = row[0]
        return f"DC_{today}_{next_num:03d}"
    
    except Exception as e:
        con.rollback()
        raise  # Fail-closed
    finally:
        con.close()
```

**Lines changed:** ~30 (replace 16 lines with ~30)

### Change 3: Update _next_classification_id() similarly (OPTIONAL)

**Note:** Same bug exists in `_next_classification_id()` (line 488)
- If fixing both: Apply same pattern to IC_YYYYMMDD_NNN
- If not: Mark as TODO

---

## VERIFICATION PLAN

After implementation:

1. **Syntax check:** `python -m py_compile mocka_mcp_server.py`
2. **Existing tests:** Run test_target1_decision_id.py
3. **Format validation:** Verify output is DC_YYYYMMDD_NNN
4. **Collision check:** 50 parallel generations → 0 duplicates
5. **Restart safety:** Generate ID, restart app, verify no duplicate
6. **Ledger integrity:** Verify new IDs append correctly

---

## ROLLBACK PROCEDURE

If issues arise:

1. Revert mocka_mcp_server.py to previous commit
2. Delete `decision_id_counters` table (automatic on next revert)
3. No other cleanup needed

---

## NEXT STEPS (await HG approval)

1. Human Gate review of CANDIDATE B recommendation
2. Approval or alternative selection
3. Implementation of chosen design
4. Verification with existing test suite
5. Final TARGET-1 = PASS confirmation

---

**Design completed:** 2026-09-21
**Status:** READ-ONLY (awaiting approval for implementation)
