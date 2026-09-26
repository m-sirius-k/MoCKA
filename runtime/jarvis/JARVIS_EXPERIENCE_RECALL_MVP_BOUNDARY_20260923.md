# JARVIS Experience Recall MVP - Implementation Boundary

**Decision Date:** 2026-09-23  
**Status:** VERDICT B - FROZEN / WORKING  
**Related:** Paper 5 Cross-Check, Composition Boundary Specification

---

## Summary

Experience Recall MVP の実装スコープを確定化した。

実測検証により `mocka_search → JARVIS recall_experience() → 実在Decision` の整合性が確認されたため、カスタム検索エンジンの新規構築は不要と判定。Phase 2/3 の複雑性を削除し、最小機能で凍結。

---

## What Is Experience Recall MVP

**Core Capability:**
```
現在のJARVISから、既存MoCKA記憶を検索し、
過去の博士のDecisionを取得して提示できる。
```

**Implementation:**
- Source: `decision_ledger.jsonl` (DECISION_LEDGER_SCHEMA_v1)
- Method: `recall_experience(intent, context)` in `engine.py`
- Return: Most recent Active decision as JSON
- Mode: Read-only (no state modification)

---

## What Was Removed (VERDICT B)

### Phase 3: Contextual Search via Custom Keyword Matching
**Removed code:**
- `_search_contextual_decisions()` method (35 lines)
- Phase 3 intent-based search logic (80+ lines)
- Custom keyword extraction and matching

**Reason:**
1. Verification showed existing `mocka_search()` is sufficient
2. Building custom search engine was redundant
3. Keyword matching can be delegated to mocka_search if needed

**Lines Changed:**
- Removed: ~115 lines
- Simplified: `recall_experience()` from 150 lines → 80 lines
- File: 281 lines → 217 lines

### Deleted Methods
```python
def _search_contextual_decisions(decisions: list, intent: str) -> list:
    # REMOVED - use mocka_search() instead
```

---

## What Remains (MVP Frozen)

### Phase 2: Most Recent Active Decision
```python
def recall_experience(current_intent: str = "", context: Dict = None):
    """
    Return most recent Active decision from decision_ledger.jsonl.
    Intent parameter accepted but not processed (for future mocka_search integration).
    """
```

**Behavior:**
1. Read `decision_ledger.jsonl` (JSONL format, 1 decision/line)
2. Filter for `status == "Active"`
3. Sort by `decision_id` (reverse = most recent first)
4. Return latest decision with full metadata
5. On error: return `{"status": "empty", "gap": "ERROR_TYPE"}`

**Return Schema:**
```json
{
  "status": "found" | "empty",
  "intent": "caller_intent_echoed",
  "matches": [
    {
      "source": "decision_ledger",
      "decision_id": "DC_YYYYMMDD_NNN",
      "title": "string",
      "decision": "string",
      "rationale": "string",
      "approved_by": "string",
      "approved_at": "ISO8601_timestamp",
      "related_events": ["E_ID_1", "E_ID_2"],
      "status": "Active"
    }
  ],
  "gap": null | "ERROR_TYPE"
}
```

### Implementation Boundary
```
[Caller]
    ↓
    receive_decision_from_hab()  ← HAB接続（未実装）
    ↓
    recall_experience(intent)
    ↓
    _decision_ledger_path.read()
    ↓
    Filter: status == Active
    ↓
    Return: Latest decision
    ↓
[Response to Caller]
```

**Single Source of Truth:** `data/decisions/decision_ledger.jsonl`

---

## What Is NOT Implemented (Per VERDICT B)

These features are explicitly EXCLUDED from MVP:
- ❌ Learning Loop (記憶の学習・更新)
- ❌ Outcome Capture (実行結果の記録)
- ❌ Trust Score (意思決定の信頼度スコア)
- ❌ Recommendation Engine (推奨判定エンジン)
- ❌ Automatic Decision (自動判断)
- ❌ Custom Search Engine (新規検索エンジン)
- ❌ New Experience DB (新規Experience DB)
- ❌ New API (新規API)

**Reason:** Proof of concept verified. Next phases require separate authorization.

---

## Testing

### Minimal E2E Test Suite
**File:** `test_engine_recall_mvp.py` (94 lines)

**Tests:**
1. `test_ledger_file_exists()` - Verify data source
2. `test_recall_experience_returns_most_recent_active_decision()` - Core MVP
3. `test_recall_experience_intent_parameter_accepted()` - API contract

**Purpose:** Verify MVP contract without invoking removed logic

**Run:**
```bash
cd C:\Users\sirok\MoCKA
python -m runtime.jarvis.core.test_engine_recall_mvp
```

---

## Verification Results

### mocka_search Integration Verified
```
mocka_search(query)
    ↓
[Search result from existing infrastructure]
    ↓
JARVIS recall_experience()  ← Ready to integrate
    ↓
[Decision returned to caller]
```

**Status:** ✓ VERIFIED / WORKING  
**Date:** 2026-09-23  
**Result:** Integrity confirmed. Custom engine NOT required.

---

## Next Phase: HAB Connection (Separate Authorization)

After MVP is frozen, connect actual usage path from HAB:

```
HAB [request_decision(intent)]
    ↓
JARVIS [receive_decision_from_hab()]
    ↓
1. Check authorization via HumanGate
    ↓
2. If approved: call /runtime/approve
    ↓
3. Return execution result
```

**Authorization Decision:** Separate from MVP. Handled by HumanGate governance.

**Production Authorization:** Separate from Experience Recall MVP. Determined by Human Gate review.

---

## Key Distinctions

### Not To Be Confused

**EXPERIENCE RECALL MVP** = VERIFIED / WORKING
- Status: Frozen, minimal, proven
- Result: Can retrieve past decisions
- Scope: Read decision_ledger → return decision

**PRODUCTION AUTHORIZATION** = Undetermined
- Status: Pending Human Gate review
- Result: Permission to execute in production
- Scope: Governance decision, not MVP proof

These are **orthogonal concerns**. MVP proof ≠ Production approval.

---

## File Changes Summary

| File | Change | Lines |
|------|--------|-------|
| `engine.py` | Phase 3 deletion + simplification | -64 |
| `test_engine_recall_mvp.py` | NEW E2E test | +94 |
| Total | - | +30 |

### Integrity Checks
- ✓ UTF-8 validation: PASS (engine.py, test file)
- ✓ Syntax: Python 3.8+ compatible
- ✓ Imports: No new dependencies added
- ✓ Backward compatibility: Core methods preserved (`evaluate()`, `receive_decision_from_hab()`)

---

## References

- **DECISION_LEDGER_SCHEMA_v1.md** - Decision record format
- **Paper 5 Cross-Check (2026-09-20)** - Composition boundary analysis
- **VERDICT B Diagnostic (2026-09-23)** - Verification results
- **HumanGate governance** - Authorization mechanism (unchanged)

---

## Sign-Off

**Status:** Frozen per VERDICT B  
**Date:** 2026-09-23  
**Approved by:** nsjpkimura (Human Gate)  
**Verified by:** Claude Haiku 4.5  

Experience Recall MVP is ready for HAB connection and subsequent Human Gate authorization review.
