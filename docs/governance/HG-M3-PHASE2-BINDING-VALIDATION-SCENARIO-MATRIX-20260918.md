# HG-M3 Phase 2: Binding Validation Scenario Matrix
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** DESIGN VERIFICATION

---

## Binding Validation Test Scenarios

Eight core scenarios covering normal operation and failure modes.

---

## CASE 01: Complete Normal Operation

### Scenario Name
**Full Binding Validation Success**

### Condition
- Authority Object exists and is valid at decision_timestamp
- Decision Object exists with valid decision_id
- All referenced Evidence Objects exist in Evidence Store
- Evidence integrity verified (hash matches)
- Timestamps in correct order: evidence_ts ≤ decision_ts ≤ validation_ts ≤ audit_ts
- Validation Record exists with validation_result = PASS

### Input State
```
Decision ID:        DEC_20260918_001
Authority ID:       AUTH_HG_001 (valid_from: 2026-01-01, valid_to: 2027-01-01)
Evidence IDs:       [EV_001, EV_002, EV_003]
Evidence Status:    All present, integrity OK
Validation:         PASS (all 6 checks passed)
Timestamps:         Correct ordering confirmed
```

### Expected Binding Result
**Status:** `VALID`  
**Reasoning:**
- Check 1 (Decision Exists): PASS ✓
- Check 2 (Authority Valid): PASS ✓
- Check 3 (Evidence Exists): PASS ✓
- Check 4 (Evidence Integrity): PASS ✓
- Check 5 (Timestamp Order): PASS ✓
- Check 6 (Validation Passed): PASS ✓

**Decision Ledger Entry:** Binding recorded as VALID
**Audit Memory:** Re-verification enabled
**Timeline to 5-year audit:** Decision is ready for archive

### Governance Action
- Proceed with decision execution
- Decision can be used as institutional authority
- Binding serves as immutable proof
- No escalation required

---

## CASE 02: Evidence Missing

### Scenario Name
**Evidence Referenced But Not Found**

### Condition
- Decision Object references 3 evidence items: [EV_001, EV_002, EV_003]
- Evidence Store lookup fails: EV_002 not found
- EV_001 and EV_003 exist and are intact
- All other checks would pass

### Input State
```
Decision ID:        DEC_20260918_002
Evidence IDs:       [EV_001, EV_002 (MISSING), EV_003]
Evidence Status:    EV_001 ✓, EV_002 ✗ (not found), EV_003 ✓
Evidence Integrity: EV_001 hash OK, EV_003 hash OK
Authority:          Valid
Validation:         N/A (cannot proceed)
```

### Expected Binding Result
**Status:** `UNKNOWN` or `NOT_VERIFIED` (indeterminate, not proven false)  
**Reason for Status:**
- Check 3 (Evidence Exists) fails
- Missing evidence could be:
  - In cold storage (retrieve needed)
  - Accidentally deleted (recovery possible)
  - Not yet ingested (wait needed)
  - Irretrievably lost (failure)
- **Key distinction:** Missing ≠ Invalid. System cannot prove binding is wrong, only incomplete.

**Decision Ledger Entry:** Binding state = NOT_VERIFIED
**Audit Memory:** Failure record created with "Evidence_Missing" reason
**Timeline:** Binding validation paused, retry possible

### Governance Action
**Immediate:**
- Binding BLOCKED (cannot proceed)
- Escalate to Human Gate for investigation

**Investigation Steps:**
1. Search archive/cold storage for EV_002
2. Check deletion logs (was it recently deleted?)
3. Check ingestion queue (is it pending?)
4. Notify decision maker of missing evidence

**Resolution:**
- If recovered: Retry binding validation
- If lost: Escalate for decision amendment
- If not yet ingested: Wait and retry

**Human Review:** YES - required to determine recovery path

---

## CASE 03: Authority Missing

### Scenario Name
**Authority Referenced But Not in Registry**

### Condition
- Decision Object specifies authority_id = "AUTH_UNKNOWN_999"
- Authority Registry lookup fails
- This authority was never registered
- All other objects exist and are valid

### Input State
```
Decision ID:        DEC_20260918_003
Authority ID:       AUTH_UNKNOWN_999 (NOT IN REGISTRY)
Decision Timestamp: 2026-09-18T10:00:00Z
Evidence:           All present, integrity OK
Authority Status:   MISSING (no historical record)
```

### Expected Binding Result
**Status:** `INVALID`  
**Reasoning:**
- Check 2 (Authority Valid) fails immediately
- No authority to validate against
- Decision maker's identity cannot be verified
- Binding fundamentally breaks

**Decision Ledger Entry:** Binding state = INVALID
**Audit Memory:** Failure record "Authority_Missing"
**Timeline:** Binding validation stops, cannot proceed

### Governance Action
**Immediate:**
- Binding BLOCKED
- Escalate to Human Gate

**Investigation:**
1. Verify authority_id (typo? wrong registry?)
2. Check if authority should have been registered
3. Examine who authorized this decision
4. Determine if decision is fraudulent or administrative error

**Resolution Paths:**
- Correct authority_id and retry (if typo)
- Register missing authority retroactively (if administrative gap)
- Invalidate decision (if unauthorized)

**Human Review:** YES - required to determine authority legitimacy

---

## CASE 04: Evidence Integrity Failure

### Scenario Name
**Evidence Hash Mismatch (Tampering Detected)**

### Condition
- Evidence Object EV_001 stored with content_hash = "abc123..."
- Current hash of EV_001 payload = "def456..." (mismatch!)
- Evidence was modified after decision
- Archive still has original copy with correct hash

### Input State
```
Decision ID:        DEC_20260918_004
Evidence ID:        EV_001
Stored Hash:        SHA256_abc123def...
Current Hash:       SHA256_def456ghi... (MISMATCH)
Storage Location:   /archive/2026/09/EV_001
Archive Hash:       SHA256_abc123def... (matches stored)
Signature Valid:    NO (mismatch suggests tampering)
```

### Expected Binding Result
**Status:** `INVALID`  
**Reasoning:**
- Check 4 (Evidence Integrity) fails
- Hash mismatch indicates content modification
- Cryptographic proof of tampering
- Evidence cannot be trusted

**Decision Ledger Entry:** Binding state = INVALID
**Audit Memory:** Failure record "Evidence_Integrity_Failure" + hash diff
**Timeline:** Binding validation stops

### Governance Action
**Immediate:**
- Binding BLOCKED
- Escalate to Human Gate (potential security incident)

**Investigation:**
1. Retrieve original from archive
2. Compare versions (what changed?)
3. Determine who had access
4. Investigate if accidental or intentional
5. Review decision validity given evidence compromise

**Resolution:**
- Restore original evidence
- Retry binding with correct evidence
- OR invalidate decision if evidence is critical

**Human Review:** YES - CRITICAL (potential tampering/fraud)

---

## CASE 05: Timestamp Conflict

### Scenario Name
**Temporal Ordering Violation**

### Condition
- Decision made: 2026-09-18T10:00:00Z
- Evidence timestamp: 2026-09-18T15:00:00Z (AFTER decision)
- Evidence created 5 hours AFTER decision was made
- Suggests retroactive evidence creation

### Input State
```
Decision ID:        DEC_20260918_005
Evidence ID:        EV_005
Evidence Timestamp: 2026-09-18T15:00:00Z
Decision Timestamp: 2026-09-18T10:00:00Z
Timestamp Delta:    +5 hours (evidence AFTER decision)
Clock Skew Check:   >1 minute difference, not a clock issue
```

### Expected Binding Result
**Status:** `INVALID` or `NOT_VERIFIED` (depends on root cause)  
**Reasoning:**
- Check 5 (Timestamp Ordering) fails
- Evidence cannot be created AFTER decision that referenced it
- Temporal causality violated

**Decision Ledger Entry:** Binding state = INVALID
**Audit Memory:** Failure record "Timestamp_Conflict"
**Timeline:** Binding validation stops

### Governance Action
**Immediate:**
- Binding BLOCKED
- Escalate to Human Gate

**Investigation:**
1. Verify timestamps (check for clock skew, NTP errors)
2. Determine if retroactive evidence creation is plausible
   - Legitimate: Evidence collected after decision but timestamped with decision time
   - Suspicious: Evidence backdated to look like it pre-existed
3. Review evidence source
4. Assess risk to decision validity

**Resolution:**
- Correct timestamp if clock skew
- Accept with documentation if plausible delay
- Escalate if potential fraud

**Human Review:** YES - temporal anomalies require judgment

---

## CASE 06: Authority Revoked After Decision

### Scenario Name
**Historical Authority State Validation**

### Condition
- Decision made: 2026-09-18T10:00:00Z
- Authority AUTH_HG_001 was valid at that time
- Authority later revoked: 2026-09-18T16:00:00Z
- Re-validating binding 2 hours after revocation
- Must verify authority WAS valid at decision time (not NOW)

### Input State
```
Decision ID:        DEC_20260918_006
Authority ID:       AUTH_HG_001
Decision Timestamp: 2026-09-18T10:00:00Z
Authority Status NOW:
  valid_from:       2026-01-01
  valid_to:         2026-09-18T16:00:00Z (EXPIRED/REVOKED)
Authority Status AT DECISION TIME:
  valid_from:       2026-01-01
  valid_to:         2027-01-01
  (different snapshot)
```

### Expected Binding Result
**Status:** `VALID`  
**Reasoning:**
- Check 2 (Authority Valid AT decision_timestamp) uses historical snapshot
- Authority was valid at 2026-09-18T10:00:00Z ✓
- Current revocation does NOT invalidate past decision
- Historical state matters, not current state

**Decision Ledger Entry:** Binding state = VALID (with historical note)
**Audit Memory:** Authority snapshot preserved
**Timeline:** Binding remains valid despite later revocation

### Governance Action
- Binding PASSES (authority was valid when decision made)
- Decision remains authorized
- Revocation only affects future decisions
- Historical integrity preserved

**Key Principle:** Binding validates authority at decision time, not at validation time

---

## CASE 07: Partial Evidence Set

### Scenario Name
**Some Evidence Exists, Some Missing**

### Condition
- Decision references 5 evidence items
- 4 evidence items found and intact
- 1 evidence item in cold storage (not immediately accessible)
- Cannot complete validation without all 5

### Input State
```
Decision ID:        DEC_20260918_007
Evidence IDs:       [EV_001, EV_002, EV_003, EV_004, EV_005]
Evidence Status:    EV_001 ✓, EV_002 ✓, EV_003 ✓, EV_004 ✓, EV_005 (in archive, 48h restore time)
Evidence Integrity: 4 out of 4 present = OK
Evidence Complete:  NO (1 missing from hot storage)
```

### Expected Binding Result
**Status:** `UNKNOWN`  
**Reasoning:**
- Check 3 (Evidence Exists) partially fails
- Some evidence available, some not
- Cannot complete binding without all evidence
- Not proven false (could be retrieved)

**Decision Ledger Entry:** Binding state = NOT_VERIFIED
**Audit Memory:** Partial validation recorded
**Timeline:** Binding paused pending evidence restoration

### Governance Action
**Immediate:**
- Binding BLOCKED (cannot proceed with partial evidence)
- Initiate archive restoration for EV_005

**Wait Process:**
- Restore from archive (estimated 24-48 hours)
- Once available, retry binding validation
- Should then transition to VALID (if no other issues)

**Decision:** Can decision execution proceed while waiting?
- **Answer depends on governance policy (Human Gate decides)**
- Option A: Strict (block decision until binding complete)
- Option B: Pragmatic (allow decision with "binding pending" status)

**Human Review:** YES (for policy decision on decision execution timing)

---

## CASE 08: Duplicate Decision Identity

### Scenario Name
**Conflicting Decision Records**

### Condition
- Two Decision Objects with same decision_id
- Both exist in Decision Ledger
- Different timestamps, authorities, evidence sets
- Violates immutability principle

### Input State
```
Decision Ledger Entry 1:
  decision_id:      DEC_20260918_001
  timestamp:        2026-09-18T10:00:00Z
  authority_id:     AUTH_HG_001
  
Decision Ledger Entry 2 (DUPLICATE):
  decision_id:      DEC_20260918_001 (SAME ID)
  timestamp:        2026-09-18T14:00:00Z
  authority_id:     AUTH_PROCESS_002
```

### Expected Binding Result
**Status:** `INVALID`  
**Reasoning:**
- Duplicate decision IDs violate ledger immutability
- Cannot determine which is authoritative
- Ledger chain integrity compromised
- Fundamental system failure

**Decision Ledger Entry:** Binding state = INVALID
**Audit Memory:** Critical failure record "Duplicate_Decision_Identity"
**Timeline:** Binding validation stops immediately

### Governance Action
**Immediate:**
- Binding BLOCKED
- CRITICAL ESCALATION to Human Gate
- System integrity investigation required

**Investigation:**
1. Determine which entry is legitimate
2. Find root cause of duplicate (ledger bug? race condition?)
3. Review all decisions created during affected period
4. Determine if other duplicates exist

**Resolution:**
- Remove/invalidate duplicate entry
- Investigate ledger implementation
- May require system rebuild/verification
- Review all bindings created during this window

**Human Review:** YES - CRITICAL (system integrity breach)

---

## Scenario Matrix Summary

| Case | Scenario | Input Status | Expected Result | Governance Action | Human Review |
|------|----------|--------------|-----------------|-------------------|---------------|
| 01 | Normal Operation | All present, valid | VALID | Execute | NO |
| 02 | Evidence Missing | 1 of 3 missing | UNKNOWN | Investigate | YES |
| 03 | Authority Missing | Authority unknown | INVALID | Escalate | YES |
| 04 | Evidence Tampered | Hash mismatch | INVALID | **CRITICAL** | YES |
| 05 | Timestamp Violation | Retroactive evidence | INVALID/UNKNOWN | Investigate | YES |
| 06 | Authority Revoked Later | Valid at decision time | VALID | Proceed | NO |
| 07 | Partial Evidence | 4 of 5 present | UNKNOWN | Restore + retry | YES |
| 08 | Duplicate Decision | Ledger conflict | INVALID | **CRITICAL** | YES |

---

## Design Validation Coverage

- ✓ Normal operation success path
- ✓ Missing data scenarios (evidence, authority)
- ✓ Integrity failures (tampering detection)
- ✓ Temporal anomalies
- ✓ Historical state preservation
- ✓ Partial/incomplete data
- ✓ System integrity violations

---

## Document Status

**Status:** READY FOR GOVERNANCE BEHAVIOR SPECIFICATION  
**Next Step:** HG-M3-PHASE2-GOVERNANCE-BEHAVIOR-SPEC-20260918.md
