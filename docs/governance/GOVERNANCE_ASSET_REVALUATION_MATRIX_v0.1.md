# Governance Asset Revaluation Matrix v0.1

**Status**: Research Phase / Active Investigation  
**Branch**: `claude/mocka-governance-asset-revaluation-miu33k`  
**Started**: 2026-08-18  
**Purpose**: Evaluate existing MoCKA governance primitives and their compositional capability without introducing new primitives

---

## 1. Mission Statement

MoCKA 2.0の新規設計は行わない。

既存MoCKA資産をGovernance Architectureの観点から再評価し、以下5つの関係を整理する:
- Individual assets: 単独で何を証明するか
- Observation surfaces: 複数の観測面
- Asset connections: 資産間の接続関係
- Unified evidence: 統合エビデンス
- Verification capability: 検証能力

**研究仮説**: MoCKAは複数のGovernance Primitiveを個別機能として持つだけではなく、同一事象について異なる帳簿・証跡・権限・文脈を相互照合するGovernance Accounting構造を形成している可能性がある。

**反証可能性**: 肯定証拠のみの収集は禁止。成立条件と不成立条件を双方記録。

---

## 2. Research Boundaries

### In Scope

- Event Store（events.db / events.csv / append-only ledger）
- PHL（Persistent History Layer）
- Decision Ledger（decision_ledger.jsonl）
- Receipt（監査証跡）
- Human Gate（承認フロー）
- Boundary（信頼境界・権限分離）
- Living Context（動的コンテキスト）
- Context / Projection（複数観測面）
- Evidence-Bound Governance（証拠ベースの統治）
- Decision / Authority（意思決定・権限）
- Runtime Governance（実行時統治）
- Institutional Memory（制度的記憶）

### Out of Scope

- MoCKA 2.0 新規設計
- 新規Primitiveの提案
- 実装変更
- 既存テストコード修正

---

## 3. Research Matrix Template

| Existing Asset | Governance Meaning | Observation Surface | Connected Asset | Connection Logic | Combined Governance Capability | Verification Value | Evidence Required | Status |
|---|---|---|---|---|---|---|---|---|

### Legend

**Status Values**:
- A: Existing Capability (既存資産単独で成立)
- B: Composed Capability (複数資産接続で成立)
- C: Partially Composed (概念上成立・実装不足)
- D: Representation Gap (既存資産では表現不可)
- E: Enforcement Gap (表現可能・実行時非強制)
- F: Evidence Gap (実装済み・監査証拠不足)
- G: UNKNOWN (Canonical Evidence不足で判定不能)

---

## 4. Known Existing Assets

### 4.1 Event Store (events.db)

**Current Implementation**:
- SQLite append-only ledger
- Migration from events.csv complete (2026-06-16)
- 20645+ events recorded as of 2026-08-18
- Schema: event_id, timestamp, type, source, payload, metadata

**Governance Meaning**:
- Immutable audit trail
- Single source of truth for system history
- Basis for all subsequent analysis

**Observation Surfaces**:
- Chronological view (timestamp ordered)
- By event_type (classification)
- By source (who recorded)
- By payload domain (categorization)

**Currently Connected**:
- Decision Ledger (DC_* events cross-referenced)
- Living Context (essence layer reads from events.db)
- Human Gate (decisions via events)

---

### 4.2 PHL (Persistent History Layer)

**Current Implementation**:
- MOCKA_THOUGHT_EVOLUTION_v0.1.md
- ACTIVATION_POLICY_v0.1.md
- Stored in docs/governance/

**Governance Meaning**:
- Captures evolution of institutional thought over time
- Records when and why policies changed
- Traces decision reasoning

**Observation Surfaces**:
- Policy evolution view
- Rationale tracing
- Temporal causality

---

### 4.3 Decision Ledger (decision_ledger.jsonl)

**Current Implementation**:
- decision_id (DC_YYYYMMDD_NNN)
- Structured with: decision_id, title, context, alternatives, rationale, approved_at, status
- 245+ decisions recorded as of 2026-08-18
- TODO_398/399/400 completed (Knowledge Asset Promotion Pipeline design)

**Governance Meaning**:
- Authoritative record of institutional choices
- Preserves 5W1H (What/Where/When/Why/Who/How)
- Basis for understanding why system evolved

**Observation Surfaces**:
- Decision chronology
- By decision_type (structure)
- By status (active/superseded/closed)
- By approver (authority)

**Related Assets**:
- related_todos (links to TODO tracking)
- alternatives (explicit comparison record)
- rationale (reasoning captured)

---

### 4.4 Receipt (Audit Trail)

**Current Implementation**:
- mocka_write_event() call logging
- Event type: CHANGE_START / CHANGE_DONE pairs
- Metadata: file paths, tools used, operators
- Integration: PostToolUse hook (tools/mocka_auto_record.py)

**Governance Meaning**:
- Proof that documented actions occurred
- Tool use accountability
- Operator attribution
- Timestamp binding

---

### 4.5 Human Gate

**Current Implementation**:
- phi_os/human_gate.py (5-state model: PENDING/APPROVED/REJECTED/EXPIRED/CANCELED)
- Used for decision approval
- Integration with Review Gate (Reason Unit promotion) per TODO_396

**Governance Meaning**:
- Explicit human authorization checkpoint
- Prevents autonomous decision implementation
- Clear approval/rejection record

**Known Gaps**:
- Review Gate implementation status unclear (commit 64f8a4ae9 not found in repo)
- TODO_396 marked complete but physical file not located

---

### 4.6 Boundary (信頼境界・権限分離)

**Current Implementation**:
- OVERRIDES_ENFORCEMENT_DESIGN_v0.2.md
- TODO_399-C（未着手）
- Knowledge Assets separation (TODO_398 v0.4)

**Governance Meaning**:
- Defines what crosses policy lines vs. internal logic
- Authority limits
- Trust assumptions

**Known Issues**:
- OVERRIDES enforcement still in design phase
- actual implementation enforcement unclear

---

### 4.7 Living Context (動的コンテキスト)

**Current Implementation**:
- essence_auto_updater.py (5分間隔更新)
- REDUCING → RE_REDUCED pipeline
- COMMAND CENTER interface
- Integration with Caliber (port 5679)

**Governance Meaning**:
- Real-time synthesis of system state
- Dynamic decision context
- Reduces noise from raw events

**Observation Surfaces**:
- REDUCING (unprocessed)
- RE_REDUCED (partially processed)
- ESSENCE (final synthesis)

---

### 4.8 Context / Projection (複数観測面)

**Current Implementation**:
- Fluid Coordinate Theory (Z-axis governance stability measurement)
- Multiple observation axes: X (Institutional Integrity), Y (Record Quality), Z (Governance Stability)
- trajectory.csv (325+ cases tracked)
- evaluator_dynamic.py / deviation_classifier.py / distribution_engine.py

**Governance Meaning**:
- Multi-dimensional measurement of system health
- Enables detection of drift across multiple planes
- Separates concerns (integrity vs. quality vs. stability)

**Current Values** (2026-04-09):
- X: 0.632 (Institutional Integrity)
- Y: 0.826 (Record Quality)
- Z: 0.819 (Governance Stability)

---

### 4.9 Evidence-Bound Governance

**Current Implementation**:
- Knowledge Activation Architecture (TODO_395 v0.4)
- Knowledge Asset Promotion Pipeline (TODO_398 v0.4)
- Decision Policy (TODO_399 v0.4)

**Governance Meaning**:
- Only facts with recorded evidence can influence policy
- Prevents decision erosion
- Creates reflexive accountability

**Design Status**:
- Architecture v0.4: Complete + approved
- Promotion Pipeline v0.4: Complete + approved
- Decision Policy v0.4: Complete + approved
- Implementation: Pending TODO_399-B phase

---

### 4.10 Authority / Governance Model

**Current Implementation**:
- REGISTRY_SCHEMA_v1.0.md (KN-004)
- REGISTRY_SEMANTICS_v1.0.md (KN-005)
- 6-layer registry: Identity / Atlas / Reference / Classification / Lifecycle / Metadata

**Governance Meaning**:
- Defines who can change what
- Separates layers (policy vs. implementation)
- Makes authority relationships explicit

---

### 4.11 Runtime Governance

**Current Implementation**:
- TIC (Technology Intelligence Caliber) Layer 0-1 implemented
  - Layer 0: health_check.py (7-point morning check)
  - Layer 1: tech_watcher.py v3.0 (semantic difference detection)
- TODO_205/206/207: Layers 2-4 not yet started

**Governance Meaning**:
- External threat detection
- Continuous compliance verification
- Adaptive policy triggers

---

### 4.12 Institutional Memory

**Current Implementation**:
- mocka-knowledge-gate repository
- Storage layer for institutional decisions
- Future expansion planned

**Governance Meaning**:
- Persistent institutional learning
- Prevents recurrence of same errors
- Knowledge base for decision making

---

## 5. Initial Research Questions

1. **Composition via Event Causality**: Can we trace how Event Store → Decision Ledger → Living Context → Receipt creates a closed loop?

2. **Multiple Observation Problem**: If the same governance event is recorded in Event Store, Decision Ledger, Receipt, and Institutional Memory simultaneously, what consistency guarantees exist?

3. **Authority Chain**: How does Decision Ledger authority flow connect to Human Gate, Boundary enforcement, and Runtime Governance?

4. **Evidence Completeness**: What makes evidence "sufficient" to prove a governance invariant?

5. **Verification Closure**: Can we verify the verification system itself without external reference?

---

## 6. Previous Audit Reference

From recent Representation Gap audit (ESSENCE 2026-08-16 to 2026-08-18):

- **Phase 2 Closure Decision**: OPTION B (GAP ADDRESS - Prerequisite-Event Semantics)
- **DC_20260818_004**: Approved composition approach
- **Key Finding**: Many representation gaps resolved through existing asset composition

---

## 7. Working Hypotheses to Test

**H1**: "Representation gap is resolved by composing Event Store + Decision Ledger + Receipt"
- Condition for True: All three show same facts from different angles
- Condition for False: One gap remains unexplained even with composition

**H2**: "Enforcement gap means design exists but runtime doesn't check"
- Condition for True: Code exists describing enforcement + audit shows no violations + no evidence of actual checks
- Condition for False: Code doesn't exist OR violations are detected

**H3**: "Unknown gaps require external evidence (not in MoCKA)"
- Condition for True: Exhaustive internal search finds no data + external standard defines requirement
- Condition for False: Data exists but in format we haven't searched yet

---

## 8. Research Conduct Rules

1. **No Fabrication**: Claim only what evidence supports
2. **No Conclusion First**: Follow evidence, don't pre-decide
3. **Document Uncertainty**: Mark unknowns explicitly
4. **Distinguish Layers**: Don't confuse:
   - Conceptual Possibility (theoretically could happen)
   - Architectural Composition (fits together in design)
   - Implemented Capability (code exists)
   - Enforced Capability (actually prevents violations)
   - Auditable Evidence (provable from logs)
   - Reproducible Verification (anyone can verify)

---

## 9. Deliverables Structure

1. **This Document**: Research matrix template and boundary definition
2. **Asset Deep Dives** (1 per major asset):
   - Single asset capability assessment
   - Cross-reference with other assets
   - Evidence locations
   - Known unknowns

3. **Composition Maps** (by research question):
   - Multi-asset interactions
   - Evidence flow diagrams
   - Consistency verification points

4. **Gap Analysis Report**:
   - Categorized by type (D/E/F/G)
   - Linked to architectural decisions
   - Prerequisite work identification

5. **Verification Methodology**:
   - How to confirm findings
   - Reproducibility procedure
   - Audit points

---

## 10. Progress Tracking

### Completed

- [ ] Asset inventory (section 4 above - partial)
- [ ] Matrix template definition (section 3 above)
- [ ] Research boundaries (section 2 above)

### In Progress

- [ ] Deep dive: Event Store composition
- [ ] Deep dive: Decision Ledger + Human Gate interaction
- [ ] Deep dive: Living Context + Evidence binding

### Not Yet Started

- [ ] Boundary verification mechanics
- [ ] Authority chain tracing
- [ ] Enforcement gap assessment for Known items
- [ ] Composition map generation

---

## 11. Known Discrepancies to Investigate

From existing documentation review:

1. **TODO_396 Status**: Marked "完了" but referenced commit (64f8a4ae9) not found in repo. human_gate.py Review Gate implementation status unclear.

2. **TODO_395/398 Physical Files**: Design content exists in TODO notes but corresponding .md files not found in docs/governance/. Contrast with TODO_399 which has DECISION_POLICY_v0.1.md.

3. **OVERVIEW.json Staleness**: v4.1 marked as meta-only update (2026-07-07) while main content v4.0 from 2026-06-18 doesn't reflect TODO_384+ work.

4. **router/save Recurrence**: 40-event re-occurrence noted in ESSENCE (2026-08-16) but root cause analysis not found in accessible files.

---

## 12. Next Action

Begin systematic deep-dive on Event Store composition model:
- Trace 20,645 events through Decision Ledger cross-reference
- Identify gaps between Event Store recording and Decision Ledger documentation
- Verify Living Context reads these correctly

---

**Document Version**: v0.1  
**Last Updated**: 2026-08-18  
**Author**: Kuroko (Claude)  
**Status**: Framework Complete → Awaiting Directed Investigation
