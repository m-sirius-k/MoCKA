# Phase10-3 Projection Independence Audit v1

Status: COMPARATIVE ANALYSIS ONLY（比較のみ。結論禁止・契約作成
禁止）
Date: 2026-06-23

本文書はPHASE10_3_PROJECTION_BOUNDARY_OPTIONS_v1.mdのCase A/B/C
について、Phase9のProjection Contract（phase9_1_semantic_
projection_v1.md）およびProjection Strategy（phase9_3a_
projection_strategy_contract_v1.md）との「距離」を比較する。
いずれのCaseも推奨しない。

## 距離の測定軸

```
本文書では「距離」を以下3種の指標で測定する（数値化はせず、
近い/中間/遠いの3段階で評価する）。

軸1: 構造的距離
    Reasoning NodeがPhase9-2で確定済みのクラス・メソッド署名
    （SemanticProjectionLayer等）と同一の実装単位に属するか否か。

軸2: 機能的距離
    Reasoning Nodeの想定操作（候補生成等）がProjection Contract
    第1〜2章（投影の2方向、核心原則）・Projection Strategy第2章
    （Candidate Generation Sources）の既存機能と重複するか否か。

軸3: 契約的距離
    Reasoning Node契約が、Projection ContractおよびProjection
    Strategyの絶対禁止・変更ルールを直接参照・継承する必要が
    あるか、独立した条文で済むか。
```

## Case A（Projection内部）

```
軸1 構造的距離: 最も近い（ゼロに近い）
    Case AはReasoning NodeをSemanticProjectionLayerの内部構成
    要素として位置づけるため、構造的にはPhase9-2の既存実装単位
    そのものに属する。Phase9-2で確定済みの2メソッド署名
    （NotImplementedError固定）を変更せずに内部統合できるかが
    前提問題として残る（PHASE10_3_PROJECTION_BOUNDARY_
    OPTIONS_v1.md Phase9整合性参照）。

軸2 機能的距離: 最も近い
    候補生成という機能そのものがProjection Contract第1章
    （投影の2方向）・Strategy第2章（Candidate Generation
    Sources、Source-A/B/C）と直接重複する。

軸3 契約的距離: 最も近い
    Reasoning Node契約はProjection ContractおよびStrategyの
    絶対禁止・変更ルールをほぼそのまま継承する必要が生じる
    可能性が高い（独立した条文を新設する余地が小さい）。
```

## Case B（Projection後段）

```
軸1 構造的距離: 中間
    Case Bでは、Reasoning NodeはSemanticProjectionLayerの外部に
    位置するが、その出力（ProjectionResult）を直接受け取る。
    構造的には別の実装単位だが、入出力の依存関係は強い
    （Observer/Advisorと同型の配置、PHASE10_3_PROJECTION_
    BOUNDARY_OPTIONS_v1.md「既存のNode配置構造をそのまま継承」）。

軸2 機能的距離: 中間
    Reasoning固有のcandidate生成（論点2 Candidate Authority）が
    存在する場合、その生成行為はProjection Strategy第2章の
    既存Source分類（Source-A/B/C）の外側で発生するため、機能的
    重複は限定的だが、入力として既存candidateを使う点で
    Strategy第3章（Collision Policy）・第4章（Ranking Policy）
    とは密接に関係する。

軸3 契約的距離: 中間
    Reasoning Node契約はProjection Contract/Strategyの絶対禁止
    （単一解収束禁止、ranking改変禁止等）をAdvisor/Observerと
    同様の形式で「継承」する条文を持つことになるが、Projection
    Contract自体の改変は不要（Phase10-1/10-2が既に採用した
    パターンと同型）。
```

## Case C（Projectionとは独立）

```
軸1 構造的距離: 最も遠い
    Reasoning NodeはSemanticProjectionLayerを経由せず、独自に
    入力（自然言語等）を処理する別経路となるため、実装単位として
    最も分離されている。

軸2 機能的距離: 中間〜遠い
    Projection層を経由しないため直接の機能重複は避けられるが、
    候補（candidate相当の概念）を独自に生成する場合、Projection
    Contract第2章「核心原則: 単一解を作らず複数候補を保持したまま
    流す」と同種の制約を、Projection Contractとは別に独自設計
    する必要が生じる（PHASE10_3_PROJECTION_BOUNDARY_OPTIONS_
    v1.md「Phase9-3A原則自体が『Projection層』を主体に書かれて
    いるため、Case Cのような独立経路に同一文言を適用できるか
    再検証が必要」）。

軸3 契約的距離: 最も遠いが、新規設計コストが最大
    Reasoning Node契約はProjection Contract/Strategyを直接
    参照する必要が薄れる（独立した条文体系で完結できる可能性）。
    一方、Projection Contractが既に確立した原則（核心原則・
    Collision Policy・Ranking Policy相当）を、Reasoning Node
    契約側でゼロから再設計するコストが生じる。
```

## 3 Case横断比較表

```
軸          | Case A（内部） | Case B（後段） | Case C（独立）
-------------|------------------|------------------|------------------
構造的距離   | 最も近い        | 中間            | 最も遠い
機能的距離   | 最も近い        | 中間            | 中間〜遠い
契約的距離   | 最も近い        | 中間            | 最も遠い
            | （継承量最大）   | （継承量中、     | （継承量最小、
            |                 | 既存パターン     | 新規設計コスト
            |                 | 一致）          | 最大）
```

## 観察事項（結論ではない）

```
観察1: 軸1〜3はCase A→B→Cの順で単調に「距離が遠くなる」傾向で
    一致している。これはCase A/B/Cが「内部→後段→独立」という
    段階的な分離度の差として設計されていることの構造的反映で
    あり、優劣の結論ではない。

観察2: 「契約的距離が遠い（Case C）」ことは「既存契約を継承する
    負担が小さい」ことを意味するが、同時に「独自に原則を再設計
    する負担が大きい」ことも意味する。距離の遠さと設計コストの
    軽重は必ずしも一致しない（距離が遠いほど自由度は増すが、
    ゼロから設計する範囲も増える）。
```

## 結論

```
本文書はCase A/B/CのProjection Contract/Strategyとの距離を
3軸で比較したのみであり、いずれのCaseも推奨していない。
次工程（Step6 Decision Readiness Report）で本文書を含む
分析結果を集約する。
```
