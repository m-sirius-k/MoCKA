# HG-M3 Phase 2: Governance Behavior Specification
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** DESIGN VERIFICATION

---

## Governance Behavior Per Scenario

For each validation scenario, specify the governance actions and Human Gate decision requirements. **AI supplementation forbidden** — only state what the binding model requires, escalation points that require human judgment.

---

## CASE 01: Complete Normal Operation

### Input State
- Authority valid at decision_timestamp
- Decision exists with valid ID
- All evidence present and integrity verified
- Timestamps in correct order
- Validation passed all 6 checks

### Detected Condition
**Status:** VALID (all checks passed)

### Validation Result
**Binding State:** `VALID`  
**System Action:** Proceed to Decision Ledger entry

### Governance Action
**Automatic (no human required):**
1. Record binding as VALID in Decision Ledger
2. Store evidence snapshot in audit trail
3. Mark decision as authority-backed
4. Enable re-verification capability

**Governance Level:** Automatic (RBAC sufficient)

### Human Review Requirement
**NO** — Normal flow requires no escalation

---

## CASE 02: Evidence Missing

### Input State
- Decision references EV_002
- EV_002 not found in Evidence Store
- Other evidence present and valid

### Detected Condition
**Status:** Evidence missing (indeterminate cause)

### Validation Result
**Binding State:** `NOT_VERIFIED` (not proven false)  
**System Action:** Block binding, create failure record

### Governance Action

**Step 1: Automatic Detection**
- Binding validation fails at Check 3
- System records "EVIDENCE_MISSING" failure
- Audit trail preserved

**Step 2: Evidence Recovery Investigation (Automatic)**
- Query cold storage for EV_002
- Check deletion logs (last seen when?)
- Check ingestion queue (pending?)
- Set recovery status and ETA

**Step 3: Decision Point (REQUIRES HUMAN GATE)**

| Recovery Status | Governance Action | Timeline | Human Gate Decision |
|-----------------|-------------------|----------|-------------------|
| Found in cold storage | Restore from archive | 24-48h | Approve restoration |
| Recently deleted (<7d) | Recover from backup | Immediate | Approve recovery |
| Deleted (7d-90d ago) | Determine restoration cost | TBD | Approve or reject |
| Lost (>90d) | Cannot recover | N/A | Amend decision or reject |

**Human Gate Must Decide:**
1. Is evidence recovery worth the cost/time?
2. Can decision proceed while waiting for evidence?
3. If unrecoverable, is decision still valid without this evidence?

### Human Review Requirement
**YES** — Recovery path requires governance judgment

---

## CASE 03: Authority Missing

### Input State
- Authority ID not in registry
- No historical record
- Cannot verify decision maker

### Detected Condition
**Status:** Authority invalid (proven false, not indeterminate)

### Validation Result
**Binding State:** `INVALID`  
**System Action:** Block binding, escalate immediately

### Governance Action

**Step 1: Automatic Detection**
- Check 2 fails immediately
- System records "AUTHORITY_MISSING" failure
- CRITICAL escalation flag set

**Step 2: Investigation (Human Gate Required)**
- Verify authority ID accuracy (typo?)
- Check if authority should have been registered
- Examine authority delegation chain
- Determine if decision is fraudulent or administrative error

**Step 3: Resolution Decision (REQUIRES HUMAN GATE)**

| Finding | Action | Authority Decision |
|---------|--------|-------------------|
| Typo in authority ID | Correct and retry | Approve correction |
| Authority never registered | Register retroactively or reject | Approve registration or invalidate decision |
| Unauthorized decision | Invalidate decision | Reject decision entirely |

**Human Gate Must Decide:**
1. Is this a correctable administrative error?
2. Should authority be retroactively registered?
3. Is decision invalid due to unauthorized decision maker?

### Human Review Requirement
**YES CRITICAL** — Authority legitimacy must be verified by human

---

## CASE 04: Evidence Integrity Failure

### Input State
- Evidence hash mismatch detected
- Content changed after decision
- Original copy available in archive

### Detected Condition
**Status:** Evidence tampering/corruption detected (proven false)

### Validation Result
**Binding State:** `INVALID`  
**System Action:** Block binding, CRITICAL escalation

### Governance Action

**Step 1: Automatic Detection**
- Check 4 fails (hash mismatch)
- System retrieves archive copy
- Compares versions
- Documents tampering evidence

**Step 2: Forensic Analysis (Human Gate Required)**
- Determine if accidental or intentional tampering
- Identify who had access to evidence
- Review access logs
- Assess impact on decision validity

**Step 3: Resolution Decision (REQUIRES HUMAN GATE)**

| Determination | Action | Authority Decision |
|---------------|--------|-------------------|
| Accidental corruption | Restore original, retry binding | Approve restoration |
| Authorized modification | If documented, accept new version | Approve with audit |
| Unauthorized tampering | **SECURITY INCIDENT** | Invalidate decision, investigate |

**Human Gate Must Decide:**
1. Is tampering accidental or malicious?
2. Can decision proceed with restored original evidence?
3. Does integrity breach require security investigation?

### Human Review Requirement
**YES CRITICAL** — Tampering requires human investigation

---

## CASE 05: Timestamp Conflict

### Input State
- Evidence timestamp AFTER decision timestamp
- Temporal causality violated
- Possible clock skew or retroactive evidence creation

### Detected Condition
**Status:** Temporal ordering violation

### Validation Result
**Binding State:** `INVALID` or `NOT_VERIFIED` (depends on delta)  
**System Action:** Block binding, investigate

### Governance Action

**Step 1: Automatic Analysis**
- Calculate timestamp delta
- Check for clock skew (<1 minute = likely clock issue)
- Check for implausible delay (>1 year = archive, probably normal)

**Step 2: Classification**

| Delta | Likely Cause | Automatic Action |
|-------|--------------|------------------|
| <1 minute | Clock skew | Correct and retry |
| 1-30 minutes | Processing delay | Accept with documentation |
| 30 min - 6 hours | Deliberate delay | Require investigation |
| >6 hours | Suspicious delay | Escalate |

**Step 3: Human Gate Decision (IF delta > 30 minutes)**

**Human Gate Must Decide:**
1. Is timing plausible (e.g., test results computed after decision)?
2. Does evidence validity depend on evidence timestamp?
3. Should decision proceed with retroactive evidence?

### Human Review Requirement
**YES** (for non-trivial deltas) — Temporal anomalies require judgment

---

## CASE 06: Authority Revoked After Decision

### Input State
- Authority was valid at decision_timestamp
- Authority later revoked/expired
- Re-validation uses historical authority state

### Detected Condition
**Status:** Authority expired, but was valid at decision time

### Validation Result
**Binding State:** `VALID` (if authority was valid at decision time)  
**System Action:** Use historical authority snapshot

### Governance Action

**Step 1: Automatic**
- Retrieve authority snapshot at decision_timestamp
- Verify authority was valid then (not now)
- Mark binding as VALID with historical note

**Step 2: Governance Signal**
- No escalation needed (revocation only affects future decisions)
- Past decision remains authorized
- Audit trail preserves authority evolution

**Governance Level:** Automatic (historical state binding is intentional)

### Human Review Requirement
**NO** — Historical authority preservation is design feature, not failure

---

## CASE 07: Partial Evidence Set

### Input State
- Decision references 5 evidence items
- 4 present, 1 in cold storage
- 1 evidence item not immediately accessible
- Complete validation blocked

### Detected Condition
**Status:** Incomplete evidence set (indeterminate)

### Validation Result
**Binding State:** `NOT_VERIFIED` (cannot proceed)  
**System Action:** Block binding, schedule archive retrieval

### Governance Action

**Step 1: Automatic**
- Initiate archive restore for missing evidence
- Estimate restore time (24-48 hours)
- Create "binding pending" status

**Step 2: Governance Decision (REQUIRES HUMAN GATE)**

| Decision | Effect | Timeline |
|----------|--------|----------|
| Wait for restoration | Block decision until binding complete | 24-48h delay |
| Accept "binding pending" | Allow decision with conditional authorization | Immediate |
| Reject decision | Cannot proceed without complete evidence | Immediate |

**Human Gate Must Decide:**
1. Can decision execution proceed while evidence is being restored?
2. What is the risk tolerance for "binding pending" status?
3. Is conditional authorization acceptable?

### Human Review Requirement
**YES** — Operation policy (execution timing vs. binding completion)

---

## CASE 08: Duplicate Decision Identity

### Input State
- Two ledger entries with identical decision_id
- Different timestamps, authorities, evidence
- Ledger immutability violated
- **System integrity breach**

### Detected Condition
**Status:** Critical system failure (ledger corruption)

### Validation Result
**Binding State:** `INVALID`  
**System Action:** CRITICAL escalation, validation stops

### Governance Action

**Step 1: Immediate**
- Halt all binding validations
- Flag both duplicate entries
- Preserve both versions for forensics

**Step 2: Investigation (Human Gate Required)**
- Determine which entry is authoritative
- Root cause analysis (bug? race condition? manual error?)
- Search for other duplicates in ledger
- Timeline when duplication occurred

**Step 3: Remediation (Human Gate Required)**
- Invalidate duplicate entry
- Restore ledger integrity
- Re-validate affected bindings
- Implement prevention

**Human Gate Must Decide:**
1. Which entry is legitimate?
2. What caused the duplication?
3. Are there other corrupted entries?
4. How to restore ledger to consistent state?

### Human Review Requirement
**YES CRITICAL** — System integrity breach requires expert human review

---

## Summary: Governance Decision Requirements

| Case | Binding State | Automatic | Human Review | Escalation Level |
|------|---------------|-----------|--------------|------------------|
| 01 | VALID | YES | NO | None |
| 02 | NOT_VERIFIED | Investigation | YES | Standard |
| 03 | INVALID | Escalate | YES | **CRITICAL** |
| 04 | INVALID | Escalate | YES | **CRITICAL** |
| 05 | INVALID/NOT_VERIFIED | Analysis | YES | Standard/Critical |
| 06 | VALID | YES | NO | None |
| 07 | NOT_VERIFIED | Initiate restore | YES | Standard |
| 08 | INVALID | Escalate | YES | **CRITICAL** |

---

## Human Gate Decision Categories

### Category A: Automatic (No escalation)
- CASE 01: Normal operation
- CASE 06: Historical authority handling
**Count:** 2 scenarios

### Category B: Standard Escalation (Investigation required)
- CASE 02: Evidence recovery
- CASE 05: Temporal anomalies (minor)
- CASE 07: Archive restoration
**Count:** 3 scenarios

### Category C: Critical Escalation (System integrity or security)
- CASE 03: Authority legitimacy
- CASE 04: Tampering/corruption
- CASE 05: Temporal anomalies (major)
- CASE 08: Ledger corruption
**Count:** 4 scenarios

---

## Key Governance Principles Embedded

1. **Fail-Closed:** Invalid binding → escalate, never allow
2. **UNKNOWN ≠ INVALID:** Indeterminate → investigate, not auto-reject
3. **Historical State:** Past authority valid at decision time, even if revoked now
4. **Audit Preservation:** All failures recorded for forensics
5. **Human Judgment:** Escalations require human review (no AI supplementation)

---

## Document Status

**Status:** READY FOR VALIDATION BOUNDARY DEFINITION  
**Next Step:** HG-M3-PHASE2-VALIDATION-BOUNDARY-DEFINITION-20260918.md

**Note:** AI is forbidden from deciding Case 02, 03, 04, 05, 07, 08. All require Human Gate decision.
