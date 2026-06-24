# MoCKA Human Gate Identity Consolidation Audit v1.0

**Status:** AUDIT
**目的:** MoCKA内で使用されている「Human Gate」という名称の実体を全て特定し、責務・系譜・関係性を整理する。
**実装・リネーム:** 禁止。本文書は監査のみ。
**調査方法:** リポジトリ全体grep（"human_gate"を含むファイル19件、md文書での言及多数）、各実体冒頭部の読込、git log作成日時確認。

---

## 第1部 Human Gate実体一覧

実コード・実文書の確認により、「Human Gate」を名乗る実体は**4つの独立した概念クラスタ**に分類される。

| # | パス | 作成時期 | 目的 | 現在の利用状況 |
|---|---|---|---|---|
| 1 | `phi_os/human_gate.py` | 2026-06-23 13:01 | PHI-OS Human Gate State Model v1。汎用リクエスト承認の状態機械（PENDING/APPROVED/REJECTED/EXPIRED/CANCELED） | HTTP経路未配線。`migrate_prevention_queue.py`の一度限り移行実行のみ（既存data: 1776件、1768件PENDING停止中）。[[MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1]]で監査済み（判定: Partially Compatible） |
| 2 | `semantic/query_engine/human_gate.py` + `human_gate_interface.py` | 2026-06-23 18:08 | Phase7-B-6/B-7。「Human Gate Ruling v0」。`GovernedCollisionRecord`（矛盾記録）への裁定（accept/reject/defer/split）を行う制度設計。「矛盾の意味的分岐点を固定する装置」と自己定義 | 契約文書（`phase7_b6_human_gate_ruling_v1.md`/`phase7_b7_human_gate_interface_v1.md`）に基づく「最小スケルトンのみ」実装。Phase7-8系列の一部として存在 |
| 3 | `docs/spec/moCKA_human_gate_v1.md`（Phase C Human Gate Spec） | 2026-06-24 18:46 | IR/Spec LayerとExecution Layer（app.py）の間に位置する「唯一の承認経路」。承認3段階（observation review/risk validation/execution approval）を定義 | 設計のみ、実装ゼロ。[[moCKA_phase1_code_binding_plan_v1]]のHuman Gate Core候補がこの系列の最初の実コード化案 |
| 4 | `docs/governance/mocka_human_gate_decision_definition_v1.md`（A6 Human Gate / Human Gate Finalization系） | 2026-06-24 12:18 | 制度層の最終裁定点。Core（自動評価）/Finalization（博士のみ、APPROVE/HOLD/REJECT/DEFER確定）の2層分離を確定。MOCKA_CODE_BINDING_HUMAN_GATE_DECISION_DRAFT_v1/FINALIZATION_v1、MOCKA_EXTENSION_HUMAN_GATE_SUMMARY_v1等、本セッションで作成した一連の裁定記録文書の上位概念 | 制度として確定済み（DRAFT, pre-authorization state継続）。実コードは存在しない |
| 5（補助） | `docs/governance/o0_human_gate_semantic_terminal_v1.md`（O0-Human Gate） | 2026-06-24 17:21 | O0観測層の終端ノード。**A6 Human Gateとは別系統と文書内で明示的に宣言**。権限なし、出力は`closure_tag`のみ（`decision`は出力しない） | 定義のみ（DRAFT, no implementation, no runtime wiring）。#4とのdual-node構造として`mocka_phase10_human_gate_insertion_map_v1.md`等に記載 |

**所見:** #3（Phase C Spec）と#4（Decision Definition/Finalization系）は同一の制度的Human Gate概念（A6 Human Gate）の異なる側面（#3=Execution境界での配置位置、#4=裁定権限の構造）であり、実質的に1つの概念群として扱える。#1・#2・#5はそれぞれ独立した別概念である。

---

## 第2部 責務比較

| # | 実体 | 分類 |
|---|---|---|
| 1 | `phi_os/human_gate.py` | **Approval State Machine** |
| 2 | `semantic/query_engine/human_gate.py` | **Semantic Ruling** |
| 3 | `moCKA_human_gate_v1.md`（Phase C Spec） | **Governance Gate** |
| 4 | `mocka_human_gate_decision_definition_v1.md`（A6 Human Gate/Finalization） | **Governance Gate** |
| 5 | `o0_human_gate_semantic_terminal_v1.md`（O0-Human Gate） | **Other**（観測終端、Governance Gateでもない——権限・裁定機能を明示的に持たない） |

**所見:** 「Human Gate」という1つの名前が、Approval State Machine・Semantic Ruling・Governance Gate・Otherという**4種類の異なる分類**にまたがって使われている。これは名称の濫用というより、各Phase（Phase3 PHI-OS／Phase7-B／Phase C・D／Phase10-O0）が独立に「人間が関わる地点」を設計する際、毎回「Human Gate」という直感的な名前を再利用してしまった結果と考えられる。

---

## 第3部 Lineage比較

| # | 実体 | Origin | Parent | Derived From | Related Systems |
|---|---|---|---|---|---|
| 1 | `phi_os/human_gate.py` | `docs/governance/control_map_v2.md`、TODO: PHI-OS-HUMAN-GATE-STATE-MODEL-V1 | PHI-OS Phase3移行プロジェクト | `data/prevention_queue.json`（旧形式） | `migrate_prevention_queue.py`、`mocka_events.db.human_gate_events` |
| 2 | `semantic/query_engine/human_gate.py` | Phase7-B-5 `GovernedCollisionRecord`（`phase7_b5_collision_governance_v1.md`） | Phase7-B-6契約 | `CollisionGovernor`/`OrderNormalizer`/`StructuralTraceReader`（変更不可の既存メソッド群） | `human_gate_interface.py`（Phase7-B-7、UI契約） |
| 3 | `moCKA_human_gate_v1.md` | Phase C設計シリーズ（IR→Execution境界の確立） | `moCKA_spec_v1.0.2-rc.md` | Phase C設計指示 | `moCKA_phaseC_execution_boundary_v1.md`、`moCKA_app_boundary_v1.md` |
| 4 | `mocka_human_gate_decision_definition_v1.md` | Phase10-Stasis/PHASE5_STEP3_SEALの「自律行動追加禁止」原則との矛盾指摘（Claudeが安全性指摘） | Phase10-3 FROZEN系列 | 当初案「Human Gate=判断アルゴリズム」からの2層分離への修正 | `mocka_hab_human_gate_relation_v1.md`、`mocka_phase10_human_gate_insertion_map_v1.md`、Code Binding Decision Draft/Finalization系列 |
| 5 | `o0_human_gate_semantic_terminal_v1.md` | A6 Human Gate定義タスク提示時に名称衝突をClaudeが指摘、博士が別系統ノードと確定 | O0語彙系（観測層） | O0-ΔL（diff generation）との対比定義 | `mocka_global_terminal_map_v1.md`（dual-node構造の最終統合） |

**所見:** #1と#2は互いに独立した起源（PHI-OS Phase3 vs Phase7-B）を持ち、接点が無い。#3・#4は同じPhase C/D〜Phase10-3時系列の中で生まれ、相互参照している。#5は#4と명시적な名前衝突を経て分離が確定した唯一のケースであり、「衝突を経て解決済み」という意味で他の組より整理状態が進んでいる。

---

## 第4部 衝突分析

### 名前衝突
- **#1と#4（およびその他Governance Gate系）の間で発生中。** `phi_os/human_gate.py`は「PHI-OS Human Gate」を名乗り、`mocka_human_gate_decision_definition_v1.md`は「A6 Human Gate」を名乗る。両者は別概念だが、コード上は両方とも単に`human_gate`という識別子を使うため、将来の検索・参照時に混同するリスクが高い。
- **#5（O0-Human Gate）は既に名前衝突をユーザー自身が認識し、文書内Disambiguationセクションで明示的に解消済み**（"It is NOT the same node as the existing A6 Human Gate"）。これは唯一の良好な前例。
- **#2（semantic/query_engine/human_gate.py）は#1・#3・#4のいずれとも名前衝突しているが、解消する文書が存在しない。**

### 意味衝突
- #1（Approval State Machine）の`approve()`/`reject()`は即座に裁定値を記録する。これは#4（A6 Human Gate Finalization）が定める「裁定は博士のみ」という制度的原則と技術的に衝突する可能性がある（[[MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1]]で既に指摘済み）。
- #2（Semantic Ruling）は「Human Gateは最終チェック機構ではない、矛盾を意味として成立させる層」と自己定義しており、#3・#4が定義する「承認経路・最終裁定点」という意味とは正反対の方向性を持つ。同じ語を使いながら定義の方向性が逆転している。

### ガバナンス衝突
- #4（A6 Human Gate）はMoCKA全体の制度核として「博士のみが裁定」を保証する設計だが、#1（`phi_os/human_gate.py`）の`approve()`はコードレベルで誰からでも呼び出し可能であり、呼び出し元が博士本人であることを保証する仕組みが無い。**もし将来#1のHTTP APIが配線される、または別モジュールが直接`hg.approve()`を呼ぶ実装が追加された場合、#4が確立した「裁定は博士のみ」という制度原則をコードが黙って迂回するリスクがある。**
- #5（O0-Human Gate）は権限を持たないことを明示しているため、ガバナンス衝突のリスクは低い。

### Code Binding影響
- [[moCKA_phase1_code_binding_plan_v1]]が提案するHuman Gate Core（#3・#4系列の最初の実コード化）は、既存の#1（`phi_os/human_gate.py`）と機能的に重複する部分（受付・状態追跡）を持つ。Phase1着手時に、新規実装者（Claudeまたは他AI）が誤って#1を「既存のHuman Gate実装」として再利用・拡張してしまうリスクがある——これは#1が#4の制度原則を満たさないまま「Human Gate」を名乗っているために発生する誤認リスクである。
- #2（Semantic Ruling）はExecution層・app.pyとは無関係な系統であり、Code Bindingへの直接影響は低い。

---

## 第5部 統合可能性評価

| # | 実体 | 評価 |
|---|---|---|
| 1 ⇄ 3/4 | `phi_os/human_gate.py` と Phase C/D Governance Gate系列 | **Related Concept**（「人間の承認を記録する」という機能領域は重なるが、権限保証の有無・語彙・対象範囲が異なるため同一概念とは言えない） |
| 2 ⇄ 3/4 | `semantic/query_engine/human_gate.py` と Phase C/D Governance Gate系列 | **Independent Concept**（裁定の意味論が正反対：Semantic Rulingは「矛盾を保存する」、Governance Gateは「実行を許可する」） |
| 1 ⇄ 2 | `phi_os/human_gate.py` と `semantic/query_engine/human_gate.py` | **Independent Concept**（起源・対象データ・裁定語彙のいずれも無関係） |
| 3 ⇄ 4 | Phase C Human Gate Spec と A6 Human Gate Decision Definition | **Same Concept**（同一の制度的Human Gate＝A6 Human Gateの異なる側面の記述。統合文書化が可能） |
| 4 ⇄ 5 | A6 Human Gate と O0-Human Gate | **Related Concept**（dual-node構造として既に文書化済み、博士自身が「別系統だが両立する」と確定。統合ではなく明確な分離関係） |

---

## 最終判定: **Human Gate Identity Risk: Medium**

判定理由：

- **Highに該当しない理由:** 最も懸念されるガバナンス衝突（#1の`approve()`が#4の「博士のみ裁定」原則を技術的に迂回できる）は、現状**#1のHTTP経路が未配線・実運用未稼働**であるため、実害は発生していない（[[MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1]]確認済み）。また#5（O0-Human Gate）は既に名前衝突を認識・解消済みの良好な前例がある。
- **Lowに該当しない理由:** 4つの異なる概念クラスタが同一の名称「Human Gate」を共有しており、特に#1と#4は機能領域が重なりながら権限保証のレベルが全く異なる。Code Binding Phase1着手時に既存#1を誤って再利用するリスクが現実的に存在する（第4部で指摘済み）。また#2は意味論が正反対でありながら未解消の名前衝突状態にある。
- これらはいずれも「今すぐ重大事故になる」状態ではないが、「次の実装ステップ（Phase1着手）で誤認・誤用が発生し得る」という意味でMedium判定が適切と判断した。

---

## Knowledge Lineage

Document:
MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md

Status:
Review

Created:
2026-06-24

Last Reviewed:
2026-06-24

Origin:
MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1（phi_os/human_gate.py単体監査）完了後、博士指示によりMoCKA全体の「Human Gate」名称実体の統合監査として実施。

Parent Documents:

* MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md
* MOCKA_LINEAGE_GOVERNANCE_FINALIZATION_v1.md

Derived From:
MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1（phi_os/human_gate.pyの個別監査結果）

Supersedes:
（無し、MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1を置き換えるものではなく上位の統合監査）

Reason For Creation:
「Human Gate」という名称がMoCKA内で4つの異なる概念（Approval State Machine/Semantic Ruling/Governance Gate×2系統/Observation Terminal）にまたがって使用されており、名前衝突・意味衝突・ガバナンス衝突・Code Binding影響を整理し、博士の今後の整理裁定のための材料を提供するため。

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
* docs/contracts/phase7_b6_human_gate_ruling_v1.md
* docs/contracts/phase7_b7_human_gate_interface_v1.md
* docs/governance/mocka_phase10_human_gate_insertion_map_v1.md

Revision History:

Revision:
R1

Date:
2026-06-24

Reason:
新規作成

Change:
初版作成（第1部実体一覧5件＋第2部責務分類＋第3部Lineage比較＋第4部衝突分析＋第5部統合可能性評価＋Risk: Medium判定）

Impact:
「Human Gate」名称の整理（リネーム・統合・分離の是非）についての博士裁定のための審査材料を提供。コード変更・リネーム・実装は無し。
