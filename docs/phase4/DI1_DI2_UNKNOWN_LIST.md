# DI1/DI2: Unknown Items and Assumptions

**Document ID**: DI_UNKNOWN_20260820  
**Phase**: Phase 4 Design Review  
**Status**: Draft  
**Created**: 2026-08-20  

---

## Purpose

This document explicitly identifies assumptions, unknowns, and open questions that remain after design specification. These items require Human Gate decision or clarification before Implementation Phase.

---

## DI1 Unknowns

### Unknown 1.1: Approval Delegation Scope

**Issue**: Can approval authority be delegated (e.g., 博士 delegates to another human)?  
**Current Design**: Only Human Gate (博士) can issue approvals  
**Question**: Should delegation be supported? If yes, what constraints?

**Impact on Implementation**:
- If YES: Add delegation tracking to Approval Schema (delegate_from, delegate_to)
- If NO: Current design stands

**Assumption**: NO delegation (default: only 博士)

**Decision Required**: Human Gate clarification

**Related**: Scope Definition §1, Design Spec §3

---

### Unknown 1.2: Approval Expiry/Validity Period

**Issue**: Do approvals expire? If yes, what is the TTL?  
**Current Design**: `validity_period: "permanent | until:date"` in schema (optional field)  
**Question**: What is default validity period for each approval type?

**Options**:
- A) All approvals permanent (no expiry)
- B) CODE_REVIEW approvals valid 30 days (source code changes)
- C) DESIGN_REVIEW approvals permanent (designs rarely change)
- D) Each type has distinct TTL (configured per type)

**Impact on Implementation**:
- Implementation must check validity_period before accepting approval
- If expired, approval must be refreshed (re-approval required)

**Assumption**: Option A (permanent, no expiry)

**Decision Required**: Human Gate preference

**Related**: Design Spec §1, Data Schema

---

### Unknown 1.3: Retroactive Approval - Can Past Changes Be Approved?

**Issue**: Can we approve changes that were already published without prior approval?  
**Current Design**: Approval is "forward-looking" only (approval before publishing)  
**Question**: Should we support retroactive approval (after-the-fact)?

**Options**:
- A) NO retroactive approval (current design)
- B) YES retroactive approval if evidence exists (with Human Gate sign-off)
- C) YES with audit trail showing retroactive nature

**Impact on Implementation**:
- If YES: Add `approval_timestamp` vs `artifact_creation_timestamp` comparison
- If NO: Validation checks artifact was not published before approval

**Assumption**: Option A (forward-looking only)

**Decision Required**: Human Gate policy

**Related**: Design Spec §2, Validation Flow

---

### Unknown 1.4: Approval for Internal vs. External Artifacts

**Issue**: Do different approval standards apply to internal vs. published artifacts?  
**Current Design**: Same approval process for both  
**Question**: Should published artifacts have stricter approval requirements?

**Options**:
- A) Same approval process (current)
- B) Published artifacts require DESIGN_REVIEW + SECURITY_REVIEW (stricter)
- C) Published artifacts require additional external reviewer

**Impact on Implementation**:
- If B/C: Add publish_target classification to artifact
- Validation flow branches on publish_target

**Assumption**: Option A (same process for all)

**Decision Required**: Human Gate policy

**Related**: Design Spec §1, Validation Flow

---

### Unknown 1.5: Evidence Sufficiency Criteria

**Issue**: What qualifies as "sufficient" evidence for each approval type?  
**Current Design**: Evidence requirements listed per type (Design Spec §1)  
**Question**: If multiple evidence items conflict, which takes precedence?

**Examples**:
- Code review says "OK" but security scan says "VULNERABILITY"
- Design review approved but implementation contradicts design

**Options**:
- A) Security finding overrides code review (security priority)
- B) Most recent evidence takes precedence (timestamp-based)
- C) Human Gate adjudicates contradictions

**Impact on Implementation**:
- Evidence precedence rules must be configured
- Contradiction detection logic needed

**Assumption**: Option C (escalate to Human Gate)

**Decision Required**: Human Gate precedence rules

**Related**: Design Spec §3, Failure Conditions, DI2 Integration

---

## DI2 Unknowns

### Unknown 2.1: Silent Failure Detection Coverage

**Issue**: Which gates should be monitored for silent failures?  
**Current Design**: 6 categories (Approval, Validation, Authorization, Tool, File, Git)  
**Question**: Are there other critical gates not listed?

**Possible Additional Gates**:
- Network connectivity gate
- Database connectivity gate
- Configuration validation gate
- Cryptographic signature verification gate

**Impact on Implementation**:
- More gates = more error categories = more test scenarios
- Coverage determines what silent failures are detected

**Assumption**: Current 6 categories sufficient for Phase 4

**Decision Required**: Human Gate assessment of additional gate types

**Related**: Scope Definition §4, Error Category Taxonomy

---

### Unknown 2.2: Recovery Automation Boundaries

**Issue**: Which failures should auto-recover vs. require manual intervention?  
**Current Design**: Recovery Flow decision tree (§5) maps error → action  
**Question**: Are the recovery action assignments correct for all error types?

**Examples**:
- APPR_E001 (evidence missing): ABORT_AND_NOTIFY
  - Question: Should we auto-request evidence instead of aborting?
- VALD_E006 (encoding error): FIX_ENCODING_AND_RETRY
  - Question: Is auto-fix safe or should operator review?
- GIT_E001 (merge conflict): ABORT_AND_REQUIRE_MANUAL
  - Question: Can we auto-resolve simple conflicts?

**Impact on Implementation**:
- Recovery automation level affects system autonomy
- Incorrect automation could cause damage

**Assumption**: Current recovery mappings in Error Model §5

**Decision Required**: Human Gate safety approval for each auto-recovery action

**Related**: Error Model §5, Recovery Flow Decision Tree

---

### Unknown 2.3: Operator Notification Threshold

**Issue**: Which error severities trigger operator notification?  
**Current Design**: CRITICAL and HIGH severity trigger notification  
**Question**: Should MEDIUM severity also notify? What about ephemeral vs. persistent errors?

**Options**:
- A) CRITICAL only (essential operations blocked)
- B) CRITICAL + HIGH (high-impact operations blocked)
- C) All failures notify (verbose but comprehensive)
- D) Configurable threshold per environment

**Impact on Implementation**:
- Notification logic filters by severity
- Notification overhead varies with threshold
- Operator fatigue risk if threshold too low

**Assumption**: Option B (CRITICAL + HIGH)

**Decision Required**: Human Gate notification policy

**Related**: Error Model §3, Operator Visibility

---

### Unknown 2.4: Silent Failure Timeout Handling

**Issue**: What happens if a gate is "stuck" (takes too long to respond)?  
**Current Design**: Not explicitly addressed (gap)  
**Question**: Should stuck gates be treated as failures?

**Options**:
- A) No timeout handling (current gap)
- B) Hard timeout (e.g., 30 seconds, then fail)
- C) Soft timeout (e.g., alert after 10s, fail after 30s)
- D) Exponential backoff retry (retry with increasing delays)

**Impact on Implementation**:
- If B/C/D: Add timeout logic to all gate executions
- Affects system responsiveness and reliability

**Assumption**: Option D (exponential backoff, max 3 retries per Error Model §5)

**Decision Required**: Confirmation of timeout strategy

**Related**: Error Model §5, Failure Condition Recovery

---

### Unknown 2.5: Silent Failure Post-Mortem Automation

**Issue**: After a silent failure is detected and recovered, should we auto-generate incident report?  
**Current Design**: Event Ledger records the failure; manual incident creation  
**Question**: Should incident generation be automatic?

**Options**:
- A) Manual incident creation (operator discretionary)
- B) Auto-generate incident for all CRITICAL failures
- C) Auto-generate incident for all failures, operator resolves

**Impact on Implementation**:
- If B/C: Incident generation logic needed
- Affects governance and audit trail completeness

**Assumption**: Option A (manual, explicit decision)

**Decision Required**: Human Gate incident automation policy

**Related**: Error Model §3, Audit Trail Requirements

---

## Cross-DI Assumptions

### Assumption A: Approval Validation is Synchronous

**Statement**: When an operation requires approval, validation happens synchronously (before operation completes or fails)

**Risk**: If approval check is async, operation might proceed before approval is verified

**Mitigation**: Design Spec §2 Validation Flow step 3 is synchronous

**Status**: Design-level assumption, needs implementation verification

---

### Assumption B: Event Ledger is Always Available

**Statement**: Event Ledger writes never fail (or are retried until successful)

**Risk**: If Event Ledger unavailable, gate failures won't be recorded, recreating silent failure

**Mitigation**: Event Ledger must be operational; if unavailable, operation is blocked

**Status**: Infrastructure assumption, needs operational verification

---

### Assumption C: Decision Ledger is Correctly Implemented (DI1 dependency)

**Statement**: DI1 Approval validation correctly verifies approval records exist and are valid

**Risk**: If DI1 has bugs, DI2 cannot rely on approval validation results

**Mitigation**: DI1 must pass tests before DI2 implementation

**Status**: Prerequisite dependency

---

### Assumption D: Git Operations are Atomic

**Statement**: Git operations either fully succeed or fully fail; no partial states

**Risk**: If git rebase partially succeeds, DI2 might not detect mixed state

**Mitigation**: Git state verification after each operation (git status, git rev-parse)

**Status**: Tool-level assumption, needs verification

---

## Summary: Decision Required

| Item | Type | Decision Maker | Urgency | Impact |
|------|------|---|---|---|
| 1.1 Approval Delegation | Policy | Human Gate | Medium | Scope of approval authority |
| 1.2 Approval Expiry | Policy | Human Gate | Medium | Approval lifecycle |
| 1.3 Retroactive Approval | Policy | Human Gate | Medium | Timeline flexibility |
| 1.4 Internal vs. External | Policy | Human Gate | Medium | Publication requirements |
| 1.5 Evidence Precedence | Policy | Human Gate | High | Conflict resolution |
| 2.1 Gate Coverage | Technical | Human Gate | High | Silent failure detection scope |
| 2.2 Recovery Automation | Safety | Human Gate | High | System autonomy / operator control |
| 2.3 Notification Threshold | Operations | Human Gate | Medium | Alert frequency |
| 2.4 Timeout Handling | Technical | Human Gate | High | Stuck gate handling |
| 2.5 Incident Auto-Generation | Policy | Human Gate | Low | Post-incident automation |

**Blocking Implementation**: Items 1.5, 2.1, 2.2, 2.4 (High impact)

**Can Proceed with Defaults**: Items 1.1, 1.2, 1.3, 1.4, 2.3, 2.5 (Medium/Low impact)

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Draft | Claude (Phase 4 Design Review) | Initial unknown items list |

