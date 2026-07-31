# PHI-OS Encoding Migration Plan v0.1

PHI-OS Encoding Contract v0.1 の適用順序。Current から Complete までの移行計画。

- 作成日: 2026-07-31
- 種別: Design(移行計画)。**NON-CANONICAL / 未実装**
- 根拠Decision: DC_20260731_002 (RC-A採択、status: Active)
- 関連Decision: DC_20260731_003 (RC-B採択) — Stage 1 のゲート条件に関与する
- 先行文書: docs/architecture/PHI_OS_ENCODING_CONTRACT_v0.1.md
- 基準commit: baddd113d0202eb08b33bcadf4c115a228234c17

---

## 0. 本計画の位置づけ

```
監査          -> 契約          -> 移行計画      -> 実装
(完了)           (完了)           (本文書)        (未着手)
INC_PIPELINE_*   ENCODING_        ENCODING_       Tier 1
FAILURE/DEPEND   CONTRACT_v0.1    MIGRATION_v0.1  2ファイル3箇所
ENCODING_INV
```

本文書はStageの定義と各Stageの完了条件を固定するものであり、
実装・コード変更・コミットは含まない。

---

## 1. 現在地

| 項目 | 値 |
|------|----|
| **現在のStage** | **Stage 0 (Current)** |
| 最終更新 | 2026-07-31 |
| 次のゲート | Stage 1 着手ゲート(第4節) |

Stage が進むごとに本表を更新する。運用者・Codex・Claude・Gemini のいずれも、
本表1行を見れば現在地が判定できることを本文書の要件とする。
(更新主体と更新タイミングの規約は第8節の未確定事項)

---

## 2. Stage 一覧

| Stage | 名称 | 対象 | 規模 | 完了条件 |
|-------|------|------|------|----------|
| 0 | Current | - | - | 現状把握が完了していること(達成済み) |
| 1 | Tier 1 適用 | 書込側 + 列保全 + 正規化 | 2ファイル3箇所 + データ正規化1回 | 条項 E-1/E-2/E-3/E-6 の充足 |
| 2 | Tier 2 適用 | 読取側の防御的適用 | 10ファイル | 条項 E-5 の充足 |
| 3 | Validation | 現用24件の適合確認 | 24ファイル | 回帰試験 R-10 から R-14 の合格 |
| 4 | Platform Adoption | PHI-OS全体 | 未確定 | **別Decision必須**(第7節) |

---

## 3. Stage 詳細

### Stage 0: Current

**状態**: 達成済み。

| 確定事項 | 根拠文書 |
|----------|----------|
| 欠陥5件(D-1からD-5)の特定 | INC_PIPELINE_FAILURE_ANALYSIS_v0.1.md |
| 根本原因2系統(RC-A / RC-B) | INC_PIPELINE_DEFECT_DEPENDENCY_v0.1.md |
| events.csv touchpoints 57件 / 現用I/O 24件 | EVENTS_CSV_ENCODING_INVENTORY_v0.1.md |
| 契約条項 E-1 から E-7 | PHI_OS_ENCODING_CONTRACT_v0.1.md |
| 回帰試験 R-01 から R-25 | INC_PIPELINE_REGRESSION_PLAN_v0.1.md |

**現在の実データ状態**: data/events.csv はBOM付き(オフセット0に1箇所、実測)。
この状態では tools/mocka_risk_engine.py 実行時に event_id 列が全132行 N/A へ置換される
(D-4、Run Aで実測)。

### Stage 1: Tier 1 適用

**目的**: D-4(データ破壊)の停止。

**作業対象**:

| # | ファイル | 位置 | 内容 | 条項 |
|---|----------|------|------|------|
| 1 | interface/db_helper.py | :77 | 全文書換え時にBOMを付与しない | E-2 |
| 2 | interface/db_helper.py | :196 | 追記のencoding規約を統一 | E-3 |
| 3 | tools/mocka_risk_engine.py | :147 | 固定列リストへの射影による列欠落を防ぐ | E-6 |
| 4 | data/events.csv | - | 正規形への正規化(BOM除去)。1回のみ | E-1 |

作業1から3はコード変更、作業4はデータ変更である。性質が異なるため分けて扱う。

**前提条件**:
- 作業4の実行前に data/events.csv のスナップショットを取得すること
  (正規化自体が全文書換えであり、条項 E-4/E-6 の対象となるため)
- **Stage 1 着手ゲート(第4節)の通過**

**完了条件**:
- 条項 E-1/E-2/E-3/E-6 の充足
- 回帰試験 R-10(BOM付きCSVでもデータ破壊しない) / R-11(列欠落なし) /
  R-12(埋め込み改行・クォート表現の保存) の合格
- 正規化後の data/events.csv がBOMなしであること、かつ全132レコードの
  event_id が正規化前と一致すること

**ロールバック**: 作業1から3はコード差分の revert。作業4はスナップショットからの復元。

### Stage 2: Tier 2 適用

**目的**: 正規形が破られた場合への防御。

**作業対象**: BOM非耐性(`utf-8`)で読む現用10ファイルを `utf-8-sig` へ統一する。

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

**性質**: 本Stageは D-4 の解消には**不要**である。Stage 1 が完了していれば
これら10件は無改修で正常動作する。Stage 2 は正規形が将来破られた場合の
影響範囲(10モジュール同時)を封じる保険である。

**完了条件**: 回帰試験 R-13(書き戻し後のCSVを他モジュールが読める)の合格。

**Stage 2 をスキップする選択**: 契約上は許容される(条項 E-5 は推奨)。
スキップした場合、第7節の未確定事項6(要確認候補7件の個別確認)が残る。

### Stage 3: Validation

**目的**: 現用24件が契約に適合していることの確認。

**作業**: 回帰試験 R-10 から R-14 を24件に対して実施する。
試験方式は INC_PIPELINE_REGRESSION_PLAN_v0.1.md 第1節の隔離サンドボックス方式。

**完了条件**: 24件すべてについて、契約条項への適合が実測で確認されること。

**留意**: Stage 2 をスキップした場合、Tier 2 対象10件は"契約の推奨条項に
未適合だが正常動作する"状態として記録し、適合済みとは区別する。

### Stage 4: Platform Adoption

**目的**: 契約の適用範囲を PHI-OS 全体へ拡張する。

**状態**: **本計画では実施しない。別Decisionを必須とする。**

DC_20260731_002 は"v0.1の規約対象は data/events.csv に限定する。PHI-OS全体への
適用は本Decisionに含めず、別Decisionとする"と裁定している。本Stageは移行の
到達点として定義するが、Stage 3 完了をもって自動的に着手できるものではない。

**着手の前提**:
- 対象データ・対象モジュールの棚卸し(events.csv に対して行ったものと同等)
- 拡張を承認する Decision の記録
- 文書名(PHI-OS Encoding Contract)の適用範囲と実効範囲の不一致の解消
  (PHI_OS_ENCODING_CONTRACT_v0.1.md 1.2節に記載の差分)

---

## 4. Stage 1 着手ゲート(重要)

**Stage 1 の完了は、D-5 の遮蔽を解除する。**

これは Encoding Contract の適用が RC-B 側(DC_20260731_003)と独立でないことを意味する。
本計画で最も注意を要する箇所である。

### 4.1 機序

```
現在: BOM付き
  -> risk_engine が utf-8 で読む -> キーが ﻿event_id
  -> row.get("event_id","") が "" -> 重複判定 "" in content が全ファイルで真
  -> INC生成が完全停止 (D-5 が D-1/D-2/D-3 を遮蔽)

Stage 1 完了後: BOMなし
  -> event_id が正しく取得できる
  -> 重複判定が通常動作する
  -> INC生成が再開する
  -> 未承認INCが GPT_RESTRICTIONS.md へ一斉掲載される
```

Tier 1 の作業対象3箇所(db_helper.py:77 / :196、risk_engine.py:147)は、
重複判定(risk_engine.py:131-136)にも公開処理の起動(同:154-159)にも触れない。
すなわち Stage 1 は D-5 を修正しないまま、その活性化要因のみを取り除く。

### 4.2 実測による裏付け

Run B(BOM除去済みCSV + 現行コード)の結果:

| 観測項目 | 結果 |
|----------|------|
| INC生成 | 6件(INC-20260731-001 から -006) |
| GPT_RESTRICTIONS.md | 全文上書きされ、6件すべてが `(要分析)` として掲載 |

GPT_RESTRICTIONS.md は origin/main へ push される公開ファイルであり、
gateway/adapter_gpt.py:247-255 がGPTセッション開始時に参照を指示している。

### 4.3 ゲート条件

Stage 1 着手前に、以下のいずれかが確定していること。

| 選択肢 | 内容 | 残る課題 |
|--------|------|----------|
| (a) 運用で担保 | Stage 1 完了から RC-B 側の D-1 是正までの区間、tools/mocka_risk_engine.py を実行しない | 実行の抑止を何で保証するか |
| (b) 順序で担保 | RC-B 側の D-1(承認ゲート)を先に実装してから Stage 1 へ進む | Encoding Contract 先行という DC_20260731_002 の裁定と順序が入れ替わる |
| (c) 分割で担保 | Stage 1 のうち作業1から3(コード変更)のみ先に行い、作業4(正規化)を D-1 是正後に行う | 作業4未了の間は D-4 が継続する |

DC_20260731_002 は"露出窓の運用上の担保は実装着手前に別途確定する"としており、
本ゲートがその該当箇所である。**選定は Human Gate 判断事項であり、本計画では行わない。**

選択肢(c)についての事実: 作業3(risk_engine.py:147 の列保全)のみでも D-4 の
データ破壊は止まる。BOMが残る限り event_id は空のままだが、書き戻しで
`N/A` へ置換されることは防げる。ただし列の値は空文字となるため、
正規化(作業4)まで完了して初めて event_id が復元される。

---

## 5. Stage と回帰試験の対応

| Stage | 適用する試験項目 | 出典 |
|-------|------------------|------|
| 1 | R-10, R-11, R-12 | INC_PIPELINE_REGRESSION_PLAN_v0.1.md |
| 2 | R-13 | 同上 |
| 3 | R-10 から R-14 の全項目を24件へ | 同上 |
| 4 | 別途定義(未着手) | - |

Stage 1 完了後は、D-1/D-2/D-3 に関わる試験項目(R-01 から R-09)が
**通常経路で実施可能になる**。これは 4.1 の遮蔽解除の裏面であり、
検証面では利点となる(修正順序案A の性質、INC_PIPELINE_REMEDIATION_SCOPE_v0.1.md 4節)。

---

## 6. Stage 進行の記録

各Stageの完了時に以下を行う。

1. 第1節の現在地表を更新する
2. mocka_write_event で CHANGE_DONE を記録する(Stage名・作業対象・検証結果を含む)
3. 回帰試験の実測値を記録する(合格/不合格ではなく実測値を残す)

Stage の完了判定を、コード変更の完了のみをもって行わない。
第3節の各完了条件の充足を実測で確認したときに完了とする。

---

## 7. 本計画の範囲外

| 項目 | 理由 |
|------|------|
| D-5(重複判定の常時成立) | Encoding Contract の対象外(PHI_OS_ENCODING_CONTRACT_v0.1.md 第5節)。条項を充足しても残存する |
| D-1/D-2/D-3 | RC-B(DC_20260731_003)の対象。INC_LIFECYCLE_STATE_MODEL_v0.1.md で扱う |
| Stage 4 の実施 | 別Decision必須(第3節 Stage 4) |
| 全文書換え権の限定(条項 E-4 の具体) | 未確定(PHI_OS_ENCODING_CONTRACT_v0.1.md 第6節2) |

---

## 8. 未確定事項

1. **Stage 1 着手ゲートの選択肢(a)(b)(c)のいずれを採るか**(第4.3節)。
   本計画で最も優先度の高い判断事項
2. **Stage 2 を実施するかスキップするか**
3. **正規化前スナップショットの取得先**。data/ 配下は .gitignore の
   包括除外パターンの確認が必要であり、C:\Users\sirok\MoCKA_backups は
   プロジェクト単位のzip保管であってファイル単位のスナップショット用途とは異なる
4. **第1節の現在地表の更新主体と更新タイミング**の規約
5. **本計画のStage順を制度として固定するか**。固定する場合は Decision 化が必要となる。
   本文書は現時点では設計文書であり、Stage順は DC_20260731_002 の範囲内での整理である

---

## 9. 本文書の限界

- 本文書は計画であり、Stage 1 以降は未実施である
- 各Stageの完了条件は、先行文書(契約・回帰試験計画)の記述に依存する。
  それらの未確定事項が確定するまで、完了条件も確定しない
- 対象範囲は C:\Users\sirok\MoCKA 配下に限定される。Cloudflare Workers側、
  他ホストは未走査であり、Stage 4 の前提となる棚卸しには含まれていない
