# Point 3 Resolution Design Need Assessment

Assessment Date: 2026-08-26
Prerequisite: ROUTE-C (Evidence Access / Sourcing Gap) CONFIRMED

---

## Prerequisite State (Fixed)

```
SOURCE:       Discussion Continuity Recovery
PROBLEM:      Session Context Binding Runtime Divergence
CONTINUITY:   CONNECTED
NECESSITY:    NOT REQUIRED
ROUTE:        ROUTE-C (Evidence Access / Sourcing Gap)
```

---

## Assessment Questions (Evidence-Based)

### Question 1: Runtime Recovery が必要とする Evidence は存在するか

**Status: DIRECT EVIDENCE**

mocka_events.db events テーブルに以下カラムが実装：
- session_id: 存在（events_latest.json で確認）
- trace_id: 存在（events_latest.json で確認）
- related_event_id: 存在（events_latest.json で確認）
- when_ts: 存在（context_builder.py line 54）
- title: 存在
- short_summary: 存在（context_builder.py line 120）

**Conclusion: YES - All necessary fields present in canonical store**

---

### Question 2: Runtime が Canonical Evidence へ到達できるか

**Status: INFERRED (Path Reference Issue)**

Current Path Reference:
```python
# context_builder.py line 15
DB_PATH = DATA_DIR / "mocka_events.db"
# where DATA_DIR = Path(__file__).parent.parent / "data"
```

Actual File Location:
```
/home/user/MoCKA/mocka_events.db  (repository root)
```

Mismatch:
- Code expects: `/home/user/MoCKA/data/mocka_events.db`
- Actual location: `/home/user/MoCKA/mocka_events.db`

**Status: DIRECT EVIDENCE**
- Path mismatch **CONFIRMED**
- Likely outcome: sqlite3.connect() fails → Exception caught (line 129-130) → return []

**Conclusion: UNKNOWN - Path mismatch likely blocks access, but needs verification**

---

### Question 3: 到達後、必要な Context を取得できるか

**Current SQL Query (context_builder.py lines 107-112):**
```python
cur.execute(
    "SELECT event_id, title, short_summary, when_ts, what_type, session_id, trace_id, related_event_id "
    "FROM events "
    f"WHERE {valid_when_ts_clause()} "
    "ORDER BY when_ts DESC LIMIT ?",
    (limit,)
)
```

Issues Identified:
- `WHERE {valid_when_ts_clause()}`: Time-based filter (recent events only)
- `LIMIT`: Hard limit (5 for ChatGPT, 30 for extended)
- **MISSING: `WHERE session_id = ?`** - No session-scope query

**Status: DIRECT EVIDENCE**

Query lacks session-scope filtering; retrieves only time-recent events without session context.

**Conclusion: NO - Multi-session context retrieval impossible**

---

### Question 4: limit=5 制約が本当に Continuity を阻害しているか

**Test Case A: Single Session Within Recent 5 Events** ✓
```
Session: SESSION_20260826_122001
Events: E1(1h ago), E2(30m ago), E3(15m ago), E4(5m ago), E5(now)
→ All retrieved, continuity maintained
```

**Test Case B: Multi-Session Spanning Beyond 5 Events** ✗
```
Session A: E1(48h ago), E2(40h ago), E3(38h ago)
           ↓
           [20800 events]
           ↓
Session B: E20804(1h ago), E20805(30m ago), ..., E20808(now)

Result: Only SESSION_B recent 5 events retrieved
→ SESSION_A context LOST
```

**Status: DIRECT EVIDENCE**

limit=5 constraint causes context loss in multi-session scenarios.

**Conclusion: PARTIALLY YES - Continuity blocked for multi-session transitions beyond 5-event window**

---

### Question 5: Path mismatch が事実か

**Status: DIRECT EVIDENCE (Confirmed)**

Code Reference:
```python
DB_PATH = DATA_DIR / "mocka_events.db"
# Resolves to: /home/user/MoCKA/data/mocka_events.db
```

Actual File:
```
/home/user/MoCKA/mocka_events.db
```

Confirmed mismatch. DB access likely fails silently via exception handler.

**Conclusion: YES - Path mismatch is confirmed fact**

---

### Question 6: events_latest.json 統合欠如が本質的問題なのか

**Current State:**
- events_latest.json: exists (200 events, snapshot)
- context_injector.py: lists "events_latest" as context_source
- context_builder.py: does NOT use events_latest.json in _load_events()

**Dual-Source Analysis:**
```
mocka_events.db (Canonical, 20980 events)
        ↓
events_latest.json (Snapshot, 200 events)
```

Current Behavior:
- Attempts mocka_events.db access
- Fails due to path mismatch (likely)
- No fallback to events_latest.json
- Returns empty list

**Status: INFERRED**

Missing fallback logic is symptom, not root cause. Root cause is path mismatch.

**Conclusion: PARTIALLY YES - Lack of fallback is implementable gap; path fix required first**

---

### Question 7: 既存 Runtime 構造だけで問題を解消可能か

**Existing Components Available:**
- mocka_events.db: Canonical Event Store (正本)
- events_latest.json: Snapshot Cache (200 events)
- context_builder.py: Context Assembly Logic
- adapter_gpt.py: Query Interface

**Option A: Path Reference Correction (Minimal)**
```python
DB_PATH = Path(__file__).parent.parent / "mocka_events.db"
```
- Scope: 1-line change
- Impact: DB access resumption
- Outcome: limit=5 constraint remains

**Option B: Fallback Logic (Moderate)**
```python
def _load_events(self, mode: str) -> list:
    result = self._load_from_db(mode)
    if not result:
        result = self._load_from_snapshot(mode)
    return result
```
- Scope: New fallback function
- Impact: Snapshot cache as recovery layer
- Outcome: Canonical + Snapshot integration

**Option C: Session-Scoped Query (Moderate)**
```python
def _load_events_for_session(self, session_id: str, mode: str) -> list:
    limit = {"standard": 50, "extended": 200}[mode]
    # WHERE session_id = ? instead of time-scope only
```
- Scope: New session-aware function, increased limits
- Impact: Multi-event session context recovery
- Outcome: Proper session continuity

**Status: DIRECT EVIDENCE**

All options implementable within existing architecture; no new persistence or data structures needed.

**Conclusion: YES - Existing Runtime structure sufficient for resolution**

---

### Question 8: 新たな設計判断が必要か

**Design Decision Points:**

**1. Canonical vs Snapshot Priority**
- Current: mocka_events.db primary, but no fallback defined
- Question: Should Canonical-first + Snapshot-fallback be institutionalized?

**2. Session-Scope as Default Filter**
- Current: Time-scope only (recent N events)
- Question: Should session_id be default grouping dimension?

**3. limit Values Justification**
- Current: limit=5 (ChatGPT), limit=30 (extended)
- Question: What's the rationale? Token budget? Latency? Design intent?
- Can limit increase?

**4. Path Reference Authority**
- Current: DB_PATH = DATA_DIR / "mocka_events.db" (incorrect)
- Question: Who owns the truth about DB location? Repository root or data/ directory?

**Status: UNKNOWN (Design Rationale Not Documented)**

No documented rationale for:
- limit=5 selection
- Time-scope-only approach
- Path reference origin
- Fallback strategy absence

**Conclusion: YES - Policy decisions needed for institutional clarity**

---

## Summary Table

| Question | Evidence Status | Finding |
|---|---|---|
| 1. Evidence Exists | DIRECT | YES |
| 2. Runtime Access | UNKNOWN | Path mismatch likely blocks access |
| 3. Context Retrieval | DIRECT | NO - Session-scope missing |
| 4. Continuity Blocking | DIRECT | PARTIAL - Multi-session scenarios only |
| 5. Path Mismatch | DIRECT | YES - CONFIRMED |
| 6. Snapshot Integration Gap | INFERRED | PARTIAL - Symptom of fallback absence |
| 7. Existing Structure Sufficiency | DIRECT | YES - All fixes within existing patterns |
| 8. New Design Judgment Needed | UNKNOWN | YES - For policy decisions |

---

## FINAL DETERMINATION

### Design Need: **YES (Limited Policy Scope)**

**What Does NOT Need Design:**
- Path reference correction (1 line, technical fix)
- Fallback logic implementation (straightforward extension)
- Session-scoped query implementation (SQL extension)

**What DOES Need Design Gate:**
1. Institutionalize Canonical Evidence (mocka_events.db) as primary Runtime source
2. Define Snapshot (events_latest.json) as formal recovery layer and fallback strategy
3. Establish session-scope as default grouping dimension (vs time-scope only)
4. Clarify path reference authority: DB location canonical location
5. Justify or adjust limit values and token allocation for context

**Scope of Design:**
- NOT new persistence system (unnecessary)
- NOT new data structure (unnecessary)
- IS clarification of component responsibilities, fallback hierarchy, and policy boundaries

**Design Gate Should Produce:**
- Canonical vs Snapshot priority policy (制度化)
- Session-scope default specification (制度化)
- limit value justification or adjustment (制度化)
- Path reference authority (制度化)

---

## Advancement Path

```
ROUTE-C CONFIRMED
        ↓
DESIGN NEED: YES (Limited Policy Scope)
        ↓
DESIGN GATE REQUIRED (for policy decisions only)
        ↓
IF gate approves:
  Implementation proceeds with path fix + fallback + session-query
  (all implementable in existing structure)
        ↓
IF gate denies or holds:
  Current system remains; no changes authorized
```

---

## Current State Summary

```
PROBLEM:           Session Context Binding Runtime Divergence
SOURCE:            Discussion Continuity Recovery (CONFIRMED)
CONTINUITY:        CONNECTED
NECESSITY:         NOT REQUIRED
ROUTE:             ROUTE-C (Evidence Access / Sourcing Gap)
DESIGN NEED:       YES (Limited policy scope)
DESIGN GATE:       REQUIRED (before implementation)
IMPLEMENTATION:    NOT AUTHORIZED (pending design gate)
```

---

**Design Need Assessment: COMPLETE**
**No Implementation authority granted.**
**Next step: Design Gate decision required.**
