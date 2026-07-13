# AUTO_SEAL M2 Connection Proposal v1.0

- Document ID: GOV-PROP-ASM2-001
- Status: Proposed (Phase 1; implementation NOT approved)
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Approval owner: きむら博士
- Parent: DC_20260713_010 (M1 CLOSED / PASS with Open Items)
- Proposal decision: DC_20260713_011
- Refs: docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md,
  docs/governance/AUTO_SEAL_M1_TERMINAL_PROCESS_PLAN_v1.0.md,
  governance/seal_auth_record.py (M1完成品)

本書は M2(接続層)の Phase 1 Proposal である。コードは含まず、実装は本書承認後の
別工程(Phase 2)とする。本書作成時点で コード変更・Migration実行は行っていない。

## 1. M2 目的

M1で構築・独立検証した Auth Model(seal_auth_record: approved_by=human 判定)を、
既存 AUTO_SEAL 経路(SealGovernanceGate)へ安全に接続する。record-only(M1は判定関数の
提供のみ)から Gate判定(verifyがNGなら seal を実行しない)へ移行する。

M2は接続層のみを対象とする。機能追加ではなく、M1の最小実働経路を既存経路へ統合する。

## 2. 接続対象

- governance/seal_governance_gate.py の SealGovernanceGate.execute() / _record_decision_unit()。
  現状: GL7 pre_execution_check が approved なら anchor_update.py を実行し、
  _record_decision_unit が approved_by="system:seal_governance_gate" を記録する。
- 再利用(無変更): governance/seal_auth_record.py の verify_auth_record()(M1完成品)。

## 3. 変更対象ファイル一覧 (Phase 2実装時。本書時点では未変更)

1. governance/seal_governance_gate.py
   - execute() に approval context 引数(approval_ctx、後方互換のデフォルト None)を追加。
   - GL7 pre_execution_check の後、seal実行の前に seal_auth_record.verify_auth_record(approval_ctx)
     を呼び、approved_by=human 等が不合格なら anchor_update.py を実行しない(record化)。
   - _record_decision_unit に Auth Model フィールド(approved_by=human, requester,
     seal_request_id, approval_timestamp, pending_ref)を後方互換で追加記録し、
     approved_by の system 固定を廃止する。
2. tests/test_seal_governance_gate_auth.py (新規)
   - Phase 3 Debug の単体テスト。anchor_update.py の実実行は _seal_runner モックで回避(sandbox)。

## 4. 変更しないファイル一覧

- app.py(/audit/seal の execute(message) 呼び出しは後方互換のまま無変更)
- scripts/ledger/anchor_update.py(frozen)
- governance/seal_auth_record.py(M1完成品、無変更で再利用)
- governance/calc_summary_hash.py / governance/mocka_git_safe_commit.py
- 本番 data/decisions/decision_ledger.jsonl / governance/anchor_record.json /
  mocka-governance-kernel/anchors/anchor_record.json / data/seal_log.json
- API / port / events.db仕様

## 5. Before / After 構成図

Before(現状):
```
caller(app.py /audit/seal) -> SealGovernanceGate.execute(message)
  -> GL7 pre_execution_check
  -> [approved] anchor_update.py 実行
  -> _record_decision_unit(approved_by="system:seal_governance_gate")
```

After(M2):
```
caller -> SealGovernanceGate.execute(message, approval_ctx=None)
  -> GL7 pre_execution_check           (事前フィルタ: aborts があれば停止)
  -> seal_auth_record.verify_auth_record(approval_ctx)   (approved_by=human 必須)
  -> [GL7 ok AND verify ok] anchor_update.py 実行
  -> [verify NG(例: human情報なし/system)] seal を実行せず拒否理由を記録
  -> _record_decision_unit(approved_by=human, requester, seal_request_id,
                           approval_timestamp, pending_ref)
```
既存 app.py の execute(message) 呼び出しは approval_ctx=None のまま動作する。その場合
verify は不合格となり seal は実行されない(Model B: human承認がなければ封印しない)。

## 6. 影響範囲

- MANUAL_SEAL(/audit/seal)経由の挙動が「human承認情報がなければ seal を実行しない」に
  変わる(Model B意図、RB-2是正)。現状 data/seal_log.json は未生成=当該経路は未使用のため
  実害は生じない。
- GL7 は承認者から事前フィルタへ(human必須化により実質格下げ)。
- _record_decision_unit の出力は既存フィールド + Auth Model追加フィールド(後方互換、
  M1のT1で検証済のadditive方式)。既存 reader は追加フィールドを無視して読める。
- execute() のシグネチャは後方互換(新引数はデフォルト None)。既存呼び出し元は無変更で動く。

## 7. Rollback 計画

- Phase 2 実装は governance/seal_governance_gate.py の変更 + 新規テスト追加のみ。
- Rollback = 当該 gate変更の revert + 新規テスト削除。M1(seal_auth_record)は無変更のため
  影響を受けない。
- Migration(Phase 4)を実施しないため本番 anchor/ledger は無変更で、戻し作業は不要。
- 実装は単独 commit とし revert 1回で取り消せる粒度に保つ。

## 8. Debug 計画 (Phase 3、sandbox限定、_seal_runner モックで anchor_update.py 実実行を回避)

| ID | 確認 | 期待 |
|---|---|---|
| D1 | 正常Seal(approval_ctx=human) | verify ok -> (mock)seal実行 |
| D2 | approved_by=human 判定 | 記録の approved_by が human |
| D3 | approved_by=system 拒否 | verify NG -> seal実行されない |
| D4 | 既存Seal互換 | GL7 abort時の既存挙動が不変 |
| D5 | 既存Anchor互換 | mock により実 anchor 非実行・本番anchor不変 |
| D6 | 既存Ledger互換 | 記録が JSONL 後方互換 |
| D7 | 副作用確認 | 本番 anchor/ledger/seal_log 不変 |
| D8 | 再現性確認 | 複数回実行で一致 |

## 9. Verification 計画 (Phase 5、独立監査)

Decision整合 / Artifact整合 / Git履歴整合 / CHANGE_START-DONE整合 / Debug Reportとの一致 /
Migration Readinessとの一致 / Rollback成立性 / 本番副作用ゼロ / M2終了条件充足。
最終判定は PASS / PASS with Open Items / FAIL。

## 10. Non Goals (M2で行わない)

- Decision実在検証の追加(M3)。
- pending_ref 実在検証の追加(M3)。
- RB-1(直接実行境界)の構造変更(M4)。
- Migration実施(本番 anchor/ledger への適用)。
- 機能追加(M2は接続層のみ)。
- 本書自体はコードを含まない(実装は本書承認後の Phase 2)。

## 11. 承認条件 (Phase 2 実装着手の条件)

1. 本書(GOV-PROP-ASM2-001)を きむら博士が承認する。
2. 変更対象(governance/seal_governance_gate.py = Core System File相当)の変更について
   Core System File Human Gate の承認を得る。
3. app.py 無変更・approval_ctx 後方互換・Migration非実施 の方針を承認する。

## 12. History

- 2026-07-13: 初版(v1.0)。M1 CLOSED(DC_20260713_010)を受け、Auth Model を既存
  SealGovernanceGate へ接続する M2 Phase 1 Proposal を起草。接続層のみを対象とし
  M3/M4 は取り込まない。実装は本書承認後(DC_20260713_011)。
