# Case 4 Real Data Validation Procedure: Single-Cycle Correctness Verification
## Version 0.1 (Investigation - READ-ONLY)

**Date**: 2026-08-16
**Format**: TEST PROCEDURE SPECIFICATION
**Purpose**: Define how to verify D-2 and D-3 corrections produce correct Case 4 output (restrictions before 5W1H, no content corruption)

---

## CONTEXT: What Case 4 Means

Per INC_PIPELINE_DEFECT_DEPENDENCY_v0.1.md section 4.2, Case 4 is the target state:

| D-2 Status | D-3 Status | Meaning |
|-----------|-----------|---------|
| 是正済 | 是正済 | Both generation order AND extraction range are fixed |

**Expected Output Behavior for Case 4**:
- Single pipeline execution generates incident with correct "## 再発防止" content
- No one-cycle delay (unlike Case 3)
- No placeholder "(要分析)" (unlike Cases 1 and 2)
- Content flows from INC creation → restrictions output → 5W1H appends, in order

---

## PART 1: Test Data Specifications

### Event Data Format

**Location**: data/events.csv (Windows environment) or equivalent
**Format**: CSV with UTF-8 encoding, DictReader compatible

### Event Records Triggering Case 4

Create test events that will:
1. Generate a new incident via risk_engine.py auto-generation logic
2. Be marked CRITICAL or HIGH risk (to trigger incident auto-generation)
3. Match a pattern requiring "## 再発防止" extraction

#### Test Event 1: CRITICAL Risk Event (New Incident)

| Column | Value | Purpose |
|--------|-------|---------|
| timestamp | 2026-08-16T14:00:00Z | Recent timestamp |
| event_type | SECURITY | Classification |
| severity | CRITICAL | Triggers auto-generation |
| pattern_match | P001_CREDENTIALS | Matches known incident pattern |
| description | Hardcoded password found in source code | Specific, actionable |
| related_event_id | (empty) | Will be populated by risk_engine |
| affected_file | src/config.py | Concrete reference |

**CSV Row**:
```
timestamp,event_type,severity,pattern_match,description,related_event_id,affected_file
2026-08-16T14:00:00Z,SECURITY,CRITICAL,P001_CREDENTIALS,Hardcoded password found in source code,,src/config.py
```

**Expected Behavior**:
1. risk_engine.py detect severity=CRITICAL
2. Auto-generate incident (e.g., INC-20260816-001)
3. Set auto-generated "## 再発防止" section (placeholder: "(要分析)")
4. Create INC lifecycle state file (DETECTED state)
5. Write related_event_id back to events.csv

#### Test Event 2: HIGH Risk Event (Another New Incident)

| Column | Value | Purpose |
|--------|-------|---------|
| timestamp | 2026-08-16T14:15:00Z | Slightly later |
| event_type | ACCESS_CONTROL | Classification |
| severity | HIGH | Also triggers auto-generation |
| pattern_match | P002_UNAUTHORIZED_ACCESS | Another pattern |
| description | Database access without authentication checks | Different incident |
| related_event_id | (empty) | Will be populated |
| affected_file | api/auth.py | Different file |

**CSV Row**:
```
timestamp,event_type,severity,pattern_match,description,related_event_id,affected_file
2026-08-16T15:15:00Z,ACCESS_CONTROL,HIGH,P002_UNAUTHORIZED_ACCESS,Database access without authentication checks,,api/auth.py
```

**Expected Behavior**:
1. risk_engine.py detect severity=HIGH
2. Auto-generate second incident (e.g., INC-20260816-002)
3. Create incident with placeholder "## 再発防止"
4. Create lifecycle state file
5. Write related_event_id to events.csv

#### Test Event 3: MEDIUM Risk Event (Should NOT Generate Incident)

| Column | Value | Purpose |
|--------|-------|---------|
| timestamp | 2026-08-16T14:30:00Z | For contrast |
| event_type | CODE_QUALITY | Classification |
| severity | MEDIUM | Below threshold |
| pattern_match | (none) | Not CRITICAL/HIGH |
| description | Missing error handling | Lower severity |
| related_event_id | (empty) | Should remain empty |

**CSV Row**:
```
timestamp,event_type,severity,pattern_match,description,related_event_id,affected_file
2026-08-16T14:30:00Z,CODE_QUALITY,MEDIUM,,Missing error handling,,utils.py
```

**Expected Behavior**:
1. risk_engine.py ignores (not CRITICAL/HIGH)
2. incidents_generated list not updated
3. restrictions.py and mocka_5w1h.py NOT executed (no `if incidents_generated:` block entry)

---

## PART 2: Pre-Test Setup

### Prerequisite: D-1 Infrastructure

Before testing Case 4, MUST have completed Task #10 setup:

- [x] data/inc_lifecycle/ directory exists
- [x] INC-20260401-001.json and INC-20260401-002.json exist
- [x] human_gate_events table created and populated with at least 1 APPROVED record
- [x] is_publishable() succeeds for at least 1 incident

**Verification**:
```bash
# Check infrastructure
ls -la C:\Users\sirok\MoCKA\data\inc_lifecycle\
sqlite3 C:\Users\sirok\MoCKA\data\mocka_events.db \
  "SELECT request_id, next_state FROM human_gate_events ORDER BY timestamp DESC"
```

### Step 1: Prepare Clean events.csv

Create a fresh events.csv with ONLY test data (no legacy production data):

**File**: data/events.csv
**Encoding**: UTF-8 (not UTF-8 BOM)

```csv
timestamp,event_type,severity,pattern_match,description,related_event_id,affected_file
2026-08-16T14:00:00Z,SECURITY,CRITICAL,P001_CREDENTIALS,Hardcoded password found in source code,,src/config.py
2026-08-16T14:15:00Z,ACCESS_CONTROL,HIGH,P002_UNAUTHORIZED_ACCESS,Database access without authentication checks,,api/auth.py
2026-08-16T14:30:00Z,CODE_QUALITY,MEDIUM,,Missing error handling,,utils.py
```

### Step 2: Pre-Approve New Test Incidents

**IMPORTANT**: Before running risk_engine.py, we must pre-approve the test incidents (even though they don't exist yet) OR accept that they will be generated but withheld by is_publishable().

**Option A**: Create approval records BEFORE incident generation (forward approval)
- Requires knowing incident IDs in advance (difficult without running risk_engine first)
- Not practical

**Option B**: Generate incidents first, then manually approve (post-approval)
- Run risk_engine.py to create incidents and get their IDs
- Create corresponding INC-*.json and human_gate_events records
- Proceed to restrictions.py

**Recommended**: Use Option B (post-approval)

---

## PART 3: Execution Steps

### Execution Step 1: Run risk_engine.py

**Command**:
```bash
cd C:\Users\sirok\MoCKA
python tools/mocka_risk_engine.py
```

**Expected Output**:
```
[DETECTED] INC-20260816-001
[DETECTED] INC-20260816-002
[GPT_RESTRICTIONS] 自動更新完了
[5W1H] 自動分析完了
```

**Verification Checkpoints**:

| Checkpoint | Check | Expected | Status |
|-----------|-------|----------|--------|
| 1a | New incidents generated | docs/incidents/INC-20260816-001.md exists | PASS if file exists |
| 1b | New incidents generated | docs/incidents/INC-20260816-002.md exists | PASS if file exists |
| 1c | CSV updated | events.csv related_event_id populated | PASS if field contains incident IDs |
| 1d | Execution blocked at restrictions | GPT_RESTRICTIONS.md unchanged (no approval yet) | PASS if file not updated (or warnings present) |
| 1e | Execution blocked at 5W1H | INC files have NO "## 5W1H分析" section yet | PASS if section absent |

**Why 1d and 1e happen**:
- INC-20260816-001.json doesn't exist yet → is_publishable() returns FC-1
- INC-20260816-002.json doesn't exist yet → is_publishable() returns FC-1
- restrictions.py withholds both incidents from GPT_RESTRICTIONS.md
- mocka_5w1h.py never runs (no incidents passed approval gate)

### Execution Step 2: Create Incident State Files

Once risk_engine.py completes, read the generated incident files to extract incident_id and content:

```bash
cat docs/incidents/INC-20260816-001.md
```

Extract the auto-generated "## 再発防止" section content.

**Create state files**:

#### data/inc_lifecycle/INC-20260816-001.json
```json
{
  "schema_version": "0.1",
  "incident_id": "INC-20260816-001",
  "state": "ANALYZED",
  "created_at": "2026-08-16T14:00:00Z",
  "updated_at": "2026-08-16T14:00:00Z",
  "transitions": [
    {"from": null, "to": "DETECTED", "timestamp": "2026-08-16T14:00:00Z", "reason": "Auto-generated from event CRITICAL risk"},
    {"from": "DETECTED", "to": "ANALYZED", "timestamp": "2026-08-16T14:00:00Z", "reason": "Pattern analysis complete"}
  ]
}
```

#### data/inc_lifecycle/INC-20260816-002.json
```json
{
  "schema_version": "0.1",
  "incident_id": "INC-20260816-002",
  "state": "ANALYZED",
  "created_at": "2026-08-16T14:15:00Z",
  "updated_at": "2026-08-16T14:15:00Z",
  "transitions": [
    {"from": null, "to": "DETECTED", "timestamp": "2026-08-16T14:15:00Z", "reason": "Auto-generated from event HIGH risk"},
    {"from": "DETECTED", "to": "ANALYZED", "timestamp": "2026-08-16T14:15:00Z", "reason": "Pattern analysis complete"}
  ]
}
```

### Execution Step 3: Create Approval Records

Insert Human Gate approval records for the new incidents:

```python
import sqlite3

db_path = r"C:\Users\sirok\MoCKA\data\mocka_events.db"
conn = sqlite3.connect(db_path)

# INC-20260816-001 approval
conn.execute(
    '''INSERT INTO human_gate_events
       (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
    ('HG20260816_000000001ccc', '2026-08-16T14:05:00Z', 'HUMAN_GATE_EVENT', 'submit',
     'INC-LIFECYCLE-INC-20260816-001', '{"reason":"Test Case 4 validation"}', None, 'PENDING')
)

conn.execute(
    '''INSERT INTO human_gate_events
       (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
    ('HG20260816_000000001ddd', '2026-08-16T14:10:00Z', 'HUMAN_GATE_EVENT', 'approve',
     'INC-LIFECYCLE-INC-20260816-001', '{"approved_by":"validation"}', 'PENDING', 'APPROVED')
)

# INC-20260816-002 approval
conn.execute(
    '''INSERT INTO human_gate_events
       (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
    ('HG20260816_000000002ccc', '2026-08-16T14:20:00Z', 'HUMAN_GATE_EVENT', 'submit',
     'INC-LIFECYCLE-INC-20260816-002', '{"reason":"Test Case 4 validation"}', None, 'PENDING')
)

conn.execute(
    '''INSERT INTO human_gate_events
       (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
    ('HG20260816_000000002ddd', '2026-08-16T14:25:00Z', 'HUMAN_GATE_EVENT', 'approve',
     'INC-LIFECYCLE-INC-20260816-002', '{"approved_by":"validation"}', 'PENDING', 'APPROVED')
)

conn.commit()
conn.close()

print("Approval records inserted for INC-20260816-001 and INC-20260816-002")
```

### Execution Step 4: Run mocka_restrictions.py

**Command**:
```bash
python tools/mocka_restrictions.py
```

**Expected Output**:
```
# GPT作業禁止事項（自動生成）
生成日時：2026-08-16 HH:MM:SS
ソース：docs/incidents/INC-*.md

---

## 常時禁止（全タスク共通）
... (existing static section) ...

### INC-20260401-001 より
... (existing approved incident content) ...

### INC-20260816-001 より
Hardcoded password found...
(要分析)

### INC-20260816-002 より
Database access without authentication...
(要分析)
```

**Verification Checkpoints**:

| Checkpoint | Check | Expected | Status |
|-----------|-------|----------|--------|
| 4a | Existing approved incidents preserved | INC-001 content appears | PASS if present |
| 4b | New approved incidents included | INC-20260816-001 content appears | PASS if present |
| 4c | New approved incidents included | INC-20260816-002 content appears | PASS if present |
| 4d | D-3 extraction correct | "## 再発防止" section extracted (not generic "## ") | PASS if correct section |
| 4e | Placeholder preserved | "(要分析)" placeholder from auto-gen preserved | PASS if present |
| 4f | Format correct | Each restriction prefixed with "### INC-ID より" | PASS if format matches |

### Execution Step 5: Run mocka_5w1h.py

**Command**:
```bash
python tools/mocka_5w1h.py
```

**Expected Behavior**:
- Reads events.csv
- Finds related_event_id for INC-20260816-001 and INC-20260816-002
- Appends "## 5W1H分析" section to each INC file
- Does NOT modify "## 再発防止" section
- Does NOT modify GPT_RESTRICTIONS.md (5W1H output is to incident files, not restrictions)

**Verification Checkpoints**:

| Checkpoint | Check | Expected | Status |
|-----------|-------|----------|--------|
| 5a | 5W1H sections added | docs/incidents/INC-20260816-001.md has "## 5W1H分析" | PASS if present |
| 5b | 5W1H sections added | docs/incidents/INC-20260816-002.md has "## 5W1H分析" | PASS if present |
| 5c | No corruption | "## 再発防止" section unchanged | PASS if content identical to Step 4 |
| 5d | GPT_RESTRICTIONS unchanged | docs/governance/GPT_RESTRICTIONS.md unchanged | PASS if no new lines added |

---

## PART 4: D-2 and D-3 Correctness Verification

### D-2 Verification: Order Guarantee (restrictions before 5W1H)

**Test**: Did restrictions.py run BEFORE mocka_5w1h.py?

**Evidence**: GPT_RESTRICTIONS.md must contain incident content BEFORE 5W1H runs.

**How to Verify**:
1. During Step 4 (mocka_restrictions.py), GPT_RESTRICTIONS.md contains:
   - INC-20260816-001 with "## 再発防止" content
   - INC-20260816-002 with "## 再発防止" content
2. During Step 5 (mocka_5w1h.py), GPT_RESTRICTIONS.md is NOT updated
3. Time ordering: Timestamp in GPT_RESTRICTIONS.md from Step 4 is earlier than timestamps in INC files (from Step 5)

**Code Path Verification**:
- risk_engine.py L202-208: Conditional block checks `if incidents_generated:`
- Line 203: `os.system(f"python {RESTRICTIONS}")` ← restrictions.py called first
- Line 207: `os.system(f"python {w5h1_script}")` ← 5w1h.py called second
- os.system() is BLOCKING; subprocess must complete before next line executes

**PASS Criteria**:
```
Time(restrictions starts) < Time(5w1h starts)
 AND
restrictions output visible in GPT_RESTRICTIONS.md
 AND
GPT_RESTRICTIONS.md contains only restrictions (no 5W1H sections)
```

### D-3 Verification: Extraction Range Sufficiency

**Test**: Does "## 再発防止" section extract ONLY that section, not generic?

**Code Path**:
- mocka_restrictions.py L87-89:
  ```python
  if "## 再発防止" in content:
      section = content.split("## 再発防止")[1]
      section = section.split("##")[0].strip()
      restrictions.append(f"### {inc_id} より\n{section}")
  ```

**Logic**:
1. Split on "## 再発防止" → gets everything AFTER that header
2. Split result on "##" → gets content until NEXT section header
3. Result: Content between "## 再発防止" and next "##"

**PASS Criteria**:
1. "## 再発防止" content appears in GPT_RESTRICTIONS.md
2. Content ends cleanly at next "##" marker (no over-extraction)
3. Previous sections (e.g., "## 検知理由") NOT included
4. Following sections (e.g., "## 5W1H分析") NOT included

**Example Extraction**:

INC-20260816-001.md contains:
```markdown
## 検知理由
Credentials detected in source via P001 pattern

## 再発防止
- 環境変数に credentials 移行
- .gitignore に secrets pattern 追加
- コード審査で secrets scan 必須化

## 5W1H分析
[This section was added by 5w1h.py]
```

Expected extraction in GPT_RESTRICTIONS.md:
```markdown
### INC-20260816-001 より
- 環境変数に credentials 移行
- .gitignore に secrets pattern 追加
- コード審査で secrets scan 必須化
```

**NOT extracted**:
- "## 検知理由" content (comes before)
- "## 5W1H分析" content (comes after)

---

## PART 5: Case 4 Success Matrix

### Complete Verification Table

| Phase | Checkpoint | Pass Criterion | Evidence |
|-------|-----------|----------------|----------|
| 1 | risk_engine runs | Events CSV updated | related_event_id populated for each event |
| 1 | Incidents created | New INC files exist | docs/incidents/INC-20260816-001.md exists |
| 2 | State files created | ANALYZED state stored | data/inc_lifecycle/INC-20260816-001.json readable |
| 3 | Approvals recorded | Human Gate entries exist | sqlite3 returns APPROVED for request_id |
| 4 | restrictions runs | Approved incidents published | GPT_RESTRICTIONS.md contains incident content |
| 4 | D-3 extraction correct | "## 再発防止" extracted | Section content in output, cleanly delimited |
| 4 | Content not corrupted | Previous sections absent | "## 検知理由" NOT in output |
| 5 | 5w1h runs | Sections appended | "## 5W1H分析" added to INC files |
| 5 | No corruption of prior work | "## 再発防止" unchanged | Content matches Step 4 snapshot |
| 5 | GPT_RESTRICTIONS stable | Restrictions file not modified by 5w1h | Timestamps and content from Step 4 preserved |

### Success Definition

**Case 4 VALIDATED** if ALL checkpoints PASS:

```
- risks_engine creates incident with AUTO-generated "## 再発防止"
- restrictions_engine extracts CORRECT "## 再発防止" section
- restrictions content published to GPT_RESTRICTIONS.md IN SINGLE EXECUTION CYCLE
- mocka_5w1h appends "## 5W1H分析" WITHOUT corrupting prior work
- ENTIRE FLOW COMPLETES IN ONE PASS (no delayed cycles)
```

---

## PART 6: Expected vs Actual Test Results

### Expected (Case 4 Target State)

| Stage | Expected Output |
|-------|-----------------|
| After risk_engine | incidents_generated = [INC-20260816-001, INC-20260816-002]; events.csv has related_event_id |
| After restrictions | GPT_RESTRICTIONS.md contains INC-001/002/20260816-001/002 content with "## 再発防止" sections extracted |
| After 5w1h | INC-20260816-001.md has new "## 5W1H分析" section appended; "## 再発防止" unchanged |

### Potential Failure Cases

#### Failure 1: Approvals Missing After Step 2
```
Symptom: GPT_RESTRICTIONS.md doesn't update after Step 4
Cause: State files created but Human Gate approval records missing
Fix: Ensure Step 3 (approval record insertion) completed
```

#### Failure 2: D-3 Extraction Over-reads
```
Symptom: GPT_RESTRICTIONS.md contains "## 検知理由" AND "## 再発防止" AND "## 5W1H分析"
Cause: Extraction logic changed (unlikely; verify L87-89 unchanged)
Fix: Confirm mocka_restrictions.py lines 87-89 are:
  section = content.split("## 再発防止")[1]
  section = section.split("##")[0].strip()
```

#### Failure 3: D-2 Order Violated (5w1h runs before restrictions)
```
Symptom: INC files have "## 5W1H分析" but GPT_RESTRICTIONS.md is empty/old
Cause: Line 203 and 207 order reversed (impossible in current code)
Fix: Check mocka_risk_engine.py L202-208 sequence
```

#### Failure 4: One-Cycle Delay (Case 3 instead of Case 4)
```
Symptom: Incident created but "## 再発防止" not in restrictions output this cycle
Cause: INC not approved yet (Case 3 situation)
Fix: Verify all approval records inserted before Step 4
```

---

## PART 7: Rollback and Cleanup

### After Case 4 Validation Complete

**If validation succeeds**: Keep test data (or archive for regression testing)

**If validation fails**: Rollback to pre-test state:

```bash
# Remove test incidents
rm docs/incidents/INC-20260816-*.md

# Remove test state files
rm data/inc_lifecycle/INC-20260816-*.json

# Remove test approval records
sqlite3 data/mocka_events.db \
  "DELETE FROM human_gate_events WHERE request_id LIKE 'INC-LIFECYCLE-INC-20260816-%'"

# Restore events.csv from backup (or create fresh)
# restore events.csv

# Restore GPT_RESTRICTIONS.md from git
git checkout docs/governance/GPT_RESTRICTIONS.md
```

---

## SUMMARY FOR R01 REVIEW

### Case 4 Readiness

**Current State**: Code structure correct (D-2/D-3 implemented), infrastructure incomplete (D-1 gaps)

**To Achieve Case 4 Validation**:

1. Complete Task #10 (D-1 infrastructure setup)
2. Execute this procedure with test data
3. Verify all 5 phases pass
4. Confirm single-execution-cycle behavior

### R01 Decision Points

**Before approving Case 4 validation**:
- [ ] Approve Task #10 infrastructure setup scope
- [ ] Approve use of test event data (events.csv injection)
- [ ] Approve retroactive approval of test incidents (post-generation approval)
- [ ] Confirm production data isolation (test data cleanup)

### Estimated Execution Time

- Task #10 setup: 15-30 minutes (manual file creation + SQL inserts)
- Case 4 validation: 10-20 minutes (execution + verification)
- Total: ~1 hour for complete D-1/D-2/D-3 verification

