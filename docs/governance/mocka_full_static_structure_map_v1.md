# MoCKA Full Static Structure Map v1 (HAB + Human Gate + Phase10 + Extension)

Status: DRAFT(参照文書として追加。pre-authorization stateを解除しない)
Date: 2026-06-24
作成者: くろこ(博士) / 整理: Claude-sonnet-4-6

## 0. 本文書の位置づけ

本図は実装・ACTIVE遷移・発火条件を一切含まない「構造可視化のみ」
である。

- 実行設計ではない
- トリガー設計ではない
- 状態遷移ロジックではない
- レイヤ関係の静的マップのみ

これまで確定した以下の文書の関係を1枚に集約したものであり、
各文書の内容自体は変更しない。

- [mocka_hab_v1_contract.md](mocka_hab_v1_contract.md)
- [mocka_human_gate_decision_definition_v1.md](mocka_human_gate_decision_definition_v1.md)
- [mocka_hab_human_gate_relation_v1.md](mocka_hab_human_gate_relation_v1.md)
- [mocka_phase10_human_gate_insertion_map_v1.md](mocka_phase10_human_gate_insertion_map_v1.md)
- [../audits/mocka_phase10_blackbox_impact_analysis_v1.md](../audits/mocka_phase10_blackbox_impact_analysis_v1.md)
- [../contracts/mocka_extension_loop_contract_v1.md](../contracts/mocka_extension_loop_contract_v1.md)

本文書追加によりpre-authorization state(FROZEN=不変/Extension=DRAFT/
Human Gate=未裁定/継続中)は解除されない。

## 1. スコープ定義

今回扱うのは構造の静的関係のみ。

- HAB
- Human Gate Core
- Human Gate Finalization
- Phase10-3 / 10-4(ブラックボックス)
- Extension

### 禁止領域(絶対非参照)

- 発火条件
- Trigger Wiring
- Phase遷移ルール
- FROZEN裁定内部ロジック
- ACTIVE遷移条件

## 2. 全体統合図(静的構造版 v1.0)

```
                  [HAB STATE LAYER]
                        |
                        v
              [ Human Gate Core      ]
              [ (evaluation only)    ]
                        |
                        v
              [ Phase10-3 / 10-4     ]
              [ (BLACK BOX)          ]
                        |
                        v
              [ Human Gate           ]
              [ Finalization         ]
              [ (Dr. decision only)  ]
                        |
                        v
              [ EXTENSION LAYER (DRAFT) ]
                        |
                        v
                [ RUNTIME / OUTPUT ]
```

## 3. 各レイヤの役割(再確認)

### HAB

- 状態スナップショット
- 意味・構造の記録のみ
- 判断機能なし

### Human Gate Core

- 評価・整合性チェック
- フィルタリング
- 注釈生成
- 非裁定

### Phase10-3/10-4

- 完全ブラックボックス
- 内部構造非依存
- 入出力のみ存在

### Human Gate Finalization

- 唯一の裁定点
- 博士による決定のみ
- APPROVE / HOLD / REJECT / DEFER確定点

### Extension Layer

- 裁定済み構造のみ受け入れ
- 未裁定データ排除
- 実行準備層

## 4. 重要な構造的意味

この図が示している本質は1つだけ。

「評価は前後に分離され、中央(Phase10)はブラックボックスのまま
維持される」

- 前段: 観測と評価
- 中央: 不可視処理
- 後段: 人間裁定と通過制御

## 5. 安全性確認

この統合図は以下を満たす。

- Phase10内部未参照
- Trigger Wiring非復活
- 発火条件未記述
- ACTIVE遷移非含意
- pre-authorization state維持

## 6. 現在の運用状態(2026-06-24時点、本文書の効力範囲外の事実)

本文書追加によりpre-authorization stateは解除されない。
FROZEN=不変/Extension=DRAFT/Human Gate=未裁定/継続中、いずれも
変化なし。本文書は「MoCKAの構造関係を固定しただけの静的マップ」
として追加されたのみである。

## 7. 実装状態

本文書は構造の静的可視化のみであり、コード・実行システムは一切
実装していない。実装着手にはHuman Gate Finalization(博士本人)の
明示指示を要する。

## 8. 次の論点(本文書の対象外、提示のみ)

ユーザーから次の論点として以下が提示されたが、本文書では着手しない。

- この構造をベースにした「境界仕様書(Interface Contract化)」
- または「HAB単体の完全定義固定」

着手にはユーザーの明示裁定を要する。
