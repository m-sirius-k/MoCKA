# DU-05: DECISION LEDGER WRITE AUTHORITY BOUNDARY

**Decision Unit ID**: DU-05  
**Title**: Decision Ledger Write Authority Boundary Architecture  
**Date**: 2026-08-13  
**Authority**: Human Gate Review  
**Status**: AWAITING HUMAN GATE JUDGMENT  

---

## DECISION QUESTION

**Primary**: Should all formal Decision Records be required to pass through a single validated persistence boundary?

**Sub-questions**:
1. Is LedgerStore the correct boundary, or should another mechanism be used?
2. Should MCP server decisions and SealGovernance decisions use the same boundary?
3. What fail-closed behavior is required for duplicate detection?
4. How should operational vs. constitutional decisions be distinguished?

---

## BACKGROUND

### Current State

**Two Active Production Paths**:
1. **MCP Server Path** (`mocka_mcp_server.py:_append_decision`)
   - Direct file append
   - No duplicate prevention
   - No authority verification
   - Any MCP client can write

2. **SealGovernance Path** (`governance/seal_governance_gate.py:_record_decision_unit`)
   - Direct file append
   - GL7 governance check
   - No duplicate prevention at write time
   - GL7 validates authority before execution

**Designed But Unused Boundary**:
- **LedgerStore** (`runtime/jarvis/record/persistence/ledger_store.py`)
  - Implements duplicate prevention
  - Not integrated into production paths
  - Used only in tests via LedgerAdapter

### Problem Statement

The Decision Ledger can contain duplicate decision_id entries because:
1. MCP path writes without checking for existing records
2. SealGovernance path writes without checking for existing records
3. LedgerStore (which could prevent this) is not used in production
4. No coordination between the two paths

This violates the implicit assumption in DECISION_LEDGER_SCHEMA_v1.md that decision_id values should be unique.

### Evidence

| Evidence | Finding |
|----------|---------|
| Code review | 2 production write paths, both bypass duplicate prevention |
| Test coverage | No tests verify duplicate scenario handling |
| Schema intent | DECISION_LEDGER_SCHEMA_v1.md implies uniqueness but doesn't enforce it |
| Incident history | No recorded duplicate incidents (may indicate low frequency or poor detection) |

---

## OPTION A: MAINTAIN CURRENT MULTI-PATH WRITE ARCHITECTURE

### Description
Keep the current design:
- MCP server writes directly for operational decisions
- SealGovernance writes directly for governance decisions
- LedgerStore remains unused
- Uniqueness is NOT enforced

### Benefits

1. **Backward Compatibility**
   - No changes to existing MCP interface
   - No refactoring of SealGovernanceGate
   - Operational decisions continue unchanged

2. **Flexibility**
   - MCP can support rapid decision updates (create new record with same decision_id)
   - SealGovernance can retry operations independently

3. **Performance**
   - No read-before-write overhead
   - No file locking mechanism needed
   - Direct append is fastest path

4. **Separation of Concerns**
   - Operational decisions (MCP) stay fast/flexible
   - Governance decisions (SealGov) stay structural/verified
   - No shared boundary logic

### Risks

1. **Semantic Ambiguity** (HIGH)
   - Duplicate decision_id values are silently allowed
   - Reader cannot distinguish error from intentional update
   - supersedes chain becomes unclear

   **Example**:
   ```
   {"decision_id": "DC_001", "status": "Active", "title": "A"}
   {"decision_id": "DC_001", "status": "Active", "title": "B"}
   
   Is B a replacement, a mistake, or an independent decision?
   Ledger provides no indication.
   ```

2. **Loss of Uniqueness Guarantee** (HIGH)
   - Schema says "decision_id uniqueness" but not enforced
   - Caller cannot rely on one-decision-per-id assumption
   - Related_documents/events references become ambiguous

3. **Audit Trail Gap** (MEDIUM)
   - No record of duplicate attempts
   - No indication of retry/re-execution
   - Difficult to trace which version is authoritative

4. **Fail-Silent Behavior** (MEDIUM)
   - If duplication occurs, no error is raised
   - Caller cannot detect collision
   - Silent data loss (old record unintentionally obscured)

5. **Governance Authority Ambiguity** (MEDIUM)
   - MCP path has no authority check
   - SealGovernance path has authority check
   - Mixed authority model creates confusion

### Long-Term Impact

- Operational model becomes "append-only log of decisions (not necessarily unique)"
- Schema documentation must be updated to reflect this
- Readers must implement deduplication logic
- Audit queries become more complex (need to filter by latest version)

### Governance Impact

- Lightweight governance (minimum intervention)
- No new validation infrastructure needed
- But: Reduces audit assurance
- Authority becomes implicit (approved_by field is unverified)

### Migration Difficulty

- **Immediate**: No migration needed
- **Future**: If uniqueness is later required, existing ledger may have duplicates that break migration

---

## OPTION B: REQUIRE LEDGERSTORE VALIDATION AS MANDATORY FORMAL DECISION BOUNDARY

### Description
Refactor production paths to use LedgerStore:
- All decision writes (MCP, SealGov, future paths) go through LedgerStore.save()
- LedgerStore enforces uniqueness
- Duplicate submissions are rejected (currently silent, must implement fail-closed)
- Single source of truth for decision storage

### Benefits

1. **Unified Boundary** (HIGH)
   - One validation point for all decisions
   - Consistent duplicate handling
   - Easier to audit and verify

2. **Uniqueness Enforced** (HIGH)
   - decision_id guaranteed unique
   - Schema requirement satisfied
   - Reader doesn't need deduplication logic

3. **Clear Failure Mode** (MEDIUM)
   - Duplicate is detected and explicitly rejected
   - Caller can handle rejection
   - Audit trail can record rejection attempt

4. **Schema Alignment** (MEDIUM)
   - DECISION_LEDGER_SCHEMA_v1.md intent realized
   - Implicit assumptions become explicit
   - Clear contracts for callers

5. **Governance Strengthening** (MEDIUM)
   - Centralized authority point
   - Easier to add future checks (role-based, time-based, etc.)
   - Clear upgrade path for security enhancements

### Risks

1. **Performance Overhead** (MEDIUM)
   - Must read entire ledger before each write
   - Ledger grows: O(n) read cost
   - For large ledgers, this could be problematic
   - Possible bottleneck for high-frequency decisions

   **Mitigation**: Implement hash index or in-memory cache

2. **Race Conditions** (MEDIUM)
   - Current check-then-act pattern is not atomic
   - Concurrent writes could still create duplicates
   - File locking needed for true uniqueness

   **Mitigation**: Add file locking or atomic write mechanism

3. **Backward Compatibility** (MEDIUM)
   - Existing MCP callers may not expect rejection
   - Retry logic needed at caller level
   - API contract changes

   **Mitigation**: Deprecation period, clear error messages

4. **Fail-Closed Behavior Undefined** (MEDIUM)
   - Current LedgerStore silently returns on duplicate
   - Must decide: exception, error code, or special return?
   - Need to implement proper rejection signaling

5. **Authority Model Conflict** (MEDIUM)
   - MCP authority (client) conflicts with storage boundary authority
   - Who decides if duplicate is acceptable?
   - Governance authority (GL7) not consulted for MCP decisions

### Long-Term Impact

- Operational model becomes "set of unique decisions"
- Audit becomes simpler (can assume latest version of each decision_id is authoritative)
- Scalability requires optimization (hash index, caching)
- Authority model must be clarified (MCP client vs. storage boundary)

### Governance Impact

- Strengthens audit assurance (uniqueness guaranteed)
- Validates schema intent
- Requires governance decision on rejection behavior (exception, error code, etc.)
- Creates dependency on storage boundary health

### Migration Difficulty

- **Immediate**: Refactor MCP server and SealGovernanceGate (medium effort)
- **Immediate**: Implement fail-closed behavior in LedgerStore (low effort)
- **Immediate**: Add concurrency control/locking (medium effort)
- **Ongoing**: Performance monitoring if high-frequency decisions added
- **Eventual**: Hash index for large ledgers (if needed)

---

## OPTION C: SEPARATE OPERATIONAL RECORDS AND CONSTITUTIONAL DECISION LEDGER

### Description
Create two separate ledgers:
1. **Decision Ledger** (formal/constitutional decisions)
   - Used by SealGovernance, formal Human Gate decisions
   - Uniqueness enforced (via LedgerStore)
   - Authority required
   - Lower frequency, high importance

2. **Decision Log** (operational decisions)
   - Used by MCP server, rapid updates
   - Duplicates allowed (append-only log)
   - No authority check
   - Higher frequency, lower governance overhead

### Benefits

1. **Clear Separation of Concerns** (HIGH)
   - Formal decisions have strong guarantees
   - Operational decisions are fast/flexible
   - No ambiguity about which path is used

2. **Appropriate Governance Per Decision Type** (HIGH)
   - Formal decisions: GL7 + uniqueness enforcement
   - Operational decisions: MCP client + flexibility
   - Matches actual usage patterns

3. **No Performance Penalty** (MEDIUM)
   - Operational log has no uniqueness check (fast append)
   - Decision Ledger can be optimized for formal use
   - Two separate data structures

4. **Flexibility for Future** (MEDIUM)
   - Formal decisions can add cryptographic signatures later
   - Operational log can be rotated/archived easily
   - Different retention policies per type

5. **Clear Schema Expectations** (MEDIUM)
   - DECISION_LEDGER_SCHEMA_v1.md applies to Formal only
   - Operational log has simpler schema
   - No ambiguity about field requirements

### Risks

1. **Increased Complexity** (MEDIUM)
   - Two data structures to manage
   - Queries must span both
   - Potential for inconsistency

2. **Ambiguous Authority** (MEDIUM)
   - How to decide if a decision goes to Formal or Operational?
   - Risk of wrong categorization
   - Governance confusion

3. **Migration Confusion** (MEDIUM)
   - Existing decision_ledger.jsonl must be split or migrated
   - Tools need to understand both
   - Transition period requires careful handling

4. **Coordination Gap** (MEDIUM)
   - Operational log and Decision Ledger are decoupled
   - Cross-references become complex
   - Related_events/documents harder to track

### Long-Term Impact

- Clear distinction between formal and operational decisions
- Audit model adapts: formal decisions are auditable, operational are logged
- Schema evolution: two paths can diverge
- Tool complexity increases (readers must understand both)

### Governance Impact

- Formal decisions get stronger governance
- Operational decisions stay lightweight
- But: Governance rules for categorization needed
- Authority becomes explicit (formal = GL7, operational = MCP client)

### Migration Difficulty

- **Immediate**: Create new Decision Ledger file structure (low effort)
- **Immediate**: Update MCP server to use Decision Log (low effort)
- **Immediate**: Update SealGovernanceGate to use Decision Ledger (low effort)
- **One-time**: Migrate existing decision_ledger.jsonl (medium effort)
- **Documentation**: Clarify which decisions go where (medium effort)

---

## OPTION D: DEFER UNTIL ARCHITECTURE REDESIGN

### Description
Accept current architecture as interim:
- No changes to MCP server
- No changes to SealGovernanceGate
- No implementation of LedgerStore boundary
- Wait for broader architecture redesign (Phase 5+)

### Benefits

1. **No Immediate Work** (HIGH)
   - Zero implementation effort
   - No breaking changes
   - No migration needed

2. **Wait for Full Architecture Picture** (MEDIUM)
   - Phase 5+ may have better solution
   - Authority model may be clarified
   - Trust requirements may be better defined

3. **No Risk of Wrong Choice** (MEDIUM)
   - Decisions made later with more information
   - Avoid locking into suboptimal boundary now

### Risks

1. **Technical Debt Accumulates** (HIGH)
   - Current ambiguity persists
   - Duplicates continue to be possible
   - Audit reliability suffers

2. **No Governance Progress** (HIGH)
   - DECISION_LEDGER_SCHEMA_v1.md intent not realized
   - Authority model remains unclear
   - Readers cannot rely on decision_id uniqueness

3. **Future Cleanup More Expensive** (MEDIUM)
   - If implemented later, existing ledger may have duplicates
   - Migration becomes more complex
   - Breaking changes harder to justify later

4. **Risk Exposure** (MEDIUM)
   - Duplicate injection attacks possible now
   - Impersonation attacks possible now
   - No protection while waiting

### Long-Term Impact

- Current state persists
- No improvement in audit assurance
- Future architecture must address this anyway
- Potential for decisions to proliferate that depend on broken guarantees

### Governance Impact

- Governance authority remains ambiguous
- No new framework needed
- But: No progress on trust model
- Audit continues with limited assurance

### Migration Difficulty

- **Deferred**: All work pushed to future phase
- **Risk**: Future work may be more complex due to accumulated state

---

## COMPARATIVE ANALYSIS

| Factor | Option A | Option B | Option C | Option D |
|--------|----------|----------|----------|----------|
| **Implementation Effort** | None | Medium | Medium-High | None |
| **Uniqueness Enforced** | ❌ No | ✅ Yes | ✅ Formal only | ❌ No |
| **Authority Verified** | ❌ No | ⚠️ Partial | ✅ Yes (formal) | ❌ No |
| **Performance Impact** | None | Medium (O(n) reads) | Low | None |
| **Schema Alignment** | ❌ No | ✅ Yes | ✅ Yes (formal) | ❌ No |
| **Audit Assurance** | ⚠️ Low | ✅ High | ✅ High (formal) | ⚠️ Low |
| **Governance Clarity** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Risk Reduction** | ❌ No | ✅ High | ✅ High (formal) | ❌ No |
| **Immediate Actionable** | ✅ Yes | ✅ Yes | ⚠️ Requires planning | ✅ Yes |
| **Future-Proof** | ⚠️ Maybe | ✅ Yes | ✅ Yes | ❌ No |

---

## SCENARIO-BASED EVALUATION

### Scenario 1: High-Frequency Decision Updates

Requirement: Support many updates to same decision_id (e.g., hourly policy changes)

| Option | Suitability |
|--------|-----------|
| A | ✅ GOOD (no uniqueness constraint) |
| B | ⚠️ FAIR (performance may suffer with large ledger) |
| C | ✅ GOOD (operational log for updates, formal for constitutional) |
| D | ⚠️ FAIR (problem postponed) |

### Scenario 2: Audit Compliance

Requirement: Prove every decision_id appears exactly once

| Option | Suitability |
|--------|-----------|
| A | ❌ POOR (duplicates possible) |
| B | ✅ EXCELLENT (uniqueness guaranteed) |
| C | ✅ EXCELLENT (formal ledger unique) |
| D | ❌ POOR (problem unresolved) |

### Scenario 3: Concurrent Decision Submissions

Requirement: Handle simultaneous submissions safely

| Option | Suitability |
|--------|-----------|
| A | ⚠️ FAIR (both writes succeed, duplicates silently created) |
| B | ⚠️ FAIR (race condition possible without locking) |
| C | ✅ GOOD (operational log accepts duplicates, formal requires coordination) |
| D | ⚠️ FAIR (problem deferred) |

### Scenario 4: Future Authority Verification

Requirement: Add cryptographic signatures to decisions later

| Option | Suitability |
|--------|-----------|
| A | ⚠️ FAIR (no boundary to extend) |
| B | ✅ EXCELLENT (single boundary can be extended) |
| C | ✅ EXCELLENT (formal ledger can be extended with signatures) |
| D | ⚠️ FAIR (redesign may not preserve current structure) |

---

## DECISION INPUTS FOR HUMAN GATE

### Questions to Clarify Before Deciding

1. **Uniqueness Requirement**: Should decision_id be globally unique or per-type unique?
2. **Authority Model**: Who has permission to create decisions? (currently undefined)
3. **Fail-Closed Behavior**: When duplicate is detected, should it be exception, error code, or silent?
4. **Performance Tolerance**: What's the acceptable latency for decision write operations?
5. **Audit Requirement**: What level of audit assurance is required? (currently weak)
6. **Decision Frequency**: How many decisions per day? (affects Option B performance)
7. **Separation Criteria**: What makes a decision "formal" vs. "operational"? (for Option C)
8. **Migration Window**: How long can current ambiguity persist? (for Option D)

### Critical Path Dependencies

- **Authority Model** → affects Options B, C (who enforces boundary?)
- **Audit Requirements** → affects Options B, C (what guarantees are needed?)
- **Performance Budget** → affects Options B, C (O(n) reads acceptable?)
- **Decision Frequency** → affects Options A, C (how fast does logging need to be?)

---

## RECOMMENDATION (For Human Gate Consideration Only)

**Status**: NO RECOMMENDATION MADE (Human Gate authority only)

This document presents evidence and options. Human judgment required on:
1. Which option best serves MoCKA's governance needs
2. What level of trust Decision Ledger must provide
3. Whether to prioritize performance, audit assurance, or simplicity
4. Timeline for implementation vs. deferral

---

## NEXT STEPS IF HUMAN GATE DECISION IS MADE

1. **If Option A Selected**: Update DECISION_LEDGER_SCHEMA_v1.md to clarify uniqueness is not enforced
2. **If Option B Selected**: Refactor MCP server and SealGovernanceGate to use LedgerStore, implement fail-closed behavior
3. **If Option C Selected**: Create separate Decision Ledger and Decision Log files, migrate existing data
4. **If Option D Selected**: Schedule follow-up review for Phase 5 architecture redesign

---

**Document Status**: AWAITING HUMAN GATE DECISION  
**Authority**: きむら博士 (Human Gate)  
**No recommendation provided**  
**Evidence only**

