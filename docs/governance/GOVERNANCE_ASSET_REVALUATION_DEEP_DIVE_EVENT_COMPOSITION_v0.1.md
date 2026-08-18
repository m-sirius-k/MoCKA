# Deep Dive: Event Store + Decision Ledger Composition

**Status**: Investigation Active  
**Related Tasks**: Research Question 1 (Composition via Event Causality) / Representation Gap Analysis  
**Focus**: Can Event Store → Decision Ledger form a complete causality chain?

---

## 1. Investigation Scope

**Question**: If all governance events are recorded in events.db AND all institutional decisions are recorded in decision_ledger.jsonl, what guarantees exist that they form a consistent, traceable record?

**Sub-questions**:
1a. Does every event have a corresponding decision record, or vice versa?  
1b. Can we trace an event ID forward to the decision it influenced?  
1c. Can we trace a decision backward to the events that justified it?  
1d. What consistency checks exist between these two systems?  
1e. How would we know if a mismatch occurred?

---

## 2. Event Store Current State

### Storage

**Location**: `/home/user/MoCKA/data/events.db` (SQLite, primary)  
**Schema**: (to be verified by inspection)  
**Record Count**: 20,645 events as of 2026-08-18 (from OVERVIEW.json)  
**Format**: Append-only (one-way write, immutable once recorded)

### Event Categories

From GOVERNANCE_ASSET_REVALUATION_MATRIX_v0.1:

- CHANGE_START / CHANGE_DONE pairs (file modification tracking)
- Decision events (DC_* decisions recorded as events)
- Incident events (E* events for anomalies)
- Governance events (policy changes, authority decisions)
- System events (app startup, tool use, etc.)

### Linking Mechanism

According to CLAUDE.md:
- Event ID format: `E{YYYYMMDD}_{NNN}` (mocka_router.py: `get_next_event_id()`)
- tags field: comma-separated categorization (e.g., "change_start,governance,asset_revaluation")
- related_event_ids: reference to linked events (if field exists)

**Critical Question**: Does every record consistently populate cross-reference fields, or are some events recorded without linkage metadata?

---

## 3. Decision Ledger Current State

### Storage

**Location**: `/home/user/MoCKA/data/decisions/decision_ledger.jsonl` (JSONL, immutable log)  
**Record Count**: 245 decisions as of 2026-08-18 (from OVERVIEW.json)  
**Schema**: 
- decision_id: DC_YYYYMMDD_NNN
- title: human-readable description
- context: situation that prompted decision
- alternatives: explicit comparison (multiple options considered)
- rationale: reasoning for choice (5W1H preservation)
- approved_at: ISO8601 timestamp
- status: (active/superseded/closed per TODO_384)
- related_todos: (array of TODO_IDs)
- related_events: (cross-reference to events.db entries)

### Linking Mechanism

**Forward link** (Decision → Event):
- related_events field: does it contain event IDs?

**Backward link** (Event → Decision):
- Do events have decision_id field?
- How are events tagged with DC_* references?

**Critical Question**: Is related_events field actually populated, or is it defined in schema but empty?

---

## 4. Hypothetical Composition Chain

If both link mechanisms work:

```
Raw Fact
  ↓ (recorded as)
Event E20260818_001 { type: "policy_change", payload: {...} }
  ↓ (triggers)
Decision evaluation process
  ↓ (results in)
Decision DC_20260818_001 { rationale: "Based on E20260818_001" }
  ↓ (cross-reference)
Decision records: related_events: ["E20260818_001"]
Event receives: tags: ["...decision_trigger,DC_20260818_001..."]
  ↓ (can verify)
Forward: DC_20260818_001.related_events[0] = "E20260818_001" ✓
Backward: E20260818_001.tags contains "DC_20260818_001" ✓
Bidirectional link ESTABLISHED
```

---

## 5. Evidence Sources to Check

### Primary Sources

1. **events.db schema inspection**
   - Verify all fields present
   - Check if related_decision_ids field exists
   - Measure populatedness of cross-reference fields

2. **decision_ledger.jsonl sample**
   - Inspect 10 recent decisions
   - Check if related_events field is populated
   - Verify format of references

3. **Record count audit**
   - Total events: 20,645
   - Total decisions: 245
   - Ratio analysis: ~84 events per 1 decision
   - Question: Is this ratio reasonable?

4. **mocka_write_event implementation**
   - Search: tools/mocka_auto_record.py / governance/verify_governance_event_required.py
   - Does it auto-link to decisions?
   - What metadata does it capture?

5. **Decision ledger population code**
   - Where is decision_ledger.jsonl written?
   - Does write happen atomically with event record?
   - Error handling if both writes don't succeed?

### Secondary Sources

- TODO_361: Decision Ledger recording obligation enforcement
- TODO_322: PHI-OS Event Gate single-path guarantee
- E20260705_732301073f4bd: MCP tool registry drift incident
- DECISION_POLICY_v0.1.md: Decision authority rules

---

## 6. Known Issues That Affect Composition

### 6.1 TODO_396 Uncertainty

**Finding**: TODO_396 (Review Gate implementation) marked "complete" but:
- Referenced commit 64f8a4ae9 not found in repository
- phi_os/human_gate.py not located in filesystem
- CHANGE_DONE recorded but physical evidence missing

**Impact on Composition Chain**: If human_gate.py Review Gate layer doesn't exist, then Reason Unit → Decision → Event flow is incomplete. Decision authority boundary is undefined.

**Status**: UNKNOWN - requires commit history investigation

### 6.2 Event Recording Hook Reliability

**Finding**: PostToolUse hook (tools/mocka_auto_record.py) automatically records CHANGE_DONE events.

**Risk**: If MoCKA server is down:
- Event records to local offline log (tools/auto_record.log)
- Not immediately written to events.db
- Gap between actual change and event record
- Composition chain breaks temporarily

**Mitigation Claimed**: Manual mocka_write_event call fills the gap

**Status**: UNVERIFIED - no audit of offline log → recovery process

### 6.3 Decision Ledger Write Timing

**Question**: When is decision_ledger.jsonl written relative to event record?

**Scenario A** (Correct):
1. Event E1 written to events.db
2. Human Gate approval processed
3. Decision D1 written to decision_ledger.jsonl
4. Both records contain cross-references
5. Composition chain: consistent

**Scenario B** (Broken):
1. Event E1 written to events.db
2. Human Gate approval processed
3. Decision D1 written to decision_ledger.jsonl
4. Cross-reference fields empty
5. Composition chain: broken

**Current Evidence**: None located - requires source code inspection

---

## 7. Testable Predictions

If composition works correctly, we should observe:

### Test P1: Decision → Event Traceability

```
SELECT COUNT(DISTINCT decision_id) FROM decisions 
WHERE related_events IS NOT NULL AND related_events != ""
```

**Expected**: ~90% of decisions have non-empty related_events (or similar percentage)  
**Actual**: ? (To be measured)

### Test P2: Event → Decision Back-Reference

```
SELECT COUNT(DISTINCT event_id) FROM events 
WHERE tags LIKE '%DC_%' OR related_decision_id IS NOT NULL
```

**Expected**: ~245 events have decision references (matching decision count, or proportion thereof)  
**Actual**: ? (To be measured)

### Test P3: Bidirectional Consistency

```
SELECT COUNT(*) FROM decisions d 
WHERE 
  d.related_events LIKE CONCAT('%', (SELECT e.event_id FROM events e LIMIT 1), '%')
  AND NOT EXISTS (
    SELECT 1 FROM events e2 
    WHERE e2.event_id IN (d.related_events) 
    AND e2.tags LIKE CONCAT('%', d.decision_id, '%')
  )
```

**Expected**: 0 (no mismatches)  
**Actual**: ? (To be measured)

### Test P4: Temporal Consistency

For each decision:
- Get approval timestamp (approved_at)
- Get related event timestamps from events.db
- Verify: event.timestamp < decision.approved_at

**Expected**: 100% of records satisfy temporal order  
**Actual**: ? (To be measured)

---

## 8. Discrepancies Already Noted

### D1: router/save recurrence (40 events)

**ESSENCE 2026-08-16 note**: "router/save: 過去40回再発"

**Implications for Composition**:
- If router/save events are duplicated
- And decisions reference these events
- Then decision rationale may appear to have more evidence than actually exists

**Evidence Required**: Event deduplication logic / root cause for 40-event series

### D2: CP932 Contamination Risk (2026-06-18)

**Finding**: check_utf8_mandate.py Rule4/5 added to prevent non-ASCII in event payloads

**Implications for Composition**:
- Events written before 2026-06-18 may have encoding issues
- Cross-system parsing (Python → MCP → JSON) may fail silently
- Link data could be corrupted

**Evidence Required**: UTF-8 audit of events.db records pre-2026-06-18

---

## 9. Implementation Gaps Identified

| Gap | Severity | Evidence Status | Prerequisite for Closure |
|-----|----------|-----------------|--------------------------|
| decision_ledger.jsonl write atomicity | HIGH | UNKNOWN | Source code inspection (where is JSONL written?) |
| Event → Decision back-reference population | HIGH | UNKNOWN | Grep for decision_id / related_decision in event write |
| Router/save recurrence root cause | MEDIUM | DOCUMENTED (40 events) | Incident root cause analysis (reference in ESSENCE) |
| TODO_396 Review Gate physical file | MEDIUM | MISSING | Git history search for commit 64f8a4ae9 |
| Offline log → events.db recovery audit | MEDIUM | CLAIMED / UNVERIFIED | Process trace (tools/auto_record.log sample + recovery flow) |

---

## 10. Next Investigation Steps

**Priority 1 - Schema Verification**:
1. Open events.db and inspect actual schema
2. Open decision_ledger.jsonl sample and inspect structure
3. Compare actual schema to assumed schema above

**Priority 2 - Population Audit**:
1. Run Test P1-P4 SQL/JSON queries against actual data
2. Measure cross-reference field populatedness
3. Document any anomalies

**Priority 3 - Source Code Trace**:
1. Find where decision_ledger.jsonl is written
2. Find where events.db gets decision_id field populated
3. Determine if writes are atomic or separate transactions

**Priority 4 - Discrepancy Resolution**:
1. Trace router/save 40-event sequence
2. Understand why events repeat
3. Verify no decision references duplicated events

---

## 11. Classification Framework Application

Based on findings so far:

**Current Status**: C (Partially Composed)

- **Composed** (B elements):
  - Events recorded independently ✓
  - Decisions recorded independently ✓
  - Both systems append-only ✓
  
- **Partially Composed** (C elements):
  - Cross-references claimed but unverified
  - Write atomicity unknown
  - Recovery process unaudited

- **Enforcement Gap** (E elements):
  - If composition exists, is it actually enforced?
  - What happens if write fails partway?
  - No documented compensating control observed

---

## 12. Hypothesis Tests

### H1: "Composition via Event Causality Works"

**Supports H1**:
- Two independent ledgers exist (decentralization ✓)
- Both use IDs for cross-reference (capability exists ✓)
- Both are immutable (integrity ✓)

**Contradicts H1**:
- Related_events field empty (linkage broken ✗)
- Event timestamps after decision approve_at (causality reversed ✗)
- router/save recurrence (deduplication fails ✗)
- TODO_396 file missing (Review Gate incomplete ✗)

**Verdict**: INCONCLUSIVE - awaiting data inspection

---

## 13. Evidence Inventory

### Available for Inspection

- [ ] events.db (file system)
- [ ] decision_ledger.jsonl (file system)
- [ ] tools/mocka_auto_record.py (source)
- [ ] governance/verify_governance_event_required.py (source)
- [ ] Git history for commit 64f8a4ae9

### Claimed but Unverified

- [ ] Event → Decision cross-reference population
- [ ] Decision → Event write atomicity
- [ ] Router/save deduplication logic
- [ ] Review Gate Review layer implementation

### Explicitly Missing

- [ ] phi_os/human_gate.py (reported in TODO_396 note)
- [ ] Commit 64f8a4ae9 (search needed)

---

## 14. Research Methodology for This Deep Dive

**Data Collection Phase**: Inspect actual files / code  
**Analysis Phase**: Run queries / compare actual vs. assumed  
**Verification Phase**: Trace 5-10 decision → event chains  
**Reporting Phase**: Update matrix with A/B/C/D/E/F/G classification

**Timeline**: Complete by end of investigation session  
**Deliverable**: Updated GOVERNANCE_ASSET_REVALUATION_MATRIX with Event Store row completed

---

**Document Version**: v0.1  
**Investigation Started**: 2026-08-18  
**Current Phase**: Scope Definition (Section 1-7) → Ready for Data Collection Phase  
**Next Reviewer**: Kimura-sensei (human gate for discrepancies found)
