# MoCKA Phase10 Human Gate Insertion Map v1

Status: DRAFT(参照文書として追加。pre-authorization stateを解除しない)
Date: 2026-06-24
作成者: くろこ(博士) / 整理: Claude-sonnet-4-6

## 0. 全体原則(前提固定)

- Trigger Wiring: 対象外(未参照・未更新)
- 発火条件: 未扱い
- 本資料の目的: 評価層の「挿入位置」のみ確定

本文書はPhase10-3/10-4を**ブラックボックス**として扱う。
内部のFROZEN裁定ロジック(
[phase10_3_signal_non_layer_contract_v1.md](phase10_3_signal_non_layer_contract_v1.md)
には一切触れず、変更しない)・起動主体の設計には踏み込まない。
[mocka_hab_human_gate_relation_v1.md](mocka_hab_human_gate_relation_v1.md)
[mocka_human_gate_decision_definition_v1.md](mocka_human_gate_decision_definition_v1.md)
で確定したHuman Gate Core/Finalizationの2層分離を前提とする。

本文書追加によりpre-authorization state(FROZEN=不変/Extension=DRAFT/
Human Gate=未裁定/継続中)は解除されない。

## 1. Phase10-3 / 10-4 基本ライン構造

```
[HAB State Layer]
        |
        v
[Phase10-3 / 10-4 Logical Layer]
        |
        v
[Extension Layer (DRAFT)]
        |
        v
[Execution / Runtime Boundary]
```

## 2. Human Gate挿入位置(Core)

### Human Gate Core(評価層)

挿入位置: HAB -> Phase10-3/10-4 に入る直前

```
[HAB]
  |
  v
* Human Gate Core(評価・整合性チェック)
  |
  v
[Phase10-3 / 10-4]
```

役割:
- 状態の読み取り
- 構造整合性チェック
- Extension影響の事前解析

ここでは一切の裁定は行わない。

## 3. Human Gate挿入位置(Finalization)

### Human Gate Finalization(人間裁定点)

挿入位置: Phase10処理後 -> Extensionに渡る直前

```
[Phase10-3 / 10-4 Output]
        |
        v
* Human Gate Finalization(博士裁定点)
        |
        v
[Extension Layer]
```

役割:
- APPROVE / HOLD / REJECT / DEFER の確定
- 状態遷移の最終許可
- Extension移行の可否確定

## 4. Extension層との境界

```
Extension Layer (DRAFT)
        ^
Human Gate Finalizationを通過したもののみ到達
```

- Extensionは「裁定済み構造のみ受け取る」。
- 未裁定データは一切入らない。

## 5. 全体統合フロー(完全版)

```
[HAB]
   |
   v
(Human Gate Core: 評価のみ)
   |
   v
[Phase10-3 / 10-4]
   |
   v
(Human Gate Finalization: 博士裁定)
   |
   v
[Extension Layer (DRAFT)]
   |
   v
[Runtime / Execution]
```

## 6. 境界ルール(重要)

### Coreの制約

- 裁定禁止
- APPROVE確定禁止
- 評価・整合性チェックのみ許可

### Finalizationの制約

- 自動決定禁止
- 博士による最終裁定のみ許可

## 7. このマップの意味(構造的本質)

「評価は前段で機械化し、決定は後段で人間固定する」

## 8. 安全性確認(本マップのスコープ内)

本マップは以下を満たす。

- Trigger Wiring未参照
- 発火条件未定義
- 自動裁定なし
- Phase10-Stasis非破壊
- Human Gate = 評価+人間裁定の分離維持

## 9. 現在の運用状態(2026-06-24時点、本文書の効力範囲外の事実)

本文書追加によりpre-authorization stateは解除されない。
FROZEN=不変/Extension=DRAFT/Human Gate=未裁定/継続中、いずれも
変化なし。本文書は他のMoCKA extension関連文書と同様、
「参照可能な設計文書」として追加されたのみである。

## 10. 実装状態

本契約は挿入位置の定義のみであり、コード・実行システムは一切
実装していない。実装着手にはHuman Gate Finalization(博士本人)の
明示指示を要する。

## 11. 次の論点(本文書の対象外、提示のみ)

ユーザーから次の論点として「このマップを基準にしたPhase10-3/10-4
差分影響分析」が提示されたが、本文書では着手しない。着手には
ユーザーの明示裁定を要する。
