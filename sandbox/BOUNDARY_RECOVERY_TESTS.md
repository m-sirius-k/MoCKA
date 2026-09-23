# PHASE 5: BOUNDARY CONDITION & RECOVERY TESTS

## Design Specification (Testing Only - Not Yet Executed)

### Boundary Test Suite

#### B1: counter=001 (First ID)
**Scenario:** Fresh counter for new date
**Expected:** DC_YYYYMMDD_001 generated successfully
**Verification:**
- Counter increments from 0 to 1
- ID format correct
- No exceptions

#### B2: counter=998 (Near Limit)
**Scenario:** Approaching daily limit
**Expected:** DC_YYYYMMDD_998 generated successfully
**Verification:**
- Counter at 998
- Next call can increment to 999

#### B3: counter=999 (At Limit)
**Scenario:** At maximum valid NNN value
**Expected:** DC_YYYYMMDD_999 generated successfully
**Verification:**
- Counter reaches 999
- ID format correct (exactly 3 digits)
- Counter stays at 999 after generation

#### B4: counter=1000 Request (Exceed Limit)
**Scenario:** Counter at 999, request next ID
**Expected:** LimitExceededException raised
**Verification:**
- Exception type correct
- Counter remains at 999 (rollback verified)
- No ID returned
- No ledger write

#### B5: Repeated 1000 Requests (Idempotence)
**Scenario:** Multiple requests while at limit
**Expected:** All requests raise exception consistently
**Verification:**
- 3+ repeated attempts all raise exception
- Counter unchanged
- No state corruption

#### B6: Daily Rollover
**Scenario:** Date changes from YYYYMMDD to YYYYMMDD+1
**Expected:** New counter row created, counter resets to 001
**Verification:**
- Old date row preserved in DB
- New date row has counter=1 after first call
- IDs for new date start from 001

#### B7: Concurrent at Limit
**Scenario:** Multiple processes/threads accessing when counter=999
**Expected:** Only one succeeds generating 999; others get exception
**Verification:**
- Exactly one process gets DC_YYYYMMDD_999
- All others get LimitExceededException
- Counter remains at 999
- Zero collisions

#### B8: Concurrent Daily Boundary
**Scenario:** Processes in different dates accessing simultaneously
**Expected:** Atomic date separation, counter rows independent
**Verification:**
- Process A: date=20260921, gets DC_20260921_NNN
- Process B: date=20260922, gets DC_20260922_NNN
- Separate counter rows in DB
- No cross-date interference

### Recovery Test Suite

#### R1: Process Termination During Transaction
**Scenario:** SIGKILL during BEGIN IMMEDIATE → UPDATE
**Environment:** Windows (SIGTERM -> process kill)
**Expected:** DB lock released, transaction rolled back
**Verification:**
- DB not corrupted
- Counter unchanged (partial increment lost)
- Next process can connect and increment

#### R2: Restart After Shutdown
**Scenario:** DB connection open, then close/reopen
**Expected:** Counter persists, can continue incrementing
**Verification:**
- Counter value preserved
- Next ID continues from last value
- No skipped numbers

#### R3: DB Corruption Simulation (if possible)
**Scenario:** Manually corrupt counter row
**Environment:** Corrupt one byte in decision_id_counters row
**Expected:** Fail gracefully (not silently)
**Verification:**
- Error raised (SQLite returns corruption error)
- No silent data loss
- Not infinite loop

#### R4: Write Failure Simulation (if possible)
**Scenario:** Filesystem writes fail (disk full, permissions)
**Environment:** Attempt write to read-only location
**Expected:** Exception propagates to caller
**Verification:**
- SQLite error raised
- Caller receives exception
- No partial state

### Measurement Points

For each boundary test, record:
1. **Counter value before/after**
2. **Exception type if raised**
3. **Lock wait time** (if instrumented)
4. **Transaction duration**
5. **DB state consistency**

### Pass/Fail Criteria

**PASS:**
- All boundary tests execute without error
- All recovery tests leave DB in consistent state
- All counter values as expected
- Zero collisions under concurrency
- All exceptions raised when expected

**FAIL:**
- Any unexpected exception
- Counter inconsistency
- DB corruption
- Collisions detected
- Silent failures (ID generated when should fail)

### Scope Notes
- Tests execute on SANDBOX DB ONLY
- No production DB access
- Fresh sandbox DB for each test run
- Instrumentation added but not required
- Recovery tests may be ENVIRONMENT-LIMITED on Windows

## Test Matrix Summary

| Test ID | Name | Type | Status |
|---------|------|------|--------|
| B1 | First ID (counter=001) | Boundary | Designed |
| B2 | Near limit (counter=998) | Boundary | Designed |
| B3 | At limit (counter=999) | Boundary | Designed |
| B4 | Exceed limit (counter→1000) | Boundary | Designed |
| B5 | Idempotent limit | Boundary | Designed |
| B6 | Daily rollover | Boundary | Designed |
| B7 | Concurrent at limit | Boundary | Designed |
| B8 | Concurrent daily boundary | Boundary | Designed |
| R1 | Process termination | Recovery | Designed (env-limited) |
| R2 | Restart persistence | Recovery | Designed |
| R3 | DB corruption | Recovery | Designed (env-limited) |
| R4 | Write failure | Recovery | Designed (env-limited) |

## Implementation Notes
- Start with B1-B5 (basic boundary)
- Progress to B6-B8 (rollover & concurrency)
- Recovery tests (R1-R4) may be skipped if environment doesn't support
- Each test isolation: fresh counter value before test
- Document any ENVIRONMENT-LIMITED tests
