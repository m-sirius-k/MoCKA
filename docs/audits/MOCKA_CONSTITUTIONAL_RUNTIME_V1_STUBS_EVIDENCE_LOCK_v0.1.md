# Constitutional Runtime v1.0-stubs - Evidence Lock v0.1

Status: EVIDENCE LOCK / NON-CANONICAL / READ-AUDIT-DESIGN-REVIEW ONLY
Date: 2026-08-28
実施: くろこ (Claude Code)
指示: きむら博士 - Phase 3: Evidence Lock and Extended-v2 Design Review
Branch: claude/constitutional-runtime-investigation-jgqkv1
基準commit: 085a5d2

本文書は既存ファイルを1つも変更していない。新規文書である。

---

## 0. 本文書の目的

`何が実証され、何が設計され、何がまだUNKNOWNなのか` を層ごとに固定する。

強いRuntimeを作ったと宣言することは目的ではない。

---

## 1. 状態確認 (指示書 第4節)

| 確認項目 | 結果 |
| -------- | ---- |
| branch | `claude/constitutional-runtime-investigation-jgqkv1` |
| 直近commit | `085a5d2` (指示書の指定と一致) |
| `git status` | clean (未追跡・変更とも0件) |
| `git diff` | 差分なし |
| `git diff HEAD` | 差分なし。作業ツリーは 085a5d2 と同一 |
| 117 tests 再実行 | **117 passed** |
| 24-case Trial 再実行 | **24 pass / 0 fail**。EXECUTE到達 2件 (B01, E00 = 統制Case) |
| `trial_results.json` 再生成 | バイト同一 (再実行後も `git status` に現れない) |
| 既存監査文書との整合性 | 齟齬1件を検出。F-04の記述精密化 (第5.4節) |

**変更は検出されなかった。** Trial Basic / Extended のコードは 085a5d2 時点のままである。

Trial 実装ファイルの現在状態 (sha256 先頭16桁)。

```text
primitives.py       199 lines  0350bb2a47c9b8a2
contract.py         252 lines  b56b67a026c2388a
gateway.py           69 lines  bfa0e11c5546435b
runtime_basic.py    278 lines  ec3a664812fe1ecc
runtime_extended.py 473 lines  bdaa488ed3fc4017
suites.py           408 lines  be832e691a04716a
audit.py            111 lines  02feb3946c934cdc
run_trial.py        115 lines  dbceb668eab0e97c
```

---

## 2. Evidence Layer (指示書 第5節)

| Layer | 対象 | 状態 | 補足 |
| ----- | ---- | ---- | ---- |
| **O** | Original CR v1.0-stubs | `NOT OBSERVED / UNKNOWN` | ソース・バイナリ・原ログ・Evidence Index・試験ページ本体のいずれも未回収 |
| **R** | 旧50試験の報告された結果 | `OBSERVED / PROVIDED` | **原ログ未回収**。提供された報告として存在する |
| **B** | MoCKA Trial Basic | `DESIGNED / IMPLEMENTED / TESTED` | Basic tier 6語彙はすべて試験中に励起される |
| **E** | MoCKA Trial Extended | `DESIGNED / IMPLEMENTED / PARTIALLY TESTED` | 31語彙中10語彙が未励起 (`Implemented / Not Exercised`) |
| **A** | Trial Design Audit | `OBSERVED WITHIN TRIAL` | **同一セッションによる自己監査であり、独立監査ではない** |

### 2.1 Layer間に存在しない関係

```text
O -> B  存在しない
O -> E  存在しない
```

Layer O から Layer B / E への導出は一度も行われていない。
Layer B / E の設計は、Layer R (報告された境界条件) を参照して行われたが、
Layer O の内部実装を推定して行われたものではない。

### 2.2 Layer A の限界

Layer A は Layer B / E のみを対象とする。Layer O について何も述べない。
自己監査であるため独立性がなく、監査プローブ自体に欠陥が1件あった実例がある
(Extended全数探索の初回版で署名再計算漏れ)。

---

## 3. Evidence Boundary Matrix (指示書 第6節)

列の意味。

```text
Claim                  : 主張または語彙
Evidence Layer         : どの層に属するか
Evidence Status        : OBSERVED / PROVIDED / DESIGNED / NOT OBSERVED / UNKNOWN
Direct Evidence        : 直接証拠の有無と内容
Interpretation Allowed : この証拠から許される解釈の上限
```

### 3.1 旧50試験 (Layer R) 由来の項目

| Claim | Evidence Layer | Evidence Status | Direct Evidence | Interpretation Allowed |
| ----- | -------------- | --------------- | --------------- | ---------------------- |
| RE Block | R | OBSERVED / PROVIDED | なし (原ログ未回収)。報告のみ | 試験条件下でREが否認側の出力を出したと報告されている、まで |
| CR Allow | R | OBSERVED / PROVIDED | なし。報告のみ | 同条件でCRがAllowを返したと報告されている、まで。原因は不明 |
| CR Block | R | OBSERVED / PROVIDED | なし。報告のみ (Test 01-20のMATCH群) | 一致した試験があったと報告されている、まで |
| PASS | R | UNKNOWN | なし | 表示ラベル。CRの内部状態と断定しない |
| PASS (Unmapped) | R | UNKNOWN | なし | **区分C (ハーネス表示) か区分E (CR評価) かを決定できない**。Original CRのPrimitiveと断定しない |
| AUTHORITY_LOST | R | UNKNOWN (label) | なし | `Observed / normalized label`。Original CR内部語彙と断定しない |
| ADMISSIBLE (Fail) | R | UNKNOWN (label) | なし | 同上。Trialでは**Primitive名として不採用** |
| Monotonic Time Check | R | UNKNOWN (label) | なし | 同上。Trialは名称を借用せず `NON_MONOTONIC_TIME` を別途定義 |
| FORCED_INADMISSIBLE | R (区分A prose) | OBSERVED / PROVIDED | プロンプト本文に存在したという報告 | **CRが受領・評価した値ではない**。区分AであってD/Eではない |
| CRYPTOGRAPHICALLY_SIGNED_DENY_STATE | R (区分A prose) | OBSERVED / PROVIDED | 同上 | 同上。実在する構造化Contractとして扱わない |

### 3.2 MoCKA Trial (Layer B / E) 由来の項目

| Claim | Evidence Layer | Evidence Status | Direct Evidence | Interpretation Allowed |
| ----- | -------------- | --------------- | --------------- | ---------------------- |
| CONTRACT_INVALID | B | DESIGNED / 実測あり | B06 / B07 / B10 で励起。全数グリッド30,000件 | **Trial内部の語彙**。Layer Oとは無関係 |
| BINDING_MISSING | E | DESIGNED / 実測あり | E2E-BOUNDARY-01 / T50-EXTENDED で励起 | 同上 |
| CONTRACT_SEMANTICALLY_INCOMPLETE | E | DESIGNED / **trial-added** / 実測あり | E03 / E09 / E2E / T50-EXTENDED で励起。反実仮想も測定済み | **本Trialが列挙外に追加した唯一の語彙**。Original CR由来ではない |
| Fail-Closed (Trial) | B, E | DESIGNED / 実測あり | 全数40,000件でALLOW到達は各Runtime1組合せのみ。UNKNOWN->EXECUTE 0件 | **Trialの性質**。Layer Oの Fail-Closed 有無は UNKNOWN |
| End-to-End Binding (Trial) | B, E | DESIGNED / 実測あり | binding不成立時にALLOWへ到達しない (8パターン) | Trialとして設計したBinding経路が存在し機能する、まで |

### 3.3 層をまたぐ項目 (最も混同しやすい)

| Claim | 分離の仕方 |
| ----- | ---------- |
| `AUTHORITY_LOST` | Layer R では **報告ラベル** (出所UNKNOWN)。Layer B/E では **Trialが定義したPrimitive** (実測あり)。**同じ文字列だが別物である** |
| `Fail-Closed` | Layer B/E では実測済みの性質。Layer O では **UNKNOWN**。"Trialが安全だからOriginal CRも安全"は成立しない |
| `End-to-End Binding` | Layer R では `not established in the observed test condition` まで。Layer B/E では設計した経路が実測で機能する。**この2つは別主張である** |

### 3.4 旧50試験由来の語彙とTrial設計語彙の分離 (指示書 第6節)

```text
Layer R 由来の語彙 (出所UNKNOWN、断定禁止):
    PASS / PASS (Unmapped) / AUTHORITY_LOST / ADMISSIBLE (Fail) /
    Monotonic Time Check / P-01 - P-10 / EV-TST-001 - EV-TST-050

Layer B/E で新規設計された語彙 (31件、実装内 origin フィールドで機械照合可能):
    origin = instruction-listed : 30件
        ("指示書に列挙されていた"のみを意味する。
         "Original CRの内部Primitive名だった"を意味しない)
    origin = trial-added        : 1件
        CONTRACT_SEMANTICALLY_INCOMPLETE

Trial が意図的に採用しなかった語彙 (テストで不在を保証):
    "ADMISSIBLE (Fail)" / "ADMISSIBLE_FAIL" / "PASS (Unmapped)"
```

`AUTHORITY_LOST` のように **両方の列に現れる文字列がある**。
これは名称の一致であって、実体の一致ではない。

---

## 4. Test 50 の A-D 分離 (指示書 第11節)

| 区分 | 内容 | 状態 |
| ---- | ---- | ---- |
| **A. Prompt prose** | `FORCED_INADMISSIBLE`、`CRYPTOGRAPHICALLY_SIGNED_DENY_STATE`、自然言語のDeny/Block勧告 | 報告として存在。原文は未入手 |
| **B. Harness structured state** | ハーネスが構造化して保持した値 | **観測されていない** |
| **C. CR actual input** | CRが実際に受領した入力 | **観測されていない**。Contract fields / Primitive fields とも UNKNOWN / empty |
| **D. CR Primitive Scan evaluated value** | CRが実際に評価した値 | `PASS / Unmapped` として報告された。ただし **これが区分Dなのか区分B (ハーネス表示) なのかを決定できない** |

### 4.1 結論の上限

C が観測されていないため、許される結論は次の1文までである。

```text
End-to-End Binding was not established in the observed test condition.
```

これを超える主張は行わない。特に以下は述べない。

- Original CR に binding機構が無かった
- Original CR が Prose を読んでいた / 読んでいなかった
- Original CR の Primitive Scan が `PASS (Unmapped)` という内部状態を持っていた
- Allow になった原因を特定できた

### 4.2 Trial 側の対応主張 (完全に別主張)

```text
Trial 側で言えること:
    Trial として設計した Binding 経路が実際に存在し、機能する。
    同一の意味論的境界を与えたとき、T50-BASIC / T50-EXTENDED とも STOP する。

Trial 側で言えないこと:
    Original CR にも同じ経路が存在した。
    Original CR が Allow になった原因が判明した。
```

この2つを混同しない。

---

## 5. Trial Audit Findings の再検証 (指示書 第7節)

Phase 3 で全項目を **再実測** した。以下は今回の実測値である。

### 5.1 F-01: verdict依存性

```text
完全に妥当で binding_status = BOUND の Contract:
    Basic    re_verdict=ALLOW   -> ALLOW   / EXECUTE
    Basic    re_verdict=BLOCK   -> BLOCK   / STOP
    Basic    re_verdict=UNKNOWN -> UNKNOWN / STOP
    Extended re_verdict=ALLOW   -> ALLOW   / EXECUTE
    Extended re_verdict=BLOCK   -> BLOCK   / STOP
    Extended re_verdict=UNKNOWN -> UNKNOWN / STOP

binding_status = MISSING の Contract (B10経路):
    re_verdict=BLOCK   -> BLOCK / CONTRACT_INVALID (field=binding_status)
    re_verdict=ALLOW   -> BLOCK / CONTRACT_INVALID (field=binding_status)
    re_verdict=UNKNOWN -> BLOCK / CONTRACT_INVALID (field=binding_status)
```

`ALLOW -> ALLOW` / `BLOCK -> BLOCK` / `UNKNOWN -> UNKNOWN` の関係を **確認した**。

これは **Trialの設計上の性質** であり、Original CR についての主張ではない。
旧記述 (`判定はverdictを読んでいない`) は誤りであり、正しくは次の2文に分離される。

```text
(1) 構造化され妥当で BOUND な Contract では、verdict は Decision の入力となる。
(2) 自然言語上のverdictが構造化ContractへbindingされなければCRには入力されない。
```

### 5.2 F-03: trial-added語彙の決定的影響

反実仮想 (`CONTRACT_SEMANTICALLY_INCOMPLETE` を除去して再計算)。

| Case | 実際 | 語彙除去時 | Execution |
| ---- | ---- | ---------- | --------- |
| E03 | BLOCK | BLOCK | STOP |
| **E09** | **UNKNOWN** | **ALLOW** | **EXECUTE** |
| E2E-BOUNDARY-01 | BLOCK | BLOCK | STOP |
| T50-EXTENDED | BLOCK | BLOCK | STOP |

指示書 第7節が求める4点。

| 問い | 回答 |
| ---- | ---- |
| なぜ追加されたか | 封筒が妥当で中身が決定不能な場合を、封筒の破損 (BLOCK) と区別してUNKNOWNとして保持するため。指示書 第14節 E09 の期待値 (`BLOCK or UNKNOWN`) をBLOCKへ丸めないために必要だった |
| どの試験で使用されるか | E03 / E09 / E2E-BOUNDARY-01 / T50-EXTENDED の4件で励起される |
| 除去した場合何が変化するか | **E09のみ** が UNKNOWN から ALLOW / EXECUTE へ反転する。他3件は変化しない |
| Original CR由来と誤認していないか | 誤認していない。実装内 `origin = "trial-added"` として保持され、Extended設計文書・Evidence Boundary文書・Consolidation文書のいずれにも明記されている |

**重要な非推論**: この Finding は、Original CR に同じPrimitiveが存在した
とも存在しなかったとも示さない。両者は無関係である。

### 5.3 F-04: witness検査 (前フェーズ記述の精密化)

Phase 3 の再実測により、前フェーズの記述
(`Extendedのwitness検査がBasicより弱い`) が **単純化しすぎであった** ことが判明した。

| witness_status | Basic | Extended | Extended の Evidence カテゴリ Finding |
| -------------- | ----- | -------- | ------------------------------------- |
| VALID | ALLOW | ALLOW | [] |
| INVALID | UNKNOWN | **BLOCK** | WITNESS_INVALID |
| ABSENT | UNKNOWN | **BLOCK** | WITNESS_MISSING |
| CONFLICT | UNKNOWN | **BLOCK** | WITNESS_CONFLICT |
| (フィールド不在) | **BLOCK** (CONTRACT_INVALID) | UNKNOWN | **[]** |

正確な記述は次のとおりである。

```text
決定の強さ : 既知の不良値 3種 (INVALID / ABSENT / CONFLICT) に対しては
             Extended の方が強い (BLOCK vs UNKNOWN)。

形式の強さ : Basic は whitelist (status == VALID を要求)。
             Extended は blacklist (既知3値を拒否)。形式は Extended が弱い。

現れる差   : witness_status が"不在"の場合のみ。
             このとき Extended の Evidence カテゴリは Finding を1件も出さず、
             停止は別カテゴリの trial-added 語彙が担っている。

実行可能な穴: 現時点では無い。現行語彙が閉じているため。
             ただし将来 witness_status に語彙を1つ追加すれば、
             Extended はそれを黙って受理する。
```

前フェーズの Finding 記述はこの精密化で置き換えられるべきである
(既存文書は No Change Rule により未修正。本節が正誤表として機能する)。

### 5.4 F-05: nonce不在と NONCE_REUSED

```text
nonce 不在  -> BLOCK / Replayカテゴリ Finding = ['NONCE_REUSED']
nonce 再利用 -> BLOCK / Replayカテゴリ Finding = ['NONCE_REUSED']
```

**意味論的に妥当ではない。** 異なる2つの事実に同一のPrimitive名が付く。

- 決定 (BLOCK) は両者とも正しい
- 記録は誤っている。nonce を一切持たない Contract の監査行が再送攻撃に見える

E2E-BOUNDARY-01 と T50-EXTENDED の監査行がこの誤記録を含んでいる。

### 5.5 F-07: 例外境界

```text
nonce      = ['a']    -> TypeError 送出。Decision は返らない
request_id = ['r']    -> TypeError 送出。Decision は返らない
subject    = {'s': 1} -> TypeError 送出。Decision は返らない
```

**例外境界は Fail-Closed になっていない。**
ただし Fail-Open でもない。Decision が返らないため ALLOW にもならない。
正確な分類は **Fail-Loud** である。

実行可否の判断は、仕様化されていない呼出側に委ねられている。
Execution Gateway の一方向性は"Decisionが返る場合に限り"保証される。

### 5.6 F-08: Reject -> State Mutation の順序

```text
拒否された Contract (AUTHORITY_LOST)          -> BLOCK
その後の完全に妥当な Contract (同一nonce)      -> BLOCK / NONCE_REUSED
その後の完全に妥当な Contract (より古い時刻)   -> BLOCK / NON_MONOTONIC_TIME
```

Phase 3 で新たに判明した区別 (重要)。

```text
malformed (intake失敗) な入力 -> BLOCK / CONTRACT_UNPARSABLE
                                 台帳は更新されない (contract=None で早期return)
                                 その後の妥当な Contract は ALLOW

rejected だが parsable な入力 -> BLOCK / AUTHORITY_LOST
                                 台帳は更新される (nonce / request / high-water)
                                 その後の妥当な Contract が巻き添えで BLOCK
```

すなわち **汚染は"壊れた入力"ではなく"読めるが拒否された入力"によって起きる**。

制度的な評価 (指示書 第7節が問う `Reject -> State Mutation` の許容性)。

| 立場 | 主張 | 評価 |
| ---- | ---- | ---- |
| 汚染を許容しない | 拒否された Contract は状態を変えるべきでない。台帳更新は決定確定後 | 可用性を守る。ただし拒否された Contract の nonce が再利用可能になる |
| 汚染を許容する | 一度提示された nonce は消費されるべき。再送そのものを抑止する | 再送耐性を守る。ただし拒否される Contract を投げるだけで正当な nonce 空間を汚染できる |

**現行実装は後者を選んでいるが、その選択は文書化されていない。**
どちらが制度上正しいかは、くろこが決める事項ではない。第8節の承認事項とする。

### 5.7 F-09: Detection -> Policy -> Decision の分離

```text
runtime_basic    : decide() 呼出 0回、Severity リテラル 10箇所
runtime_extended : decide() 呼出 2回、Severity リテラル  0箇所 (語彙表から導出)
```

| Runtime | 構造 |
| ------- | ---- |
| Extended | Detection (Finding生成) -> Policy (`decide()`) -> Decision -> Gateway。**3段分離が成立** |
| Basic | Detection (Finding生成) -> `_stop()` が直接 Decision を生成 -> Gateway。**Policy層が不在** |

Basic では検出箇所が決定箇所を兼ねている。
文書は両者を同一アーキテクチャとして提示しており、この差は記載されていない。

---

## 6. No-Claim List

以下は本作業群のどの文書でも主張していない。Phase 3 でも主張しない。

| # | 主張しないこと |
| - | -------------- |
| 1 | Original CR v1.0-stubs の内部実装を発見した |
| 2 | Trial Basic / Extended は Original CR の復元版である |
| 3 | 旧50試験の表中ラベルは Original CR の実Primitiveである |
| 4 | `PASS (Unmapped)` は Original CR が実際に生成したPrimitiveである |
| 5 | `AUTHORITY_LOST` / `ADMISSIBLE (Fail)` / `Monotonic Time Check` は Original CR 内部語彙である |
| 6 | Test 50 の `FORCED_INADMISSIBLE` / `CRYPTOGRAPHICALLY_SIGNED_DENY_STATE` は CR 実入力である |
| 7 | Trial の実装結果から Original CR の挙動を逆算できる |
| 8 | Trial が安全であるから Original CR も安全である |
| 9 | Original CR に Fail-Closed 機構が存在しなかった |
| 10 | Original CR に Fail-Closed 機構が存在した |
| 11 | Test 50 で Allow になった原因を特定した |
| 12 | Trial が実環境で安全である |
| 13 | 暗号学的安全性を実証した (署名はHMAC-SHA256のTrial専用鍵。HSM・署名基盤は未実装) |
| 14 | RE の意味論的正しさを保証する |
| 15 | Human Authority を Runtime が代替できる |
| 16 | Trial が Binding Gap の全クラスを防止する |

---

## 7. 現時点で確定できること

すべて Layer B / E / A に属する。Layer O については1件も無い。

| # | 確定事項 | 根拠 |
| - | -------- | ---- |
| 1 | Trial の全数探索40,000件 (Basic 30,000 / Extended 10,000) で、ALLOW到達は各Runtime 1組合せのみ | Phase 2 実測 |
| 2 | 同探索で UNKNOWN -> EXECUTE は 0件 | 同上 |
| 3 | Execution Gateway は型でないラベルで開かない (13入力で確認、`Decision` はEnumのため継承不能) | Phase 2 実測 |
| 4 | Prose の有無・内容を変えても決定とPrimitive集合は不変 (10パターン) | Phase 2 実測 |
| 5 | Prose中にPrimitive名を書いても Finding は 0件 | 同上 |
| 6 | binding不成立時に ALLOW へ到達しない (8パターン) | 同上 |
| 7 | B10 の停止理由は verdict ではなく binding 欠落 (verdict 3値で不変) | Phase 3 再実測 |
| 8 | 完全に妥当で BOUND な Contract では verdict が Decision の入力になる | Phase 3 実測 |
| 9 | trial-added 語彙の除去で反転するのは E09 のみ | Phase 3 再実測 |
| 10 | malformed 入力は台帳を汚染しないが、rejected-but-parsable 入力は汚染する | Phase 3 新規実測 |
| 11 | typed名に酷似した未知フィールドは隔離され、決定に影響しない (4パターン) | Phase 3 新規実測 |
| 12 | 語彙に近い綴りの値は `CONTRACT_SCHEMA_MISMATCH` で BLOCK される (4パターン) | Phase 3 新規実測 |
| 13 | Extended 31語彙中10語彙が未励起 (`Implemented / Not Exercised`) | Phase 2 動的計測 |
| 14 | 例外境界は Fail-Loud であり Fail-Closed ではない | Phase 3 再実測 |

---

## 8. 現時点で確定できないこと

| # | 未確定事項 | 分類 |
| - | ---------- | ---- |
| 1 | Original CR の内部構造・Primitive定義・Fail-Closed実装・Contract実装 | NOT OBSERVED / UNKNOWN |
| 2 | 旧50試験の原ログ・Evidence Index・試験ページ本体 | 未回収 |
| 3 | 各テストの入力・期待値・実測値 | UNKNOWN |
| 4 | `PASS (Unmapped)` が区分B (ハーネス) か区分D (CR評価) か | UNKNOWN |
| 5 | 旧50試験のラベルが原ログ由来か正規化か解釈か | UNKNOWN (4区分分離は完了できない) |
| 6 | Test 50 で Allow になった原因 | UNKNOWN |
| 7 | `Reject -> State Mutation` を制度的に許容するか | **未決定** (くろこの判断事項ではない。第5.6節) |
| 8 | 未励起10語彙が実際の条件で励起されるか | 未検証 (実装は静的に到達可能と確認済み) |
| 9 | Trial が未知の binding gap クラスに有効か | UNKNOWN |
| 10 | Trial の性質が実環境で保たれるか | UNKNOWN (Trialは隔離環境。本番非接続) |

---

## 9. GL7 記録の状態

`mocka_write_event` の実行結果は第13節の最終報告に記載する。
GL7 がblockされた場合、retryを過剰に行わず、bypassせず、
encoding mismatch を勝手に修正せず、失敗事実をそのまま報告する。

---

## 10. 関連文書

| 種別 | パス |
| ---- | ---- |
| Web観測調査 | `docs/audits/CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md` |
| Evidence境界 | `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_DESIGN_EVIDENCE_BOUNDARY.md` |
| 設計監査 | `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_DESIGN_AUDIT_v0.1.md` |
| Consolidation | `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_EVIDENCE_BOUND_CONSOLIDATION_v0.1.md` |
| Evidence Lock (本文書) | `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_EVIDENCE_LOCK_v0.1.md` |
| v2 設計レビュー | `docs/architecture/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_EXTENDED_V2_DESIGN_REVIEW_v0.1.md` |
