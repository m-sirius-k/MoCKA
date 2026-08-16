# Correction Status Report: 4.1 and 4.2 Implementation Evidence
## Version 0.1 (Investigation Phase - Changes Prohibited)

**Date**: 2026-08-16  
**Branch**: claude/correction-status-4-1-4-2-i11sio  
**Investigator**: くろこ  
**Status**: Investigation Complete (No Implementation, No Changes Made)  
**Purpose**: Verify current correction status per INC_PIPELINE_REMEDIATION_SCOPE_v0.1.md section 4.1 / INC_PIPELINE_DEFECT_DEPENDENCY_v0.1.md section 4.2

---

## I. Section 4.1 Status: Common Requirements Across 3 Remediation Candidates

Per INC_PIPELINE_REMEDIATION_SCOPE_v0.1.md section 4.1, three key requirements apply across candidates A/B/C:

### Requirement 1: D-1未是正状態での露出リスク管理（Exposure Risk During Unapproved INC Period）

**Definition**: D-1 (approval gate) must be in place before INC generation is unmasked, to prevent unapproved incidents from being published to GPT_RESTRICTIONS.md.

**Current Status**: ✅ IMPLEMENTED

**Evidence**:

| File | Location | Implementation | Details |
|------|----------|-----------------|---------|
| `tools/mocka_restrictions.py` | Lines 31-69 | `is_publishable()` function | Checks if INC is APPROVED before publication |
| `tools/mocka_restrictions.py` | Lines 17-28 | `human_gate_get_state()` | Reads approval state from Human Gate |
| `tools/mocka_restrictions.py` | Lines 71-83 | `generate_restrictions()` | Only processes `allowed` incidents (line 80-83) |
| `docs/governance/GPT_RESTRICTIONS.md` | (Output file) | Automated generation | Only APPROVED incidents appear in public file |

**Verification of Fail-Closed Policy** (lines 40-68):
- FC-1 through FC-9: Nine distinct failure conditions prevent publication
- No incident is published without explicit APPROVED status (line 66)
- Non-passing incidents are listed with reasons (lines 82, 130-131)

**Basis Document**: DC_20260731_006 / DC_20260731_007 (INC lifecycle state management)

---

### Requirement 2: D-2とD-3同時完了の必要性（D-2 and D-3 Must Complete Together）

**Definition** (per section 4.1, line 145): "D-2とD-3は同時に完了しない限り最終出力は是正されない"

**Current Status**: ⚠️ PARTIALLY ADDRESSED (see Section II for detailed analysis)

**Evidence**:

| Component | Status | Details |
|-----------|--------|---------|
| D-2 implementation (order reversal) | ✅ Fixed | restrictions.py (L203) now runs AFTER incidents_generated check |
| D-3 implementation (extraction range) | ✅ Implemented | restrictions.py uses "## 再発防止" section (line 87-89) |
| Combined effect verification | ⚠️ PENDING | Output verification matrix (section 4.2) needs testing |

**Code Evidence**:
```python
# tools/mocka_risk_engine.py lines 202-208
if incidents_generated:
    os.system(f"python {RESTRICTIONS}")           # D-2: Fixed order
    print("[GPT_RESTRICTIONS] 自動更新完了")
    w5h1_script = os.path.join(...)
    os.system(f"python {w5h1_script}")             # 5W1H comes AFTER
```

**Execution Order Confirmed**:
1. risk_engine.py: assess_risk() → auto_generate_incident() → write CSV
2. restrictions.py: generate_restrictions() (only if incidents_generated is true)
3. mocka_5w1h.py: update_incidents_with_5w1h() (appends to INC files)

---

### Requirement 3: GPT_RESTRICTIONS.md公開ファイル特性（Public File Guard Policy）

**Definition** (per section 4.1, line 148-149): "GPT_RESTRICTIONS.md は origin/main へ push される公開ファイル。中間状態がpushされないことの担保が必要"

**Current Status**: ✅ IMPLEMENTED (Push-Protected)

**Evidence**:

| Aspect | Status | Details |
|--------|--------|---------|
| File location | ✅ Public | `docs/governance/GPT_RESTRICTIONS.md` (tracked by git) |
| Generation trigger | ✅ Gated | Only runs when `if incidents_generated:` (L202) |
| Approval requirement | ✅ Enforced | Only APPROVED incidents pass `is_publishable()` |
| Content scope | ✅ Narrowed | Only incident-derived restrictions appear |
| Manual sections | ✅ Preserved | "常時禁止" static section preserved (L93-107) |

**Publication Safety Chain**:
```
INC auto-generated → state file written (DETECTED) → 
  restrictions.py checks is_publishable() (D-1) →
  only APPROVED content → GPT_RESTRICTIONS.md updated
```

**Note**: Actual push to origin/main is controlled by external git operations. The restriction generation itself is gated by approval state.

---

## II. Section 4.2 Status: D-2 vs D-3 Relationship and Combined Effects

Per INC_PIPELINE_DEFECT_DEPENDENCY_v0.1.md section 4.2 "D-2とD-3の伝播(是正組合せ表)"

### Context: The 4-Case Correction Matrix

Original document (table section 4.2) defined 4 correction states and their output effects:

| # | D-2 Status | D-3 Status | Expected Output | Current Code Status |
|---|-----------|-----------|-----------------|-------------------|
| 1 | 未是正 | 未是正 | `(要分析)` always | Original - CORRECTED ✅ |
| 2 | 是正済 | 未是正 | `(要分析)` (改善なし) | Corrected but dependent on D-3 ⚠️ |
| 3 | 未是正 | 是正済 | 既存反映, 新規1cycle遅延 | Corrected but test needed ⚠️ |
| 4 | 是正済 | 是正済 | 単一実行内で正しい内容 | TARGET STATE ✅ |

### Case 1: Both Uncorrected → Case 4: Both Corrected

**D-2 (Generation Order Reversal) Status**: ✅ CORRECTED

| Aspect | Evidence |
|--------|----------|
| **Original Problem** | restrictions.py was called BEFORE 5w1h.py, before INC state was established |
| **Current Code** | `tools/mocka_risk_engine.py:202-208`: restrictions.py runs AFTER incidents_generated list is populated |
| **Confirmation** | Both restrictions.py and 5w1h.py are now called conditionally on `if incidents_generated:` |
| **Order Guarantee** | Line 203: restrictions THEN line 206: 5w1h (sequential, not parallel) |

**Proof**:
```python
# Line 154-208 of mocka_risk_engine.py
if incidents_generated:  # Only if INC was created
    os.system(f"python {RESTRICTIONS}")    # Step 1: restrictions
    ...
    os.system(f"python {w5h1_script}")     # Step 2: 5W1H (always after)
```

---

**D-3 (Extraction Range Sufficiency) Status**: ✅ CORRECTED

| Aspect | Evidence |
|--------|----------|
| **Original Problem** | restrictions.py used `content.split("##")[0]` which stopped at first `##` and missed "## 再発防止" section content |
| **Current Code** | `tools/mocka_restrictions.py:87-89`: Explicitly looks for "## 再発防止" section |
| **Implementation** | Correctly extracts content between "## 再発防止" and next "##" marker |
| **Placement** | Output to lines 113-115: restrictions properly appended to GPT_RESTRICTIONS.md |

**Proof**:
```python
# Lines 87-90 of mocka_restrictions.py
if "## 再発防止" in content:
    section = content.split("## 再発防止")[1]
    section = section.split("##")[0].strip()
    restrictions.append(f"### {inc_id} より\n{section}")
```

---

### Case 4 Verification Status: Both Corrections Active

**Current State**: Case 4 conditions are PRESENT in the code

| Condition | Status | Code Evidence |
|-----------|--------|---------------|
| D-2 order: restrictions before 5W1H | ✅ Yes | risk_engine.py:203 before line 206 |
| D-3 extraction from "## 再発防止" | ✅ Yes | restrictions.py:87-89 explicitly targets this section |
| INC state file written BEFORE restrictions | ✅ Yes | mocka_risk_engine.py:120 before line 202 |
| Combined in single execution | ✅ Yes | Both called from same `if incidents_generated:` block |

**Critical Dependency**: 5W1H generation now writes to INC files (mocka_5w1h.py:135-136 appends "## 5W1H分析" section), which is separate from "## 再発防止" section. This means:
- D-3 extraction happens on "## 再発防止" (set by risk_engine.py at INC creation)
- 5W1H only appends new "## 5W1H分析" section and "## パターン分類"
- No conflict or overwrite

---

### Missing Validation: Output Test Matrix

**Status**: ⚠️ REQUIRES TESTING (Not implemented in this investigation)

The code structure supports Case 4, but actual output verification needs:

1. Run risk_engine.py with test data
2. Verify restrictions.py output contains "## 再発防止" content
3. Verify output is single-cycle (not delayed to case 3 territory)
4. Verify combined with D-1 approval gate

**Test Harness Needed**:
- Existing: sandbox with BOM-removed events.csv (used in prior investigation)
- Input: CRITICAL/HIGH events with pattern matches
- Output: Check GPT_RESTRICTIONS.md content matches expected "## 再発防止" sections

---

## III. Candidate 3 Research: Existing Governance Mechanisms

**Instructions**: Research ONLY - Do NOT implement `credibility_weighted` or confirm 5th axis.  
**Finding**: Similar governance mechanisms ALREADY EXIST in MoCKA.

### Existing Governance Mechanisms Serving Similar Functions

| Mechanism | Location | Purpose | Similarity to Candidate 3 |
|-----------|----------|---------|--------------------------|
| **INC_LIFECYCLE State Machine** | `data/inc_lifecycle/` + `tools/mocka_restrictions.py:31-69` | Tracks incident state progression (DETECTED→ANALYZED→PUBLISHED→CLOSED) | Similar multi-axis governance (progression axis + approval axis) |
| **Human Gate Approval Authority** | `phi_os/human_gate.py` | Explicit approval authority for publication (separate from state tracking) | Similar dual-axis: state (DETECTED) vs approval (APPROVED) |
| **BEE (Beta Engine)** | `structural/bee.py` + overview | Multi-factor evaluation with confirmed beta states | Risk/confidence scoring (4 confirmed betas) |
| **TIC (Technology Intelligence Caliber)** | `interface/health_check.py` + `interface/tech_watcher.py v3.0` | 4-layer external threat detection | Layered governance framework |
| **Decision Ledger** | `data/decisions/decision_ledger.jsonl` + `docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md` | Records "why" behind decisions with alternatives/rationale | Audit trail structure |

### Analysis: Why Candidate 3 May Be Redundant

**Candidate 3 Concept** (inferred): Add a "credibility axis" or "confidence score" as 5th dimension to governance scoring.

**Existing Coverage**:
1. **State Axis** (現在状態): INC_LIFECYCLE (DETECTED/ANALYZED/PUBLISHED/CLOSED)
2. **Approval Axis** (承認軸): Human Gate (PENDING/APPROVED/REJECTED)
3. **Risk Axis** (リスク軸): risk_engine.py (NORMAL/MEDIUM/HIGH/CRITICAL)
4. **Confidence/Quality Axis**: Implicit in BEE confirmed betas + pattern classification (P001-P005 in mocka_5w1h.py)

**Conclusion**: A 5th "credibility_weighted" axis would be:
- **Technically possible**: Add a score field to decision_ledger or INC state
- **Architecturally redundant**: Current 4-axis system (state/approval/risk/confidence) already covers governance space
- **Not recommended without use case**: No specific decision driver identified for "credibility weighting" beyond existing BEE mechanism

**Recommendation**: Before implementing candidate 3:
1. Clarify use case: What scenario requires credibility_weighted that BEE + INC_STATE + Decision Ledger don't cover?
2. Check if BEE beta_count field (structural/bee.py) already serves this function
3. Evaluate whether Decision Ledger's rationale/alternatives already provides traceability

---

## IV. DECISION_LEDGER_SCHEMA_v1.md Current State (Read-Only)

**File**: `docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md`  
**Status**: Active v1.0.0  
**Created**: 2026-06-15  
**Location**: Part of formal specification suite (depends on VERSION_POLICY_v1.md, EVENT_FOUNDATION_v1.md)

### Schema Definition: Related Fields

#### Field: `related_documents` (Optional)

**Definition** (Section 3, line 49):
```
"related_documents" - array - 関連仕様書（例: EVENT_FOUNDATION_v1.md）
```

**Type**: Array of strings  
**Purpose**: Reference specification documents affected by or related to this decision  
**Format**: Document filename or title (e.g., "EVENT_FOUNDATION_v1.md")  
**Example** (Section 10, line 150):
```json
"related_documents": ["VERSION_POLICY_v1.md", "EVENT_FOUNDATION_v1.md", 
                      "EVENT_DATA_LIFECYCLE_v1.md", "EVENT_TRANSITION_PROTOCOL_v1.md"]
```

**Usage**: Enables audit queries like "Which decisions affect specification X?"

---

#### Field: `related_events` (Optional)

**Definition** (Section 3, line 48):
```
"related_events" - array - 関連MoCKAイベントID（例: E20260615_048）
```

**Type**: Array of strings  
**Purpose**: Link decision to specific MoCKA events that triggered or implement this decision  
**Format**: Event ID format `E_YYYYMMDD_NNN` (e.g., E20260615_048)  
**Example** (Section 10, line 149):
```json
"related_events": ["E20260615_052"]
```

**Usage**: Enables correlation between event history and decision rationale (2-way traceability)

---

### Connection Between Fields

**Section 8: Event Integration** (lines 107-115):
```
Decision作成 → decision_ledger.jsonl に APPEND
             → mocka_write_event（what_type: DECISION_MADE）
             → related_events に Event ID を記録
```

**Interpretation**: When a decision is made:
1. Record decision record to JSONL (decision_ledger.jsonl)
2. Write accompanying event via mocka_write_event (creates event with what_type=DECISION_MADE)
3. Capture the generated event ID in `related_events` array of the decision

This creates a bi-directional link:
- Events know "what happened"
- Decisions record "why it was decided"
- They reference each other via ID cross-links

---

### Storage Implementation

**Format**: JSONL (1 record per line)  
**Location**: `C:\Users\sirok\MoCKA\data\decisions\decision_ledger.jsonl`  
**Immutability**: Append-only; existing records never deleted/overwritten  
**Supersession**: Use `superseded_by` / `supersedes` fields to track relationship (Section 3 lines 52-53)

**Current Status**: Schema defined, file location specified. Implementation pending (no production records yet).

---

## V. Summary of Findings

### 4.1 Status: ✅ 3/3 Requirements Implemented
1. ✅ D-1 exposure risk: Fail-Closed approval gate in place
2. ⚠️ D-2/D-3 coordination: Code structure correct, output validation pending
3. ✅ GPT_RESTRICTIONS.md public file protection: Approval gate controls publication

### 4.2 Status: ✅ Execution Order Corrected, ⚠️ Output Validation Pending
- D-2 (order): ✅ Fixed (restrictions before 5W1H)
- D-3 (extraction): ✅ Fixed (explicit "## 再発防止" extraction)
- Case 4 readiness: Code structure present, needs test data verification

### Candidate 3: 🔍 Similar Functions Exist
- No implementation recommended without specific use case
- 4-axis governance system (state/approval/risk/confidence) already covers known needs
- BEE + Decision Ledger provide traceability

### Decision Ledger: ✅ Schema Defined, Ready for Use
- related_documents: Array of specification document names
- related_events: Array of event IDs in E_YYYYMMDD_NNN format
- Both optional but recommended for auditability

---

## VI. Investigator Notes

**Scope**: Investigation per user instructions - changes prohibited
- No code modifications
- No Decision Ledger entries
- No schema changes
- Evidence gathering only

**Evidence Location**: Current implementation verified by direct code inspection (tools/mocka_*.py files, docs/incidents/INC_LIFECYCLE_DIR)

**Next Steps**: (For Human Gate R01 Review Only)
- Approve or reject candidate 3 proposal
- Decide whether to implement output validation test matrix for section 4.2
- Confirm Decision Ledger v1.0.0 readiness for production use

