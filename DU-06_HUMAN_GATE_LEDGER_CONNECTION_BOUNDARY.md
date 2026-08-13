# DU-06: HUMAN GATE → LEDGER CONNECTION BOUNDARY

**Decision Unit ID**: DU-06  
**Title**: Human Gate Decisions and Decision Ledger Connection Architecture  
**Date**: 2026-08-13  
**Authority**: Human Gate Review  
**Status**: AWAITING HUMAN GATE JUDGMENT  

---

## DECISION QUESTION

**Primary**: Should Human Gate decisions require a mandatory controlled persistence path through LedgerAdapter before becoming formal Decision Ledger records?

**Sub-questions**:
1. Should Decision Ledger contain only approved Human Gate decisions?
2. Should MCP/SealGov decisions be separate from formal Human Gate decisions?
3. What is the institutional relationship between Human Gate approvals and Decision Ledger entries?
4. Who is the authoritative source for decision records?

---

## BACKGROUND

### Current State

**Architectural Disconnect**:
```
PHI-OS Human Gate (Production)
    └─ mocka_events.db (human_gate_events table)
        └─ Decisions APPROVED/REJECTED
        
    NO CONNECTION TO
    
    data/decisions/decision_ledger.jsonl (Production Decision Ledger)
        └─ Contains MCP decisions
        └─ Contains SealGov decisions
        └─ Does NOT contain Human Gate decisions
```

**Three Parallel Decision Systems**:
1. **mocka_events.db**: Human Gate request state (event-sourced)
2. **decision_ledger.jsonl**: MCP/SealGov decisions (append-only)
3. **jarvis_ledger.jsonl**: Test decisions (Jarvis only)

**Design Intent (Jarvis Path)**:
```
HumanGate.approve() → LedgerAdapter → LedgerStore → Decision Ledger
(Designed but not integrated into production)
```

**Actual Reality (Production)**:
```
PHI-OS Human Gate → mocka_events.db
                 (NOT connected to Decision Ledger)

MCP/SealGov → decision_ledger.jsonl
           (bypasses Human Gate)
```

### Problem Statement

No guaranteed path from Human Gate approval to Decision Ledger persistence. Three independent systems with no coordination:
- Human decisions in mocka_events.db
- MCP/SealGov decisions in decision_ledger.jsonl
- Test decisions in jarvis_ledger.jsonl
- No unified authority model

---

## OPTION A: MAINTAIN CURRENT DISCONNECTED ARCHITECTURE

### Description
Accept that:
- PHI-OS Human Gate and Decision Ledger are independent systems
- Decision Ledger serves MCP/SealGov decisions only (not Human Gate)
- Human Gate decisions remain in mocka_events.db
- No unified authority model required

### Benefits

1. **Operational Independence** (HIGH)
   - Human Gate operates independently
   - MCP/SealGov decisions proceed independently
   - No dependency between systems

2. **No Migration Required** (MEDIUM)
   - Current state continues
   - No refactoring needed
   - No data movement

3. **Different Use Cases** (MEDIUM)
   - Human Gate: Interactive decision approval
   - MCP: Rapid operational decisions
   - SealGov: Governance decisions
   - Each system optimized for its purpose

4. **Simple Authority Model** (MEDIUM)
   - Human Gate: mocka_events.db is authoritative
   - MCP/SealGov: decision_ledger.jsonl is authoritative
   - Clear separation of concerns

### Risks

1. **No Unified Audit Trail** (HIGH)
   - Decisions split across two ledgers
   - Audit queries must span both
   - Difficult to trace decision lifecycle

2. **Authority Ambiguity** (HIGH)
   - MCP decisions lack Human Gate approval
   - SealGov decisions are governance-approved only
   - Mixed authority models

3. **Schema Misalignment** (MEDIUM)
   - DECISION_LEDGER_SCHEMA_v1.md implies formal decisions
   - But Decision Ledger is MCP/SealGov only
   - Schema doesn't match actual contents

4. **Lost Human Authority** (MEDIUM)
   - Even if Human Gate approves, decision doesn't appear in Decision Ledger
   - Decision authority doesn't propagate
   - Two separate approval paths

### Long-Term Impact

- MoCKA operates with dual decision authority
- Audit becomes more complex (query both systems)
- Future features must account for two ledger sources
- Governance authority remains unclear

### Governance Impact

- Lightweight governance (no new requirements)
- But: Weaker audit assurance
- No unified decision authority

### Migration Difficulty

- **Immediate**: No changes needed
- **Future**: If unified ledger needed later, migration will be complex

---

## OPTION B: REQUIRE HUMAN GATE → LEDGERADAPTER → LEDGERSTORE PATH

### Description
Integrate Human Gate approvals into Decision Ledger:
- When Human Gate approves a decision_id, automatically record in Decision Ledger
- Use LedgerAdapter as mandatory interface
- LedgerStore enforces uniqueness
- Single Decision Ledger source of truth

**Modified Flow**:
```
Human Gate Approval
    │
    ├─ Update: mocka_events.db (APPROVED state)
    │
    └─ Trigger: Decision Record creation
        ├─ LedgerAdapter.record(decision_id, "APPROVED")
        ├─ LedgerStore.save() [with duplicate prevention]
        └─ Persist to: data/decisions/decision_ledger.jsonl
```

### Benefits

1. **Unified Decision Authority** (HIGH)
   - All formal decisions in one Decision Ledger
   - Single source of truth
   - Clear authority model

2. **Human Authority Preserved** (HIGH)
   - Human Gate approval creates Decision Ledger entry
   - Authority chain: Human → approval → ledger
   - Traceable decisions

3. **Duplicate Prevention** (MEDIUM)
   - LedgerStore prevents duplicate decision_ids
   - Uniqueness guaranteed
   - Schema requirement met

4. **Audit Simplification** (MEDIUM)
   - Single Decision Ledger to query
   - No split authority
   - Clear decision lifecycle

### Risks

1. **Integration Complexity** (MEDIUM)
   - Must connect PHI-OS Human Gate to LedgerAdapter
   - Must ensure decision_id matches
   - Must handle failures gracefully

2. **Dependency Chain** (MEDIUM)
   - Decision Ledger depends on Human Gate
   - If Human Gate fails, Decision Ledger incomplete
   - New coupling between systems

3. **Decision Ledger Content Changes** (MEDIUM)
   - Currently has MCP + SealGov decisions
   - Adding Human Gate decisions changes semantics
   - MCP decisions are unverified, Human Gate are verified

4. **Authority Model Conflict** (MEDIUM)
   - MCP decisions: client-provided approved_by (unverified)
   - Human Gate decisions: approver name (unverified, but from authorized user)
   - SealGov decisions: system:seal_governance_gate (GL7 verified)
   - Mixed trust levels in same ledger

### Long-Term Impact

- Clearer institutional decision authority
- Single source for all decision records
- Must distinguish between verified (HG, SealGov) and unverified (MCP)
- Decision Ledger becomes central authority

### Governance Impact

- Strengthens decision authority
- Clarifies approval workflow
- Requires governance rule: "Only authorized approvals create Decision Ledger entries"

### Migration Difficulty

- **Immediate**: Add trigger/listener from PHI-OS to LedgerAdapter (medium effort)
- **Immediate**: Handle decision_id coordination (medium effort)
- **One-time**: Backfill Decision Ledger with historic Human Gate decisions (low effort, optional)
- **Ongoing**: Ensure PHI-OS and Decision Ledger stay synchronized

---

## OPTION C: SEPARATE CONSTITUTIONAL AND OPERATIONAL DECISIONS

### Description
Create two separate ledgers by decision type:

1. **Constitutional Decision Ledger** (formal, signed decisions)
   - Human Gate approvals: YES
   - GL7 governance decisions: YES
   - Cryptographic signatures: maybe
   - High audit assurance

2. **Operational Decision Log** (rapid, transient decisions)
   - MCP rapid decisions: YES
   - System decisions: YES
   - Low ceremony, high frequency
   - Lower audit requirements

### Benefits

1. **Appropriate Governance Per Type** (HIGH)
   - Constitutional: Strong authority, uniqueness, audit
   - Operational: Flexible, fast, less ceremony

2. **No Mixed Authority** (MEDIUM)
   - Clear separation of decision types
   - No confusion about verification level
   - Readers know which ledger to trust

3. **Scalability** (MEDIUM)
   - Operational log can be rotated/archived quickly
   - Constitutional ledger is immutable, minimal size
   - Performance optimized per type

4. **Future Extensions** (MEDIUM)
   - Constitutional decisions can add signatures
   - Operational log can add TTL
   - Different retention policies

### Risks

1. **Routing Complexity** (MEDIUM)
   - Must decide: is this decision constitutional or operational?
   - Risk of wrong categorization
   - Governance rules needed

2. **Audit Span** (MEDIUM)
   - Audit queries must span both ledgers
   - Risk of missing decisions
   - More complex audit procedures

3. **Migration Effort** (MEDIUM)
   - Split existing decision_ledger.jsonl
   - Categorize existing decisions
   - Update tools to handle both

4. **Ambiguity** (MEDIUM)
   - MCP decisions: are they constitutional? (probably not)
   - SealGov decisions: are they constitutional? (probably yes)
   - Rules needed for categorization

### Long-Term Impact

- Clear decision tiers
- Different retention/archival policies
- Schema evolution: two ledgers can diverge
- Governance rules needed for routing

### Governance Impact

- Clarifies decision types
- Enables tier-based governance
- Requires classification rules

### Migration Difficulty

- **Immediate**: Create Constitutional Ledger (low effort)
- **Immediate**: Update Human Gate to use Constitutional Ledger (medium effort)
- **Immediate**: Keep MCP decisions in Operational Log (low effort)
- **One-time**: Categorize existing decisions (medium effort)
- **Documentation**: Clear classification rules (low effort)

---

## OPTION D: DEFER UNTIL ARCHITECTURE REDESIGN

### Description
Postpone connection decision until Phase 5+ architecture redesign:
- Current state acceptable as interim
- Future architecture may provide better solution
- Wait for full governance model clarification

### Benefits

1. **No Immediate Work** (HIGH)
   - Zero implementation effort
   - No breaking changes
   - No migration complexity

2. **Wait for Full Picture** (MEDIUM)
   - Phase 5 redesign may address root causes
   - Authority model may be clarified globally
   - Better solution may emerge

### Risks

1. **Technical Debt Accumulates** (HIGH)
   - Disconnected systems persist
   - No authority model clarity
   - Audit remains complex

2. **Deferred Complexity** (MEDIUM)
   - Future solution must handle current state
   - Backfill of historic decisions may be needed
   - Migration will be complex

3. **Governance Gap** (HIGH)
   - Decision authority remains ambiguous
   - No institutional policy on decision recording
   - MCP decisions continue unverified

### Long-Term Impact

- Current state persists until Phase 5+
- No progress on decision authority
- Future work may be more expensive

### Governance Impact

- No new governance required
- But: Governance authority remains unclear

---

## COMPARATIVE ANALYSIS

| Factor | Option A | Option B | Option C | Option D |
|--------|----------|----------|----------|----------|
| **Implementation Effort** | None | Medium | Medium-High | None |
| **Integration Complexity** | None | Medium | Medium-High | None |
| **Unified Authority** | ❌ NO | ✅ YES | ✅ YES (per tier) | ❌ NO |
| **Human Authority Preserved** | ❌ NO | ✅ YES | ✅ YES | ❌ NO |
| **Audit Simplicity** | ⚠️ Two ledgers | ✅ One ledger | ⚠️ Two ledgers | ⚠️ Two systems |
| **Duplicate Prevention** | ❌ NO | ✅ YES | ✅ YES (const.) | ❌ NO |
| **Schema Alignment** | ❌ NO | ✅ YES | ✅ YES (const.) | ❌ NO |
| **Governance Clarity** | ❌ NO | ✅ YES | ✅ YES | ❌ NO |
| **Immediate Actionable** | ✅ YES | ✅ YES | ⚠️ Complex | ✅ YES |

---

## SCENARIO-BASED EVALUATION

### Scenario 1: Audit Compliance

Requirement: Prove every Human Gate approval corresponds to a decision record

| Option | Suitability |
|--------|-----------|
| A | ❌ POOR (approval in mocka_events, no Decision Ledger entry) |
| B | ✅ EXCELLENT (human approval triggers Decision Ledger entry) |
| C | ✅ EXCELLENT (constitutional ledger contains human decisions) |
| D | ❌ POOR (problem unresolved) |

### Scenario 2: Multi-Phase Decisions

Requirement: Human Gate initiates decision, MCP/SealGov completes it

| Option | Suitability |
|--------|-----------|
| A | ⚠️ FAIR (decisions split across systems) |
| B | ✅ GOOD (all in Decision Ledger, MCP completion updates record) |
| C | ⚠️ FAIR (initiation in constitutional, completion in operational) |
| D | ⚠️ FAIR (problem deferred) |

### Scenario 3: Authority Verification

Requirement: Prove decision was authorized by Human Gate

| Option | Suitability |
|--------|-----------|
| A | ⚠️ FAIR (must query mocka_events, no Decision Ledger evidence) |
| B | ✅ EXCELLENT (Decision Ledger entry proves Human Gate approval) |
| C | ✅ EXCELLENT (constitutional ledger proves authorization) |
| D | ⚠️ FAIR (problem deferred) |

---

## DECISION INPUTS FOR HUMAN GATE

### Questions to Clarify

1. **Authority Model**: Should all formal decisions be approved by Human Gate or is MCP/SealGov approval sufficient?
2. **Decision Scope**: Should Decision Ledger contain only Human Gate decisions or all decisions (MCP/SealGov/HG)?
3. **Verification Level**: Should MCP decisions have same verification as Human Gate decisions?
4. **Audit Requirement**: What audit assurance is required for decision records?
5. **Constitutional vs. Operational**: How to distinguish decision types?
6. **Human Authority**: Can decisions be valid without Human Gate approval?

### Critical Dependencies

- Authority model → affects which decisions are recorded
- Audit requirements → affects verification level
- Decision types → affects ledger structure
- Future governance → affects current design

---

**Document Status**: AWAITING HUMAN GATE DECISION  
**Authority**: きむら博士 (Human Gate)  
**No recommendation provided**  
**Evidence base**: Complete forensic analysis
