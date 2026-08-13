# DU-09: LEGACY EVENT STORE BOUNDARY DECISION

**Decision Unit ID**: DU-09
**Title**: Legacy Event Store Boundary Decision
**Date**: 2026-08-13
**Authority**: Human Gate Review (きむら博士)
**Status**: AWAITING HUMAN GATE JUDGMENT

---

## DECISION QUESTION

**Primary**: Should `mocka_events.db` be reclassified from Authority Store to Evidence Event Store?

**Sub-questions**:
1. What is the institutional role of mocka_events.db?
2. Should it be the source of truth for decision authority, or only evidence of decisions?
3. What is the relationship between Human Gate events and formal Decision Ledger entries?
4. Can mocka_events.db be bypassed in production?

---

## CURRENT STATE

**mocka_events.db Current Role**:

| Aspect | Current Status |
|--------|----------------|
| **Storage** | SQLite database (mutable) |
| **Contents** | Human Gate events (event-sourced) |
| **Authority** | Implicit (approver names, timestamps) |
| **Usage** | Human Gate state management |
| **Connection to Decision Ledger** | NONE (disconnected) |
| **Bypassable** | YES (MCP writes directly to Decision Ledger) |

**Current Flow**:
```
Human Approval
    |
    v
PHI-OS Human Gate
    |
    v
mocka_events.db [stored]
    
    (NO connection to Decision Ledger)
    
MCP/SealGov (independent)
    |
    v
decision_ledger.jsonl [direct write, no HG check]
```

**Key Gap**: Human Gate decisions don't propagate to Decision Ledger. Two systems are independent.

---

## OPTION A: MOCKA_EVENTS.DB AS AUTHORITY STORE

### Definition

mocka_events.db is the institutional authority source for decision decisions. All Human Gate decisions are authoritative when recorded here. Decision Ledger entries must reference this source.

### Role

```
AUTHORITY STORE:
- Primary source of truth for Human Gate decisions
- Individual approver identity preserved
- Complete event history available
- Can be replayed to reconstruct any state
- Audit trail originates here
- Formal decisions are recorded here first
```

### Responsibilities

1. **Approval Authority**
   - Records who approved what
   - When they approved it
   - What state transitions occurred
   - All context available

2. **Institutional Decision Record**
   - Formal authority for Human Gate decisions
   - Cannot be overridden by MCP
   - Cannot be overridden by SealGov
   - Must be queried before accepting external decisions

3. **Audit Source**
   - Complete event trail
   - Timestamps and state history
   - Individual identity preservation
   - Cannot be modified retroactively (event-sourced)

### Consequences

**Benefits**:
- ✅ Authority is preserved and individual
- ✅ Complete history is available
- ✅ Event-sourced allows replay
- ✅ Institutional decisions are traceable
- ✅ Clear responsibility (humans → events)

**Requirements**:
- ⚠️ mocka_events.db must be accessible
- ⚠️ All systems must query it for authority
- ⚠️ ID coordination needed (request_id ↔ decision_id)
- ⚠️ LedgerAdapter must use it for verification

**Risks**:
- ❌ SQLite is mutable (not cryptographically sealed)
- ❌ Admin access can modify records
- ❌ Single point of failure (if DB unavailable)
- ❌ Requires integration work (PHI-OS → LedgerAdapter)

### Institutional Impact

Decision authority is rooted in Human Gate approvals. All formal decisions trace back to this source. Institutional governance is clear: humans decide, systems record.

---

## OPTION B: MOCKA_EVENTS.DB AS EVIDENCE EVENT STORE

### Definition

mocka_events.db is reclassified as a supporting evidence store, not the authoritative source. It provides context and history but is not the formal authority. Decision Ledger is authoritative.

### Role

```
EVIDENCE STORE:
- Provides historical context for decisions
- Shows past approvals and rejections
- Useful for audit context
- NOT authoritative for formal decisions
- NOT required for decision validity
- Decisions can exist without corresponding events
```

### Responsibilities

1. **Historical Context**
   - Provides background information
   - Shows decision-making process
   - Useful for understanding rationale
   - Optional for validation

2. **Audit Context (not authority)**
   - Supplementary information
   - Shows workflow history
   - Helps explain decisions
   - Not required proof

3. **Reference Material**
   - Can be queried for context
   - Cannot block decisions
   - Cannot override Decision Ledger
   - Cannot enforce requirements

### Consequences

**Benefits**:
- ✅ No integration required
- ✅ Current state continues
- ✅ MCP/SealGov independent
- ✅ Simple, no coordination needed
- ✅ No refactoring required

**Costs**:
- ❌ Authority is lost
- ❌ Individual approver identity not in formal record
- ❌ Decisions can be created without Human Gate approval
- ❌ MCP can forge approval (no verification)
- ❌ Institutional governance is weakened

**Risks**:
- ❌ Authority model is fragmented
- ❌ Audit trail is incomplete (events not linked to decisions)
- ❌ Cannot verify decision authority
- ❌ Unsafe for AI agents (unverified authority)

### Institutional Impact

Decision authority is NOT based on Human Gate approval. Decisions can be recorded in Decision Ledger without institutional verification. Governance is weakened.

---

## OPTION C: HYBRID ROLE (Authority + Evidence)

### Definition

mocka_events.db serves dual role:

1. **Authority for Human Gate Decisions**: Approvals recorded here are authoritative for Human Gate-initiated decisions
2. **Evidence for Historical Context**: Provides supplementary information for all decisions

### Role

```
PRIMARY (Authority):
- Human Gate approvals are authoritative
- Individual identity is preserved
- Can be queried for authority verification
- Must be checked before accepting HG-derived decisions

SECONDARY (Evidence):
- Provides historical context for all decisions
- Shows workflow and deliberation
- Useful for audit understanding
- Supplementary information
```

### Responsibilities

1. **Authority for Human Gate Path**
   - Records approvals as authoritative
   - Queries required for HG-derived decisions
   - Individual identity preserved
   - Replay-able history

2. **Evidence for All Decisions**
   - Provides context and background
   - Shows decision history
   - Explains rationale
   - Aids audit understanding

3. **Boundary Enforcement**
   - LedgerAdapter queries events
   - Verifies HG approval before Decision Ledger write
   - Links records for traceability
   - Prevents unapproved decisions

### Consequences

**Benefits**:
- ✅ Authority preserved for HG decisions
- ✅ Context available for all decisions
- ✅ Traceability established
- ✅ Clear dual role
- ✅ Supports governance

**Requirements**:
- ⚠️ LedgerAdapter must query events
- ⚠️ ID coordination needed
- ⚠️ Integration work required
- ⚠️ Query performance optimization

**Risks**:
- ⚠️ Two-system coordination complexity
- ⚠️ Queries must span both systems
- ⚠️ Integration effort required
- ⚠️ Migration of existing decisions

### Institutional Impact

Decision authority is dual-layered: Human Gate approvals are authoritative, supporting evidence is available from events. Institutional governance is clear and verifiable.

---

## COMPARATIVE ANALYSIS

| Aspect | Option A (Authority) | Option B (Evidence) | Option C (Dual) |
|--------|----------|----------|----------|
| **Authority Status** | ✅ YES | ❌ NO | ✅ YES (for HG) |
| **Evidence Available** | ✅ YES | ✅ YES | ✅ YES |
| **Individual Identity** | ✅ YES | ❌ NO | ✅ YES (for HG) |
| **Integration Required** | ⚠️ YES | ✅ NO | ⚠️ YES |
| **Refactoring Needed** | ⚠️ YES | ✅ NO | ⚠️ YES |
| **Institutional Governance** | ✅ STRONG | ❌ WEAK | ✅ STRONG |
| **Audit Completeness** | ✅ COMPLETE | ⚠️ LIMITED | ✅ COMPLETE |
| **AI Agent Safe** | ✅ YES | ❌ NO | ✅ YES |
| **Implementation Effort** | ⚠️ MODERATE | ✅ MINIMAL | ⚠️ MODERATE |

---

## INSTITUTIONAL IMPLICATIONS

### If Option A (Authority) Chosen

**Meaning**: "mocka_events.db is the institutional source of truth for Human Gate decisions"

**Consequence**: 
- All Human Gate approvals must be in events.db to be valid
- Decision Ledger must reference events for authority
- MCP must verify HG approval before recording
- Institutional governance is verifiable

**Impact on Current Systems**:
- MCP: Must check events.db before writing
- SealGov: Must link to relevant HG approval
- PHI-OS: Continues recording approvals (becomes more important)
- Decision Ledger: Becomes formal record (with authority link)

### If Option B (Evidence) Chosen

**Meaning**: "mocka_events.db is optional context, not authoritative"

**Consequence**:
- Decisions can exist in Decision Ledger without events
- MCP approvals don't need HG backing
- Authority model is fragmented
- Institutional governance is weakened

**Impact on Current Systems**:
- MCP: Can write without checking events
- SealGov: No authority linking required
- PHI-OS: Events become less important (optional context)
- Decision Ledger: Becomes sole authority (but unverified)

### If Option C (Dual) Chosen

**Meaning**: "mocka_events.db is authoritative for HG decisions, evidence for others"

**Consequence**:
- Human Gate decisions have strong authority
- Other decisions (MCP/SealGov) can be independent
- Authority model is clear and layered
- Institutional governance is preserved for HG path

**Impact on Current Systems**:
- MCP: Optional use of HG authority (or independent)
- SealGov: Uses GL7 authority, can reference HG
- PHI-OS: Central to authority model
- Decision Ledger: References events where applicable

---

## SCENARIO-BASED EVALUATION

### Scenario 1: Retrospective Audit

**Question**: "Prove that decision DC_001 was properly authorized."

| Option | Answer |
|--------|--------|
| **A** | Query events.db by request_id, show approver and timestamp, complete proof |
| **B** | Query Decision Ledger, show claimed approver (but cannot verify), incomplete proof |
| **C** | Query Decision Ledger, follow link to event, show approver, complete proof (for HG) |

**Best Answer**: Option A or C

### Scenario 2: Compliance Audit

**Question**: "Which decisions were approved by humans?"

| Option | Answer |
|--------|--------|
| **A** | Query events.db (all HG events are by humans, definitive) |
| **B** | Query Decision Ledger, check actor field (unverified, unreliable) |
| **C** | Query Decision Ledger for HG-source decisions, link to events (reliable for HG) |

**Best Answer**: Option A or C

### Scenario 3: Governance Validation

**Question**: "Should this decision be allowed?"

| Option | Logic |
|--------|-------|
| **A** | IF found in events.db AND approved state THEN allowed |
| **B** | IF found in Decision Ledger THEN allowed (no verification) |
| **C** | IF (HG source AND found in events.db) OR (GL7 approved) THEN allowed |

**Best Answer**: Option A or C

---

## RELATIONSHIP TO OTHER DECISION UNITS

### Dependency on DU-07 (LedgerAdapter)

If DU-07 chooses **Option B** (adopt LedgerAdapter):
- mocka_events.db becomes input to LedgerAdapter
- LedgerAdapter queries events for authority
- Options A or C become more viable (events are actively used)

If DU-07 chooses **Option A** (maintain current):
- mocka_events.db remains disconnected
- Option B becomes more likely (evidence only)

### Dependency on DU-08 (Canonical Authority)

If DU-08 chooses **Option A** (events as canonical):
- mocka_events.db must be Option A (Authority Store)
- Consistent with events-based model

If DU-08 chooses **Option B** (ledger as canonical):
- mocka_events.db could be Option B (Evidence only)
- Decision Ledger is primary authority

If DU-08 chooses **Option C** (hybrid):
- mocka_events.db should be Option C (Dual role)
- Complementary model

---

## DECISION CRITERIA

### Evaluation Dimensions

1. **Authority Priority**: How important is verifying authority?
   - If CRITICAL → Choose Option A or C
   - If IMPORTANT → Choose Option C
   - If OPTIONAL → Choose Option B

2. **Governance Requirement**: Does institutional governance depend on this?
   - If YES → Choose Option A or C
   - If MAYBE → Choose Option C
   - If NO → Choose Option B

3. **Integration Cost**: How much can be spent on integration?
   - If HIGH BUDGET → Choose Option A or C
   - If MEDIUM BUDGET → Choose Option C
   - If LOW BUDGET → Choose Option B

4. **AI Safety**: Will AI agents use this for decisions?
   - If YES → Choose Option A or C
   - If MAYBE → Choose Option C
   - If NO → Choose Option B

---

## RECOMMENDATION SUMMARY

| Aspect | Option A (Authority) | Option B (Evidence) | Option C (Dual) |
|--------|----------|----------|----------|
| **Alignment with institutional intent** | ✅ YES | ❌ NO | ✅ YES |
| **Supports governance** | ✅ YES | ❌ NO | ✅ YES |
| **Authority verification** | ✅ YES | ❌ NO | ✅ YES (for HG) |
| **Implementation effort** | ⚠️ MODERATE | ✅ NONE | ⚠️ MODERATE |
| **Audit completeness** | ✅ STRONG | ⚠️ WEAK | ✅ STRONG |
| **Coordination complexity** | ⚠️ MEDIUM | ✅ NONE | ⚠️ MEDIUM |

---

**DECISION UNIT DU-09 COMPLETE**

No recommendation made. Authority: Human Gate (きむら博士)

