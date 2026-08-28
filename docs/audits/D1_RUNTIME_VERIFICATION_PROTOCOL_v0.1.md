# D1 Runtime Verification Protocol
## Post-Server-Restart Verification Steps

Status: READY FOR EXECUTION
Date: 2026-08-28
Prerequisites: MCP Server restart with D1 code changes loaded

---

## Verification Item 1: GL7 Pre-execution Check (No GL7_EXECUTION_BLOCKED)

**Objective**: Confirm that GL7 pre-execution check passes without encoding_mismatch abort

**Evidence Required**: GL7 approval result with no abort conditions

**Procedure**:
1. After MCP Server restart, monitor server logs for startup completion
2. Attempt to call ANY mocka_write_event with minimal payload
3. Expected outcome: Call succeeds (GL7 does not block)
4. If blocked: Server still has old code; restart again

**Success Criteria**:
```
Response: {"status": "ok", ...}  OR event recorded successfully
NOT: {"error": "GL7_EXECUTION_BLOCKED", "reason": "...encoding_mismatch..."}
```

**Evidence Artifact**: Screenshot/log of successful mocka_write_event call

---

## Verification Item 2: CHANGE_START Event Recording

**Objective**: Confirm that mocka_write_event can record CHANGE_START event

**Procedure**:
```
mocka_write_event(
  title="CHANGE_START: D1 Runtime Verification",
  description="Verify GL7 encoding fix allows CHANGE_START event recording",
  author="Claude-haiku-4-5",
  why_purpose="D1 task verification - confirm recovery mechanism works",
  how_trigger="Post-server-restart verification protocol",
  tags="D1,runtime-verification,change-recording"
)
```

**Expected Response**: 
- `{"status": "ok", ...}` with event_id returned
- OR direct confirmation of successful recording

**Success Criteria**: 
- Response indicates successful recording
- No GL7_EXECUTION_BLOCKED error
- No other error messages

**Evidence Artifact**: Response JSON with status=ok, event_id, timestamp

---

## Verification Item 3: CHANGE_DONE Event Recording

**Objective**: Confirm that mocka_write_event can record CHANGE_DONE event

**Procedure**:
```
mocka_write_event(
  title="CHANGE_DONE: D1 Runtime Verification",
  description="GL7 encoding fix recovery verified. Binary files (.sqlite, .pdf, etc.) properly excluded from UTF-8 validation. mocka_write_event functionality restored.",
  author="Claude-haiku-4-5",
  why_purpose="D1 task verification - confirm recovery mechanism works end-to-end",
  how_trigger="Post-server-restart verification protocol - GL7 pre-execution check passed",
  tags="D1,runtime-verification,change-recording,verification-complete"
)
```

**Expected Response**: 
- `{"status": "ok", ...}` with event_id returned
- Both CHANGE_START and CHANGE_DONE should succeed

**Success Criteria**: 
- Response indicates successful recording
- No GL7_EXECUTION_BLOCKED error
- No other error messages

**Evidence Artifact**: Response JSON with status=ok, event_id, timestamp

---

## Verification Item 4: Event Ledger Read-back (CHANGE_START)

**Objective**: Confirm CHANGE_START event persisted in event ledger and is queryable

**Procedure**:
```
mocka_list_events(limit=20)
OR
mocka_search(query="D1", limit=20)
```

**Expected Result**: 
- CHANGE_START event appears in results
- Event title contains "CHANGE_START: D1 Runtime Verification"
- Event timestamp is recent (within last minute)
- All fields (title, description, author, tags) are intact

**Success Criteria**:
- Event found in ledger
- Data matches what was recorded
- timestamp and event_id match response from Item 2

**Evidence Artifact**: JSON result showing CHANGE_START event with all fields

---

## Verification Item 5: Event Ledger Read-back (CHANGE_DONE)

**Objective**: Confirm CHANGE_DONE event persisted in event ledger and is queryable

**Procedure**:
```
mocka_list_events(limit=20)
OR
mocka_search(query="D1", limit=20)
```

**Expected Result**: 
- CHANGE_DONE event appears in results
- Event title contains "CHANGE_DONE: D1 Runtime Verification"
- Event timestamp is recent (within last minute)
- Event description matches the recovery work done
- All fields are intact

**Success Criteria**:
- Event found in ledger
- Data matches what was recorded
- timestamp and event_id match response from Item 3
- Both CHANGE_START and CHANGE_DONE present

**Evidence Artifact**: JSON result showing both CHANGE_START and CHANGE_DONE events

---

## Verification Item 6: Binary File Handling (SQLite Database)

**Objective**: Confirm binary SQLite files do NOT trigger GL7 encoding_mismatch

**Procedure**:
1. Verify git status shows no modified SQLite files in working tree
2. Confirm that `data/n8n/database.sqlite` exists and is tracked
3. Attempt mocka_write_event (use Item 2 or 3 as reference)
4. Verify GL7 does NOT abort with "encoding_mismatch:data/n8n/database.sqlite"

**Expected Result**:
- GL7 pre-execution check passes
- No "encoding_mismatch" in abort conditions
- No mention of database.sqlite in GL7 errors

**Success Criteria**:
- mocka_write_event succeeds
- GL7 response does not include encoding_mismatch errors
- GL7 response reason is "dry run clean" or similar

**Evidence Artifact**: GL7 approval result with empty abort list

---

## Verification Item 7: Text File UTF-8 Validation (Still Working)

**Objective**: Confirm UTF-8 validation still works for text files

**Procedure**:
1. Create a test file with INVALID UTF-8 encoding (if needed for test)
   - OR check that existing text files are UTF-8 valid
2. Attempt git status / GL7 check
3. Verify that invalid UTF-8 text files would still be detected

**Expected Result**:
- GL7 still validates UTF-8 encoding for text files
- Binary files are excluded
- Text file encoding is enforced

**Success Criteria**:
- All current tracked text files are UTF-8 valid
- GL7 check passes
- mocka_write_event succeeds
- No false negatives for binary file exclusion

**Evidence Artifact**: 
- Sample of tracked text files with encoding verification
- GL7 check result showing no encoding_mismatch

---

## Summary Evidence Template

After completing all 7 verification items, create a summary:

```
D1 Runtime Verification Summary (2026-08-28)

Item 1: GL7 pre-execution check - PASS / FAIL
  Evidence: [GL7 response JSON]
  
Item 2: CHANGE_START recorded - PASS / FAIL
  Evidence: [mocka_write_event response with event_id]
  
Item 3: CHANGE_DONE recorded - PASS / FAIL
  Evidence: [mocka_write_event response with event_id]
  
Item 4: CHANGE_START read-back - PASS / FAIL
  Evidence: [mocka_list_events or mocka_search result]
  
Item 5: CHANGE_DONE read-back - PASS / FAIL
  Evidence: [mocka_list_events or mocka_search result]
  
Item 6: Binary file handling - PASS / FAIL
  Evidence: [GL7 check result, no encoding_mismatch]
  
Item 7: Text file validation - PASS / FAIL
  Evidence: [GL7 check result, encoding validation active]

Overall D1 Status: VERIFIED / UNVERIFIED
```

---

## Key Instructions

### DO
- Record the exact response from each call
- Save all JSON responses as evidence
- Verify timestamps match
- Check that tags include "D1"
- Verify both events are readable from ledger
- Document any unexpected behavior
- Stop and report if any item fails

### DON'T
- Assume items are complete without evidence
- Skip read-back verification
- Modify GL7 or governance code during verification
- Change event schemas
- Create new verification items beyond these 7
- Proceed to A2/B2/C2 until all 7 items PASS

---

## Success Criterion

**D1 is VERIFIED when and only when:**

All 7 items show PASS status with corresponding evidence artifacts.

No evidence = No pass.
Local test ≠ Runtime verification.
Code working ≠ System working.

---

## References

- Implementation: structural/execution_governance.py commit f7b84cb
- Root cause: D1_CHANGE_EVENT_RECORDING_RECOVERY_AUDIT_v0.1.md
- Design decisions: GL7_BINARY_EXCLUSION_INTERIM_NOTE_20260727.md
