# MoCKA Constitutional Runtime v1.0-stubs Trial-Basic

Status: EXPERIMENTAL / ISOLATED / NON-CANONICAL
Date: 2026-08-28
作成: くろこ (Claude Code)
指示: きむら博士 - MoCKA Constitutional Runtime v1.0-stubs Trial Design (Basic / Extended Dual Trial Specification)
実装: `experiments/constitutional_runtime_trial/runtime_basic.py`
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 位置づけ (No Overclaim)

本文書が定義するのは、MoCKAが新規に設計する独立したTrial Runtimeである。

本Trialは以下を **主張しない**。

- 既存CRのソースを回収した
- 既存CRを復元した / 再現した
- 既存 v1.0-stubs の内部構造が判明した
- Test 50で使用されたPrimitiveを復元した

既存の `Constitutional Runtime v1.0-stubs` の内部実装は `NOT OBSERVED` である
(根拠: `docs/audits/CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md`)。
本文書で確定するのは、本Trialの内部仕様のみであり、その分類は `DESIGNED` である。

使用する自己記述は次の範囲に限る。

- MoCKA Trial Implementation
- MoCKA Constitutional Runtime v1.0-stubs Trial
- Behavior-informed design
- Evidence-bound reconstruction-independent implementation
- New implementation based on observed test boundaries

---

## 1. 目的

CRは何を受け取り、何を判定し、どの条件で実行を止めるのか。
これを最小限の決定論的構造として検証可能にする。

Trial-Basicは基礎 (Foundation) であり、境界攻撃 (Boundary Stress) はTrial-Extendedが担う。

---

## 2. 境界モデル

REの出力をCRの入力に直結させない。両者の間に必ずTyped Verification Contractを置く。

```text
Reasoning Engine (RE)
  |
  |  自然言語 / 非構造化出力。ここまではProse。
  v
Verification Contract           <- typed intake (schema / enum / timestamp)
  |
  |  ここを通過した値だけがPrimitive評価の対象になる
  v
Constitutional Runtime (CR)
  |
  v
Primitive Evaluation
  |
  v
Decision  ALLOW / BLOCK / UNKNOWN
  |
  v
Execution Gateway   ALLOW -> EXECUTE,  BLOCK -> STOP,  UNKNOWN -> STOP
```

禁止される経路 (実装上、到達不能にしてある)。

```text
RE says Block
   |
   v
CR blocks directly        <- 禁止。Contractを経由しない判定は存在しない
```

自然言語 / 非構造化データ / RE Verdict / Verification Contract / Primitive /
Execution Decision の6者を、実装上も別の型として分離する。

---

## 3. Basic Input Contract

実装: `experiments/constitutional_runtime_trial/contract.py`

12フィールド。すべて必須。1つでも欠落・null・型不一致があればintakeは失敗する。

| Field | 種別 | 型 / 語彙 | Evidence |
| ----- | ---- | --------- | -------- |
| contract_id | metadata | str | DESIGNED |
| schema_version | metadata | str, サポート値 "1.0" のみ | DESIGNED |
| request_id | metadata | str | DESIGNED |
| issued_at | metadata | ISO-8601 timestamp | DESIGNED |
| expires_at | metadata | ISO-8601 timestamp | DESIGNED |
| re_verdict | decision-bearing | ALLOW / BLOCK / UNKNOWN | DESIGNED |
| authority_state | decision-bearing | VALID / LOST / REVOKED / MISMATCH | DESIGNED |
| admissibility_state | decision-bearing | ADMISSIBLE / INADMISSIBLE / UNKNOWN | DESIGNED |
| witness_present | decision-bearing | bool | DESIGNED |
| witness_status | decision-bearing | VALID / INVALID / ABSENT / CONFLICT | DESIGNED |
| integrity_status | decision-bearing | VERIFIED / FAILED / SIGNATURE_MISSING / DIGEST_MISMATCH | DESIGNED |
| binding_status | decision-bearing | BOUND / MISSING / INVALID / UNMAPPED | DESIGNED |

これらを既存CRが保持していたとは主張しない。MoCKA Trial Runtimeとしての新規定義である。

### 3.1 Prose Quarantine

スキーマに無いキーは `prose` 隔離領域へ移される。

- 評価器は隔離領域を一切読まない
- `contract.get(field)` はスキーマ外フィールドに対して `KeyError` を送出する
- 監査用に `prose_keys()` でキー名のみ取得できる。値は取得しない

これが `Prose is not a Primitive.` の実装形である。

---

## 4. Basic Primitive Set

6語彙のみ。実装: `experiments/constitutional_runtime_trial/primitives.py`

| Primitive | Severity | 意味 |
| --------- | -------- | ---- |
| CONTRACT_INVALID | BLOCKING | Contractがtyped intakeを通過しない |
| AUTHORITY_LOST | BLOCKING | authority_stateがVALIDでない |
| INADMISSIBLE | BLOCKING | admissible = false |
| EXPIRED | BLOCKING | 有効期限切れ |
| INTEGRITY_FAILURE | BLOCKING | integrity_statusがVERIFIEDでない |
| UNKNOWN | INDETERMINATE | 判定不能。ALLOWへ変換されない |

### 4.1 不採用語彙 (重要)

| 観測報告された表記 | 本Trialでの扱い |
| ------------------ | --------------- |
| `ADMISSIBLE (Fail)` | Primitive名として採用しない。正式には `INADMISSIBLE` / `admissible = false` |
| `PASS (Unmapped)` | Primitive名として採用しない。Extendedの `BINDING_UNMAPPED` が対応し、常にUNKNOWNへ解決する |

これらは `Observed / normalized label` として扱い、既存CRの内部Primitive名だったとは断定しない。
テスト `test_admissible_fail_is_not_a_primitive_name` が、この2語彙が語彙表に不在であることを機械的に保証する。

---

## 5. Decision Rule Chain

短絡評価 (short-circuit)。最初に発火した規則が決定する。監査記録は1決定=1 Primitiveとなる。

| # | 条件 | Primitive | Decision |
| - | ---- | --------- | -------- |
| 1 | typed intakeに1件以上のdefect | CONTRACT_INVALID | BLOCK |
| 2 | authority_state != VALID | AUTHORITY_LOST | BLOCK |
| 3 | admissibility_state == INADMISSIBLE | INADMISSIBLE | BLOCK |
| 4 | expires_at <= now | EXPIRED | BLOCK |
| 5 | integrity_status != VERIFIED | INTEGRITY_FAILURE | BLOCK |
| 6 | binding_status != BOUND | CONTRACT_INVALID | BLOCK |
| 7 | witness必須かつ不在/無効 | policy=UNKNOWN: UNKNOWN / policy=BLOCK: CONTRACT_INVALID | UNKNOWN or BLOCK |
| 8 | admissibility_state == UNKNOWN | UNKNOWN | UNKNOWN |
| 9 | 上記いずれも非該当 | (なし) | bound verdictを適用 |

規則6は指示書 第7節の規則列に対する **DESIGNED追加** である。
未binding のverdictが判定へ到達しないために必要であり、B10の中核となる。

### 5.1 Bound Verdict Rule

規則9で、Contractが `binding_status = BOUND` を宣言している場合に限り、
`re_verdict` はTyped入力として扱われる。その効果は次の束 (lattice) の下限演算に限定される。

```text
BLOCK  <  UNKNOWN  <  ALLOW
```

- bound verdict = BLOCK   -> 決定を BLOCK へ引き下げる (否認は尊重する)
- bound verdict = UNKNOWN -> 決定を UNKNOWN へ引き下げる
- bound verdict = ALLOW   -> 何も引き上げない

すなわち、verdictは許可を **与えない**。拒否のみを伝えられる。
これが `A verdict is not an execution authority.` の実装形である。

未binding の場合、verdictはCRにとって単なるProseであり、規則6で既に停止している。

---

## 6. Fail-Closed Rule

以下のいずれかに該当する場合、`ALLOW` へフォールバックしてはならない。Basicでは原則 `BLOCK` とする。

- Verification Contractそのものが存在しない (`None`)
- Contractを構造化して受領できない (str / bytes / その他非mapping)
- 必須フィールドが欠落している
- 型検証・enum検証・timestamp検証に失敗した

この仕様は"既存CRがFail-Closedだった"という意味ではない。
MoCKA Trial Runtimeとして新たに採用する設計判断 (`DESIGNED`) である。

機械的保証: `test_every_single_field_omission_fails_closed` が12フィールドを1つずつ
欠落させ、いずれもALLOWへ到達しないことを確認する。

---

## 7. Basic固有の設計判断 (すべてDESIGNED / 開示済み)

| # | 判断 | 理由 |
| - | ---- | ---- |
| 1 | 短絡評価 | 監査記録を1決定1 Primitiveに保つ。Extendedは全件収集で対照をなす |
| 2 | 語彙の畳み込み: authority_state の LOST/REVOKED/MISMATCH を AUTHORITY_LOST に集約 | Basicは6語彙を維持する。分割はExtendedの役割 |
| 3 | 語彙の畳み込み: binding_status の MISSING/INVALID/UNMAPPED を CONTRACT_INVALID に集約 | 同上。情報は失われるが、意図的な単純化である |
| 4 | witness規則は明示policy。既定は UNKNOWN | Basicは固有のEvidence系Primitiveを持たないため。UNKNOWNもGatewayでSTOPとなり、fail-closedは保たれる |
| 5 | bound verdictは下限演算のみ | 許可の付与をverdictから構造的に切り離すため |
| 6 | Gatewayでの `isinstance(decision, Decision)` 検査 | 実装中に検出した実欠陥への対処。詳細はRESULTS文書 |

---

## 8. 実装対応表

| 構成要素 | ファイル |
| -------- | -------- |
| Primitive語彙 / Severity / decide() | `experiments/constitutional_runtime_trial/primitives.py` |
| Typed intake / Prose quarantine | `experiments/constitutional_runtime_trial/contract.py` |
| Trial-Basic 規則列 | `experiments/constitutional_runtime_trial/runtime_basic.py` |
| Execution Gateway / bound verdict lattice | `experiments/constitutional_runtime_trial/gateway.py` |
| 監査レコード | `experiments/constitutional_runtime_trial/audit.py` |

---

## 9. 非目標 / 制約

- 本Trialは既存MoCKA本番Runtimeへ接続しない。標準ライブラリのみを使用する
- events.db / Decision Ledger / Human Gate / Event Store へ一切書き込まない
- 本番導入は別Decisionとする。本文書はその判断材料ではあるが、判断そのものではない
- 本文書はNON-CANONICALであり、正本化・承認処理は行っていない
