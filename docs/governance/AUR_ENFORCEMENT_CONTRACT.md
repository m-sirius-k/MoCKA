# A-U-R Enforcement Contract
## ID: CONT-AUR-ENFORCEMENT-v1.0
## Status: WEB_PREPARED (PC Runtime Verification required)
## Date: 2026-10-02
## Canon Reference: docs/contracts/action_execution_contract_v1.md Stage 5

---

## 1. Theorem

Executable(a,t) <=> Assessment_Admissible(a,t)
               AND Authority_Valid(a,t)
               AND Runtime_Conformant(a,t)

Abbreviation: A AND U AND R

---

## 2. The Single Enforcement Point

There MUST be exactly ONE place in the system where A AND U AND R are
evaluated simultaneously before execution is permitted. This file defines
that point.

Implementation: aur/enforcement.py :: EnforcementPoint.check()

Inputs:
  assessment  : AssessmentRecord | dict | None  (A condition)
  gate_result : dict | None                     (U condition)
  gl7_result  : dict | None                     (R condition)

Output:
  {"decision": "ALLOW"|"DENY", "reason": str, "enforcement_id": str, ...}

---

## 3. A Condition (Assessment)

Evaluator: aur/assessment.py :: create_assessment()
Admissible when:
  - assessment is not None
  - assessment.admissible == True
  - assessment.confidence >= 0.5 (CONFIDENCE_THRESHOLD)

Fail-closed:
  - assessment is None -> DENY
  - assessment.admissible is False -> DENY
  - confidence < 0.5 -> DENY
  - exception during check -> DENY

UNKNOWN axes: allowed, each reduces confidence by 0.15

---

## 4. U Condition (Authorization)

Authority: Human Gate ONLY (phi_os/human_gate.py)
Valid when: gate_result.status == "APPROVED"

Fail-closed:
  - gate_result is None -> DENY (BA04 bypass prevention)
  - status == "PENDING" -> DENY
  - status == "REJECTED" -> DENY
  - status == "EXPIRED" -> DENY
  - status == "CANCELED" -> DENY
  - status is None -> DENY

NOTE: AI, JARVIS, HAB, くろこ are NOT authority holders.
The Human Gate is the ONLY valid authority source for U=True.

---

## 5. R Condition (Runtime Conformance)

Evaluator: structural/execution_governance.py :: GL7.pre_execution_check()
Conformant when: gl7_result.approved == True AND gl7_result.aborts == []

Abort conditions that trigger R=False:
  - new_directory_detected
  - unexpected_file_count
  - deletion_outside_scope
  - grounding_not_completed

Fail-closed:
  - gl7_result is None -> DENY
  - approved is None -> DENY
  - approved == False -> DENY
  - aborts non-empty -> DENY

---

## 6. Decision Output

ALLOW: A=True AND U=True AND R=True
DENY: any condition False or exception

The decision MUST be recorded as an EnforcementRecord before execution proceeds.

---

## 7. BA04 Bypass Prevention

BA04 = execution without Human Gate approval.

This contract prevents BA04 by:
1. Requiring gate_result as a non-None input
2. Accepting ONLY "APPROVED" status (all other values -> DENY)
3. Having no override, no fallback, no exception to this rule

Any code path that reaches execution without passing through
EnforcementPoint.check() is a BA04 bypass violation.

---

## 8. Memory and Consequence Post-Execution

After ALLOW + Execute:
1. ConsequenceRecord MUST be created (aur/consequence.py)
2. ExperienceMemoryEntry MUST be written (memory/experience_memory.py)
3. Reassessment context is available for next assessment of same action

The enforcement point itself does NOT trigger consequence recording.
That is the caller's responsibility per Action Execution Contract (Stage 7-8).

---

## 9. Non-Byppassable Properties

- The fail-closed logic (DENY on None/exception) cannot be overridden
- The Human Gate APPROVED requirement cannot be relaxed
- No "test mode", "dry run mode", or "admin override" bypasses the U check
- The enforcement_id MUST be generated for every call (including DENY)

---

## 10. PC Verification Required

This contract is WEB_PREPARED. Runtime verification on C:\Users\sirok\MoCKA is
required before marking as RUNTIME_VERIFIED.

PC verification checklist:
[ ] EnforcementPoint.check() importable on real Windows Python
[ ] All 13 deny tests pass on C:\Users\sirok\MoCKA
[ ] Event recorded via mocka_write_event when called
[ ] Integration with phi_os/human_gate.py tested
[ ] Integration with GL7 (structural/execution_governance.py) tested
