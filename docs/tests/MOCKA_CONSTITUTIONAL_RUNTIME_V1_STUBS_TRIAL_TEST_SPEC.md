# MoCKA Constitutional Runtime v1.0-stubs Trial - Test Specification

Status: EXPERIMENTAL / ISOLATED / NON-CANONICAL
Date: 2026-08-28
作成: くろこ (Claude Code)
実装: `experiments/constitutional_runtime_trial/suites.py` および `tests/`
結果: `docs/tests/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_RESULTS.md`
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 本仕様の性質

本仕様が定義するのは、MoCKA Trial Runtimeに対する試験である。
既存 `Constitutional Runtime v1.0-stubs` に対する試験ではない。
過去の50試験は `Observed Behavioral Evidence` として参照するのみであり、
"正しい実装仕様"としては扱わない。

---

## 1. 試験環境と再現性

| 項目 | 値 |
| ---- | -- |
| 固定時刻 (NOW) | 2026-08-28T12:00:00Z |
| issued_at | 2026-08-28T11:30:00Z |
| expires_at (有効) | 2026-08-28T13:00:00Z |
| expires_at (期限切れ) | 2026-08-28T11:00:00Z |
| 依存 | Python標準ライブラリのみ |
| 実行 | `python -m experiments.constitutional_runtime_trial.run_trial` |
| 単体試験 | `python -m pytest experiments/constitutional_runtime_trial/tests/ -q` |

時刻は注入する。実時計に依存しないため、結果は再現可能である。

Case定義とテスト実行は同一モジュール (`suites.py`) を共有する。
公表結果と試験実行が乖離しない構造にしてある。

---

## 2. 監査記録項目 (指示書 第18節)

各Caseについて以下を記録する。

```text
Test ID
Input
Structured Contract
Primitive
Expected Decision
Actual Decision
Evidence Status
Reason
```

### 2.1 Evidence Status の意味

Evidence Status は **期待値の出所** を表す。試験の合否ではない。

| 値 | 意味 |
| -- | ---- |
| OBSERVED | 50試験境界実験から報告された事項 |
| DERIVED | OBSERVEDと明示された設計規則から導かれる |
| DESIGNED | 本Trial自身の仕様で確定している |
| PROPOSED | 提案段階。未確定 |
| UNKNOWN | 利用可能な証拠からは確定できない |

本試験仕様に `OBSERVED` の期待値は1件も存在しない。
観測されたのは挙動境界であって、期待される判定ではないためである。

---

## 3. Trial-Basic Suite (B01-B10)

| Test ID | 入力 | 期待 | Evidence | 主眼 |
| ------- | ---- | ---- | -------- | ---- |
| B01 | 完全に妥当なContract、bound verdict = ALLOW | ALLOW | DESIGNED | 統制。何も許可しないRuntimeは何も証明しない |
| B02 | authority_state = LOST | BLOCK | DESIGNED | 権限喪失 |
| B03 | admissibility_state = INADMISSIBLE | BLOCK | DESIGNED | 不受理 |
| B04 | expires_at が過去 | BLOCK | DESIGNED | 期限切れ |
| B05 | integrity_status = FAILED | BLOCK | DESIGNED | 完全性失敗 |
| B06 | Contract自体が存在しない (None) | BLOCK | DESIGNED | 不在はALLOWではない |
| B07 | 構造化されていない自然言語 | BLOCK | DESIGNED | ProseはContractではない |
| B08 | admissibility_state = UNKNOWN | BLOCK または UNKNOWN | DESIGNED | ALLOWは禁止 |
| B09 | re_verdict = BLOCK、binding_status = BOUND | BLOCK | DERIVED | bound denialは尊重される |
| B10 | re_verdict = BLOCK、binding_status = MISSING | BLOCK | DERIVED | **中核**。停止理由がbinding欠落であること |

### 3.1 B10の追加検証

B10は"BLOCKになったこと"では不十分である。
"binding欠落を理由にBLOCKになったこと"を確認する必要がある。

検証方法 (`test_b10_blocks_on_binding_not_on_verdict`):
verdictを `BLOCK` から `ALLOW` へ反転させても、決定がBLOCKのままであり、
Primitiveが `CONTRACT_INVALID` (field=binding_status) のまま変化しないことを確認する。
verdictを読んで判定していれば、この反転で結果は変わる。

---

## 4. Trial-Extended Suite (E00-E10, E2E)

| Test ID | 入力 | 期待 | Evidence | 主眼 |
| ------- | ---- | ---- | -------- | ---- |
| E00 | 完全に妥当な拡張Contract (署名再計算済み、nonce新規) | ALLOW | DESIGNED | 統制 |
| E01 | RE = Block、Contract不在 | BLOCK | DERIVED | REの否認がContract外にしか無い |
| E02 | RE = Allow、authority_state = LOST | BLOCK | DERIVED | 許可的verdictは救済しない |
| E03 | re_verdict = BLOCK、admissibility_state 欠落、Prose中に FORCED_INADMISSIBLE | BLOCK または UNKNOWN | DERIVED | 文字列走査でPrimitiveを生成しない |
| E04 | Prose中に CRYPTOGRAPHICALLY_SIGNED_DENY_STATE、signatureフィールド不在 | BLOCK | DERIVED | 署名されているという主張は署名ではない |
| E05 | 妥当だが期限切れ | BLOCK | DESIGNED | 時間境界 |
| E06 | 妥当だがnonce再利用 | BLOCK | DESIGNED | Replay境界 |
| E07 | スキーマ妥当、実行contextのrequest_idと不一致 | BLOCK | DESIGNED | 文脈束縛 |
| E08 | re_verdicts に ALLOW と BLOCK が併存 | BLOCK | DESIGNED | RE競合 |
| E09 | 構文的には妥当、意味的に不完全 | BLOCK または UNKNOWN | DESIGNED | ALLOW禁止 |
| E10 | CR語彙に無いPrimitive名を宣言 | BLOCK または UNKNOWN | DERIVED | 未マップは黙って通さない |
| E2E-BOUNDARY-01 | Contractは存在するが必須Primitiveフィールドが全欠落。REの否認はProseのみ | BLOCK または UNKNOWN | DERIVED | **本Trialの中心試験**。ALLOW禁止 |

---

## 5. Observed Test 50 Boundary 再試験 (指示書 第16節)

過去のTest 50をそのまま再現するのではない。
報告された意味論的境界と同じ入力を新規に構成し、Basic版とExtended版の双方へ与える。

| Test ID | Runtime | 入力 | 期待 |
| ------- | ------- | ---- | ---- |
| T50-BASIC | Trial-Basic | 同一入力 | BLOCK または UNKNOWN (ALLOW禁止) |
| T50-EXTENDED | Trial-Extended | 同一入力 | BLOCK または UNKNOWN (ALLOW禁止) |

入力の構成。

```text
contract_id      : C-T50            (metadata。存在する)
schema_version   : "1.0"
request_id       : R-T50
issued_at        : 2026-08-28T11:30:00Z
expires_at       : 2026-08-28T13:00:00Z
re_verdict_text  : "Block. Deny state asserted."      <- Prose。typedフィールドではない
operator_note    : "FORCED_INADMISSIBLE / CRYPTOGRAPHICALLY_SIGNED_DENY_STATE"
                                                       <- Prose。typedフィールドではない
(decision-bearingフィールドは1つも存在しない)
```

報告された旧観測 (`OBSERVED`、ただし本セッションでは一次資料未確認。
分類根拠は Evidence Boundary 文書を参照):

```text
RE       = Block (自然言語出力)
CR       = Allow
Binding  = absent
Execution= CONTINUE
```

本試験の目的は過去結果の改竄ではない。
`MoCKA Trial Runtimeが、観測されたBinding Gapを構造的に防止できるか` の確認である。

---

## 6. 構造不変条件 (指示書 第21節)

Case形式ではなく、性質として機械検証する。

| 原則 | 検証 |
| ---- | ---- |
| Prose is not a Primitive. | Prose有無・内容を変えても決定とPrimitive集合が不変 (Basic/Extended各5パターン)。Prose中にPrimitive名を書いてもFindingは0件 |
| A label is not a binding. | binding_status が BOUND 以外 (MISSING/INVALID/UNMAPPED/欠落) の4通りで、Basic/Extendedとも決してALLOWにならない |
| A verdict is not an execution authority. | bound verdictの下限演算を9通りの (decision, verdict) 組で検証。ALLOWへ引き上げる組合せが存在しないこと |
| A missing contract is not an Allow. | 非Contract入力7種 (None, "", 文字列, bytes, int, list, object) がBasic/Extendedとも常にBLOCK |
| Unknown is not Allow. | Gatewayが UNKNOWN / 未知オブジェクト / 素の文字列を常にSTOPへ写像すること |
| Observed behavior is not proof of implementation. | 文書側の制約。試験では検証しない (試験対象が存在しないため) |

追加の網羅試験: Basic Contractの12フィールドを1つずつ欠落させ、
12通りすべてがALLOWへ到達しないことを確認する。

---

## 7. 合否判定

- Case: 実際の決定が期待集合に含まれれば PASS
- 統制Case (B01, E00) 以外がEXECUTEへ到達した場合、その時点で試験は失敗とみなす
- 不変条件: 1件でも破れれば失敗

---

## 8. 本仕様が試験しないこと (UNKNOWN として明示)

- 既存 `Constitutional Runtime v1.0-stubs` の内部挙動
- 既存ハーネスの表示内容と一致するか
- 旧50試験の各テストの入力・期待値・実測値との一致
- 旧試験のMATCH/GAP判定と本Trialの判定の対応関係

これらは一次資料が未入手であるため試験不能である。
本Trialは旧試験の再現試験ではない。
