# MoCKA 制御マップ v2.0（責務固定版・決定記録）

Status: DECISION_RECORDED（本文書は意思決定の記録。コード変更は未実施）
Date: 2026-06-23
前版: `docs/governance/control_map_v1.md`（Bモデル採用の初期決定）
関連: `docs/governance/gl7_execution_kernel_spec_v1.md`,
MOCKA_TODO: CONTROL-MAP-V1-DECISION, GL7-UNENFORCED-CONDITIONS-BUG

## 1. 確定原則（制御三層の役割固定）

control_map_v1.mdの3保留事項について、個別の是非判断ではなく
「責務をどこに置くか」のルールとして以下を確定する：

- **GL7**: 構文・実行レベルの物理制約のみ（この変更を実行できる/できないか）
- **PHI-OS**: 意味・リスク・整合性判断（この変更を許可すべきか。Human Gate含む）
- **App/UI層**: 運用フロー（人間への提示・承認/却下の入力受付・再試行）

## 2. 3保留事項の再配置（確定）

| 項目 | 処理 | 理由 |
|---|---|---|
| `FORBIDDEN_EXECUTIONS`(execution_governance.py:26-35) | GL7から削除し、PHI-OSの「意味禁止ルール」へ統合 | `create_new_folder_without_grounding`等の8項目は「実行できるか/できないか」という物理制約ではなく、「この行為の意味が許容されるか」という意味判断であるため |
| `encoding_mismatch`(execution_governance.py:40) | GL7のABORT_CONDITIONSから廃止。役割は既存の`mocka_check_utf8`に統合(新規実装は不要、既存ツールへの一本化) | エンコーディング検証はGL7の「実行制御」ではなく「データ品質チェック」であり、既に専用ツールが存在するため重複実装を避ける |
| Human Gate | PHI-OSを「唯一のHuman Gate意味層」とする。app.py(prevention_queue)はUIトリガ(承認/却下の入力受付)に限定。GL7はHuman Gateに関与しない | Human Gateは「実行できるか」ではなく「許可すべきか」の判断であり、PHI-OSの責務範囲(意味裁定)に一致するため |

## 3. GL7側の変更（廃止リスト・素案）

実装時にGL7から削除する対象：
- `FORBIDDEN_EXECUTIONS`リスト定義（execution_governance.py:26-35）
- `ABORT_CONDITIONS`内の`"encoding_mismatch"`（execution_governance.py:40）

GL7に残るABORT_CONDITIONS（実発火している4条件のみ）：
- `grounding_not_completed`
- `deletion_outside_scope`
- `new_directory_detected`
- `unexpected_file_count`

## 4. PHI-OS側の変更（移設リスト・素案）

実装時にPHI-OSへ追加する対象：
- `FORBIDDEN_EXECUTIONS`8項目相当の意味禁止ルール（`phi_os/gate_validator.py`への新規追加、または専用モジュール`phi_os/semantic_forbidden.py`等として新設するかは別途設計）
- Human Gate（承認待ち状態を持つ判定ロジック。現状`phi_os/event_gate.py`にはpending状態の概念がなく、新規追加が必要）

`encoding_mismatch`はPHI-OSへの移設ではなく、既存`mocka_check_utf8`ツールへの一本化（呼び出し元の運用ルールとして「変更前に必ずmocka_check_utf8を呼ぶ」を強制する方向、CLAUDE.mdの既存プロトコルと一致）。

## 5. App層側の変更（素案）

- `app.py`の`/decision/approve`・`/decision/reject`は、承認/却下の最終判定をPHI-OS側の関数呼び出しに委譲する形へ変更。現状`prevention_queue.json`を直接書き換えている処理を、PHI-OS経由に変更する必要がある（未設計）。

## 6. 未決定事項（本v2でも保留）

- `prevention_queue`が扱う「再発パターンへの予防策提案」と、GL7 Dry Run通過後に想定される「変更実行の人間承認」は対象が異なる可能性がある。両者を本当に同じPHI-OS Human Gateとして統合するか、別々のHuman Gateとして並存させるかは、実装設計時に再確認が必要。

## 7. 次の一手

本v2は責務の境界線の確定記録であり、コードへの反映はまだ行っていない。
次は「GL7最小カーネル化（削除後の実コード設計）」として、
具体的にどのコードをどう変更するかの実装設計に進む。