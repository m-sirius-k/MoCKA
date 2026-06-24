# MoCKA HAB (Human Authority Boundary) v1

Status: DRAFT(参照文書として追加。pre-authorization stateを解除するものではない)
Date: 2026-06-24
作成者: くろこ(博士) / 整理: Claude-sonnet-4-6

## 0. 本文書の位置づけ(重要)

本文書はpre-authorization state(2026-06-24に確定: 何も追加しない/
裁定しない/統合しない、次のトリガーは外部=Human Gate側)を解除する
ものではない。

HABは「状態を動かす指示」ではなく「状態の扱い方の定義」である。
- 状態解除(trigger解除): 何かを動かす/制約を外す/判断を開始する
- 構造定義(HAB v1): どう動くかのルール化、まだ動かない、
  どの状態でも適用される

本文書追加後も、現在の状態は変化しない:
FROZEN=不変、Extension=DRAFT、Human Gate=未裁定、
pre-authorization state=継続中。

## 1. 基本定義

HABはMoCKAにおける以下を制御する統治層である。

「どの層に、いつ、誰の判断で、どの強度で介入できるか」

対象層:
- FROZEN層(事実・不変)
- Extension層(Analytical / index / meta-essence / loop)
- Human Gate(裁定)

## 2. 状態モデル(State Model)

全システム状態は以下で統一管理される。

- STABLE: 通常運用(読み取り・追加のみ)
- DRAFT: 設計中(変更可能だが非確定)
- REVIEW: 人間裁定待ち
- STASIS: 完全停止(変更禁止)
- ACTIVE: 裁定確定・運用開始

## 3. Trigger Condition Map(発火条件)

### 3.1 Human Gate発火条件

以下のいずれかで発火する。

- FROZEN層への変更要求
- Extension層の構造変更要求
- index/meta-essence/loopの再定義
- Phase10系(Signal / Stasis)に関わる再開要求
- 「制度的許可」を伴う判断要求

### 3.2 自動処理許可条件

以下はHuman Gate不要。

- Analytical Event追加
- index append-only追加
- meta-essence生成(非破壊)
- Loopの観測記録

### 3.3 即時STASIS条件

以下で強制停止する。

- FROZEN書き換え試行
- Signal Contract再定義
- Trigger Wiring再開要求(Phase10-Stasis override)

## 4. Authority Boundary Matrix(権限境界)

| 層 | 読み取り | 追加 | 変更 | 削除 |
|---|---|---|---|---|
| FROZEN | 可 | 不可 | 不可 | 不可 |
| Analytical | 可 | 可 | 不可 | 不可 |
| index | 可 | 可 | 不可 | 不可 |
| meta-essence | 可 | 可 | 不可 | 不可 |
| Loop | 可 | 可(記録のみ) | 不可 | 不可 |
| Human Gate | 可 | 条件付き | 制度変更のみ | 不可 |

## 5. Transition Rules(状態遷移)

### 5.1 DRAFT -> ACTIVE

条件:
- Human Gate裁定完了
- FROZEN非干渉確認
- Extension構造整合確認

### 5.2 ACTIVE -> REVIEW

条件:
- 構造変更要求発生
- Phase再定義要求
- 重大矛盾検出

### 5.3 REVIEW -> STASIS

条件:
- 裁定保留
- 矛盾未解決
- 安全停止要求

### 5.4 STASIS -> ACTIVE

条件:
- Human Gate再承認
- 全層整合再確認

## 6. MoCKA全体統治モデル

```
[FROZEN LAYER]
  事実固定・変更不可
        |
        v
[EXTENSION LAYER]
  観測・構造・圧縮(Analytical / index / meta-essence / loop)
        |
        v
[HAB LAYER]
  発火条件・権限・状態遷移管理
        |
        v
[HUMAN GATE]
  制度裁定(最終意思決定)
```

## 7. 本質定義(最重要)

HABは制御システムではなく、

「どの現実が編集可能かを定義する境界層」

である。

## 8. 完成状態(本文書のスコープ)

- Trigger Map: 確定
- Authority Matrix: 確定
- Transition Rules: 確定
- STASIS制御: 統合済み
- Extension整合: 維持

## 9. 現在の運用状態(2026-06-24時点、本文書の効力範囲外の事実)

本文書はルール定義であり、現在の実際の状態を変更しない。
2026-06-24時点の実際の状態は以下の通り(変化なし):

- FROZEN: 不変
- Extension: DRAFT
- Human Gate: 未裁定
- pre-authorization state: 継続中

本文書(HAB v1)自体は「参照可能な設計文書」として追加されたのみであり、
DRAFT -> ACTIVE への遷移条件(5.1節)はまだ満たされていない。

## 10. 実装状態

本契約は統治モデルの定義のみであり、コード・実行システムは一切
実装していない。実装着手にはHuman Gateの明示指示を要する。
