# LEDGERADAPTER AUTHORITY MODEL DECISION v1.0

**Report Date**: 2026-08-13
**Phase**: Human Gate Ledger Authority Boundary Consolidation — Phase 2
**Purpose**: Reclassify LedgerAdapter role and evaluate two architectural models

---

## CURRENT STATUS

**Classification**: CATEGORY B - Optional Helper Abstraction
**Production Usage**: None (test-only)
**Integration**: Jarvis HumanGate (test), no production integration
**Files**: 
- `runtime/jarvis/record/adapter/ledger_adapter.py` (15 lines)
- `runtime/jarvis/gate/human_gate.py` (uses LedgerAdapter)

---

## MODEL A: LEDGERADAPTER AS UTILITY LAYER

### Definition

LedgerAdapter functions as a **convenience wrapper** providing schema translation and storage abstraction without enforcing authority boundaries.

### Characteristics

```
┌──────────────────────┐
│  Caller (Any code)   │
└──────────┬───────────┘
           │
           v
┌──────────────────────┐
│  LedgerAdapter       │
├──────────────────────┤
│ Responsibilities:    │
│ - Data transformation│
│ - Schema wrapping    │
│ - Storage dispatch   │
└──────────┬───────────┘
           │
           v
┌──────────────────────┐
│  LedgerStore         │
│  + Uniqueness check  │
└──────────┬───────────┘
           │
           v
┌──────────────────────┐
│  File I/O            │
└──────────────────────┘
```

### Responsibilities (Model A)

1. **Data Transformation**
   - Convert (decision_id, status) → DecisionRecord
   - Apply schema defaults
   - Generate timestamp
   - **No validation of inputs**

2. **Storage Abstraction**
   - Simplify caller interface
   - Hide DecisionRecord complexity
   - Delegate to LedgerStore
   - **No authority enforcement**

3. **Convenience Features**
   - Handle common cases
   - Reduce boilerplate
   - Aid testing
   - **No fail-closed behavior**

### What Model A Does NOT Do

- ❌ Verify Human Gate approval exists
- ❌ Check approver identity
- ❌ Validate decision_id format
- ❌ Enforce uniqueness (delegates to LedgerStore)
- ❌ Provide authority proof
- ❌ Prevent unauthorized writes
- ❌ Maintain audit trail of access
- ❌ Ensure immutability beyond file level

### Authority Implications

**Assumption**: If you can call LedgerAdapter, you are authorized
**Reality**: No verification of this assumption
**Gap**: Zero access control

### Failure Behavior

```
adapter.record("DC_001", "APPROVED")
  - Success: record written, returned to caller
  - Failure (duplicate): record silently skipped, same record returned
  - Caller cannot distinguish success from failure
```

**Verdict**: Fail-silent, not fail-closed

### Use Cases (Model A Works For)

- Testing (test harness controls all inputs)
- Non-sensitive development
- Prototyping
- Local validation
- Internal-only tools

### Use Cases (Model A Fails For)

- Production decision recording
- Authority-dependent decisions
- Audit compliance
- Formal governance
- Systems requiring proof of approval

---

## MODEL B: LEDGERADAPTER AS AUTHORITY ENFORCEMENT BOUNDARY

### Definition

LedgerAdapter functions as a **mandatory control point** enforcing Human Gate authority requirements before any decision can persist to the formal Decision Ledger.

### Architecture

```
┌──────────────────────┐
│  Human Gate          │
│  Approval Event      │
└──────────┬───────────┘
           │
           v
┌──────────────────────┐
│  LedgerAdapter       │
├──────────────────────┤
│ 1. Approval Check    │
│    ├─ Query: Human   │
│    │   Gate approved?│
│    ├─ Result: proof  │
│    └─ Fail-closed    │
│                      │
│ 2. Identity Verify   │
│    ├─ Query: Who?    │
│    ├─ Validate: Known│
│    └─ Store: Name    │
│                      │
│ 3. Decision Verify   │
│    ├─ Check: ID fmt  │
│    ├─ Check: No dups │
│    └─ Check: Immutable│
│                      │
│ 4. Append Enforce    │
│    ├─ Write record   │
│    ├─ Guarantee: +1  │
│    └─ Proof: offset  │
└──────────┬───────────┘
           │
           v
┌──────────────────────┐
│  Decision Ledger     │
│  (canonical)         │
└──────────────────────┘
```

### Responsibilities (Model B)

#### 1. Human Approval Verification

**Pre-condition**: Decision must have prior Human Gate approval

```python
def record(self, decision_id, request_id, status):
    # REQUIRED: Lookup approval in mocka_events.db
    approval = HumanGateEventStore.find_approval(request_id)
    
    if not approval:
        raise AuthorizationError(
            f"No Human Gate approval for {request_id}"
        )
    
    if approval['next_state'] != 'APPROVED':
        raise AuthorizationError(
            f"Request not approved: {approval['next_state']}"
        )
    
    # Continue only if verified
```

**Guarantees**:
- ✅ Decision must be pre-approved
- ✅ Fail-closed: no exception = approved
- ✅ Audit trail: which approval triggered this record

#### 2. Approver Identity Verification

**Pre-condition**: Approver must be verifiable human

```python
    # Extract approver from approval record
    approver = approval['approver']
    
    # REQUIRED: Verify approver is known entity
    if not IdentityService.is_valid_human(approver):
        raise AuthenticationError(
            f"Approver not recognized: {approver}"
        )
    
    # REQUIRED: Store individual identity (not generic)
    record = DecisionRecord(
        decision_id=decision_id,
        request_id=request_id,
        status=status,
        actor=approver,  # Individual, not "HUMAN_GATE"
        approval_timestamp=approval['timestamp']
    )
```

**Guarantees**:
- ✅ Approver is individual human
- ✅ Identity is preserved in record
- ✅ Traceable back to specific person

#### 3. Decision Identity Verification

**Pre-condition**: Decision must not already exist in ledger

```python
    # REQUIRED: Check for duplicate decision_id
    existing = LedgerStore.get(decision_id)
    
    if existing:
        raise IntegrityError(
            f"Decision already recorded: {decision_id}\n"
            f"First recording: {existing['timestamp']}\n"
            f"Previous status: {existing['status']}"
        )
    
    # REQUIRED: Validate decision_id format
    if not self._is_valid_decision_id(decision_id):
        raise FormatError(
            f"Invalid decision_id format: {decision_id}"
        )
    
    # REQUIRED: Verify no orphaned dependencies
    if not self._has_valid_context(decision_id, request_id):
        raise ContextError(
            f"Decision context invalid"
        )
```

**Guarantees**:
- ✅ No duplicate decision_ids in formal ledger
- ✅ Format consistency enforced
- ✅ Context integrity verified

#### 4. Append-Only Enforcement

**Post-condition**: Written record is permanent and traceable

```python
    # REQUIRED: Write with immutable append
    result = LedgerStore.save_immutable(
        record=record,
        write_mode='append_only',
        integrity_check=True
    )
    
    if not result['success']:
        raise PersistenceError(
            f"Failed to persist decision: {result['error']}"
        )
    
    # REQUIRED: Return proof of recording
    return DecisionRecordReceipt(
        decision_id=decision_id,
        ledger_offset=result['file_offset'],
        timestamp=result['write_timestamp'],
        hash_proof=result['content_hash']
    )
```

**Guarantees**:
- ✅ Record is appended, never modified
- ✅ File offset proves position
- ✅ Hash proves content
- ✅ Cannot be corrupted

### Required Implementation Changes

For Model B to work:

1. **Modify LedgerAdapter constructor**
   ```python
   class LedgerAdapter:
       def __init__(self):
           self.store = LedgerStore()
           self.human_gate_db = HumanGateEventStore()
           self.identity_service = IdentityService()
   ```

2. **Add approval lookup**
   - Query mocka_events.db for Human Gate decision
   - Validate APPROVED state
   - Extract approver identity

3. **Add identity verification**
   - Connect to identity/user store
   - Verify approver is valid entity
   - Handle unknown users (fail-closed)

4. **Add duplicate detection**
   - Check Decision Ledger for existing decision_id
   - Fail if found

5. **Add receipt generation**
   - Return proof of recording
   - Include file offset, timestamp, hash
   - Enable audit verification

### Failure Behavior

```
Scenario: Unauthorized write attempt

adapter.record("DC_001", "REQ_123", "APPROVED")
  - Step 1: Check Human Gate for REQ_123
  - Result: NOT FOUND
  - Action: Raise AuthorizationError
  - Ledger: NOT MODIFIED
  - Caller: Receives exception
  - Audit: Exception logged with attempt details

Scenario: Duplicate detection

adapter.record("DC_001", "REQ_123", "APPROVED")
  - Step 3: Check Decision Ledger
  - Result: DC_001 already exists
  - Action: Raise IntegrityError
  - Ledger: NOT MODIFIED
  - Caller: Receives exception
  - Audit: Duplicate attempt logged
```

**Verdict**: Fail-closed, not fail-silent

---

## COMPARATIVE ANALYSIS

### Functionality Comparison

| Feature | Model A (Utility) | Model B (Boundary) |
|---------|---|---|
| **Data transformation** | ✅ Basic | ✅ Advanced |
| **Authority verification** | ❌ NO | ✅ YES |
| **Identity preservation** | ❌ NO | ✅ YES |
| **Duplicate prevention** | ⚠️ Delegated | ✅ Enforced |
| **Fail-closed** | ❌ NO | ✅ YES |
| **Audit trail** | ❌ NO | ✅ YES |
| **Production-ready** | ❌ NO | ✅ YES (if implemented) |

### Risk Assessment

| Risk | Model A | Model B |
|------|---------|---------|
| Unauthorized write | ❌ Possible | ✅ Blocked |
| Duplicate decision | ❌ Possible | ✅ Blocked |
| Approver identity loss | ❌ Silent | ✅ Prevented |
| Silent failure | ❌ Risk | ✅ Exceptions |
| Audit integrity | ❌ Weak | ✅ Strong |
| Test coverage | ⚠️ False positives | ✅ True coverage |

### Implementation Cost

| Phase | Model A | Model B |
|-------|---------|---------|
| **Design** | 0 hours | 4 hours |
| **Implementation** | 0 hours | 16 hours |
| **Testing** | 2 hours | 12 hours |
| **Integration** | 0 hours | 8 hours |
| **Total** | 2 hours | 40 hours |

---

## DECISION FRAMEWORK

### When to Choose Model A

**Conditions**:
- LedgerAdapter used for testing only
- No production decision recording
- No formal authority requirements
- Short-lived prototypes

**Acceptable if**: Test harness is under full control

### When to Choose Model B

**Conditions**:
- Production decision recording required
- Human Gate approval is institutional requirement
- Audit compliance needed
- Formal governance in place

**Required if**: Decisions affect institutional authority

---

## ARCHITECTURAL IMPLICATIONS

### If Model A is Chosen

- LedgerAdapter remains test utility
- Production continues direct writes (MCP, SealGov)
- No unified authority boundary
- Duplicate prevention NOT enforced
- Test code provides false confidence
- **Gap**: Design/deployment mismatch continues

### If Model B is Chosen

- LedgerAdapter becomes production control point
- All Human Gate decisions go through LedgerAdapter
- Unified authority boundary established
- Duplicate prevention enforced
- Test code provides real assurance
- **Integration**: PHI-OS must connect to LedgerAdapter

---

## HYBRID APPROACH: Model A + B (Staged)

### Phase 1: Implement Model B (design consolidation)
- Redesign LedgerAdapter with authority checks
- Document required integrations
- Prepare for production deployment

### Phase 2: Test Integration
- Jarvis tests use full Model B checks
- Validate all verification logic
- Build confidence in boundary

### Phase 3: Production Integration
- Connect PHI-OS Human Gate to LedgerAdapter
- Migrate decision recording through boundary
- Sunset direct write paths

### Phase 4: Full Enforcement
- Direct writes blocked or deprecated
- LedgerAdapter is canonical path
- Authority boundary operational

---

## INSTITUTIONAL REQUIREMENTS

### Prerequisite for Model B

1. **Human Gate System Available**
   - mocka_events.db must be accessible
   - Approval queries must be fast
   - State must be reliable

2. **Identity Service Required**
   - User/approver validation needed
   - Must distinguish human from system actors
   - Should support role-based lookup

3. **Decision Coordination Needed**
   - decision_id must map to request_id
   - OR request_id must be embedded in decision
   - OR separate mapping table required

4. **Audit System Ready**
   - Receipt storage for proof
   - Exception logging for attempts
   - Queryable access logs

---

## RECOMMENDATION SUMMARY

| Aspect | Model A | Model B |
|--------|---------|---------|
| **Meets design intent** | ❌ NO | ✅ YES |
| **Viable for production** | ❌ NO | ✅ YES (if implemented) |
| **Implementation effort** | ✅ Minimal | ⚠️ Moderate |
| **Institutional value** | ❌ Low | ✅ High |
| **Risk mitigation** | ❌ None | ✅ Complete |

---

**PHASE 2 ANALYSIS COMPLETE**

Two models defined and compared. No recommendation made (Human Gate authority).

Ready for Phase 3: Canonical Authority Store Definition.

