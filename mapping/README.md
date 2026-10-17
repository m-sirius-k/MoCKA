# MoCKA Mapping (v0.1)

MoCKA 全体の資産・機能・依存・作業・記憶を、人間と AI が同じ地図から把握するための索引群である。
本ディレクトリは既存資産の索引であり、原本ではない。原本は移動・複製・改名せず、参照のみを行う。

入口は [MASTER_MAP.md](MASTER_MAP.md) である。

## 1. 構成

| ファイル | 役割 |
|---|---|
| [MASTER_MAP.md](MASTER_MAP.md) | 全体の総合地図。目的・原則、主要システム、入口、参照先、作業、接続候補、再利用候補、矛盾、次の実装候補 |
| [ASSET_INDEX.json](ASSET_INDEX.json) | 資産台帳(機械可読)。A001 から A074 まで |
| [DEPENDENCY_MAP.md](DEPENDENCY_MAP.md) | システム・機能・データの依存関係。静的参照に基づく |
| [CAPABILITY_MAP.md](CAPABILITY_MAP.md) | 機能の入口、起動要件、境界、検証状態 |
| [WORK_MAP.md](WORK_MAP.md) | 現在地、TODO の状態、進行中作業、次の候補 |
| [MEMORY_INDEX.md](MEMORY_INDEX.md) | 原則、制度判断、設計判断、実装記録、結果、根拠への索引 |
| [LOCATION_GUIDE.md](LOCATION_GUIDE.md) | 所在・階層の入口。質問から見る場所への対応、背景の根拠、未確認範囲 (2026-10-10 追加) |
| [FILE_LOCATION_INDEX.csv](FILE_LOCATION_INDEX.csv) | 全ファイルの所在、役割タグ、背景の根拠 (機械可読、2026-10-10 追加) |
| [DIRECTORY_INDEX.csv](DIRECTORY_INDEX.csv) | 全ディレクトリの親子関係と件数 (機械可読、2026-10-10 追加) |
| [SCHEMA.md](SCHEMA.md) | 台帳の項目定義と状態語彙 |
| [OPERATING_PROCEDURE.md](OPERATING_PROCEDURE.md) | 運用手順 (作業前確認、検証順序、承認が必要な操作、禁止事項) |
| [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | 未確認事項、矛盾、重複、所在不明 |
| [VERIFICATION_LOG.md](VERIFICATION_LOG.md) | 実行した確認と結果 (稼働確認、件数差の原因、訂正) |
| [IMPLEMENTATION_DECISION_PACKAGE.md](IMPLEMENTATION_DECISION_PACKAGE.md) | 実装判断パッケージ (Phase 6)。HG 判断待ち、判断後の作業、証拠ギャップ。判断ではない |
| [EVENT_GATE_CONTROL_PACKAGE.md](EVENT_GATE_CONTROL_PACKAGE.md) | Event Gate の統制境界の判断パッケージ (Phase 5)。判断ではない |
| [SYNAPSE_CHAIN_VERIFICATION.md](SYNAPSE_CHAIN_VERIFICATION.md) | Mapping -> Memory -> Synapse の読取経路の実証記録 |
| [verify_mapping.py](verify_mapping.py) | 静的検証ツール (読取のみ)。証拠種別と状態の整合を強制 |
| [verify_memory_chain.py](verify_memory_chain.py) | Q-34 / Q-35 / Q-38 を再現する読取専用スクリプト (書込なし、Memory のハッシュで確認) |
| [HG_DECISION_PACKAGE.md](HG_DECISION_PACKAGE.md) | HG 判断待ち事項 (Q-39, Q-40, Q-34, Q-37, Q-36, Q-41, Q-38) の証拠付き資料。判断ではない |
| [evaluate_memory_retrieval.py](evaluate_memory_retrieval.py) | Memory 検索の評価 (ケース, 候補の比較)。Memory 本体は変更しない |
| [verify_decision_allocation.py](verify_decision_allocation.py) | Decision ID 採番の隔離再現 (一時 SQLite のみ、本番 DB は開かない) |

既存資料との関係: 既存の KUROKO PC 監査 (ルート直下の `KUROKO_PC_*.md`) は、MASTER_MAP と MEMORY_INDEX から参照する。重複して作成していない。

## 2. 状態語彙

`PRESENT` / `CONNECTED` / `USED` / `ENFORCED` / `VERIFIED` / `UNKNOWN` / `NOT_VERIFIED`。詳細は [SCHEMA.md](SCHEMA.md) を参照する。

存在すること (PRESENT) は、利用可能 (USED) を意味しない。コード上の参照 (CONNECTED) は、実行時の接続や結果を証明しない。

## 3. 利用方法

1. 全体を把握する: [MASTER_MAP.md](MASTER_MAP.md) を読む。
   所在を探す場合は [LOCATION_GUIDE.md](LOCATION_GUIDE.md) から入る。
   ファイル名・属性・資産IDで検索する場合は `search_index/`（ローカル検索 UI）を使う。手順は [../search_index/README.md](../search_index/README.md)。
2. 特定の資産を探す: [ASSET_INDEX.json](ASSET_INDEX.json) を `asset_id` または `path` で検索する。
3. 機能の呼び方を知る: [CAPABILITY_MAP.md](CAPABILITY_MAP.md) を読む。
4. 次の作業を決める: [WORK_MAP.md](WORK_MAP.md) と [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) を読む。

## 4. 検証

```bash
PYTHONUTF8=1 python mapping/verify_mapping.py
```

検査内容: JSON の構文、必須項目、語彙、ID 参照、パスの存在、mapping/*.md の相対リンク。書込は行わない。終了コードは 0 が成功、1 が失敗。

## 5. 更新方法

1. 資産を追加・変更する前に、`asset_id` と `path` で既存エントリの重複を確認する。
2. 実際に確認した内容だけを記載する。未確認の項目は `null` または `UNKNOWN` / `NOT_VERIFIED` とする。
3. `last_verified` を更新する。
4. `verify_mapping.py` を実行し、FAIL がないことを確認する。
5. 既存の原本ファイルは変更しない。

## 6. 注意

- 本ディレクトリの記載は作成時点の静的確認の結果であり、現在の実装状態を証明しない。
- 本ディレクトリは HG の設計選択、実装認可、テスト実行認可を与えない。
- 本ディレクトリの作成時点では、サーバーの起動、テストの実行、git 操作、events.db への書込は行っていない。
- CLAUDE.md が求める CHANGE_START / CHANGE_DONE の記録は、本作業では events.db へ書き込んでいない。詳細は [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) §7 を参照する。
- 本ディレクトリ内の文書は、CP932 汚染防止規約 (CLAUDE.md) に従い、非 ASCII の装飾記号を使わない。

