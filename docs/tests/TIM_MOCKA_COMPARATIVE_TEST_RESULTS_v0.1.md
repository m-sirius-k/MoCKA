# TIM_MOCKA_COMPARATIVE_TEST v0.1 - Results

Status: EXPERIMENTAL / ISOLATED / NON-CANONICAL
Date: 2026-08-28
実施: くろこ (Claude Code)
試験仕様: `docs/tests/TIM_MOCKA_COMPARATIVE_TEST_v0.1.md`
Source境界: `docs/audits/TIM_MOCKA_SOURCE_BOUNDARY_v0.1.md`
結果JSON: `experiments/tim_mocka_comparative/results/comparative_results.json`
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 実行環境

| 項目 | 値 |
| ---- | -- |
| Python | 3.11.15 |
| 固定時刻 | 2026-08-28T12:00:00Z |
| 実行 (matrix) | `python -m experiments.tim_mocka_comparative.run_comparative` |
| 実行 (不変条件) | `python -m pytest experiments/tim_mocka_comparative/tests/ -q` |
| 外部依存 | なし (標準ライブラリのみ) |
| 本番接続 | なし |

---

## 1. サマリ

```text
Matrix Case       : 10 件 (T01-T10)
PASS              : 10
FAIL              : 0
EXECUTE 到達      : 1 件 (T01 = 統制ケース)
False-positive 検査: 10/10 が宣言どおりの Finding のみを出した
不変条件試験      : 42 passed
```

Regression Baseline (指示書 第12節、変更禁止) は影響を受けていない。

```text
Constitutional Runtime Trial : 117 passed / 24 case pass / 0 fail (作業前後で同一)
既存ファイルの差分            : 0
```

---

## 2. Matrix 結果 (実行出力そのまま)

| Case | 過去 | 現在 | Eligibility | Execution | Findings |
| ---- | ---- | ---- | ----------- | --------- | -------- |
| T01 | Allow | premises unchanged | ELIGIBLE | **EXECUTE** | PREMISES_UNCHANGED |
| T02 | Allow | validity expired | RE_EVALUATE | STOP | TEMPORAL_EXPIRED |
| T03 | Allow | authority revoked | BLOCK | STOP | AUTHORITY_REVOKED |
| T04 | Allow | evidence changed | RE_EVALUATE | STOP | EVIDENCE_CHANGED |
| T05 | Allow | context content changed | RE_EVALUATE | STOP | CONTEXT_CHANGED |
| T06 | Block | premises unchanged | ELIGIBLE | STOP | PREMISES_UNCHANGED |
| T07 | Block | state improved | RE_EVALUATE | STOP | EVIDENCE_CHANGED |
| T08 | UNKNOWN | no new evidence | UNKNOWN | STOP | NO_NEW_EVIDENCE |
| T09 | UNKNOWN | new evidence present | RE_EVALUATE | STOP | NEW_EVIDENCE_PRESENT |
| T10 | Allow (reused) | context mismatch | RE_EVALUATE | STOP | CONTEXT_MISMATCH |

`Evidence` / `Timestamp` / `Decision` / `Authority` / `Validity` /
`Current Context` / `Execution Eligibility` の分離記録は結果JSONにある。

### 2.1 注目すべき2行

```text
T06  過去 Block + 前提不変 -> ELIGIBLE / STOP
     再利用可能であることと、実行が許されることは別である。
     ELIGIBLE は "再利用してよい" であって "許可" ではない。

T01  過去 Allow + 前提不変 -> ELIGIBLE / EXECUTE
     唯一 EXECUTE に到達した行。これが無ければ Gate は
     "何も通さない装置" と区別できない。
```

---

## 3. 採点結果 (5軸、指示書 第10節)

| Case | Evidence preservation | Temporal validity | Authority continuity | Context continuity | Re-evaluation correctness |
| ---- | --------------------- | ----------------- | -------------------- | ------------------ | ------------------------- |
| T01 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASS |
| T02 | NOT_TESTED | **PASS** | NOT_TESTED | NOT_TESTED | PASS |
| T03 | NOT_TESTED | NOT_TESTED | **PASS** | NOT_TESTED | PASS |
| T04 | **PASS** | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASS |
| T05 | NOT_TESTED | NOT_TESTED | NOT_TESTED | **PASS** | PASS |
| T06 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASS |
| T07 | **PASS** | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASS |
| T08 | **PASS** | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASS |
| T09 | **PASS** | NOT_TESTED | NOT_TESTED | NOT_TESTED | PASS |
| T10 | **UNKNOWN** | NOT_TESTED | NOT_TESTED | **PASS** | PASS |

集計。

```text
evidence_preservation      PASS=4  UNKNOWN=1  NOT_TESTED=5
temporal_validity          PASS=1             NOT_TESTED=9
authority_continuity       PASS=1             NOT_TESTED=9
context_continuity         PASS=2             NOT_TESTED=8
re_evaluation_correctness  PASS=10
FAIL                       0件
```

### 3.1 採点方式について (作業中に修正した点)

初回実装では、ケースが変化させていない次元も"変化が検出されなかったこと"を
PASS として数えていた。その結果 `temporal_validity PASS=10` という集計が出た。

これは誤解を招く。実際に有効期限を変化させているケースは **T02 の1件のみ** である。
10件が時間軸を試験したかのように読める集計は、試験の網羅度を過大に見せる。

修正後は、**そのケースが実際に変化させた次元のみを PASS/FAIL で採点** し、
変化させていない次元は `NOT_TESTED` とした。
その結果、集計は"各次元を実際に試験しているケース数"を表すようになった。

変化させていない次元が誤検出されないことは、
軸集計に混ぜず **False-positive 検査** として別に測定している (10/10)。

### 3.2 UNKNOWN の使用 (1件)

`T10 / evidence_preservation = UNKNOWN`

Context が別である場合、evidence digest の比較は機械的には可能である。
しかし **Context 境界を跨いだ Evidence 比較が意味を持つか** は本試験では決定できない。
PASS にも FAIL にもしていない。指示書 第10節に従い、UNKNOWN を FAIL として扱わない。

---

## 4. Critical Test: T50-TIM-REUSE

同一の DecisionRecord に対する2経路の比較。入力は、Gate が観測できるすべての前提が
変化している状態 (期限切れ / Evidence 変化 / Authority 変更 / Context 不一致 / Context 内容変化)。

| | Path A (直接再利用) | Path B (再評価あり) |
| - | ------------------- | ------------------- |
| 出力 | **ALLOW** | RE_EVALUATE / STOP |
| 現在との比較回数 | **0** | 4 |
| Findings | (なし。比較していない) | CONTEXT_MISMATCH, AUTHORITY_CHANGED, TEMPORAL_EXPIRED, EVIDENCE_CHANGED |
| Evidence preservation | FAIL | PASS |
| Temporal validity | FAIL | PASS |
| Authority continuity | FAIL | PASS |
| Context continuity | FAIL | PASS |
| Re-evaluation correctness | FAIL | PASS |
| 正当性 | **NOT A LEGITIMATE ALLOW** | - |

### 4.1 A の ALLOW をどう扱うか

```text
A は ALLOW を返した。しかしこれは
"過去の verdict をそのまま返した" 以上のことを意味しない。
現在の Evidence / Authority / Context / 有効期限を1つも参照していない。
```

指示書 第7節の規定どおり、この出力を正当な Allow として評価しない。
A は **アンチパターンの統制** として実装されており、
5軸すべてで FAIL となることが設計上の期待値である (実測でそのとおりになった)。

A が存在することには意味がある。全軸で FAIL になりうる経路を持たない採点表は、
PASS が何を意味するかを示せないためである。

### 4.2 B について確認されたこと

B では、現在の Evidence と Authority が実際に再検証された。
4つの独立した Finding が同時に立ち、いずれか1つでも RE_EVALUATE には十分である。

---

## 5. 3層への分離 (指示書 第8節)

### Layer 1: Observed (試験で実際に観測された事実)

| # | 事実 |
| - | ---- |
| 1 | 10ケースすべてが期待どおりの Eligibility / Execution を返した |
| 2 | EXECUTE に到達したのは T01 (過去 Allow + 前提不変) の1件のみ |
| 3 | 288通りの全数探索で、EXECUTE に到達した組合せは **1つだけ** (過去 ALLOW かつ全前提不変) |
| 4 | `RE_EVALUATE` と `UNKNOWN` は1件も EXECUTE に到達しなかった |
| 5 | 再利用可能な過去 BLOCK (T06) は ELIGIBLE だが STOP のまま |
| 6 | 過去 Block + Evidence 改善 (T07) は自動 Allow にならず RE_EVALUATE |
| 7 | 過去 UNKNOWN は、新 Evidence が無い限り UNKNOWN のまま (T08) |
| 8 | 単一前提の変化6種すべてで、過去 Allow が EXECUTE に到達しなくなる |
| 9 | Path A は現在を0回しか参照せず ALLOW を返す。Path B は同一入力で STOP |
| 10 | 型でない値 (`"ELIGIBLE"` 等) は Execution Gate を通過しない |

### Layer 2: Derived (試験結果から限定的に導出できる性質)

| # | 導出 | 限定 |
| - | ---- | ---- |
| 1 | 本 Gate の構造では、過去の Allow それ自体は現在の実行根拠にならない | 本 Gate が観測できる4次元 (Evidence / 時間 / Authority / Context) に限る |
| 2 | 再利用可能性 (Eligibility) と許可 (Execution) は分離できる | T06 が実例 |
| 3 | UNKNOWN は保持でき、Allow へ暗黙変換されない | 本 Gate の還元規則の範囲で |
| 4 | "判断"ではなく"判断が成立した条件"を保存すれば、再検証が可能になる | 条件の表現が digest である範囲で |
| 5 | 直接再利用と再評価は、同一入力で異なる結果を出す | Path A / B の対比による |

### Layer 3: Designed (Constitutional Runtime へ実装する場合の設計案)

**これは設計案であり、正式仕様ではない。** 採用には別途 Human Gate を要する。

指示書 第13節が挙げる流れ。

```text
Evidence -> Validity -> Authority -> Context -> Re-evaluation -> Decision -> Execution Gate
```

本試験で実装した Gate はこの流れの **Re-evaluation の部分だけ** を扱っている。

| 概念 (指示書 第9節) | 本試験での扱い | 正式Primitive採用 |
| ------------------- | -------------- | ----------------- |
| Decision | 過去判断 3値 (ALLOW/BLOCK/UNKNOWN) として実装 | **未決定** |
| Evidence | digest として実装。内容的妥当性は扱わない | **未決定** |
| Validity | validity_until (Temporal Boundary) として実装 | **未決定** |
| Authority | authority_id + authority_state として実装 | **未決定** |
| Context | context_id + context_digest として実装 | **未決定** |
| Temporal Boundary | validity_until として実装 | **未決定** |
| Re-evaluation | Eligibility 4値として実装 | **未決定** |

指示書 第9節の明示に従い、**この試験だけでは採用を決定しない**。

### Layer 4 (別枠): Original CR

```text
Evidence Status: NOT OBSERVED / UNKNOWN
```

本試験は Original CR について何も述べない。
本試験の結果を Original CR の性質として記録しない。

---

## 6. 本試験で確定していないこと

| # | 事項 | 分類 |
| - | ---- | ---- |
| 1 | Timさん側で実際に問題となった判断境界と一致するか | **検証不能** (資料未提供。Source境界文書 第1.4節) |
| 2 | 再評価の結果がどうなるか | 対象外。本 Gate は"再評価が必要か"までしか判定しない |
| 3 | T07 で改善後に Allow になるか | UNKNOWN。Gate の外側 |
| 4 | Context 境界を跨いだ Evidence 比較の意味 | UNKNOWN (T10) |
| 5 | Evidence の内容的妥当性 | 対象外。digest の一致のみ |
| 6 | Authority の正統性 | 対象外。状態と識別子のみ |
| 7 | 実環境での有効性 | 対象外。隔離実験 |
| 8 | Original CR が同様の Gate を持っていたか | NOT OBSERVED / UNKNOWN |

---

## 7. Final Source Boundary (指示書 第14節)

> Original Constitutional Runtime v1.0-stubs was not recovered.
>
> The MoCKA Constitutional Runtime is an independently designed reconstruction
> and must not be treated as evidence of the original implementation.

加えて本作業固有の境界。

> No source material from Tim was supplied to this session. The case matrix
> implemented here comes from the commissioning instruction itself, and this
> experiment must not be treated as evidence of what Tim's position is.

---

## 8. 再現手順

```bash
python -m experiments.tim_mocka_comparative.run_comparative
python -m pytest experiments/tim_mocka_comparative/tests/ -q
```

MoCKA本番サーバ・DB・ネットワークを必要としない。
