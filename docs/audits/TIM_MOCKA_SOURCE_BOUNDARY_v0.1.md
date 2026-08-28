# TIM_MOCKA Source Boundary v0.1

Status: SOURCE BOUNDARY RECORD / NON-CANONICAL
Date: 2026-08-28
実施: くろこ (Claude Code)
指示: きむら博士 - TimさんのMoCKA版対照試験およびConstitutional Runtime次段階準備
Human Gate: 実験開始について承認済み (指示書 第1節・第16節)
Branch: claude/constitutional-runtime-investigation-jgqkv1
基準commit: f0f1ea8

---

## 0. 本文書の役割

本作業で参照した情報源と、参照できなかった情報源を固定する。
特に、**Timさん由来の資料が本セッションに一切供給されていない** という事実を記録する。

---

## 1. Source Lock (指示書 第2節)

### 1.1 Original CR

```text
Constitutional Runtime v1.0-stubs
Evidence Status: NOT OBSERVED / UNKNOWN
```

内部実装、Primitive定義、Contract構造、Fail-Closed実装について、
本作業では推測を一切行っていない。

### 1.2 Original 50-Test

```text
50項目試験報告書
Evidence Status: OBSERVED / SECONDARY EVIDENCE
```

原ログ、Evidence Index、試験ページ本体はいずれも **未回収** である。
参照可能なのは、きむら博士から提供された報告内容のみである。

本作業 (Tim-MoCKA対照試験) は、この50試験の結果を **入力として使用していない**。
試験の設計・実行・結果のいずれも、50試験の数値に依存しない。

### 1.3 MoCKA Trial

```text
Constitutional Runtime Trial Basic / Extended
Evidence Status: DESIGNED / IMPLEMENTED / TESTED
```

Original CR とは完全に分離されている。
本作業では Trial のコードを **1行も変更していない** (第4節)。

### 1.4 Tim Source (本作業で新たに固定する層)

```text
Timさん側の議論・テスト観点
Evidence Status: NOT PROVIDED TO THIS SESSION
```

**これが本作業で最も重要な境界である。**

本セッションに供給された入力は、きむら博士の指示書のみである。
Timさんの発言、投稿、コード、試験設計、議論ログ等は **1件も提供されていない**。
リポジトリ内にも該当資料は存在しない (探索実施済み。`tim` を含む既存ファイルは
`timeline` / `time_api` 等の別語であり、いずれも無関係)。

したがって本作業は次のように扱う。

| 項目 | 扱い |
| ---- | ---- |
| 試験の case matrix (T01-T10) | **きむら博士の指示書 第6節に明記されたもの**。指示書からの直接引用であり、Timさんの見解の再構成ではない |
| 中心試験 (T50-TIM-REUSE) の構造 | 同じく指示書 第7節に明記されたもの |
| Re-evaluation Gate の構造 | 指示書 第5節の図に明記されたもの |
| Timさんが実際に何を問題としたか | **UNKNOWN** |
| 本試験が Timさん側の判断境界を正しく再現しているか | **検証不能**。照合対象が存在しない |

指示書 第4節は本試験の目的を
`Timさん側で問題となった判断境界を、MoCKAの構造で再現可能な形にすること` と定めている。
その目的の **前半 (Timさん側で問題となった判断境界)** は、
本セッションからは確認できない。
後半 (MoCKAの構造で再現可能な形にする) のみが実施可能であり、実施した。

---

## 2. 停止条件の検討 (指示書 第15節)

指示書は次を即停止条件としている。

```text
Timさんの明示されていない思想を仕様化する必要が生じた
```

### 2.1 判定

**停止条件には該当しなかった。** 理由は次のとおりである。

試験に必要な仕様は、すべて指示書 第5節・第6節・第7節に明記されていた。
Timさんの未明示の思想を推測して補う必要は生じなかった。
くろこが行ったのは、指示書に書かれた case matrix を実行可能な形にすることのみである。

### 2.2 ただし記録すべき制約

停止条件に該当しなかったことは、
`本試験が Timさんの観点を正しく反映している` ことを意味しない。

```text
実施したこと : 指示書に明記された判断境界を、MoCKA上で実行可能な試験にした。
実施していないこと : その判断境界が Timさん側の問題意識と一致するかの確認。
```

この確認には Timさん由来の一次資料が要る。現時点で入手していない。

### 2.3 他の停止条件

| 停止条件 | 該当 | 根拠 |
| -------- | ---- | ---- |
| Original CR を推測し始める必要が生じた | **該当なし** | 本試験は Original CR を参照していない |
| Timさんの明示されていない思想を仕様化する必要が生じた | **該当なし** | 第2.1節 |
| 既存MoCKAコード変更が必要になった | **該当なし** | 新規ディレクトリのみ。既存ファイル差分0 |
| Decision Ledger 等の既存制度境界を変更する必要が生じた | **該当なし** | 一切触れていない |
| UNKNOWN を便宜上 Allow または Block へ変換する必要が生じた | **該当なし** | T08 で UNKNOWN を UNKNOWN のまま保持。採点でも UNKNOWN を FAIL に変換していない |

---

## 3. No Reverse Causality Rule の遵守 (指示書 第3節)

| 禁止事項 | 遵守状況 |
| -------- | -------- |
| Trial の実装から Original CR の内部構造を推定すること | 行っていない。本試験は Trial とも Original CR とも接続していない |
| Trial で成立した Fail-Closed 性を Original CR の性質として記録すること | 行っていない |
| Original 50-Test の結果から、存在が未確認の Primitive を創作すること | 行っていない。本試験の語彙は 50試験の語彙と重複が無い |
| Timさんの議論を、本人が明示していない仕様として固定すること | 行っていない。第2節のとおり、仕様はすべて指示書由来である |

### 3.1 本試験の語彙の出所

本試験は独自の finding 語彙 9件を持つ。

```text
PREMISES_UNCHANGED / TEMPORAL_EXPIRED / AUTHORITY_REVOKED / AUTHORITY_CHANGED /
EVIDENCE_CHANGED / CONTEXT_CHANGED / CONTEXT_MISMATCH /
NO_NEW_EVIDENCE / NEW_EVIDENCE_PRESENT
```

出所は **本試験のために新規に定義したもの** である。

- Original CR の語彙ではない (Original CR の語彙は UNKNOWN)
- 50試験の報告ラベルではない (`AUTHORITY_LOST` 等とは別物。名称も重複させていない)
- Constitutional Runtime Trial の31語彙とも別物 (共有・継承・import なし)
- Timさんが提示した語彙でもない (提示された語彙は存在しない)

指示書 第9節が挙げる候補概念
(`Decision` / `Evidence` / `Validity` / `Authority` / `Context` /
`Temporal Boundary` / `Re-evaluation`) についても、
**本試験だけでは正式Primitiveとしての採用を決定しない**。
採用には別途 Human Gate を要する (指示書 第16節)。

---

## 4. Existing Trial Protection (指示書 第12節)

### 4.1 Regression Baseline の固定

```text
Constitutional Runtime Trial:
    117 tests  -> 117 passed  (作業前後で同一)
     24 cases  ->  24 pass / 0 fail、EXECUTE到達 2件 (B01, E00)
    trial_results.json -> 再生成してもバイト同一
```

### 4.2 変更の有無

```text
git diff --stat HEAD  -> 差分なし
```

既存ファイルは1件も変更していない。追加したのは新規ディレクトリ
`experiments/tim_mocka_comparative/` と新規文書3件のみである。

`CHANGE PROPOSED` として提示すべき変更提案は、本作業では発生しなかった。

### 4.3 テスト数の扱い

本作業で **新規に31テストを追加した** が、これは別ディレクトリの独立スイートである。

```text
Regression Baseline (変更禁止) : experiments/constitutional_runtime_trial/tests/  117 tests
本作業の新規スイート           : experiments/tim_mocka_comparative/tests/          31 tests
```

Baseline の117という数値は変わっていない。2つの数値を合算して報告しない。

---

## 5. 隔離の確認

| 項目 | 状態 |
| ---- | ---- |
| Constitutional Runtime Trial からの import | **0件** |
| MoCKA 本番モジュールからの import | **0件** |
| 外部依存 | なし (標準ライブラリのみ) |
| events.db / Decision Ledger / Human Gate への書込 | なし |
| 固定時刻 | `2026-08-28T12:00:00Z` (実時計に非依存) |
| 出力先 | `experiments/tim_mocka_comparative/results/` のみ |

---

## 6. Final Source Boundary (指示書 第14節)

> Original Constitutional Runtime v1.0-stubs was not recovered.
>
> The MoCKA Constitutional Runtime is an independently designed reconstruction
> and must not be treated as evidence of the original implementation.

これに加えて、本作業固有の境界を1つ追加する。

> No source material from Tim was supplied to this session. The case matrix
> implemented here comes from the commissioning instruction itself, and this
> experiment must not be treated as evidence of what Tim's position is.

---

## 7. 承認が必要な事項 (指示書 第16節)

| 事項 | 状態 |
| ---- | ---- |
| 本実験の開始 | **承認済み** |
| Trial の実装変更 | 未承認 (本作業では発生せず) |
| 既存MoCKAへの統合 | 未承認 (行っていない) |
| 正式Primitive の追加 | 未承認 (本試験の語彙9件はすべて実験ローカル) |
| Decision Ledger への制度的採用 | 未承認 (行っていない) |
| Timさん由来資料の照合 | **資料未提供のため実施不能** |

---

## 8. 制度記録

`mocka_write_event` の結果は最終報告に記載する。
GL7 がblockされた場合、迂回せず、encoding mismatch を修正せず、失敗事実を報告する。

---

## 9. 関連文書

| 種別 | パス |
| ---- | ---- |
| 試験仕様 | `docs/tests/TIM_MOCKA_COMPARATIVE_TEST_v0.1.md` |
| 試験結果 | `docs/tests/TIM_MOCKA_COMPARATIVE_TEST_RESULTS_v0.1.md` |
| Source境界 (本文書) | `docs/audits/TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md` |
| 隔離実装 | `experiments/tim_mocka_comparative/` |
| CR Trial Evidence Lock | `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_EVIDENCE_LOCK_v0.1.md` |
