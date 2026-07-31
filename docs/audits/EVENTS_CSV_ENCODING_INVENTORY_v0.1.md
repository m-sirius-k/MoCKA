# EVENTS_CSV_ENCODING_INVENTORY_v0.1

data/events.csv に触れる全Pythonモジュールの棚卸し。Encoding Contract の適用対象確定のための入力。

- 作成日: 2026-07-31
- 種別: Observation(観測記録)。Decisionではない
- 上位記録: DC_20260731_001 (status: Active)
- 先行文書: INC_PIPELINE_DEFECT_DEPENDENCY_v0.1.md (RC-A の根拠)
- 本工程での禁止事項遵守: コード修正なし / 既存ファイル編集なし / コミットなし / Decision Ledger登録なし / 設計案の採用判断なし
- 基準commit: baddd113d0202eb08b33bcadf4c115a228234c17 (HEAD)
- 一次データ: docs/audits/events_csv_encoding_inventory.csv (全57行)

---

## 0. 母数の訂正

先行報告で提示した"58ファイル"は、`events.csv` という文字列を含む `.py` ファイルの
単純grep件数であった。本棚卸しで精査した結果、以下のとおり訂正する。

| 段階 | 件数 | 内訳 |
|------|------|------|
| 単純grep(先行報告の58) | 58 | 部分文字列の誤検出を含む |
| 誤検出の除外 | -1 | interface/simulation_layer.py は `sim_events.csv` を指しており別ファイル |
| **精査後の検出総数** | **57** | 以下すべての分類の合計 |

57件のうち、実際に data/events.csv へ I/O を行う現用モジュールは **24件** である。
Encoding Contract の適用対象を検討する際の実質的な母数はこの24件であり、58ではない。

---

## 1. 分類の定義

| 分類軸 | 値 | 定義 |
|--------|----|------|
| status | current | 現用。下記のretired/experimentのいずれにも該当しない |
| | retired | ファイル名に `_backup` `_bak` `_broken` `_old` `app_patch` を含む、または archive/backups 配下 |
| | experiment | experiments/ mocka_v3_eval/ sandbox/ 配下 |
| access | read / write / read+write | data/events.csv に対する実I/Oを検出 |
| | reference-only | パス定数の定義・文中の言及・文字列リテラル内のコードのみで、実I/O呼び出しを検出せず |

---

## 2. 集計

### 2.1 status x access

| status | read | read+write | write | reference-only | 小計 |
|--------|------|------------|-------|----------------|------|
| current | 15 | 6 | 3 | 9 | **33** |
| experiment | 12 | 1 | 0 | 6 | 19 |
| retired | 0 | 4 | 0 | 1 | 5 |
| 合計 | 27 | 11 | 3 | 16 | **57** |

**current かつ実I/Oあり = 24件**(15 + 6 + 3)。

### 2.2 current 24件のencoding規約の分布

| BOMに対する作用 | 件数 | 意味 |
|------------------|------|------|
| 読取:BOM非耐性 (`utf-8`) | 10 | BOMが付いていると先頭列のキーが `\ufeffevent_id` になる |
| 読取:BOM耐性 (`utf-8-sig`) | 8 | BOMの有無を問わず正しく読める |
| 読取:BOM耐性(多段フォールバック) | 3 | `["utf-8-sig","utf-8","shift_jis","cp932"]` を順に試行 |
| 追記:BOM不変 | 7 | 追記モード。BOMを増減させない(実測で確認) |
| 書込:BOM除去 (`"w"` + `utf-8`) | 2 | 全文書換えでBOMを消す |
| 書込:BOM付与 (`"w"` + `utf-8-sig`) | 1 | 新規作成時にBOMを付ける |

読取側だけで **3種類の規約が併存**している(BOM非耐性 / BOM耐性 / 多段フォールバック)。
統一された契約は存在しない。

### 2.3 component別(current 33件)

| component | 件数 |
|-----------|------|
| interface | 12 |
| caliber | 7 |
| (root直下) | 6 |
| tools | 4 |
| data | 3 |
| scripts | 1 |

---

## 3. 書込を行う現用モジュール(11箇所 / 8ファイル)

BOMの状態を変化させうるのは `"w"`(全文書換え)のみである。

| ファイル | 位置 | モード | encoding | BOMへの作用 |
|----------|------|--------|----------|-------------|
| interface/db_helper.py | :77 | w | utf-8-sig | **BOMを付ける**(ファイル不在時のみ実行) |
| tools/mocka_repair_events.py | :45 | w | utf-8 | **BOMを消す** |
| tools/mocka_risk_engine.py | :143 | w | utf-8 | **BOMを消す** |
| interface/db_helper.py | :196 | a | utf-8-sig | 不変 |
| caliber/caliber_monitor.py | :46 | a | utf-8 | 不変 |
| caliber/chat_pipeline/chat_raw_ingest.py | :31 | a | utf-8 | 不変 |
| caliber/chat_pipeline/mocka_chat_capture.py | :79 | a | utf-8 | 不変 |
| caliber/chat_pipeline/mocka_condense_worker.py | :85, :125 | a | utf-8 | 不変 |
| mocka_pipeline.py | :106 | a | utf-8 | 不変 |
| watchdog_mocka_v2.py | :85 | a | utf-8 | 不変 |

RC-A(先行文書3.1)で指摘した"相反する規約を持つ全文書換え主体の併存"は、
本棚卸しにより **BOM付与1箇所 / BOM除去2箇所** と確定した。

---

## 4. 潜在リスクの拡がり

### 4.1 D-4と同型の障害を起こしうるモジュール

BOM非耐性(`utf-8`)で読む現用モジュール10件のうち、ソース中で先頭列名 `event_id` を
参照するコードを含むものは **8件** である。

| ファイル | `event_id` 参照箇所数 |
|----------|----------------------|
| interface/router.py | 4 |
| interface/incident_learner.py | 4 |
| interface/evaluator_dynamic.py | 3 |
| tools/mocka_risk_engine.py | 2 (D-4の確認済み発生箇所) |
| interface/Essence_Direct_Parser.py | 1 |
| interface/language_detector.py | 1 |
| interface/mocka_events_sync.py | 1 |
| tools/mocka_failure_scan.py | 1 |
| tools/mocka_5w1h.py | 0 |
| tools/mocka_repair_events.py | 0 |

**重要な限定**: 上表は"BOM非耐性で events.csv を読む"ことと"ソース中に `event_id`
参照が存在する"ことの2つを別々に確認した結果を並べたものである。当該モジュールが
その `event_id` 参照を **CSVのDictReader由来の行に対して** 行っているか(SQLite由来等
ではないか)は個別未確認である。したがって本節は"D-4と同型の障害が8件で発生している"
ことを主張するものではなく、"確認が必要な候補が8件ある"ことを示す。

確定しているのは tools/mocka_risk_engine.py の1件のみである(先行文書でdry-run実測済み)。

### 4.2 BOM状態の反転構造

```
interface/db_helper.py:77 が実行される (ファイル不在時)
      -> BOM 付与
             |
tools/mocka_risk_engine.py:143 または
tools/mocka_repair_events.py:45 が実行される
      -> BOM 除去
             |
      -> BOM の有無は最後に実行された主体で決まる
             |
      -> BOM非耐性で読む10モジュールの挙動が実行順に依存する
```

現在の data/events.csv はBOM付き(オフセット0に1箇所のみ、実測)。
すなわち直近に全文書換えを行ったのはBOM除去側ではない。

---

## 5. 適用対象の候補分類(選定は行わない)

| 区分 | 件数 | 内容 |
|------|------|------|
| 第1候補 | 24 | current かつ実I/Oあり。契約の実効対象 |
| 要判定 | 9 | current だが reference-only。パス定数のみ保持するもの等 |
| 対象外候補 | 19 | experiment 配下 |
| 対象外候補 | 5 | retired |

### 5.1 current かつ reference-only の9件(要判定)

| ファイル | 内容 |
|----------|------|
| app.py | `EVENTS_CSV` を定義。コメントに"廃止済み変数(互換保持のみ・書き込み禁止)"と明記 |
| mocka_mcp_server.py | `EVENTS_CSV` `FALLBACK_EVENTS` を定義し `.exists()` で存在確認・パス解決のみ行う。コメントに"廃止済み(互換保持のみ)" |
| mocka_caliber_sqlite_patch.py | 文字列リテラル内にI/Oコードを保持するパッチ生成スクリプト。自身は data/events.csv へI/Oしない |
| scripts/write_condense_worker.py | 同上(コード生成スクリプト) |
| interface/pattern_engine_v2.py | `EVENTS_CSV` を定義するが本文で未使用 |
| interface/policy_generator.py | 日本語の方針文中で events.csv に言及 |
| interface/essence_classifier.py | パターン語彙リストの要素として文字列を保持 |
| interface/pattern_registry_seed.py | 文中の言及 |
| make_movement_map.py | 文中の言及 |

このうち app.py と mocka_mcp_server.py は、コード内コメントで自ら廃止済みと宣言している。
宣言と実態が一致していること(実I/Oが無いこと)は本棚卸しで確認した。

---

## 6. 走査方式と限界

### 6.1 方式

静的解析。ファイルごとに以下を実施した。

1. `events.csv` パスへ束縛された定数名を file-local に解決(定数名はモジュールごとに
   `EVENTS` `EVENTS_CSV` `CSV_PATH` `LOG_PATH` 等と異なるため、名前ベースの横断検索では
   別ファイル用の同名定数を誤って拾う)
2. 当該定数またはリテラルを用いた `open()` / `read_text()` / `write_text()` から
   mode と encoding を抽出
3. 直接I/Oが無い場合、同一ファイル内のヘルパ関数へ定数が渡されていないかを見て
   間接I/Oとして解決(例: `read_csv(CSV_PATH)`)
4. `encoding=<変数>` の場合、近傍のフォールバックリスト定義を探索
5. 三重引用符リテラル内のコードは直接I/Oとして数えない

### 6.2 限界(未確認事項)

1. 静的解析であり、動的にパスを組み立てる経路・`subprocess` 経由・他言語からの
   アクセスは検出できない
2. 4.1の限定のとおり、`event_id` 参照がCSV由来かDB由来かは個別未確認
3. モジュール間をまたぐ間接I/O(別モジュールのヘルパへ渡す)は解決していない。
   同一ファイル内のみ解決した
4. `mocka_mcp_server.py` はパス解決のみを行うが、解決されたパスを受け取った側が
   読むか否かは追跡していない
5. 走査範囲は C:\Users\sirok\MoCKA 配下の `.py` に限定される。Cloudflare Workers側、
   他ホスト、`.js` 等の他言語ファイルは未走査
6. status分類はパス・ファイル名の規則に基づく機械分類であり、実際の運用状態
   (現に実行されているか)とは別である。特に experiment 19件・retired 5件が
   本当に実行されないかは未確認

---

## 7. 一次データ

docs/audits/events_csv_encoding_inventory.csv (57行)

列: `path` / `component` / `status` / `access` / `alias_names` / `io_count` /
`encodings` / `bom_effects` / `io_detail`

`io_detail` は `L<行番号>:<mode>:<encoding>:<direct|indirect:関数名()>` の形式。
