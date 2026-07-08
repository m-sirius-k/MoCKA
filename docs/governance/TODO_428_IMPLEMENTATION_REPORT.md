# TODO_428 Implementation Report

作成: Claude-sonnet-5(くろこ) / 2026-07-08

前提: 初版"実装着手指示書 v1.0"は実際のTODO_428(Overview Generator設計)と内容が一致しない
汎用テンプレートだったため、一次データ(`MOCKA_TODO_ACTIVE.json`)・`TODO_428_DESIGN_NOTES.md`を
正としてきむら博士の裁定によりv2.0指示に修正の上で実装した。差分は
[TODO_428_IMPLEMENTATION_SCOPE.md](TODO_428_IMPLEMENTATION_SCOPE.md)冒頭に記録済み。

## Implementation Summary

一次データ(`MOCKA_TODO_ACTIVE/ARCHIVE.json`・`decision_ledger.jsonl`・`mocka_events.db`・
`anchor_record.json`)から`data/MOCKA_OVERVIEW_CURRENT.json`を機械的に再集計するGenerator
(`scripts/state/overview_current_generator.py`)を新設した。legacyの
`C:\Users\sirok\MOCKA_OVERVIEW.json`は読み書き対象外(参照もしない)。

実装中に、`mocka_events.db`のwhen_ts列に文字化け/破損データ(既知事象、TODO_423 Decision
Ledger文字化けと同種)が混在しており、当初`ORDER BY when_ts DESC`(文字列比較)で最新event
取得を実装した結果、`latest_timestamp`が破損レコードの値("pipeline"等)を誤って拾う不具合を
Test実行前に自己発見した。`export_for_cloudflare.py`の既存パターン(`ORDER BY rowid DESC`)に
合わせて修正し、正しい最新timestampを返すことを確認済み。

## Generated Artifact

`data/MOCKA_OVERVIEW_CURRENT.json`(新規)

```json
{
  "meta": {"generated_at": "...", "generator_version": "1.0", "source_hashes": {...}},
  "todo_summary": {"未着手": 37, "保留": 11, "進行中": 6, "完了": 412, "廃止": 14},
  "recent_decisions": {"count": 43, "latest": {...}},
  "recent_events": {"count": 14978, "latest_timestamp": "2026-07-08T07:03:05.617011+00:00"},
  "seal_status": {"anchor_type": "manual_external_post", "sealed_at_utc": "...", "sealed_summary_hash": "..."},
  "integrity_warnings": [
    {"check": "todo_consistency", "todo_id": "TODO_414", "detail": "ACTIVE.completedに分類されているが status='未着手'(完了以外)"}
  ]
}
```

`integrity_warnings`は実行1回目から実際にTODO_414の状態不整合(completedバケットに
status='未着手'のまま残存)を検出した。これはMOCKA_OVERVIEW_STALENESS_REPORT.mdが
発見した既知乖離とは別件の、新規検出事例である。

## Input SSOT

`data/MOCKA_TODO_ACTIVE.json`・`data/MOCKA_TODO_ARCHIVE.json`・
`data/decisions/decision_ledger.jsonl`・`data/mocka_events.db`(events table)・
`governance/anchor_record.json`のみ。手動編集済みoverview・cache・runtime log・
temporary outputは一切参照しない。

## Output Schema

[TODO_428_IMPLEMENTATION_SCOPE.md](TODO_428_IMPLEMENTATION_SCOPE.md)の"Output Schema"節の通り。
JSON Schema形式のファイルは今回新設していない(schemaの構造はDesign Notes/Scope文書内の
サンプルJSONで代替。正式なJSON Schemaファイル化は次工程の検討事項とする)。

## Stale Detection

`MOCKA_OVERVIEW.json`(legacy)への上書き・参照は一切行っていない(Non Goals通り)。
Generator自体が毎回一次データから再集計するため、"本文が古くなる"という事象自体が
構造的に発生しない設計(Design Notes記載の方針通り)。

## Integrity Check

`STATE_INTEGRITY_CHECK_DESIGN_v0.1.md`のチェック1(TODO整合)のうち、宣言済みInput SSOT内で
実装可能な範囲(ACTIVE.completedバケットとstatus値の不整合検知、およびTODO_384正規5値への
正規化)のみを実装した。チェック2(Event整合)・チェック3(Artifact整合)、およびチェック1の
本来定義(一次データ vs 状態表示層の突合)は今回のNon Goalsとし未実装(理由:
状態表示層側の`MOCKA_OVERVIEW.json`比較は本Generatorが参照禁止としている対象と重複するため、
別途の設計判断が必要)。

## Compatibility

- `C:\Users\sirok\MOCKA_OVERVIEW.json`: 未変更(Test Cで確認)
- `data/MOCKA_OVERVIEW.json`(export_for_cloudflareミラー): 未変更
- `mocka_mcp_server.py` / `export_for_cloudflare.py` / Gateway等既存処理: 未変更(コード変更なし)

## Test Results

| Test | 内容 | 結果 |
|---|---|---|
| Test A | generate()を2回実行し、generated_at除外後の内容ハッシュ(SHA256)が一致することを確認 | PASS |
| Test B | todo_summaryの合計件数が一次データ(ACTIVE.todos+ACTIVE.completed+ARCHIVE.completed)の件数合計と一致することを確認 | PASS |
| Test C | Generator実行前後でlegacy `MOCKA_OVERVIEW.json`のSHA256が変化しないことを確認 | PASS |

実行コマンド: `python tests/test_overview_current_generator.py`(3件ともPASS)

## Seal Verification

Generator実行自体はcommitを伴わない読み取り専用処理のため、Human Gate PENDING化は不要
(Design Notes記載の方針通り)。既存seal方式(`anchor_record.json`のhash生成ロジック)は
変更しておらず、本実装は`seal_status`として同ファイルの既存値を読み取って埋め込んでいるのみ。
commit実行自体はTask 9により停止し、Human Gate(きむら博士)の承認を待つ。

## Changed Files

- `docs/governance/TODO_428_IMPLEMENTATION_SCOPE.md`(新規)
- `scripts/state/overview_current_generator.py`(新規)
- `tests/test_overview_current_generator.py`(新規)
- `docs/governance/TODO_428_IMPLEMENTATION_REPORT.md`(新規、本ファイル)
- `data/MOCKA_OVERVIEW_CURRENT.json`(新規生成物、Generator実行により作成)

## Unchanged Files

- `C:\Users\sirok\MOCKA_OVERVIEW.json`(legacy)
- `data/MOCKA_OVERVIEW.json`
- `mocka_mcp_server.py`
- `PlanningCaliber/workshop/mocka-cloudflare/export_for_cloudflare.py`
- `governance/anchor_record.json` / `mocka-governance-kernel/anchors/anchor_record.json`
- `data/MOCKA_TODO_ACTIVE.json` / `data/MOCKA_TODO_ARCHIVE.json`
- `data/decisions/decision_ledger.jsonl`

## Remaining Risks

- **[重要・要Human Gate判断] `data/MOCKA_OVERVIEW_CURRENT.json`は現状`.gitignore`の`data/*`除外に該当し、
  ホワイトリスト(`!data/MOCKA_OVERVIEW.json`等と同様の`!data/MOCKA_OVERVIEW_CURRENT.json`パターン)が
  存在しないため、このままでは`mocka_git_safe_commit()`がエラーを出さず静かにスキップする
  (CLAUDE.md記載のTODO_390型事象)。`.gitignore`への1行追加はgit共有設定の変更であり本実装の
  宣言スコープ(Task 3-8)外のため、本報告で発見のみとし変更は行っていない。commit実行前に
  Human Gateで`.gitignore`へのホワイトリスト追加要否を判断する必要がある。
- integrity_warningsで検出したTODO_414(ACTIVE.completedにあるがstatus='未着手')は、
  本実装のスコープ外(検知のみ、自動修正はしない)。別途Human Gateでの判断が必要。
- チェック2(Event整合)・チェック3(Artifact整合)は未実装。将来的にGeneratorへ追加するか、
  `STATE_INTEGRITY_CHECK_DESIGN_v0.1.md`が提案する分割案(単独`state_integrity_check.py`)で
  別実装するかは次工程の判断事項。
- Generatorの自動実行タイミング(手動のみか定期実行か)は未確定(Non Goals通り、本実装では
  手動実行のみ)。定期実行化する場合はAUTO_SEAL系と同型の"自動処理がHuman Gateを迂回する"
  リスクを内包しないよう、別途Human Gate審査が必要(Design Notes記載の懸念事項)。
- `mocka_events.db`のwhen_ts列に文字化け/破損レコードが15件存在することを本実装の過程で
  再確認した(既知のTODO_423系統の事象と同型)。本Generatorはrowid順採用によって影響を回避
  済みだが、根本原因(文字化けそのもの)はTODO_423側の課題として別管理のまま。
- MCPセッション不通のため、本セッションでの`mocka_write_event`/`mocka_decision_write`による
  正規記録(CHANGE_START/CHANGE_DONE、Decision Ledger登録)は未発行。復旧後の遡及記録が必要
  (TODO_427と同型の扱い)。

## Completion Checklist

- [x] Scope document created
- [x] Impact analysis completed(既存実装なし、重複なしを確認済み)
- [x] Input SSOT fixed
- [x] Output schema created(JSON Schemaファイル化は未実施、構造定義のみ)
- [x] Legacy compatibility confirmed(Test C)
- [x] Seal integration confirmed(既存anchor_record読み取りのみ、方式変更なし)
- [x] Tests PASS(Test A/B/C 3件)
- [x] Implementation report created
- [ ] Commit待機状態(次セクション参照)
