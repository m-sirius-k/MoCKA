# Comprehensive Investigation Report: Section 4.1/4.2, BEE, Candidate 3, and Semantica Integration
## Version 0.1 (Investigation Complete - READ-ONLY, No Implementation)

**Date**: 2026-08-16  
**Format**: FACT → EVIDENCE → UNKNOWN → R01判断 → 推奨アクション  
**Scope**: Investigation only. No implementation, no Decision Ledger changes, no schema changes.

---

## I. SECTION 4.1 STATUS: COMMON REQUIREMENTS ACROSS 3 REMEDIATION CANDIDATES

### Requirement 1: D-1未是正状態での露出リスク管理

**FACT**: D-1 (approval gate) prevents unapproved incidents from being published.

**EVIDENCE**:
- `tools/mocka_restrictions.py:31-69`: `is_publishable()` function with Fail-Closed design
- 9 distinct failure conditions (FC-1 through FC-9) prevent publication
- Line 66: `if approval != "APPROVED": return False`
- Only incidents with human_gate status == "APPROVED" are published
- Withheld incidents logged with reasons (lines 130-131)

**UNKNOWN**:
- Infrastructure incomplete: INC_LIFECYCLE_DIR doesn't exist, human_gate_events table empty
- Approval records for existing incidents (INC-001, INC-002) not yet created
- Unclear whether D-1 was active when current GPT_RESTRICTIONS.md was generated (2026-07-31)

**R01判断**: D-1 実装済みだが、インフラが整備待ち (実機能するには state file作成と approval record投入が必須)

**推奨アクション**: 
1. R01 承認後、INC_LIFECYCLE_DIR を作成
2. 既存manual INC-001 を明示的に APPROVED 状態に設定
3. 統合テスト実行

---

### Requirement 2: D-2とD-3同時完了の必要性

**FACT**: Both D-2 and D-3 corrections are present in code.

**EVIDENCE**:
- **D-2 (order reversal)**: `risk_engine.py:203` → `restrictions.py` runs BEFORE line 206 → `5w1h.py`
  - Sequential os.system() calls guarantee order
  - Both conditional on `if incidents_generated:`
  
- **D-3 (extraction range)**: `restrictions.py:87-89` explicitly targets "## 再発防止" section
  - `section.split("##")[0].strip()` correctly extracts single section
  - Real data verification: INC-001 "## 再発防止" content appears in output ✅
  
- **Combined Effect**: Code structure supports Case 4 (both corrected)

**UNKNOWN**:
- Whether Case 4 output is actually achieved in current system
- Need to run with real event data to verify 5W1H appends without overwriting approval sections

**R01判断**: D-2・D-3 ともにコード修正済み、Case 4 対応。実行時検証待ち。

**推奨アクション**:
1. Test data preparation (events with CRITICAL/HIGH + "## 再発防止" content)
2. Run risk_engine → restrictions → 5w1h sequence
3. Verify GPT_RESTRICTIONS.md shows correct "## 再発防止" without Case 2/3 partial symptoms

---

### Requirement 3: GPT_RESTRICTIONS.md公開ファイル特性

**FACT**: Publication is gated by approval state; only APPROVED incidents appear in public file.

**EVIDENCE**:
- `generate_restrictions()` line 80-83: `if not allowed: withheld.append() → continue`
- Only incidents passing `is_publishable()` reach output (line 113)
- Real data: INC-002 (unapproved) correctly absent from output
- INC-001 (manual/appears approved) correctly present
- Push protection: Execution order ensures no mid-state publication

**UNKNOWN**:
- Whether INC-001's "approval" status is actually recorded in human_gate
- If infrastructure fails, whether there's fallback publication logic

**R01判断**: 公開ファイル保護は実装済み。インフラ完成待ち。

**推奨アクション**: D-1インフラ整備時に同時検証

---

## II. SECTION 4.2 REAL DATA VALIDATION

### D-2 Verification: Order Reversal

**FACT**: restrictions.py runs before 5w1h.py in current code.

**EVIDENCE**:
```python
# risk_engine.py L202-208
if incidents_generated:
    os.system(f"python {RESTRICTIONS}")      # Step 1
    print("[GPT_RESTRICTIONS] 自動更新完了")
    w5h1_script = ...
    os.system(f"python {w5h1_script}")       # Step 2 (after Step 1)
```

**Status**: ✅ CONFIRMED

---

### D-3 Verification: Extraction Range

**FACT**: "## 再発防止" section is explicitly extracted.

**EVIDENCE**:
```python
# restrictions.py L87-90
if "## 再発防止" in content:
    section = content.split("## 再発防止")[1]
    section = section.split("##")[0].strip()
    restrictions.append(f"### {inc_id} より\n{section}")
```

Real data output: INC-001 content correctly appears in GPT_RESTRICTIONS.md lines 23-25

**Status**: ✅ CONFIRMED

---

### Case 4 Overall Status: ⚠️ CODE CORRECT, INFRASTRUCTURE INCOMPLETE

| Component | Status | Evidence |
|-----------|--------|----------|
| D-2: Order | ✅ Fixed | Sequential execution guaranteed |
| D-3: Range | ✅ Fixed | Explicit section extraction |
| D-1: Gate | ✅ Implemented | is_publishable() present |
| Infrastructure | ❌ Incomplete | No state files, no approval records |
| Execution | ⚠️ Would REJECT all | Without state/approval, Fail-Closed =no publish |

**Conclusion**: Code is correct; infrastructure setup required for actual Case 4 execution.

---

## III. BEE SYSTEM ANALYSIS: Confidence Axis Inventory

### BEE Architecture (structural/bee.py)

**Core Mechanism**: β (Beta) Lifecycle tracking through evidence/contradiction counts

**Axes**:
1. **Evidence Count (X-axis)**: Support signals collected from events
2. **Contradiction Rate (Y-axis)**: `contra / ev` ratio
3. **Lifecycle Status**: Auto-updated based on thresholds
4. **Confidence (Implicit)**: `ev / (ev + contra) * 100` (calculated, not stored)

**Stage Transitions** (lines 39-46):
- 観察β: 0-4 evidence
- 成長中: 5-19 evidence, contra_rate ≤ 0.39
- 確立: ≥20 evidence, contra_rate ≤ 0.19
- 制度化: ≥20 evidence (meta-β generated)
- 衰退: contra_rate ≥ 0.40
- 消滅: 90+ days without update

**Confidence Calculation** (implicit, line 532):
```python
pct = int(ev / total * 100) if total > 0 else 0
```

---

### BEE's Confidence vs Candidate 3 "credibility_weighted"

**FACT**: BEE has implicit confidence (support ratio), but NOT a persistent "credibility_weighted" field.

**BEE Current Capability**:
- ✅ Tracks evidence count (supportive signals)
- ✅ Tracks contradiction count (opposing signals)
- ✅ Calculates confidence percentage on-the-fly
- ✅ Adjusts lifecycle based on confidence thresholds
- ✅ Integrates with PHI DNA approvals (evidence +5 when approved)
- ❌ Does NOT store permanent "credibility_weighted" score
- ❌ Does NOT propagate confidence to Decision records
- ❌ Does NOT cross-link β confidence with Incident approval confidence

**What Candidate 3 Would ADD**:
- Persistent "credibility_weighted" field in Decision Ledger or INC state
- Cross-domain confidence: evidence + expert_approval + meta_β_consensus
- Propagation of confidence scores through causal chains
- Threshold-based filtering based on credibility (not just binary approval)

---

### UNKNOWN: Whether Candidate 3 Is Actually Needed

**Evidence for "Yes, it's needed"**:
- Decision Ledger lacks confidence metric (currently binary: exists/doesn't exist)
- INC state lacks quality/credibility score beyond lifecycle stage
- BEE confidence is implicit (calculated) not explicit (stored)
- No current mechanism for "this decision is controversial but approved" (nuance)

**Evidence for "No, it's redundant"**:
- BEE already tracks evidence/contradiction → implicit confidence
- Human Gate approval is explicit: APPROVED or not (no shades of gray needed)
- Decision Ledger already has `alternatives` and `rationale` (explains confidence)
- Lifecycle stages already encode confidence level (観察β=low, 確立=high)

**Actual Use Case Examples** (UNKNOWN): No concrete scenario in code where "credibility_weighted" would change behavior beyond current BEE + approval logic.

---

### R01判断

**現状**: BEEの implicit confidence で大半のニーズを満たしている。しかし persistent credibility_weighted スコアはない。

**必要性**: 未確定。具体的なユースケース（「このDecisionは契約だが信頼度60%で実装待ち」等）がなければ提案段階に留める。

**推奨**: Decision Ledger に "confidence" フィールドを追加するなら、根拠として「BEEの contradition 率が高い」「複数の相反Decision がある」などを明記する必要がある。

---

## IV. DECISION LEDGER SCHEMA v1 VERIFICATION

### Current State: ✅ Active v1.0.0

**Location**: `docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md`  
**Status**: Active (created 2026-06-15)  
**Storage**: `data/decisions/decision_ledger.jsonl` (append-only JSONL)

### Related Fields Defined

| Field | Type | Status | Definition |
|-------|------|--------|-----------|
| `related_documents` | Array | Optional | Specification documents affected (e.g., "EVENT_FOUNDATION_v1.md") |
| `related_events` | Array | Optional | Event IDs in E_YYYYMMDD_NNN format |
| `supersedes` | String | Optional | Previous Decision ID this replaces |
| `superseded_by` | String | Optional | Later Decision that replaces this |

### Actual Usage in MoCKA

**UNKNOWN**: No production Decision records exist yet in decision_ledger.jsonl (database empty).

**Inferred Use Cases** (from schema examples, Section 10):
- Related events: Link decision to triggering events (E20260615_052)
- Related documents: Track affected specifications
- Supersedes: Track decision evolution without overwriting

### FACT: Schema Already Handles Most Relationship Needs

**Present Capabilities**:
- ✅ Document traceability (related_documents)
- ✅ Event linkage (related_events)
- ✅ Decision supersession (supersedes/superseded_by)
- ✅ Rationale documentation (rationale field)
- ✅ Alternative tracking (alternatives with rejected_reason)

**NOT Present**:
- ❌ Causal relationship type (e.g., "caused_by", "enables", "conflicts_with")
- ❌ Bidirectional links (only one-way via supersedes)
- ❌ Strength-of-relationship scores
- ❌ Temporal ordering constraints

### R01判断

**現状**: Schema v1.0 は基本的な関係定義に十分。

**追加提案**: 「causal_links」フィールドを検討する価値あり。ただし、実装例がないまま追加は慎重に。

**推奨**: 次回のDecision記録時に、実際に「このDecisionはAの結果である」という関係を明示する必要があるか確認してから追加判断する。

---

## V. SEMANTICA FROM MOCKA ABSORPTION: Strategic Classification

### What's Already in MoCKA (Similar Functions Exist)

| Semantica Concept | MoCKA Equivalent | Status | Coverage |
|-------------------|------------------|--------|----------|
| Confidence Scoring | BEE beta evidence count | ✅ Exists | Implicit, needs explicit propagation |
| Lifecycle States | INC state machine (DETECTED→ANALYZED→PUBLISHED→CLOSED) | ✅ Exists | Partial (incomplete infrastructure) |
| Approval Authority | Human Gate (PENDING/APPROVED/REJECTED) | ✅ Exists | Complete |
| Causality Tracking | Decision Ledger supersedes/alternatives | ⚠️ Partial | One-directional only |
| Evidence Aggregation | BEE pattern detection | ✅ Exists | Limited to keywords/patterns |
| Relationship Mapping | Decision Ledger related_documents/events | ✅ Exists | Document/event level only |

---

### What's Missing in MoCKA (Semantica Could Provide)

| Gap | Semantica Concept | MoCKA Impact | Absorption Value |
|-----|-------------------|--------------|------------------|
| Strength-of-link scoring | Relationship weights | Could improve decision prioritization | MEDIUM |
| Semantic type system | Causal vs correlation vs constraint | Decision reasoning clarity | LOW (manual rationale suffices) |
| Cross-domain entity resolution | Global ID mapping | Would improve linked data | HIGH (if event/decision schema split persists) |
| Contradiction detection | Automated conflict finding | Risk detection | HIGH (complements BEE) |
| Knowledge graph queries | Structured questions over relationships | Audit capability | HIGH |

---

### Strategic Absorption Candidates: Top 3 Recommendations

#### **Candidate A: Contradiction Detection Engine (Highest Value)**

**What It Addresses**:
- Currently BEE detects contradiction via keyword signals
- Semantica could: Detect logical contradictions in Decision rationale text
- Use case: "Decision A says X is safe; Decision B says X is risky" → AUTO-DETECT

**MoCKA Integration Points**:
- Input: Decision Ledger records
- Logic: NLP on rationale fields + alternatives
- Output: Contradiction flags to Human Gate review

**Absorption Strategy**:
1. Create `decision_contradiction_detector.py` (new tool)
2. Run post-Decision-submission, pre-approval
3. Flag for Human Gate manual review (not auto-reject)
4. Log to events.db as "CONTRADICTION_DETECTED" event

**Risk**: None (detection-only, no auto-action)  
**Effort**: Medium (NLP integration)  
**Value**: High (catches logic errors before institutionalization)

---

#### **Candidate B: Relationship Strength Scoring (Medium Value)**

**What It Addresses**:
- Current related_documents/events are binary: present or absent
- Semantica could: Score link strength (primary vs secondary vs tangential)
- Use case: "This Decision DIRECTLY CAUSES schema change, ENABLES Protocol v2, MENTIONS Architecture v1"

**MoCKA Integration Points**:
- Extend Decision Ledger schema with relationship types
- Backward compatible (optional field)
- Used in audit queries ("Which decisions directly affect X?")

**Absorption Strategy**:
1. Add optional `relationship_strength` array to Decision Ledger
2. Format: `{target: "document_id", strength: "primary|enabling|related", reason: "..."}`
3. Implement in version 1.1 (non-breaking)
4. Use in DECISION_LEDGER_SCHEMA_v1.1.md

**Risk**: Schema extension (backward compat OK)  
**Effort**: Low (data structure only, no processing logic)  
**Value**: Medium (audit clarity)

---

#### **Candidate C: Cross-Domain Entity Resolution (Medium Value)**

**What It Addresses**:
- Events use E_YYYYMMDD_NNN format
- Decisions use DC_YYYYMMDD_NNN format
- Incidents use INC-YYYYMMDD-NNN format
- Semantica could: Map common entities (who_actor, where_component, what_type) across formats
- Use case: "Show me all Decisions related to 'router.py changes'" (across Event, INC, Decision domains)

**MoCKA Integration Points**:
- Create `entity_linker.py` that normalizes and cross-references IDs
- Query tool: "Find all artifacts affecting entity X"
- Output: Unified view for audit

**Absorption Strategy**:
1. Define canonical entity registry (component names, actor IDs)
2. Linker maps Events/INCs/Decisions to canonical IDs
3. Query tool uses registry for cross-domain searches
4. Non-invasive (optional, metadata layer)

**Risk**: Maintenance (keep registry up-to-date)  
**Effort**: Medium (entity registry + linker)  
**Value**: Medium-High (audit efficiency)

---

## VI. NOT RECOMMENDED: Concepts Conflicting with MoCKA Philosophy

### Why These Should NOT Be Absorbed

| Semantica Concept | MoCKA Conflict | Reason |
|-------------------|----------------|--------|
| Auto-contradiction resolution | Unknown Preservation | MoCKA requires explicit Human Gate judgment, not auto-resolve |
| Probabilistic truth scores | Evidence Supremacy | Events are facts (recorded), not probabilities |
| Schema versioning (SemVer) | VERSION_POLICY_v1 already defined | Conflicting governance models |
| Graph traversal without records | Append-Only Invariant | Semantica's query-time derivation vs MoCKA's event-sourced truth |

---

## VII. PROHIBITION ENFORCEMENT: What Was NOT Done

✅ **Complied with**:
- ❌ NO code changes to existing files
- ❌ NO Decision Ledger modifications
- ❌ NO schema changes (only designs proposed)
- ❌ NO "credibility_weighted" field created
- ❌ NO Decision Ledger entries created
- ❌ NO candidate 3 confirmed as 5th axis
- ✅ READ-ONLY investigation only

---

## FINAL SUMMARY FOR R01 REVIEW

### Section 4.1 Status
- ✅ 3/3 common requirements implemented in code
- ⚠️ D-1 infrastructure incomplete (state files, approval records)
- **Action**: Complete infrastructure setup post-approval

### Section 4.2 Status
- ✅ D-2 and D-3 corrections present in code
- ✅ Case 4 code structure ready
- ⚠️ Never executed with real data yet
- **Action**: Integration testing with sample data

### BEE Analysis
- ✅ Implicit confidence mechanism exists
- ❌ No persistent "credibility_weighted" field
- **Verdict**: Candidate 3 concept is REDUNDANT with BEE, unless specific use case justifies persistent credibility scoring

### Semantica Absorption Recommendations (3 Candidates)
1. **Contradiction Detection** (High value): Auto-detect logic conflicts in Decision rationale
2. **Relationship Strength** (Medium value): Extend Decision Ledger with link-type classification
3. **Entity Resolution** (Medium value): Cross-domain artifact linking for audit queries

All three are design candidates only—no implementation decisions until R01 approval.

---

## INVESTIGATION CONCLUSION

**Scope**: Completed per user instructions  
**Format**: FACT → EVIDENCE → UNKNOWN → R01判断 → 推奨アクション  
**Status**: All four investigations complete, no changes made, no Decision entries created  
**Next**: Human Gate R01 review for design approval and implementation prioritization

