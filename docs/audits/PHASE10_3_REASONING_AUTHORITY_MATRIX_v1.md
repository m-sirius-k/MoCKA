# Phase10-3 Reasoning Authority Matrix v1

Status: STRUCTURING ONLY（整理のみ。採択禁止・契約作成禁止）
Date: 2026-06-23

本文書はObserver Node（Phase10-1, FOUND・未固定）・Advisor Node
（Phase10-2, FOUND・未固定）・Reasoning Node（Phase10-3未着手、
Phase10-0第1章Category 3で仮置き定義のみ・
PHASE10_3_REASONING_PREPARATION_NOTE_v1.mdで論点列挙済み）の
権限を、既存契約に明記された範囲でマトリクス化する。Reasoning
列の値はすべて「既存文書からの引用または論点としての仮置き」で
あり、本文書が新たに採択するものではない。

## Authority Matrix

```
操作                      | Observer | Advisor | Reasoning
--------------------------|----------|---------|------------
read                      | 許可     | 許可    | 未確定(論点A-2)
aggregate                 | 許可     | 未記載  | 未確定
explain                   | 許可     | 許可    | 未確定(論点A-1)
                            (状態説明  (候補説明  (Phase10-0
                             のみ)      ・解釈含む) Category3で
                                                  仮置き)
compare                   | 不可     | 許可    | 未確定
                            (候補比較   (候補比較
                             権限なし)   明記)
recommend                 | 不可     | 許可    | 未確定
                            (提案権限   (Recommendation
                             なし)       出力形式)
generate_candidate        | 不可     | 不可    | 未確定(論点B-1)
                            (Phase10-0  (Phase10-2第4章
                             第1章で      「代替候補提示は
                             Projection   既存candidate群の
                             介入禁止)    再提示に限定、新規
                                          candidate生成は
                                          Phase9層の責務」
                                          と明記)
derive_candidate          | 不可     | 不可    | 未確定(論点B-2)
expand_candidate          | 不可     | 不可    | 未確定(論点B-3)
reconstruct_candidate     | 不可     | 不可    | 未確定(論点B-4)
adopt                     | 不可     | 不可    | 不可
                            (Human Gate (Human Gate (Phase10-0
                             のみ)       のみ)       第4章三分離
                                                     はNode種別を
                                                     問わず適用)
execute                   | 不可     | 不可    | 不可
                            (Orchestrator (Orchestrator (同上、
                             のみ)         のみ)         三分離原則は
                                                        Reasoning Node
                                                        にも及ぶ前提)
resolve_collision         | 不可     | 不可    | 不可
                            (Phase7-B5   (Phase7-B5   （論点C-3:
                             継承)        継承)        生成によるcollision
                                                       増加と既存collision
                                                       解消は別概念と
                                                       仮区別されている
                                                       が未確定）
```

## 凡例

```
許可:        既存契約（Phase10-1/10-2）に明記された許可操作
不可:        既存契約に明記された禁止操作、または上位契約
              （Phase10-0第4章三分離等）から確実に導出される禁止
未確定:      Reasoning Node契約が存在しないため、本文書時点では
              論点としてのみ存在する操作（PHASE10_3_REASONING_
              PREPARATION_NOTE_v1.mdの論点A〜Cを参照）
未記載:       Advisor Node契約（Phase10-2）に明記がなく、許可・
              禁止のいずれとも確定できない操作
```

## 観察事項（採択ではない、構造上の指摘のみ）

```
観察1: adopt/execute/resolve_collisionの3操作は、Observer/
    Advisor/Reasoningのいずれにおいても「不可」で揃っている。
    これはPhase10-0第4章Reasoning Ownership Rule（Reasoning/
    Adoption/Execution三分離）がNode種別を問わず適用される
    設計であることの構造的反映であり、Reasoning Node契約が
    まだ存在しない現時点でも、この3操作については既に境界が
    確定していると見ることができる（PHASE10_3_HUMAN_GATE_
    DEPENDENCY_AUDIT_v1.mdで別途検証する）。

観察2: generate_candidate/derive_candidate/expand_candidate/
    reconstruct_candidateの4操作（PHASE10_3_REASONING_
    PREPARATION_NOTE_v1.md候補B-1〜B-4）は、Observer/Advisorの
    両方で「不可」が確定しているのに対し、Reasoningでは
    「未確定」のままである。この4操作こそがReasoning Nodeを
    Observer/Advisorと区別する核心的差分になる可能性が高いが、
    本文書ではこれを採択しない。

観察3: aggregateはObserverのみに明記があり、Advisor契約には
    記載が無い（「未記載」）。これはAdvisor Nodeが集計機能を
    持たないことを意味するのか、単に契約記述の対象外だったのかが
    既存契約から判別できない。Reasoning Node設計時にこの空白を
    どう扱うかも論点として残る（本文書では判断しない）。
```

## 結論

```
本文書はObserver/Advisor/Reasoningの権限を既存文書の範囲で
マトリクス化したのみであり、Reasoningの「未確定」項目について
いずれも採択・固定していない。
```
