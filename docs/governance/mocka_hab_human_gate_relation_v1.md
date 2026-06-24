# MoCKA HAB x Human Gate Relation v1 (Integration)

Status: DRAFT(参照文書として追加。pre-authorization stateを解除しない)
Date: 2026-06-24
作成者: くろこ(博士) / 整理: Claude-sonnet-4-6

## 0. 本文書の位置づけ

本文書は
[mocka_hab_v1_contract.md](mocka_hab_v1_contract.md)と
[mocka_human_gate_decision_definition_v1.md](mocka_human_gate_decision_definition_v1.md)
の関係を定義する統合文書である。両文書の内容を変更せず、
両者の間の依存方向・遷移経路のみを確定する。

本文書追加によりpre-authorization state(FROZEN=不変/Extension=DRAFT/
Human Gate=未裁定/継続中)は解除されない。

## 1. 基本分離(絶対構造)

MoCKAにおけるHABとHuman Gateは、同じ領域を扱わない。

| 要素 | 役割 | 性質 |
|---|---|---|
| HAB | 状態定義 | 静的(what is) |
| Human Gate | 裁定補助 | 動的評価(should it move) |

- HABは「現状の記述」である。
- Human Gateは「変化の評価」である。

## 2. 関係の本質(非対称依存)

関係は一方向依存である。

```
HAB -> Human Gate
```

HABはHuman Gateの入力になるが、Human GateはHABを変更しない。

- HAB = 材料(state snapshot)
- Human Gate = 判定装置(evaluation filter)

## 3. 遷移パス(重要)

状態変化は必ず以下の経路を取る。

```
HAB(DRAFT / STABLE / FROZEN)
        |
        v
Human Gate Core(評価)
        |
        v
Human Gate Finalization(博士裁定)
        |
        v
HAB状態更新(必要時のみ)
```

Human Gate Core/Finalizationの定義は
[mocka_human_gate_decision_definition_v1.md](mocka_human_gate_decision_definition_v1.md)
に従う。本文書はこの2層分離を前提とし、それを変更しない。

## 4. 禁止構造(今回の核心)

以下を禁止する。

- **直接遷移**: HAB -> ACTIVE(Human Gateを経由しない遷移)
- **自動裁定ループ**: Human Gate Core -> 自動APPROVE確定
- **HABの意思化**: HABが「判断主体」になる構造

## 5. 安全構造

本統合により以下が保証される。

1. **人間裁定の唯一性**: Finalizationは必ず博士本人が行う。
2. **自動評価の限定性**: Coreは「判断材料生成」のみを行う。
3. **状態の非自律性**: HABは一切の意思を持たない(状態記述のみ)。

## 6. MoCKA全体での位置

```
[HAB] -> 状態記述層
   |
   v
[Human Gate Core] -> 評価層
   |
   v
[Human Gate Final] -> 博士裁定点
   |
   v
[Phase / Extension] -> 実行・遷移層
```

## 7. 設計上の意味

この構造の意味は1つに収束する。

「評価は機械化できるが、遷移は人間にしか起こせない」

## 8. 現在の運用状態(2026-06-24時点、本文書の効力範囲外の事実)

本文書追加によりpre-authorization stateは解除されない。
FROZEN=不変/Extension=DRAFT/Human Gate=未裁定/継続中、いずれも
変化なし。本文書は[mocka_hab_v1_contract.md](mocka_hab_v1_contract.md)
[mocka_human_gate_decision_definition_v1.md](mocka_human_gate_decision_definition_v1.md)
と同様、「参照可能な設計文書」として追加されたのみである。

## 9. 実装状態

本契約は関係構造の定義のみであり、コード・実行システムは一切
実装していない。実装着手にはHuman Gate Finalization(博士本人)の
明示指示を要する。

## 10. 次の論点(本文書の対象外、提示のみ)

以下はユーザーから次の論点として提示されたが、本文書では着手しない。

- Phase10統合との接続
- Phase10-3/10-4の「FROZEN裁定」との関係
- Extension層の発火条件
- どの段階でHuman Gateが挿入されるか

これらはPhase10-3 FROZEN契約・Phase10-Stasis・Trigger Wiring未裁定の
領域に直接触れるため、着手にはユーザーの明示裁定を要する。
