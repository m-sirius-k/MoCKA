# D-1 Infrastructure Pre-Check: Current State Analysis
## Version 0.1 (Investigation - READ-ONLY)

**Date**: 2026-08-16  
**Format**: INFRASTRUCTURE READINESS ASSESSMENT  
**Purpose**: Determine current state of D-1 infrastructure before Case 4 validation execution

---

## PART 1: FACT - What Currently Exists

### 1.1 Incident Files in Repository

| File | Exists | Status | Details |
|------|--------|--------|---------|
| docs/incidents/INC-20260401-001.md | YES | Manual | Human-authored, marked "Claude Sonnet 4.6 / 2026-04-01" |
| docs/incidents/INC-20260401-002.md | YES | Auto-gen | Auto-generated, marked "自動生成 / 要Claude確認" (unapproved) |

**Evidence**: Both files verified present in /home/user/MoCKA/docs/incidents/

**INC-001 Content**:
- Approval line (L27): "承認：Claude Sonnet 4.6 / 2026-04-01"
- Has "## 再発防止" section with actual content (L21-24)
- Manual incident, no 5W1H sections

**INC-002 Content**:
- Approval line (L21-22): "承認：自動生成 / 要Claude確認"
- Has "## 再発防止" section with "(要分析)" placeholder (L15-16)
- Already has "## 5W1H分析" appended (L23-36)
- Auto-generated incident

---

### 1.2 Lifecycle State Directory

| Component | Status | Location | Details |
|-----------|--------|----------|---------|
| data/inc_lifecycle/ | **MISSING** | /home/user/MoCKA/data/inc_lifecycle | Directory does not exist |
| INC-20260401-001.json | **MISSING** | (would be in inc_lifecycle) | Not found |
| INC-20260401-002.json | **MISSING** | (would be in inc_lifecycle) | Not found |

**Evidence**: `test -d /home/user/MoCKA/data/inc_lifecycle` returns false

**ls -la /home/user/MoCKA/data/** output confirms: No inc_lifecycle directory listed

---

### 1.3 Human Gate Approval Records

| Component | Status | Details |
|-----------|--------|---------|
| mocka_events.db file | EXISTS | Location: /home/user/MoCKA/data/mocka_events.db |
| File size | **EMPTY** | 0 bytes (created but never initialized) |
| human_gate_events table | **MISSING** | Table does not exist in database |
| Approval records for INC-001 | **MISSING** | No submit/approve records |
| Approval records for INC-002 | **MISSING** | No submit/approve/reject records |

**Evidence**: 
- `file /home/user/MoCKA/data/mocka_events.db` returns "empty"
- Python sqlite3 query: "SELECT name FROM sqlite_master WHERE type='table'" returns no tables
- Database is 0 bytes; no schema initialized

---

### 1.4 is_publishable() Implementation

| Component | Status | Details |
|-----------|--------|---------|
| Function exists | YES | tools/mocka_restrictions.py L31-69 |
| FC-1 through FC-9 checks | YES | All 9 Fail-Closed conditions implemented |
| Logic correctness | YES | Code path verified correct |
| Dependencies callable | NO | human_gate_get_state() will fail due to missing table |

**Evidence**: Direct code inspection of mocka_restrictions.py

```python
def is_publishable(inc_id):
    # Lines 40-41: FC-1 check
    if not os.path.exists(path):
        return False, "FC-1 state ファイルが存在しない"
    
    # Lines 61-67: FC-7/FC-8 approval checks
    try:
        approval = human_gate_get_state(request_id)  # Will fail: table missing
    except Exception as e:
        return False, f"FC-9 承認状態の取得に失敗({e})"
    if approval is None:
        return False, f"FC-7 承認軸にレコードが存在しない({request_id})"
    if approval != "APPROVED":
        return False, f"FC-8 承認状態が APPROVED でない({approval})"
```

---

## PART 2: EVIDENCE - Detailed Findings

### 2.1 GPT_RESTRICTIONS.md Generation History

**Current File State**:
- Generated: 2026-07-31 18:07:02 (16 days ago)
- Contains: INC-20260401-001 content only
- Omits: INC-20260401-002

**Analysis**:
```
Timeline:
2026-07-31 18:07:02  → GPT_RESTRICTIONS.md generated (shows INC-001 published)
2026-08-XX (unknown) → is_publishable() added to mocka_restrictions.py
2026-08-16 (today)   → Investigation: infrastructure completely missing
```

**Conclusion**: GPT_RESTRICTIONS.md was generated BEFORE is_publishable() approval gate was implemented. The file does NOT reflect current code behavior.

---

### 2.2 What is_publishable() Will Do TODAY

**Test Scenario**: Run `python tools/mocka_restrictions.py` with current environment

**Predicted Execution Path**:

```
For INC-20260401-001:
  ├─ is_publishable("INC-20260401-001") called
  ├─ Line 40: Check if data/inc_lifecycle/INC-20260401-001.json exists
  ├─ FAILS: FC-1 (file does not exist)
  ├─ Returns: (False, "FC-1 state ファイルが存在しない")
  └─ Result: INC-001 WITHHELD from output

For INC-20260401-002:
  ├─ is_publishable("INC-20260401-002") called
  ├─ FAILS: FC-1 (state file missing)
  └─ Result: INC-002 WITHHELD from output

Output: GPT_RESTRICTIONS.md updated with:
  - Header "# GPT作業禁止事項（自動生成）"
  - Timestamp of current execution
  - "## 常時禁止" static section only
  - NO incident-derived restrictions
  - Footer: "[掲載] 0件 / [非掲載] 2件"
  - Reasons listed:
    "[非掲載] INC-20260401-001: FC-1 state ファイルが存在しない"
    "[非掲載] INC-20260401-002: FC-1 state ファイルが存在しない"
```

**Evidence**: Code logic at lines 80-82, is_publishable() L40-41

---

### 2.3 Database Initialization Behavior

**Current State**: mocka_events.db file exists but is empty (0 bytes)

**What Will Happen When is_publishable() Calls human_gate_get_state()**:

```python
# mocka_restrictions.py L61
approval = human_gate_get_state(request_id)

# Calls phi_os/human_gate.py get_state()
def get_state(request_id: str, conn=None) -> str | None:
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()  # Opens connection to 0-byte mocka_events.db
    try:
        _ensure_table(conn)   # CREATE TABLE IF NOT EXISTS
        row = _latest_event(conn, request_id)
        return row['next_state'] if row else None
    finally:
        if owns_conn:
            conn.close()
```

**What Happens**:
1. _get_conn() opens connection to empty database
2. _ensure_table() runs CREATE TABLE IF NOT EXISTS (L56-67)
3. Table gets initialized (created) in memory for this connection
4. _latest_event() queries the newly-created-but-empty table
5. No rows found → returns None
6. is_publishable() line 64: `if approval is None:` → TRUE
7. Returns (False, "FC-7 承認軸にレコードが存在しない(...)")

**Critical Finding**: The database will be MODIFIED by _ensure_table() during human_gate_get_state() READ operation. However:
- This happens automatically on first call
- The table will be empty (no records)
- is_publishable() will still fail (FC-7)

---

## PART 3: UNKNOWN - Unclear States

### 3.1 Canonical Incident Designation

**Question**: Why are INC-20260401-001 and INC-20260401-002 considered "the" existing incidents?

**Evidence**:
- Both files exist in docs/incidents/
- Previous investigation documents reference them as case study subjects
- But no explicit "canonical" marker in repo

**Assessment**: Based on file presence and naming convention (oldest dates). No explicit authority designation found.

---

### 3.2 Previous Approval Status of INC-001

**Observation**: INC-001 has "Claude Sonnet 4.6 / 2026-04-01" in approval field

**Question**: What does this approval marker mean?
- Is it a formal approval?
- Is it just a comment?
- Does it imply prior human_gate record?

**Evidence**: No human_gate_events records exist, so this is not a formal Human Gate approval

**Assessment**: UNKNOWN - the approval field is human-written metadata, not machine-verified status

---

### 3.3 INC-002 5W1H Section Origin

**Observation**: INC-002 already has "## 5W1H分析" section (L23-36)

**Question**: Was this added by mocka_5w1h.py? Or manually added?

**Evidence**: 
- File exists with content
- No git history available in this session to verify timing
- Pattern matches mocka_5w1h.py output format (5W pattern)

**Assessment**: UNKNOWN - likely auto-generated by 5w1h.py, but timing unclear

---

## PART 4: FAILURE MODE VERIFICATION

### 4.1 Failure Scenario: Running is_publishable() Today

**Scenario**: Execute `python tools/mocka_restrictions.py`

**Predicted Result**:
```
Failures for INC-20260401-001:
  ├─ FC-1 (no state file)
  ├─ Never reaches FC-7/FC-8 (fails early)
  └─ Status: WITHHELD

Failures for INC-20260401-002:
  ├─ FC-1 (no state file)
  ├─ Never reaches FC-7/FC-8
  └─ Status: WITHHELD

Database Side Effect:
  ├─ human_gate_events table CREATED (via _ensure_table)
  ├─ Table structure initialized
  ├─ Still EMPTY (no records)
  └─ DB file size changes from 0 bytes to non-zero
```

**Why FC-1 Fails First**:
- is_publishable() checks in sequence (L40-56 for progression axis)
- Approval axis checks come after (L59-67)
- FC-1 check at L40-41 fails immediately
- Function returns without checking FC-7/FC-8

---

## PART 5: INFRASTRUCTURE READINESS MATRIX

### Complete Status Table

| Requirement | Component | Current Status | Evidence | Blocker Type |
|-------------|-----------|-----------------|----------|--------------|
| **Directory Structure** | data/inc_lifecycle/ | MISSING | Directory not found in filesystem | INFRASTRUCTURE |
| **State File: INC-001** | INC-20260401-001.json | MISSING | Not in (nonexistent) inc_lifecycle dir | INFRASTRUCTURE |
| **State File: INC-002** | INC-20260401-002.json | MISSING | Not in (nonexistent) inc_lifecycle dir | INFRASTRUCTURE |
| **State File Schema** | v0.1 definition | DEFINED | Specified in D1_INFRASTRUCTURE_GAPS document | (Ready when files created) |
| **Approval Table** | human_gate_events | MISSING | Table not in mocka_events.db | INFRASTRUCTURE |
| **Approval Records: INC-001** | submit + approve | MISSING | No records in (missing) table | HUMAN AUTHORITY |
| **Approval Records: INC-002** | submit (± approve) | MISSING | No records in (missing) table | HUMAN AUTHORITY |
| **is_publishable() Function** | FC-1 to FC-9 logic | IMPLEMENTED | Code present, logic verified | (Ready) |
| **Database File** | mocka_events.db | EXISTS (empty) | File present but 0 bytes | (Auto-initialized on first call) |

---

## PART 6: BLOCKER CLASSIFICATION

### Infrastructure Gaps vs Human Authority Gaps

**Infrastructure Gaps** (Technical, must be created before testing):
1. data/inc_lifecycle/ directory
2. INC-*.json state files (JSON format, schema)
3. human_gate_events table (SQLite initialization)

**Human Authority Gaps** (Approval decisions, must be made by authorized person):
1. Approval records for INC-20260401-001 (submit + approve events)
2. Approval records for INC-20260401-002 (submit + reject/approve/pend events)

**Critical Distinction**:
- Infrastructure can be created procedurally (no human judgment)
- Approval records CANNOT be created without Human Gate decision
- is_publishable() will still FAIL even if infrastructure exists, if approvals are missing

---

## PART 7: CASE 4 READINESS ASSESSMENT

### R01判断 - Infrastructure Readiness Status

**Overall Status**: **C. INFRASTRUCTURE BLOCKED**

### Detailed Breakdown

| Axis | Status | Reason |
|------|--------|--------|
| **Progression Axis (進行軸)** | BLOCKED | state files don't exist (FC-1 will reject all) |
| **Approval Axis (承認軸)** | BLOCKED | no human_gate_events records exist (FC-7/FC-8 will reject) |
| **Code Implementation** | READY | is_publishable() logic correct and complete |
| **Database Initialization** | AUTO | will initialize on first call, but remains empty |
| **Case 4 Executable** | NO | Cannot proceed until FC-1/FC-7/FC-8 conditions satisfied |

---

## PART 8: 推奨アクション - Recommended Actions

### Immediate Pre-Requisites for Case 4 Validation

**Phase 1: Infrastructure Setup (Before Human Authority Required)**
- [ ] Create data/inc_lifecycle/ directory
- [ ] Create INC-20260401-001.json with schema_version="0.1", state="ANALYZED"
- [ ] Create INC-20260401-002.json with schema_version="0.1", state="ANALYZED"
- [ ] Verify mocka_events.db gets initialized (happens on first is_publishable() call)

**Phase 2: Human Authority (Requires R01 Decision)**
- [ ] Create Human Gate approval records for INC-20260401-001 (submit + approve)
- [ ] Create Human Gate approval records for INC-20260401-002 (submit + approve/reject)
- [ ] Explicit authorization: "INC-001 should be published" (is_publishable() must return True)
- [ ] Explicit authorization: "INC-002 should be [published/withheld]" (explicit approval state needed)

**Phase 3: Verification**
- [ ] Run is_publishable() checks for both incidents
- [ ] Verify return values: INC-001 → (True, "APPROVED"), INC-002 → depends on R01 decision
- [ ] Confirm mocka_restrictions.py can update GPT_RESTRICTIONS.md with approved content

**Phase 4: Case 4 Validation**
- [ ] Execute Case 4 test procedure (CASE_4_REAL_DATA_VALIDATION_PROCEDURE_v0.1.md)
- [ ] Verify D-2 order (restrictions before 5w1h)
- [ ] Verify D-3 extraction ("## 再発防止" section boundaries)

---

## PART 9: SUMMARY FOR R01 REVIEW

### Current Infrastructure State: COMPLETELY MISSING

**What Exists**:
- Code: is_publishable() function ✅
- Code: D-2/D-3 logic corrections ✅
- Incident files: INC-001 and INC-002 ✅
- Database file: mocka_events.db (empty) ⚠️

**What Does NOT Exist**:
- Directory: data/inc_lifecycle/ ❌
- Files: INC-*.json state files ❌
- Table: human_gate_events ❌
- Records: Approval events ❌

### Why GPT_RESTRICTIONS.md Shows INC-001

**Timeline Analysis**:
1. 2026-07-31 18:07:02 - GPT_RESTRICTIONS.md created with INC-001 content
2. 2026-08-XX (later) - is_publishable() approval gates added to mocka_restrictions.py
3. 2026-08-16 (today) - Infrastructure does not exist

**Conclusion**: File was generated with OLDER version of code (without approval gates). Current code would REJECT all incidents.

### Two-Part Approval Requirement

**Part A: Infrastructure Setup (Technical)**
- Procedure: Defined in D1_INFRASTRUCTURE_GAPS_EXACT_SPECIFICATION_v0.1.md
- Effort: ~15-30 minutes
- Authority: Technical, no human judgment required
- Blocker: None (when approved)

**Part B: Human Authority Approval (Policy)**
- Question: Should INC-20260401-001 be published? (Currently has manual approval marker)
- Question: Should INC-20260401-002 be published? (Currently marked unapproved)
- Authority: Required from R01 (Human Gate authority)
- Blocker: Cannot proceed without explicit decision

---

## CONCLUSION

**D-1 Infrastructure Status**: C. INFRASTRUCTURE BLOCKED

**Readiness for Case 4**: NOT READY

**Prerequisites**:
1. Create directory + state files (technical, no decision required)
2. Obtain Human Authority approval decision (R01 must confirm each incident's publication status)
3. Create human_gate_events approval records (after R01 decision)
4. Run Case 4 validation procedure

**Estimated Time to Ready**:
- Infrastructure setup: 15-30 minutes
- Human Authority decision: Pending R01
- Approval record creation: 5-10 minutes
- Case 4 validation: 15-20 minutes
- **Total**: ~1 hour (excluding R01 decision time)

---

