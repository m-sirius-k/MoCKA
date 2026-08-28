# TIM_MOCKA_COMPARATIVE_TEST v0.1 - Test Specification

Status: EXPERIMENTAL / ISOLATED / NON-CANONICAL
Date: 2026-08-28
実施: くろこ (Claude Code)
指示: きむら博士 - TimさんのMoCKA版対照試験およびConstitutional Runtime次段階準備
Human Gate: 実験開始について承認済み
実装: `experiments/tim_mocka_comparative/`
結果: `docs/tests/TIM_MOCKA_COMPARATIVE_TEST_RESULTS_v0.1.md`
Source境界: `docs/audits/TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md`

---

## 0. 出所の明示 (先に読む部分)

本試験の case matrix は **きむら博士の指示書 第5節・第6節・第7節に明記されたもの** である。

Timさん由来の資料は本セッションに1件も供給されていない。
したがって本試験は、Timさんの見解を再現したものではなく、
**指示書に記述された判断境界を MoCKA 上で実行可能にしたもの** である。
詳細は Source境界文書 第1.4節。

---

## 1. 試験の対象

ただ1つの問いを扱う。

```text
過去の判断を、現在、再利用してよいか。よいとすれば何を根拠とするか。
```

中心原則 (指示書 第5節)。

```text
"過去にAllowされた" ことそれ自体を、
"現在もAllowである" ことの根拠として使用しない。
```

---

## 2. 構造

```text
Past Evidence
      |
      v
Past Decision  ------ 保存されるのは verdict だけではない。
      |               その判断が成り立っていた前提も一緒に保存する。
      | time passes
      v
Present Context
      |
      v
Re-evaluation Gate
      |
      +---- 前提が不変 --------> ELIGIBLE (再利用可)
      |
      +---- 前提が変化 --------> RE_EVALUATE / BLOCK / UNKNOWN
```

`ELIGIBLE` は"再利用してよい"であって"許可"ではない。
再利用可能な過去 BLOCK は、再利用しても BLOCK のままである。

---

## 3. データ構造

実装: `experiments/tim_mocka_comparative/temporal.py`

### 3.1 DecisionRecord (過去)

| フィールド | 内容 |
| ---------- | ---- |
| decision_id | 判断の識別子 |
| decision | ALLOW / BLOCK / UNKNOWN |
| decided_at | 判断が行われた時刻 |
| validity_until | Temporal Boundary。この時刻まで有効 |
| evidence_digest | 判断が依拠した Evidence の要約 |
| authority_id | 判断を行った Authority |
| context_id | 判断が行われた Context の識別子 |
| context_digest | その Context の内容の要約 |

### 3.2 PresentContext (現在)

| フィールド | 内容 |
| ---------- | ---- |
| now | 現在時刻 (試験では固定) |
| evidence_digest | 現在の Evidence |
| authority_id | 現在の Authority |
| authority_state | VALID / LOST / REVOKED |
| context_id | 現在の Context 識別子 |
| context_digest | 現在の Context 内容 |

### 3.3 判定語彙 (実験ローカル。正式Primitiveではない)

| Finding | 重み | 意味 |
| ------- | ---- | ---- |
| PREMISES_UNCHANGED | INFORMATIONAL | 記録された前提がすべて保たれている |
| TEMPORAL_EXPIRED | REQUIRE_REEVALUATION | 有効期限を過ぎた |
| AUTHORITY_REVOKED | HARD_BLOCK | 現在の Authority が失効している |
| AUTHORITY_CHANGED | REQUIRE_REEVALUATION | 判断時と別の Authority |
| EVIDENCE_CHANGED | REQUIRE_REEVALUATION | Evidence が変化した |
| CONTEXT_CHANGED | REQUIRE_REEVALUATION | 同一 Context の内容が変化した |
| CONTEXT_MISMATCH | REQUIRE_REEVALUATION | 別の Context へ適用しようとしている |
| NO_NEW_EVIDENCE | MAINTAIN_UNKNOWN | UNKNOWN 判断以降、新しい Evidence が無い |
| NEW_EVIDENCE_PRESENT | REQUIRE_REEVALUATION | UNKNOWN 判断以降、新しい Evidence がある |

### 3.4 還元規則

```text
HARD_BLOCK が1件でもある            -> BLOCK
REQUIRE_REEVALUATION が1件でもある  -> RE_EVALUATE
上記が無く、過去判断が UNKNOWN      -> UNKNOWN (そのまま維持)
それ以外                            -> ELIGIBLE
```

### 3.5 Execution Gate

```text
ELIGIBLE かつ 過去判断が ALLOW  -> EXECUTE
それ以外すべて                  -> STOP
```

`RE_EVALUATE` と `UNKNOWN` は決して EXECUTE にならない。
再利用可能な過去 BLOCK も EXECUTE にならない。

---

## 4. Minimum Test Matrix (指示書 第6節)

| Case | 過去の判断 | 現在の状態 | 期待 | 期待 Eligibility | 期待 Execution |
| ---- | ---------- | ---------- | ---- | ---------------- | -------------- |
| T01 | Allow | 前提不変 | Allow可能 | ELIGIBLE | EXECUTE |
| T02 | Allow | 期限経過 | 再評価 | RE_EVALUATE | STOP |
| T03 | Allow | 権限変更 | Blockまたは再評価 | BLOCK / RE_EVALUATE | STOP |
| T04 | Allow | Evidence変更 | 再評価 | RE_EVALUATE | STOP |
| T05 | Allow | Context変更 | 再評価 | RE_EVALUATE | STOP |
| T06 | Block | 前提不変 | Block維持 | ELIGIBLE | STOP |
| T07 | Block | 状態改善 | 自動Allow禁止 | RE_EVALUATE | STOP |
| T08 | UNKNOWN | 新Evidenceなし | UNKNOWN維持 | UNKNOWN | STOP |
| T09 | UNKNOWN | 新Evidenceあり | 再評価 | RE_EVALUATE | STOP |
| T10 | 過去Decision再利用 | Context不一致 | 再利用禁止 | RE_EVALUATE | STOP |

T01 は統制ケースである。何も再利用できない Gate は何も証明しない。

各ケースについて、`Evidence` / `Timestamp` / `Decision` / `Authority` /
`Validity` / `Current Context` / `Execution Eligibility` を分離して記録する
(実装: `run_comparative.py` の audit 行)。

---

## 5. Critical Test: T50-TIM-REUSE (指示書 第7節)

同一の DecisionRecord に対し、2つの経路を並べて比較する。

```text
A: Past Decision reused directly
   -> 保存された verdict をそのまま返す。現在を一切参照しない。

B: Past Decision + Current Re-evaluation
   -> 同じ record を Re-evaluation Gate に通す。
```

入力は、Gate が見られるすべての前提が変化している状態とする。

```text
validity_until : 過去 (期限切れ)
evidence       : 変化
authority_id   : 別
context_id     : 別
context_digest : 変化
```

### 5.1 評価規則 (重要)

```text
A が ALLOW を返しても、それを正当な Allow とは評価しない。
```

A は **アンチパターンの統制** として実装されている。
現在を1つも参照しないため、採点5軸すべてで FAIL となる。
A の出力は"得られてしまった出力"として記録し、eligibility の証拠としては扱わない。

B については、現在の Evidence と Authority が再検証されることを確認する。

---

## 6. 採点 (指示書 第10節)

各ケースを5軸で採点する。値は4種。

```text
PASS / FAIL / UNKNOWN / NOT_TESTED
```

**UNKNOWN を FAIL として扱わない。**

| 軸 | 判定方法 |
| -- | -------- |
| Evidence preservation | 記録された evidence_digest が現在と比較され、変化の有無が正しく検出されたか |
| Temporal validity | validity_until と現在時刻の関係が正しく検出されたか |
| Authority continuity | Authority の失効・変更が正しく検出されたか |
| Context continuity | Context の内容変化・識別子不一致が正しく検出されたか |
| Re-evaluation correctness | Eligibility と Execution が期待どおりか |

### 6.1 NOT_TESTED の使い方

そのケースが当該次元を変化させていない場合は `NOT_TESTED` とする。
"変化させていないので検出されなかった"ことを PASS と記録しない。

### 6.2 UNKNOWN の使い方

本試験で UNKNOWN を用いるのは T10 の Evidence preservation である。
Context が別である場合、evidence_digest の比較は機械的には可能だが、
**Context 境界を跨いだ Evidence 比較が意味を持つかは本試験では決定できない**。
これを PASS にも FAIL にもしない。

---

## 7. 再現手順

```bash
python -m experiments.tim_mocka_comparative.run_comparative
python -m pytest experiments/tim_mocka_comparative/tests/ -q
```

| 項目 | 値 |
| ---- | -- |
| 固定時刻 | 2026-08-28T12:00:00Z |
| 判断時刻 | 2026-08-01T00:00:00Z |
| 有効期限 (有効) | 2026-09-30T00:00:00Z |
| 有効期限 (期限切れ) | 2026-08-10T00:00:00Z |
| 依存 | Python標準ライブラリのみ |
| 本番接続 | なし |

---

## 8. 本仕様が試験しないこと

| # | 事項 | 分類 |
| - | ---- | ---- |
| 1 | Timさん側で実際に問題となった判断境界と一致するか | **検証不能** (資料未提供) |
| 2 | Original CR がこのような Gate を持っていたか | UNKNOWN |
| 3 | 再評価そのものの正しさ (再評価したら何になるか) | 対象外。本 Gate は"再評価が必要か"までしか判定しない |
| 4 | Evidence の内容的な妥当性 | 対象外。digest の一致・不一致のみを見る |
| 5 | Authority の正統性 | 対象外。状態と識別子のみを見る |
| 6 | 実環境での安全性 | 対象外。隔離実験である |

特に 3 は重要である。本 Gate は `RE_EVALUATE` を出すだけであり、
**再評価の結果がどうなるかについては何も述べない**。
T07 (過去 Block + 状態改善) が `RE_EVALUATE` になることは、
改善後に Allow になることを意味しない。
