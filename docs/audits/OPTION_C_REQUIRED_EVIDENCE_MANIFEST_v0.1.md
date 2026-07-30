# Option C Required Evidence Manifest v0.1

Status: 必要資料の一覧化のみ（内容の推測・代替記述は行わない）
Date: 2026-07-30
記録者: 執行官Claude（くろこ、Cloud session）
関連: OPTION_C_EVIDENCE_AVAILABILITY_AUDIT_v0.1.md

本文書は、当初指示のTask 1〜4を実施するために本セッションが実際に閲覧する必要がある一次資料を列挙する。
各文書について、必要理由・使用目的・監査対象（元のTask 1〜4のどれに使うか）を記載する。
文書の内容そのものは記載しない（存在しないため）。

---

## 1. 既に本セッションで閲覧可能な一次資料（参考、収集不要）

```
PHI_OS_CONSTITUTION_v1.md
MEANING_AUTHORITY_v1.md
docs/audits/MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md
phi_os/event_gate.py 他phi_os/配下の実装コード一式
Decision Ledger: DC_20260730_010 / DC_20260729_001 / DC_20260730_009（全文）
Event Ledger: 該当CHANGE_START/CHANGE_DONEの要約（short_summary/why_purpose/after_state）
```

---

## 2. 収集が必要な一次資料

### 2.1 JARVIS化ロードマップ系（S03〜S05・P2系、2026-07-29作成）

| 文書 | 必要理由 | 使用目的 | 監査対象 |
|---|---|---|---|
| PHI_MEMORY_ARCHITECTURE_v1.0.md（S03） | Jarvis化ロードマップPhase J1本体。Memory Layer 4分類・Future Jarvis Integration章を含む | Memory層とSequence Controller/Evidence Pipelineとの接続確認 | Task 1 |
| PHI_MEMORY_ARCHITECTURE_DESIGN_SCOPE_v0.1.md | S03の前段Scope文書 | S03の前提・スコープ確認 | Task 1 |
| PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md（S04） | Sequence ControllerのDesign Scope。Future Jarvis Runtime Connection章を含む | Sequence Controllerの責務境界確認 | Task 1, Task 3 |
| PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md（S05） | Sequence Controller Architecture本体。MoCKAとの境界（次に何をするか vs 許可・証拠確認）を規定 | Option C RunnerがSequence Controllerの判断領域を侵害していないかの確認 | Task 1, Task 2 |
| PHI_MODULE_INTERFACE_CONTRACT_v0.1.md | Module Interface契約 | Runner/Write ClientがModule Interfaceと整合するかの確認 | Task 1 |
| PHI_SEQUENCE_STATE_MODEL_v1.0.md | 状態遷移モデル（S07遷移、Forbidden Transition Handling等） | Runtime Layer Mappingの依存関係確認 | Task 3 |
| PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md | Memory Access Governance | Runnerの記録経路がAccess Control Policyに反しないかの確認 | Task 1 |
| PHI_HUMAN_GATE_INTEGRATION_MODEL_v1.0.md | Human Gate統合モデル | Option C RunnerがHuman Gate境界を自動で越えていないかの確認 | Task 2 |
| PHI_RUNTIME_SIMULATION_SCOPE_v0.1.md（Phase I） | Runtime Simulationの範囲定義 | Runtime層一覧化の基礎 | Task 3 |
| PHI_RUNTIME_BINDING_ARCHITECTURE_v1.0.md（Phase II） | Runtime Binding Architecture | 各Runtime層の入力・出力・依存関係の一次情報 | Task 3 |
| PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md（P2-02） | Module Adapter仕様 | （Module Adapterとの整合）確認 | Task 1 |
| PHI_STATE_TRANSITION_RUNTIME_DESIGN_v1.0.md（P2-03） | 状態遷移Runtime設計 | Runtime層の遷移責務確認 | Task 3 |
| PHI_EVIDENCE_RUNTIME_PIPELINE_v1.0.md（P2-04） | Evidence Runtime Pipeline。Input〜Memoryの経路定義 | （Evidence Pipelineとの整合）確認 | Task 1, Task 3 |

### 2.2 JARVIS構想・Deferred境界系

| 文書 | 必要理由 | 使用目的 | 監査対象 |
|---|---|---|---|
| PHI_OS_IDENTITY_COMPARATIVE_ANALYSIS_DRAFT_v0.1.md | DC_20260729_001が対象とした原本ドラフト | Deferred裁定の対象範囲の正確な確認 | Task 2 |
| JARVIS_CONCEPT_REEVALUATION_REPORT_v0.1.md | DC_20260729_001の保留理由再評価結果（継続保留） | Option C設計が保留理由の再解消・再燃に影響していないかの確認 | Task 2 |
| PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1.md | Jarvis化ロードマップとPHI-REG-04の接続点、J1〜J5ロードマップ記載 | ロードマップ全体像とOption Cの位置関係確認 | Task 1, Task 4 |

### 2.3 PHL Stage 1 / Option C系（2026-07-30作成）

| 文書 | 必要理由 | 使用目的 | 監査対象 |
|---|---|---|---|
| PHL_STAGE1_HEALTH_CHECK_RUNNER_DESIGN_v0.1.md | Option A/B/C選択の原設計文書（Q-1） | Option C採用の前提・却下されたOption A/Bの詳細確認 | Task 2, Task 4 |
| PHL_STAGE1_IMPLEMENTATION_PATH_ANALYSIS_v0.1.md | DC_20260730_010のrelated_documents | Option C実装経路の前提確認 | Task 1 |
| M1B_PHASE_PB_RUNTIME_PATH_ANALYSIS_v0.1.md | DC_20260730_010のrationaleが参照する既存パターン（Phase P-B/M1-B） | Option Cが既存確立パターンと本当に整合するかの確認 | Task 1, Task 4 |
| PHL_STAGE1_RUNNER_OPTION_C_ARCHITECTURE_v0.1.md | Option Cアーキテクチャ本体（コンポーネント構成・データフロー・境界定義・例外処理） | Task 1〜4すべての中核資料 | Task 1, 2, 3, 4 |
| PHL_STAGE1_RUNNER_IO_SPEC_v0.1.md | Runner I/O仕様（HC-1〜HC-4、Success/Failure等） | Runtime Layer MappingのRunner Runtime入出力確認 | Task 3 |
| PHL_STAGE1_EVIDENCE_PAYLOAD_SPEC_v0.1.md | Evidence Payload必須9項目 | mocka_write_eventスキーマとの整合確認 | Task 1, Task 3 |
| PHL_STAGE1_OPTION_C_IMPACT_ANALYSIS_v0.1.md | RC-011・MoCKA・Event Ledgerへの影響分析、Phase P-Bとの共通化可能性 | Task 4（Runtime Infrastructure化の妥当性）の直接材料 | Task 4 |

### 2.4 コード実体

| 対象 | 必要理由 | 使用目的 | 監査対象 |
|---|---|---|---|
| relay_client.py（RC-011） | Option C設計内で繰り返し参照される既存コンポーネント本体 | （RC-011は無変更）という設計文書上の記述の実コード照合 | Task 1, Task 4 |

---

## 3. 収集経路についての注記

収集経路（Local Windows環境からの貼り付け、本セッションへのファイル添付、リポジトリへのcommit/push等）
については本文書では決定しない。収集経路の選択はREPOSITORY_DIVERGENCE_REPORT_v0.1.mdおよび
OPTION_C_AUDIT_RESUMPTION_PLAN_v0.1.mdで扱う。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-30 | 0.1 | 初版。Task A〜D切替指示に基づき作成。 |
