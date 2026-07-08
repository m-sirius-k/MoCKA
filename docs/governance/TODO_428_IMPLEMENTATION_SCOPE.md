# TODO_428 Implementation Scope

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / AUTO_SEAL Pack1(TODO_427)完了後の実装着手

前提: 実装着手指示書(初版)がTODO_428の実データ(本ファイル記載)と一致しない汎用テンプレートであったため、
一次データ(`MOCKA_TODO_ACTIVE.json`のTODO_428エントリ)・`TODO_428_DESIGN_NOTES.md`を正として
きむら博士の裁定によりv2.0指示に修正済み(2026-07-08)。本スコープ文書はv2.0指示に基づく。

## Purpose

`MOCKA_OVERVIEW.json`(legacy、v4.0=2026-06-18で本文凍結)を直接修正せず、一次データから
現在状態を機械的に再集計する`MOCKA_OVERVIEW_CURRENT.json`を生成するGeneratorを新設する。
対象事象: MOCKA_OVERVIEW_STALENESS_REPORT.mdで発見されたTODO_242/325/266/171/215/346の
状態乖離+TODO_209見落とし。

## Input SSOT

| ソース | 用途 |
|---|---|
| `data/MOCKA_TODO_ACTIVE.json`(todos+completed, 69件) | 未着手/進行中/保留の集計元 |
| `data/MOCKA_TODO_ARCHIVE.json`(meta+completed) | ACTIVE層のみでは検出不能な乖離(TODO_215/346型)対応 |
| `data/decisions/decision_ledger.jsonl`(43件、JSONL) | 直近decision件数・最新decision |
| `data/mocka_events.db`(events table, 14,978件) | 直近event件数・最新event timestamp |
| `governance/anchor_record.json`(および`mocka-governance-kernel/anchors/anchor_record.json`、内容同一) | seal/anchor状態 |

## Output Schema

新設ファイル: `data/MOCKA_OVERVIEW_CURRENT.json`(legacyの`C:\Users\sirok\MOCKA_OVERVIEW.json`とは別ファイル)

```json
{
  "meta": { "generated_at": "...", "generator_version": "1.0", "source_hashes": {...} },
  "todo_summary": { "未着手": 0, "進行中": 0, "保留": 0, "完了": 0, "廃止": 0 },
  "recent_decisions": { "count": 0, "latest": {...} },
  "recent_events": { "count": 0, "latest_timestamp": "..." },
  "seal_status": { "anchor_type": "...", "sealed_at_utc": "...", "sealed_summary_hash": "..." },
  "integrity_warnings": []
}
```

`integrity_warnings`は`STATE_INTEGRITY_CHECK_DESIGN_v0.1.md`のチェック1(TODO整合)のみ本実装に含める
(チェック2/3はEvent引用照合・git untracked照合を要し、スコープ外。Non Goals参照)。

## Legacy Compatibility

- `C:\Users\sirok\MOCKA_OVERVIEW.json`(legacy正本、`mocka_mcp_server.py:59 OVERVIEW_PATH`が読む実体)は
  一切変更しない(read-onlyで参照もしない。Generatorは`data/`配下の一次データのみを読む)。
- `data/MOCKA_OVERVIEW.json`(`export_for_cloudflare.py`が生成する`_snapshot_at`付きミラー)も変更しない。
- 既存の`export_for_cloudflare.py`・`mocka_mcp_server.py`・Gateway等の既存処理は無変更。

## Seal Integration

- Generator実行自体はcommitを伴わない読み取り専用の集計処理であり、Human Gate PENDING化は不要。
- 生成物(`MOCKA_OVERVIEW_CURRENT.json`)をcommitする場合は`governance/mocka_git_safe_commit.py`の
  `mocka_git_safe_commit()`経由に統一する(TODO_364準拠)。本実装ではcommit自体は行わず、
  commit判断はHuman Gate(きむら博士)に委ねる(Task 9で停止)。
- 既存seal方式(`anchor_record.json`のhash生成ロジック等)は変更しない。読み取りのみ。

## Non Goals

- `MOCKA_OVERVIEW.json`(legacy)への上書き・本文修正
- 既存seal/hash方式の変更
- 既存TODOデータ構造(`MOCKA_TODO_ACTIVE.json`等)のスキーマ変更
- Integrity Checkチェック2(Event整合)・チェック3(Artifact整合)の実装(チェック1のみ)
- Generatorの自動実行タイミング(定期実行化)の決定 — 手動実行のみとし、定期実行化はHuman Gate別途判断

## Changed Files

- `docs/governance/TODO_428_IMPLEMENTATION_SCOPE.md`(新規、本ファイル)
- `scripts/state/overview_current_generator.py`(新規、Task 3)
- `docs/governance/TODO_428_IMPLEMENTATION_REPORT.md`(新規、Task 8)
- `data/MOCKA_OVERVIEW_CURRENT.json`(新規生成物、Task 3実行時に作成)

## Unchanged Files

- `C:\Users\sirok\MOCKA_OVERVIEW.json`(legacy)
- `data/MOCKA_OVERVIEW.json`(export_for_cloudflareミラー)
- `mocka_mcp_server.py`
- `PlanningCaliber/workshop/mocka-cloudflare/export_for_cloudflare.py`
- `governance/anchor_record.json` / `mocka-governance-kernel/anchors/anchor_record.json`
- `data/MOCKA_TODO_ACTIVE.json` / `data/MOCKA_TODO_ARCHIVE.json`
- `data/decisions/decision_ledger.jsonl`
