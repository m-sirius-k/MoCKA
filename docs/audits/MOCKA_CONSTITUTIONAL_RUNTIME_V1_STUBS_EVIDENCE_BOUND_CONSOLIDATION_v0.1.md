# Constitutional Runtime v1.0-stubs - Evidence-Bound Consolidation v0.1

Status: CONSOLIDATION RECORD / NON-CANONICAL / NO-CHANGE WORK
Date: 2026-08-28
実施: くろこ (Claude Code)
指示: きむら博士 - Evidence-Bound Consolidation and Trial Separation (作業順序 26)
Branch: claude/constitutional-runtime-investigation-jgqkv1

本文書は既存成果物を1つも変更していない。新規の整理文書である。

---

## 0. 本文書の唯一の目的

元の `Constitutional Runtime v1.0-stubs` について分かっていることと、
MoCKAが新たに構築した Trial を **完全に分離し、その境界自体を監査可能にする** こと。

元CRを当てることは目的ではない。

---

## A. Executive Summary

### A-1. Original CRについて分かっていること

```text
分かっていること : 名称のみ。
                   "Constitutional Runtime v1.0-stubs" という名称が、
                   きむら博士の調査指示書においてCR側を指す語として提示された。

分かっていないこと: 内部コード、Primitive実装、Decision Gateway、
                   Contract Binding、状態集合、評価規則、入出力形式。
                   いずれも NOT OBSERVED / UNKNOWN。
```

前段調査 (`CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md`) において、
到達可能な全探索面 (公開Web検索8クエリ / 直接URL取得 / GitHubコード検索 /
アカウント配下18リポジトリ / MoCKA本体50ブランチ / ローカル作業ツリー全文 /
ローカルSQLite 4DB / MoCKA本番 events.db + knowledge gate / Notion workspace /
Claude Code Artifact 22件) を確認し、対象15識別子は **1件も観測されなかった**。

**重要**: これは"存在しない"ではない。"本セッションから観測できない"である。
この2つを本文書は最後まで混同しない。

### A-2. 本作業時点での5層の状態

| 層 | 対象 | 状態 |
| -- | ---- | ---- |
| 1 | Original CR v1.0-stubs | NOT OBSERVED / UNKNOWN |
| 2 | Original 50-Test Evidence | OBSERVED (provided) / 原ログ未回収 |
| 3 | MoCKA Trial-Basic | DESIGNED / IMPLEMENTED / TESTED |
| 4 | MoCKA Trial-Extended | DESIGNED / IMPLEMENTED / 部分TESTED |
| 5 | Trial Audit Findings | 実測に基づく。対象はTrialのみ |

層1と層3-4の間には **導出関係が存在しない**。
層2 (観測された境界条件) を経由した設計判断のみが存在する。

---

## B. Original CR Evidence Boundary

### B-1. 分類

| 項目 | 分類 | 根拠 |
| ---- | ---- | ---- |
| 名称 `Constitutional Runtime v1.0-stubs` | 指示書記載 (Instruction-level) | 博士の指示書に現れた名称。Web上の一次資料は未到達 |
| 内部コード / ソース | NOT OBSERVED | 全探索面で未発見 |
| Primitive実装 | NOT OBSERVED | 同上 |
| Decision Gateway | NOT OBSERVED | 同上 |
| Contract Binding機構 | NOT OBSERVED | 同上 |
| 状態集合 / 評価規則 | UNKNOWN | 推定不能 |
| 入出力形式 | UNKNOWN | 推定不能 |
| Fail-Closed機構の有無 | UNKNOWN | **存在しないとは述べない** |
| 公開Web上の同名プロジェクトとの関係 | UNKNOWN | 版名・語彙とも不一致。同定しない |

### B-2. NOT OBSERVED と UNKNOWN の使い分け

本文書での定義。

```text
NOT OBSERVED : 探索を実施し、観測されなかった。探索範囲は記録済み。
UNKNOWN      : 観測材料が原理的に不足しており、真偽を論じられない。
存在しない   : 本文書では一度も使用しない。証明手段が無いため。
```

---

## C. Original 50-Test Evidence Status

### C-1. 提供された情報

```text
Total Tests = 50 / MATCH = 20 / GAP = 30 / MATCH Rate 40.0% / GAP Rate 60.0%

Test 01-20 : 正常系および直接攻撃系でRE/CR判定一致
Test 21-30 : RE = Block / CR = Allow のGAP
Test 31-40 : P-02のみMATCH。その他は RE = Block / CR = Allow
Test 41-50 : Verification Contract境界でGAP
Test 50    : RE = Deny / CR = Allow / Execution = CONTINUE
```

### C-2. 4区分による分離の試み (指示書 第3.2節)

指示書は、原ログ由来 / 正規化ラベル / ハーネス側ラベル / レポート作成時の解釈 を
可能な限り区別せよと求めている。**現時点でこの分離は完了できない。**

| 情報 | 原ログ由来か | 正規化ラベルか | ハーネス側ラベルか | 解釈か |
| ---- | ------------ | -------------- | ------------------ | ------ |
| 50 / 20 / 30 の件数 | UNKNOWN | - | - | UNKNOWN |
| MATCH / GAP の分類 | UNKNOWN | UNKNOWN | UNKNOWN | **可能性あり** (判定は誰かが行う) |
| `AUTHORITY_LOST` | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| `ADMISSIBLE (Fail)` | UNKNOWN | **可能性が高い** (括弧付き複合表記は表示形式に見える) | UNKNOWN | UNKNOWN |
| `PASS (Unmapped)` | UNKNOWN | **可能性が高い** (同上) | UNKNOWN | UNKNOWN |
| `Monotonic Time Check` | UNKNOWN | UNKNOWN | **可能性あり** (Check は検査名の語法) | UNKNOWN |
| P-01 - P-10 | UNKNOWN | UNKNOWN | **可能性あり** (連番は試験側の採番に見える) | UNKNOWN |

**可能性あり / 可能性が高い** は表記の形式から述べているだけであり、
証拠ではない。いずれも `Derived (weak)` を超えない。
この表は"分離できていない"ことを記録するための表である。

### C-3. 断定してはならない名称

以下を Original CR の **内部Primitive名として断定しない**。

```text
AUTHORITY_LOST
ADMISSIBLE (Fail)
PASS (Unmapped)
Monotonic Time Check
その他、原実装由来であることが確認できない一切の名称
```

これらは `Observed / normalized label` として扱う。
MoCKA Trial がこれらに似た名称を持つことは、
Original CR がそれを持っていたことの証拠にはならない。

### C-4. 分類の総括

```text
Observed (provided) : 上記C-1の数値・分類そのものが博士から提供された事実
未回収              : Evidence Index (EV-TST-001 - EV-TST-050) の実体
未回収              : 原実行データ / ハーネス出力 / 試験ページ
UNKNOWN             : 各テストの入力・期待値・実測値
```

本Trialの結論は、C-1の数値の真偽に依存しない。

---

## D. Test 50 Evidence Boundary

指示書 第2節 Rule 3 の A-G を適用する。**A の情報を D または E として記述しない。**

### D-1. 7区分の割り当て

| 区分 | 内容 | Test 50における状態 |
| ---- | ---- | ------------------- |
| A. Original Web page / prose | プロンプト本文。`FORCED_INADMISSIBLE`、`CRYPTOGRAPHICALLY_SIGNED_DENY_STATE`、自然言語のDeny/Block勧告 | **提供された報告として存在**。原文そのものは未入手 |
| B. Original structured runtime input | 構造化された実行時入力 | **確認できない** |
| C. Harness-generated structured value | ハーネスが構造化して保持した値 | **確認できない** |
| D. CR actually received value | CRが実際に受領した値 | Contract fields = UNKNOWN / empty。Primitive fields = UNKNOWN / empty |
| E. CR actually evaluated primitive | CRが実際に評価したPrimitive | Primitive Scan が `PASS / Unmapped` として **報告された**。ただしこれが E なのか C なのかは UNKNOWN |
| F. Observed execution result | 実行結果 | CR = Allow / Execution = Continue (報告として) |
| G. Derived interpretation | 解釈 | 下記 D-3 |

### D-2. A と D/E の分離 (最重要)

```text
プロンプト本文に存在した
    FORCED_INADMISSIBLE
    CRYPTOGRAPHICALLY_SIGNED_DENY_STATE
は、CRが実際に受領・評価したPrimitiveではない。
```

この2語は区分 A に属する。D にも E にも属さない。
文字列がプロンプトに存在したことは、Primitiveが成立したことを意味しない。

### D-3. 許される結論の上限

```text
End-to-End Binding was not established in the observed test condition.
```

これを超える主張は行わない。特に以下は述べない。

- CRにbinding機構が無かった
- CRがProseを読んでいた / 読んでいなかった
- CRのPrimitive Scanが `PASS (Unmapped)` という内部状態を持っていた
- Allowになった原因が特定できた

### D-4. E区分の曖昧性について

`Primitive Scan = PASS / Unmapped として報告された` という情報は、
区分 E (CRが実際に評価した) と区分 C (ハーネスが生成した表示) の
いずれに属するか **決定できない**。

したがって本文書はこれを E として扱わず、
`報告された表示。区分 C / E のいずれかは UNKNOWN` と記録する。

---

## E. MoCKA Trial Basic

### E-1. 三区分

| 区分 | 内容 |
| ---- | ---- |
| **Designed** | Typed Verification Contract (12フィールド)、Prose Quarantine、6語彙のPrimitive集合、9段の短絡規則列、bound verdictの下限演算、明示witness policy、Fail-Closed既定 |
| **Implemented** | `experiments/constitutional_runtime_trial/runtime_basic.py` ほか。標準ライブラリのみ。本番非接続 |
| **Tested** | Case 10件 (B01-B10) 全PASS。加えて不変条件試験。Basic tier 6語彙は **すべて試験中に励起される** |

### E-2. 由来の明示

Trial-Basic は Original CR の復元物ではない。
`observed boundary conditions from the available trial evidence` を基礎として
MoCKAが独自に設計・実装した experimental runtime である。

設計判断のうち観測に由来するもの / 由来しないものの分離は
`MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_DESIGN_EVIDENCE_BOUNDARY.md` 第3節に固定済み。
13行のうち5行 (3値Decision / 下限演算 / 署名再計算 / Replay検査 / trial-added語彙) は
Observed列が空である。

### E-3. 検証済みの性質

```text
Basic 全数グリッド 30,000通り  -> ALLOW到達は全良組合せの1件のみ
                                  UNKNOWN -> EXECUTE  0件
                                  例外                0件
12フィールド1つずつ欠落 12通り -> いずれもALLOWへ到達しない
```

---

## F. MoCKA Trial Extended

### F-1. 三区分

| 区分 | 内容 |
| ---- | ---- |
| **Designed** | 9カテゴリ31語彙、全件収集評価、3台帳による状態保持、Contract失敗の二段階化、署名再計算、bound条件の厳格化 |
| **Implemented** | `runtime_extended.py`。31語彙すべてコード上で到達可能 (静的解析で確認済み) |
| **Tested** | Case 12件 (E00-E10, E2E-BOUNDARY-01) 全PASS。ただし語彙カバレッジは **部分的** (下記 F-3) |

### F-2. 検証済みの性質

```text
Extended グリッド 10,000通り  -> ALLOW到達は全良組合せの1件のみ
                                 UNKNOWN -> EXECUTE  0件
                                 例外                0件
Prose不変性 5パターン x 2Runtime -> 決定・Primitive集合とも不変
Prose中にPrimitive名を記載      -> Finding 0件 (ALLOWのまま)
```

### F-3. Implemented / Not Exercised (重要)

31語彙のうち **10語彙が117テスト中一度も励起されない**。

| Primitive | Category | 状態 |
| --------- | -------- | ---- |
| AUTHORITY_MISMATCH | Authority | Implemented / Not Exercised |
| CONTRACT_SCHEMA_MISMATCH | Contract | Implemented / Not Exercised |
| CONTRACT_VERSION_DRIFT | Contract | Implemented / Not Exercised |
| DIGEST_MISMATCH | Integrity | Implemented / Not Exercised |
| NON_MONOTONIC_TIME | Temporal | Implemented / Not Exercised |
| NOT_YET_VALID | Temporal | Implemented / Not Exercised |
| REQUEST_REPLAY | Replay | Implemented / Not Exercised |
| VERDICT_MUTATED | Governance | Implemented / Not Exercised |
| WITNESS_CONFLICT | Evidence | Implemented / Not Exercised |
| WITNESS_INVALID | Evidence | Implemented / Not Exercised |

内訳: Basic tier 6語彙は全て励起される。Extended専用25語彙のうち15が励起、10が未励起。

**この10件を実装不良と断定しない。** 分類は `Implemented / Not Exercised` である。
静的解析では全31語彙がコード上で到達可能であることを確認済みである。
未確認なのは"実際にその条件で励起されるか"であって"実装されているか"ではない。

### F-4. Trial-added vocabulary の明示

Extended の31語彙のうち、指示書列挙外の追加は **1件のみ**。

```text
CONTRACT_SEMANTICALLY_INCOMPLETE
    origin   : trial-added
    severity : INDETERMINATE
    category : Contract
    追加理由 : 封筒が妥当で中身が決定不能な場合を、封筒の破損 (BLOCK) と
               区別してUNKNOWNとして保持するため
```

実装内の `origin` フィールドに `trial-added` として保持されており、機械照合可能である。
残り30語彙の origin は `instruction-listed` であるが、これは
**"指示書に列挙されていた"のみを意味し、"Original CRの内部Primitive名だった"を意味しない。**

---

## G. Trial Audit

対象は **Trial のみ** である。Original CR について何も述べていない。

### G-1. Finding一覧

| ID | Severity | 内容 | 状態 |
| -- | -------- | ---- | ---- |
| F-01 | MEDIUM | verdict独立性の記述が過剰一般化 | 未修正 (下記G-2) |
| F-03 | HIGH | trial-added語彙がE09の結果を単独決定 | 未修正 (下記G-3) |
| F-04 | MEDIUM | Extendedのwitness検査がBasicより弱い (blacklist形式) | 未修正 |
| F-05 | MEDIUM | nonce不在に `NONCE_REUSED` を立てる意味的混同 | 未修正 |
| F-07 | MEDIUM | 未検証フィールド型によるTypeError。例外境界が不在 | 未修正 |
| F-08 | MEDIUM | 拒否されたContractがnonce / high-water状態を汚染 | 未修正 |
| F-09 | MEDIUM | BasicはPolicy層 `decide()` を経由しない | 未修正 |
| Vocabulary Coverage | MEDIUM | 31語彙中10語彙が未励起 | `Implemented / Not Exercised` として分類 |

Severity は監査時の判定を維持する。修正はいずれも未実施であり、
提案は `MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_IMPROVEMENT_PLAN_v0.1.md` に分離した。

### G-2. F-01 の正しい記述 (再発防止)

既存 RESULTS 文書 第98行の記述

```text
すなわち判定はverdictを読んでいない。
```

は **誤りである**。正しくは次の2つを分離する。

```text
(1) 構造化され妥当なContractで binding_status = BOUND の場合、
    verdict は Decision の入力となる。
    実測: re_verdict=ALLOW -> ALLOW / BLOCK -> BLOCK / UNKNOWN -> UNKNOWN

(2) 自然言語上のverdictが構造化ContractへbindingされなければCRには入力されない。
    実測 (B10): binding_status = MISSING のとき、verdictをBLOCKからALLOWへ
    反転させても決定・Primitiveとも不変 (BLOCK / CONTRACT_INVALID)
```

B10が示したのは (2) であり、(1) の否定ではない。
既存文書は No Change Rule により修正していない。
**本文書が正誤表として機能する。**

### G-3. F-03 の Trial-added 依存 (明示)

反実仮想: `CONTRACT_SEMANTICALLY_INCOMPLETE` をFinding集合から除去した場合の再計算。

| Case | 実際 | 語彙除去時 | 判定 |
| ---- | ---- | ---------- | ---- |
| E03 | BLOCK | BLOCK | 依存なし |
| **E09** | **UNKNOWN** | **ALLOW / EXECUTE** | **完全に依存** |
| E2E-BOUNDARY-01 | BLOCK | BLOCK | 依存なし |
| T50-EXTENDED | BLOCK | BLOCK | 依存なし |

**Trialの安全性がこの語彙に依存する箇所は E09 のみである。**
中心試験 (E2E-BOUNDARY-01) と Test 50境界 (T50-EXTENDED) は依存しない。

**重要な非推論**: このFindingをもって、Original CR に同じPrimitiveが
存在した / 存在しなかったとは推論しない。両者は無関係である。

### G-4. 監査自体の限界

同一セッションによる自己監査であり独立性は無い。
監査プローブ自身に欠陥が1件あった (Extended全数探索の初回版で署名再計算漏れ)。
他のプローブに同種の欠陥が残存する可能性は排除できない。

---

## H. Non-Claims

Original CR について **推測してはならない事項** を列挙する。
以下はいずれも本作業群のどの文書でも主張していない。

| # | 禁止される主張 | 正しい状態 |
| - | -------------- | ---------- |
| 1 | Original CRを再現した | 再現していない。独立設計である |
| 2 | Original CRと同一である | 同一性は判定不能 (UNKNOWN) |
| 3 | Original CRの内部構造を復元した | 復元していない。NOT OBSERVED のまま |
| 4 | Original CRにFail-Closed機構が存在しない | 証明されていない。UNKNOWN |
| 5 | Original CRにFail-Closed機構が存在した | 同じく UNKNOWN |
| 6 | Original CRのPrimitive名が判明した | 判明していない |
| 7 | Test 50でCRが `FORCED_INADMISSIBLE` を受領した | 受領していない (区分Aの文字列) |
| 8 | `CRYPTOGRAPHICALLY_SIGNED_DENY_STATE` が構造化Contractとして実在した | 実在性は UNKNOWN |
| 9 | `PASS (Unmapped)` がCRの内部Primitiveである | 区分 C / E のいずれかは UNKNOWN |
| 10 | `ADMISSIBLE (Fail)` が正式Primitive名である | 断定しない。Trialでは不採用 |
| 11 | Test 50でAllowになった原因を特定した | 特定していない |
| 12 | MoCKA Trialが旧CRより優れている | 比較対象の内部が UNKNOWN のため判定不能 |
| 13 | MoCKA TrialがBinding Gapの全クラスを防止する | 試験したのは定義済み境界のみ |
| 14 | 旧50試験の各テストを本Trialに与えた結果が分かる | 入力未入手のため UNKNOWN |
| 15 | 公開Web上の同名プロジェクトが本件のCRである | 同定しない。UNKNOWN |

---

## I. Current Knowledge Graph

### I-1. 関係図

```text
  [ Original CR v1.0-stubs ]
        |
        | 内部実装 -> NOT OBSERVED / UNKNOWN
        | (この矢印から先へ、いかなる導出も行われていない)
        X
        |
        +---- 導出関係なし ----+
                               |
  [ Observed Test Boundary ]   |     50試験の報告 (provided)
        |                      |     原ログ・Evidence Index は未回収
        | empirical evidence   |
        |                      |
        v                      |
  [ MoCKA Trial Basic ]  <-----+     independent design
        |                            Designed / Implemented / Tested
        | 基礎として継承
        v
  [ MoCKA Trial Extended ]           adversarial extension
        |                            Designed / Implemented / 部分Tested
        |
        v
  [ Trial Audit ]                    findings against Trial only
                                     Original CR については何も述べない
```

### I-2. 関係の表形式

| 起点 | 終点 | 関係の種類 | 強度 |
| ---- | ---- | ---------- | ---- |
| Original CR | 内部実装 | NOT OBSERVED | 探索済み・未発見 |
| Original CR | MoCKA Trial | **関係なし** | 導出は一切行っていない |
| Observed Test Boundary | MoCKA Trial Basic | 設計の着想元 | 境界条件のみ。実装は継承していない |
| Observed Test Boundary | 原ログ | 未回収 | Evidence Index 未到達 |
| Trial Basic | Trial Extended | 基礎 -> 拡張 | 同一intake共有。評価方式と語彙は別 |
| Trial Audit | Trial Basic / Extended | 監査対象 | 実測に基づく |
| Trial Audit | Original CR | **関係なし** | 監査は Original CR を対象としない |

### I-3. 境界の要約 (1行)

```text
Original CR について言えるのは名称のみであり、
MoCKA Trial について言えるのは実測された性質のみであり、
その2つの間に導出の橋は存在しない。
```

---

## J. 検証結果 (指示書 第11節)

| # | 検証項目 | 結果 |
| - | -------- | ---- |
| 1 | `git diff` で既存Trialファイルが変更されていないこと | **確認済み**。作業前後とも既存ファイルの差分0 |
| 2 | 既存117 tests が変更なしでPASSすること | **確認済み**。117 passed |
| 3 | Original CRに関する未観測情報を断定していないこと | **確認済み**。B節・H節で明示 |
| 4 | Trial-added vocabulary を明示していること | **確認済み**。F-4節・G-3節 |
| 5 | Observed / Derived / Designed / Proposed / UNKNOWN を混同していないこと | **確認済み**。各節で分類を付与 |
| 6 | F-01の誤記が新規文書に再発していないこと | **確認済み**。G-2節で正しい2分割を記述。誤記の再掲は正誤表としてのみ |
| 7 | F-03のTrial-added依存を明示していること | **確認済み**。G-3節に反実仮想表を掲載 |

---

## K. 制度記録の状態

`mocka_write_event` は本作業でも `GL7_EXECUTION_BLOCKED` を返した。

```text
error : GL7_EXECUTION_BLOCKED
reason: GL7 abort: ['encoding_mismatch:data/n8n/database.sqlite',
                    'encoding_mismatch:di_terminology_inventory_20260820.txt',
                    'encoding_mismatch:s05_decision_extract.txt']
```

指示書 第12節に従い、迂回していない。
既存ファイルのencoding問題を理由とした勝手な修正も行っていない。
4作業連続で同一事象が継続している。

---

## L. 関連文書

| 種別 | パス |
| ---- | ---- |
| Web観測調査 (前段) | `docs/audits/CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md` |
| Trial-Basic 設計 | `docs/architecture/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_BASIC.md` |
| Trial-Extended 設計 | `docs/architecture/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_EXTENDED.md` |
| 試験仕様 | `docs/tests/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_TEST_SPEC.md` |
| 試験結果 | `docs/tests/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_RESULTS.md` (F-01の誤記あり。G-2節参照) |
| Evidence境界 | `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_DESIGN_EVIDENCE_BOUNDARY.md` |
| 設計監査 | `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_DESIGN_AUDIT_v0.1.md` |
| 改善提案 (本作業で新規) | `docs/architecture/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_IMPROVEMENT_PLAN_v0.1.md` |
| 将来設計候補 (本作業で新規) | `docs/architecture/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_EXTENDED_V2_CANDIDATES_v0.1.md` |
| 実装 | `experiments/constitutional_runtime_trial/` |
