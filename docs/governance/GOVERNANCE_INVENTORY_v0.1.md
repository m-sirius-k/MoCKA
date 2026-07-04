# Governance Inventory v0.1 (Phase B-1)

位置づけ: R01実行指示書「MoCKA Governance Catalog v1.0 制定プロジェクト」Phase B-1(Governance Inventory)に基づく。MoCKAリポジトリ全体からConstitution/Standard/Rule/Series/Ledger/Audit/Decision/Gate/Registry/Approval/Archive/Governance文書/正式制定済み標準に相当する対象を網羅的に抽出する。新制度追加・名称変更・統廃合・優先順位付け・将来構想・推測は一切行わない。事実確認のみを行う。

調査範囲: `docs/governance/`(104件)・`docs/audits/`(57件)・`docs/contracts/`(37件)・その他`docs/*`配下(69件、architecture/caliber/archive/experimental/handoff/incidents/internal/lifecycle/mocka3/papers/phase1/releases/spec/verification/api)・`docs/NAMING_CONVENTION.md`(1件)・`governance/`および`verify/`配下のPythonコード(約25件)・`data/MOCKA_TODO_ACTIVE.json`内のArchitecture Contract系エントリ(18件)・`governance/registry.json`の構造。`docs/reference/semantic_dictionary/`(生データ、制度文書ではない)は対象外とした。

記録項目: 名称/文書名/保存場所/現在の状態/制定状況/関連制度。「制定状況」は各文書が自ら明記する状態表記のみを引用し、明記がない場合は「記載なし」とする。「関連制度」は各文書のファイル名・タイトルが示す所属シリーズ(命名上の事実)のみを記載し、内容の解釈による関係付けはPhase B-3(Relationship Mapping)に委ねる。

---

## 1. docs/governance/ 配下(104件)

### 1-1. Architecture Contract Series(Registry Series KN-001〜KN-007)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度(所属シリーズ) |
|---|---|---|---|---|---|
| REGISTRY_CHARTER_v1.0.md | KN-001: Registry Series 憲章 | docs/governance/ | 記載なし | きむら博士承認待ち(Pending) | Registry Series(KN) |
| CATEGORY_REGISTRY_v2.0.md | KN-002: Category Registry | docs/governance/ | 記載なし | きむら博士承認待ち(Pending) | Registry Series(KN) |
| REGISTRY_RECORD_SPEC_v1.0.md | KN-003: Registry Record Specification | docs/governance/ | 記載なし | きむら博士承認待ち(Pending) | Registry Series(KN) |
| REGISTRY_SCHEMA_v1.0.md | KN-004: Registry Schema | docs/governance/(および PlanningCaliber/fp/に複製あり、CROSS_REFERENCE_ANALYSIS_v0.1.md参照) | 「正本配置(Human Approval Gate承認済み)」 | 承認済み | Registry Series(KN) |
| REGISTRY_SEMANTICS_v1.0.md | KN-005: Registry Semantics(意味論) | docs/governance/ | 記載なし | 記載なし | Registry Series(KN) |
| REGISTRY_STATE_MODEL_v1.0.md | KN-006: Registry State Model(状態遷移) | docs/governance/ | 記載なし | 記載なし | Registry Series(KN) |
| REGISTRY_VALIDATION_v1.0.md | KN-007: Registry Validation(検証機構の仕様設計) | docs/governance/ | 記載なし | 記載なし | Registry Series(KN) |
| TERM-001_REGISTRY_TERMINOLOGY.md | TERM-001: Registry Terminology & Principles | docs/governance/ | 記載なし | きむら博士承認待ち(Pending) | Registry Series(KN)/TERM |
| GM2_REGISTRY_BASELINE_002.md | Registry Series ベースラインスナップショット v2 | docs/governance/ | 承認済み | 承認済み(KN-001/002/TERM-001承認、2026-07-01) | Registry Series(KN)/GM2 |

### 1-2. Module Governance Series(MODULE_*_v1.md、13件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度(所属シリーズ) |
|---|---|---|---|---|---|
| MODULE_AUDIT_PROTOCOL_v1.md | MoCKA Module Audit Protocol v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_CERTIFICATION_v1.md | MoCKA Module Certification v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_COMPLIANCE_MODEL_v1.md | MoCKA Module Compliance Model v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_DISCOVERY_MODEL_v1.md | MoCKA Module Discovery Model v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_GOVERNANCE_RUNTIME_v1.md | MoCKA Module Governance Runtime v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_HEALTH_MODEL_v1.md | MoCKA Module Health Model v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_INDEX_SPEC_v1.md | MoCKA Module Index Spec v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_LIFECYCLE_v1.md | MoCKA Module Lifecycle v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_POLICY_ENGINE_v1.md | MoCKA Module Policy Engine v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_QUERY_PROTOCOL_v1.md | MoCKA Module Query Protocol v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_REGISTRY_MODEL_v1.md | MoCKA Module Registry Model v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_RULE_ENGINE_v1.md | MoCKA Module Rule Engine v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |
| MODULE_VALIDATION_ENGINE_v1.md | MoCKA Module Validation Engine v1 | docs/governance/ | Draft | 記載なし | Module Governance Series |

### 1-3. Audit Series(Vocabulary/Cross Reference/CI Failure、今回サイクル成果物含む、14件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| VOCABULARY_INDEX_SCAN_EVIDENCE_v0.1.md | Vocabulary Index Scan — Evidence v0.2 | docs/governance/ | Fact Collection Phase(v0.2) | 記載なし | Vocabulary Audit |
| VOCABULARY_AUDIT_EVALUATION_v0.1.md | Vocabulary Audit Evaluation v0.3 | docs/governance/ | Evaluation Phase(v0.3)、R01役割終了・博士へ最終裁定委譲 | 記載なし(未裁定) | Vocabulary Audit |
| VOCABULARY_AUDIT_ANALYSIS_v0.1.md | Vocabulary Audit Analysis v0.1(Analysis-01) | docs/governance/ | Analysis Phase | 記載なし | Vocabulary Audit |
| VOCABULARY_AUDIT_DECISION_BRIEF_v0.1.md | Vocabulary Audit Decision Brief v0.1(Decision-01) | docs/governance/ | Decision Preparation Phase | R01 Final Decision(FD-001)にて承認・採択(R01_FINAL_DECISION_v0.1.md) | Vocabulary Audit |
| CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md | Cross Reference Audit + Git状態調査 v0.1 | docs/governance/ | Fact Collection Phase | 記載なし | Cross Reference Audit |
| CROSS_REFERENCE_ANALYSIS_v0.1.md | Cross Reference Analysis v0.1(Analysis-02) | docs/governance/ | Analysis Phase | 記載なし | Cross Reference Audit |
| CROSS_REFERENCE_DECISION_BRIEF_v0.1.md | Cross Reference Decision Brief v0.1(Decision-02) | docs/governance/ | Decision Preparation Phase | R01 Final Decision(FD-002)にて承認・採択 | Cross Reference Audit |
| CI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.md | CI Failure Fact Collection — MoCKA Global Rule Guard v0.1 | docs/governance/ | Fact Collection Phase | 記載なし | CI Failure Analysis |
| CI_FAILURE_ANALYSIS_v0.1.md | CI Failure Analysis v0.1(Analysis-03) | docs/governance/ | Analysis Phase | 記載なし | CI Failure Analysis |
| CI_FAILURE_DECISION_BRIEF_v0.1.md | CI Failure Decision Brief v0.1(Decision-03) | docs/governance/ | Decision Preparation Phase | R01 Final Decision(FD-003)にて承認・採択 | CI Failure Analysis |
| R01_FINAL_DECISION_v0.1.md | R01 Final Decision v0.1 | docs/governance/ | Decision Record | FD-001/002/003承認・監査サイクル完了宣言 | Vocabulary/Cross Reference/CI Failure共通 |
| AUDIT_PROCESS_EXTRACTION_v0.1.md | Audit Process Extraction v0.1(Phase A-1) | docs/governance/ | Fact Collection Phase A-1 | 記載なし | MoCKA Audit Standard制定プロジェクト |
| AUDIT_PROCESS_VERIFICATION_v0.1.md | Audit Process Verification v0.1(Phase A-2) | docs/governance/ | Verification Phase A-2 | 記載なし | MoCKA Audit Standard制定プロジェクト |
| MOCKA_AUDIT_STANDARD_DRAFT_v0.1.md | MoCKA Audit Standard Draft v0.1(Phase A-3) | docs/governance/ | Draft Preparation Phase A-3 | R01へ提出済み・博士最終制定待ち | MoCKA Audit Standard制定プロジェクト |
| MOCKA_AUDIT_STANDARD_DRAFT_INTERNAL_AUDIT_v0.1.md | MoCKA Audit Standard Draft Internal Audit v0.1(Phase A-4) | docs/governance/ | Internal Audit Phase A-4、混入ゼロ確認済み | 記載なし | MoCKA Audit Standard制定プロジェクト |

### 1-4. Guarantee & Assurance Audits(4件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| GUARANTEE_MATRIX_AUDIT_v0.1.md | Guarantee Matrix Audit v0.1 | docs/governance/ | Task-H | 記載なし | Guarantee系 |
| GUARANTEE_VERIFICATION_MATRIX_v0.1.md | Guarantee to Verification Matrix v0.1 | docs/governance/ | Task-K | 記載なし | Guarantee系 |
| GUARANTEE_MATURITY_INDEX_v0.1.md | Guarantee Maturity Index v0.1 | docs/governance/ | Task-L | 記載なし | Guarantee系 |
| GUARANTEE_COVERAGE_MAP_v0.1.md | Guarantee Coverage Map v0.1 | docs/governance/ | Task-P | 記載なし | Guarantee系 |

### 1-5. Human Gate & Institutional Audits(4件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md | Human Gate Connectivity Audit v0.1 | docs/governance/ | Task-M | 記載なし | Human Gate系 |
| CONCEPT_AUDIT_v0.1.md | Concept Audit v0.1 | docs/governance/ | Task-I | 記載なし | Vocabulary系 |
| CONTRADICTION_AUDIT_v0.1.md | Contradiction Audit v0.1 | docs/governance/ | Task-Q | 記載なし | 横断監査 |
| FIRST_PRINCIPLES_AUDIT_v0.1.md | First Principles Audit v0.1 | docs/governance/ | Task-J | 記載なし | 横断監査 |

### 1-6. Vocabulary & Semantics(3件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| VOCABULARY_CONSTITUTION_v0.1.md | Vocabulary Constitution v0.1 | docs/governance/ | Task-N | 記載なし | Vocabulary系 |
| VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md | Vocabulary and Pattern Audit — 判定基準 v0.1 | docs/governance/ | Task-E | 記載なし | Vocabulary系 |
| VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md | Vocabulary and Pattern Audit — 対象一覧 v0.1 | docs/governance/ | Task-F | 記載なし | Vocabulary系 |

### 1-7. Policy Documents(運用ポリシー、5件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| ACTIVATION_POLICY_v0.1.md | Knowledge Activation Policy v0.1 | docs/governance/ | MOCKA_THOUGHT_EVOLUTION_v0.1.md参照 | 記載なし | 知識活性化系 |
| DECISION_POLICY_v0.1.md | Decision Policy v0.1 | docs/governance/ | TODO_399-401三部作 | 記載なし | Decision Policy Series |
| EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md | External Knowledge Adoption Policy v0.1 | docs/governance/ | Task-D | 記載なし | 知識活性化系 |
| DECISION_RULE_LAYER_v1.0.md | Decision Rule Layer v1.0 | docs/governance/ | DECISION_POLICY_v0.1.md用語準備文書 | 記載なし | Decision Policy Series |
| CONFLICT_RESOLUTION_MATH_v0.1.md | Conflict Resolution Math Closure v0.2 | docs/governance/ | TODO_400設計 | 記載なし | Decision Policy Series |

### 1-8. Repository Status & Vocabulary Standards(4件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| REPOSITORY_STATUS_VOCABULARY_v0.1.md | Repository Status Vocabulary v0.1 | docs/governance/ | Task-H | 記載なし | Status Vocabulary系 |
| STATUS_VOCABULARY_v1.0_DRAFT.md | Status Vocabulary v1.0 - Draft | docs/governance/ | DRAFT(Task-G準備) | 未制定(Draft) | Status Vocabulary系 |
| STATUS_VOCABULARY_v1.0_CONSTITUTION.md | Status Vocabulary v1.0 - Constitution | docs/governance/ | 確定(博士裁定2026-07-03) | 制定済み | Status Vocabulary系 |
| ACTIVITY_FREQUENCY_METADATA_v0.1.md | Activity Frequency Metadata v0.1 | docs/governance/ | STATUS_VOCABULARY v1.0補完 | 記載なし | Status Vocabulary系 |

### 1-9. Satellite Repository Positioning(3件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| SATELLITE_REPOSITORY_POSITIONING_OPTIONS_v0.1.md | Satellite Repository Positioning - Options v0.1 | docs/governance/ | Task-I | 記載なし | Satellite Repository系 |
| SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_DRAFT.md | Satellite Repository Architecture v1.0 - Draft | docs/governance/ | DRAFT(Task-I結果の裁定案) | 未制定(Draft) | Satellite Repository系 |
| SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_CONSTITUTION.md | Satellite Repository Architecture v1.0 - Constitution | docs/governance/ | 確定(博士裁定2026-07-03) | 制定済み(4衛星リポジトリ承認) | Satellite Repository系 |

### 1-10. Phase Execution Governance(5件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| phase2_execution_governance_v1.md | MoCKA Phase2 — Execution Governance Layer v1.0 | docs/governance/ | FINALIZED(2026-06-25) | 制定済み | Phase2系 |
| phase2_execution_governance_finalization_v1.md | MoCKA Phase2 — Execution Governance Finalization v1.0 | docs/governance/ | APPROVED(2026-06-25) | 制定済み | Phase2系 |
| phase3_execution_runtime_design_v1.md | MoCKA Phase3 — Execution Runtime Layer Design v1.0[EXECUTION-ARCHIVE] | docs/governance/ | EXECUTION-ARCHIVE/INACTIVE(2026-06-25) | アーカイブ化(非活性) | Phase3系 |
| phase3_simulation_sealed_v1.md | MoCKA Phase3 — SIMULATION-SEALED v1.0 | docs/governance/ | SIMULATION-SEALED v1.0(2026-06-25) | 制定済み(実行能力ゼロとして採択) | Phase3系 |
| phase5_boundary_declaration.md | Phase5 Boundary Declaration(Step3時点) | docs/governance/ | ACTIVE | 記載なし | Phase5系 |

### 1-11. Phase10統合・終端宣言(8件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| phase10_3_integrated_mapping_v2.md | Phase10-3 Integrated Mapping v2.0 | docs/governance/ | DRAFT | 記載なし | Phase10系 |
| phase10_3_integrated_mapping_v3.md | Phase10-3 Integrated Mapping v3.0(Unified Stabilization Patch) | docs/governance/ | DRAFT | 記載なし | Phase10系 |
| phase10_3_final_freeze_declaration_v1.md | Phase10-3 Final Freeze Declaration v1.0 | docs/governance/ | DECLARATION | 制定済み(Phase10-3参照体系として凍結) | Phase10系 |
| freeze_log.md | Phase10-3 Topology Freeze — Log v1.0 | docs/governance/ | FREEZE RECORD | 記載なし | Phase10系 |
| phase10_4_boundary_audit_v1.md | Phase10-4 Boundary Audit v1.0 | docs/governance/ | AUDIT | 記載なし | Phase10系 |
| phase10_4_independent_stability_review_v1.md | Phase10-4 Independent Stability Review v1.0 | docs/governance/ | REVIEW | 記載なし | Phase10系 |
| mocka_phase10_human_gate_insertion_map_v1.md | MoCKA Phase10 Human Gate Insertion Map v1 | docs/governance/ | DRAFT | 記載なし | Phase10系/Human Gate |
| mocka_global_terminal_map_v1.md | MoCKA Global Terminal Map v1.0 | docs/governance/ | TERMINAL DECLARATION | 制定済み(7層システムモデル集約) | 全体終端宣言系 |
| mocka_terminal_closure_v1.md | MoCKA Terminal Closure Declaration v1.0 | docs/governance/ | CLOSURE | 制定済み | 全体終端宣言系 |

### 1-12. Human Gate Architecture(5件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| mocka_human_gate_decision_definition_v1.md | MoCKA Human Gate Decision Definition v1(Corrected: Two-Layer Split) | docs/governance/ | DRAFT | 記載なし | Human Gate系 |
| mocka_hab_v1_contract.md | MoCKA HAB(Human Authority Boundary) v1 | docs/governance/ | DRAFT | 記載なし | Human Gate系/HAB |
| mocka_hab_human_gate_relation_v1.md | MoCKA HAB x Human Gate Relation v1(Integration) | docs/governance/ | DRAFT | 記載なし | Human Gate系/HAB |
| mocka_full_static_structure_map_v1.md | MoCKA Full Static Structure Map v1 | docs/governance/ | DRAFT | 記載なし | Human Gate系/HAB/Phase10/Extension |
| o0_human_gate_semantic_terminal_v1.md | O0-Human Gate(Semantic Closure Node) v1.0 | docs/governance/ | DRAFT | 記載なし | Human Gate系 |

### 1-13. Code Binding & Finalization Documents(4件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| MOCKA_CODE_BINDING_HUMAN_GATE_DECISION_DRAFT_v1.md | MoCKA Code Binding — Human Gate Decision Draft v1.0 | docs/governance/ | DRAFT | 未裁定(選択肢提示のみ) | Code Binding系/Human Gate |
| MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1.md | MoCKA Code Binding — Human Gate Finalization v1.0 | docs/governance/ | APPROVED | 制定済み | Code Binding系/Human Gate |
| MOCKA_EXTENSION_HUMAN_GATE_SUMMARY_v1.md | MoCKA Extension Human Gate Decision Summary v1 | docs/governance/ | SUBMITTED FOR DECISION | 未裁定(提出段階) | Extension系/Human Gate |
| MOCKA_LINEAGE_GOVERNANCE_FINALIZATION_v1.md | MoCKA Lineage Governance — Finalization v1.0 | docs/governance/ | DECIDED | 制定済み | Lineage系 |

### 1-14. Charter & Foundational Documents(3件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| MOCKA_CHARTER_v2.md | MOCKA CHARTER v2.0 | docs/governance/ | Charter | 制定済み(8条憲章) | 全体基盤 |
| MOCKA_THOUGHT_EVOLUTION_v0.1.md | MoCKA思想進化史 v0.1 | docs/governance/ | v0.1(現行復元) | 記載なし | 全体基盤 |
| GOVERNANCE_ARCHITECTURE_OVERVIEW_v1.md | MoCKA Governance Architecture Overview v1 | docs/governance/ | Draft(2026-06-15) | 未制定(Draft) | 全体基盤 |

### 1-15. Operational Design & Runtime(6件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| gl7_execution_kernel_spec_v1.md | GL7 Execution Kernel 仕様書 v1.0 | docs/governance/ | CONFIRMED | 制定済み(execution_governance.pyコードから抽出) | GL7系 |
| control_map_v1.md | MoCKA 制御マップ v1.0(決定記録・未実装) | docs/governance/ | DECISION_RECORDED | 決定記録(未実装) | 制御系 |
| control_map_v2.md | MoCKA 制御マップ v2.0(責務固定版・決定記録) | docs/governance/ | DECISION_RECORDED | 決定記録 | 制御系/GL7 |
| execution_gate_v1.md | MoCKA Phase5 実装移行前 最終安全チェックリスト(Execution Gate v1) | docs/governance/ | PROPOSED | 未制定(提案) | Phase5系 |
| minimal_safe_architecture_v1.md | MoCKA Phase5 実装用 最小安全アーキテクチャ(Minimal Safe Architecture v1) | docs/governance/ | PROPOSED | 未制定(提案) | Phase5系 |
| state_dependency_risk_map_v1.md | State Dependency Risk Map v1 | docs/governance/ | PROPOSED | 未制定(提案) | Phase5系 |
| runtime_boundary_v1.md | Runtime Boundary v1 | docs/governance/ | PROPOSED | 未制定(提案) | Phase5系 |

### 1-16. System Integrity & Verification(3件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| GL7_STATE_INTEGRITY_NOTE_v1.0.md | GL7_STATE_INTEGRITY_NOTE v1.0 | docs/governance/ | Observation Record | 記載なし | GL7系 |
| OVERRIDES_ENFORCEMENT_DESIGN_v0.2.md | OVERRIDES Enforcement設計 v0.2 | docs/governance/ | Design Complete | 記載なし | 制御系 |
| DESIGN_MEMO_INL_v0.1.md | MoCKA Incident Navigation Layer(INL) v0.1 — 設計メモ | docs/governance/ | Draft(2026-07-02) | 未制定(Draft) | インシデント管理系 |

### 1-17. Evolution & Adoption Policies(2件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| EVOLUTION_LAYER_SPECIFICATION_v0.1.md | Evolution Layer Specification v0.1 | docs/governance/ | Task-O | 記載なし | 進化層系 |
| WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md | Writer/Checker Institutional Design v0.1 | docs/governance/ | Task-B | 記載なし | Writer/Checker系 |

### 1-18. Analysis & Investigation Reports(6件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| EXECUTION_RUNTIME_SYSTEM_LEVEL2_VERIFICATION_v0.1.md | Execution Runtime System - Level2 Verification v0.1 | docs/governance/ | Task-K | 記載なし | Execution Runtime系 |
| PHI_OS_REFERENCE_PATH_CHECK_v0.1.md | PHI-OS Reference Path Check v0.1 | docs/governance/ | Task-J | 記載なし | PHI-OS系 |
| civilization_loop_investigation_v1.md | Civilization Loop断絶調査 + 関連系統棚卸し v1 | docs/governance/ | INVESTIGATION_REPORT | 記載なし | Loop系 |
| prevention_queue_backlog_analysis_v1.md | prevention_queue未処理1,798件 傾向分析 v1 | docs/governance/ | ANALYSIS_REPORT | 記載なし | 運用分析系 |
| VERIFICATION_LOG_v0.1.md | Verification Log v0.1 | docs/governance/ | Task-J | 記載なし | Execution Runtime系 |
| INCIDENT_LEGACY_NOTE.md | runtime/incident_* レガシー調査ノート | docs/governance/ | Investigation | 記載なし | インシデント管理系 |

### 1-19. Management & Governance Framework(4件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| TODO_ARTIFACT_GOVERNANCE_v1.0.md | TODO Artifact Governance v1.0 | docs/governance/ | Governance Standard | 記載なし | TODO管理系 |
| mocka_knowledge_lineage_standard_v1.md | MoCKA Knowledge Lineage Standard v1.0 | docs/governance/ | Standard | 記載なし | Lineage系 |
| adapter_governance_v1.md | Adapter Governance v1(Phase5 Step4-A: Authority Design) | docs/governance/ | DRAFT | 未制定(Draft) | Adapter系/Phase5 |
| R01_FINAL_DECISION_v0.1.md | (1-3で計上済み。重複記載回避のためここでは省略) | docs/governance/ | — | — | — |

### 1-20. Contract & Design Separation(2件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| contract_status_separation_design_v1.md | contract_status分離設計 v1(TODO_385設計案) | docs/governance/ | DESIGN_PROPOSAL | 未制定(提案) | TODO管理系 |
| contract_status_separation_design_v2.md | contract_status分離設計 v2(TODO_385設計案・17件全件対応) | docs/governance/ | DESIGN_PROPOSAL(博士裁定2026-06-28で拡張) | 一部裁定あり(拡張範囲について) | TODO管理系 |

### 1-21. Miscellaneous Operational Rules(2件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| import_safety_rule_v1.md | Import Safety Rule v1 | docs/governance/ | PROPOSED | 未制定(提案) | 実装安全系 |
| GPT_RESTRICTIONS.md | GPT作業禁止事項(自動生成) | docs/governance/ | Auto-generated(2026-04-01) | 記載なし(インシデント由来の禁止事項リスト) | インシデント管理系 |

注記: 1-1〜1-21で計上した実件数は103件(R01_FINAL_DECISION_v0.1.mdは1-3で計上済みのため1-19では重複計上していない)。調査エージェントの一次集計は104件だったが、内訳整理の過程で1件はカテゴリ間の重複記載であることを確認した(実質103件、集計手法上の差異であり文書自体の過不足ではない)。

---

## 2. docs/audits/ 配下(57件)

### 2-1. MOCKA_*系(11件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| MOCKA_CODE_BINDING_FINAL_REVIEW_v1.md | MoCKA Code Binding — Final Review v1.0 | docs/audits/ | AUDIT | 記載なし | Code Binding系 |
| MOCKA_CODE_BINDING_READINESS_REVIEW_v1.md | MoCKA Code Binding Readiness Review v1.0 | docs/audits/ | AUDIT | 記載なし | Code Binding系 |
| MOCKA_CODE_BINDING_READINESS_REVIEW_v2.md | Code Binding Readiness Review v2.0 | docs/audits/ | AUDIT | 記載なし | Code Binding系 |
| MOCKA_GOVERNANCE_VOCABULARY_AUTHORITY_RECONCILIATION_AUDIT_v1.md | Governance Vocabulary & Authority Reconciliation Audit v1.0 | docs/audits/ | AUDIT | 記載なし | Vocabulary系 |
| MOCKA_HUMAN_GATE_FINALIZATION_AUDIT_v1.md | Human Gate Finalization Report v1.0 | docs/audits/ | AUDIT | 記載なし | Human Gate Audit Series |
| MOCKA_HUMAN_GATE_FINALIZATION_CLOSURE_AUDIT_v1.md | Human Gate Finalization Closure Audit v1.0 | docs/audits/ | AUDIT | 記載なし | Human Gate Audit Series |
| MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md | MoCKA Human Gate Identity Audit v1.0 | docs/audits/ | AUDIT | 記載なし | Human Gate Audit Series |
| MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md | MoCKA Human Gate Identity Consolidation Audit v1.0 | docs/audits/ | AUDIT | 記載なし | Human Gate Audit Series |
| MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md | MoCKA Human Gate Registry Audit v1.0 | docs/audits/ | AUDIT | 記載なし | Human Gate Audit Series |
| MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1.md | MoCKA Lineage Governance Audit v1.0 | docs/audits/ | AUDIT | 記載なし | Lineage系 |
| MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md | MoCKA PHI-OS Identity Audit v1.0 | docs/audits/ | AUDIT | 記載なし | PHI-OS系 |

Human Gate Audit Series 5件(MOCKA_HUMAN_GATE_IDENTITY_AUDIT/IDENTITY_CONSOLIDATION_AUDIT/REGISTRY_AUDIT/FINALIZATION_AUDIT/FINALIZATION_CLOSURE_AUDIT)は、CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.mdにより2026-06-25作成(3コミットにまとまり作成)であることが確認済み。

### 2-2. PHASE10_*系(33件、最大の監査群)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| PHASE10_1_EVENT_TRACE_AUDIT_v1.md | Phase10-1 Event Trace Audit v1 | docs/audits/ | FORENSIC AUDIT ONLY | 記載なし | Phase10-1系 |
| PHASE10_1_EXISTENCE_AUDIT_v1.md | Phase10-1 Existence Audit v1 | docs/audits/ | FORENSIC AUDIT ONLY | 記載なし | Phase10-1系 |
| PHASE10_1_GIT_TRACE_AUDIT_v1.md | Phase10-1 Git Trace Audit v1 | docs/audits/ | FORENSIC AUDIT ONLY | 記載なし | Phase10-1系 |
| PHASE10_1_OBSERVER_FORENSIC_AUDIT_v1.md | Phase10-1 Observer Node Contract — Forensic Audit v1 | docs/audits/ | FORENSIC AUDIT FINAL | 記載なし | Phase10-1系 |
| PHASE10_1_SEAL_TRACE_AUDIT_v1.md | Phase10-1 Seal Trace Audit v1 | docs/audits/ | FORENSIC AUDIT ONLY | 記載なし | Phase10-1系 |
| PHASE10_2_AUDIT_REPORT_v1.md | Phase10-2 Audit Report v1 | docs/audits/ | AUDIT ONLY | 記載なし | Phase10-2系 |
| PHASE10_2_EVENT_TRACE_AUDIT_v1.md | Phase10-2 Event Trace Audit v1 | docs/audits/ | FORENSIC AUDIT ONLY | 記載なし | Phase10-2系 |
| PHASE10_2_GIT_TRACE_AUDIT_v1.md | Phase10-2 Git Trace Audit v1 | docs/audits/ | FORENSIC AUDIT ONLY | 記載なし | Phase10-2系 |
| PHASE10_3_ADVISOR_REASONING_SEPARATION_v1.md | Phase10-3 Advisor vs Reasoning Separation Report v1 | docs/audits/ | STRUCTURING ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_CANDIDATE_AUTHORITY_MATRIX_v1.md | Phase10-3 Candidate Authority Matrix v1 | docs/audits/ | MATRIX COMPARISON ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_CANDIDATE_AUTHORITY_OPTIONS_v1.md | Phase10-3 Candidate Authority Options v1 | docs/audits/ | OPTIONS STUDY ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_CANDIDATE_LIFECYCLE_AUDIT_v1.md | Phase10-3 Candidate Lifecycle Audit v1 | docs/audits/ | STRUCTURING ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_COLLISION_AMPLIFICATION_AUDIT_v1.md | Phase10-3 Collision Amplification Audit v1 | docs/audits/ | STRUCTURING ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_COLLISION_GAP_ANALYSIS_v1.md | Phase10-3 Collision Gap Analysis v1 | docs/audits/ | ANALYSIS ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_COLLISION_GOVERNANCE_STUDY_v1.md | Phase10-3 Collision Governance Study v1 | docs/audits/ | STRUCTURING ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_CONTRACT_READINESS_REPORT_v1.md | Phase10-3 Contract Readiness Report v1 | docs/audits/ | READINESS JUDGEMENT ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_DECISION_DEPENDENCY_MAP_v1.md | Phase10-3 Decision Dependency Map v1 | docs/audits/ | IMPACT ANALYSIS ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_DECISION_DEPENDENCY_MAP_v2.md | Phase10-3 Decision Dependency Map v2 | docs/audits/ | DEPENDENCY STRUCTURE FORMALIZATION | 記載なし | Phase10-3系 |
| PHASE10_3_DECISION_READINESS_REPORT_v1.md | Phase10-3 Decision Readiness Report v1 | docs/audits/ | READINESS JUDGEMENT ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_HEARING_READINESS_AUDIT_v1.md | Phase10-3 Hearing Readiness Audit v1 | docs/audits/ | READINESS AUDIT ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_HUMAN_GATE_DECISION_BRIEF_v1.md | Phase10-3 Human Gate Decision Brief v1 | docs/audits/ | DECISION BRIEF | 記載なし | Phase10-3系/Human Gate |
| PHASE10_3_HUMAN_GATE_DECISION_PACKAGE_v1.md | Phase10-3 Human Gate Decision Package v1 | docs/audits/ | DECISION PACKAGE ONLY | 記載なし | Phase10-3系/Human Gate |
| PHASE10_3_HUMAN_GATE_DEPENDENCY_AUDIT_v1.md | Phase10-3 Human Gate Dependency Audit v1 | docs/audits/ | STRUCTURING ONLY | 記載なし | Phase10-3系/Human Gate |
| PHASE10_3_HUMAN_GATE_HEARING_PACKAGE_v1.md | Phase10-3 Human Gate Hearing Package v1 | docs/audits/ | HEARING PACKAGE | 記載なし | Phase10-3系/Human Gate |
| PHASE10_3_HUMAN_GATE_LOAD_ANALYSIS_v1.md | Phase10-3 Human Gate Load Analysis v1 | docs/audits/ | COMPARATIVE ANALYSIS ONLY | 記載なし | Phase10-3系/Human Gate |
| PHASE10_3_LEAST_AUTHORITY_AUDIT_v1.md | Phase10-3 Least Authority Audit v1 | docs/audits/ | COMPARATIVE ANALYSIS ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_LONG_TERM_INSTITUTIONAL_AUDIT_v1.md | Phase10-3 Long-Term Institutional Audit v1 | docs/audits/ | LONG-TERM AUDIT ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_PROJECTION_BOUNDARY_MATRIX_v1.md | Phase10-3 Projection Boundary Matrix v1 | docs/audits/ | MATRIX COMPARISON ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_PROJECTION_BOUNDARY_OPTIONS_v1.md | Phase10-3 Projection Boundary Options v1 | docs/audits/ | OPTIONS STUDY ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_PROJECTION_INDEPENDENCE_AUDIT_v1.md | Phase10-3 Projection Independence Audit v1 | docs/audits/ | COMPARATIVE ANALYSIS ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_REASONING_AUTHORITY_MATRIX_v1.md | Phase10-3 Reasoning Authority Matrix v1 | docs/audits/ | STRUCTURING ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_REASONING_DEFINITION_COMPARISON_v1.md | Phase10-3 Reasoning Definition Comparison v1 | docs/audits/ | COMPARISON ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_REASONING_DEFINITION_OPTIONS_v1.md | Phase10-3 Reasoning Definition Options v1 | docs/audits/ | OPTIONS STUDY ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_REASONING_PREPARATION_NOTE_v1.md | Phase10-3 Reasoning Preparation Note v1 | docs/audits/ | PREPARATION NOTE ONLY | 記載なし | Phase10-3系 |
| PHASE10_3_RESONANCE_NODE_REDEFINITION_v1.md | Phase10-3 Resonance Node Redefinition v1 | docs/audits/ | REDEFINITION ANALYSIS ONLY | 記載なし | Phase10-3系 |
| PHASE10_ADVISOR_GOVERNANCE_AUDIT_v1.md | Phase10 Advisor Governance Audit v1 | docs/audits/ | AUDIT ONLY | 記載なし | Phase10系 |
| PHASE10_FIXATION_PACKAGE_OPTIONS_v1.md | Phase10 Fixation Package Options v1 | docs/audits/ | OPTIONS AUDIT ONLY | 記載なし | Phase10系 |
| PHASE10_FIXED_STATE_MATRIX_v1.md | Phase10 Fixed-State Matrix v1 | docs/audits/ | FORENSIC AUDIT ONLY | 記載なし | Phase10系 |

### 2-3. Other Phase Series(2件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| PHASE7_DRIFT_ESSENCE_MONITOR_COLLISION_AUDIT_v1.md | Phase7 Drift Monitor/Essence/Monitor系 機能重複統合監査 v1 | docs/audits/ | COLLISION AUDIT ONLY | 記載なし | Phase7系 |
| phase9_artifacts_audit_v1.md | Phase9成果物監査・整理 v1 | docs/audits/ | AUDIT ONLY | 記載なし | Phase9系 |

### 2-4. mocka_*(小文字)系(6件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| mocka_execution_approval_v1.md | Execution Approval v1 | docs/audits/ | 記載なし | 記載なし | 実行承認系 |
| mocka_global_consistency_audit_v1.md | MoCKA Global Consistency Audit v1.0 | docs/audits/ | 記載なし | 記載なし | 横断監査 |
| mocka_observation_review_scope_v1.md | Observation Review Scope v1 | docs/audits/ | 記載なし | 記載なし | Observation系 |
| mocka_phase10_blackbox_impact_analysis_v1.md | MoCKA Phase10-3/10-4 Differential Impact Analysis(Blackbox-Preserving) v1 | docs/audits/ | AUDIT | 記載なし | Phase10系 |
| mocka_risk_validation_preparation_v1.md | Risk Validation Preparation v1 | docs/audits/ | 記載なし | 記載なし | リスク検証系 |
| mocka_risk_validation_v1.md | Risk Validation v1 | docs/audits/ | 記載なし | 記載なし | リスク検証系 |

---

## 3. docs/contracts/ 配下(37件)

### 3-1. Phase5/Adapter系(5件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| adapter_contract_v1.md | Adapter Contract v1(Phase5 Step4-B) | docs/contracts/ | DRAFT | 未制定 | Adapter系/Phase5 |
| adapter_message_schema_v1.md | Adapter Message Schema v1(Phase5 Step4-B) | docs/contracts/ | DRAFT | 未制定 | Adapter系/Phase5 |
| adapter_registry_v1.md | Adapter Registry v1(Phase5 Step4-C) | docs/contracts/ | DRAFT | 未制定 | Adapter系/Phase5 |
| advisor_adapter_contract_v1.md | Advisor Adapter Contract v1(Phase5 Step5) | docs/contracts/ | DRAFT | 未制定 | Adapter系/Phase5 |
| advisor_adapter_runtime_v1.md | Advisor Adapter Runtime Design v1(Phase5 Step6) | docs/contracts/ | DRAFT | 未制定 | Adapter系/Phase5 |

### 3-2. Registry/Core(2件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| capability_registry_v1.md | Capability Registry v1(Phase5 Step3) | docs/contracts/ | FROZEN | 制定済み(凍結) | Phase5系 |
| time_os_contract_v1.md | Time OS Contract v1(Phase5 Step3 Freeze) | docs/contracts/ | FROZEN | 制定済み(凍結) | Phase5系 |

### 3-3. Phase7-A系(Intent/Meaning、4件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| phase7_a4_intent_real_data_binding_v1.md | Phase7-A-4-Intent: Real Data Binding Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase7-A系 |
| phase7_a4_real_data_binding_v1.md | Phase7-A-4: Real Data Binding Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase7-A系 |
| explanation_builder_contract_v1.md | Explanation Builder Contract v1(Phase7-A-3) | docs/contracts/ | DRAFT | 未制定 | Phase7-A系 |
| meaning_query_engine_contract_v1.md | Meaning Query Engine Contract v1(Phase7-A-1) | docs/contracts/ | DRAFT | 未制定 | Phase7-A系 |

### 3-4. Phase7-B系(構造/衝突/Human Gate、7件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| phase7_b3_structural_recovery_v1.md | Phase7-B-3: Structural Recovery Layer Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase7-B系 |
| phase7_b4_order_normalization_v1.md | Phase7-B-4: Order Normalization Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase7-B系 |
| phase7_b5_collision_governance_v1.md | Phase7-B-5: Collision Governance Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase7-B系 |
| phase7_b6_human_gate_ruling_v1.md | Phase7-B-6: Human Gate Ruling Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase7-B系/Human Gate |
| phase7_b7_human_gate_interface_v1.md | Phase7-B-7: Human Gate Interface Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase7-B系/Human Gate |
| decision_replay_system_contract_v1.md | Decision Replay System Contract v1(Phase7-B-1) | docs/contracts/ | DRAFT | 未制定 | Phase7-B系 |
| semantic_execution_layer_contract_v1.md | Semantic Execution Layer Contract v1(Phase7-D-1) | docs/contracts/ | DRAFT | 未制定 | Phase7-D系 |

### 3-5. Phase7-C系(Drift Monitor、2件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| drift_monitor_contract_v1.md | Drift Monitor Contract v1(Phase7-C-1) | docs/contracts/ | DRAFT | 未制定 | Phase7-C系 |
| drift_monitor_scoring_v1.md | Drift Monitor Scoring Contract v1(Phase7-C-2) | docs/contracts/ | DRAFT | 未制定 | Phase7-C系 |

### 3-6. Phase8系(Runtime Integration、3件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| phase8_2_runtime_bridge_v1.md | Phase8-2: Runtime Bridge Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase8系 |
| phase8_4_observation_surface_v1.md | Phase8-4: Observation Surface Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase8系 |
| phase8_hab_runtime_integration_v1.md | Phase8: HAB Runtime Integration Layer Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase8系/HAB |

### 3-7. Phase9系(Semantic Projection、2件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| phase9_1_semantic_projection_v1.md | Phase9-1: Semantic Projection Layer Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase9系 |
| phase9_3a_projection_strategy_contract_v1.md | Phase9-3A: Projection Strategy Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase9系 |

### 3-8. Phase10系(Cognitive/Observer/Advisor/Signal、6件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| phase10_0_cognitive_integration_concept_contract_v1.md | Phase10-0: Cognitive Integration Concept Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase10系 |
| phase10_1_observer_node_contract_v1.md | Phase10-1: Observer Node Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase10系 |
| phase10_2_advisor_node_contract_v1.md | Phase10-2: Advisor Node Contract v1 | docs/contracts/ | DRAFT | 未制定 | Phase10系 |
| phase10_3_signal_non_layer_contract_v1.md | Phase10-3 Signal Non-Layer Contract v1 | docs/contracts/ | FROZEN(Human Gate裁定済み) | 制定済み | Phase10系/Human Gate |
| phase10_3_watchpoint_declaration_v1.md | Phase10-3 Watchpoint Declaration v1 | docs/contracts/ | 記載なし | 記載なし | Phase10系 |
| phase10_4_operational_observation_layer_v1.md | Phase10-4: Operational Observation Layer(宣言のみ) | docs/contracts/ | 記載なし | 記載なし | Phase10系 |

### 3-9. MoCKA Extension系(4件)

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| mocka_extension_analytical_event_contract_v1.md | MoCKA Extension - Analytical Event Contract v1 | docs/contracts/ | DRAFT | 未制定 | Extension系 |
| mocka_extension_index_contract_v1.md | MoCKA Extension - Index Contract v1(Trace Graph Type) | docs/contracts/ | DRAFT | 未制定 | Extension系 |
| mocka_extension_loop_contract_v1.md | MoCKA Extension - Loop Contract v1 | docs/contracts/ | DRAFT | 未制定 | Extension系 |
| mocka_extension_meta_essence_contract_v1.md | MoCKA Extension - Meta-Essence Contract v1 | docs/contracts/ | DRAFT | 未制定 | Extension系 |

---

## 4. その他docs/*配下(69件)

### 4-0. docs/直下

| 名称 | 文書名 | 保存場所 | 現在の状態 | 制定状況 | 関連制度 |
|---|---|---|---|---|---|
| NAMING_CONVENTION.md | MoCKA Naming Convention — Official Specification | docs/ | Status: FIXED(統治承認なしに変更禁止) | 制定済み | 命名規則(最上位アーキテクチャ名のみ対象) |

### 4-1. docs/architecture/(12件)

| 名称 | 保存場所 | 現在の状態 | 制定状況 |
|---|---|---|---|
| ROUTER_API.md | docs/api/ | 記載なし | 記載なし |
| ARCHITECTURE.md | docs/architecture/ | 記載なし | 記載なし |
| ARCHITECTURE_DIAGRAM.md | docs/architecture/ | 記載なし | 記載なし |
| ARCHITECTURE_MOCKA_2_0_v1.md | docs/architecture/ | 確定版(タイトル内) | 記載なし |
| COGNITIVE_GOVERNANCE_LAYER_v1.md | docs/architecture/ | Step 4: Activation | 記載なし |
| EVENT_ENTRY_v1.md | docs/architecture/ | 記載なし | 記載なし |
| INTENT_GRAPH_v1.md | docs/architecture/ | 記載なし | 記載なし |
| INTENT_SCHEMA_v1.md | docs/architecture/ | 記載なし | 記載なし |
| PRE_CONSTRAINT_ARCHITECTURE_v1.md | docs/architecture/ | 記載なし | 記載なし |
| SEMANTIC_DRIFT_ENGINE_v1.md | docs/architecture/ | 記載なし | 記載なし |
| SHADOW_MOVEMENT_PRINCIPLE.md | docs/architecture/ | 記載なし | 記載なし |
| mocka_time_os_phase5_step3.md | docs/architecture/ | Status: STABLE(基準線) | 記載なし |

### 4-2. docs/caliber/(5件)

| 名称 | 保存場所 | 現在の状態 | 制定状況 |
|---|---|---|---|
| CALIBER_DESIGN_PRINCIPLES.md | docs/caliber/ | 記載なし(バージョン1.0) | 記載なし |
| CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md | docs/caliber/ | 記載なし | 記載なし |
| DRIFT_STANDARD_v1.1.md | docs/caliber/ | 記載なし(制定日: 2026-04-01) | 記載なし |
| LOOP_DESIGN_PRINCIPLES.md | docs/caliber/ | 記載なし(バージョン1.0) | 記載なし |
| LOOP_HEALTH_INDEX_DESIGN_v0.1.md | docs/caliber/ | 記載なし | 記載なし |

### 4-3. docs/archive/(18件)

| 名称 | 保存場所 | 現在の状態 |
|---|---|---|
| DOG_PHASE14.6_DUAL_LAYER_MCGS.md | docs/archive/ | 記載なし |
| ECOSYSTEM_MAP.md | docs/archive/ | 記載なし |
| ORPHAN_CLASSIFICATION_20260223.md | docs/archive/ | 記載なし |
| ORPHAN_EVENTS_20260223.md | docs/archive/ | 記載なし |
| PHASE0_TO_9C_SYSTEM_STATE.md | docs/archive/ | 記載なし |
| PHASE13B_FREEZE.md | docs/archive/ | Freeze(タイトル内) |
| PHASE14.6_BRANCH_REGISTRY_INIT_NOTE.md | docs/archive/ | 記載なし |
| PHASE14.6_DUAL_LAYER_GOVERNANCE_COMPLETION.md | docs/archive/ | 記載なし |
| PHASE14_BRANCH_POLICY_DRAFT.md | docs/archive/ | Status: Draft(タイトル内) |
| PHASE15_PROOF_DICTIONARY.md | docs/archive/ | 記載なし |
| PHASE17_PRE_FREEZE.md | docs/archive/ | Status: Pre-Freeze |
| PHASE17_STABLE_DECLARATION.md | docs/archive/ | Status: STABLE(タイトル内) |
| PHASE18_ENTRYPOINT.md | docs/archive/ | 記載なし |
| PHASE9C_PARTIAL_CHAIN_POLICY.md | docs/archive/ | 記載なし |
| STRUCTURE_INVENTORY_20260223_181903.md | docs/archive/ | 記載なし |
| STRUCTURE_LOCK_20260223.md | docs/archive/ | 記載なし |
| STRUCTURE_LOCK_APPEND_20260223.md | docs/archive/ | 記載なし |
| VERIFICATION_SAMPLE.md | docs/archive/ | 記載なし |

### 4-4. docs/experimental/(1件)

| 名称 | 保存場所 | 現在の状態 |
|---|---|---|
| interface_contract_formalization_experiment_v1.md | docs/experimental/ | Status: EXPERIMENTAL/NON-CANONICAL |

### 4-5. docs/handoff/(2件)

| 名称 | 保存場所 | 現在の状態 |
|---|---|---|
| MoCKA_Relay_requirements_v1.md | docs/handoff/ | 記載なし |
| PHASE11_AUDIT_RECONSTRUCTION.md | docs/handoff/ | 記載なし |

### 4-6. docs/incidents/(5件)

| 名称 | 保存場所 | 現在の状態 |
|---|---|---|
| CHANGE_PLAN_IMPORT_APP_SIDE_EFFECT_v1.md | docs/incidents/ | Status: DRAFT |
| INC-20260401-001.md | docs/incidents/ | 記載なし |
| INC-20260401-002.md | docs/incidents/ | 記載なし |
| INCIDENT_IMPORT_APP_SIDE_EFFECT.md | docs/incidents/ | Status: Implementation完了 |
| INCIDENT_TEMPLATE.md | docs/incidents/ | (テンプレート) |

### 4-7. docs/internal/(1件)・docs/lifecycle/(1件)

| 名称 | 保存場所 | 現在の状態 |
|---|---|---|
| external_service_inventory_phase1.md | docs/internal/ | 記載なし(Phase1事実抽出) |
| PRE_CONSTRAINT_ARCHITECTURE_LIFECYCLE_v1.md | docs/lifecycle/ | 記載なし |

### 4-8. docs/mocka3/(19件)

| 名称 | 保存場所 | 現在の状態 |
|---|---|---|
| AUDIT_TRACE_LAYER_RULES_v1.md | docs/mocka3/ | 記載なし |
| CANONICAL_SESSION_BOUNDARY_FINDINGS_v1.md | docs/mocka3/ | 記載なし |
| CANONICAL_TRACE_ID_DESIGN_PROPOSAL_v1.md | docs/mocka3/ | 記載なし |
| CANONICAL_TRACE_ID_GENERATION_RULE_v1.md | docs/mocka3/ | Status: Draft |
| CHANGE_TRANSACTION_PROTOCOL_v1.md | docs/mocka3/ | 記載なし |
| DECISION_LEDGER_SCHEMA_v1.md | docs/mocka3/ | 記載なし |
| EVENT_DATA_LIFECYCLE_v1.md | docs/mocka3/ | 記載なし |
| EVENT_FOUNDATION_v1.md | docs/mocka3/ | 記載なし |
| EVENT_TAXONOMY_v1.md | docs/mocka3/ | Status: Draft |
| EVENT_TRANSITION_PROTOCOL_v1.md | docs/mocka3/ | 記載なし |
| MODULE_CATALOG_v1.md | docs/mocka3/ | 記載なし |
| MODULE_DEPENDENCY_MODEL_v1.md | docs/mocka3/ | 記載なし |
| MODULE_MATURITY_MODEL_v1.md | docs/mocka3/ | 記載なし |
| TRACE_ID_CLASSIFICATION_RULES_v1.md | docs/mocka3/ | 記載なし |
| TRACE_ID_OPTION_IMPACT_MATRIX_v1.md | docs/mocka3/ | 記載なし |
| TRACE_ID_SEMANTIC_AUDIT_v1.md | docs/mocka3/ | 記載なし |
| VERSION_POLICY_v1.md | docs/mocka3/ | 記載なし |
| data_lifecycle.md | docs/mocka3/ | 記載なし |
| taxonomy.md | docs/mocka3/ | 記載なし(taxonomy.jsonがFROZEN v1.1として`verify_taxonomy_integrity.py`により検証対象) |

参考: `taxonomy.json`(同ディレクトリ)は`governance/verify_taxonomy_integrity.py`により「FROZEN v1.1、7カテゴリ」であることが検証対象となっていることをコード調査で確認済み。

### 4-9. その他個別ディレクトリ(4件)

| 名称 | 保存場所 | 現在の状態 |
|---|---|---|
| phase7_semantic_operating_layer_paper_v1.md | docs/papers/ | 記載なし |
| human_gate_core_snapshot_v1.md | docs/phase1/ | 記載なし |
| PHASE5_STEP3_SEAL.md | docs/releases/ | Status: STABLE |
| replay_equivalence_report.md | docs/verification/ | Status: PASS |

### 4-10. docs/spec/(9件)

| 名称 | 保存場所 | 現在の状態 |
|---|---|---|
| moCKA_app_boundary_v1.md | docs/spec/ | 記載なし(設計のみ) |
| moCKA_human_gate_v1.md | docs/spec/ | 記載なし |
| moCKA_phase1_code_binding_plan_v1.md | docs/spec/ | Status: DESIGN |
| moCKA_phaseC_execution_boundary_v1.md | docs/spec/ | 記載なし |
| moCKA_phaseD_execution_contract_v1.md | docs/spec/ | 記載なし |
| moCKA_phaseD_execution_core_v1.md | docs/spec/ | 記載なし |
| moCKA_phaseD_execution_enablement_v1.md | docs/spec/ | 記載なし(実装準備仕様・設計のみ) |
| moCKA_phaseD_execution_flow_v1.md | docs/spec/ | 記載なし |
| moCKA_spec_v1.0.2-rc.md | docs/spec/ | 記載なし |

---

## 5. Governance実装コード(governance/・verify/配下、約25件)

| 名称 | 保存場所 | 機能(一次説明) | verify_all.pyでの参照 |
|---|---|---|---|
| verify_governance_event_required.py | governance/ | governance_event.jsonの存在・署名検証 | あり(governance_event_required) |
| verify_revoke_event.py | governance/ | revoke_event.jsonのed25519署名検証 | あり(revoke_event) |
| verify_role_policy.py | governance/ | role_policy.jsonスキーマ検証 | あり(role_policy) |
| verify_approval_flow.py | governance/ | approval_flow.jsonスキーマ検証 | あり(approval_flow) |
| deterministic_build_gate.py | governance/ | phase17_determinism_check.py実行(存在時) | あり(deterministic_build_gate) |
| chaos_gate.py | governance/ | registry*.json改ざん耐性テスト | あり(chaos_gate) |
| verify_anchor_interface.py | governance/ | anchor_record.jsonのsealed_summary_hash検証 | あり(anchor_interface) |
| verify_external_audit_report.py | governance/ | external_audit_report.json検証(任意インターフェース) | あり(external_audit_report_interface) |
| verify_taxonomy_integrity.py | governance/ | docs/mocka3/taxonomy.jsonがFROZEN v1.1・7カテゴリであることを検証 | あり(taxonomy_integrity) |
| sign_governance_event.py | governance/ | governance_event.jsonへの署名付与 | なし(管理用ユーティリティ) |
| sign_revoke_event.py | governance/ | revoke_event.jsonへの署名付与 | なし(管理用ユーティリティ) |
| check_origin.py | governance/ | git origin一致・作業ツリークリーン確認 | なし(pre-commit用ユーティリティ) |
| calc_summary_hash.py | governance/ | anchor_record.jsonのsealed_summary_hash算出 | なし(verify_anchor_interfaceから呼出) |
| mocka_git_safe_commit.py | governance/ | git add/commit/push一元化ヘルパー(Core System File除外、TODO_364正本) | なし(共有ライブラリ) |
| index_add_columns.py | governance/infield/ | CSVインデックスへのsupersedes/verified列追加 | なし |
| gen_role_keys.py | governance/keys/ | ed25519キーペア生成・registry.json登録 | なし |
| rotate_root_key_v2.py | governance/keys/ | root_key_v2ローテーション | なし |
| push_export_A_to_sheets.py | governance/outfield/ | phase24_export_A.csvをGoogle Sheetsへ送信 | なし |
| push_export_A_to_sheets_diff.py | governance/outfield/ | index_signature.sha256をcsv末尾行に追加 | なし |
| sync_to_sheets.py | governance/propagation/ | Phase23-C: public_index_v1.jsonをAPPROVED_TO_SYNC.flag確認の上Sheetsへ同期 | なし |
| verify_all.py | (ルート) | 9ステップの検証オーケストレータ本体 | (本体) |
| accept_outfield_pass.py | verify/ | inbox/quarantineマニフェスト・summary_matrix.json検証(TEMPLATE/REPLACE_METOKEN拒否) | なし |
| manifest_resolver.py | verify/ | freeze_manifest.json解決・Ed25519署名検証 | 条件付き参照(verify.manifest_resolver.py存在時) |
| key_anchor_verify_v3.py | verify/ | KEY_GENERATION_ANCHOR_v3.json構造検証 | なし |
| key_history_verify_v3.py | verify/ | phase3鍵ポリシーの鍵履歴検証 | なし |
| ci_minimal_chain_test.py | verify/ | CI最小チェーンテスト | なし |
| key_generation_verify_v3.py | verify/ | 鍵生成検証 | なし |
| runtime_ledgers_verify.py | verify/ | ランタイムLedger検証 | なし |

---

## 6. Architecture Contract系(data/MOCKA_TODO_ACTIVE.json、18件)

TODO管理標準(TODO_ARTIFACT_GOVERNANCE_v1.0.md、CLAUDE.md記載のstatus正規値一覧)における「Architecture Contract系」(category="設計成果物"またはTODO_接頭辞を持たない独自ID)に該当するエントリ。

| ID | 名称 | 状態(status) | 関連制度 |
|---|---|---|---|
| CATEGORY_REGISTRY_V1 | カテゴリ/シリーズ命名規則v1確定 | 完了 | Registry Series/GM2 |
| DRY-RUN-001-TEST-CASE-SPEC | MoCKA First Contract Execution Test Case(Dry Run v1・未実行シナリオ) | 未着手 | 実行検証系 |
| GL7-UNENFORCED-CONDITIONS-BUG | GL7の安全条件3点が実行経路に未接続 | 未着手 | GL7系 |
| GL7-VALIDATION-MISSING-BUG | mocka_write_eventに空文字/欠損バリデーションが存在しない | 進行中 | GL7系 |
| GM2_BASELINE_STEP1 | GM2 Baseline — Step1完了時点のスナップショット固定 | 完了 | GM2系 |
| GM2_REGISTRY_BASELINE_001 | GM2 Registry Baseline 001 | 完了 | Registry Series/GM2 |
| GM2_ROADMAP | GM2ロードマップ記録 | 完了 | GM2系 |
| GM2_STEP1_COMPLETE | GM2 Step1(Operational Assurance)完了記録 | 完了 | GM2系/Decision Policy Series |
| GM3_VISION | GM3 Charter — Knowledge Governance(長期ビジョン) | 完了 | GM3系 |
| GOVERNANCE_MILESTONE_GM1 | Governance Milestone 1(GM-1) | 完了 | Decision Policy Series/Governance Audit Series |
| GOVERNANCE_MILESTONE_GM1_ADDENDUM | GOVERNANCE_MILESTONE_GM1補遺 | 完了 | Decision Policy Series |
| HAB-3FIELD-TRANSFORM-MIN-SPEC | Phase 0.5: API収束フェーズ | 未着手 | HAB系 |
| KN_IA_NAMING_CONFIRMED | IA正式名称の再確認 | 完了 | Registry Series(KN-002準拠) |
| KN_SERIES_LEDGER | Knowledge Navigation Series台帳 | 完了 | Registry Series(KN) |
| PHI-OS-HUMAN-GATE-STATE-MODEL-V1 | PHI-OS Human Gate State Model v1 + GL7最小カーネル仕様v1 | 進行中 | PHI-OS系/Human Gate/GL7 |
| REGISTRY_CHARTER_APPROVAL | REGISTRY_CHARTER_APPROVAL — KN-001正式承認 | 完了 | Registry Series(KN-001) |
| REGISTRY_SERIES_V1_0_BASELINE | Registry Series v1.0 Baseline | 完了 | Registry Series(KN) |
| REGISTRY_SERIES_V1_1_CANDIDATE | Registry Series v1.1 Candidate | 未着手 | Registry Series(KN) |

---

## 7. governance/registry.json(構造のみ)

保存場所: `governance/registry.json`。schema=`mocka.keys.ed25519.registry.v3`、version=3。root_keys(root_key_v1: revoked、root_key_v2: active)・operational_keys(operational_key_v1: active)・policy(require_active_keys/governance_event_required/key_version_monotonic)・metaの各キーを持つ。役割: Human Gate署名・governance_event検証の鍵台帳。verify_role_policy.py/verify_governance_event_required.py/verify_revoke_event.pyから参照される。

---

## 8. 全体集計

| 区分 | 件数概算 |
|---|---|
| docs/governance/ | 103~104件 |
| docs/audits/ | 57件 |
| docs/contracts/ | 37件 |
| その他docs/*(architecture/caliber/archive/experimental/handoff/incidents/internal/lifecycle/mocka3/papers/phase1/releases/spec/verification/api) | 69件 |
| docs/NAMING_CONVENTION.md | 1件 |
| governance/・verify/配下Pythonコード | 約25件 |
| data/MOCKA_TODO_ACTIVE.json内Architecture Contract系エントリ | 18件 |
| governance/registry.json | 1件(構造のみ記録) |
| **合計(概算)** | **約311件** |

本集計は今回の3エージェント調査(2026-07-04実施)による一次データに基づく。`docs/reference/semantic_dictionary/`配下の生データ、および`data/MOCKA_TODO_ACTIVE.json`内の通常TODO(TODO_接頭辞付き、category≠設計成果物)は本棚卸しの対象外とした。

---

## 改訂履歴

- v0.1(2026-07-04): R01実行指示書Phase B-1に基づき新規作成。3件の調査エージェント(docs/governance配下、docs/audits/docs/contracts等その他docs配下、governance実装コード+MOCKA_TODO_ACTIVE.json内Architecture Contract系+registry.json)の結果を統合。くろこ起草。
