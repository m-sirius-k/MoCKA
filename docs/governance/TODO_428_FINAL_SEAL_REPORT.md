# TODO_428 Final Seal Report

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / commit実行前の最終封印文書

## Objective

MoCKAの状態認識を"人間が手で書く自由記述"から"一次データから機械的に再構成できる
表示層"へ転換すること。単なる便利スクリプトの追加ではなく、状態表示の正しさを
構造(Structure)で担保し、記録(Record)を積み重ね、検証(Verification)可能な形に
するというMoCKAの三要素をこの一角で具体化すること。

## Historical Background

`MOCKA_OVERVIEW.json`(legacy)は本文(session_history/next_actions/current_issues)を
人間が手動更新する運用だった。2026-07-08の状態監査(監査官R01)で、本文がv4.0
(2026-06-18)時点のまま凍結され、meta欄のみseal更新される状態が続いていたことが判明し、
TODO_242/325/266/171/215/346(計6件)の状態乖離とTODO_209の見落としが発見された
(MOCKA_OVERVIEW_STALENESS_REPORT.md)。この事象を受け、状態表示を"書く"ものから
"都度計算する"ものへ移行する方針がTODO_428として立てられ、`TODO_428_DESIGN_NOTES.md`
(2026-07-08、設計深化のみ)で入力SSOT・出力schema・legacy非破壊方針が固められた。

## Problem Before

- 状態表示層(MOCKA_OVERVIEW.json)の本文が一次データと無関係に固定化し、更新されない限り
  自動的に陳腐化する構造だった
- "ファイルが存在する"を"実装完了"と誤推論するリスクも別途確認されており
  (`STATE_INTEGRITY_CHECK_DESIGN_v0.1.md`)、状態表示の信頼性そのものに疑義があった
- 乖離が起きても検知する仕組みがなく、次に監査するまで気づかれない設計だった

## Implemented Solution

`scripts/state/overview_current_generator.py`を新設し、`data/MOCKA_TODO_ACTIVE.json`・
`data/MOCKA_TODO_ARCHIVE.json`・`data/decisions/decision_ledger.jsonl`・
`data/mocka_events.db`・`governance/anchor_record.json`のみを入力として
`data/MOCKA_OVERVIEW_CURRENT.json`を毎回ゼロから再集計する。本文相当の情報
(todo_summary/recent_decisions/recent_events/seal_status)は自由記述を一切含まず、
すべて一次データからの機械的な集計値のみで構成される。加えて、TODO_384正規5値への
正規化を通じてstatus/bucket不整合を検知する`integrity_warnings`をGenerator自体に
組み込んだ(STATE_INTEGRITY_CHECK_DESIGN_v0.1.mdのチェック1の実装可能な範囲)。

## Architecture Change

```
変更前:
一次データ(TODO/Ledger/Events/Seal) -- (無接続、手動転記のみ) --> MOCKA_OVERVIEW.json(手動更新・陳腐化する)

変更後:
一次データ(TODO/Ledger/Events/Seal)
        v
overview_current_generator.py(毎回全量再集計、書込先はlegacyと別ファイル)
        v
data/MOCKA_OVERVIEW_CURRENT.json(Derived Artifact、再生成可能)
        v
integrity_warnings(検知のみ、自動修正はしない)
        v
Human Governance(きむら博士の判断)
```

legacyの`C:\Users\sirok\MOCKA_OVERVIEW.json`は本変更で一切触れておらず、
Historical Snapshotとしてそのまま存続する(過去の記憶を消さない方針、R01)。

## Verification

| 項目 | 内容 | 結果 |
|---|---|---|
| Test A | generate()を2回実行、generated_at除外後のcontent hash(SHA256)一致 | PASS |
| Test B | todo_summary合計が一次データ件数合計と一致 | PASS |
| Test C | Generator実行前後でlegacy MOCKA_OVERVIEW.jsonのSHA256が不変 | PASS |
| Runtime確認 | Repository=Runtimeであることを確認済み(app.py/mocka_mcp_server.py) | PASS |
| Safe-commit dry-run | 対象ファイルをgit add→ステージ確認→is_core_system_file()判定(全件False)→git restore --stagedで解除。実commitなし | PASS |

`mocka_git_safe_commit()`には`--dry-run`引数は存在しない(実装未確認のまま前回指示書に
記載されていた誤り)。目的(commitせずに対象を確認する)を満たすため、同関数が内部で行う
git add→ステージ済みファイルのcore判定という手順のみを手動で再現し、最後に必ず
`git restore --staged`で解除した。commitは一度も実行していない。

## Generated Artifact Policy

`data/MOCKA_OVERVIEW_CURRENT.json`はGit管理対象外のまま維持する。理由は、この
ファイルがGeneratorの実行結果(Derived Artifact)であり、一次データさえ保全されていれば
いつでも同一内容を再生成できるため、Artifact自体を保存することよりArtifactを
再生成できる能力(Generatorコードとテスト)を保全することの方がMoCKA的に重要という
判断による。`.gitignore`へのホワイトリスト追加(`!data/MOCKA_OVERVIEW_CURRENT.json`)は
今回行わない。

## Discovered Integrity Findings

`docs/governance/TODO_428_DATA_FINDINGS.md`に記録済み。

1. TODO_414: `MOCKA_TODO_ACTIVE.json`の`completed`配列に分類されているが
   `status`フィールドが`未着手`のまま(status/bucket不整合)。修正はTODO_428のスコープ外。
2. `mocka_events.db`のwhen_ts列に文字化け/破損レコードが15件存在(TODO_423系統と同型)。
   Generator側は`ORDER BY rowid DESC`への変更で影響を回避済みだが、根本原因は別課題。

これらはTODO_428の不具合ではなく、Generatorが状態監査能力を獲得したことにより
新規発見されたものである。

## Deferred Issues

- `.gitignore`へのホワイトリスト追加要否(Generated Artifact Policy参照、今回は現状維持)
- TODO_414のstatus/bucket不整合修正(別TODO化してHuman Gate判断)
- `mocka_events.db` when_ts列の根本的な文字化け修正(TODO_423側の課題として別管理)
- Integrity Checkチェック2(Event整合)・チェック3(Artifact整合)の実装
- Generatorの定期実行化要否(現状は手動実行のみ)

## Commit Scope

以下5ファイルをcommit対象として最終固定する(`TODO_428_DATA_FINDINGS.md`は
"実装変更ではなくGeneratorが発見した制度的証跡"というきむら博士の判断により含める)。

- `scripts/state/overview_current_generator.py`
- `tests/test_overview_current_generator.py`
- `docs/governance/TODO_428_IMPLEMENTATION_SCOPE.md`
- `docs/governance/TODO_428_IMPLEMENTATION_REPORT.md`
- `docs/governance/TODO_428_DATA_FINDINGS.md`

含めない: `data/MOCKA_OVERVIEW_CURRENT.json`(Generated Artifact Policy参照)。

## Final Status

- TODO_428 Implementation: 完了
- TODO_428 Verification: 完了
- TODO_428 Documentation: 完了(本ファイルを以て100%)
- TODO_428 Commit: 未実施(Human Gate承認待ち)
- TODO_428 Seal: 未完了(commit実行後、`mocka_git_safe_commit()`経由でのcommit完了を以て封印とする)
