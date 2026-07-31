# PHI-OS Encoding Contract v0.1

data/events.csv に対する読み書き規約。RC-A(DC_20260731_002)に基づく設計文書。

- 作成日: 2026-07-31
- 種別: Design(設計文書)。**NON-CANONICAL / 未実装**
- 根拠Decision: DC_20260731_002 (RC-A採択、status: Active)
- 上位記録: DC_20260731_001
- 状態: Draft。本文書に基づくコード変更は未着手
- 基準commit: baddd113d0202eb08b33bcadf4c115a228234c17
- 一次データ: docs/audits/events_csv_encoding_inventory.csv

---

## 1. スコープ

### 1.1 対象

| 項目 | 内容 |
|------|------|
| 対象データ | C:\Users\sirok\MoCKA\data\events.csv |
| 対象モジュール | 同ファイルへ実I/Oを行う現用Pythonモジュール 24件 |
| 契約の目的 | D-4(BOM付きCSVによるevent_id列の全損)の再発防止と、規約分裂の解消 |

### 1.2 対象外

DC_20260731_002 の裁定に従い、以下は本v0.1の対象外とする。

- PHI-OS全体、および data/events.csv 以外のデータファイル(拡張は別Decision)
- experiment 配下 19件 / retired 5件
- current かつ reference-only の 9件(第4節で要判定として扱う)

文書名は DC_20260731_002 の指示に従い PHI-OS Encoding Contract とするが、
v0.1 の適用範囲は上記のとおり data/events.csv に限定される。名称の適用範囲と
実効範囲が一致していない点は、拡張時に解消されるべき差分として明記しておく。

---

## 2. 現状の規約分裂(契約が必要な理由)

現用24件の実測分布。

| 作用 | 件数 | 具体 |
|------|------|------|
| 読取:BOM非耐性 (`utf-8`) | 10 | BOM付きだと先頭列のキーが `\ufeffevent_id` になる |
| 読取:BOM耐性 (`utf-8-sig`) | 8 | BOMの有無を問わず正しく読める |
| 読取:BOM耐性(多段フォールバック) | 3 | `["utf-8-sig","utf-8","shift_jis","cp932"]` を順に試行 |
| 追記:BOM不変 | 7 | 追記モード。BOMを増減させない |
| 書込:BOM除去 (`"w"`+`utf-8`) | 2 | tools/mocka_risk_engine.py:143 / tools/mocka_repair_events.py:45 |
| 書込:BOM付与 (`"w"`+`utf-8-sig`) | 1 | interface/db_helper.py:77 |

BOM状態は最後に実行された全文書換え主体によって反転する。現物はBOM付きである。

---

## 3. 契約条項

### 3.1 正規形の定義

**条項 E-1(必須)**: data/events.csv の正規形は **BOMなしUTF-8** とする。

選定の根拠は対称的ではない。以下は Python の codec 仕様に基づく事実である。

| ファイルの状態 | `utf-8` で読む(10件) | `utf-8-sig` で読む(8+3件) |
|----------------|----------------------|---------------------------|
| BOMなし | 正常 | 正常 |
| BOMあり | **先頭列のキーが壊れる** | 正常 |

すなわち BOMなしを正規形とすれば、現存する21件の読取側はすべて無改修で正常動作する。
BOMありを正規形とした場合、10件が改修対象となる。本条項は設計上の好みではなく、
影響件数の非対称性から導かれる。

### 3.2 書込側の条項

**条項 E-2(必須)**: 全文書換え(`"w"`)は BOM を付与してはならない。`encoding="utf-8"` を用いる。

**条項 E-3(必須)**: 追記(`"a"`)も `encoding="utf-8"` を用いる。

追記モードの `utf-8-sig` はファイル中間へBOMを挿入しないことを実測で確認済みであり、
現時点で実害はない。本条項は規約の一本化を目的とし、実害の除去を目的としない。

**条項 E-4(必須)**: 全文書換えを行う主体は限定する。

現状は3箇所(db_helper.py:77 / risk_engine.py:143 / repair_events.py:45)が全文書換えを行う。
全文書換えは以下のリスクを持つため、主体の限定が必要である。

- 他プロセスの追記分の消失(競合制御が現行コードに存在しない)
- 固定列リスト(`FIELDNAMES`)への射影による列欠落
- 埋め込み改行・クォート表現の正規化

限定の具体(どのモジュールに全文書換え権を残すか)は第6節の未確定事項とする。

### 3.3 読取側の条項

**条項 E-5(推奨 / Tier 2)**: 読取は `encoding="utf-8-sig"` を用いる。

条項 E-1 が守られている限り、`utf-8` で読んでも正常に動作する。本条項は
正規形が破られた場合に備える防御的措置であり、D-4の解消に必須ではない。

### 3.4 列の保全

**条項 E-6(必須)**: 全文書換え時に、入力に存在した列を欠落させてはならない。

現行 `tools/mocka_risk_engine.py:147` は `{k: row.get(k,"N/A") for k in FIELDNAMES}` により
固定列リストへ射影する。現ヘッダ23列と `FIELDNAMES` 23列は一致していることを確認済みだが、
将来の列追加時に無言で欠落する構造である。

### 3.5 検証

**条項 E-7(必須)**: 本契約への適合は、書込直後の実測により検証する。

検証項目は INC_PIPELINE_REGRESSION_PLAN_v0.1.md の R-10 から R-14 に定義済み。

---

## 4. 適合状況と改修対象

### 4.1 Tier 1(条項 E-1 から E-3、E-6 の充足に必要な最小改修)

| ファイル | 位置 | 現状 | 契約適合 | 要改修 |
|----------|------|------|----------|--------|
| interface/db_helper.py | :77 | `"w"` + utf-8-sig | 違反(E-2) | **要** |
| interface/db_helper.py | :196 | `"a"` + utf-8-sig | 違反(E-3、実害なし) | **要** |
| tools/mocka_risk_engine.py | :143 | `"w"` + utf-8 | 適合(E-2) | 不要 |
| tools/mocka_risk_engine.py | :147 | FIELDNAMES射影 | 違反(E-6) | **要** |
| tools/mocka_repair_events.py | :45 | `"w"` + utf-8 | 適合(E-2) | 不要 |
| 追記5モジュール(caliber系3 / mocka_pipeline.py / watchdog_mocka_v2.py) | - | `"a"` + utf-8 | 適合(E-3) | 不要 |

Tier 1 の改修対象は **2ファイル / 3箇所**。

加えて、現物 data/events.csv がBOM付きであるため、正規形への正規化(BOMの除去)が1回必要となる。
この正規化操作自体が全文書換えであるため、条項 E-4/E-6 の対象となる。

### 4.2 Tier 2(条項 E-5 の防御的適用)

BOM非耐性で読む現用10件。条項 E-1 が守られる限り改修なしで動作するため、
Tier 2 を適用するか否かは Human Gate の判断事項とする(第6節)。

| ファイル | 先頭列 event_id への参照 |
|----------|--------------------------|
| interface/router.py | 4 |
| interface/incident_learner.py | 4 |
| interface/evaluator_dynamic.py | 3 |
| tools/mocka_risk_engine.py | 2 |
| interface/Essence_Direct_Parser.py | 1 |
| interface/language_detector.py | 1 |
| interface/mocka_events_sync.py | 1 |
| tools/mocka_failure_scan.py | 1 |
| tools/mocka_5w1h.py | 0 |
| tools/mocka_repair_events.py | 0 |

**限定**: 上表の `event_id` 参照が、CSVのDictReader由来の行に対するものか
SQLite由来かは個別未確認である。D-4と同型の障害が確定しているのは
tools/mocka_risk_engine.py の1件のみであり、残る7件は要確認候補である。

### 4.3 要判定(current かつ reference-only の9件)

| ファイル | 内容 | 本契約の適用 |
|----------|------|--------------|
| app.py | `EVENTS_CSV` 定義のみ。コメントに廃止済み・書き込み禁止と明記 | 不要(実I/Oなし) |
| mocka_mcp_server.py | パス解決のみ。コメントに廃止済みと明記 | 要判定(解決先の利用者を追跡していない) |
| mocka_caliber_sqlite_patch.py | 文字列リテラル内にI/Oコードを保持するパッチ生成 | 要判定(生成されるコードが契約に従う必要) |
| scripts/write_condense_worker.py | 同上 | 要判定 |
| interface/pattern_engine_v2.py | `EVENTS_CSV` 定義のみ、未使用 | 不要 |
| interface/policy_generator.py | 日本語の方針文中で言及 | 不要 |
| interface/essence_classifier.py | 語彙リストの要素 | 不要 |
| interface/pattern_registry_seed.py | 文中の言及 | 不要 |
| make_movement_map.py | 文中の言及 | 不要 |

コード生成スクリプト2件は、自身は契約対象外だが**生成物が契約に従う必要がある**点で
通常の reference-only とは性質が異なる。

---

## 5. 本契約とD-4/D-5の関係

| 欠陥 | 本契約による扱い |
|------|------------------|
| D-4 (event_id列の全損) | 条項 E-1/E-2/E-6 で扱う。本契約の主目的 |
| D-5 (重複判定の常時成立) | **本契約の対象外**。D-5の現在の活性化要因はD-4だが、D-5自体は部分一致判定という別種の不健全さを持ち、条項の充足では解消しない(DC_20260731_002 制約C-2) |

条項 E-1 から E-7 がすべて充足されても D-5 は残存する。この点は、
Encoding Contract の適用をもってD-4系統が完了したと見なさないための明示である。

---

## 6. 未確定事項(Human Gate判断待ち)

1. **Tier 2(条項 E-5)を適用するか否か**。適用しない場合、正規形が一度でも破られた
   時点で10モジュールが同時に影響を受ける。適用する場合、10ファイルの改修が発生する
2. **全文書換え権をどのモジュールに残すか**(条項 E-4 の具体)。現状3箇所
3. **現物CSVの正規化(BOM除去)をいつ・どの主体が実行するか**。実行自体が全文書換えである
4. **4.3 の要判定3件**(mocka_mcp_server.py / コード生成スクリプト2件)の扱い
5. **契約違反の検知方法**。静的検査を導入するか、回帰試験(R-10からR-14)のみとするか
6. Tier 2 未適用の場合、4.2の要確認候補7件について `event_id` 参照がCSV由来か
   DB由来かの個別確認を行うか

---

## 7. 本文書の限界

- 本契約は静的解析に基づく棚卸し(EVENTS_CSV_ENCODING_INVENTORY_v0.1.md)を前提とする。
  動的パス構築・subprocess経由・他言語からのアクセス・モジュール跨ぎの間接I/Oは
  棚卸しの検出範囲外であり、本契約の適用漏れが存在しうる
- 走査範囲は C:\Users\sirok\MoCKA 配下の `.py` に限定される。Cloudflare Workers側、
  他ホストは未走査
- 本文書は設計であり、実装・検証は未実施である
