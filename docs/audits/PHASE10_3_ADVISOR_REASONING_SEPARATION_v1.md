# Phase10-3 Advisor vs Reasoning Separation Report v1

Status: STRUCTURING ONLY（整理のみ。結論禁止・契約作成禁止）
Date: 2026-06-23

本文書はAdvisor Node（Phase10-2、確定済み・未固定）と
Reasoning Node（Phase10-3、未確定）の境界を、候補生成/候補比較/
推薦/説明/派生/再構成の6操作で整理する。結論は出さない。

## 6操作比較表

```
操作        | Advisor Node（既存契約・確定済み）  | Reasoning Node（未確定・論点として整理）
-------------|---------------------------------------|----------------------------------------------
候補生成     | 禁止（Phase10-2第2章「禁止:           | 未確定（PHASE10_3_CANDIDATE_AUTHORITY_
            | candidate削除/candidate統合」、第4章   | OPTIONS_v1.md Model A〜Dのいずれか、または
            | 「代替候補提示は既存candidate群の       | 不許可、のいずれも論点として残る）。
            | 再提示に限定、新規candidateの生成は     | Reasoning Definition Option A/B（PHASE10_3_
            | Phase9層の責務」と明記）。              | REASONING_DEFINITION_OPTIONS_v1.md）を
            |                                        | 採る場合は候補生成主体になり、Option Cを
            |                                        | 採る場合は生成は「結果の一部」に縮小される。

候補比較     | 許可（Phase10-2第2章「許可:            | 未確定。PHASE10_3_REASONING_AUTHORITY_
            | 候補比較」、第2章で「複数候補の          | MATRIX_v1.mdでcompareは「未確定」のまま
            | 差異・共通点を並べて示す」と明記）。     | 整理されている。Advisorが既に比較機能を
            |                                        | 持つため、Reasoningが比較を担う場合、
            |                                        | 機能重複の整理が必要（後述「重複領域」参照）。

推薦         | 許可（Phase10-2第3章 Advisor Output    | 未確定。Reasoning Definition Option A/Bでは
            | Policy「Recommendation」として確定済み、| 推薦に相当する出力概念は定義されていない
            | 唯一解提示・winner宣言・top-1確定は      | （候補生成が主目的のため）。Option Cでは
            | 禁止）。                                | 「意味的推論の結果」として推薦相当の出力が
            |                                        | 生じる可能性があるが、Advisorの
            |                                        | Recommendationと同一物になるか別概念に
            |                                        | なるかは未整理。

説明         | 許可（Phase10-2第1章役割2「候補の       | 未確定。PHASE10_3_REASONING_DEFINITION_
            | 説明」、Observer Nodeの「状態説明」より  | OPTIONS_v1.mdでOption Cが「Advisorとの
            | 踏み込んだ「候補間の関係性や背景に       | 差分: 最小」と評価されている操作。3 Option中
            | ついての解釈を含めてよい」と明記）。     | 最も重複度が高い領域。

派生         | 禁止（Phase10-2第2章で明示の禁止語       | 未確定（PHASE10_3_REASONING_PREPARATION_
            | 「candidate統合」はあるが、「派生」      | NOTE_v1.md候補B-2 derive_candidate）。
            | 自体は明示の禁止語に無い。ただし第4章   | Reasoning Definition Option Bで明示的に
            | 「代替候補提示は既存candidate群の        | 候補生成に加えて含まれる操作として
            | 再提示に限定」という記述から、新規       | 仮定されている。
            | candidateを導出する「派生」もこの        |
            | 限定の範囲外＝禁止と解釈される）。       |

再構成       | 禁止（Phase10-2第2章「禁止:             | 未確定（候補B-4 reconstruct_candidate）。
            | candidate統合」が再構成
            | （複数candidateの情報を組み合わせる      | PHASE10_3_CANDIDATE_AUTHORITY_OPTIONS_
            | 操作）と最も直接的に重なる禁止事項）。  | v1.mdでModel D（reconstruct含む）が
            |                                        | 「mergeと同一視されうるリスク」と
            |                                        | 既に指摘されている。
```

## 重複領域の整理（結論ではない、構造の指摘のみ）

```
重複領域1: 説明
    Advisor Nodeの「候補の説明」（役割2）とReasoning Definition
    Option C（意味的推論主体）は、PHASE10_3_REASONING_
    DEFINITION_OPTIONS_v1.mdで既に「Advisorとの差分: 最小」と
    評価されている。両者が同一の操作を指すのか、推論の深さ・
    範囲が異なるのかが未整理のまま残る。

重複領域2: 候補比較
    Advisor Nodeの「候補比較」（許可済み操作）とReasoning Node
    が比較を担う場合の関係。PHASE10_3_CANDIDATE_LIFECYCLE_
    AUDIT_v1.md論点D-2「Advisorは提示のための比較、Reasoningは
    生成判断のための比較」という仮の区別が提示されているが、
    これは仮説であり確定していない。

重複領域3: 推薦と説明の出力境界
    Advisor Output Policy（Recommendation/Alternative/Risk/
    Observation）という確定済みの4出力形式と、Reasoning Node
    の出力形式（未定義）がどう関係するか。Reasoning Nodeが
    独自の出力形式を持つのか、Advisorの出力形式を共有・拡張
    するのかが未整理。
```

## 非重複領域の整理（結論ではない）

```
非重複領域1: 候補生成
    Advisorは明確に禁止、Reasoningは未確定（許可される可能性が
    ある操作として論点化されている）。これがAdvisor/Reasoningの
    最も明確な機能的差分点になりうる（PHASE10_3_REASONING_
    DEFINITION_OPTIONS_v1.md Option A/Bで「Advisorとの差分:
    最大」と評価された理由と一致）。

非重複領域2: 派生・再構成
    Advisorはいずれも禁止（再構成はcandidate統合として明示禁止、
    派生は「再提示への限定」から禁止と解釈）。Reasoningは
    いずれも未確定。候補生成と同様、Advisor/Reasoningの差分点に
    なりうる候補だが、再構成については「mergeとの同一視リスク」
    という別の論点（PHASE10_3_CANDIDATE_AUTHORITY_OPTIONS_v1.md）
    も絡む。
```

## 結論

```
本文書はAdvisor NodeとReasoning Nodeの境界を6操作で整理した
のみであり、いずれの操作についても許可・禁止・統合の判断
（結論）を出していない。次工程（Step6 Human Gate Decision
Package）で本文書の論点を集約する。
```
