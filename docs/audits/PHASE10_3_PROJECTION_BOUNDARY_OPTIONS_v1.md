# Phase10-3 Projection Boundary Options v1

Status: OPTIONS STUDY ONLY（並列比較のみ。結論禁止・採択禁止・
契約作成禁止）
Date: 2026-06-23

本文書はPHASE10_3_REASONING_PREPARATION_NOTE_v1.md論点D
（Reasoning NodeはProjection前/後のどちらを扱うべきか）を、
3つのCaseとして並列比較する。いずれも採択しない。

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
    Reasoning Nodeは入力（自然言語等）に対しProjection層を
    経由せず独自に意味的判断を行う、Projection層と並列の
    別経路。
```

## 比較表

```
比較項目          | Case A（内部）       | Case B（後段）        | Case C（独立）
--------------------|------------------------|------------------------|------------------------
Phase9整合性         | 低。Phase9-1〜9-3Aは  | 高。Phase10-1/10-2が   | 中。Phase9層への
                     | SemanticProjection     | 既に確立した「後段     | 直接依存は無くなる
                     | Layerの2メソッド署名    | Node」パターン         | ため、Phase9-1〜
                     | を確定済み（Phase9-2、 | （Observer/Advisorと   | 9-3Aの絶対禁止
                     | NotImplementedError    | 同型配置）をそのまま   | （単一解収束禁止等）
                     | 固定）。Reasoning      | 適用できる。           | を直接遵守する義務が
                     | Nodeを内部要素にする    |                        | 薄れる一方、Phase9
                     | 場合、この既存署名を    |                        | 層との整合性を別途
                     | 変更せずに統合できるか  |                        | 設計し直す必要が
                     | が論点（署名変更は     |                        | ある。
                     | Phase9-2/10-0で禁止    |                        |
                     | 済み）。               |                        |
Candidate Source整合性| 中。Phase9-3A         | 高。既存candidate群    | 低。Case Cが独自の
                     | Source-A/B/C（Intent/  | （Phase9生成済み）を   | candidateを生成する
                     | Explanation/Hybrid     | 入力として扱う点で     | 場合、Phase9-3Aの
                     | Path）と同じ生成経路を  | Advisor Nodeと同型。   | Source-A/B/C分類
                     | 共有する可能性があり、  | Reasoning固有の        | （Intent/Explanation/
                     | 既存Source分類との      | candidate生成（B-1等） | Hybrid Path）が
                     | 重複・競合が生じやすい。| を行う場合、その生成    | 適用されず、新たな
                     |                        | がPhase9-3Aの分類の    | 第4のSourceとして
                     |                        | 外側で発生する点が     | 扱う必要が生じる
                     |                        | 整理を要する。         | （既存分類との
                     |                        |                        | 整合性が論点）。
Ranking整合性        | 低。Phase9-3A第4章     | 中。Phase10-1/10-2の  | 低〜中。独自経路で
                     | Ranking Policyは        | 禁止事項（Ranking変更  | あっても「採択する
                     | Projection層内部の      | 禁止）がそのまま適用   | のはProjection層では
                     | scoreまで規定している。 | できるため、後段       | ない」という
                     | Reasoning Nodeが内部に  | Nodeパターンとしての   | Phase9-3A原則
                     | 入る場合、この既存      | 整合性は高い。         | 自体が「Projection
                     | Ranking Policyの適用    |                        | 層」を主体に書かれて
                     | 範囲を拡張・変更する     |                        | いるため、Case Cの
                     | ことになり、Phase9-3A   |                        | ような独立経路に
                     | 自体の改変リスクが生じる。|                       | 同一文言を適用できる
                     |                        |                        | か再検証が必要。
Human Gate整合性     | 中。三分離原則         | 高。Observer/Advisorと | 中。三分離原則自体は
                     | （Phase10-0第4章）は    | 同型のため、既存の     | Node種別を問わず
                     | Node種別を問わず適用    | Human Gate依存関係     | 適用される
                     | されるためHuman Gateの  | 確認パターン           | （PHASE10_3_
                     | 単一裁定点自体は揺らが  | （PHASE10_3_HUMAN_     | HUMAN_GATE_
                     | ないが、Projection層    | GATE_DEPENDENCY_       | DEPENDENCY_
                     | 内部への統合は          | AUDIT_v1.md）をそのまま | AUDIT_v1.md確認
                     | Phase9-1絶対禁止        | 適用しやすい。         | 事項1・2参照）が、
                     | （Runtime/Human Gateの  |                        | 独立経路の場合
                     | クラス・メソッド署名    |                        | Human Gateへの
                     | 変更禁止）の対象範囲に  |                        | 提示物の形式が
                     | Projection層自体が       |                        | Projection層経由とは
                     | 含まれるかという        |                        | 異なる可能性があり、
                     | 解釈問題が生じる。      |                        | Phase7-B6既存裁定
                     |                        |                        | タイプとの接続を
                     |                        |                        | 別途要する。
```

## Case間の構造的観察（結論ではない）

```
観察1: Case Bはいずれの比較項目でも既存パターン（Observer/
    Advisor）との整合性が最も高く出ている。これはCase Bが
    既存のNode配置構造をそのまま継承する選択であるため
    構造的に当然の結果であり、優劣の結論ではない。

観察2: Case Aは「Phase9-2で確定済みのメソッド署名を変更せずに
    内部統合できるか」という技術的・制度的な前提問題を抱えており、
    この前提が解決されない限りCase A自体の実現可能性が
    評価できない。

観察3: Case Cは既存層への依存を最小化する代わりに、Phase9-3A
    Source分類・Phase7-B6裁定タイプという既存の確定済み構造との
    接続を新たに設計する必要があり、「独立性」と「既存制度との
    接続コスト」が表裏の関係にある。
```

## 結論

```
本文書はCase A/B/Cを4観点で並列比較したのみであり、いずれも
採択していない。次工程（Step6 Human Gate Decision Package）で
本文書の論点を集約する。
```
