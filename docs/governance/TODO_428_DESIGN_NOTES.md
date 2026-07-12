# TODO_428_DESIGN_NOTES

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / 設計深化のみ、generator実装・overview上書きは行っていない

対象TODO: TODO_428「MOCKA_OVERVIEW_CURRENT_GENERATION」(status: 未着手)。関連: `MOCKA_OVERVIEW_STALENESS_REPORT.md`、`STATE_INTEGRITY_CHECK_DESIGN_v0.1.md`

## 入力SSOT(確定)

| ソース | 用途 |
|---|---|
| `data/MOCKA_TODO_ACTIVE.json`(todos+completed) | 進行中/未着手/保留のタスク一覧、直近next_actions候補 |
| `data/MOCKA_TODO_ARCHIVE.json` | 完了・廃止済みタスク。TODO_215/346型(ACTIVE層のみでは検出不能な乖離)対応のため必須 |
| `data/decisions/decision_ledger.jsonl` | 直近のHuman Gate承認履歴、current_issuesの根拠 |
| `data/mocka_events.db`(events テーブル) | session_history、直近イベントサマリー |
| seal metadata(`governance/anchor_record.json`、`mocka-governance-kernel/anchors/anchor_record.json`) | phase/seal状態表示 |

**正本パスの原則**: `C:\Users\sirok\MOCKA_OVERVIEW.json`(mocka_mcp_server.py:59 `OVERVIEW_PATH`)が読まれる実体であり、Generatorの出力先候補としてもこちらを起点に検討する。`data/MOCKA_OVERVIEW.json`は`export_for_cloudflare.py`が生成する`_snapshot_at`付きミラーであり、Generator設計とは別レイヤー(既存のコピー機構をそのまま維持)。

## 出力schema(案)

新設ファイル名は`MOCKA_OVERVIEW_CURRENT.json`(またはユーザー案の`MOCKA_STATE_CURRENT.json`)。既存`MOCKA_OVERVIEW.json`(legacy)とは別ファイルとし、**legacyへの上書きは行わない**(過去の記憶を消さない、というR01方針に対応)。

```
{
  "meta": { "generated_at": "...", "generator_version": "...", "source_hashes": {...} },
  "todo_summary": { "未着手": [...], "進行中": [...], "保留": [...] },  // ACTIVE+ARCHIVEから機械的に集計
  "recent_decisions": [...],   // decision_ledger.jsonl直近N件
  "recent_events": [...],      // events.db直近N件
  "seal_status": {...},        // anchor_record.jsonから
  "integrity_warnings": [...]  // STATE_INTEGRITY_CHECK_DESIGN_v0.1.mdの3チェック結果
}
```

本文(session_history/next_actions/current_issues相当)は**人間が書く自由記述ではなく、一次データから機械的に集計した値のみ**とする。これがlegacy版との本質的な違い(手動更新の陳腐化を構造的に排除する)。

## stale検出

`STATE_INTEGRITY_CHECK_DESIGN_v0.1.md`のチェック1(TODO整合)をそのまま踏襲。Generator自体が毎回一次データから再集計するため、原理的に「本文が古くなる」という事象自体が発生しなくなる(手動更新のstaleness_noteのような免責事項が不要になる設計)。

## Integrity Check連携

`STATE_INTEGRITY_CHECK_DESIGN_v0.1.md`のチェック1-3(TODO整合/Event整合/Artifact整合)の出力を、`integrity_warnings`フィールドとしてそのまま埋め込む。Generator実行のたびに整合性チェックも同時に走る一体型設計とする(チェックのみを先行して単体スクリプト化する分割案も設計文書側に残してある)。

## seal連携設計

Generator実行自体は「状態表示の再集計」であり、`anchor_update.py`のようなgit commitを伴うseal操作ではない。ただし出力ファイル(`MOCKA_OVERVIEW_CURRENT.json`)自体の変更履歴を残すため、Generator実行後にcommitする場合は`mocka_git_safe_commit()`経由に統一する(TODO_364準拠)。Generatorの自動実行タイミング(手動起動のみか、定期実行かは未確定)自体もHuman Gate要否の検討対象とする — 定期自動実行にする場合、AUTO_SEAL_50EVT/日次分岐で今回是正したのと同型の「自動処理がHuman Gateを迂回する」リスクを内包しないよう、実行そのものはPENDING不要(読み取り専用の集計処理でありcommitを伴わない限り)だが、**commit・push判断は必ず人間を介する**設計とする。

## 実装着手条件(再掲)

AUTO_SEAL Pack1のcommit・Phase 4 Close確定後に着手する。本ノートはその前段の設計深化のみであり、コードは一切書いていない。
