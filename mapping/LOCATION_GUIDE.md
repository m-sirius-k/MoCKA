# MoCKA 所在・階層ガイド（LOCATION_GUIDE）

この文書は `mapping/` の入口である。「何がどこにあるか」「その背景をどの資料で確認するか」を、人間とAIが同じ手順で探せるように案内する。
本文に資産の詳細を重複して書かない。詳細は下表の帳簿を参照する。

区分: 所在と階層は、今回の読取専用走査（`C:\Users\sirok\MoCKA`）と既存索引から確認した実測値。背景は証拠がある項目だけを記載し、残りは `UNKNOWN` とする。

## 1. まず見る表（質問から所在へ）

| 知りたいこと | 見る場所 | 種別 |
|---|---|---|
| MoCKA の全体地図（入口） | [MASTER_MAP.md](MASTER_MAP.md) | 既存索引 |
| 既存の資産台帳（74件、機械可読） | [ASSET_INDEX.json](ASSET_INDEX.json) | 既存索引 |
| ファイル単位の所在・背景の根拠 | [FILE_LOCATION_INDEX.csv](FILE_LOCATION_INDEX.csv) | 今回生成 |
| ディレクトリ単位の階層・件数 | [DIRECTORY_INDEX.csv](DIRECTORY_INDEX.csv) | 今回生成 |
| 全資産（関数・クラス・API・DB 等）の台帳 | [../docs/governance/MOCKA_ASSET_REGISTRY_20261010_001.csv](../docs/governance/MOCKA_ASSET_REGISTRY_20261010_001.csv) | 今回生成（前回作業） |
| 資産間の接続（呼出し・読書き・認可など） | [../docs/governance/MOCKA_CONNECTION_REGISTRY_20261010_001.csv](../docs/governance/MOCKA_CONNECTION_REGISTRY_20261010_001.csv) | 今回生成（前回作業） |
| 21 ノードの統合 Mapping（状態付き） | [../docs/governance/MOCKA_INTEGRATED_MAPPING_20261010_001.md](../docs/governance/MOCKA_INTEGRATED_MAPPING_20261010_001.md) | 前回作業 |
| 機械検証の結果と除外範囲 | [../docs/governance/MOCKA_MAPPING_VALIDATION_20261010_001.md](../docs/governance/MOCKA_MAPPING_VALIDATION_20261010_001.md) | 前回作業 |
| 正本のイベント台帳（DB） | `data/mocka_events.db`（読取専用。本文書は中身を開かない） | 実データ |
| 決定台帳（Decision Ledger） | `data/decisions/decision_ledger.jsonl` | 実データ |
| HG（Human Gate）の状態機械 | `phi_os/human_gate.py` | 実装 |
| Event Gate（イベント受理） | `phi_os/event_gate.py` | 実装 |
| MCP サーバー（ツール群） | `mocka_mcp_server.py` | 実装 |
| Runtime Gate（実行境界） | `core_kernel/orchestra/runtime_gate.py` | 実装 |
| 認可レコードの生成 | `core_kernel/governance/runtime/rcl/authorization.py` | 実装 |
| Memory 本体 | `memory/`（MoCKA 3.0 系） | 実装・データ |
| Memory（core_kernel 系） | `core_kernel/memory_core/` | 実装 |
| Synapse / Knowledge Activation の設計 | `docs/governance/ACTIVATION_POLICY_v0.1.md` | 設計 |
| Synapse の既存監査 | `KUROKO_PC_SYNapse_MASTER_MAP_20261003.md`（ルート直下） | 監査 |
| AI 向けの起動規約と設定 | `.claude/CLAUDE.md` | 設定 |
| 起動入口（サーバー等） | `app.py`（他は FILE_LOCATION_INDEX.csv の ENTRY_OR_SERVICE で絞る） | 実装 |
| テスト | `tests/`、`phi_os/tests/`（FILE_LOCATION_INDEX.csv の TEST で絞る） | テスト |
| 過去版・バックアップ・旧資料 | `docs/archive/`（本走査の除外対象。FILE_LOCATION_INDEX.csv には含まれない）、および FILE_LOCATION_INDEX.csv の HISTORY_OR_ARCHIVE | 履歴 |
| 作業の現在地と未解決事項 | [WORK_MAP.md](WORK_MAP.md)、[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | 既存索引 |
| これまでの検証の経緯 | [VERIFICATION_LOG.md](VERIFICATION_LOG.md) | 既存記録 |
| 外部に置かれた正本宣言（リポジトリ外） | `C:/Users/sirok/MOCKA_OVERVIEW.json`（本走査の対象外。存在は確認済み、中身は未読） | リポジトリ外 |

## 1a. 検索で探す（Mapping から検索へ）

- ローカル検索 UI（読取専用、127.0.0.1 のみ）: `python -B -m search_index.server --port 5110` を起動し、http://127.0.0.1:5110/ を開く。
- 手順と範囲は [search_index/README.md](../search_index/README.md)。検索結果の詳細から、この資産ID・参照元の `mapping/*.md`・接続台帳の関連へ戻れる。
- 検索結果は証拠候補であり、認可ではない。結果がないことは存在しないことを意味しない。

## 2. 全体の階層（実測）

- ファイル総数 7666（走査対象）、ディレクトリ数 1072（ルートを含む）、最大階層 10。
- 除外したディレクトリ（名前による）: `.git`、`.venv`、`venv`、`archive`、`__pycache__`、`node_modules`。除外したファイル 7134 件。除外は存在しないことを意味しない（本文書の対象外）。
- 階層別のディレクトリ数: 深さ0: 1, 深さ1: 87, 深さ2: 203, 深さ3: 169, 深さ4: 205, 深さ5: 117, 深さ6: 77, 深さ7: 82, 深さ8: 94, 深さ9: 14, 深さ10: 23

トップレベルの件数（再帰、上位）:

| トップ | 再帰ファイル数 | 直下ファイル数 | 文書化（mapping 内で言及されるディレクトリ数） |
|---|---|---|---|
| `data` | 1805 | 176 | 12 |
| `records` | 1423 | 0 | 2 |
| `PlanningCaliber` | 923 | 4 | 7 |
| `docs` | 776 | 21 | 6 |
| `runtime` | 575 | 324 | 6 |
| `core_kernel` | 180 | 1 | 6 |
| `interface` | 121 | 111 | 8 |
| `tools` | 109 | 76 | 10 |
| `governance` | 98 | 38 | 10 |
| `scripts` | 78 | 19 | 1 |
| `phi_os` | 77 | 21 | 10 |
| `experiments` | 74 | 39 | 2 |
| `audit` | 46 | 4 | 6 |
| `network` | 36 | 0 | 0 |
| `structural` | 35 | 35 | 1 |
| `caliber` | 33 | 7 | 5 |
| `semantic` | 28 | 8 | 1 |
| `mocka-governance-kernel` | 27 | 1 | 0 |
| `gateway` | 26 | 24 | 6 |
| `mocka_v3_eval` | 24 | 24 | 0 |
| `tests` | 24 | 15 | 1 |
| `canonical` | 21 | 0 | 0 |
| `mocka3` | 21 | 5 | 3 |
| `production_certification` | 19 | 1 | 0 |
| `mapping` | 18 | 18 | 6 |

## 3. 分類（実態から。固定の体系ではない）

ファイル 1 件に複数の役割タグが付く。タグは、拡張子・ファイル名・パス・索引の記載から機械的に付けた。最終的な分類ではない。

| タグ | 件数 | 付与の根拠 |
|---|---|---|
| DATA_OR_LEDGER | 3286 | 拡張子（json/jsonl/csv/db 等）または名前に ledger |
| SOURCE_CODE | 2022 | 拡張子（py/js/ps1/sh 等） |
| DOCUMENT | 1764 | 拡張子（md/txt/docx/html/pdf 等） |
| HISTORY_OR_ARCHIVE | 1024 | 名前・パスに backup/bak/old/archive/_vN/copy 等 |
| VERIFICATION_OR_AUDIT | 415 | 名前に verify/validat/audit/check/reconcil/forensic |
| SPEC_OR_DESIGN | 340 | 名前に design/spec/contract/schema/architecture/proposal |
| LOG_OR_GENERATED | 327 | 拡張子 log、または名前に output/generated/snapshot/dump |
| UNCLASSIFIED | 300 | 上記のどれにも当たらない |
| TEST | 227 | 名前が test_、または tests/test のパス |
| BINARY_OR_MEDIA | 201 | 画像・圧縮・Office・DB 付随ファイル |
| ENTRY_OR_SERVICE | 72 | 静的に起動入口と判定（scan の PROCESS_ENTRY） |
| CONFIG | 56 | `.claude/`・`.codex/`、`.env*`、名前に config/settings、toml/ini/yaml 等 |
| API_OR_MCP | 43 | 静的に HTTP ルートまたは MCP ツールを含む（scan） |

scan の登録役割（REG_*。資産台帳の役割資産に由来）:

- GATE_MODULE: 80
- MEMORY_ASSET: 58
- DB_FILE: 35
- LEDGER: 28
- CONFIG_FILE: 18
- SYNAPSE_ASSET: 15
- DB_SIDECAR: 14

UNCLASSIFIED は 300 件（3.9%）。

## 4. 背景（歴史）の根拠と、その範囲

ファイルの背景を示す証拠は 3 種類あり、それぞれの件数は次のとおり。

| 根拠 | 件数 | 意味 |
|---|---|---|
| GIT_FIRST_ADD（git で最初に追加されたコミット） | 4174 | 追跡済みファイルの初回追加日。作成日の有力な根拠 |
| FILENAME_DATE（名前に日付） | 2920 | 名前の日付は作成・版の目安。作成日そのものとは限らない |
| NONE（根拠なし） | 2164 | 追跡されず名前にも日付がない。背景は UNKNOWN |

- `mtime_observed`（更新時刻）は作成日の根拠として使わない（`mtime_is_creation_evidence` は全件 NO）。
- 追跡済みファイル 4279 件のうち、初回追加を特定できたのは 4174 件。残りは UNKNOWN（パス表記の差などによる）。
- 追跡されていないファイル（未追跡・無視設定）は git 履歴がない。
- 現在の `mapping/` 配下の更新時刻は 2026-10-10T15:27:39+09:00 から 2026-10-10T19:42:20+09:00 の範囲で、今日の作業による書換えの時刻である。

## 5. `mapping/` 自体の経緯（確認できた範囲）

- `mapping/` はすべて git 未追跡（追跡ファイル 0 件）。ディレクトリとしてのコミット履歴は存在しない（NOT_FOUND）。
- 各ファイルの内部記載: `MASTER_MAP.md` の作成日は 2026-10-10。`VERIFICATION_LOG.md` には 2026-10-10 の節が 15 件あり、段階ごとの訂正と結論が記録されている。過去の版の記録は見つからなかった（NOT_FOUND）。
- git のコミットメッセージに mapping を含むものは 42 件あるが、`mapping/` ディレクトリそのものの変更ではない。
- 今回の所在索引の作成日は本作業（2026-10-10）。上記の既存索引とは別に、ファイル単位・ディレクトリ単位の機械可読の索引を追加した。

## 6. 未確認・未収集の範囲

- 除外ディレクトリ（`archive`、`.venv`、`venv`、`.git` など）の内容は本索引に含まれない。特に `docs/archive/` は履歴資料の所在として重要だが、本走査の対象外。
- 秘密情報・資格情報（名前から判定した 47 件。内容は開いていない）。
- リポジトリ外の参照先（`C:/Users/sirok/MOCKA_OVERVIEW.json` など）の中身。
- 他の端末・クラウド・外部リポジトリ（`PlanningCaliber/` 以下の一部リポジトリは独自の remote を持つ。詳細は資産台帳の REPOSITORY 行）。
- DB の中身、実行状態、サービスの稼働は未確認。

## 7. 使い方（AI と人間共通）

1. 目的の語で [FILE_LOCATION_INDEX.csv](FILE_LOCATION_INDEX.csv) を検索する（`path`、`role_tags`、`registry_roles`）。
2. 背景を見るときは `git_first_added`、`filename_date`、`background_evidence` の順に確認する。`mtime_observed` は参考にとどめる。
3. 階層を見るときは [DIRECTORY_INDEX.csv](DIRECTORY_INDEX.csv) の `parent_directory` をたどる。
4. 中身や関係を確認するときは、前回作業の資産台帳・接続台帳を `asset_id` または `canonical_path` で引く。
5. 状態（存在・接続・利用・強制・検証）は、資産の状態語彙（[SCHEMA.md](SCHEMA.md)）に従う。存在すること（PRESENT）は利用可能（USED）を意味しない。

## 8. 再生成

- `FILE_LOCATION_INDEX.csv` と `DIRECTORY_INDEX.csv` は、資産台帳（前回作業）と `git log --all --diff-filter=A --name-only` の出力から作った。
- 生成手順のスクリプトは作業用の一時領域に置き、リポジトリには含めていない。再生成には同じ入力が必要（NOT_REPRODUCIBLE_FROM_REPO_ALONE）。

## 9. 既存索引との関係

- 既存の `ASSET_INDEX.json`（A001〜A074）は手作業の台帳。旧来の 60 件の項目は変更していない。追加分の 14 件は 2026-10-18 に SCHEMA.md の項目へ正規化した（変更履歴は VERIFICATION_LOG.md）。
- 新しい索引（FILE・DIRECTORY）は、手作業台帳の代わりではなく、所在の網羅のための補完。
- 既存の [README.md](README.md) と [MASTER_MAP.md](MASTER_MAP.md) からこの文書へ案内する。
