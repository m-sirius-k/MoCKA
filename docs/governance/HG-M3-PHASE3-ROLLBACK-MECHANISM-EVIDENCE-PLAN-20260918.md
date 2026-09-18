# HG-M3 Phase 3: Rollback Mechanism Evidence Plan
**Date:** 2026-09-18 | **Authority:** Conditional Authorization (Option B) | **Status:** PREPARATION

---

## PURPOSE

Define and verify rollback mechanisms for Phase 3. This document specifies:
- When rollback is required
- How rollback is executed
- What recovery procedures are available
- How rollback success is verified
- Evidence collection during rollback

---

## ROLLBACK TRIGGER CONDITIONS

### Trigger Condition T1: Production Contamination Detected
**Definition:** Any Phase 3 code or data found in production systems

**Detection Method:**
- Automated: Production database audit scan (hourly)
- Manual: Code review finds production connections in Phase 3 branch
- Alert: Connection attempt to production logged as CRITICAL

**Rollback Decision:** IMMEDIATE
**Authority:** Automated (no Human Gate approval needed for emergency rollback)

**Response Time:** < 5 minutes from detection

---

### Trigger Condition T2: Data Leakage Confirmed
**Definition:** Production data found in sandbox database

**Detection Method:**
- Automated: Data origin audit (data provenance check)
- Manual: Test results show production table references
- Alert: Write-to-production-table transaction rolled back + logged

**Rollback Decision:** IMMEDIATE
**Authority:** Automated

**Response Time:** < 5 minutes from confirmation

---

### Trigger Condition T3: Credential Exposure
**Definition:** Production API key or password found in Phase 3 code/logs

**Detection Method:**
- Automated: Pre-commit credential scanning
- Automated: Runtime credential leak detection
- Manual: Security audit discovers exposed credential

**Rollback Decision:** IMMEDIATE + Credential Rotation
**Authority:** Automated (then Human Gate notification)

**Response Time:** < 5 minutes + credential rotation < 1 hour

---

### Trigger Condition T4: Unrecoverable Test Failure
**Definition:** Sandbox state corrupted such that rollback is necessary

**Detection Method:**
- Test failure + manual inspection shows database corruption
- Schema mismatch prevents test continuation
- Data integrity check fails multiple times

**Rollback Decision:** MANUAL (Human Gate approval after assessment)
**Authority:** Implementation team + Human Gate review

**Response Time:** Assessment < 30 minutes, then rollback < 1 hour

---

## ROLLBACK CHECKPOINTS

### Checkpoint CP1: Pre-Implementation Snapshot
**Timing:** Day 1 of Phase 3 (before any code changes)

**Content:**
```
Snapshot Type: Full database backup
Source: Sandbox database (sb_phase3.db)
State: Empty or clean baseline
Checksum: SHA256 hash calculated and stored
```

**Storage Location:** `/home/user/MoCKA/data/rollback/phase3_pre_implementation.backup`

**Verification:**
```
Restore Test: Restore from checkpoint, verify database is intact
Checksum Test: SHA256 matches original
Size Test: File size and schema match expectations
Timestamp: Checkpoint recorded with ISO 8601 timestamp
```

**Rollback From CP1:**
```
Step 1: Delete current sandbox database
Step 2: Restore from phase3_pre_implementation.backup
Step 3: Verify schema integrity
Step 4: Confirm all Phase 3 code changes reverted in database
Result: Sandbox returns to clean initial state
```

**Recovery Timeline:** 5-10 minutes

---

### Checkpoint CP2: Code Milestone Snapshot (Weekly)
**Timing:** End of each development week (Friday)

**Content:**
```
Type: Git commit checkpoint + database backup
Git Commit: Tag as release/phase3-week1, release/phase3-week2, etc.
Database: Backup of sandbox database at end of week
Code State: Specific commit hash recorded
```

**Storage Location:** 
- Git: Tagged commits (via `git tag`)
- Database: `/home/user/MoCKA/data/rollback/phase3_week1_backup.backup`

**Verification:**
```
Git Verification: Tag points to correct commit
Branch State: Confirm branch history is accurate
Database State: Verify backup matches code checkpoint
Consistency: Code and data checkpoint in sync
```

**Rollback From CP2:**
```
Step 1: Restore database from phase3_weekN_backup.backup
Step 2: Reset git branch to release/phase3-weekN tag
Step 3: Rebuild code from checkpoint
Step 4: Verify test suite passes at checkpoint state
Step 5: Confirm data integrity post-rollback
Result: Sandbox returns to last known good state at week boundary
```

**Recovery Timeline:** 15-30 minutes

---

### Checkpoint CP3: Test Execution Checkpoint
**Timing:** Before each test run (unit/integration/validation)

**Content:**
```
Type: Database snapshot before destructive operations
Purpose: Enable rollback if test corrupts data
Database: Backup before test execution
Test ID: Record which test this checkpoint guards
```

**Storage Location:** `/home/user/MoCKA/data/rollback/phase3_test_TESTID_backup.backup`

**Verification:**
```
Existence: Checkpoint file exists and is readable
Timestamp: Recorded before test start
Size: Backup file size matches current database
CRC: Checksum validates integrity
```

**Rollback From CP3:**
```
Step 1: Detect test failure or data corruption
Step 2: Restore database from phase3_test_TESTID_backup.backup
Step 3: Re-run test from restored state
Step 4: Verify same failure reproduced (or different error)
Step 5: Log test failure evidence for analysis
Result: Database returns to pre-test state, test can be re-run
```

**Recovery Timeline:** 2-5 minutes per checkpoint

---

### Checkpoint CP4: Schema Deployment Checkpoint
**Timing:** Before creating or modifying sandbox database schema

**Content:**
```
Type: Database schema export (DDL statements)
Purpose: Enable schema rollback if deployment fails
Format: SQL schema dump (`sqlite3 .schema > schema_export.sql`)
Completeness: Includes all tables, indices, constraints
```

**Storage Location:** `/home/user/MoCKA/data/rollback/phase3_pre_schema.sql`

**Verification:**
```
File Format: Valid SQL syntax (parseable)
Table Count: Matches expected count of sb_* tables
Schema Completeness: All constraints present
Index Completeness: All indices present
```

**Rollback From CP4:**
```
Step 1: Delete corrupt or partial schema
Step 2: Restore from phase3_pre_schema.sql
Step 3: Verify schema integrity (`PRAGMA integrity_check`)
Step 4: Validate table structure matches code expectations
Step 5: Confirm data constraints are enforced
Result: Database schema returns to consistent state
```

**Recovery Timeline:** 5 minutes

---

## RECOVERY PROCEDURES

### Procedure R1: Emergency Production Isolation Rollback
**Trigger:** Production contamination detected (Condition T1)

**Steps:**

```
1. IMMEDIATE ACTIONS (< 1 minute)
   - Kill all Phase 3 processes
   - Close all connections to production systems
   - Disable deployment pipelines
   - Record incident timestamp

2. ISOLATION VERIFICATION (< 2 minutes)
   - Verify no Phase 3 code in production
   - Confirm no sandbox data in production
   - Check no Phase 3 credentials active
   - Validate network isolation

3. ROLLBACK EXECUTION (< 2 minutes)
   - Restore sandbox from CP1 (pre-implementation)
   - Verify production systems untouched
   - Clear all Phase 3 process caches
   - Confirm production operations resume

4. INCIDENT DOCUMENTATION (< 5 minutes)
   - Record exactly what was found in production
   - Timestamp of detection
   - Impact assessment
   - Root cause analysis (immediate assessment)

5. HUMAN GATE NOTIFICATION (< 10 minutes)
   - Incident report to events.db
   - Status: PRODUCTION_CONTAMINATION_INCIDENT
   - Details: What was found, recovery steps taken
   - Decision: Whether Phase 3 can continue

Timeline: 10-15 minutes total
```

---

### Procedure R2: Data Leakage Rollback
**Trigger:** Production data in sandbox (Condition T2)

**Steps:**

```
1. IMMEDIATE ACTIONS (< 1 minute)
   - Pause all Phase 3 code execution
   - Halt any ongoing tests
   - Lock sandbox database (read-only mode)
   - Capture database state for forensics

2. LEAK SOURCE INVESTIGATION (< 10 minutes)
   - Audit database for production row IDs
   - Check data timestamps for origin
   - Review code execution logs
   - Identify which code path caused leak

3. PRODUCTION VERIFICATION (< 5 minutes)
   - Confirm production database unchanged
   - Verify no production data was exfiltrated
   - Check data access logs for unauthorized reads
   - Validate data integrity in production

4. ROLLBACK EXECUTION (< 5 minutes)
   - Restore sandbox from CP1 (pre-implementation)
   - Delete the compromised sandbox database
   - Re-initialize clean sandbox database
   - Verify data origin is synthetic only

5. ROOT CAUSE FIX (30-60 minutes)
   - Identify code bug that caused leak
   - Implement fix
   - Add test case to prevent recurrence
   - Code review before resuming Phase 3

Timeline: 60-90 minutes total
```

---

### Procedure R3: Credential Exposure Rollback
**Trigger:** Production credential exposed (Condition T3)

**Steps:**

```
1. IMMEDIATE ACTIONS (< 1 minute)
   - Pause all Phase 3 code execution
   - Disable exposed credential in production
   - Record all locations credential appeared
   - Isolate Phase 3 branch from network

2. CREDENTIAL ROTATION (< 1 hour)
   - Generate new production credential
   - Update production systems with new credential
   - Verify all production services working
   - Confirm old credential no longer works

3. CODE CLEANUP (< 30 minutes)
   - Remove credential from Phase 3 code
   - Remove credential from git history (git-filter-branch if needed)
   - Remove credential from any logs
   - Verify git history contains no credential

4. SANDBOX RESET (< 5 minutes)
   - Restore sandbox from CP1 (pre-implementation)
   - Clear all Phase 3 environment variables
   - Verify no hardcoded credentials remain
   - Confirm Phase 3 uses sandbox credentials only

5. HUMAN GATE NOTIFICATION (< 10 minutes)
   - Incident report to events.db
   - Status: CREDENTIAL_EXPOSURE_INCIDENT
   - Details: Which credential, where it was found
   - Mitigation: Credential rotated
   - Decision: Whether Phase 3 can continue

Timeline: 90-120 minutes total
```

---

### Procedure R4: Corruption Recovery Rollback
**Trigger:** Database corruption or unrecoverable test failure (Condition T4)

**Steps:**

```
1. ASSESSMENT (< 30 minutes)
   - Analyze corruption type
   - Determine if rollback is sufficient or root cause fix needed
   - Check which checkpoint is closest to clean state
   - Estimate recovery time

2. CHECKPOINT SELECTION (< 5 minutes)
   - Identify best rollback checkpoint (CP1-4)
   - Verify checkpoint integrity
   - Confirm checkpoint has needed data for recovery
   - Get Human Gate approval to proceed with rollback

3. ROLLBACK EXECUTION (< 15 minutes)
   - Stop all Phase 3 processes
   - Restore from selected checkpoint
   - Verify restoration integrity
   - Confirm corruption is gone

4. ROOT CAUSE INVESTIGATION (< 1 hour)
   - Identify what caused corruption
   - Implement fix if code defect
   - Add test to prevent recurrence
   - Code review fix before resuming

5. RESUMPTION DECISION (Human Gate)
   - Report status to Human Gate
   - Request approval to resume Phase 3
   - If approved: resume from cleaned state
   - If denied: prepare for Phase 3 termination

Timeline: 2-3 hours total
```

---

## ROLLBACK VERIFICATION PROCEDURES

### Verification V1: Database Integrity Check
**Method:** SQLite integrity check

**Command:**
```sql
PRAGMA integrity_check;
```

**Expected Result:**
```
ok
```

**Action if Failed:**
- Restore from checkpoint
- Run integrity check again
- If still failing: escalate to Human Gate

---

### Verification V2: Schema Consistency Check
**Method:** Schema structure validation

**Checks:**
```
1. All sb_* tables present
2. All required columns exist
3. All indices present
4. All constraints defined
5. No production tables (non-prefixed)
6. No orphaned views/triggers
```

**Expected Result:** All checks pass

**Action if Failed:**
- Restore from schema checkpoint (CP4)
- Re-run validation
- If still failing: escalate to Human Gate

---

### Verification V3: Data Origin Audit
**Method:** Data lineage verification

**Checks:**
```
1. All records created by test fixtures
2. No production row IDs (IDs not from production range)
3. No timestamps predating Phase 3
4. Row count <= 1,000 (test data limit)
5. No sensitive production data fields
```

**Expected Result:** All data synthetic and test-only

**Action if Failed:**
- Identify contaminated rows
- Delete contaminated rows
- Restore complete dataset from checkpoint if needed
- Run audit again

---

### Verification V4: Code Isolation Check
**Method:** Production reference scan

**Checks:**
```
1. No production API URLs in code
2. No production database connection strings
3. No production credentials in code/logs
4. All API calls point to localhost (mocks)
5. All database references use sb_* prefix
```

**Expected Result:** Zero production references found

**Action if Failed:**
- Remove production references
- Add test to catch regression
- Code review before resuming

---

## EVIDENCE COLLECTION DURING ROLLBACK

### Evidence E1: Incident Recording
**When:** Immediately upon rollback trigger detection

**Record:**
```
Incident Type: PRODUCTION_CONTAMINATION | DATA_LEAKAGE | CREDENTIAL_EXPOSURE | CORRUPTION
Detected At: ISO 8601 timestamp
Trigger Condition: Specific condition (T1/T2/T3/T4)
Details: Exact finding (what was wrong)
Logs: Copy all relevant error/audit logs
```

**Storage:** Events.db (mocka_write_event)

---

### Evidence E2: Rollback Execution Log
**When:** During rollback procedure execution

**Record:**
```
Step: Which recovery step (R1-4, step N)
Action: What was performed
Timestamp: When each step completed
Result: Success / Failure / Partial
Duration: How long this step took
```

**Storage:** Rollback execution log file + events.db

---

### Evidence E3: Verification Results
**When:** After rollback completion

**Record:**
```
Verification Type: V1-4 (which verification)
Result: PASS / FAIL
Details: Any failures found
Timestamp: When verification ran
Approver: Who approved results
```

**Storage:** Verification report + events.db

---

### Evidence E4: Root Cause Analysis
**When:** After assessment of why rollback was needed

**Record:**
```
Root Cause: Specific code/configuration issue
Impact Scope: What was affected
Prevention: How will this be prevented?
Code Fix: If needed, what code changed
Test Case: If needed, what test added
```

**Storage:** Root cause analysis document + code commit

---

## ROLLBACK TESTING

### Test RT1: Restore From Pre-Implementation Checkpoint
**Frequency:** Weekly (during Phase 3)

**Steps:**
```
1. Create backup of current sandbox database
2. Restore from CP1 (pre-implementation)
3. Verify database is clean (no Phase 3 modifications)
4. Verify test suite runs against restored state
5. Confirm rollback procedure works end-to-end
6. Re-restore current state from backup
```

**Expected Result:** Restore procedure completes successfully

**Evidence:** Test execution log recorded

---

### Test RT2: Production Isolation Verification
**Frequency:** Daily (during Phase 3)

**Steps:**
```
1. Scan Phase 3 code for production references
2. Attempt to access production database (should be blocked)
3. Verify production credentials not in Phase 3 code
4. Check network connectivity (sandbox isolated)
5. Confirm rollback from CP1 still works
```

**Expected Result:** All isolation checks pass

**Evidence:** Security scan report recorded

---

## ROLLBACK READINESS CHECKLIST

- [ ] CP1 (Pre-Implementation Snapshot) created and verified
- [ ] CP2 (Weekly Snapshot) procedure defined
- [ ] CP3 (Test Checkpoint) automation set up
- [ ] CP4 (Schema Checkpoint) procedure defined
- [ ] R1 (Emergency Isolation Rollback) procedure documented
- [ ] R2 (Data Leakage Rollback) procedure documented
- [ ] R3 (Credential Exposure Rollback) procedure documented
- [ ] R4 (Corruption Recovery Rollback) procedure documented
- [ ] V1-4 (Verification procedures) implemented
- [ ] E1-4 (Evidence collection) configured
- [ ] RT1-2 (Rollback tests) scheduled
- [ ] Human Gate notified of rollback readiness

---

## ROLLBACK AUTHORITY

**Automatic Rollback:** Conditions T1-T3 (production contamination, data leakage, credential exposure)
- Authority: Automated (no approval needed)
- Response: Immediate

**Manual Rollback:** Condition T4 (corruption recovery)
- Authority: Human Gate decision (after assessment)
- Response: Assessment < 30 min, then rollback decision

**Escalation:** If any rollback fails
- Authority: Human Gate review
- Response: Incident investigation + decision to continue or terminate Phase 3

---

**ROLLBACK MECHANISM READY FOR VERIFICATION**

**All rollback procedures defined. All checkpoints prepared. All evidence collection configured.**

**Phase 3 can proceed with full recovery capability.**

