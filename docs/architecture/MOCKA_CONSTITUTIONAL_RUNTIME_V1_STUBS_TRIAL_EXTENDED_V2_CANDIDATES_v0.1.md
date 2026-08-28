# MoCKA Constitutional Runtime v1.0-stubs Trial-Extended v2 - Design Candidates v0.1

Status: CANDIDATE RECORD / NOT IMPLEMENTED / NON-CANONICAL
Date: 2026-08-28
作成: くろこ (Claude Code)
指示: きむら博士 - Evidence-Bound Consolidation and Trial Separation (作業順序 26, 第9節)
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 本文書の性質と目的

**今回の作業では実装しない。** 将来の Trial Extended v2 の候補を記録するのみである。

### 0.1 目的の限定 (重要)

本候補群の目的は **Primitive を増やすことではない**。
次の3つを分離して検証することである。

```text
Contract existence  !=  Contract validity  !=  Contract authority

    存在する            妥当である            権限を伴う

    Contractという      スキーマ・型・語彙    その Contract が
    オブジェクトが      が要求を満たす        実行を許可する
    渡された                                  根拠になりうる
```

現行の Trial-Extended は、この3者をある程度分離しているが、
分離が **試験によって固定されているか** は別問題である。
v2 候補は、3者の境界に負荷をかける入力の一覧である。

### 0.2 Non-Claims

- 本候補群は Original CR に対する試験ではない
- 本候補群の必要性が、Original CR に同種の弱点があったことを示すとは述べない
- 候補が全て実装されても、Binding Gap の全クラスを防止できるとは述べない

---

## 1. 候補一覧 (指示書 第9節の17項目)

`現行の到達度` 列の意味。

```text
未着手      : 対応する試験が存在しない
部分的      : 近い境界を触る既存Caseがあるが、この観点では試験していない
```

| # | 候補 | 分離対象 | 現行の到達度 | 備考 |
| - | ---- | -------- | ------------ | ---- |
| 1 | valid Contract + modified verdict | authority | **部分的** (B10反転検証、E08競合) | B10はbinding不成立時。妥当かつBOUNDな Contract の verdict 改変は未試験 |
| 2 | valid Contract + modified nonce | validity | **部分的** (E06 nonce再利用) | 再利用は試験済み。署名後の nonce 差し替え (署名不整合) は未試験 |
| 3 | valid Contract + modified timestamp | validity | **部分的** (E05 期限切れ) | 期限切れは試験済み。署名後の timestamp 改変は未試験 |
| 4 | valid Contract + modified witness | validity / authority | **未着手** | F-04 (witness検査がblacklist) と直結する |
| 5 | valid Contract + modified signature | validity | **未着手** | `SIGNATURE_INVALID` は未励起語彙10件の1つ |
| 6 | schema-compatible semantic corruption | validity | **部分的** (E09 意味的不完全) | 欠落は試験済み。型は合うが意味が破壊されている入力は未試験 |
| 7 | UNKNOWN disguised as ALLOW | authority | **未着手** | 最重要候補。下記 2.1 |
| 8 | stale valid Contract replay | validity / authority | **未着手** | `REQUEST_REPLAY` は未励起 |
| 9 | rejected Contract replay | existence / authority | **未着手** | F-08 (state contamination) と直結する |
| 10 | contradictory verdict / primitive | authority | **部分的** (E08 RE競合) | verdict間の矛盾は試験済み。verdict と primitive の矛盾は未試験 |
| 11 | duplicate Contract | existence | **未着手** | 同一 Contract の二重提示。`REQUEST_REPLAY` 経路 |
| 12 | valid Contract followed by malformed Contract | existence | **未着手** | 系列試験。状態汚染の有無 |
| 13 | malformed Contract followed by valid Contract | existence | **未着手** | 同上。F-08の逆向き |
| 14 | unknown field injection | existence / validity | **部分的** (Prose不変性試験) | Prose隔離は試験済み。typed名に酷似した未知フィールドは未試験 |
| 15 | type-confusion attack | validity | **部分的** (Gateway型厳格性13入力) | Gatewayは試験済み。Contract層の型混同は F-07 で未防御と判明 |
| 16 | context substitution | authority | **部分的** (E07 context不一致) | 単純な不一致は試験済み。文脈の入れ替え (別の妥当な文脈への差し替え) は未試験 |
| 17 | cross-session Contract reuse | authority | **未着手** | 現行Runtimeはセッション概念を持たない。設計課題を含む |

集計: 未着手 8件 / 部分的 9件。

---

## 2. 特に重要な候補

### 2.1 #7 UNKNOWN disguised as ALLOW

3つの分離すべてに関わる中心候補である。

```text
狙い : UNKNOWN 相当の状態を、ALLOW に見える形で提示したとき、
       Runtime が UNKNOWN として扱い続けるか。

想定入力の方向性:
  - admissibility_state を ALLOW 語彙に近い綴りで与える
  - binding_status = "BOUND" を宣言しつつ、binding の実体が無い
  - declared_primitives に既知語彙と1文字違いの名前を入れる
  - re_verdict = "ALLOW" と verdict_digest の不整合を組み合わせる

期待する性質:
  UNKNOWN は ALLOW へ変換されない。
  既知語彙に似ているだけの値は既知語彙として扱われない。
```

現行実装では intake の enum 検証がこれらの多くを弾く見込みだが、
**見込みであって検証結果ではない**。

### 2.2 #9 rejected Contract replay

監査 Finding F-08 と直結する。

```text
既に実測済みの事実 (監査 P6):
  拒否された Contract が nonce を消費し、
  後続の妥当な Contract が NONCE_REUSED で BLOCK される。

  拒否された未来日時 Contract が high-water を更新し、
  後続の妥当な Contract が NON_MONOTONIC_TIME で BLOCK される。
```

v2 ではこれを **試験として固定する** 必要がある。
ただし、その前に"拒否された Contract の nonce を消費すべきか"という
制度上の方針を確定すること (Improvement Plan M-2 参照)。
方針が決まらないうちに試験を書くと、期待値が決められない。

### 2.3 #15 type-confusion attack

Gateway層は検証済みだが、Contract層は未防御である。

```text
検証済み (監査 P1):
  Gateway は plain str / str サブクラス / 別のstr Enum を拒否する。

未防御 (監査 P6, F-07):
  Contract層で nonce / request_id / subject に unhashable な値を与えると
  TypeError が評価器から脱出する。
```

v2 の試験を書く前に Improvement Plan H-2 (型検証) を実施する方が合理的である。
現状のまま試験を書くと、期待値が"TypeError が送出されること"になってしまう。

### 2.4 #12 / #13 系列試験

現行の Case 形式は `prime` で先行 Contract を与えられるが、
系列そのものを検証対象にしていない。

```text
#12 valid -> malformed : 妥当な Contract の後に壊れた Contract を出しても、
                         先の決定は覆らない (過去の ALLOW は取り消されない)。
                         同時に、壊れた Contract は ALLOW を継承しない。

#13 malformed -> valid : 壊れた Contract の後でも、妥当な Contract は
                         正しく評価される (状態汚染が無い)。
```

#13 は F-08 の逆向きの性質であり、現状では **成立しない可能性が高い**
(拒否された Contract が台帳を汚染するため)。

---

## 3. 3分離への対応表

| 分離 | 問い | 対応候補 |
| ---- | ---- | -------- |
| **Contract existence** | Contract という物体が渡されたか | #9, #11, #12, #13, #14 |
| **Contract validity** | スキーマ・型・語彙・完全性の要求を満たすか | #2, #3, #5, #6, #8, #14, #15 |
| **Contract authority** | 実行を許可する根拠になりうるか | #1, #4, #7, #10, #16, #17 |

現行 Trial-Extended における3者の分離状況。

```text
existence : intake が None / str / 非mapping を弾く時点で分離済み
            -> CONTRACT_MISSING / CONTRACT_UNPARSABLE

validity  : 型・enum・timestamp・署名・digest の検証で分離済み
            -> CONTRACT_SCHEMA_MISMATCH / SIGNATURE_* / DIGEST_MISMATCH

authority : binding_status と bound verdict の下限演算で分離済み
            -> BINDING_* / 下限演算により verdict は許可を与えない
```

すなわち **設計上は3者が分離されている**。
v2 の目的は、この分離が入力の変異に対して安定かを確かめることである。

---

## 4. v2 を実装する場合の前提条件

以下を満たしてから着手することを推奨する。

| # | 前提 | 理由 |
| - | ---- | ---- |
| 1 | Improvement Plan H-2 (型検証) の実施 | #15 の期待値が決められない |
| 2 | Improvement Plan M-2 (state contamination) の方針確定 | #9 / #13 の期待値が決められない |
| 3 | Improvement Plan M-4 (未励起語彙の試験) の実施 | #5 / #8 が触る語彙が現在未励起であり、基礎の確認が先 |
| 4 | Improvement Plan M-5 (expected_primitives) の実施 | v2 は"止まったこと"ではなく"正しい理由で止まったこと"を見る必要がある |

**前提4が最も重要である。**
現行の Case 形式のまま v2 を書くと、17候補のほとんどが
"ALLOW にならないこと"しか検証しない試験になる。
それは既に全数グリッド 40,000件が示している性質であり、新しい情報が増えない。

---

## 5. 語彙追加についての方針

v2 の実装で新規 Primitive が必要になった場合。

```text
必須: origin = "trial-added" として実装内に記録する
必須: Evidence Boundary 文書と Consolidation 文書へ追記する
必須: 反実仮想 (その語彙を除いた場合に結果が変わるCase) を測定して開示する
禁止: Original CR に同じ Primitive が存在したという推論
禁止: 追加によって結論を強化すること
```

現行の trial-added 語彙は `CONTRACT_SEMANTICALLY_INCOMPLETE` の1件のみであり、
その反実仮想は測定・開示済みである (Consolidation 文書 G-3節)。
v2 でも同じ手続きを踏むこと。

---

## 6. 本文書の位置づけ

- 実装計画ではない。候補の記録である
- 優先順位は付けていない。前提条件 (第4節) が先である
- 17候補すべてを実装する必要があるとは述べない
- 実装の可否・範囲はきむら博士の判断による
