# MoCKA Human Gate Identity Audit v1.0

**Status:** AUDIT
**対象:** `phi_os/human_gate.py`
**実装・新規実装・リネーム:** 禁止。本文書は監査のみ。
**調査方法:** 実ファイル読み込み（250行全文）、リポジトリ全体grep、`data/mocka_events.db`実データ確認、git log確認。

---

## 1. 現在の責務

`phi_os/human_gate.py`は「PHI-OS Human Gate State Model v1」と自称する、汎用的なリクエスト承認の**状態機械**である。

- ファイル冒頭コメントで「PHI-OSがHuman Gateの唯一の状態管理責務を持つ。GL7およびApp層はHuman Gate状態を保持しない」と明記。
- 状態: `PENDING / APPROVED / REJECTED / EXPIRED / CANCELED`の5値。
- 遷移: `submit→PENDING`、`approve/reject/expire: PENDING→{APPROVED/REJECTED/EXPIRED}`、`cancel: {PENDING,APPROVED,REJECTED}→CANCELED`。
- **イベントソーシング設計**: state自体は保存せず、`human_gate_events`テーブル（`mocka_events.db`内）のevent列から都度再構築する（`get_state()`）。
- HTTP API（Flask Blueprint `human_gate_bp`）として`/api/human_gate/submit`・`/approve`・`/reject`・`/status/<id>`・`/pending`の5エンドポイントを定義済み。

## 2. 利用箇所

実コード調査の結果、本モジュールを直接利用しているのは以下の2箇所のみ：

| 利用箇所 | 利用形態 |
|---|---|
| `phi_os/migrate_prevention_queue.py` | `from phi_os import human_gate as hg`で直接import。冒頭コメントに「Phase3移行スクリプト: data/prevention_queue.json -> phi_os.human_gate event」と明記。**一度限りの移行スクリプト。** |
| `phi_os/tests/test_human_gate.py` | pytestスイート（テスト用途のみ、本番呼び出しではない） |

`interface/risk_scorer.py`に"human_gate_overrides"という**コメント上の言及のみ**存在し、実コード呼び出しは無い。

## 3. 呼び出し経路

- **HTTP経路: 未配線。** `app.py`全体をgrep検索した結果、`human_gate_bp`の`register_blueprint`呼び出しは0件。Flask Blueprintとして定義されているが、Command Center（port:5000）からは一切到達不可能な状態。
- **直接呼び出し経路: 1ルートのみ実在。** `migrate_prevention_queue.py`が`hg.submit()`/関連関数をインプロセスで直接呼ぶ経路のみが実際に使われている。
- 結論: 本モジュールはこれまで「HTTP API経由のHuman Gate運用」としては一度も稼働したことがなく、唯一の実行経路は単発の移行スクリプトである。

## 4. 実行実績の有無

`data/mocka_events.db`の`human_gate_events`テーブルを直接確認した結果：

- **合計1776件**の実データが存在（モジュール自体は「実行実績あり」）。
- 内訳: `submit`1772件 / `approve`4件 / `reject`0件 / `expire`0件 / `cancel`0件。
- 全件のタイムスタンプは2026-06-23付近に集中、`payload.source`は全て`"prevention_queue_migration"`、`request_id`は`TECH_ALERT_*`形式。
- **解釈:** これは継続的な承認運用の実績ではなく、`migrate_prevention_queue.py`による**一括移行イベントの着地点**としての実績である。1772件のうち1768件（=1772-4）は移行後そのままPENDING状態で停止しており、その後一度も処理（approve/reject/expire）されていない。
- **結論: 「実行実績はある」が「運用としての承認フローは実質的に機能していない（PENDINGキューが事実上の死蔵状態）」。**

## 5. Phase C / Phase D 定義との整合性

[[moCKA_phaseC_execution_boundary_v1]] / [[moCKA_human_gate_v1]] / Phase D文書群（[[moCKA_phaseD_execution_core_v1]]等）が定義するHuman Gateは以下の構造を持つ：

- 承認3段階（observation review / risk validation / execution approval）
- Human Gate Core（評価機構、自動、判断材料生成のみ、裁定値を返さない）とHuman Gate Finalization（博士本人のみ、APPROVE/HOLD/REJECT/DEFERの確定）の2層分離（[[mocka_human_gate_decision_definition_v1]]で確定済み）
- IR→Execution変換禁止、app.pyが唯一の実行終端、という境界契約との連動

`phi_os/human_gate.py`を照合した結果：

| 観点 | Phase C/D定義 | phi_os/human_gate.py | 整合性 |
|---|---|---|---|
| 状態語彙 | APPROVE/HOLD/REJECT/DEFER | PENDING/APPROVED/REJECTED/EXPIRED/CANCELED | **不一致**（語彙が異なる別系統） |
| Core/Finalization分離 | 明確に2層分離、Coreは裁定値を返さない | 分離なし。`approve()`/`reject()`を呼べば誰でも即座に裁定値（APPROVED/REJECTED）が記録される | **不一致**（自律裁定化防止の仕組みが無い） |
| 実行境界（IR→Execution） | app.pyが唯一の実行終端 | 本モジュールはapp.pyと無関係に独立動作する汎用ゲート | **無関係**（接続点が無い） |
| イベントソーシング思想 | 明文化なし（ただしMoCKA三要素「Record」原則と一致） | event列からstate再構築、append-only | **思想レベルでは整合** |

**結論: 語彙・分離構造・実行境界の3点でPhase C/D定義と不一致。イベントソーシングという設計思想のみ整合。**

## 6. Human Gate Core候補との重複箇所

[[moCKA_phase1_code_binding_plan_v1]]が提案するHuman Gate Core（`phi_os/human_gate/core.py`、未実装）は「Input Evaluation + Risk & Consistency Checkのみ、判断材料生成に限定し裁定値を返さない」と定義されている。

重複・衝突点：

- **`submit()`相当の機能は重複候補。** 「リクエストを受け付けてPENDING状態にする」という機能は、Core候補が将来持つ「Input Evaluationの入力受付」と概念的に重なる。
- **`approve()`/`reject()`は明確な非互換。** これらは裁定値を直接記録する関数であり、Core候補の「裁定値を返さない」という設計原則そのものに違反する形になる。既存モジュールをCoreとして転用した場合、Core自体が裁定機構になってしまい、[[feedback_flag_autonomy_risk_in_governance_design]]で繰り返し警戒されてきた自律裁定化パターンに直接抵触する。
- **呼び出し元の認証・権限チェックが存在しない。** `approve(request_id)`はどのコードからでも呼び出せ、呼び出し元が「博士本人の操作」であることを保証する仕組みが無い。Human Gate Finalizationの原則（裁定は常に博士のみ）を技術的に強制していない。

**結論: 「受付（submit/get_state/list_pending）」部分はCore候補と機能的に重複するが、「裁定（approve/reject）」部分はCore候補の設計原則と矛盾し、そのままでは転用不可。**

## 7. 将来的に妥当な扱い（継続利用／統合／分離／廃止）

判断材料：

- 実データ1776件が存在し、append-only原則上イベント履歴自体は消去できない（廃止してもevents.db内の記録は残る）。
- モジュールの「受付・状態追跡」部分はCore候補と概念が重なる。
- モジュールの「裁定記録（approve/reject）」部分はHuman Gate Finalization原則（裁定は博士のみ）を技術的に強制しておらず、現状のまま将来Phase1のCoreとして昇格させると危険。
- リポジトリ内に同名「Human Gate」を名乗る別系統が既に2つ存在する（本ファイルと`semantic/query_engine/human_gate.py`=Phase7-B-6 Human Gate Ruling v0、概念が全く異なる：Ruling側はcollision裁定の固定装置、本ファイルは汎用承認ワークフロー）。3つ目の概念がガバナンス文書群（A6 Human Gate/O0-Human Gate/Human Gate Core/Finalization）に存在する。

**評価（妥当性の所見、最終判断は博士）：**

- **継続利用（現状のまま）**: 非推奨。HTTP経路が配線されておらず実質死蔵、かつ裁定記録に権限チェックが無いまま将来誤って呼び出される潜在リスクがある。
- **統合（Human Gate Coreへ吸収）**: 部分的にのみ妥当。「受付・状態追跡」機能のみ参考にする価値はあるが、「裁定記録」機能はそのまま統合すべきではない。
- **分離（独立した別名のモジュールとして存続）**: 最も整合性が高い所見。本モジュールは「汎用承認ワークフロー（Generic Approval Queue）」として、Phase C/Dの「Human Gate」とは異なる役割・別名で存続させ、名称の重複自体を解消するのが筋が良い（ただしリネームは本監査の対象外であり、本文書では実施しない）。
- **廃止**: 非推奨。1776件の実データ（特に1768件の未処理PENDING）が残っており、無条件の廃止はデータ・運用上の整理を先に必要とする。

**所見（推奨ではなく観察）: 「分離」が最も整合的だが、これは博士の裁定事項であり本監査では確定しない。**

---

## 最終判定: **Partially Compatible**

判定理由：

- イベントソーシング・append-only・Record原則というMoCKAの基本哲学とは整合している（Compatible側の根拠）。
- しかし語彙（PENDING/APPROVED系 vs APPROVE/HOLD/REJECT/DEFER系）、Core/Finalization分離の欠如、裁定権限チェックの欠如、app.py実行境界との接続欠如の4点でPhase C/D定義から外れている（Incompatible側の根拠）。
- 完全な不整合（Incompatible）とは言えない理由は、構造的な接続を変更すれば（リネーム・統合等を経て）整合させる余地が残っているため。完全な整合（Compatible）とは言えない理由は、現状のまま転用すると自律裁定化リスクを技術的に許してしまうため。

---

## Knowledge Lineage

Document:
MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md

Status:
Review

Created:
2026-06-24

Last Reviewed:
2026-06-24

Origin:
MOCKA_LINEAGE_GOVERNANCE_FINALIZATION_v1で次監査テーマとしてPHI-OS Identity Auditが指定された流れの中で、博士指示によりphi_os/human_gate.py単体のIdentity Auditを先行実施。

Parent Documents:

* moCKA_phase1_code_binding_plan_v1.md
* moCKA_phaseC_execution_boundary_v1.md
* mocka_human_gate_decision_definition_v1.md

Derived From:
moCKA_phase1_code_binding_plan_v1（Human Gate Core候補との重複確認の必要性）

Supersedes:
（無し）

Reason For Creation:
phi_os/human_gate.pyの責務・利用実績・Phase C/D整合性・Human Gate Core候補との重複を確認し、将来の継続利用/統合/分離/廃止判断のための監査材料を提供するため。

Affected Components:

* phi_os/human_gate.py
* phi_os/migrate_prevention_queue.py
* moCKA_phase1_code_binding_plan_v1（Human Gate Core設計）
* data/mocka_events.db（human_gate_eventsテーブル）

Related Documents:

* semantic/query_engine/human_gate.py（別系統、Phase7-B-6 Human Gate Ruling v0）
* MOCKA_LINEAGE_GOVERNANCE_FINALIZATION_v1.md
* moCKA_phase1_code_binding_plan_v1.md

Revision History:

Revision:
R1

Date:
2026-06-24

Reason:
新規作成

Change:
初版作成（7項目調査＋Partially Compatible判定）

Impact:
phi_os/human_gate.pyの将来扱い（継続利用/統合/分離/廃止）についての博士裁定のための審査材料を提供。コード変更・実装・リネームは無し。
