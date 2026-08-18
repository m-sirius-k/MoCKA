# Critical Findings: Data Inspection Phase

**Severity**: HIGH - Direct contradiction between OVERVIEW.json claims and actual storage  
**Discovery Date**: 2026-08-18  
**Impact**: Composition chain hypothesis requires major revision

---

## Executive Summary

Investigation of actual MoCKA storage revealed **critical discrepancy** between documented system architecture (OVERVIEW.json) and implemented reality:

| Claim | Expected | Actual | Status |
|-------|----------|--------|--------|
| events.db contains 20,645 events | Populated SQLite DB | 0 bytes (empty) | **BROKEN** |
| decision_ledger.jsonl exists | JSONL file in data/decisions/ | Not found | **MISSING** |
| Events link to decisions | related_events field populated | 1% embedded refs | **BROKEN** |
| Dual ledger system operational | Two independent composable systems | Fragmented storage | **BROKEN** |

---

## Finding 1: events.db Empty Despite Claims

### Evidence

- **File**: `/home/user/MoCKA/data/events.db`
- **Actual size**: 0 bytes (confirmed 2026-08-18 19:47 UTC)
- **Claimed content**: "20,645 events recorded as of 2026-08-18" (OVERVIEW.json line 271)
- **Claimed seal**: SHA256 `ad98246bef68a9a28f56b40d8b675e2b878b20db42ebec50c525132ea947ea27` (2026-06-18)

### Classification

**Category**: F (Evidence Gap)
- Representation exists in schema (could be populated)
- Implementation exists (SQLite database)
- But runtime is empty (no data)

### Root Cause Investigation

**Hypothesis A**: Database migration incomplete
- Theory: CSV→SQLite migration (claimed 2026-06-16) didn't complete
- Evidence: `events_latest.json` contains 200 events (vs. 20,645 claimed)
- Note: Migration claimed in OVERVIEW.json but actual events.db is empty

**Hypothesis B**: Events written to different file
- Alternative storage: `events_latest.json` (200 events)
- Format: JSON, not SQLite
- Implication: events.db is abandoned/legacy

**Hypothesis C**: MoCKA server not running during inspection
- Possibility: essence_auto_updater.py would populate events.db if running
- Current state: Server status unknown at inspection time

### Impact on Composition Chain

**Events.db is the foundation** of the composition hypothesis. If it's empty:
- Test P1-P4 (SQL queries against events.db) cannot execute
- Bidirectional linking assumptions cannot be verified
- Cross-reference population unknown

---

## Finding 2: Decision Ledger Missing Entirely

### Evidence

- **Expected location**: `/home/user/MoCKA/data/decisions/decision_ledger.jsonl`
- **Actual result**: File not found (searched 2026-08-18 19:48 UTC)
- **Claimed count**: 245 decisions (OVERVIEW.json line 380)
- **Related TODOs**: TODO_398/399/400 describe design, not data

### File Search Results

Searched all MoCKA data directories:
- `/home/user/MoCKA/data/` - **No decision_ledger.jsonl**
- `/home/user/MoCKA/data/decisions/` - **Directory doesn't exist**
- `/home/user/MoCKA/data/storage/` - **No JSONL files**

### Related Files Found But Not Decisions

- `decision_hg_chain_map.txt` (map document, not data ledger)
- `decision_gate_boundary_map.txt` (architecture doc)
- `decision_reference_map.txt` (reference doc)
- `DECISION_LAYER.md` (documentation)
- `decision/` directory (unclear what it contains)

### Classification

**Category**: D (Representation Gap)
- Design exists in DECISION_POLICY_v0.1.md
- Schema defined in TODO_399-404 notes
- But **physical storage doesn't exist**

### Implications

1. **245 decisions claimed but not findable**
   - Were they ever recorded?
   - Or recorded in different format?

2. **Decision authority chain undefined**
   - No audit trail of who approved what
   - No "related_todos" links as claimed
   - No "alternatives considered" documentation

3. **Knowledge Asset Promotion (TODO_398)**
   - Design discusses moving decisions → Knowledge Assets
   - But no source decisions to promote
   - Pipeline incomplete before starting

---

## Finding 3: Event-Decision Cross-References Minimal

### Evidence from events_latest.json

Sample of 200 events analyzed:

```
Cross-reference Field Population:
- related_event_id: 200/200 (100.0%)  ← All events have this
- free_note mentions DC_*: 2/200 (1.0%)
- short_summary mentions DC_*: 2/200 (1.0%)  ← Only 2 events!
- title mentions DECISION_MADE: 1/200 (0.5%)  ← Only 1 event!
```

### Classification

**Category**: E (Enforcement Gap)
- Linking mechanism CAN exist (fields present)
- But actual usage is 1% - not enforced
- Related_event_id is populated (100%) but not for decisions (1%)

### Root Cause

Query on first event shows:
- `related_event_id`: hash value present (some linking occurs)
- `title`: "[DECISION_MADE] DC_20260811_001" (1 example found)
- `free_note`: mostly empty or organizational metadata

**Question**: Why is related_event_id populated for ALL events but DC_ references for only 1%?

**Possibility**: related_event_id links to OTHER events (not decisions)

---

## Finding 4: Storage Architecture Fragmented

### Actual Storage Layout

```
/data/
├── events.db (0 bytes - EMPTY)
├── events_latest.json (200 events)
├── events_backup_20260401_*.csv (legacy)
├── events_corrupted.csv
├── essence_condensed.json
├── lever_essence.json
└── storage/
    ├── infield/ (local cache)
    │  ├── CORE/ (chat records)
    │  ├── REDUCED/ (processed)
    │  └── ESSENCE/ (synthesized)
    ├── outfield/ (collaborative)
    └── outbox/
       ├── RAW/ (unprocessed)
       └── PILS_DONE/ (processed outgoing)
```

### Observation

**No centralized event ledger exists.** Instead:
- Multiple JSON snapshots (events_latest.json vs. backup CSVs)
- Processing pipeline (infield → storage → outbox)
- Essence synthesis (REDUCED → ESSENCE)
- No unified event source of truth

### Classification

**Category**: B (Composed - but composed differently than assumed)

Current composition:
- Events are read from events_latest.json (200 record snapshot)
- Processed through essence_auto_updater.py (5-min interval)
- Synthesized into COMMAND CENTER context
- But **NOT persisted back to events.db**

---

## Finding 5: OVERVIEW.json Staleness Confirmed

### Evidence from Document Inspection

**OVERVIEW.json v4.1 (2026-07-07)** states:

```json
"staleness_note": "v4.1はmeta欄(updated/version)のみのseal更新...
本文はv4.0(2026-06-18)時点のまま未更新であり、
TODO_384以降・KN-004・TODO_411-425等の作業が反映されていない"
```

**Actual state inspection confirms**:
- claims "20,645 events in events.db" (FALSE - db is empty)
- claims "decision_ledger.jsonl" with 245 records (FALSE - file missing)
- claims "living context synthesis" working (PARTIAL - only 200 events)

### Classification

**Category**: F (Evidence Gap)
- OVERVIEW.json describes **intended** architecture
- NOT the **actual** operational architecture
- Gap between design document and runtime reality

---

## Critical Discrepancies Requiring Resolution

### D1: events.db Migration Status

**Question**: Was the events.csv → events.db migration (2026-06-16) completed?

**Evidence For**: OVERVIEW.json claims "events.csv complete廃止・SQLite単一化完了"  
**Evidence Against**: events.db is 0 bytes (no data)

**Next Action**: Git history search for migration commit / check essence_auto_updater.py write logic

### D2: Decision Ledger Creation

**Question**: Was decision_ledger.jsonl ever created?

**Evidence For**: TODO_361 records an "obligation to record to ledger" (2026-06-15+)  
**Evidence Against**: File not found in filesystem

**Next Action**: Git history for decision_ledger.py / check data/decisions/ permissions

### D3: Cross-Reference Population Process

**Question**: Why is related_event_id populated (100%) but DC_ references rare (1%)?

**Evidence**: Sample event data shows both fields exist but only one is used  
**Hypothesis**: related_event_id might cross-reference to OTHER events, not decisions

**Next Action**: Inspect events_latest.json related_event_id values to understand linkage pattern

### D4: MoCKA Server State

**Question**: Is MoCKA running during inspection?

**Evidence For**: essence_auto_updater.py claims 5-min refresh (would populate events.db)  
**Evidence Against**: events.db is 0 bytes (not updated)

**Next Action**: Check localhost:5000 / 5002 / 5679 availability / process status

---

## Revised Hypothesis Assessment

### Original H1: "Composition via Event Causality Works"

**Original Prediction**: Event Store (20,645) + Decision Ledger (245) + Receipt + Human Gate = complete causality chain

**Actual Finding**:
- Event Store: Empty (0 bytes)
- Decision Ledger: Missing file
- Cross-references: 1% (not enforced)
- Human Gate: Unclear integration

**Verdict**: **H1 FALSIFIED** - Composition chain does not exist in current implementation

### New Hypothesis: "Composition Partially Implemented, Fragmented Storage"

**Observation**: 200 events in events_latest.json suggest active recording somewhere, but not in designed ledger  
**Question**: Is essence_auto_updater.py reading from different source?  
**New Theory**: Living Context reads events from transient JSON snapshots, not persisted ledger

---

## Impact on Research Matrix Classification

| Asset | Previous Assumption | Updated Classification | Evidence |
|-------|-------------------|----------------------|----------|
| Event Store | B (Composed) | F (Evidence Gap) | DB empty, data elsewhere |
| Decision Ledger | B (Composed) | D (Representation Gap) | File missing entirely |
| Cross-References | B (Composed) | E (Enforcement Gap) | 1% populated, not enforced |
| Living Context | B (Composed) | C (Partially Composed) | Reads 200 events (not 20,645) |

---

## Immediate Actions Required

**Priority 1 - Verify MoCKA Server State** (20 min)
- Check if MoCKA services running (ports 5000/5002/5679)
- Inspect essence_auto_updater.py logs
- Determine if events.db is intentionally empty or broken

**Priority 2 - Locate Actual Event Data** (30 min)
- Search git history for decision_ledger.py / event write logic
- Check data/decisions/ directory permissions
- Trace where 200 events in events_latest.json originate

**Priority 3 - Explain Discrepancies** (1 hour)
- Document why OVERVIEW.json claims 20,645 (sealed 2026-06-18) vs. empty DB
- Find commit that broke events.db or explain intentional abandonment
- Determine if this is known-broken or undocumented regression

**Priority 4 - Assess Research Validity** (TBD)
- If composition chain is broken, is research still meaningful?
- Should task shift to "How to implement the composition chain"?
- Or is studying the fragmentation itself the research goal?

---

## Classification Summary

| Category | Count | Examples |
|----------|-------|----------|
| A (Existing Capability) | 0 | - |
| B (Composed Capability) | 0 | - |
| C (Partially Composed) | 1 | Living Context (100 of 200 events?) |
| D (Representation Gap) | 2 | Decision Ledger, Event-Decision linking |
| E (Enforcement Gap) | 2 | Cross-references (1% populated), Authority chain |
| F (Evidence Gap) | 2 | events.db empty, OVERVIEW staleness |
| G (UNKNOWN) | 3 | Server state, data origin, migration status |

---

**Report Status**: Framework-breaking findings require recalibration  
**Next Document**: Revised research methodology (conditional on server status)  
**Author**: Kuroko (Claude)  
**Date**: 2026-08-18

---

### Appendix: Sample Event Record

```json
{
  "event_id": "E20260811_507968211f17b",
  "title": "[DECISION_MADE] DC_20260811_001: p-DERS...",
  "channel_type": "gate",
  "when_ts": "2026-08-11T05:35:07.968237+00:00",
  "related_event_id": "a1cbd149946c23522158003ae0ab3fb07c7b118b69acc9b7894e043c2c18",
  "free_note": "decision_ledger,DC_20260811_001,Active|who_role=executor|...",
  "data_integrity": "normal",
  "lifecycle_phase": "in_operation"
}
```

Note: Only 1 of 200 events has this structure. Others lack DECISION_ metadata.
