# Phase10-3 Reasoning Definition Options v1

Status: OPTIONS STUDY ONLY（並列比較のみ。結論禁止・採択禁止・
契約作成禁止）
Date: 2026-06-23

本文書はPHASE10_3_REASONING_PREPARATION_NOTE_v1.md論点A-1
（Reasoningとは候補生成行為そのものか、候補生成の前提となる
意味的判断か）を、3つのOptionとして並列比較する。いずれも
採択しない。

## Option A: Reasoning = 候補生成主体

```
定義（仮）: ReasoningはEventCandidate/NLCandidateそのものを
            生成する行為主体である。
```

```
比較項目              | 内容
-----------------------|----------------------------------------
Observerとの差分        | 最大。Observerは生成権限を一切持たない
                        | （Phase10-1第2章禁止: Candidate変更）。
                        | Option Aは候補生成という新規権限を
                        | Reasoningに与える点で、Observerとの
                        | 差は「観測」と「生成」という質的な差。
Advisorとの差分         | 最大。Advisor Nodeは「代替候補提示は
                        | 既存candidate群の再提示に限定」され
                        | 新規生成は明示的に禁止されている
                        | （Phase10-2第4章）。Option Aは
                        | Advisorが禁止された操作をReasoningに
                        | 許可する形になる。
Projectionとの境界      | 最も近接。SemanticProjectionLayer
                        | （Phase9）が既に担う「候補生成」と
                        | 機能的に重複する可能性が高い。
                        | Reasoning NodeがPhase9層の代替・拡張に
                        | なるのか、別の生成経路になるのかが
                        | 直接の論点になる。
Human Gateとの距離      | 中程度。生成のみであり採択は行わない
                        | ため、Human Gateとの距離自体は他の
                        | Option と変わらない（Phase10-0三分離は
                        | いずれのOptionでも維持される前提）。
```

## Option B: Reasoning = 候補生成＋候補派生主体

```
定義（仮）: Reasoningは新規候補の生成に加え、既存candidateからの
            派生（derive_candidate、PHASE10_3_REASONING_
            PREPARATION_NOTE_v1.md候補B-2）も担う行為主体である。
```

```
比較項目              | 内容
-----------------------|----------------------------------------
Observerとの差分        | 最大（Option Aと同様、生成権限の有無が
                        | 質的差）。
Advisorとの差分         | 最大かつOption Aより広い。Advisorの
                        | 「代替候補提示」（既存candidate群の
                        | 再提示）と「候補派生」（既存candidateを
                        | 起点に新たなcandidateを導出）は表面上
                        | 似ているため、両者の機能的境界が
                        | Option Aより一層不明瞭になる
                        | （PHASE10_3_CANDIDATE_LIFECYCLE_
                        | AUDIT_v1.md論点D-2と直接関連）。
Projectionとの境界      | Option Aと同様に近接するが、「派生」は
                        | 「新規生成（ゼロから）」とは異なる
                        | 操作であり、既存candidateを入力とする
                        | 点でProjection層のIntent Path/
                        | Explanation Path（Phase9-3A）の
                        | 候補生成ロジックとの関係がさらに
                        | 複雑化する。
Human Gateとの距離      | Option Aと同様、中程度（三分離は維持
                        | される前提）。ただし派生元candidateの
                        | 出自（why_generated等）が複数世代に
                        | 渡って積み重なる場合、Human Gateが
                        | 裁定時に参照する情報量が増える
                        | （距離そのものではなく、裁定材料の
                        | 複雑度が増す）。
```

## Option C: Reasoning = 意味的推論主体（候補生成は結果の一部）

```
定義（仮）: Reasoningの本質は候補間・観測結果間の意味的関係を
            推論することであり、候補生成はその推論プロセスの
            派生的な出力（結果の一部）に過ぎない。
```

```
比較項目              | 内容
-----------------------|----------------------------------------
Observerとの差分        | 中程度。Observerの「状態説明」
                        | （Phase10-1第2章、解釈を加えない）に
                        | 対し、Option Cは「意味的関係の解釈」を
                        | 中心に置く点で差がある。ただし候補
                        | 生成が主目的でないため、Option A/Bより
                        | Observerとの差は小さい。
Advisorとの差分         | 最小。Advisor Nodeの役割2（候補の説明）・
                        | 役割3（代替案の提示）・役割4（矛盾点の
                        | 指摘）は、いずれも「意味的関係の解釈」
                        | という点でOption Cの定義と重なりが大きい
                        | （PHASE10_3_CANDIDATE_LIFECYCLE_
                        | AUDIT_v1.md論点D-2が指摘する重複が
                        | 最も顕著になる）。
Projectionとの境界      | 最も遠い。候補生成が「結果の一部」に
                        | 過ぎないため、Projection層の責務
                        | （候補生成そのもの）とは明確に分離
                        | できる可能性がある。
Human Gateとの距離      | Option A/Bと同様、三分離は維持される
                        | 前提。ただし「意味的推論」という性質上、
                        | Human Gateへの提示物が「候補」ではなく
                        | 「解釈・関係性の説明」になる場合があり、
                        | Phase7-B6裁定タイプ（accept/reject/
                        | defer/split）が候補単位の裁定を前提と
                        | している既存構造と、Option Cの出力形式
                        | がどう接続するかという論点が新たに
                        | 生じる。
```

## 比較表（3 Option横断、事実整理のみ）

```
                  Option A    Option B    Option C
候補生成権限       あり        あり(+派生)  結果の一部のみ
Advisorとの重複度   低          中          高
Projectionとの近接度 高          高          低
Human Gate裁定形式  candidate単位 candidate単位+派生履歴 解釈・関係性中心
                                                          （既存裁定形式との
                                                           接続が論点）
```

## 結論

```
本文書はOption A/B/Cを並列比較したのみであり、いずれも採択
していない。次工程（Step6 Human Gate Decision Package）で
本文書の論点を集約する。
```
