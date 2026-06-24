# Phase10-3 Projection Boundary Matrix v1

Status: MATRIX COMPARISON ONLY（比較のみ。結論禁止・採択禁止・契約作成禁止）
Date: 2026-06-24

本文書はPHASE10_3_PROJECTION_BOUNDARY_OPTIONS_v1.mdおよび
PHASE10_3_PROJECTION_INDEPENDENCE_AUDIT_v1.mdで整理されたCase A
（Projection内部）/Case B（Projection後段）/Case C（Projectionとは
独立）を、Projectionとの重複/Advisorとの重複/Observerとの重複/
Semantic Layer侵食リスクの4観点のみで再整理する。結論は行わない。

## Case定義

```
Case A: Projection内部
    Reasoning NodeがPhase9 SemanticProjectionLayerの一部
    （内部構成要素）として位置づく。
Case B: Projection後段
    Reasoning NodeはProjection層が生成したProjectionResultを
    受け取る、Projection層の外側にあるNode
    （Advisor/Observerと同じ後段配置）。
Case C: Projectionとは独立
    Reasoning Nodeは入力（自然言語等）に対しProjection層を経由せず
    独自に意味的判断を行う、Projection層と並列の別経路。
```

## 比較マトリクス

```
観点              | Case A（内部）         | Case B（後段）         | Case C（独立）
--------------------|---------------------------|---------------------------|---------------------------
Projectionとの重複  | 最大。Phase9-1〜9-3Aの     | 中。既存candidate群を      | 最小。Phase9層への直接
                    | SemanticProjectionLayer    | 受け取るのみで内部処理は   | 依存が無くなるが、独自
                    | メソッド署名（Phase9-2     | 共有しない。Source分類     | candidateを生成する場合は
                    | 確定済み）と統合する場合、  | （Source-A/B/C）との      | Phase9-3A分類の外側に
                    | 既存署名の変更が必要に     | 関係整理は必要だが構造的   | 第4のSourceとして並立する
                    | なる可能性（署名変更は     | 重複ではない。            | リスク。
                    | Phase9-2/10-0で禁止済み）。|                          |
--------------------|---------------------------|---------------------------|---------------------------
Advisorとの重複      | 中。Projection内部に       | 高。既存candidate群を      | 低〜中。独自経路のため
                    | 統合される場合、Advisorが   | 受け取る点でAdvisorと      | Advisorが扱う既存
                    | 同じProjection出力を参照    | 同型配置（後段Node        | candidate群との関係が
                    | する構造に近づく。          | パターン）。               | 薄くなる。
--------------------|---------------------------|---------------------------|---------------------------
Observerとの重複     | 低。Observerは後段Node     | 高。Observer/Advisorと     | 低。Observerも後段Node
                    | パターン（Phase10-1）の    | 同型のNode配置パターンを   | パターンのため、独立経路
                    | 外側にあるため、内部統合    | 共有する。                | のCase Cはこのパターン
                    | のCase Aとは構造的に異なる。|                          | 自体から外れる。
--------------------|---------------------------|---------------------------|---------------------------
Semantic Layer侵食   | 最大。Projection層内部の    | 中。Phase10-1/10-2の       | 低〜中。Phase9-3A原則
リスク               | Ranking Policy（Phase9-3A  | 禁止事項（Ranking変更禁止）| （Projection層主体で
                    | 第4章）の適用範囲を拡張・    | がそのまま適用できるため、 | 記述）を独立経路に同一
                    | 変更することになり、        | 既存制度への侵食は小さい。 | 文言で適用できるかが
                    | Phase9-3A自体の改変リスクが |                          | 未解決のまま残る。
                    | 生じる。                   |                          |
```

## Case間の構造的観察（観察のみ、結論ではない）

```
PHASE10_3_PROJECTION_BOUNDARY_OPTIONS_v1.mdの観察1〜3を継承:
Case Bはいずれの観点でも既存パターン（Observer/Advisor）との
整合性が高く出るが、これはCase Bが既存Node配置構造をそのまま
継承する選択であるための構造的な結果であり、優劣の結論ではない。

Case Aは「Phase9-2で確定済みのメソッド署名を変更せずに内部統合
できるか」という前提問題を抱えており、この前提が解決されない限り
Case A自体の実現可能性が評価できない。

Case Cは既存層への依存を最小化する代わりに、Phase9-3A Source分類・
Phase7-B6裁定タイプという既存の確定済み構造との接続を新たに設計
する必要があり、「独立性」と「既存制度との接続コスト」が表裏の
関係にある。
```

## 注記

本文書はCase A/B/Cを4観点で再整理したのみであり、結論・採択は
行っていない。
