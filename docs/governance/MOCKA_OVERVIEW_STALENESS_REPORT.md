# MOCKA_OVERVIEW_STALENESS_REPORT

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / 一次データ非変更のread-only調査結果

## 対象ファイル

| ファイル | 役割 | 根拠 |
|---|---|---|
| `C:\Users\sirok\MOCKA_OVERVIEW.json` | 正本(canonical)。`mocka_mcp_server.py:59` `OVERVIEW_PATH`が指す実体で、`mocka_get_overview`ハンドラ(`mocka_mcp_server.py:405-406`)が実際に読むファイル | `AI_BOOT_HUB.md:38`も同ファイルを「正本」として明記 |
| `C:\Users\sirok\MoCKA\data\MOCKA_OVERVIEW.json` | ミラー(生成物)。`_snapshot_at`フィールド以外は正本とbyte-for-byte一致。`mocka_mcp_server.py`からは読まれない | `gateway/context_builder.py:12`がこちらを読む(Gateway/Cloudflare向け別経路) |

ミラーの生成元は`PlanningCaliber\workshop\mocka-cloudflare\export_for_cloudflare.py`の`copy_files()`(69-80行)+`_inject_snapshot_ts()`(45-53行)。10分周期の`sync_watch.py`デーモンが駆動し、コピー後`data/MOCKA_OVERVIEW.json`等をmocka_git_safe_commit経由でpush。**正本自体は変更しない設計**(スクリプト内コメントで明記)。

## meta/staleness記述(原文)

両ファイル`meta.staleness_note`(root/data共通、`data\MOCKA_OVERVIEW.json:9-14`相当)に既に自己申告あり:

> 「v4.1はmeta欄(updated/version)のみのseal更新(Living Context整合性監査、監査官R01承認、E20260707_491579458f00f/IC_20260705_011対応)。session_history/next_actions/current_issues等の本文はv4.0(2026-06-18)時点のまま未更新であり、TODO_384以降・KN-004・TODO_411-425等の作業が反映されていない。本文の内容更新は別途「自動生成候補→Integrity Check→Human Gate→seal更新」方式の設計確定後に実施する(次工程)。backup(A:/MOCKA_OVERVIEW.json)は本更新時点で2026-06-01版のまま(primaryより古い)であることも確認済み。」

`meta.updated: "2026-07-07"` / `meta.version: "4.1"` — つまりmeta欄だけがseal更新され、本文(session_history/next_actions/current_issues)はv4.0(2026-06-18)で凍結されたまま。今回発見した乖離は、この既知のギャップの具体例である。

## 一次データとの乖離(古い記述一覧)

`MOCKA_TODO_ACTIVE.json`(todos/completed)・`MOCKA_TODO_ARCHIVE.json`と全61件のTODO_ID言及(30種)を突合した結果、確認済みの矛盾は6件、暗黙の見落としが1件。

| TODO_ID | Overview記載 | 実際のstatus | 所在 |
|---|---|---|---|
| TODO_242 | 未着手(`:329,439,448,495,543`) | **進行中** | ACTIVE:236 |
| TODO_325 | 未着手(`:328`) | **保留** | ACTIVE:261 |
| TODO_266 | 保留中(`:326,440`) | **完了** | ACTIVE:1345 |
| TODO_171 | 未着手扱い(deferred、`:461`) | **完了** | ACTIVE:1527 |
| TODO_215 | 未着手扱い(`:517`) | **完了** | ARCHIVE:2620(ACTIVEには不在) |
| TODO_346 | 未対応扱い(`:441`) | **完了** | ARCHIVE:4283(ACTIVEには不在) |
| TODO_209 | statusタグなし(暗黙の見落とし、`:456,553`) | 保留(2026-06-15以降・設計範囲確定済み) | ACTIVE:51 |

うちTODO_215・TODO_346はACTIVE層のみの確認では検出できず、ARCHIVE層まで見て初めて判明した。**将来の再生成方式は、ACTIVE層だけでなくARCHIVE層も参照する必要がある。**

その他確認したTODO_178/205/206/207/239/122/150、およびTODO_011-014/322/208/333/195/345/123/354/151/154/155/384/411は、Overview記載と一次データが一致(矛盾なし)。TODO_206自体はOverview・一次データとも「未着手」で一致しているが、本報告作成中に`interface/impact_analyzer.py`という新規未追跡ファイルの出現を別途確認しており、実装が並行して進行中の可能性がある(本報告の対象外、別途一次データ更新を要する事象として注記のみ)。

## 修正方式候補

1. **手動パッチ(非推奨)**: 該当7箇所の文字列を個別修正。乖離が今後も蓄積するため対症療法に留まる。今回はこの方式を採らなかった(部分修正による帳尻合わせを避ける方針のため)。
2. **既存コピー機構の拡張**: `export_for_cloudflare.py`は現状「正本をそのままコピー+`_snapshot_at`付与」のみで、本文の再生成は行っていない。同ファイル内`export_events()`(26-43行)は`data/mocka_events.db`から`events`テーブルを読み出し`data/events_latest.json`を生成するパターンを既に持っており、これが「一次データから本文JSONを生成する」ための唯一の既存の前例。
3. **本命候補**: `MOCKA_TODO_ACTIVE.json`(+ARCHIVE)・`decision_ledger.jsonl`・`events.db`・seal/anchor metadataから`session_history`/`next_actions`/`current_issues`を組み立てる新規ジェネレータを、`export_events()`のパターンを土台に設計する。staleness_note自身が既に「自動生成候補→Integrity Check→Human Gate→seal更新」という方式を予告しており、`docs/governance/TODO_SSOT_INTEGRATION_DESIGN_v0.1.md:50`にも`export_for_cloudflare.py`をパイプライン段階として図示した既存設計がある。この2つの既存資料を出発点にできる。
4. git側の副作用(commit/push)を伴わせる場合は、`governance/mocka_git_safe_commit.py`経由に統一する(TODO_364準拠、既に`sync_watch.py`もこの経由で実装済み)。

本報告は現状把握のみであり、上記いずれの方式も実装は未着手。次工程はPhase 3(TODO候補ドラフト)を参照。
