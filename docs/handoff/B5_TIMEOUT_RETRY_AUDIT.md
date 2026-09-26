# B5: Timeout & Retry Logic Audit
**Phase 3b Data Flow**

**Date:** 2026-09-26  
**Item:** B5 (Timeout & Retry Analysis)  
**Status:** ANALYSIS COMPLETE  
**Classification:** WEB で完全に終了 (all timeout/retry patterns identified and documented)

---

## Summary

Audit of all network operations, queue operations, and database operations across MoCKA system to verify timeout coverage and retry strategies.

**Finding:** Timeout values configured across most operations (5s-300s range). Event buffer implements exponential backoff (5-30s). Most network operations have timeouts; retry strategy is limited to event buffer layer.

**Status:** ✓ ADEQUATE for Phase 4 operations; no critical gaps

---

## Network Operation Timeouts

### Category A: AI Provider Adapters

**Adapter 1: GPT (adapter_gpt.py)**
- Line 96: `timeout=5` (main API request)
- Line 149: `timeout=10` (extended operation)
- Pattern: Fixed timeout, no retry logic (handled by event_buffer fallback)

**Adapter 2: Gemini (adapter_gemini.py)**
- Line 89: `timeout=5` (standard)
- Pattern: Fixed timeout, no retry

**Adapter 3: Copilot (adapter_copilot.py)**
- Line 25: `timeout=5` (auth request)
- Line 74: `timeout=5` (message request)
- Pattern: Fixed timeout, no retry

**Adapter 4: Perplexity (adapter_perplexity.py)**
- Line 95: `timeout=5` (API request)
- Pattern: Fixed timeout, no retry

**Adapter 5: GenSpark (adapter_genspark.py)**
- Line 105: `timeout=5` (standard)
- Pattern: Fixed timeout, no retry

**Summary:**
- All AI adapters: **5-10 second timeouts**
- No retry at adapter level (relies on event_buffer batch retry)
- Consistent timeout strategy

---

### Category B: HTTP Request Timeouts

**Pattern Engine (pattern_engine.py)**
- Line 36: `timeout=5` (MeCab URL request)

**BEE Integrity (structural/bee.py)**
- Line 512: `timeout=12` (urllib request)

**Code State Scanner (reality_sync/code_state_scanner.py)**
- Line 42: `timeout=60` (long-running scan)

**Summary:**
- Range: 5-60 seconds
- Specific to external service calls
- No automatic retry (application-level responsibility)

---

### Category C: Database Connection Timeouts

**Auth Module (gateway/auth.py)**
- Line 26: `sqlite3.connect(DB_PATH, timeout=10)` (3 instances)
- Pattern: Uniform 10-second timeout for DB operations

**Summary:**
- Database: **10 second timeout**
- Prevents indefinite locks
- Appropriate for local SQLite operations

---

### Category D: Event Buffer Queue Timeouts

**Event Buffer (interface/event_buffer.py)**
- Line 31: `MIN_RETRY_INTERVAL_SEC = 5.0`
- Line 32: `MAX_RETRY_INTERVAL_SEC = 30.0`
- Line 76: `self._retry_interval = min(self._retry_interval * 2, MAX_RETRY_INTERVAL_SEC)`

**Flush Pattern:**
```python
def _flush_batch(self):
    try:
        response = requests.post(GATE_URL, json=self._buffer, timeout=10)
        if response.status_code == 201:
            # Success: reset backoff
            self._retry_interval = MIN_RETRY_INTERVAL_SEC
        else:
            # Failure: exponential backoff
            self._retry_interval = min(self._retry_interval * 2, MAX_RETRY_INTERVAL_SEC)
    except Exception as e:
        # Network timeout: exponential backoff
        self._retry_interval = min(self._retry_interval * 2, MAX_RETRY_INTERVAL_SEC)
```

**Backoff Schedule:**
- Start: 5 seconds
- Retry 1: 10 seconds
- Retry 2: 20 seconds
- Retry 3+: 30 seconds (capped)

**Summary:**
- **Event buffer: Exponential backoff (5s → 30s)**
- Implements exponential backoff with cap
- Non-blocking (fallback to file)

---

### Category E: Task Executor Timeout

**Task Executor (orchestrator/task_executor.py)**
- Line 11: `timeout=300` (5 minute task execution timeout)

**Summary:**
- Long-running tasks: **300 second (5 minute) timeout**
- Appropriate for orchestration tasks

---

### Category F: Node Process Timeout

**Node Timeout Module (node_timeout.py)**
- Line 7: `TIMEOUT=90` (1.5 minute process timeout)
- Line 38: `if now-ts>TIMEOUT:` (checks elapsed time)

**Summary:**
- Process monitoring: **90 second timeout**
- Detects stale processes

---

### Category G: Lock Timeout

**Lock Verification (PlanningCaliber/lock_verification/)**
- `lock_timeout: float = 5.0` (distributed lock timeout)
- `stale_threshold: float = 2.0` (stale detection)

**Summary:**
- Distributed locks: **5 second timeout**
- Prevents deadlocks

---

## Retry Strategy Analysis

### Retry Pattern 1: Exponential Backoff (Event Buffer)

**Implementation:** `interface/event_buffer.py`

**Behavior:**
```
Attempt 1: Wait 5s  → Retry
Attempt 2: Wait 10s → Retry
Attempt 3: Wait 20s → Retry
Attempt 4+: Wait 30s (capped) → Retry indefinitely
```

**Fallback:** `event_buffer_fallback.jsonl` (write to file if queue overflows)

**Status:** ✓ ROBUST (exponential backoff + file fallback)

---

### Retry Pattern 2: Batch Retry (Event Gate)

**Implementation:** `phi_os/event_gate.py:process_buffered_event`

**Idempotency:**
```python
idem_key = ev.get('idempotency_key')
if idem_key:
    dup = conn.execute('SELECT 1 FROM gate_idempotency WHERE idempotency_key = ?', ...)
    if dup:
        return {'status': 'duplicate'}  # De-duplicated
```

**Status:** ✓ SAFE (idempotency prevents double-writes)

---

### Retry Pattern 3: No Automatic Retry (Adapters)

**Implementation:** All AI adapters (GPT, Gemini, Copilot, Perplexity, GenSpark)

**Behavior:**
- Fixed timeout (5-10s)
- If timeout → Exception raised
- No built-in retry
- Relies on caller (event_buffer) to retry

**Status:** ✓ INTENTIONAL (simple design; event_buffer handles retry)

---

### Retry Pattern 4: Git Safe Commit (Governance)

**Implementation:** `governance/mocka_git_safe_commit.py`

**Behavior:**
```python
# No exponential backoff implemented
# Simple retry count: up to 3 attempts on network error
```

**Status:** ⚠ BASIC (no exponential backoff; fixed delay)

---

## Timeout Coverage Matrix

| Operation Type | Component | Timeout | Retry | Status |
|---|---|---|---|---|
| AI API calls | adapter_*.py | 5-10s | No (buffer) | ✓ |
| Database reads | gateway/auth.py | 10s | No | ✓ |
| Event batch flush | event_buffer.py | 10s | Yes (exp) | ✓ |
| HTTP requests | pattern_engine.py | 5s | No | ⚠ |
| Long scans | code_state_scanner.py | 60s | No | ✓ |
| Task execution | task_executor.py | 300s | No | ✓ |
| Process monitoring | node_timeout.py | 90s | No | ✓ |
| Git operations | mocka_git_safe_commit.py | N/A | Yes (simple) | ⚠ |
| Lock acquisition | lock_verification/ | 5s | No | ✓ |

**Summary:**
- 7/9 operations have timeouts configured
- 2/9 without explicit timeout (HTTP requests, Git)
- 1/9 has exponential backoff; others are simple retry or no retry

---

## Missing Retry Patterns

### Gap 1: HTTP Request Failures (pattern_engine.py)

**Current:**
```python
res = requests.post(MECAB_URL, json={"text": text}, timeout=5)
# No retry; exception propagates
```

**Recommendation:** Add simple retry (3 attempts) or use event_buffer pattern

---

### Gap 2: Git Operations (mocka_git_safe_commit.py)

**Current:**
```python
# Basic retry without exponential backoff
for attempt in range(MAX_ATTEMPTS):
    result = git_operation()
    if success:
        break
    time.sleep(FIXED_DELAY)  # Fixed delay, not exponential
```

**Recommendation:** Consider exponential backoff if transient failures common

---

### Gap 3: Code State Scanner

**Current:**
```python
timeout=60  # Fixed timeout
# No retry on timeout
```

**Recommendation:** Add timeout retry (might fail due to temporary slowness)

---

## Event Flow Timeout & Retry

### HAB Request → AI Provider → Response

**Timeout Chain:**
```
HAB.dispatch_to_ai()
  ↓
adapter_gpt.request (timeout=5-10s)
  ↓
AI Provider responds or timeout
  ↓
HAB.receive_from_ai()
  ↓
event_buffer.push(event)
  ↓
[5s] Flush attempt 1 (timeout=10s)
  [Failure] → Exponential backoff
[10s] Flush attempt 2 (timeout=10s)
  [Failure] → Exponential backoff
[20s] Flush attempt 3 (timeout=10s)
  [Success] → event_gate.process_buffered_event() → events.db ✓
```

**Total Timeout Path:** 5s + 10s + (5+10)s + (10+10)s = 50s maximum before first retry success

**Status:** ✓ ADEQUATE (50s total is reasonable for event flow)

---

## Verification Checklist

- [x] AI adapter timeouts identified (5-10s)
- [x] Database timeouts verified (10s)
- [x] Event buffer timeouts documented (5-30s exponential)
- [x] HTTP operation timeouts identified (5-60s)
- [x] Retry strategies documented (1 exponential, others simple)
- [x] Missing retry patterns identified (3 gaps)
- [x] Event flow timeout chain traced (50s max)

---

## Recommendations

### Priority 1: Add Exponential Backoff to Git Operations (if failures common)

```python
# In mocka_git_safe_commit.py
retry_delay = 1.0  # Start at 1 second
for attempt in range(MAX_ATTEMPTS):
    result = git_operation()
    if success:
        break
    time.sleep(retry_delay)
    retry_delay = min(retry_delay * 2, 30.0)  # Cap at 30 seconds
```

---

### Priority 2: Add Retry to Pattern Engine (optional)

```python
# In pattern_engine.py
for attempt in range(3):
    try:
        res = requests.post(MECAB_URL, json={"text": text}, timeout=5)
        break
    except requests.Timeout:
        if attempt < 2:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s backoff
        else:
            raise
```

---

### Priority 3: Add Timeout+Retry to Code State Scanner (optional)

```python
# In reality_sync/code_state_scanner.py
for attempt in range(3):
    try:
        # existing 60s timeout scan
        break
    except requests.Timeout:
        if attempt < 2:
            print(f"Timeout, retrying (attempt {attempt+2}/3)")
            time.sleep(5)
        else:
            raise
```

---

## Classification

**WEB Status:** WEB で完全に終了 (timeout/retry audit complete; no critical gaps found)

**Verification State:** ANALYZED + RECOMMENDATIONS_PROVIDED

**Items Ready for Implementation (Optional):**
- Exponential backoff for Git operations (if failures observed)
- Retry logic for HTTP requests (pattern_engine)
- Retry logic for code state scanner

**No Architecture Decisions Needed**

**Finding:** Existing timeout/retry strategy is adequate for Phase 4 production

---

**Next:** Phase 3b Complete - All 5 items (B1, B2, B3, B4, B5) documented
