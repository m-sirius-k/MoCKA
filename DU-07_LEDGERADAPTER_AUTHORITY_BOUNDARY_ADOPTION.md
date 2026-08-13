# DU-07: LEDGERADAPTER AUTHORITY BOUNDARY ADOPTION DECISION

**Decision Unit ID**: DU-07
**Title**: LedgerAdapter Authority Boundary Adoption Decision
**Date**: 2026-08-13
**Authority**: Human Gate Review (きむら博士)
**Status**: AWAITING HUMAN GATE JUDGMENT

---

## DECISION QUESTION

**Primary**: Should LedgerAdapter be formally adopted as the mandatory authority enforcement boundary for all Human Gate decisions before they become formal Decision Ledger records?

**Sub-questions**:
1. Should LedgerAdapter remain a test-only utility or move to production?
2. Should LedgerAdapter verify Human Gate approval before recording decisions?
3. Should LedgerAdapter preserve individual approver identity in recorded decisions?
4. Should MCP direct writes be bypassed through LedgerAdapter?

---

## CURRENT STATE

**LedgerAdapter Classification**: CATEGORY B - Optional Helper Abstraction

**Current Usage**: 
- Jarvis HumanGate (test framework only)
- Not used in production
- Not used by MCP server
- Not used by SealGov

**Current Role**:
- Data transformation (schema wrapping)
- Storage dispatch to LedgerStore
- Minimal validation (none)
- No authority enforcement
- No production integration

**Current File**: `runtime/jarvis/record/adapter/ledger_adapter.py` (15 lines)

**Production Paths** (bypass LedgerAdapter):
- MCP: mocka_decision_write → direct write
- SealGov: execute() → direct write
- Both write directly to decision_ledger.jsonl
- Both bypass any LedgerAdapter boundary

---

## OPTION A: MAINTAIN CURRENT STATUS (LedgerAdapter as Test Utility)

### Description

LedgerAdapter remains a test-only helper for Jarvis framework. No production integration planned. MCP and SealGov continue direct writes.

### Implementation

```
Production Path:
  MCP → decision_ledger.jsonl [direct]
  SealGov → decision_ledger.jsonl [direct]
  
Test Path:
  Jarvis → LedgerAdapter → LedgerStore → jarvis_ledger.jsonl

Isolation Complete: Two separate decision ledgers, no integration
```

### Consequences

**Benefits**:
- ✅ No refactoring needed
- ✅ No integration complexity
- ✅ Production continues as-is
- ✅ Test code independent

**Costs**:
- ❌ Production bypasses authority checks
- ❌ Authority boundary NOT established
- ❌ Test code provides false confidence
- ❌ Design/deployment gap continues
- ❌ MCP authority unverified
- ❌ Duplicate prevention NOT enforced

**Institutional Impact**:
- Authority model: fragmented, unverified
- Audit trail: incomplete, split across systems
- Governance: weakened, no formal boundary
- Future: AI agents cannot rely on authority

### Governance Implication

Decision authority remains unverified. MCP clients can create decisions with false authority. Institutional governance is undermined.

---

## OPTION B: ADOPT LEDGERADAPTER AS PRODUCTION BOUNDARY (Model B)

### Description

LedgerAdapter is redesigned and deployed as mandatory production boundary. All Human Gate decisions must pass through LedgerAdapter before becoming formal Decision Ledger records. MCP and SealGov paths redirect through LedgerAdapter.

### Redesigned Architecture

```
Production Implementation:

Human Gate Approval
    |
    v
mocka_events.db [Authority Source]
    |
    v
LedgerAdapter [Authority Boundary]
    ├─ Verify: Approval exists in mocka_events.db
    ├─ Verify: Approver identity is valid
    ├─ Verify: No duplicate decision_id
    ├─ Transform: Preserve individual approver
    └─ Write: decision_ledger.jsonl [canonical]

MCP Server (redirected):
  mocka_decision_write()
    └─ LedgerAdapter.record() [mandatory]
    
SealGov (redirected):
  SealGovernanceGate.execute()
    └─ LedgerAdapter.record() [mandatory]
```

### Required Changes

**LedgerAdapter Responsibilities** (Model B):

```python
class LedgerAdapter:
    def record(self, decision_id, request_id, status, approval_source):
        # 1. Verify Human Gate Approval
        approval = self._verify_human_approval(request_id)
        if not approval:
            raise AuthorizationError(f"No HG approval: {request_id}")
        
        # 2. Verify Approver Identity
        approver = approval['approver']
        if not self._is_valid_approver(approver):
            raise AuthenticationError(f"Invalid approver: {approver}")
        
        # 3. Check for Duplicates
        if self._decision_exists(decision_id):
            raise IntegrityError(f"Duplicate decision_id: {decision_id}")
        
        # 4. Create and Record
        record = DecisionRecord(
            decision_id=decision_id,
            request_id=request_id,
            status=status,
            actor=approver,  # Individual, not generic
            human_gate_event_id=approval['event_id'],
            timestamp=datetime.now().isoformat()
        )
        
        # 5. Write to Decision Ledger
        self.store.save_immutable(record)
        
        # 6. Return Receipt
        return DecisionRecordReceipt(
            decision_id=decision_id,
            approver=approver,
            timestamp=record['timestamp'],
            ledger_proof=record.get('hash_proof')
        )
```

### Consequences

**Benefits**:
- ✅ Authority boundary established
- ✅ All decisions verified before recording
- ✅ Individual approver identity preserved
- ✅ Duplicate prevention enforced
- ✅ Unified decision authority
- ✅ Audit trail is complete
- ✅ Safe for AI agent validation
- ✅ Test code provides true assurance

**Costs**:
- ⚠️ Refactoring effort (16-24 hours)
- ⚠️ Integration complexity
- ⚠️ Must connect PHI-OS to LedgerAdapter
- ⚠️ Requires identity service integration
- ⚠️ Performance impact (lookup + verify + write)
- ⚠️ New dependencies (mocka_events.db availability)

**Institutional Impact**:
- Authority model: unified, verified
- Audit trail: complete, traceable
- Governance: strong, formal boundary
- Future: AI agents can safely validate authority

### Implementation Phases

**Phase 1: Design** (2 weeks)
- LedgerAdapter Model B design
- Authority integration planning
- Identity service mapping

**Phase 2: Test** (2 weeks)
- Jarvis tests redesigned for Model B
- All verification logic tested
- Mock Human Gate for testing

**Phase 3: Integration** (2 weeks)
- PHI-OS connected to LedgerAdapter
- MCP redirected through boundary
- SealGov redirected through boundary

**Phase 4: Deployment** (1 week)
- Gradual rollout to production
- Monitor for failures
- Fallback procedures ready

**Total Effort**: 4-6 weeks

### Governance Implication

Decision authority is unified and verified. All decisions pass through institutional boundary. Formal governance is operational.

---

## OPTION C: LEDGERADAPTER AS OPTIONAL HELPER WITH GOVERNANCE BYPASS

### Description

LedgerAdapter can be used by systems that want verification, but is not mandatory. MCP and SealGov can choose to use LedgerAdapter or write directly. Governance rules specify which path to use per decision type.

### Conditional Architecture

```
High-Authority Decisions:
  → LedgerAdapter [Model B verification]
  → decision_ledger.jsonl

Operational Decisions:
  → Direct write [Model A convenience]
  → decision_ledger.jsonl

MCP chooses path:
  mocka_decision_write(..., use_ledger_adapter=True)
  OR
  mocka_decision_write(..., use_ledger_adapter=False)
```

### Consequences

**Benefits**:
- ✅ Flexibility for different decision types
- ✅ Fast path available for urgent decisions
- ✅ Gradual migration possible
- ✅ Systems can choose verification level

**Costs**:
- ❌ Authority model is ambiguous
- ❌ Governance rules must distinguish cases
- ❌ Audit trail is inconsistent
- ❌ Some decisions have authority, some don't
- ❌ Cannot trust Decision Ledger authority
- ❌ Duplicate prevention is partial

**Institutional Impact**:
- Authority model: mixed/ambiguous
- Audit trail: incomplete/inconsistent
- Governance: requires complex rules
- Future: AI agents cannot rely on authority

### Governance Burden

Requires clear rules for when LedgerAdapter is mandatory. Risk of miscategorization.

---

## DECISION CRITERIA

### Evaluation Dimensions

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| **Authority Assurance** | HIGH | ❌ NO | ✅ YES | ⚠️ PARTIAL |
| **Audit Completeness** | HIGH | ❌ NO | ✅ YES | ⚠️ PARTIAL |
| **Governance Clarity** | HIGH | ❌ NO | ✅ YES | ⚠️ REQUIRES RULES |
| **Implementation Effort** | MEDIUM | ✅ MINIMAL | ⚠️ MODERATE | ⚠️ MODERATE |
| **Future AI Safety** | MEDIUM | ❌ NO | ✅ YES | ⚠️ CONDITIONAL |
| **Institutional Risk** | MEDIUM | ❌ HIGH | ✅ LOW | ⚠️ MEDIUM |

### Recommended Factors for Decision

1. **Authority Requirement**: How critical is verifying decision authority?
   - If CRITICAL → Choose Option B
   - If IMPORTANT → Choose Option B or C
   - If OPTIONAL → Choose Option A

2. **Audit Requirement**: How important is audit completeness?
   - If REQUIRED → Choose Option B
   - If IMPORTANT → Choose Option B
   - If OPTIONAL → Choose Option A or C

3. **Governance Capability**: How capable is the governance system?
   - If STRONG → Can enforce complex rules (Option C possible)
   - If MODERATE → Needs clear boundaries (Option B preferred)
   - If WEAK → Cannot enforce conditionality (Option A only)

4. **AI Integration**: Will AI agents make decisions?
   - If YES → Need verified authority (Option B required)
   - If MAYBE → Prefer verifiable path (Option B)
   - If NO → Authority less critical (Option A possible)

---

## DECISION INPUTS FOR HUMAN GATE

### Questions to Clarify

1. **Authority Model**: Is Human Gate approval the institutional requirement for formal decisions?

2. **MCP Authority**: Should MCP decisions have same verification as Human Gate decisions?

3. **Verification Level**: Is decision authority important enough to verify before recording?

4. **AI Integration**: Will future AI agents need to trust decision authority?

5. **Audit Standard**: What audit assurance is required for Decision Ledger?

6. **Governance Scope**: Does institutional governance require unified authority?

---

## RECOMMENDATION SUMMARY

| Aspect | Option A | Option B | Option C |
|--------|----------|----------|----------|
| **Meets institutional intent** | ❌ NO | ✅ YES | ⚠️ PARTIAL |
| **Meets design spec** | ❌ NO | ✅ YES | ⚠️ PARTIAL |
| **Implementation effort** | ✅ MINIMAL | ⚠️ MODERATE | ⚠️ MODERATE |
| **Institutional value** | ❌ LOW | ✅ HIGH | ⚠️ MEDIUM |
| **Risk mitigation** | ❌ NONE | ✅ COMPLETE | ⚠️ PARTIAL |
| **Audit assurance** | ❌ WEAK | ✅ STRONG | ⚠️ CONDITIONAL |

---

**DECISION UNIT DU-07 COMPLETE**

No recommendation made. Authority: Human Gate (きむら博士)

