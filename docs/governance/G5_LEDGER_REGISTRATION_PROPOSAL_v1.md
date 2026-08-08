# G-5 Ledger Registration Proposal v1

## G-5 裁定群 Decision Ledger 登録設計案

**文書番号:** EBGA-G5-LRP-001
**作成日:** 2026-08-06
**Status:** **PROPOSAL**
**Approval:** **Pending Human Authority**
**Registration Model:** **B (G-5 統合 Decision 1件登録)**

**本文書は提案であり、裁定ではない。** 記載された登録内容はいずれも未実行である。

---

## 0. 本文書の位置付け

### 0.1 実施していないこと

| # | 事項 | 状態 |
|---|---|---|
| 1 | Decision Ledger への write | **未実施** (`decision_ledger.jsonl` 208行のまま) |
| 2 | commit | **未実施** |
| 3 | push | **未実施** |
| 4 | v0.6 変更 | **未実施** |
| 5 | Rule 変更 / 実装変更 / 自動修復 | **未実施** |

### 0.2 推奨の位置付け

本文書の Registration Model B は **きむら博士の指示により固定されたもの**である。
第1章の採用根拠および第5章の Risk Register は Human Gate Core の出力であり、
**承認を構成しない** (`mocka_human_gate_decision_definition_v1.md` 第7章)。

### 0.3 登録実行の条件

本提案の実行は Human Authority の明示指示による。**くろこの判断では実行しない。**

---

## 1. Registration Model: B

**G-5 裁定群を Decision Ledger へ 1件の Decision として登録する。**

### 1.1 採用根拠 (Confirmed)

| # | 根拠 |
|---|---|
| 1 | 確定方針の文言が「G-5 裁定群として一括登録」である (`E20260806_704100096a9c2`) |
| 2 | `DC_20260805_001` が Gate 1 の10項目 (C2-01..03 / G-9..11 / Q-1..4) を **1件で登録した先例**がある |
| 3 | Decision Ledger スキーマ14フィールドに **親子関係の表現がない** (Model C は Rule 変更または慣行依存を要する) |
| 4 | Model A は確定方針の文言と一致しない |

### 1.2 不採用となった Model (ドラフト。文面は Human Authority が確定する)

| Model | 内容 | 不採用の理由 (案) |
|---|---|---|
| A | 3件個別 Decision 登録 | 確定方針の文言 (G-5 裁定群として一括登録) と一致しない |
| C | Parent Decision + Child Decision 構造 | Ledger スキーマに親子表現がなく、`decision_id` は自動採番のため親 ID の事前指定もできない (`DC_20260801_002` HG-4) |

**却下ではなく、本提案において選択されなかったものとして記録する。**

---

## 2. Decision Structure

**以下は Decision Ledger へ書き込む内容の案である。未実行。**

### 2.1 フィールド構成

| フィールド | 内容 (案) |
|---|---|
| `decision_id` | **自動採番** (`DC_20260801_002` HG-4 により明示指定しない) |
| `title` | G-5 Human Gate Criteria Decision: HG-C08 / HG-C09 / HG-C10 の確定 (External Reference: EBGA-G5-HGC08-DR-001 / -HGC09-DR-001 / -HGC10-DR-001) |
| `context` | Gate 1 (`DC_20260805_001`) の未解消 Unknown G-5 (Human Gate 接続先が5系統並存) に対し、Gate 2 の準備工程として判断基準を定義し、HG-C01 から HG-C13 および CQ / C2-b 算入を裁定した。基準文書は v0.1 から v0.6 へ段階的に改訂され、HG-C08 / C09 / C10 は個別の Decision Record として確定した。本登録は一括登録方針に基づく |
| `alternatives` | Model A / Model C (1.2 の内容) |
| `decision` | 2.2 のブロック構造 |
| `rationale` | 2.3 |
| `impact` | 2.4 |
| `related_events` | 第4章 |
| `related_documents` | 第3章 |
| `approved_by` | きむら博士 |
| `approved_at` | 登録実行時点 |
| `supersedes` / `superseded_by` | null |
| `status` | Active |

### 2.2 decision 本文 (ブロック構造。Gate 1 と同形式)

```
[HG-C08] 検証軸 (C2-b) のサンプリング対象経路の選定基準 - APPROVED
  対象集合: 承認確定に到達する経路をすべて対象とする (Model B)
  技術的判定基準: 承認状態を確定させる関数への到達を境界同定の基準とする (E を補完採用)
  境界: 全経路は対象集合の定義であり、検証実施方法は HG-C14 にて別途規定する
  External Reference: EBGA-G5-HGC08-DR-001

[HG-C09] C2-a と C2-b の不一致の扱い - APPROVED
  X-1 HG-C09 を先行裁定。意味論は HG-C10 の責務として保持
  X-2 不一致発生という事実を Event / Ledger 対象として保持
  X-3 判定値の変更・統合・上書きは行わない
  X-4 追跡単位は発生経路単位
  X-5 HG-C08 の対象集合との整合性を維持
  X-6 再発件数等による自動昇格は禁止。通知トリガーとして扱う
  X-7 比較単位差異の存在を記録対象とする
  X-8 比較・変換ルールは HG-C14 へ委任
  X-9 Core 層で不一致検知 Event を生成
  X-10 Finalization 層で制度的確定を行う
  X-11 新規 Pending 台帳は作成しない
  X-12 既存 Event / Ledger 体系を利用する
  External Reference: EBGA-G5-HGC09-DR-001

[HG-C10] 不一致の意味論 - APPROVED
  Y-1 意味論は複合階層分類とする。単一の意味を与えない
  Y-2 分類は既存 Integrity Ledger の type / boundary 語彙を流用する
  Y-3 新規分類体系による制度拡張は後続判断とする
  Y-4 不一致自体を Evidence 化しない。既存 Evidence への参照付与に留める
  Y-5 Core が候補を付与し、Finalization が最終意味を確定する
  Y-6 Unknown は保持するが、再評価条件または期限を付す
  Y-7 Severity 概念は導入しない
  Y-8 Incident 連携条件は HG-C10 の対象外とする
  Y-9 Integrity Ledger 連携条件は HG-C09 の RU-1 として継続する
  Y-10 C2-a 対象範囲は HG-C10 確定後に依存関係を確認する
  External Reference: EBGA-G5-HGC10-DR-001

[Established Criteria Reference] HG-C01 から HG-C07
  本ブロックは既に確定した判断基準の参照であり、本 Decision で新たに裁定するものではない
  HG-C01 判定語彙4値 (PASS / CONDITIONAL / FAIL / UNKNOWN) を採用
  HG-C02 UNKNOWN と FAIL は分離する
  HG-C03 評価粒度 = 系統単位 / 検証粒度 = 経路単位 / 独立記録
  HG-C04 Criterion 2 は C2-a (評価軸) と C2-b (検証軸) に分離記録する
  HG-C05 全充足を必要条件とする。UNKNOWN は FAIL 扱いしない
  HG-C06 比較表に総合判定欄は設置しない
  HG-C07 Criterion 5 は対象外 (N/A) を許容し FAIL / UNKNOWN と区別する
  正本の所在: G5_DECISION_CRITERIA_DEFINITION_v0.6.md (Governance Definition Artifact) 6.1

Human Authority Seal: きむら博士 / 20260806
未裁定として残るもの: HG-C14 (比較単位・判定規則)
Design Freeze ACTIVE / Implementation STOP 維持
```

### 2.3 rationale (案)

G-5 は Human Gate 接続先が5系統並存する状態に対し、正典を決める前に
「Human Gate と呼ぶために最低限満たす制度条件」を先に固定する順序で進められた。
HG-C01 から HG-C13 および CQ / C2-b 算入の裁定により判断基準が確定し、
HG-C08 / C09 / C10 は個別 Decision Record として Human Authority が確定した。
登録単位は確定方針の文言および Gate 1 の先例に従い、G-5 裁定群として1件とする。

### 2.4 impact (案)

**確定するもの:** G-5 判断基準の運用条件 (判定語彙 / 記録分離 / 必要条件 / N/A の扱い) /
検証軸の対象集合 / 不一致の記録・追跡境界 / 不一致の意味論。

**本 Decision で変更しないもの:** Criterion 1 から 5 の評価目的・確認項目 (博士提示のまま不変) /
判定値の計算方法 / 既存 Decision Ledger 208行 / Integrity Ledger 48行 / Event Ledger /
`human_gate_events` / コード・実装 (Implementation STOP 維持)。

**未実施のまま残るもの:** HG-1 から HG-5 への比較評価 / 正典候補の決定 /
Governance Definition Artifact (v0.6) への裁定反映 / HG-C14 の裁定 / RU 群の解消。

---

## 3. Related Documents Classification

**3区分で分類する。合計17文書。**

### 3.1 Decision Record (裁定内容の正本) - 3件

| 文書 | 行数 | 分類理由 |
|---|---|---|
| `docs/governance/HG-C08_DECISION_RECORD_v1.0.md` | 272 | Human Authority の確定値と Authority 記録を保持する。`decision` 本文の出所 |
| `docs/governance/HG-C09_DECISION_RECORD_v1.0.md` | 329 | 同上 |
| `docs/governance/HG-C10_DECISION_RECORD_v1.0.md` | 307 | 同上 |

### 3.2 Governance Definition Artifact - 1件

| 文書 | 行数 | 分類理由 |
|---|---|---|
| `docs/governance/G5_DECISION_CRITERIA_DEFINITION_v0.6.md` | 827 | **判断基準の正本**であり、裁定結果が反映される対象文書である。判断材料 (Preparation Evidence) ではなく、G-5 の制度定義そのものを保持する。HG-C01 から HG-C07 の確定内容 (6.1) の正本所在でもある |

**注記:** `DC_20260805_001` Q-1 で確定した Rule Registry の **Rule Artifact 候補**にあたるかは未確認である。
本分類は Rule Artifact 化を先取りしない。

### 3.3 Preparation Evidence (判断材料) - 13件

| 文書 | 行数 |
|---|---|
| `G5_DECISION_CRITERIA_DEFINITION_v0.1.md` | 471 |
| `G5_DECISION_CRITERIA_DEFINITION_v0.2.md` | 633 |
| `G5_DECISION_CRITERIA_DEFINITION_v0.3.md` | 708 |
| `G5_DECISION_CRITERIA_DEFINITION_v0.4.md` | 781 |
| `G5_DECISION_CRITERIA_DEFINITION_v0.5.md` | 835 |
| `G5_DECISION_CRITERIA_DECISION_PREP_v0.1.md` | 404 |
| `G5_HGC03_OPTION_COMPARISON_v0.1.md` | 162 |
| `G5_HGC08_DECISION_PREP_v0.1.md` | 283 |
| `G5_HGC09_DECISION_PREP_v0.1.md` | 370 |
| `G5_HGC09_DECISION_SCOPE_v0.1.md` | 329 |
| `G5_HGC09_DECISION_INPUT_v0.1.md` | 389 |
| `G5_HGC10_DECISION_PREP_v0.1.md` | 310 |
| `G5_HGC10_DECISION_INPUT_v0.1.md` | 386 |

**分類理由:** いずれも Human Gate Core の出力であり `decision` 値を含まない
(`mocka_human_gate_decision_definition_v1.md` 第6章)。裁定そのものではないため
`related_documents` への列挙に留め、`decision` 本文の出所とはしない。
**v0.1 から v0.5 は各時点の状態を保存する版**であり、正本は v0.6 (3.2) である。

### 3.4 Established Criteria Reference

**HG-C01 から HG-C07 は Decision Record 扱いとしない。**

| 項目 | 内容 |
|---|---|
| 位置付け | **既に確定した判断基準への参照** (Established Criteria Reference) |
| 記載先 | `decision` 本文の `[Established Criteria Reference]` ブロック (2.2) |
| 正本の所在 | Governance Definition Artifact (`v0.6`) 6.1 および Event 記録 |
| 本 Decision での扱い | **新たに裁定しない**。参照として記載する |

### 3.5 分類対象外

| 対象 | 理由 |
|---|---|
| 本文書 (`G5_LEDGER_REGISTRATION_PROPOSAL_v1.md`) | 提案であり裁定の構成要素ではない |

---

## 4. Related Events

| # | Event ID | 内容 |
|---|---|---|
| 1 | `E20260806_0143683733535` | CHANGE_START: HG-C08 Decision Record v1.0 最終化 |
| 2 | `E20260806_1217499317e93` | CHANGE_DONE: HG-C08 Decision Record v1.0 確定 (APPROVED) |
| 3 | `E20260806_514190447f563` | CHANGE_START: HG-C09 Decision Record v1.0 作成 |
| 4 | `E20260806_640536242e3a7` | CHANGE_DONE: HG-C09 Decision Record v1.0 確定 (APPROVED) |
| 5 | `E20260806_7607018817507` | CHANGE_START: HG-C10 裁定入力の反映と Decision Record v1.0 作成 |
| 6 | `E20260806_9225378642c1b` | CHANGE_DONE: HG-C10 Decision Record v1.0 確定 (APPROVED) |
| 7 | `E20260806_354237668e317` | DECISION_HOLD: 一括登録方針の維持確認 |
| 8 | `E20260806_13942678895d0` | STOP_POINT: G-5 最終登録前監査完了 |
| 9 | `E20260806_4569236141b81` | AUDIT: G-5 Decision Governance 完了状態監査 |

**全9件は events.db への読み戻しで実在を確認済み。**

---

## 5. Risk Register

| # | リスク | 根拠 | 現状 |
|---|---|---|---|
| R-1 | 統合1件は3裁定を1行に束ねるため、後日1件のみ訂正する場合の粒度が粗い | Ledger は行単位の `supersedes` のみを持つ | 未解消。`decision` のブロック構造で記述面のみ緩和 |
| R-2 | HG-C01 から C07 に個別 Record が存在しない | 所在は Governance Definition Artifact 6.1 と Event のみ | **Established Criteria Reference として扱うことで整理済 (3.4)** |
| R-3 | HG-C14 が未裁定のまま登録される | 比較単位・判定規則が未定義 | 未解消 |
| R-4 | RU 群が未解消のまま登録される | HG-C09 RU-1 / HG-C10 RU-1・RU-2 / C2-a 対象範囲 (Y-10) | 未解消 |
| R-5 | Governance Definition Artifact (v0.6) 未反映のまま登録すると、Ledger と基準文書の記述が乖離する期間が生じる | 反映箇所は 4.2.6-4 / 4.2.7 S-4 / 5.1 / 5.2 / 6.2 / 7.2 | 未実施 |
| R-6 | 既存 Ledger に重複 ID が7件あり、新規登録が同型と誤読されうる | `DC_20260801_002` P-1 該当。HG-1 により修復禁止 | 観測のみ |
| R-7 | commit `2bc81b400` / `98fe932a5` / `1c6511798` に CHANGE_START/DONE がなく、commit から Event への逆引きが成立しない | `DC_20260731_008` GOV-PROC-CETR-001 | **観測のみ。問題判定を行わない** |
| R-8 | G-5 文書は既に origin/main へ push 済で公開状態にある | HEAD = `f24e2826e`、未push 0 | 事実 |
| R-9 | 登録実行時に `mocka_decision_write` のセッション内可用性確認が必要 | capability drift (`IC_20260705_018`) | 未確認 |
| R-10 | 登録は append-only であり、実行後の取消はできない | 憲法原則1 / I-1 | 実行前で停止中 |
| R-11 | Governance Definition Artifact の分類が Rule Registry の Rule Artifact 化と競合しないか未確認 | `DC_20260805_001` Q-1 | 未確認 (3.2 注記) |

---

## 6. 登録実行手順 (案。実行は Human Authority の指示による)

| # | 手順 |
|---|---|
| 1 | `mocka_decision_write` の可用性を確認する (R-9) |
| 2 | 第2章の内容で1件を登録する (`decision_id` 自動採番) |
| 3 | `mocka_decision_get` で読み戻し、反映を確認する (Execution Integrity 規定) |
| 4 | CHANGE_START / CHANGE_DONE を記録する |
| 5 | Governance Definition Artifact (v0.6) への反映は別途の指示による (R-5) |

**手順1から5はいずれも未実行である。**

---

## 7. 本文書の限界

1. 本文書は **提案であり裁定ではない**。第2章の登録内容は未実行である
2. 1.2 の不採用理由および 2.3 / 2.4 の文面は **ドラフト**であり、確定は Human Authority が行う
3. 3.2 の Governance Definition Artifact 分類は **Rule Artifact 化を先取りしない** (R-11)
4. 第5章の R-7 は **観測のみ**であり、問題判定を含まない
5. 行数・件数の実測は 2026-08-06 時点のものである

---

## Knowledge Lineage

| 参照 | 内容 |
|---|---|
| `HG-C08 / C09 / C10 DECISION_RECORD_v1.0.md` | `decision` 本文の出所 (3.1) |
| `G5_DECISION_CRITERIA_DEFINITION_v0.6.md` | Governance Definition Artifact。6.1 に HG-C01..C07 の確定一覧 (3.2 / 3.4) |
| `DC_20260805_001` | Gate 1。G-5 の定義、10項目1件登録の先例、Q-1 Rule Registry |
| `DC_20260801_002` | HG-4 (ID 自動採番) / P-1 (重複 ID) |
| `DC_20260731_008` | COMMIT_EVENT_TRACEABILITY_POLICY (R-7) |
| `IC_20260705_018` | capability drift (R-9) |
| `E20260806_704100096a9c2` | 一括登録方針の確定 |
| `E20260806_4569236141b81` | 完了状態監査 |
| `docs/governance/mocka_human_gate_decision_definition_v1.md` | 第6章 / 第7章 |

**Status: PROPOSAL / Approval: Pending Human Authority**
