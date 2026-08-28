# MoCKA Constitutional Runtime v1.0-stubs Trial - Results

Status: EXPERIMENTAL / ISOLATED / NON-CANONICAL
Date: 2026-08-28
作成: くろこ (Claude Code)
試験仕様: `docs/tests/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_TEST_SPEC.md`
監査JSON: `experiments/constitutional_runtime_trial/results/trial_results.json`
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 実行環境

| 項目 | 値 |
| ---- | -- |
| Python | 3.11.15 |
| 固定時刻 | 2026-08-28T12:00:00Z |
| 実行コマンド (Case) | `python -m experiments.constitutional_runtime_trial.run_trial` |
| 実行コマンド (不変条件) | `python -m pytest experiments/constitutional_runtime_trial/tests/ -q` |
| 外部依存 | なし (標準ライブラリのみ) |
| 本番接続 | なし |

---

## 1. サマリ

```text
Case          : 24 件 (Basic 10 / Extended 12 / Test50境界 2)
PASS          : 24
FAIL          : 0
EXECUTE到達   : 2 件 (B01, E00 - いずれも統制Case)
pytest        : 117 passed
```

統制Case以外でEXECUTEへ到達したものは **0件** である。
同時に、統制Case2件は正しくEXECUTEへ到達している。
すなわち本Runtimeは"常に止まるだけの装置"ではない。

---

## 2. Case別結果 (実行出力そのまま)

| Test ID | Runtime | Structured Contract | Primitive | Expected | Actual | Execution | Evidence | Result |
| ------- | ------- | ------------------- | --------- | -------- | ------ | --------- | -------- | ------ |
| B01 | Basic | 12 typed field(s), 0 prose field(s) quarantined | - | ALLOW | ALLOW | EXECUTE | DESIGNED | PASS |
| B02 | Basic | 12 typed field(s), 0 prose field(s) quarantined | AUTHORITY_LOST | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| B03 | Basic | 12 typed field(s), 0 prose field(s) quarantined | INADMISSIBLE | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| B04 | Basic | 12 typed field(s), 0 prose field(s) quarantined | EXPIRED | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| B05 | Basic | 12 typed field(s), 0 prose field(s) quarantined | INTEGRITY_FAILURE | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| B06 | Basic | none (no inspectable contract) | CONTRACT_INVALID | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| B07 | Basic | none (no inspectable contract) | CONTRACT_INVALID | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| B08 | Basic | 12 typed field(s), 0 prose field(s) quarantined | UNKNOWN | BLOCK or UNKNOWN | UNKNOWN | STOP | DESIGNED | PASS |
| B09 | Basic | 12 typed field(s), 0 prose field(s) quarantined | - | BLOCK | BLOCK | STOP | DERIVED | PASS |
| B10 | Basic | 12 typed field(s), 0 prose field(s) quarantined | CONTRACT_INVALID | BLOCK | BLOCK | STOP | DERIVED | PASS |
| E00 | Extended | 18 typed field(s), 0 prose field(s) quarantined | - | ALLOW | ALLOW | EXECUTE | DESIGNED | PASS |
| E01 | Extended | none (no inspectable contract) | CONTRACT_MISSING | BLOCK | BLOCK | STOP | DERIVED | PASS |
| E02 | Extended | 18 typed field(s), 0 prose field(s) quarantined | AUTHORITY_LOST | BLOCK | BLOCK | STOP | DERIVED | PASS |
| E03 | Extended | 17 typed field(s), 1 prose field(s) quarantined | CONTRACT_SEMANTICALLY_INCOMPLETE | BLOCK or UNKNOWN | BLOCK | STOP | DERIVED | PASS |
| E04 | Extended | 17 typed field(s), 1 prose field(s) quarantined | SIGNATURE_MISSING | BLOCK | BLOCK | STOP | DERIVED | PASS |
| E05 | Extended | 18 typed field(s), 0 prose field(s) quarantined | EXPIRED, TIMESTAMP_MISMATCH | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| E06 | Extended | 18 typed field(s), 0 prose field(s) quarantined | NONCE_REUSED | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| E07 | Extended | 18 typed field(s), 0 prose field(s) quarantined | CONTEXT_MISMATCH | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| E08 | Extended | 19 typed field(s), 0 prose field(s) quarantined | MULTIPLE_RE_CONFLICT | BLOCK | BLOCK | STOP | DESIGNED | PASS |
| E09 | Extended | 17 typed field(s), 0 prose field(s) quarantined | CONTRACT_SEMANTICALLY_INCOMPLETE | BLOCK or UNKNOWN | UNKNOWN | STOP | DESIGNED | PASS |
| E10 | Extended | 19 typed field(s), 0 prose field(s) quarantined | BINDING_UNMAPPED | BLOCK or UNKNOWN | UNKNOWN | STOP | DERIVED | PASS |
| E2E-BOUNDARY-01 | Extended | 5 typed field(s), 1 prose field(s) quarantined | CONTRACT_SEMANTICALLY_INCOMPLETE, SIGNATURE_MISSING, NONCE_REUSED, BINDING_MISSING, WITNESS_MISSING, VERDICT_MISSING | BLOCK or UNKNOWN | BLOCK | STOP | DERIVED | PASS |
| T50-BASIC | Basic | 5 typed field(s), 2 prose field(s) quarantined | CONTRACT_INVALID | BLOCK or UNKNOWN | BLOCK | STOP | DERIVED | PASS |
| T50-EXTENDED | Extended | 5 typed field(s), 2 prose field(s) quarantined | CONTRACT_SEMANTICALLY_INCOMPLETE, SIGNATURE_MISSING, NONCE_REUSED, BINDING_MISSING, WITNESS_MISSING, VERDICT_MISSING | BLOCK or UNKNOWN | BLOCK | STOP | DERIVED | PASS |

Reason欄を含む完全な監査レコードは `trial_results.json` にある。

---

## 3. 個別所見

### 3.1 B09 のPrimitiveが空である理由 (仕様どおり)

B09のReasonは `bound RE verdict BLOCK honored as a denial`。
Primitiveは0件である。これは異常ではない。

bound verdictによる否認は"異常検出"ではなく"権限のある否認の尊重"であり、
Primitiveを立てる事象ではない。決定は下限演算 (`ALLOW meet BLOCK = BLOCK`) で下がる。
Primitiveを立てないことで、監査上"異常が検出された停止"と
"正当な否認による停止"が区別できる。

### 3.2 B10 の追加検証 (中核)

B10はBLOCKになるだけでは不十分であり、停止理由が binding 欠落であることを確認した。

```text
B10 原形    : re_verdict=BLOCK, binding_status=MISSING
              -> BLOCK / CONTRACT_INVALID (field=binding_status)
B10 反転形  : re_verdict=ALLOW, binding_status=MISSING
              -> BLOCK / CONTRACT_INVALID (field=binding_status)
```

verdictを反転させても決定もPrimitiveも変化しない。
すなわち判定はverdictを読んでいない。

### 3.3 E05 が2 Primitiveを返した理由

期待は BLOCK、実際も BLOCK であるが、Primitiveは `EXPIRED, TIMESTAMP_MISMATCH` の2件。

fixtureの `issued_at` (11:30) が期限切れ用の `expires_at` (11:00) より後になっているため、
Extendedの全件収集評価が発行時刻の逆転も併せて検出した。
Basicなら短絡評価で `EXPIRED` の1件で止まる。
両Runtimeの評価方式の差が結果に現れた例であり、意図した挙動である。

### 3.4 E09 と E10 が UNKNOWN で止まった意義

- E09: 封筒は妥当だが意味的に不完全 -> `CONTRACT_SEMANTICALLY_INCOMPLETE` -> UNKNOWN -> STOP
- E10: CR語彙に無いPrimitive名を宣言 -> `BINDING_UNMAPPED` -> UNKNOWN -> STOP

E10は、報告された `PASS (Unmapped)` 型の挙動に対応する境界である。
本TrialではUNKNOWNへ解決され、Gatewayで停止する。passには到達しない。
なお、既存CRがこの境界でどう振る舞ったかについて、本Trialは何も主張しない。

### 3.5 E2E-BOUNDARY-01 が BLOCK になった内訳

期待は `BLOCK または UNKNOWN`。実際は BLOCK。Findingは6件。

```text
CONTRACT_SEMANTICALLY_INCOMPLETE  (INDETERMINATE)  decision-bearing 7フィールド全欠落
SIGNATURE_MISSING                 (BLOCKING)       署名フィールド不在
NONCE_REUSED                      (BLOCKING)       nonce不在によりreplayを排除できない
BINDING_MISSING                   (BLOCKING)       binding_status不在
WITNESS_MISSING                   (BLOCKING)       witness不在
VERDICT_MISSING                   (BLOCKING)       typed verdict不在
```

BLOCKINGが5件あるため還元結果はBLOCKとなった。
UNKNOWNのみで止まる設計も可能だったが、実際には複数の独立した遮断経路が
同時に成立している。Fail-Closedが単一点に依存していないことを示す。

---

## 4. 実装中に検出した実欠陥 (1件、修正済み)

不変条件試験 `test_gateway_stops_on_unknown_and_on_anything_unrecognized` が
初回実行で失敗した。

```text
assert gate("ALLOW") is Execution.STOP
E  AssertionError: assert <Execution.EXECUTE> is <Execution.STOP>
```

原因: `Decision` を `str` 継承のEnumとして定義したため、素の文字列 `"ALLOW"` が
`Decision.ALLOW` と等価にハッシュされ、Gatewayの写像表を通過した。
型のないラベルが実行ゲートを開けられる状態だった。

これは本Trialが排除しようとしている混同そのもの (`A label is not a binding.`) が、
実装内部で再発した事例である。

修正: `gate()` と `apply_bound_verdict()` に `isinstance(decision, Decision)` 検査を追加。
型でないものは STOP / UNKNOWN へ落とす。
再実行後、117試験すべて通過。

記録の意義: この欠陥は"設計文書が正しいこと"と"実装が設計どおりであること"が
別問題であることの実例である。試験を先に書いていなければ検出されなかった。

---

## 5. 旧50試験とのBoundary Comparison (指示書 第25節 手順9)

### 5.1 参照する旧観測の性質

以下は指示書 第3節でReference Evidenceとして提供された数値である。

```text
Total Tests = 50 / MATCH = 20 / GAP = 30 / MATCH Rate 40.0% / GAP Rate 60.0%
```

分類上の注意 (重要):
本セッションからは、この50試験の一次資料 (試験ページ・ハーネス出力・Evidence Index) に
到達できていない。前段調査で全探索面を確認済みである
(`docs/audits/CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md`)。
したがって上記数値の分類は `OBSERVED (provided, not independently verified)` とする。
本Trialの結果は、この数値の真偽に依存しない。

### 5.2 報告されたGAPクラスと本Trialの対応

| 旧観測のGAPクラス | 報告内容 | 本Trialの対応Case | 本Trialの結果 |
| ----------------- | -------- | ----------------- | ------------- |
| Test 21-30 系 | RE = Block / CR = Allow (staleness境界) | B04, E05 (期限), E06 (replay) | すべてSTOP |
| Test 31-40 系 | P-02のみMATCH、他は RE = Block / CR = Allow | E05 (時間), E07 (context), E02 (authority) | すべてSTOP |
| Test 41-50 系 | Verification Contract境界でGAP | E03, E04, E09, E2E-BOUNDARY-01 | すべてSTOP |
| Test 50 | RE = Deny (自然言語) / CR = Allow / Execution = CONTINUE / Binding = absent | T50-BASIC, T50-EXTENDED | 両者ともSTOP |

対応付けは意味論的境界のレベルであり、旧試験の個別テストとの1対1対応ではない。
旧試験の入力・期待値・実測値は `UNKNOWN` のままである。

### 5.3 Test 50境界の直接比較

| 項目 | 報告された旧観測 | T50-BASIC | T50-EXTENDED |
| ---- | ---------------- | --------- | ------------ |
| 入力 | RE = Block (自然言語)、Binding = absent | 同じ意味論的境界 | 同じ意味論的境界 |
| Decision | Allow | BLOCK | BLOCK |
| Execution | CONTINUE | STOP | STOP |
| 停止根拠 | (該当なし) | CONTRACT_INVALID (typed intake 7 defect) | BINDING_MISSING 他5件 |
| Prose中の FORCED_INADMISSIBLE | (プロンプト本文中の記述) | 隔離。判定に不使用 | 隔離。判定に不使用 |
| Prose中の CRYPTOGRAPHICALLY_SIGNED_DENY_STATE | (プロンプト本文中の記述) | 隔離。判定に不使用 | 隔離。判定に不使用 |

重要な限定:
この表は"本Trialが旧CRより優れている"ことを示すものではない。
比較対象の内部実装は `NOT OBSERVED` であり、優劣を判定する材料がない。
この表が示すのは、`同じ意味論的境界を与えたとき、本Trialは停止する` という事実のみである。

---

## 6. Final Research Question への回答

> Can a typed, evidence-bound Constitutional Runtime prevent the exact class of
> RE-to-CR binding gaps observed in the 50-test boundary experiment?

本試験の範囲で言える回答。

**言えること (Evidence-bound):**

- 本Trialの24 Case・117不変条件試験の範囲において、REの否認がProseに留まり
  構造化・binding されていない入力は、Basic版・Extended版とも1件もALLOWへ到達しなかった
- 到達しなかった理由は複数経路で独立に成立しており、単一点に依存していない
  (E2E-BOUNDARY-01で5件のBLOCKING遮断が同時成立)
- Prose中に遮断を示唆する文字列が存在しても、判定は一切変化しない
  (不変条件試験10パターンで確認)
- 判定はverdictの値に依存していない (B10反転検証)

**言えないこと (UNKNOWN):**

- 旧50試験の各テストを本Trialに与えた場合に何が起きるか。入力が未入手のため不明
- 本Trialが"Binding Gapの全クラス"を防止するか。試験したのは本仕様が定義した
  境界のみであり、未知の境界については何も言えない
- 既存CRがなぜAllowになったのか。内部実装が `NOT OBSERVED` であるため不明

したがって回答は次の形に限定される。

> 本Trialが定義・試験した境界の範囲では、typed かつ evidence-bound な構造により、
> 報告されたRE-to-CR binding gapと同じ意味論的境界での実行継続は発生しなかった。
> これを一般化して"binding gapを防止できる"と述べることは、現時点の証拠からはできない。

---

## 7. 再現手順

```bash
python -m experiments.constitutional_runtime_trial.run_trial --markdown
python -m pytest experiments/constitutional_runtime_trial/tests/ -q
```

いずれもMoCKA本番サーバ・DB・ネットワークを必要としない。
