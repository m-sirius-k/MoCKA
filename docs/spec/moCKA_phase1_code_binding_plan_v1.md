# MoCKA Code Binding — Phase 1 Plan v1.0

**Status:** DESIGN — Human Gate段階承認の第1段階のみを対象とする計画書
**基準文書:** [[MOCKA_CODE_BINDING_FINAL_REVIEW_v1]]、[[MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1]]
**対象スコープ:** Phase1 = Human Gate Core（評価機構のみ）の単体構築。Execution engine / app.py orchestration / Output formatterはPhase1の対象外（Phase2以降）。
**実装・コード生成:** 禁止。本文書は設計と監査のみ。

---

## 1. 対象ファイル

| ファイル | 種別 | 状態 |
|---|---|---|
| `phi_os/human_gate/__init__.py` | 新規（未作成） | Phase1で作成予定（本文書では作成しない） |
| `phi_os/human_gate/core.py` | 新規（未作成） | Human Gate Coreの本体。Input Evaluation + Risk & Consistency Checkのみを実装する想定。判断材料生成に限定し、APPROVE/HOLD/REJECT/DEFERのいずれも返さない。 |
| `phi_os/tests/test_human_gate_core.py` | 新規（未作成） | Coreの入出力契約テスト。Core/Finalization境界テスト（Coreが裁定値を返さないことの確認）を含む。 |

**既存ファイルの参照のみ（変更しない）:**
- `phi_os/human_gate.py`（既存実体、Phase1新設モジュールとの関係・重複有無を実装前に確認する対象。本文書では確認方法のみ提示し、確認作業自体は行わない）
- `docs/contracts/advisor_adapter_contract_v1.md`、`docs/governance/mocka_human_gate_decision_definition_v1.md`、`docs/spec/moCKA_human_gate_v1.md`（Core/Finalization分離原則の参照元）

---

## 2. 変更範囲

- `phi_os/human_gate/`配下への新規ファイル追加のみ。
- 既存モジュール（`phi_os/event_gate.py`、`relay/`配下、`app.py`）への変更・呼び出し追加は**Phase1には含まない**。
- Human Gate Coreは完全にスタンドアロンで構築し、どこからも呼び出されない状態でテストのみ通すことをPhase1の完了形とする（呼び出し配線はPhase2以降）。

## 3. 変更禁止範囲

- `app.py`（全行）— Phase1では一切変更しない。理由は第4節「app.py変更の有無」で明記。
- `relay/`配下全ファイル（Phase4/5で確立済みの契約`{state, policy, action}`を含み、Human Gate Phase1とは無関係）。
- `phi_os/event_gate.py`、`phi_os/integrity.py`（Event Integrity Framework確定済み資産、Phase1の対象外）。
- 既存`phi_os/human_gate.py`（重複・統合の判断はPhase1完了後に別途実施。Phase1内で削除・改修・リネームはしない）。
- IR/Spec文書群（v1.0/v1.0.1/v1.0.2-rc、Phase C/D文書群）— 本文書はこれらを参照するのみで内容を変更しない。

## 4. テスト計画

| テスト項目 | 内容 |
|---|---|
| 入出力契約テスト | Core入力（query/context相当）に対し、出力が「判断材料（評価結果）」の形式のみであることを確認 |
| Core/Finalization境界テスト | Coreの出力にAPPROVE/HOLD/REJECT/DEFERに相当する値が一切含まれないことを確認（自律裁定化防止の直接的な検証） |
| 既存回帰テスト | phi_os既存テストスイート（現行104件、Time API/Replay系含む）全件PASSの確認。Phase1新設コードがこれらに影響しないことを確認 |
| 既知incident非干渉確認 | Phase1ではapp.pyを変更しないため、`import app`実行は不要。pytest経由のみでの動作確認とし、INCIDENT_IMPORT_APP_SIDE_EFFECT（モジュールレベルthread起動による即時AUTO-AUDIT発火）を回避する（既存Time API Step1/Step2/Step3で確立済みの手順を継続） |

## 5. Completion Criteria

1. `phi_os/human_gate/core.py`が実装され、入出力契約テストが全件PASSすること。
2. Core/Finalization境界テストがPASSし、Coreが裁定値を返さないことが実証されること。
3. phi_os既存テストスイート（104件）に1件もFAILが発生しないこと。
4. `app.py`に1行の変更も加えられていないこと（git diffで確認可能な状態）。
5. Phase1完了報告書（第7節Audit Artifact）が作成され、commit + tag + `mocka_seal`の3点が揃うこと。

## 6. Rollback Procedure

[[MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1]]で確定済みの原因追跡型ロールバック（特定→監査→影響範囲確認→復旧方針決定→再検証）をPhase1に適用する。

Phase1固有の補足：
- Phase1はapp.py非接触・新規ファイルのみの追加であるため、最終フォールバックは**Phase1開始前のcommit（新規ファイル追加前の状態）への復帰**で完結する。既存資産（app.py、relay/、既存human_gate.py等）への影響が原理的に発生しないため、Readiness Review/Final Reviewで指摘された「最終フォールバック地点の未明文化」というリスクは、Phase1の範囲に限れば実質的に解消される（Phase1開始直前のtagを基準点とすればよい）。
- 発動条件: 第4節テスト項目のいずれかがFAILした場合、または既存テストスイートにFAILが波及した場合。

## 7. Audit Artifact

実装が行われた場合、以下を残す（本文書では作成しない、実装後タスクとして列挙のみ）：

1. **Phase1完了報告書**（`docs/releases/CODE_BINDING_PHASE1_SEAL.md`形式）— commit/tag/mocka_seal値、テスト結果件数を記載。
2. **Core/Finalization境界実証記録** — 境界テストの実行結果（裁定値が出力に含まれないことの証跡）。
3. **既存human_gate.pyとの関係整理メモ** — 重複・統合・棄却のいずれを採るかの判断記録（Phase1完了後、Phase2着手前に作成）。
4. **Knowledge Lineageセクション**（[[mocka_knowledge_lineage_standard_v1]]準拠）— 新設`core.py`・`test_human_gate_core.py`それぞれにCode Lineage相当の記録を残す（コードへの記録形式は別途Code Lineage標準の制定を要する。未制定の場合は完了報告書内に代替記載する）。

---

## app.py変更の有無（明記）

**Phase1において、`app.py`は一切変更しない。**

理由：
- Human Gate Coreはスタンドアロンモジュールとして構築可能であり、Phase1の完了条件（第5節）に呼び出し配線を含めていない。
- これにより、既知incident（モジュールレベルthread起動による`import app`時の即時AUTO-AUDIT発火・意図しないgit commit）との接触を完全に回避できる。
- app.pyへの呼び出し追加（orchestrationフック）は、Phase1のCore単体動作が確認された後のPhase2以降の対象とする。

---

## 判定: Phase1 Not Ready

判定理由：

1. **Human Gate Finalization v1の最終裁定（APPROVE/HOLD/REJECT/DEFER）が依然未記入。** Phase1の対象範囲・テスト計画・Completion Criteriaを設計レベルで整えることと、博士がこの計画に基づく実装着手を承認することは別である。[[MOCKA_CODE_BINDING_FINAL_REVIEW_v1]]で示した通り、過去2回ともCode Binding移行は「まだ早い」と判定されたパターンが確立している。
2. **既存`phi_os/human_gate.py`との関係が未整理のまま新規モジュールを追加することになる。** 重複実装・名称衝突のリスクがあり、Phase1着手前にこの既存ファイルの役割確認（最低限、内容を読み関係を判定すること）が必要だが、本文書ではその確認自体を実施していない（設計と監査のみという指示の範囲内）。
3. 上記2点はいずれも、博士の明示的な実装着手承認（Human Gateを発動して実装してよい、との直接的な言明）が出ていない現状において、Claude側が先取りして「Ready」と結論づけることを妥当としない。

**次の正しいアクション：** 博士が本計画（対象ファイル/変更範囲/テスト計画/Completion Criteria/Rollback Procedure）を確認し、(1)既存`phi_os/human_gate.py`との関係をどう扱うか、(2)実装着手そのものを承認するか、の2点について裁定すること。

---

## Knowledge Lineage

Document:
moCKA_phase1_code_binding_plan_v1.md

Status:
Draft

Created:
2026-06-24

Last Reviewed:
2026-06-24

Origin:
MOCKA_CODE_BINDING_FINAL_REVIEW_v1で「段階承認の第1段階の範囲が未確定」と指摘されたことを受け、その第1段階（Human Gate Core単体構築）を具体的に計画するために作成。

Parent Documents:

* MOCKA_CODE_BINDING_FINAL_REVIEW_v1.md
* MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1.md
* moCKA_phaseD_execution_enablement_v1.md

Derived From:
MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1（承認単位=段階承認の裁定）

Supersedes:
（無し）

Reason For Creation:
Human Gate段階承認の第1段階の具体的な対象・範囲・テスト計画・完了条件・ロールバック手順・監査成果物を明示し、博士の裁定材料とするため。

Affected Components:

* Human Gate Core（新設予定）
* 既存phi_os/human_gate.py（関係未整理）
* phi_os/tests/

Related Documents:

* moCKA_phaseD_execution_enablement_v1.md
* mocka_human_gate_decision_definition_v1.md
* MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1.md

Revision History:

Revision:
R1

Date:
2026-06-24

Reason:
新規作成

Change:
初版作成（対象ファイル/変更範囲/変更禁止範囲/テスト計画/Completion Criteria/Rollback Procedure/Audit Artifact、app.py変更無しの明記、Phase1 Not Ready判定）

Impact:
Phase1着手可否についての博士裁定のための審査材料を提供。実装・コード生成は行っていない。
