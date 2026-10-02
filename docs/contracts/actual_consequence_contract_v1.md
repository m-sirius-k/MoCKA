# Contract C: Actual Consequence Contract v1.0

## ID: CONT-ACTUAL-CONSEQUENCE-v1.0
## Status: ACTIVE
## Date: 2026-10-02
## Author: MoCKA Implementation Session (E20261002_981617553cb52)

---

## 1. Purpose

"Execution Success != Actual Consequence Verified" is a core MoCKA principle.
This contract defines what constitutes an Actual Consequence record and how
it differs from mere execution success/failure.

Execution success means: the Python function returned without raising an exception.
Actual Consequence means: the observable state change in the world was verified.

---

## 2. Scope

This contract governs:
- ConsequenceRecord schema
- What constitutes a verified consequence
- How ConsequenceRecord links to AssessmentRecord
- How ConsequenceRecord feeds into Experience Memory

---

## 3. ConsequenceRecord Schema

Required fields:
- consequence_id: str     (unique, format: CONSQ-{YYYYMMDD}-{hex8})
- action_id: str          (links to the executed action)
- assessment_id: str      (links to Contract A AssessmentRecord)
- timestamp: str          (ISO 8601 UTC, time of consequence observation)
- execution_success: bool (did the execution function return without exception)
- consequence_verified: bool (was the actual state change verified)
- verification_method: str   (how was verification performed)
- actual_changes: list[str]  (list of observed changes)
- expected_changes: list[str] (what was expected from dry run)
- deviation: list[str]    (actual_changes XOR expected_changes)
- outcome: str            (SUCCESS | PARTIAL | FAILURE | UNKNOWN)

Optional fields:
- error_detail: str       (if execution_success=False)
- verification_error: str (if consequence_verified=False due to verification failure)

---

## 4. Outcome Classification

SUCCESS: execution_success=True AND consequence_verified=True AND deviation=[]
PARTIAL: execution_success=True AND (consequence_verified=True AND deviation != [])
FAILURE: execution_success=False OR (consequence_verified=True AND actual changes
         indicate rollback/error state)
UNKNOWN: consequence_verified=False (verification could not be performed)

---

## 5. Verification Methods

Acceptable verification methods:
- "git_diff": compare git status before and after
- "file_hash": compare file hashes before and after
- "db_query": query database for expected record presence
- "api_response": check API response matches expected state
- "manual": human verified (requires Human Gate confirmation)
- "unverified": verification not implemented for this action type

"unverified" is an acceptable value but MUST be recorded honestly.
The presence of "unverified" in the record does NOT make the consequence
record invalid; it makes the UNKNOWN outcome legitimate.

---

## 6. Deviation Handling

If deviation != []:
- The deviation MUST be recorded even if execution was "successful"
- The deviation MUST be fed into Experience Memory as a signal
- A HIGH deviation (more than 20% of expected changes) SHOULD trigger
  a reassessment request

---

## 7. Linking Requirements

ConsequenceRecord MUST link to:
- AssessmentRecord via assessment_id
- The action's mocka_write_event via action_id

ConsequenceRecord MUST be created even when:
- Execution failed (execution_success=False)
- Verification failed (set consequence_verified=False, outcome=UNKNOWN)
- The action was a dry run (consequence_verified=True, actual_changes=[])

---

## 8. Fail-Closed

If ConsequenceRecord cannot be created (exception during consequence recording):
- The failure MUST be logged to mocka_write_event
- The enforcement point's record MUST be updated with consequence_error
- Experience Memory MUST NOT receive a consequence without a record
