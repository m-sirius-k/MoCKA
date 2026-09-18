# HG-M3 Phase 2: Open Question Register
**Date:** 2026-09-18 | **Authority:** Human Gate | **Status:** DESIGN VERIFICATION

---

## Open Questions from Validation Scenario Design

Questions discovered during 8-scenario validation requiring Human Gate decision.

---

## CORE GOVERNANCE ISSUES (require decision)

### Q1: Evidence Restoration Cost-Benefit
**Category:** CORE GOVERNANCE ISSUE  
**Scenario:** CASE 02 (Evidence Missing in cold storage)

**Question:**
If evidence is recoverable from cold storage (24-48 hour restore time), should decision execution be BLOCKED until binding is VALID?

**Options:**
- A) Strict: Always block until binding valid (safest, but delays decisions)
- B) Risk-based: Allow execution if evidence likely recoverable (faster, but risk)
- C) Policy-based: Policy specifies threshold per decision type (flexible, complex)

**Impact:** Operational delay vs. assurance trade-off

**Human Gate Decision:** REQUIRED

---

### Q2: Authority Retroactive Registration
**Category:** CORE GOVERNANCE ISSUE  
**Scenario:** CASE 03 (Authority Missing)

**Question:**
If an authority is missing from registry but was legitimate (e.g., administrative error), can it be retroactively registered to validate past decisions?

**Options:**
- A) Never (strict immutability: authority must exist when decision made)
- B) Always (pragmatic: corrects administrative errors)
- C) Case-by-case (human judgment per incident)

**Impact:** Ledger integrity vs. flexibility

**Human Gate Decision:** REQUIRED

---

### Q3: Temporal Anomaly Tolerance
**Category:** CORE GOVERNANCE ISSUE  
**Scenario:** CASE 05 (Timestamp Conflict)

**Question:**
How much timestamp delay between evidence creation and decision reference is acceptable?

**Options:**
- A) Strict (≤1 second: evidence must be contemporaneous)
- B) Flexible (≤30 days: reasonable processing delay)
- C) Policy-based (thresholds per decision type)

**Impact:** Detection of retroactive evidence modification

**Human Gate Decision:** REQUIRED

---

## OPERATION POLICY ISSUES (process decisions)

### Q4: Partial Binding Execution
**Category:** OPERATION POLICY ISSUE  
**Scenario:** CASE 07 (Partial Evidence)

**Question:**
When evidence is pending restoration, can decision proceed with "binding pending" status?

**Status:** PENDING means:
- Decision is authorized in principle (4 of 5 evidence present)
- Binding will be retro-validated once evidence restored
- If evidence unrecoverable, decision can be reversed

**Options:**
- A) No: Always wait for complete binding (safest)
- B) Yes: Allow with time limit (e.g., 48 hours to complete binding)
- C) Conditional: Depends on decision criticality

**Impact:** Operational speed vs. assurance timing

**Human Gate Decision:** REQUIRED

---

### Q5: Binding Verification Frequency
**Category:** OPERATION POLICY ISSUE  
**Scenario:** Post-CASE06 (Authority evolution)

**Question:**
Should bindings be re-verified periodically (e.g., annually) or only at creation?

**Options:**
- A) Once only: Verify at creation, no periodic checks (simple, but late detection)
- B) Annual: Re-verify yearly to catch evidence destruction/corruption (catches drift)
- C) Continuous: Monitor all bindings for state changes (resource-intensive)

**Impact:** Detection latency for binding state changes

**Human Gate Decision:** REQUIRED

---

### Q6: Escalation Notification
**Category:** OPERATION POLICY ISSUE  
**Scenario:** CASE 04 (Evidence Tampering)

**Question:**
When binding fails with CRITICAL level (tampering, duplicate decision, unauthorized authority), who is notified and how urgently?

**Options:**
- A) Human Gate only, within business hours
- B) Human Gate + decision maker, within 1 hour
- C) Human Gate + auditor + decision maker, immediate (24/7)

**Impact:** Incident response time

**Human Gate Decision:** REQUIRED

---

## IMPLEMENTATION DETAIL QUESTIONS (clarification)

### Q7: Cold Storage Restore Time
**Category:** IMPLEMENTATION DETAIL  
**Scenario:** CASE 02, CASE 07

**Question:**
What is realistic restore time from cold storage?

**Design assumption:** 24-48 hours  
**Implementation reality:** TBD (depends on archive system)

**Status:** Clarification needed, does not block design approval

---

### Q8: Hash Algorithm Selection
**Category:** IMPLEMENTATION DETAIL  
**Scenario:** CASE 04 (Evidence Integrity)

**Question:**
SHA256 specified. Are there requirements for post-quantum resistance?

**Design assumption:** SHA256 sufficient for 5-year audit  
**Implementation reality:** May need algorithm agility

**Status:** Clarification needed, does not block design approval

---

### Q9: Timestamp Precision
**Category:** IMPLEMENTATION DETAIL  
**Scenario:** CASE 05, CASE 06

**Question:**
Should timestamps be ISO 8601 (second precision) or include microseconds?

**Design assumption:** ISO 8601 full format (YYYY-MM-DDTHH:MM:SSZ)  
**Implementation reality:** May need microsecond for concurrent decisions

**Status:** Clarification needed, does not block design approval

---

### Q10: Authority Snapshot Size
**Category:** IMPLEMENTATION DETAIL  
**Scenario:** CASE 06 (Historical authority)

**Question:**
Storing full authority object snapshot in ledger entry. Storage overhead?

**Design assumption:** Snapshot is "good enough" size  
**Implementation reality:** TBD (depends on authority object size)

**Status:** Clarification needed, does not block design approval

---

## Summary: Questions by Decision Category

| Category | Count | Decision Required | Examples |
|----------|-------|-------------------|----------|
| CORE GOVERNANCE | 3 | YES | Evidence restoration, retroactive registration, temporal tolerance |
| OPERATION POLICY | 3 | YES | Partial binding, verification frequency, escalation notification |
| IMPLEMENTATION DETAIL | 4 | NO | Restore time, hash algorithm, timestamp precision, snapshot size |

**Gate 2 (Design Finalization) must address:** 6 governance/policy questions

---

## Document Status

**Status:** READY FOR REVIEW PACKAGE INTEGRATION  
**Next Step:** HG-M3-PHASE2-BINDING-VALIDATION-REVIEW-PACKAGE-20260918.md

