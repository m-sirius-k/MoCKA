# Trial-Extended v2 - Design Review v0.1

Status: DESIGN REVIEW ONLY / NOT IMPLEMENTED / NON-CANONICAL
Date: 2026-08-28
実施: くろこ (Claude Code)
指示: きむら博士 - Phase 3: Evidence Lock and Extended-v2 Design Review
Branch: claude/constitutional-runtime-investigation-jgqkv1
基準commit: 085a5d2
前提文書: `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_EVIDENCE_LOCK_v0.1.md`

**実装は行っていない。** v2実装 / v1修正 / Test追加 / Primitive追加 /
Schema変更 / Decision変更 / Gateway変更 のいずれも行っていない。

---

## 0. 本レビューの立場

v2 は `より強い実装` を目指さない。目指すのは `より強く証拠化できるRuntime` である。

したがって本レビューの中心的な問いは次の1つである。

```text
何を検証すれば、Runtime が本当に
"判断を実行制御へ結び付ける装置" と言えるのか。
```

Original CR の再現 / 実環境の安全性 / 暗号学的安全性 / HSM・署名基盤の実装 /
RE の意味論的正しさ / Human Authority の代替 は、いずれも主張しない。

---

## 1. v1 Trial の到達点

### 1.1 実測で確定している性質

| # | 性質 | 実測 |
| - | ---- | ---- |
| 1 | ALLOW到達の希少性 | 全数探索40,000件 (Basic 30,000 / Extended 10,000) でALLOW到達は各Runtime1組合せのみ |
| 2 | Unknown Preservation | 同探索で UNKNOWN -> EXECUTE は 0件 |
| 3 | 型境界 | Gateway は plain str / str サブクラス / 別のstr Enum を拒否。`Decision` はEnumのため継承不能 |
| 4 | Prose非Primitive化 | Prose有無・内容を変えても決定とPrimitive集合は不変 (10パターン)。Prose中にPrimitive名を書いてもFinding 0件 |
| 5 | Binding必須性 | binding不成立時にALLOWへ到達しない (8パターン) |
| 6 | 停止理由の特定 | B10はverdictではなくbinding欠落で停止 (verdict 3値で不変) |
| 7 | 語彙近似値の拒否 | 語彙に近い綴りの値は `CONTRACT_SCHEMA_MISMATCH` でBLOCK (4パターン) |
| 8 | 未知フィールドの隔離 | typed名に酷似した未知フィールドは隔離され決定に影響しない (4パターン) |

### 1.2 到達していない領域

| # | 領域 | 状態 |
| - | ---- | ---- |
| 1 | 語彙カバレッジ | 31語彙中10語彙が未励起 (`Implemented / Not Exercised`) |
| 2 | 停止理由の検証 | 24Case中、励起Primitiveを検証しているのはB10の1件のみ |
| 3 | 例外境界 | Fail-Loud であり Fail-Closed ではない |
| 4 | 状態汚染 | rejected-but-parsable な Contract が nonce / high-water を汚染する |
| 5 | Policy層 | Basic は `decide()` を経由しない (Extendedのみ3段分離) |
| 6 | 系列 | 複数Contractの系列を性質として検証する形式が無い |

### 1.3 v1 の総括

```text
v1 が示したこと : "ALLOWにならないこと" は極めて強く示された。
v1 が示せていないこと : "正しい理由で止まったこと" はほとんど示されていない。
```

この非対称が v2 の出発点である。

---

## 2. Audit Findings (Phase 3 再実測後)

| ID | 内容 | Phase 3 での変化 |
| -- | ---- | ---------------- |
| F-01 | 完全に妥当でBOUNDなContractではDecisionがverdictに依存する。`ALLOW->ALLOW` / `BLOCK->BLOCK` / `UNKNOWN->UNKNOWN` を確認 | 再実測で確認。Basic / Extended とも同一挙動。**Trialの性質であり Original CR への主張ではない** |
| F-03 | `CONTRACT_SEMANTICALLY_INCOMPLETE` (trial-added) がE09のDecisionに決定的影響 | 再実測で確認。反転するのは E09 のみ。他3件は不変 |
| F-04 | Extendedのwitness検査のwhitelist / blacklist差異 | **記述を精密化**。既知3値には Extended の方が強い (BLOCK vs UNKNOWN)。弱いのは形式と"不在"時のみ |
| F-05 | nonce不在と `NONCE_REUSED` | 再実測で確認。異なる2事実に同一Primitive名。**意味論的に妥当でない** |
| F-07 | 未検証field型による TypeError | 再実測で確認。Fail-Closed ではなく **Fail-Loud** |
| F-08 | rejected Contract が nonce / high-water を汚染 | 再実測で確認。**新事実**: malformed (intake失敗) は汚染しない。汚染するのは rejected-but-parsable のみ |
| F-09 | Basic は Detection -> Policy -> Decision が完全分離していない | 再実測で確認。`decide()` 呼出 Basic 0回 / Extended 2回。Severityリテラル Basic 10箇所 / Extended 0箇所 |

詳細と実測値は Evidence Lock 文書 第5節にある。

---

## 3. 17候補の評価 (指示書 第8節・第12節)

### 3.1 採点軸の定義

指示書 第12節の7軸を、本レビューでは次の意味で用いる。**各0-5点。**

| 軸 | 定義 |
| -- | ---- |
| Evidence strength | その試験の結果が、主張したい性質をどれだけ直接裏付けるか。"止まったこと"しか示せないなら低く、"正しい理由で止まったこと"を示せるなら高い |
| Determinism | 時刻・順序・外部状態に依存せず、同じ入力が同じ結果を返すか |
| Boundary clarity | Existence / Validity / Authority のどれか1つに素直に対応するか |
| Failure containment | その候補が失敗したとき、修正が局所で済むか (設計全体の作り直しにならないか) |
| Authority preservation | Authority境界 (verdict != authority) を実際に押すか |
| Reproducibility | 第三者が同一環境で再実行できるか |
| Auditability | 生成される監査記録が、それ自体で読めるか |

**重要**: Evidence strength は **現行のCase形式のもとで** 採点する。
現行形式は決定値しか検証しないため、多くの候補がここで頭打ちになる。
`M-5後` 列は、Improvement Plan M-5 (`expected_primitives` の照合) 実施後の想定値である。

### 3.2 採点表

Ev = Evidence strength (現行) / Ev+ = M-5後の想定 / Det = Determinism /
Bnd = Boundary clarity / Cont = Failure containment / Auth = Authority preservation /
Rep = Reproducibility / Aud = Auditability

| # | 候補 | 軸 | Ev | Ev+ | Det | Bnd | Cont | Auth | Rep | Aud | 計 | 判定 |
| - | ---- | -- | -- | --- | --- | --- | ---- | ---- | --- | --- | -- | ---- |
| 1 | valid + modified verdict | Authority | 4 | 4 | 5 | 5 | 4 | 5 | 5 | 4 | 32 | 承認可 (重複大) |
| 2 | valid + modified nonce | Validity | **2** | 4 | 5 | 4 | 4 | 1 | 5 | 3 | 24 | 対象外 |
| 3 | valid + modified timestamp | Validity | **2** | 4 | 5 | 4 | 4 | 1 | 5 | 4 | 25 | 対象外 |
| 4 | valid + modified witness | Validity/Authority | **2** | 4 | 5 | 3 | 3 | 3 | 5 | 4 | 25 | 対象外 |
| 5 | valid + modified signature | Validity | 4 | 5 | 5 | 5 | 5 | 2 | 5 | 5 | 31 | **承認可** |
| 6 | schema-compatible semantic corruption | Validity | **1** | 2 | 4 | 2 | 2 | 2 | 4 | 2 | 17 | 対象外 |
| 7 | UNKNOWN disguised as ALLOW | Authority | 3 | 4 | 5 | 4 | 5 | 5 | 5 | 4 | 31 | **承認可** |
| 8 | stale valid Contract replay | Validity/Authority | **2** | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 22 | 対象外 |
| 9 | rejected Contract replay | Existence/Authority | **1** | 4 | 4 | 3 | 2 | 4 | 4 | 3 | 21 | 対象外 (方針未定) |
| 10 | contradictory verdict / primitive | Authority | 3 | 4 | 5 | 4 | 4 | 5 | 5 | 4 | 30 | **承認可** |
| 11 | duplicate Contract | Existence | **2** | 4 | 5 | 5 | 4 | 2 | 5 | 4 | 27 | 対象外 |
| 12 | valid -> malformed | Existence | 3 | 4 | 5 | 4 | 4 | 3 | 5 | 4 | 28 | **承認可** |
| 13 | malformed -> valid | Existence | 4 | 4 | 5 | 5 | 4 | 2 | 5 | 4 | 29 | **承認可** |
| 14 | unknown field injection | Existence/Validity | 3 | 4 | 5 | 4 | 4 | 3 | 5 | 4 | 28 | **承認可** |
| 15 | type-confusion attack | Validity | **1** | 4 | 5 | 4 | 2 | 2 | 5 | 2 | 21 | 対象外 (H-2が前提) |
| 16 | context substitution | Authority | 3 | 4 | 5 | 4 | 4 | 5 | 5 | 4 | 30 | **承認可** |
| 17 | cross-session Contract reuse | Authority | **1** | 1 | 3 | 3 | 2 | 4 | 3 | 2 | 18 | 対象外 (設計判断が先) |

太字の Ev は `Evidence strength < 3` に該当し、指示書 第12節の規則により
**重要候補であっても実装承認対象から外す**。

### 3.3 採点結果の集計

```text
承認可 (Ev >= 3) : 8件  #1 #5 #7 #10 #12 #13 #14 #16
対象外 (Ev <  3) : 9件  #2 #3 #4 #6 #8 #9 #11 #15 #17
```

### 3.4 最も重要な観察

対象外9件のうち、**候補それ自体の価値が低いのは #6 と #17 の2件のみ** である。
残る7件 (#2 #3 #4 #8 #9 #11 #15) は、候補の価値ではなく
**前提条件が未整備であるために Evidence strength が上がらない**。

| 前提 | それが解ける候補 | Ev の変化 |
| ---- | ---------------- | --------- |
| M-5 (`expected_primitives` の照合) | #2 #3 #4 #8 #11 | 2 -> 4 |
| M-2 (Reject -> State Mutation の制度方針確定) | #9 | 1 -> 4 |
| H-2 (型検証) | #15 | 1 -> 4 |
| session概念の設計判断 | #17 | 1 -> 1 (設計変更が要る) |

```text
すなわち v2 における最大の投資対象は、17候補そのものではなく
"停止理由を検証できる試験形式" (M-5) である。
これ1つで対象外9件のうち5件が承認可へ移る。
```

### 3.5 既存Trialとの重複

| 候補 | 重複対象 | 程度 |
| ---- | -------- | ---- |
| #1 | `test_bound_verdict_can_only_lower_a_decision` (9組) + Phase 3 F-01 再実測 | **大**。新規情報は少ない |
| #7 | Phase 3 C3 プローブ (語彙近似値4パターン) | 中。プローブは試験化されていない |
| #14 | Phase 3 C2 プローブ (lookalike 4パターン) + Prose不変性試験 | 中。同上 |
| #13 | Phase 3 C1 プローブ | 中。同上 |
| #16 | E07 (単純なcontext不一致) | 小。substitution は別 |
| #5 #10 #12 | なし | なし |

**#7 / #13 / #14 は Phase 3 のプローブで既に事実を確認済みだが、
プローブは scratchpad にあり試験として固定されていない。**
v2 の作業の一部は"既に測ったことを試験として固定する"ことである。

---

## 4. Existence / Validity / Authority の現状

### 4.1 v1 における3者の分離状況

```text
Existence : intake が None / str / 非mapping を弾く時点で分離済み
            -> CONTRACT_MISSING / CONTRACT_UNPARSABLE
            実測: malformed 入力は台帳を汚染せず、後続の妥当Contractは ALLOW

Validity  : 型・enum・timestamp・署名・digest の検証で分離済み
            -> CONTRACT_SCHEMA_MISMATCH / SIGNATURE_* / DIGEST_MISMATCH
            実測: 語彙近似値4パターンすべて CONTRACT_SCHEMA_MISMATCH で BLOCK

Authority : binding_status と bound verdict の下限演算で分離済み
            -> BINDING_* / verdict は決定を下げられるが上げられない
            実測: binding不成立時にALLOW到達なし (8パターン)
```

### 4.2 分離が最も弱い箇所

| 境界 | 弱さ | 根拠 |
| ---- | ---- | ---- |
| Existence / Validity の境界 | **rejected-but-parsable が Existence 側の副作用を持つ** | F-08。読めるが拒否された Contract が台帳を汚染する。malformed は汚染しない |
| Validity / Authority の境界 | witness が形式上 blacklist | F-04。既知3値には強いが、形式が閉じていない |
| Detection / Decision の境界 | Basic に Policy層が無い | F-09 |

---

## 5. v2 の優先順位

### 5.1 最小構成 (Minimum Viable v2)

3候補。Existence / Validity / Authority を1つずつ、いずれも Ev >= 4 または
Authority preservation 5 のものを選ぶ。

| 順 | 候補 | 軸 | 選定理由 |
| -- | ---- | -- | -------- |
| 1 | #5 valid + modified signature | Validity | 単一ビットの改変が ALLOW -> BLOCK を起こす。決定値だけで結論が出る唯一級の候補。Ev 4 / 計31 |
| 2 | #7 UNKNOWN disguised as ALLOW | Authority | Unknown Preservation の中核。Authority preservation 5。Ev 3 |
| 3 | #13 malformed -> valid | Existence | 汚染しないことを固定する。#9 (汚染する) との対比が Existence 境界を最も鋭く示す。Ev 4 |

この3件は **前提条件なしで今すぐ試験化できる**。

### 5.2 攻撃的構成 (Aggressive v2)

最小構成 + 承認可の残り5件。

```text
#10 contradictory verdict / primitive  (Authority preservation 5)
#16 context substitution               (Authority preservation 5)
#12 valid -> malformed                 (系列の前半)
#14 unknown field injection            (隔離の固定)
#1  valid + modified verdict           (重複大。最後に置く)
```

`#10` と `#16` は Authority preservation が最高点であり、
`判断を実行制御へ結び付ける装置` かどうかを最も直接に押す。
最小構成に次いで優先すべきはこの2件である。

### 5.3 前提条件を解いてから着手する群

| 前提 | 解けたら着手 | 備考 |
| ---- | ------------ | ---- |
| M-5 実施 | #2 #3 #4 #8 #11 | 5件が一度に承認可へ移る。**投資効率が最も高い** |
| M-2 方針確定 | #9 | 制度判断が先。くろこの判断事項ではない |
| H-2 実施 | #15 | 型検証がないと期待値が"TypeErrorが出ること"になる |
| session設計判断 | #17 | schema変更を伴う。今回の禁止事項に該当 |
| 意味論の定義 | #6 | "意味的に壊れている"の oracle が存在しない |

---

## 6. 各構成の試験可能性と期待される証拠

### 6.1 最小構成

| 候補 | 試験可能性 | 期待される証拠 |
| ---- | ---------- | -------------- |
| #5 | 高。署名を1文字変えるだけ。固定時刻・固定鍵で決定的 | 妥当Contractの ALLOW が、署名1文字の改変で BLOCK になる。Validity が Authority を与えないことの最短の証拠 |
| #7 | 高。intake の enum 検証が既に多くを弾くことは Phase 3 で確認済み | 語彙に似ているだけの値・binding の空宣言・digest不整合のいずれも ALLOW に到達しない。到達したものがあれば、それが最重要 Finding になる |
| #13 | 高。Phase 3 C1 で実測済み | malformed 入力の後でも、妥当Contractは ALLOW / EXECUTE に到達する。Existence の失敗が後続を汚染しないことの証拠 |

### 6.2 攻撃的構成の追加分

| 候補 | 試験可能性 | 期待される証拠 |
| ---- | ---------- | -------------- |
| #10 | 高。`re_verdict=ALLOW` と `declared_primitives` に遮断系Primitiveを同時指定 | verdict が ALLOW でも、宣言されたPrimitiveと矛盾すれば ALLOW にならない。verdict != authority の直接証拠 |
| #16 | 中。別の"妥当な"実行contextへの差し替え | Contract 単体が妥当でも、結び付く先が違えば authority は成立しない。Binding Integrity の証拠 |
| #12 | 高。系列2件 | 妥当Contractの ALLOW が、後続の malformed によって遡って変わらない。かつ malformed は ALLOW を継承しない |
| #14 | 高。Phase 3 C2 で4パターン実測済み | typed名に酷似した未知フィールドは決定に影響しない。Prose Quarantine の境界がフィールド名の類似で破れない証拠 |
| #1 | 高。既存試験と重複 | 追加の証拠は限定的。Ev は高いが新規性が低い |

### 6.3 期待される証拠の限界 (明示)

```text
これらの試験がすべて通っても言えないこと:

  - Trial が実環境で安全である
  - Trial が Binding Gap の全クラスを防止する
  - Original CR にも同じ経路が存在した
  - 暗号学的安全性が実証された
    (署名は Trial 専用 HMAC-SHA256 定数鍵。HSM・署名基盤は未実装)
  - RE の意味論的正しさが保証される
  - Human Authority を Runtime が代替できる
```

---

## 7. 未解決問題

| # | 問題 | 状態 |
| - | ---- | ---- |
| 1 | `Reject -> State Mutation` を制度的に許容するか | **未決定**。#9 の期待値が書けない。第8節の承認事項 |
| 2 | "意味的に壊れているが schema 適合"の定義 | 未定義。#6 の oracle が無い |
| 3 | Runtime に session 概念を導入するか | 未決定。#17 は schema 変更を伴う |
| 4 | 未励起10語彙が実条件で励起されるか | 未検証 (静的到達可能性は確認済み) |
| 5 | Basic に Policy層を導入するか (F-09) | 未決定。短絡評価という設計意図と衝突しうる |
| 6 | `NONCE_MISSING` 語彙を追加するか (F-05) | 未決定。trial-added が2件目になる |
| 7 | 例外を表す Primitive が必要か (F-07 / H-3) | 未決定。H-2 実施後に再判断が望ましい |

---

## 8. 実装承認条件

以下がすべて満たされたときのみ、v2 の実装へ進む。

### 8.1 必須条件

| # | 条件 | 現状 |
| - | ---- | ---- |
| 1 | きむら博士による本レビューの承認 | 未 |
| 2 | 最小構成3件 (#5 / #7 / #13) の範囲確定 | 未 |
| 3 | v2 が既存 v1 を変更しないことの確認 (新規ファイルのみ) | 設計方針として本レビューに記載 |
| 4 | 新規 Primitive を追加する場合、`origin = trial-added` として記録し反実仮想を測定・開示する手続きの確認 | 手続きは v2 Candidates 文書 第5節に確定済み |

### 8.2 候補別の追加条件

| 候補 | 追加条件 |
| ---- | -------- |
| #9 | 第7節-1 (Reject -> State Mutation の制度方針) の確定が先 |
| #15 | Improvement Plan H-2 (型検証) の実施が先 |
| #2 #3 #4 #8 #11 | Improvement Plan M-5 (`expected_primitives`) の実施が先 |
| #17 | session 概念の設計判断が先。schema 変更を伴う |
| #6 | "意味的破壊"の定義が先 |

### 8.3 承認しても実施しないもの

```text
本レビューの承認は、Improvement Plan の実装承認を含まない。
M-5 / M-2 / H-2 はそれぞれ別に承認を要する。
```

---

## 9. 本レビューが主張しないこと

- 本レビューは Original CR の設計レビューではない。対象は MoCKA Trial のみである
- 候補の必要性が Original CR に同種の弱点があったことを示すとは述べない
- 17候補すべてを実装する必要があるとは述べない
- 採点は本レビュー時点の判断であり、前提条件が変われば変わる
- 総合点だけで採否を決めていない。`Evidence strength < 3` の規則を優先している
