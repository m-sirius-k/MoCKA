# MoCKA Spec v1.0.2-rc

## 1. 概要

本バージョン（v1.0.2-rc）は、MoCKAにおける観測層（observer）の意味論修正を定義する差分仕様である。

本Specは以下の目的を持つ：

- 観測関数の不整合（idempotence表現の型破綻）の除去
- observerの意味論を「deterministic projection」に統一
- 実装層との整合性維持
- IR層の観測定義の安定化

本Specはv1.0 / v1.0.1を改変しない。差分拡張として扱う。

---

## 2. 対象範囲

対象：

- IR層 observer定義
- Spec層 第4部（観測関数の必須条件）
- registry記述（note層）

非対象：

- app.py（実装層）
- state / transition実装
- execution layer全般

---

## 3. 変更内容

### 3.1 削除（廃止）

以下のidempotence定義は削除する：

```
observer(S) = observer(observer(S))
```

理由：

- observer: S → O に対して O → S が未定義
- 型整合性が成立しない自己適用構造
- 実装・IRいずれにも存在しない非現実構造

---

### 3.2 新定義（採用）

observerは以下の性質を持つ：

```
observer: S → O
```

#### determinism（観測決定性）

```
∀S:
observer(S) = O
```

性質：

- 同一入力Sに対して常に同一出力Oを返す
- 非可逆（non-invertible）
- state transitionを生成しない
- pure projection（副作用なし）
- IR層における観測専用関数

---

## 4. IR層との関係

observerはIR層において以下の役割を持つ：

- 状態の生成は禁止
- 状態の変更は禁止
- 出力は観測結果のみに限定される
- 再入力ループ構造は存在しない

---

## 5. 実装整合性

対応する実装：

- decision_log_detail()
- _calc_todo_risk_score()

これらはすべて以下の性質を持つ：

- 単方向projection
- 入力 state → 出力 result
- 出力の再入力ループなし
- 副作用なし（read-only）

---

## 6. registry整合

MoCKA registry状態：

- v1.0     = structural base（不変）
- v1.0.1   = constraint refinement（不変）
- v1.0.2-rc = observer semantics correction

---

## 7. 非変更領域

以下は変更されない：

- v1.0 / v1.0.1本体
- app.py
- state / transition実装
- Phase C（Human Gate制御）

---

## 8. Phase状態

- Phase C：Human Gate待機中
- IR → Code 自動変換：禁止
- execution layer変更：禁止

---

## 9. 意味的確定

本Specによりobserverは以下に確定する：

- 観測 = 非生成的射影
- 観測 = 状態変換を持たない関数
- 観測 = deterministic mapping

---

## 10. 結論

MoCKAにおける観測層は以下に収束する：

- idempotence（自己適用構造）→ 廃止
- determinism（射影の一意性）→ 採用
- observer = S → O の純粋写像として固定
