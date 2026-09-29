# PHASE 5.1.1 Lineage Implementation Contract
## Human Gate 承認用仕様書

**Date**: 2026-09-28  
**Status**: PRE-GATE (implementation not started)  
**Scope**: vendor/model/runtime/source の 4 fields  
**Target**: Event Store persistence & readback  

---

## 1. FIELD SEMANTICS CONTRACT

### 1.1 vendor

**Definition:**  
AI service provider identifier (OpenAI / Anthropic / Google / Perplexity / Genspark / Copilot)

**Producer:** adapter_gpt.py:87 (line 87)
```python
"vendor": "OpenAI"
```

**Producer Code Path:**
- adapter_gpt.py:70-99 (handle_function_call)
- Source: Hard-coded per adapter (vendor specific)
- adapter_claude.py:81 = "Anthropic"
- adapter_gemini.py = "Google"
- adapter_perplexity.py = "Perplexity"
- adapter_genspark.py = "Genspark"

**Payload Key:** actor.vendor  
**Gateway Key:** vendor (gateway.py:337)  
**Buffer Key:** vendor (event_buffer.py:52-58, preserved as-is)  
**Event Gate Input Key:** vendor (payload.get('vendor'))  
**Event Store Target:** [NEW COLUMN] vendor TEXT  

**Current Runtime Value Examples:**
- "OpenAI" (from GPT adapters)
- "Anthropic" (from Claude adapters)
- "Google" (from Gemini adapters)

**NULL Handling:** Fallback to "Unknown" if not provided (gateway.py:337)

**Existing Code Reference:**
- gateway.py:337: `vendor = actor.get("vendor", "Unknown")`
- gateway.py:363: `"vendor": vendor,`
- event_buffer.py: payload transmitted as-is

---

### 1.2 model

**Definition:**  
Specific model version/identifier within vendor (gpt-4-turbo / claude-opus-5 / gemini-1.5 / etc.)

**Producer:** adapter_gpt.py:88 (line 88)
```python
"model": model  # parameter passed from caller
```

**Producer Code Path:**
- adapter_gpt.py:70-99 (handle_function_call parameter)
- Default: "GPT" (line 71)
- Caller can override: model="gpt-4-turbo"
- adapter_claude.py:65: default="claude-opus-5"
- adapter_gemini.py: default="gemini-1.5-pro"

**Payload Key:** actor.model  
**Gateway Key:** model (gateway.py:338)  
**Buffer Key:** model (event_buffer.py:52-58, preserved as-is)  
**Event Gate Input Key:** model (payload.get('model'))  
**Event Store Target:** [NEW COLUMN] model TEXT  

**Current Runtime Value Examples:**
- "gpt-4-turbo" (from OpenAI adapters)
- "claude-opus-5" (from Anthropic adapters)
- "gemini-1.5-pro" (from Google adapters)

**NULL Handling:** Empty string "" if not provided (gateway.py:338, no fallback)

**Existing Code Reference:**
- gateway.py:338: `model = actor.get("model", "")`
- gateway.py:364: `"model": model,`

---

### 1.3 runtime

**Definition:**  
Runtime environment / execution context (ChatGPT / API / Claude / Canvas / Gemini Web / etc.)

**Producer:** adapter_gpt.py:89 (line 89)
```python
"runtime": runtime  # parameter passed from caller
```

**Producer Code Path:**
- adapter_gpt.py:70-99 (handle_function_call parameter)
- Default: "ChatGPT" (line 71)
- adapter_claude.py:65: default="Claude"
- adapter_gemini.py: default="Gemini Web"

**Payload Key:** actor.runtime  
**Gateway Key:** [gateway.py does NOT explicitly receive runtime as separate key]
**Gateway Extraction:** gateway.py:365: `"runtime": actor.get("runtime", "")`  
**Buffer Key:** runtime (event_buffer.py:52-58, preserved as-is)  
**Event Gate Input Key:** runtime (payload.get('runtime'))  
**Event Store Target:** [NEW COLUMN] runtime TEXT  

**Current Runtime Value Examples:**
- "ChatGPT" (from GPT web interface)
- "Claude" (from Claude API or web)
- "Gemini Web" (from Gemini web interface)

**NULL Handling:** Empty string "" if not provided (no fallback)

**CRITICAL NOTE:**  
runtime フィールドは gateway.py では **明示的に抽出されていない**。actor.get("runtime") の値が直接 event_buffer に渡されているのみ。

**Existing Code Reference:**
- gateway.py:365: `"runtime": actor.get("runtime", "")`

---

### 1.4 source

**Definition:**  
Source/origin of the request (Orchestra / direct / manual / API / etc.)

**Producer:** adapter_gpt.py:90 (line 90)
```python
"source": source  # parameter passed from caller
```

**Producer Code Path:**
- adapter_gpt.py:70-99 (handle_function_call parameter)
- Default: "Orchestra" (line 72)
- adapter_claude.py:66: default="Orchestra"

**Payload Key:** actor.source  
**Gateway Key:** source (gateway.py:339)  
**Gateway Secondary Key:** ai_actor (gateway.py:362: `"ai_actor": source`)  
**Buffer Key:** source (event_buffer.py:52-58, preserved as-is)  
**Event Gate Input Key:** source (payload.get('source'))  
**Event Store Target (Current):** ai_actor TEXT (not source)  
**Event Store Target (Proposed):** [NEW COLUMN] source TEXT  

**Current Runtime Value Examples:**
- "Orchestra" (from Orchestra UI)
- "Direct" (from direct API calls)
- "Manual" (from manual entry)

**NULL Handling:** Fallback to "Direct" if not provided (gateway.py:339)

**CRITICAL ISSUE:**  
source は **ai_actor 列に変換される** (gateway.py:362)。既存 DB には source としての記録がなく、ai_actor として保存される。

**Existing Code Reference:**
- gateway.py:339: `source = actor.get("source", "Direct")`
- gateway.py:362: `"ai_actor": source`
- gateway.py:366: `"source": source,`
- event_gate.py: ai_actor のみ処理 (source は無視)

---

## 2. SCHEMA CONTRACT

### 2.1 Current CREATE TABLE events

```sql
CREATE TABLE "events" (
    event_id            TEXT PRIMARY KEY,
    when_ts             TEXT NOT NULL,
    who_actor           TEXT,
    what_type           TEXT,
    ...
    ai_actor            TEXT,
    session_id          TEXT,
    ...
    request_id          TEXT DEFAULT NULL
)
```

**Key Constraints:**
- PRIMARY KEY: event_id (TEXT)
- NOT NULL: when_ts, _source
- CHECK: _source IN (allowed values)
- No foreign keys
- No unique constraints except PK

**Existing Columns Related to Lineage:**
- who_actor: currently stores "OpenAI/gpt-4-turbo" (concatenated vendor/model)
- ai_actor: currently stores source (Orchestra/Direct/etc.)
- request_id: nullable, for tracing requests

---

### 2.2 Proposed Schema Changes

**Add 4 columns:**

```sql
ALTER TABLE events ADD COLUMN vendor TEXT;
ALTER TABLE events ADD COLUMN model TEXT;
ALTER TABLE events ADD COLUMN runtime TEXT;
ALTER TABLE events ADD COLUMN source TEXT;
```

**Rationale:**
- vendor: Currently stored implicitly in who_actor (before "/")
- model: Currently stored implicitly in who_actor (after "/")
- runtime: Currently not stored anywhere (lost)
- source: Currently stored as ai_actor (conflated, needs separate field)

**Column Characteristics:**
- Type: TEXT (allows NULL)
- NOT NULL: NO (existing rows will be NULL)
- Default: NULL
- Indexed: NO (optional for Phase 5.1.1)
- Collation: BINARY (default)

**Schema Impact Assessment:**

| Aspect | Impact | Reasoning |
|--------|--------|-----------|
| Existing rows | None (NULL for new columns) | Backward compatible |
| Insert performance | Negligible | 4 additional TEXT columns |
| SELECT performance | Negligible (no WHERE clause on new cols yet) | No index yet |
| Storage size | ~4 bytes per row per column (NULL) | Text type, minimal overhead |
| Rollback | Straightforward (DROP COLUMN) | SQLite supports DDL rollback in transaction |
| Migration from existing data | Possible with UPDATE from who_actor/ai_actor | Not required for Phase 5.1.1 |

---

### 2.3 Migration Mechanism

**Method: SQLite ALTER TABLE ADD COLUMN**
```sql
ALTER TABLE events ADD COLUMN vendor TEXT;
ALTER TABLE events ADD COLUMN model TEXT;
ALTER TABLE events ADD COLUMN runtime TEXT;
ALTER TABLE events ADD COLUMN source TEXT;
```

**Execution:**
- Atomic transaction
- Can be run directly against mocka_events.db
- No need for separate migration file (inline in gate initialization, or manual)
- Backward compatible (existing data unaffected)

**Rollback:**
```sql
ALTER TABLE events DROP COLUMN vendor;
ALTER TABLE events DROP COLUMN model;
ALTER TABLE events DROP COLUMN runtime;
ALTER TABLE events DROP COLUMN source;
```

---

## 3. FREEZE / GOVERNANCE CHECK

### 3.1 Phase 4-7 Freeze Status

**Current Freeze:** cfa19a55e (2026-09-27 10:20:59Z)  
**Status:** LOCKED for implementation (Phase 4-7)  
**Exception Scope:** Schema migration explicitly carved out

**Assessment:**

| Item | Status | Evidence |
|------|--------|----------|
| Code change to gateway.py | BLOCKED | In Phase 4-7 freeze |
| Code change to event_gate.py | BLOCKED | In Phase 4-7 freeze |
| Code change to adapter_*.py | BLOCKED | In Phase 4-7 freeze |
| Schema migration (ALTER TABLE) | READY | Outside code freeze, governance decision |
| DB data change | READY | Read-only verification only (no writes) |
| Server restart | BLOCKED | Per Phase 5.0 scope |
| Process restart | BLOCKED | Per Phase 5.0 scope |

**Judgment:**

```
FREEZE_COMPATIBLE: PARTIAL
  - Schema migration: YES (governance domain)
  - Code change: NO (Phase 4-7 freeze)
  - Therefore: Schema-only contract is FREEZE_COMPATIBLE
            Implementation of event_gate.py awaits Phase 5.2
```

---

### 3.2 Human Gate Scope Compatibility

**Current Phase 5.0 Scope:** "Genesis Bootstrap + HAB-JARVIS Runtime Verification"  
**HDF Audit Baseline:** FINAL (Phase 5.0 closure)  
**HDF Implementation Review:** PRECHECK complete (Phase 5.1)

**Lineage Contract Status:** 
- Part of Phase 5.1 (Implementation Review)
- Blocked by Phase 4-7 freeze (code changes)
- Can proceed with schema definition (governance)

**Judgment:**

```
HG_SCOPE_COMPATIBLE: YES (partial implementation)
  - HDF Audit Baseline: COMPLETE
  - Lineage Contract Definition: READY
  - Code Implementation: DEFERRED (Phase 5.2, after freeze lift)
```

---

## 4. MINIMUM PATCH BOUNDARY

### 4.1 When Phase 4-7 Freeze Lifts (Phase 5.2+)

**File 1: event_gate.py**

```
Location: C:\Users\sirok\MoCKA\phi_os\event_gate.py
Function: _write(payload: dict, conn=None) -> None
Lines: 46-76 (row construction)

Change: Add 4 lines after line 75 (before empty-string-to-None conversion):

  row = {
      ...existing 25 fields...
      'request_id': payload.get('request_id'),
+     'vendor': payload.get('vendor'),           # NEW
+     'model': payload.get('model'),             # NEW
+     'runtime': payload.get('runtime'),         # NEW
+     'source': payload.get('source') or payload.get('ai_actor'),  # NEW
  }
```

**Rationale:**
- 4 lines added
- Parallel structure to existing extraction
- source fallback to ai_actor (for backward compat)
- No conditional logic needed

**Verification:**
- No change to INSERT statement (dynamic column list)
- Row dict size increases from 25 to 29 fields
- Existing code paths unaffected

---

### 4.2 Schema Initialization (Immediate, Phase 5.1.1)

**DB Path:** C:\Users\sirok\MoCKA\data\mocka_events.db

**SQL:**
```sql
ALTER TABLE events ADD COLUMN vendor TEXT;
ALTER TABLE events ADD COLUMN model TEXT;
ALTER TABLE events ADD COLUMN runtime TEXT;
ALTER TABLE events ADD COLUMN source TEXT;
```

**Execution Options:**
1. Manual: Direct SQL against mocka_events.db
2. Automated: Add to gate initialization (phi_os/event_gate.py:__init__ or similar)
3. Migration file: Create data/migrations/001_add_lineage_columns.sql

---

### 4.3 Readback Path (Automatic)

**File:** mocka_mcp_server.py  
**Function:** _db_read_events()  
**Current:** SELECT * FROM events (dynamic)  
**Change:** None required (automatically includes new columns)

---

## 5. VERIFICATION CONTRACT

### 5.1 Test Case Structure

**Scenario:** Gateway receives adapter payload with vendor/model/runtime/source

```
Input (adapter_gpt.py):
  payload = {
      "actor": {
          "vendor": "OpenAI",
          "model": "gpt-4-turbo",
          "runtime": "ChatGPT",
          "source": "Orchestra",
      },
      ...
  }

Step 1: Gateway Extraction (gateway.py:337-365)
  Expected: vendor="OpenAI", model="gpt-4-turbo", 
            runtime="ChatGPT", source="Orchestra"

Step 2: Event Buffer (event_buffer.py:57)
  Expected: Same 4 fields preserved

Step 3: Event Gate Process (event_gate.py:_write)
  Expected (NEW): row['vendor']="OpenAI", row['model']="gpt-4-turbo",
                  row['runtime']="ChatGPT", row['source']="Orchestra"

Step 4: Event Store INSERT (mocka_events.db)
  Expected (NEW): vendor column receives "OpenAI"
                  model column receives "gpt-4-turbo"
                  runtime column receives "ChatGPT"
                  source column receives "Orchestra"

Step 5: Readback (mocka_mcp_server.py)
  SELECT vendor, model, runtime, source FROM events WHERE event_id = ?
  Expected: ("OpenAI", "gpt-4-turbo", "ChatGPT", "Orchestra")
```

### 5.2 Verification Checkpoints

| Checkpoint | Verifiable? | Method |
|------------|------------|--------|
| Gateway sends vendor/model/runtime/source | YES | HTTP request body inspection |
| Buffer receives and preserves | YES | event_buffer.py print/log |
| Event Gate processes | YES | _write() function parameters |
| Event Store stores | YES | SELECT query on events table |
| Readback returns correct values | YES | mocka_mcp_server.py _db_read_events() |
| 4 fields match across chain | YES | trace with request_id/event_id |

---

## 6. FINAL CONTRACT DEFINITION

### 6.1 Lineage Fields Contract

```
vendor = TEXT, NOT NULL at producer
         ↓ Gateway extraction (line 337)
         ↓ Buffer transmission
         ↓ Event Gate row construction (proposed: line 76+)
         ↓ Event Store column (new)
         ↓ Readback: SELECT vendor
         
model = TEXT, nullable at producer (default="")
        ↓ Gateway extraction (line 338)
        ↓ Buffer transmission
        ↓ Event Gate row construction (proposed)
        ↓ Event Store column (new)
        ↓ Readback: SELECT model

runtime = TEXT, nullable at producer (default="")
          ↓ Gateway extraction (line 365)
          ↓ Buffer transmission
          ↓ Event Gate row construction (proposed)
          ↓ Event Store column (new)
          ↓ Readback: SELECT runtime

source = TEXT, NOT NULL at producer (default="Direct")
         ↓ Gateway extraction (line 339)
         ↓ Also mapped to ai_actor (line 362)
         ↓ Buffer transmission
         ↓ Event Gate row construction (proposed)
         ↓ Event Store columns: source (new) + ai_actor (existing)
         ↓ Readback: SELECT source, ai_actor
```

---

### 6.2 Implementation Preconditions

```
LINEAGE_CONTRACT = READY
  - Semantics: Defined from primary code ✓
  - Producer path: Identified ✓
  - Payload keys: Verified ✓
  - Current runtime values: Documented ✓

SCHEMA_CONTRACT = READY
  - Proposed columns: 4 TEXT fields ✓
  - Backward compatibility: Confirmed (NULL for existing) ✓
  - Migration: ALTER TABLE defined ✓
  - Rollback: DROP COLUMN defined ✓
  - No conflicts with existing schema ✓

FREEZE_COMPATIBILITY = PARTIAL
  - Schema migration: READY (governance domain) ✓
  - Code changes (event_gate.py): BLOCKED (Phase 4-7 freeze) ✗
  - Therefore: Contract definition READY, implementation DEFERRED

HG_SCOPE_COMPATIBILITY = READY
  - Within Phase 5.1 scope: ✓
  - Supports HDF Audit Baseline: ✓
  - Non-breaking change: ✓

VERIFICATION_CONTRACT = READY
  - Test case structure: Defined ✓
  - Checkpoints: All verifiable ✓
  - Readback mechanism: Automatic (SELECT *) ✓

MINIMUM_PATCH = IDENTIFIED
  - Schema: 4 ALTER TABLE statements
  - Code: 4 lines in event_gate.py _write() (Phase 5.2+)
  - Readback: No change (automatic)
```

---

## 7. HUMAN GATE APPROVAL REQUEST

**REQUEST SUMMARY:**

Lineage 4-field contract (vendor/model/runtime/source) is ready for Human Gate approval to proceed with:

1. **Phase 5.1.1 (Immediate):** Schema definition + migration SQL
   - 4 ALTER TABLE statements
   - No code changes, no server impact
   - Reversible (DROP COLUMN)

2. **Phase 5.2 (After Phase 4-7 freeze lift):** Code implementation
   - 4 lines in event_gate.py _write()
   - No new files, no new functions
   - Non-breaking change (optional input)

**PRECONDITIONS MET:**
- ✓ Lineage semantics defined from primary code
- ✓ Schema impact assessed (backward compatible)
- ✓ Freeze compatibility understood (schema OK, code deferred)
- ✓ Verification contract established
- ✓ Rollback plan defined

**DECISION REQUIRED:**

```
[ ] APPROVE Phase 5.1.1 schema migration (proceed immediately)
    └─ Then await Phase 4-7 freeze lift for Phase 5.2 code

[ ] BLOCK (with specific concern)
    └─ Specify which precondition needs re-evaluation
```

---

**STATUS: READY FOR HUMAN GATE REVIEW**

**Date:** 2026-09-28 11:50 UTC  
**Next Action:** Human Gate approval → Schema migration → Phase 5.2 code implementation
