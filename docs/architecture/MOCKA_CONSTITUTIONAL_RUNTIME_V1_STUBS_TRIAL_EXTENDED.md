# MoCKA Constitutional Runtime v1.0-stubs Trial-Extended

Status: EXPERIMENTAL / ISOLATED / NON-CANONICAL
Date: 2026-08-28
作成: くろこ (Claude Code)
実装: `experiments/constitutional_runtime_trial/runtime_extended.py`
前提文書: `docs/architecture/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_BASIC.md`
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 位置づけ (No Overclaim)

Trial-Basicと同一の境界を適用する。本文書もまた、既存CRの復元ではない。
既存 `Constitutional Runtime v1.0-stubs` の内部実装は `NOT OBSERVED` のままである。
ここで確定するのは本Trial-Extendedの内部仕様のみであり、分類は `DESIGNED` である。

---

## 1. 目的

Basicが"このContractは使用可能か"を問うのに対し、Extendedは
"このContractはどのように壊れるか、そして壊れ方のいずれかがALLOWへ到達しうるか"
を問う。

対象は、Verification Contractそのものの破損、時間、再利用、競合、文脈不一致、Unknown である。

---

## 2. Basicとの差分 (4点)

| # | 差分 | 内容 |
| - | ---- | ---- |
| 1 | 全件収集評価 | 短絡しない。全カテゴリを評価し、全Findingを記録してから1回だけ決定へ還元する。監査価値は失敗の全体像にある |
| 2 | 語彙の分割 | Basicが畳み込んだものを分離する (AUTHORITY_LOST / REVOKED / MISMATCH、BINDING_MISSING / INVALID / UNMAPPED、CONTRACT_MISSING / UNPARSABLE / SCHEMA_MISMATCH / VERSION_DRIFT) |
| 3 | Contract失敗の二段階化 | metadata欠落は CONTRACT_SCHEMA_MISMATCH (BLOCK)。decision-bearing欠落は CONTRACT_SEMANTICALLY_INCOMPLETE (UNKNOWN)。封筒が壊れているのと、封筒は正しいが中身が決定不能なのは別の欠陥である。そしてどちらもALLOWではない |
| 4 | 状態保持 | Replayと単調時刻の検査には記憶が要る。nonce台帳・request台帳・subject別high-water markを保持する |

---

## 3. Decision Model

内部Decision Stateは3値。

```text
ALLOW
BLOCK
UNKNOWN
```

Execution Gatewayでの写像。

```text
ALLOW   -> EXECUTE
BLOCK   -> STOP
UNKNOWN -> STOP
```

還元規則 (`primitives.decide`)。

```text
BLOCKINGのFindingが1件でもある        -> BLOCK
そうでなくINDETERMINATEが1件でもある  -> UNKNOWN
いずれも無い                          -> ALLOW
```

`UNKNOWN != ALLOW` は Severity を Boolean にしないことで構造的に保証する。
Gateway側の写像はさらに一方向であり、ALLOW以外は実行に到達しない。

---

## 4. Extended Primitive Categories

実装: `experiments/constitutional_runtime_trial/primitives.py`

| Category | Primitive | Severity | Origin |
| -------- | --------- | -------- | ------ |
| Contract | CONTRACT_MISSING | BLOCKING | instruction-listed |
| Contract | CONTRACT_INVALID | BLOCKING | instruction-listed |
| Contract | CONTRACT_UNPARSABLE | BLOCKING | instruction-listed |
| Contract | CONTRACT_SCHEMA_MISMATCH | BLOCKING | instruction-listed |
| Contract | CONTRACT_VERSION_DRIFT | BLOCKING | instruction-listed |
| Contract | CONTRACT_SEMANTICALLY_INCOMPLETE | INDETERMINATE | **trial-added** |
| Authority | AUTHORITY_LOST | BLOCKING | instruction-listed |
| Authority | AUTHORITY_REVOKED | BLOCKING | instruction-listed |
| Authority | AUTHORITY_MISMATCH | BLOCKING | instruction-listed |
| Admissibility | INADMISSIBLE | BLOCKING | instruction-listed |
| Admissibility | UNKNOWN | INDETERMINATE | instruction-listed |
| Temporal | EXPIRED | BLOCKING | instruction-listed |
| Temporal | NOT_YET_VALID | BLOCKING | instruction-listed |
| Temporal | TIMESTAMP_MISMATCH | BLOCKING | instruction-listed |
| Temporal | NON_MONOTONIC_TIME | BLOCKING | instruction-listed |
| Integrity | INTEGRITY_FAILURE | BLOCKING | instruction-listed (Basic継承) |
| Integrity | SIGNATURE_INVALID | BLOCKING | instruction-listed |
| Integrity | SIGNATURE_MISSING | BLOCKING | instruction-listed |
| Integrity | DIGEST_MISMATCH | BLOCKING | instruction-listed |
| Replay | NONCE_REUSED | BLOCKING | instruction-listed |
| Replay | REQUEST_REPLAY | BLOCKING | instruction-listed |
| Replay | CONTEXT_MISMATCH | BLOCKING | instruction-listed |
| Binding | BINDING_MISSING | BLOCKING | instruction-listed |
| Binding | BINDING_INVALID | BLOCKING | instruction-listed |
| Binding | BINDING_UNMAPPED | INDETERMINATE | instruction-listed |
| Evidence | WITNESS_MISSING | BLOCKING | instruction-listed |
| Evidence | WITNESS_INVALID | BLOCKING | instruction-listed |
| Evidence | WITNESS_CONFLICT | BLOCKING | instruction-listed |
| Governance | MULTIPLE_RE_CONFLICT | BLOCKING | instruction-listed |
| Governance | VERDICT_MISSING | BLOCKING | instruction-listed |
| Governance | VERDICT_MUTATED | BLOCKING | instruction-listed |

`origin` 列の意味。

- `instruction-listed`: 指示書 第6節 / 第12節に列挙された名称
- `trial-added`: 本Trialが列挙外に追加した語彙。1件のみであり、ここで開示する

追加した1件 `CONTRACT_SEMANTICALLY_INCOMPLETE` の理由は第2節の差分3である。
指示書 第14節 E09 の期待値 (`BLOCK or UNKNOWN`) を、BLOCKへ丸めずUNKNOWNとして
保持するために必要だった。

---

## 5. カテゴリ別の判定内容

### 5.1 Contract

intakeが返すtier中立のdefect codeを、Extended語彙へ写像する。

| defect code | Primitive |
| ----------- | --------- |
| MISSING | CONTRACT_MISSING |
| UNPARSABLE | CONTRACT_UNPARSABLE |
| UNSUPPORTED_SCHEMA_VERSION | CONTRACT_VERSION_DRIFT |
| MISSING_METADATA_FIELD | CONTRACT_SCHEMA_MISMATCH |
| BAD_TYPE / BAD_ENUM | CONTRACT_SCHEMA_MISMATCH |
| (decision-bearingフィールドの欠落) | CONTRACT_SEMANTICALLY_INCOMPLETE |

### 5.2 Authority

`authority_state` の LOST / REVOKED / MISMATCH をそれぞれ別Primitiveへ。
加えて `required_role` と `actor_role` が両方存在して不一致なら AUTHORITY_MISMATCH。
(観測報告にあった `GUEST_USER` / `SUPER_ADMIN` のrole mismatch形はこの経路で扱われる。
ただし、既存CRがこの経路を持っていたとは主張しない。)

### 5.3 Temporal

- `expires_at <= now` -> EXPIRED
- `not_before > now` -> NOT_YET_VALID
- `issued_at > expires_at` -> TIMESTAMP_MISMATCH
- subject別high-water markより `issued_at` が過去 -> NON_MONOTONIC_TIME

### 5.4 Integrity

署名は再計算する。主張は検証しない。

- `signature` フィールド不在 (policy: signature_required) -> SIGNATURE_MISSING
- `signature` 再計算不一致 -> SIGNATURE_INVALID
- `payload_digest` 再計算不一致 -> DIGEST_MISMATCH
- `integrity_status` の自己申告値も独立にPrimitive化する

署名鍵はTrial専用定数であり、本番鍵材料は使用しない。

### 5.5 Replay

- nonce不在 (policy: nonce_required) -> NONCE_REUSED (replayを排除できないため)
- nonce既出 -> NONCE_REUSED
- request_id既出 -> REQUEST_REPLAY
- 実行contextのrequest_idと不一致 -> CONTEXT_MISMATCH

### 5.6 Binding

- MISSING / INVALID -> BLOCKING
- UNMAPPED -> INDETERMINATE (UNKNOWNへ解決。passには決してならない)
- `declared_primitives` に語彙表未登録の名前 -> BINDING_UNMAPPED

CRが知らないPrimitive名は、黙って通さない。UNKNOWNとして停止する。

### 5.7 Evidence / Governance

- witness不在 / INVALID / CONFLICT / ABSENT を分離
- `re_verdicts` に相異なるverdictが2つ以上 -> MULTIPLE_RE_CONFLICT
- verdict不在 -> VERDICT_MISSING
- `verdict_digest` が `re_verdict` と不整合 -> VERDICT_MUTATED

---

## 6. Bound Verdict の扱い

Basicと同一の下限演算を用いる。ただしbindingの成立条件がより厳しい。

```text
bound_verdict が採用されるのは
    binding_status == "BOUND"
かつ
    Bindingカテゴリの Finding が0件
の場合のみ。それ以外では verdict は CR にとってProseである。
```

---

## 7. 文字列走査の禁止

本Runtimeのいずれのカテゴリも、Prose隔離領域を読まない。
Primitiveは1つとしてテキスト照合から生成されない。

機械的保証:

- `test_extended_decision_is_invariant_under_prose` - Prose有無で決定とPrimitive集合が不変
- `test_no_primitive_name_appears_in_prose_derived_findings` - Prose中に
  `AUTHORITY_LOST INADMISSIBLE EXPIRED` と書かれていても、Findingは0件でALLOWのまま

後者は重要である。Prose走査を実装していれば、この試験は必ず落ちる。

---

## 8. Comparison Matrix (指示書 第20節)

| Dimension | Basic | Extended | 本Trialでの実現 |
| --------- | ----- | -------- | --------------- |
| Contract validation | Yes | Yes | 両者とも同一のtyped intakeを共有。写像先語彙が異なる |
| Authority | Yes | Expanded | LOST集約 vs LOST/REVOKED/MISMATCH + role照合 |
| Admissibility | Yes | Expanded | 同語彙。ExtendedはUNKNOWNを他Findingと合成する |
| Time | Basic | Full | expiryのみ vs expiry/not_before/mismatch/monotonic |
| Integrity | Basic | Full | status読取のみ vs HMAC再計算 + digest再計算 |
| Replay | No/Basic | Yes | Basicは不対応 vs nonce/request/context |
| Context binding | Basic | Full | binding_statusのみ vs binding + 実行context照合 |
| Witness | Basic | Full | 明示policyで1判定 vs MISSING/INVALID/CONFLICT分離 |
| RE conflict | No | Yes | Basicは単一verdictのみ vs re_verdicts競合検知 |
| Unknown preservation | Yes | Yes | 両者ともUNKNOWNを保持しGatewayでSTOP |
| Fail-closed | Yes | Strict | Basicは原則BLOCK vs Extendedは欠落種別ごとにBLOCK/UNKNOWNへ分岐しつつ常にSTOP |
| Attack surface | Low | High | 10試験 vs 12試験 (E00統制含む) |
| Complexity | Low | High | 6 Primitive / 短絡 vs 31 Primitive / 全件収集 + 状態保持 |
| Trial purpose | Foundation | Boundary Stress | - |

---

## 9. 非目標 / 制約

Trial-Basic 第9節と同一。本番接続禁止、標準ライブラリのみ、本番ストアへの書込なし、
NON-CANONICAL。本番導入は別Decisionとする。
