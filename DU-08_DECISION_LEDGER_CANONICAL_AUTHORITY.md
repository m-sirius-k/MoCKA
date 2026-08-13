# DU-08: DECISION LEDGER CANONICAL AUTHORITY DECISION

**Decision Unit ID**: DU-08
**Title**: Decision Ledger Canonical Authority Decision
**Date**: 2026-08-13
**Authority**: Human Gate Review (きむら博士)
**Status**: AWAITING HUMAN GATE JUDGMENT

---

## DECISION QUESTION

**Primary**: What system should be the single authoritative source of truth for institutional decisions in MoCKA?

**Sub-questions**:
1. Should all formal decisions be recorded in decision_ledger.jsonl?
2. Should decision_ledger.jsonl contain only Human Gate-approved decisions?
3. Should MCP/SealGov decisions have equal authority as Human Gate decisions?
4. Should decision authority be verifiable or taken on faith?

---

## CURRENT STATE

**Three Parallel Decision Storage Systems**:

| System | Storage | Current Use | Authority Status |
|--------|---------|------------|-----------------|
| **Event Store** | mocka_events.db | Human Gate events | Verified (approver name) |
| **Decision Ledger** | decision_ledger.jsonl | MCP/SealGov decisions | Unverified (client-supplied) |
| **Test Ledger** | jarvis_ledger.jsonl | Jarvis test decisions | None (test-only) |

**Reality**:
- Decision Ledger contains MCP/SealGov decisions (not Human Gate)
- Human Gate decisions stay in mocka_events.db (not Decision Ledger)
- No single source of truth
- No unified authority model

**Design Intent** (implied):
- Decision Ledger should be canonical
- All decisions should be recorded there
- Decisions should be formally approved

---

## OPTION A: MOCKA_EVENTS.DB AS CANONICAL AUTHORITY

### Definition

All institutional decisions are authoritative in `mocka_events.db`. The event-sourced Human Gate system becomes the formal repository. Decision Ledger becomes a derived view/cache of events.

### Architecture

```
Human Decision Making
    |
    v
mocka_events.db [CANONICAL]
├─ Complete event history
├─ State transitions
├─ Individual approver identity
├─ Timestamps
└─ All context preserved
    |
    v
decision_ledger.jsonl [DERIVED VIEW]
    └─ Cache of approved decisions
    └─ Readable snapshot
    └─ Can be regenerated
```

### Data Model

**Primary** (mocka_events.db):
```json
{
  "event_id": "HG20260813_001ABC",
  "timestamp": "2026-08-13T10:30:45Z",
  "type": "human_gate_request",
  "action": "approve",
  "request_id": "REQUEST_123",
  "next_state": "APPROVED",
  "approver": "alice"
}
```

**Secondary** (decision_ledger.jsonl):
```json
{
  "decision_id": "DC_20260813_001",
  "request_id": "REQUEST_123",
  "event_id": "HG20260813_001ABC",
  "approved_by": "alice",
  "status": "APPROVED",
  "timestamp": "2026-08-13T10:30:45Z",
  "source": "HUMAN_GATE",
  "canonical_source": "mocka_events.db"
}
```

### Evaluation

**Strengths**:
- ✅ Individual authority preserved (approver name)
- ✅ Complete history available
- ✅ State transitions recorded
- ✅ Audit trail is comprehensive
- ✅ Replay-able from first principles
- ✅ Clear responsibility (humans → events)

**Weaknesses**:
- ❌ Requires abandoning immutable Decision Ledger
- ❌ SQLite is mutable (lacks cryptographic seal)
- ❌ MCP/SealGov decisions not in this system
- ❌ Requires ID mapping (request_id ↔ decision_id)
- ❌ Must connect all systems to mocka_events.db
- ❌ Breaks from append-only principle

**Institutional Impact**:
- Authority: Strong, verified, individual
- Audit: Complete, queryable, with context
- Governance: Clear (humans decide, system records)
- Future: Depends on mocka_events.db availability

**Risk Assessment**: MEDIUM
- Mutable storage is vulnerability
- Single point of failure (mocka_events.db)
- ID coordination complexity

---

## OPTION B: DECISION_LEDGER.JSONL AS CANONICAL AUTHORITY

### Definition

All institutional decisions are authoritative in `decision_ledger.jsonl`. The append-only ledger is the formal authority. This is the current de facto state.

### Architecture

```
Multiple Sources
├─ MCP Server
├─ SealGov
├─ Human Gate (if connected)
    |
    v
decision_ledger.jsonl [CANONICAL]
├─ Append-only immutable
├─ Formal record
├─ Single source of truth
└─ No modification possible
    |
    v
mocka_events.db [REFERENCE ONLY]
    └─ Context/history (optional)
```

### Data Model

**Primary** (decision_ledger.jsonl):
```json
{
  "decision_id": "DC_20260813_001",
  "title": "Policy Amendment",
  "approved_by": "alice",  [unverified]
  "status": "APPROVED",
  "timestamp": "2026-08-13T10:30:45Z",
  "source": "MCP"
}
```

### Evaluation

**Strengths**:
- ✅ Immutable at file level (cannot be modified)
- ✅ Append-only enforced by OS
- ✅ Simple storage model
- ✅ Current implementation
- ✅ Portable (just a file)
- ✅ No single point of failure (file is independent)

**Weaknesses**:
- ❌ No authority verification (approved_by field unverified)
- ❌ No Human Gate connection
- ❌ No duplicate prevention
- ❌ MCP can forge approval
- ❌ Incomplete audit trail (no context)
- ❌ Cannot replay state transitions
- ❌ Unsafe for AI agents (unverified authority)

**Institutional Impact**:
- Authority: Unverified, potentially forged
- Audit: Superficial, missing context
- Governance: Weak, no formal requirement
- Future: Dangerous (AI might trust false authority)

**Risk Assessment**: HIGH
- Unverified authority is critical flaw
- Duplicate decisions are possible
- Audit cannot determine truth

---

## OPTION C: HYBRID MODEL (mocka_events.db + decision_ledger.jsonl)

### Definition

Two systems with complementary roles:

1. **mocka_events.db**: Authoritative source for WHO approved and WHEN
2. **decision_ledger.jsonl**: Authoritative source for WHAT decision was formally recorded

Each is authoritative for its domain, linked by common ID.

### Architecture

```
Human Gate (Authority)
    |
    v
mocka_events.db [Authority Source]
├─ AUTHORITATIVE FOR: Who? When?
├─ Event: request_id, approver, timestamp
├─ Proof: Individual identity
└─ Mutable: Event-sourced updates possible
    |
    +─────────────────────────────┐
    |                             |
    v                             v
Decision Recording          Backfill (optional)
    |                             |
    ├─ LedgerAdapter              └─ Create historical
    │   ├─ Verify approval           Decision Records
    │   ├─ Extract approver          for past approvals
    │   └─ Create record
    |
    v
decision_ledger.jsonl [Decision Source]
├─ AUTHORITATIVE FOR: What? (formal record)
├─ Record: decision_id, approver, timestamp
├─ Proof: Immutable file entry
└─ Immutable: Append-only, cannot modify
    |
    └─ Link back to HG event for verification
```

### Data Model

**Primary Authority** (mocka_events.db):
```json
{
  "event_id": "HG20260813_001ABC",
  "timestamp": "2026-08-13T10:30:45Z",
  "request_id": "REQUEST_123",
  "action": "approve",
  "approver": "alice",
  "next_state": "APPROVED"
}
```

**Formal Record** (decision_ledger.jsonl):
```json
{
  "decision_id": "DC_20260813_001",
  "request_id": "REQUEST_123",
  "status": "APPROVED",
  "approver": "alice",
  "human_gate_event_id": "HG20260813_001ABC",
  "timestamp": "2026-08-13T10:30:45Z",
  "source": "HUMAN_GATE",
  "content_hash": "sha256:abc123..."
}
```

### Evaluation

**Strengths**:
- ✅ Individual authority verified (from events)
- ✅ Formal record is immutable (file-level)
- ✅ Audit trail is complete (both systems)
- ✅ Authority is provable (link events → ledger)
- ✅ Replay-able (events have state history)
- ✅ Safe for AI agents (authority is verifiable)
- ✅ No single point of failure (systems independent)

**Weaknesses**:
- ⚠️ Two systems must be maintained
- ⚠️ Coordination required (ID mapping)
- ⚠️ Queries span both systems
- ⚠️ Migration complexity (existing decisions)
- ⚠️ Performance (dual lookup)

**Institutional Impact**:
- Authority: Strong, verified, traceable
- Audit: Comprehensive, at two levels
- Governance: Clear (events → boundary → ledger)
- Future: Safe (AI can verify authority)

**Risk Assessment**: LOW
- Dual redundancy (two systems complement)
- Clear responsibility (who approves what)
- Verifiable at both levels

---

## COMPARATIVE ANALYSIS

| Factor | Option A | Option B | Option C |
|--------|----------|----------|----------|
| **Authority Verification** | ✅ YES | ❌ NO | ✅ YES |
| **Immutability** | ⚠️ PARTIAL | ✅ YES | ✅ YES |
| **Completeness** | ✅ EXCELLENT | ⚠️ LIMITED | ✅ EXCELLENT |
| **Queryability** | ✅ SQL | ✅ File read | ✅ BOTH |
| **Audit Trail** | ✅ DEEP | ⚠️ SURFACE | ✅ DEEP + FORMAL |
| **Replay-able** | ✅ YES | ❌ NO | ✅ YES |
| **AI Agent Safe** | ✅ POSSIBLE | ❌ RISKY | ✅ YES |
| **Mutable** | ⚠️ YES | ❌ NO | ⚠️ PARTIAL |
| **Effort to Implement** | 16 hours | 0 hours | 24 hours |
| **Single Point of Failure** | ✅ mocka_events.db | ❌ NONE | ❌ NONE |

---

## SCENARIO-BASED EVALUATION

### Scenario 1: Audit Requirement

**Question**: "Who approved decision DC_001?"

| Option | Result |
|--------|--------|
| **A** | Query mocka_events.db by request_id, find approver name, complete context |
| **B** | Query decision_ledger.jsonl by decision_id, find claimed approver (unverified) |
| **C** | Query decision_ledger.jsonl by decision_id, follow link to event, verify approver, complete context |

**Winner**: Option C (combines verification with formal record)

### Scenario 2: AI Agent Execution

**Question**: "Should an AI agent execute decision DC_001?"

| Option | Answer |
|--------|--------|
| **A** | AI queries events by request_id, verifies approver, can proceed safely |
| **B** | AI queries ledger, sees claimed approval (unverified), executes (RISKY) |
| **C** | AI queries ledger, verifies event link, checks approver, executes safely |

**Winner**: Option C (safe verification possible)

### Scenario 3: Governance Compliance

**Question**: "Prove this decision was formally approved."

| Option | Evidence |
|--------|----------|
| **A** | Show event record from mocka_events.db (mutable, but events prove sequence) |
| **B** | Show ledger entry (immutable, but authority unverified) |
| **C** | Show ledger entry + event link (immutable record + verified authority) |

**Winner**: Option C (dual proof)

---

## DECISION CRITERIA

### Evaluation Dimensions

1. **Authority Assurance**: How critical is verifying decision authority?
   - If CRITICAL → Choose Option C or A
   - If IMPORTANT → Choose Option C
   - If OPTIONAL → Choose Option A or B

2. **Immutability**: How critical is preventing modification?
   - If CRITICAL → Choose Option B or C
   - If IMPORTANT → Choose Option C
   - If OPTIONAL → Choose Option A or C

3. **Auditability**: How complete must audit trail be?
   - If COMPREHENSIVE → Choose Option A or C
   - If IMPORTANT → Choose Option C
   - If OPTIONAL → Choose Option B

4. **AI Integration**: Will AI agents need to trust authority?
   - If YES → Choose Option C (only safe option)
   - If MAYBE → Choose Option C
   - If NO → Choose Option A or B

5. **Simplicity**: How simple should the system be?
   - If CRITICAL → Choose Option B
   - If IMPORTANT → Choose Option A
   - If OPTIONAL → Choose Option C

---

## IMPLEMENTATION PATHWAYS

### If Option A Chosen

**Approach**: Rebuild around event-sourced authority
1. Make mocka_events.db the canonical source
2. Implement decision_ledger as derived cache
3. Connect all systems to query events first
4. Add cryptographic signing to events (optional)

**Timeline**: 4-6 weeks
**Risk**: Mutable storage vulnerability

### If Option B Chosen

**Approach**: Accept current state as-is
1. No changes to existing systems
2. Acknowledge authority is unverified
3. Trust MCP/SealGov to verify externally
4. Implement governance rules elsewhere

**Timeline**: 0 weeks
**Risk**: Unverified authority (HIGH)

### If Option C Chosen

**Approach**: Establish hybrid model with boundary
1. Implement LedgerAdapter authority boundary (DU-07)
2. Connect systems through boundary
3. Decision Ledger references mocka_events.db
4. Queries can span both systems

**Timeline**: 4-6 weeks
**Risk**: Coordination complexity (LOW)

---

## DECISION INPUTS FOR HUMAN GATE

### Questions to Clarify

1. **Authority Requirement**: Is decision authority important enough to verify and preserve?

2. **Immutability vs. Authority Trade-off**: Is a mutable authority source acceptable?

3. **Audit Standard**: How deep must audit trails be?

4. **Future AI**: Will AI agents ever need to trust decision authority?

5. **Governance Clarity**: Should canonical authority be obvious to all stakeholders?

---

## RECOMMENDATION SUMMARY

| Aspect | Option A | Option B | Option C |
|--------|----------|----------|----------|
| **Authority verification** | ✅ YES | ❌ NO | ✅ YES |
| **Institutional intent** | ⚠️ PARTIAL | ❌ NO | ✅ YES |
| **Design soundness** | ⚠️ GOOD | ❌ POOR | ✅ EXCELLENT |
| **Implementation effort** | ⚠️ MODERATE | ✅ NONE | ⚠️ MODERATE |
| **AI safety** | ⚠️ POSSIBLE | ❌ RISKY | ✅ SAFE |
| **Audit completeness** | ✅ EXCELLENT | ⚠️ LIMITED | ✅ EXCELLENT |

---

**DECISION UNIT DU-08 COMPLETE**

No recommendation made. Authority: Human Gate (きむら博士)

