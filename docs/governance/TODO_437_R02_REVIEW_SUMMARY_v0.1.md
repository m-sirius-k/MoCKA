# TODO_437 R02 Review Summary v0.1

作成: Claude-sonnet-5(くろこ) / 2026-07-10 / Human Gate提出用の概要資料・実装は行っていない

目的: 本文書はHuman Gate担当者が、
[TODO_437_R02_REMEDIATION_PLAN_v0.1.md](TODO_437_R02_REMEDIATION_PLAN_v0.1.md)
(全255行)を全文読まずとも短時間で判断できるよう、確定事項・未確定事項・
承認が必要な項目・実装のブロッカー・次フェーズ移行条件を要約したものである。
詳細な根拠・数値・手法は本編(R02 Remediation Plan v0.1)側を参照すること。

## Background

- TODO_437(`/agent/mocka_write_event`応答遅延・timeout=3不一致)は、TODO_413
  (mocka_git_safe_commit.py制度保証化)の実装検証中に副次発見された。
- 2026-07-10のプロファイリングにより、DC_20260710_003が前提としていた原因仮説
  (GATE呼び出しは高速・遅延はWorkingContext側)は実測で否定された
  (GATE単体2.27〜2.33秒、WorkingContext等3関数は合計約0.03秒)。
- この訂正はDecision Ledgerを書き換えず、新規Decision `DC_20260710_005`として
  追記記録した(append-only原則)。
- R01監査(event_id: `E20260710_7368241085333`)にて、本件運用は条件付き承認
  (Mitigation完了・根本原因調査継続)と裁定された。
- 本Review Summaryは、その後作成したR02 Remediation Plan v0.1(根本原因調査計画・
  恒久対策候補の設計書)のHuman Gate提出に向けた概要資料である。

## Current State

| 項目 | 状態 |
|---|---|
| TODO_437 status | 進行中 |
| Mitigation(timeout=3→12統一、10箇所) | 完了 |
| Root Cause Analysis | 設計中(R02 Remediation Plan v0.1作成済み、調査は未実施) |
| Permanent Fix | 未実施 |
| TODO_438(execution_governance.py統合) | 未着手(本件と無関係、一切触れていない) |
| Decision Ledger | DC_20260710_003(無修正)・DC_20260710_005(新規)。本ラウンドでの追加なし(新規裁定事項なしのため) |
| Git | Mitigation分は commit `3755c107f`/`e7a779a4c` で push済み。R02設計書2件は未commit |

## Confirmed Decisions

- `DC_20260710_003`: mocka_git_safe_commit()をGit操作の制度的責任点とする実装決定(無修正、有効)。
- `DC_20260710_005`: DC_20260710_003の原因仮説(GATE高速・WorkingContext側が遅延源)は
  実測により否定された。timeout=12統一は暫定対策(Mitigation)として採用する。
  根本原因は未確定であり継続調査を行う。
- R01監査(`E20260710_7368241085333`): Human Gate運用/Decision Ledger更新/TODO運用/
  コミット表現/検証の5項目いずれも適合。条件: 継続調査完了までは
  「暫定対策完了・恒久対策未完了」の扱いを維持すること。

## Pending Decisions

以下はいずれも未確定であり、R02実装フェーズ移行前にHuman Gateでの判断を要する。

1. GATE単体2.3秒の真因(H1: サブステップ別処理時間 / H2: events.dbロック競合)の
   どちらが支配的か、あるいは両方か。
2. E2Eとの差3.7秒の真因(H3: mocka_mcp_server.pyの単一スレッド直列処理 / H4: I/O待ち)の
   どちらが支配的か、あるいは両方か。
3. 恒久対策候補A〜E(R02 Remediation Plan 4章/12章)のうち、どれを採用するか
   (組み合わせ含む)。
4. TODO_437 Permanent Fix完了判定基準(R02 Remediation Plan 7章)の数値目標
   (暫定案: E2Eレイテンシ1秒未満)の最終確定。

## Human Gate Required Items

R02 Remediation Plan 13章で定義した6つの判断境界(いずれも承認前は着手しない)。

1. 調査実施承認 — 3.1〜3.5の根本原因調査計画そのものの開始可否。
2. 計測コード追加承認 — GATE内部(`process_event()`等)への一時的な計測コード挿入可否
   (py-spy等の非侵襲手法で完結する場合は本境界を経由しない)。
3. threaded=True検証承認 — 本番とは別プロセス・別ポートの複製環境での比較検証実施可否。
4. 恒久対策候補選択承認 — 調査結果を踏まえた候補A〜Eの採用選定。
5. 本番変更承認 — 選定候補の本番環境(mocka_mcp_server.py/app.py/events.db)への適用
   (再起動を伴う変更は必ず本境界を経由)。
6. TODO_437 Close判断 — 完了判定基準(a)〜(e)充足確認後のPermanent Fix完了・Close。

## Implementation Blockers

- R02実装(3章の調査含む)は、上記Human Gate Required Itemsの境界1(調査実施承認)を
  得るまで一切開始しない。
- GATE内部への計測コード挿入(境界2)は、本番稼働中プロセスへの影響可能性があるため、
  py-spy等の非侵襲手法で完結できない場合は独立承認が必要。
- threaded=True検証(境界3)は複製環境の構築が前提であり、本番と同一のデータ・依存関係を
  再現できるかが技術的な未検証事項として残っている。
- events.db書き込み経路の変更(候補B)は、データ整合性への影響が大きいため、他候補
  (A/C/D/E)よりも高いリスク評価としている(R02 Remediation Plan 12章参照)。
- TODO_437の完了判定基準(7章)の数値目標は未確定であり、これが確定しない限り
  境界6(Close判断)には到達できない。

## Next Phase Entry Conditions

以下がすべて満たされた時点で、R02実装フェーズ(3章の根本原因調査)へ移行できる。

1. Human Gateが、R02 Remediation Plan v0.1(本編)およびR02 Review Summary v0.1
   (本資料)の内容を確認済みであること。
2. Human Gate Required Itemsの境界1(調査実施承認)が明示的に承認されていること。
3. R02設計書2件(Remediation Plan / Review Summary)がcommitされていること
   (本ラウンドではcommit未実施。commitはHuman Gate確認後に別途実施する)。
4. 本資料に記載したPending Decisionsのうち、調査着手に必要な前提(境界2・3の
   個別承認要否の判断)が明確になっていること。

移行後も、恒久対策候補の選定(境界4)・本番変更(境界5)・TODO_437 Close(境界6)は、
それぞれ個別のHuman Gate承認を要する独立した境界のままとする。
