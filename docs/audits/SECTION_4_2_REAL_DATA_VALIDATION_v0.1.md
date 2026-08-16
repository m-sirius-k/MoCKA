# Section 4.2 Real Data Validation: Case 4 Status Analysis
## Version 0.1 (Investigation - READ-ONLY)

**Date**: 2026-08-16  
**Analysis Format**: FACT → EVIDENCE → UNKNOWN → STATUS

---

## FACT: Current Pipeline State (Observed Data)

### Incident Population
- **INC-20260401-001**: Manual incident from 2026-04-01
  - Status: "Claude Sonnet 4.6 / 2026-04-01" (appears to be APPROVED)
  - Sections: 発生内容 / 原因分析 / 対処 / **再発防止** / 憲章違反条項 / 承認
  - Currently PUBLISHED in GPT_RESTRICTIONS.md (line 21-26)

- **INC-20260401-002**: Auto-generated incident, same date
  - Status: "自動生成 / 要Claude確認" (UNAPPROVED)
  - Sections: 発生内容 / 検知理由 / 再発防止 / 憲章違反条項 / 承認 / **5W1H分析** / パターン分類
  - Currently NOT PUBLISHED in GPT_RESTRICTIONS.md (correctly withheld)

### GPT_RESTRICTIONS.md Output (Generated 2026-07-31 18:07:02)
- Shows only INC-001 "再発防止" section content
- INC-002 is absent (good - it's unapproved)
- Manual static section preserved

---

## EVIDENCE: D-2 and D-3 Correction Status

### D-2 (Generation Order): ✅ CORRECTED IN CODE

**Code Location**: `tools/mocka_risk_engine.py` lines 202-208

```python
if incidents_generated:
    os.system(f"python {RESTRICTIONS}")    # D-2: restrictions.py
    print("[GPT_RESTRICTIONS] 自動更新完了")
    w5h1_script = os.path.join(...)
    os.system(f"python {w5h1_script}")     # Then 5W1H analysis
    print("[5W1H] 自動分析完了")
```

**Analysis**:
- Sequential execution confirmed: restrictions runs BEFORE 5W1H
- Both are conditional on `incidents_generated` list being populated
- Order guarantee: Cannot run 5W1H before restrictions (sequential os.system calls)

**Evidence Status**: ✅ CONFIRMED

---

### D-3 (Extraction Range): ✅ CORRECTED IN CODE

**Code Location**: `tools/mocka_restrictions.py` lines 87-90

```python
if "## 再発防止" in content:
    section = content.split("## 再発防止")[1]
    section = section.split("##")[0].strip()
    restrictions.append(f"### {inc_id} より\n{section}")
```

**Analysis**:
- Explicitly targets "## 再発防止" section (not generic)
- Extracts content between "## 再発防止" and next section marker
- Correctly handles both INC-001 (manual) and INC-002 (auto-generated)

**Real Data Evidence**:
- INC-001 has: "再発防止：\n憲章第2条制定\nsecrets/フォルダ運用開始\n.gitignore完全版適用"
  - This content appears in GPT_RESTRICTIONS.md (lines 23-25) ✅
  
- INC-002 has: "再発防止：\n（要分析）"
  - But it doesn't appear in output (correctly withheld by D-1 check) ✅

**Evidence Status**: ✅ CONFIRMED

---

### D-1 (Approval Gate): ✅ IMPLEMENTED BUT INFRASTRUCTURE INCOMPLETE

**Code Location**: `tools/mocka_restrictions.py` lines 79-83

```python
allowed, reason = is_publishable(inc_id)
if not allowed:
    withheld.append((inc_id, reason))
    continue
```

**is_publishable() Logic** (lines 31-69):
1. Checks if INC_LIFECYCLE state file exists (FC-1)
2. Checks if state file is readable JSON (FC-2, FC-3)
3. Validates schema_version and state values (FC-4, FC-5)
4. Validates incident_id consistency (FC-6)
5. Queries human_gate for approval status (FC-7, FC-8, FC-9)
6. Only publishes if approval == "APPROVED"

**Infrastructure Status**:
- ✅ is_publishable() function implemented with 9 Fail-Closed conditions
- ❌ INC_LIFECYCLE_DIR (`data/inc_lifecycle/`) does NOT exist
- ❌ human_gate_events table in mocka_events.db does NOT exist
- ⚠️ Approval records for existing incidents (INC-001, INC-002) do NOT exist

**Current Behavior if Executed Today**:
```
INC-20260401-001: is_publishable() → FC-1 (state file missing) → withheld
INC-20260401-002: is_publishable() → FC-1 (state file missing) → withheld
```

**Paradox**: INC-001 appears in GPT_RESTRICTIONS.md, but would fail is_publishable() check.

**Resolution**: GPT_RESTRICTIONS.md was generated (2026-07-31 18:07:02) BEFORE is_publishable() infrastructure was fully implemented. If the pipeline runs today with current code, NEITHER incident would be published.

---

## CASE 4 VERIFICATION MATRIX

Per INC_PIPELINE_DEFECT_DEPENDENCY_v0.1.md section 4.2:

| Aspect | Case 4 Required | Current Status | Verified |
|--------|-----------------|-----------------|----------|
| D-2 order: restrictions before 5W1H | ✅ Yes | ✅ Code correct | ✅ |
| D-3 extraction: "## 再発防止" section | ✅ Yes | ✅ Code correct | ✅ |
| D-1 approval gate in place | ✅ Yes | ✅ Code exists | ⚠️ INFRASTRUCTURE MISSING |
| Single execution cycle | ✅ Yes | ✅ Sequential os.system | ✅ |
| Expected output: correct content in single cycle | ⚠️ UNKNOWN | ⚠️ Code correct, but infrastructure blocks execution | ⚠️ |

---

## UNKNOWN: Why INC-001 Is Published Despite Infrastructure Gap

**Observation**: GPT_RESTRICTIONS.md contains INC-001 content, but:
1. INC_LIFECYCLE state files don't exist
2. Human Gate approval records don't exist
3. is_publishable() should reject both incidents

**Three Hypotheses**:

### H1: Legacy Code Path (Most Likely)
- GPT_RESTRICTIONS.md was generated on 2026-07-31
- Current restrictions.py with is_publishable() may not have been used for that generation
- An earlier version without approval gates existed

**Evidence**:
- Generate_restrictions() has "# RC-B最小実装" comment (line 79) suggesting this is recent
- But GPT_RESTRICTIONS.md output format is simple without withheld list annotations
- If approval gates were active, we'd see "[非掲載] INC-002: FC-1 ..." message

### H2: Manual Fallback (Possible)
- INC-001 may be manually approved or whitelisted outside the approval system
- "Claude Sonnet 4.6 / 2026-04-01" in approval field suggests manual approval record
- Possible that is_publishable() has additional logic for manual incidents

**Evidence Needed**: Review full mocka_restrictions.py for any bypass logic

### H3: Test/Development State (Possible)
- The GPT_RESTRICTIONS.md may be from a development build
- Production system may have proper state files and approvals

**Evidence Needed**: Check commit history for when state files were expected to exist

---

## RECOMMENDATION FOR R01 REVIEW

### Status Summary

**Section 4.2 D-2 and D-3**: ✅ CODE CORRECTIONS CONFIRMED
- Both fixes are present and logically correct
- Sequential execution order: ✅ guaranteed
- Extraction range: ✅ targets correct section
- Case 4 code structure: ✅ present

**D-1 Approval Infrastructure**: ⚠️ INCOMPLETE
- is_publishable() function: ✅ implemented
- INC_LIFECYCLE state storage: ❌ not created
- Human Gate database: ❌ empty (table doesn't exist yet)
- Approval records: ❌ don't exist for existing incidents

### What This Means

**If the pipeline runs today**:
- Code changes (D-2, D-3) will execute correctly
- Approval gate (D-1) will REJECT all incidents without state files
- Result: NO incidents published (overly restrictive, Fail-Closed)

**Expected Next Phase**:
1. Create `data/inc_lifecycle/` directory
2. Populate approval records in human_gate_events
3. Mark manual incidents as APPROVED
4. Test pipeline to verify Case 4 output

### Test Readiness

**To achieve full Case 4 verification**:

1. **Setup Phase** (one-time):
   ```
   mkdir -p data/inc_lifecycle
   # Manually approve INC-001 in human_gate
   # Create INC-001.json state file with DETECTED/ANALYZED/PUBLISHED
   ```

2. **Test Phase**:
   ```
   python tools/mocka_risk_engine.py  # Generate new INC if data exists
   python tools/mocka_restrictions.py # Should show INC-001 + new approved INCs
   python tools/mocka_5w1h.py        # Should append 5W1H to new INCs
   # Verify GPT_RESTRICTIONS.md content matches Case 4 expectations
   ```

3. **Verification**:
   - Only APPROVED incidents appear in output
   - "## 再発防止" sections correctly extracted
   - 5W1H sections appended without corrupting approval sections
   - No intermediate states visible in public file

---

## CONCLUSION

**Real Data Status**: Section 4.2 corrections (D-2, D-3) are present in code. D-1 infrastructure is incomplete.

**Case 4 Readiness**: Code logic is correct. Infrastructure setup is pending.

**Recommendation**: 
1. R01 approval required before creating state files
2. Explicitly approve existing manual incidents
3. Run integration test with sample data
4. Verify Case 4 output matches specification

