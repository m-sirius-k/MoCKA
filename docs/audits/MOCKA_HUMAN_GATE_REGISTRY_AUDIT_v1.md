# MoCKA Human Gate Registry Audit v1.0

**Status:** AUDIT
**目的:** 既存のHuman Gate Identity Audit / Identity Consolidation Auditの結果を正式な識別台帳として整理し、今後のKnowledge LineageおよびCode Bindingでの名称衝突を防止する。
**実装・新規実装・リネーム・新規モジュール作成:** 禁止。本文書は監査文書のみ。
**入力文書:** [[MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1]] / [[MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1]] / [[mocka_human_gate_decision_definition_v1]] / [[o0_human_gate_semantic_terminal_v1]] / [[moCKA_human_gate_v1]] / PHASE10_3関連監査群 / [[MOCKA_CODE_BINDING_HUMAN_GATE_DECISION_DRAFT_v1]] / [[MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1]]

---

## 第1部 Human Gate Registry

| Registry ID | Name | Classification | Origin | Current Status | Primary Responsibility |
|---|---|---|---|---|---|
| HG-REG-01 | `phi_os/human_gate.py`（PHI-OS Human Gate State Model v1） | Approval State Machine | PHI-OS Phase3移行プロジェクト（`docs/governance/control_map_v2.md`系列） | 実装済み。HTTP経路未配線（`human_gate_bp`は`app.py`に未登録）。`migrate_prevention_queue.py`からの一度限り移行呼び出しのみ実行実績あり（`human_gate_events`テーブルに1776件、うち1768件PENDING停止中）。 | リクエスト承認の状態追跡（PENDING/APPROVED/REJECTED/EXPIRED/CANCELED）をイベントソーシングで保持する汎用ワークフロー。 |
| HG-REG-02 | `semantic/query_engine/human_gate.py` + `human_gate_interface.py`（Human Gate Ruling v0） | Semantic Ruling | Phase7-B-5 `GovernedCollisionRecord`（`phase7_b5_collision_governance_v1.md`） | Phase7-B-6/B-7契約に基づく最小スケルトンのみ実装済み。Execution層・app.pyとは無関係に独立動作。 | `GovernedCollisionRecord`（矛盾記録）に対する裁定（accept/reject/defer/split）を行い、「矛盾の意味的分岐点を固定する」装置。承認経路ではなく矛盾保存の意味論。 |
| HG-REG-03 | Phase C Human Gate Spec（`docs/spec/moCKA_human_gate_v1.md`） | Governance Gate | Phase C設計シリーズ（IR→Execution境界の確立、`moCKA_spec_v1.0.2-rc.md`由来） | 設計のみ、実装ゼロ。`moCKA_phase1_code_binding_plan_v1`のHuman Gate Core候補がこの系列最初の実コード化案として参照中。 | IR/Spec LayerとExecution Layer（app.py）の間に位置する「唯一の承認経路」。承認3段階（observation review/risk validation/execution approval）を定義する制度仕様。 |
| HG-REG-04 | Phase10-3 Human Gate（A6 Human Gate / Human Gate Finalization系、`mocka_human_gate_decision_definition_v1.md`を中心とする文書群） | Governance Gate | Phase10-Stasis「自律行動追加禁止」原則との矛盾指摘（[[feedback_flag_autonomy_risk_in_governance_design]]に記録済みの経緯）から2層分離へ修正された制度設計 | 制度として確定済み（DRAFT、pre-authorization state継続中、未ACTIVE）。実コードは存在しない。 | Human Gate Core（自動評価・判断材料生成のみ・裁定値を返さない）とHuman Gate Finalization（博士のみ、APPROVE/HOLD/REJECT/DEFER確定）の2層分離による制度核としての最終裁定点。 |
| HG-REG-05 | O0 Human Gate（`docs/governance/o0_human_gate_semantic_terminal_v1.md`） | Other（観測終端、権限・裁定機能を明示的に持たない） | A6 Human Gate定義タスク提示時に名称衝突をClaudeが指摘、博士が別系統ノードと確定 | DRAFT、未実装、ランタイム未配線。`mocka_phase10_human_gate_insertion_map_v1.md`等にHG-REG-04とのdual-node構造として記載。 | O0観測層の終端ノード。出力は`closure_tag`のみで`decision`は出力しない。HG-REG-04（A6 Human Gate）とは文書内で明示的に別系統と宣言済み。 |

**所見:** 「Human Gate」という1つの名前が、Approval State Machine（HG-REG-01）・Semantic Ruling（HG-REG-02）・Governance Gate（HG-REG-03/04）・Other（HG-REG-05）の4種類の分類にまたがって使用されている。HG-REG-03とHG-REG-04は同一の制度的Human Gate概念（A6 Human Gate）の異なる側面（HG-REG-03=Execution境界での配置位置、HG-REG-04=裁定権限の構造）である。

---

## 第2部 Identity Mapping

| 比較対 | 関係 | 理由 |
|---|---|---|
| HG-REG-01 ⇄ HG-REG-03/04 | **Related Concept** | 「人間の承認を記録する」という機能領域は重なるが、権限保証の有無・語彙（PENDING/APPROVED系 vs APPROVE/HOLD/REJECT/DEFER系）・対象範囲が異なるため同一概念とは言えない。 |
| HG-REG-02 ⇄ HG-REG-03/04 | **Independent Concept** | 裁定の意味論が正反対。HG-REG-02は「矛盾を保存する」層、HG-REG-03/04は「実行を許可する」層。同じ語を使いながら方向性が逆転している。 |
| HG-REG-01 ⇄ HG-REG-02 | **Independent Concept** | 起源（PHI-OS Phase3 vs Phase7-B）・対象データ・裁定語彙のいずれも無関係。接点が無い。 |
| HG-REG-03 ⇄ HG-REG-04 | **Same Concept** | 同一の制度的Human Gate（A6 Human Gate）の異なる側面の記述。統合文書化が可能。 |
| HG-REG-04 ⇄ HG-REG-05 | **Related Concept** | dual-node構造として既に文書化済み。博士自身が「別系統だが両立する」と確定済み。統合ではなく明確な分離関係。 |

---

## 第3部 Governance Boundary

- **制度的裁定主体（Institutional Ruling Authority）:** HG-REG-04（A6 Human Gate / Human Gate Finalization）のみ。裁定値（APPROVE/HOLD/REJECT/DEFER）を確定できるのは博士本人に限定される制度設計であり、これがMoCKA全体での唯一の最終裁定点である。HG-REG-03はHG-REG-04と同一概念群の一部（配置位置の定義側）であり、裁定主体としての実体は持たない。
- **実装資産（Implementation Asset）:** HG-REG-01（`phi_os/human_gate.py`）とHG-REG-02（`semantic/query_engine/human_gate.py`）。いずれも実コードとして存在するが、HG-REG-01はHG-REG-04の制度原則（裁定は博士のみ）を技術的に強制していない汎用承認ワークフローであり、HG-REG-02はExecution境界とは無関係な矛盾裁定スケルトンである。
- **観測系（Observation Layer）:** HG-REG-05（O0 Human Gate）。権限を持たず、`closure_tag`のみを出力する終端ノード。裁定（`decision`）を一切出力しない。
- **推論系（Reasoning/Inference Layer）:** 該当する実体は本Registry中に存在しない。HG-REG-02はSemantic Rulingだが、これは既存の固定裁定語彙（accept/reject/defer/split）への分岐であり、推論を行う層ではない。Reasoning Node相当の概念はPhase10-3監査群（`PHASE10_3_RESONANCE_NODE_REDEFINITION_v1.md`等）で別途「Reasoning Node名称を前提としない」方針が確定しており、Human Gate Registryの対象には含めない。

---

## 第4部 Code Binding Safety Note

Phase1 Code Binding（Human Gate Core実装）着手時に**誤って再利用してはならない既存Human Gate実装**を以下に列挙する。

### `phi_os/human_gate.py`（HG-REG-01）とPhase1 Human Gate Coreとの関係

- **再利用禁止理由:** Phase1 Human Gate Core（`phi_os/human_gate/core.py`、未実装、HG-REG-03/04系列の最初の実コード化案）は「Input Evaluation + Risk & Consistency Checkのみ、裁定値を返さない」と定義されている。これに対し`phi_os/human_gate.py`の`approve()`/`reject()`は呼び出し元の権限チェックなしに即座に裁定値を記録できる関数であり、Core候補の設計原則（裁定値を返さない）に直接違反する。
- **部分的に参照可能な範囲:** `submit()`/`get_state()`/`list_pending()`に相当する「受付・状態追跡」機能のみは、Core候補の「Input Evaluationの入力受付」と概念的に重なるため参考にする価値がある。**ただし、そのまま流用するのではなく、権限チェック・裁定値非出力の原則を満たす形で再設計すること。**
- **既存データの扱い:** `human_gate_events`テーブルの1776件（append-only）は消去しないが、これを「運用実績」としてHuman Gate Coreの正当性根拠に転用してはならない（実態は単発移行スクリプトの着地点であり、継続的な承認運用の実績ではない）。

### `semantic/query_engine/human_gate.py`（HG-REG-02）とPhase1 Human Gate Coreとの関係

- **再利用禁止理由:** 意味論が正反対。HG-REG-02は「矛盾を保存する」装置であり、Phase1 Human Gate Core（HG-REG-03/04系列）が目指す「実行を許可する」という方向性とは無関係。`CollisionGovernor`/`OrderNormalizer`/`StructuralTraceReader`等の既存メソッド群はGovernedCollisionRecord専用に設計されており、承認フロー全般への転用を想定した設計ではない。
- **結論:** Phase1 Human Gate Core実装時にHG-REG-02のクラス・関数・契約を流用してはならない。完全に独立した別実装として扱うこと。

### 共通の安全策

- Phase1着手時、新規実装者（Claudeまたは他AI）が「Human Gate」という名前だけで既存コードを検索し、HG-REG-01またはHG-REG-02を「既存のHuman Gate実装」として誤認・再利用するリスクが現実的に存在する。本Registryの**Registry ID（HG-REG-01〜05）を実装着手前の参照キーとして必ず使用すること。**

---

## 第5部 Registry Recommendation

**A. Human Gate RegistryをKnowledge Lineage対象へ追加するか**

提言：追加する。本Registryは5実体の起源・分類・関係性を一意に固定する文書であり、Knowledge LineageのParent/Derived From/Related Documents追跡対象として位置づけることで、将来の監査文書がHuman Gateに言及する際の参照基盤になる。

**B. `docs/lineage/`配下に`human_gate_registry_v1.md`として管理するか**

提言：判断は博士裁定に委ねる。現状`docs/audits/`配下に類似監査文書群（Identity Audit/Identity Consolidation Audit等）が既に蓄積されているため、本文書も同ディレクトリに置くことで既存の監査系譜と一貫する。一方、`docs/lineage/`への配置は「監査」ではなく「識別台帳」としての性格を明示する利点がある。いずれを選ぶ場合も、移動はリネーム・新規配置に該当するため、本監査の範囲では実施しない。

**C. Registry ID命名規則を導入するか**

提言：導入する。本文書で暫定的に使用した`HG-REG-{NN}`形式（領域接頭辞-REG-連番）は、Human Gate以外の将来の名称衝突（例: Reasoning Node、Adapter等）にも拡張可能な汎用パターンである。正式採用する場合は命名規則自体を別文書（例: `docs/governance/registry_id_naming_convention_v1.md`）として固定することを推奨する。

---

## 判定: **Registry Ready**

判定理由：

- 5実体すべてについて既存監査（Identity Audit/Identity Consolidation Audit）から十分な裏付け情報が得られており、Registry ID・分類・起源・現状・責務の記入に欠落がない。
- Identity Mapping（第2部）はConsolidation Auditの統合可能性評価と完全に整合し、矛盾なく再構成できた。
- Governance Boundary（第3部）は4分類（制度的裁定主体/実装資産/観測系/推論系）のいずれも実体の割り当てに曖昧さが残らなかった。
- Code Binding Safety Note（第4部）はPhase1着手前に必要な「再利用禁止」の具体的根拠を提示できている。
- 唯一未確定なのは第5部Bの配置先（`docs/audits/`継続か`docs/lineage/`新設か）だが、これは制度的選択であり監査の完全性を損なうものではない。

---

## Knowledge Lineage

Document:
MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md

Status:
Review

Created:
2026-06-24

Last Reviewed:
2026-06-24

Origin:
博士指示「Human Gate Registry Audit v1」実施。既存のIdentity Audit/Identity Consolidation Auditの結果を正式な識別台帳として整理する目的。

Parent Documents:

* MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md
* MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md

Derived From:
MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1（第1部実体一覧・第2部責務比較・第5部統合可能性評価を直接の土台として再構成）

Supersedes:
（無し。既存2監査を置き換えるものではなく、その内容を正式台帳形式へ整理した派生文書）

Reason For Creation:
「Human Gate」名称の今後のKnowledge LineageおよびCode Bindingでの名称衝突を防止するため、既存監査結果を正式な識別台帳（Registry）として固定するため。

Affected Components:

* phi_os/human_gate.py
* semantic/query_engine/human_gate.py
* semantic/query_engine/human_gate_interface.py
* docs/spec/moCKA_human_gate_v1.md
* docs/governance/mocka_human_gate_decision_definition_v1.md
* docs/governance/o0_human_gate_semantic_terminal_v1.md
* moCKA_phase1_code_binding_plan_v1.md（Code Binding影響）

Related Documents:

* MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md
* MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md
* docs/contracts/phase7_b6_human_gate_ruling_v1.md
* docs/contracts/phase7_b7_human_gate_interface_v1.md
* docs/governance/mocka_phase10_human_gate_insertion_map_v1.md
* MOCKA_CODE_BINDING_HUMAN_GATE_DECISION_DRAFT_v1.md
* MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1.md

Revision History:

Revision:
R1

Date:
2026-06-24

Reason:
新規作成

Change:
初版作成（第1部Registry5件＋第2部Identity Mapping＋第3部Governance Boundary＋第4部Code Binding Safety Note＋第5部Registry Recommendation＋判定Registry Ready）

Impact:
Human Gate名称の識別台帳化により、今後のKnowledge Lineage参照およびPhase1 Code Binding着手時の既存実装誤用リスクを低減する審査材料を提供。コード変更・実装・リネーム・新規モジュール作成は無し。
