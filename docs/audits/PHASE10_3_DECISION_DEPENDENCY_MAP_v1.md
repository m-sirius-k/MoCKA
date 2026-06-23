# Phase10-3 Decision Dependency Map v1

Status: IMPACT ANALYSIS ONLY（波及分析のみ。推奨禁止・採択禁止・
契約作成禁止）
Date: 2026-06-23

本文書は論点1（Reasoning Definition、PHASE10_3_REASONING_
DEFINITION_OPTIONS_v1.md）のOption A/B/Cそれぞれが、論点2
（Candidate Authority）・論点3（Projection Boundary）・論点4
（Collision Amplification）・論点5（Advisor境界）へどう波及
するかを整理する。いずれのOptionも推奨・採択しない。

## Option Aの波及

```
Option A: Reasoning = 候補生成主体

-> 論点2への波及:
    Model A（generateのみ）が最も自然に対応する。Option Aは
    「派生・拡張・再構成」を定義に含まないため、Model B/C/Dを
    選ぶ場合は論点1（Option A）と論点2（Model B以上）の間に
    定義上の不整合が生じる可能性がある（Reasoningの定義に
    含まれない操作をAuthorityとして許可することの整合性問題）。

-> 論点3への波及:
    Case A（Projection内部）またはCase B（Projection後段）との
    結びつきが強い。Option Aの「候補生成」はPhase9
    SemanticProjectionLayerの責務と直接重複するため
    （PHASE10_3_REASONING_DEFINITION_OPTIONS_v1.md
    「Projectionとの境界: 最も近接」）、Case C（独立）を選ぶ場合は
    Phase9層との機能的重複をどう避けるかという追加論点が生じる。

-> 論点4への波及:
    candidate生成が確定するため、collision増幅の空白
    （PHASE10_3_COLLISION_AMPLIFICATION_AUDIT_v1.md）が
    実際に問題化する可能性が論点3 Option中で最も高い
    （生成行為そのものがcollisionを生み得る構造、
    PHASE10_3_COLLISION_GOVERNANCE_STUDY_v1.md確認事項1参照）。

-> 論点5への波及:
    Advisorとの差分は最大（候補生成がAdvisorで禁止されている
    操作のため）。Advisor/Reasoningの境界は「候補生成の有無」
    という単一軸でほぼ説明できるため、論点5の複雑性は3 Option中
    最小になる可能性がある。
```

## Option Bの波及

```
Option B: Reasoning = 候補生成＋候補派生主体

-> 論点2への波及:
    Model B（generate + derive）が直接対応する。Model C/Dを
    選ぶ場合、Option Bの定義（生成+派生のみ）にexpand/
    reconstructが含まれないため、Option Aと同様の定義上の
    不整合が生じうる。

-> 論点3への波及:
    Option Aと同様にCase A/Bとの結びつきが強いが、「派生」は
    既存candidateを入力とするため、Case B（後段、既存candidate群
    を受け取る配置）との整合性がOption Aよりもさらに高くなる
    可能性がある（派生元candidateがPhase9生成物である前提が
    Case Bの配置と自然に一致するため）。

-> 論点4への波及:
    候補生成＋候補派生の両方がcollisionを生む可能性を持つ
    （PHASE10_3_COLLISION_GOVERNANCE_STUDY_v1.md確認事項1
    「派生candidateが既存candidateと矛盾する場合、collisionが
    増える」）。論点4の空白がOption Aよりも広い範囲
    （生成由来+派生由来の両方）で問題化しうる。

-> 論点5への波及:
    Advisorとの差分は最大かつOption Aより広い。Advisorの
    「代替候補提示」（既存candidate群の再提示）と
    Reasoningの「候補派生」（既存candidateから新candidateを
    導出）が表面上類似するため、論点5の機能境界整理が
    Option Aより複雑になる（PHASE10_3_REASONING_DEFINITION_
    OPTIONS_v1.md「Advisorとの差分: 最大かつOption Aより広い」）。
```

## Option Cの波及

```
Option C: Reasoning = 意味的推論主体（候補生成は結果の一部）

-> 論点2への波及:
    候補生成が主目的ではないため、Model A〜Dのいずれを選んでも
    Option Cの定義との直接的な矛盾は生じにくい（候補生成が
    「結果の一部」という位置づけのため、Authority範囲の広狭は
    定義そのものへの影響が小さい）。ただし、Model選択による
    実際の運用上の影響（collision/Projection/Human Gate影響）は
    Option A/Bと同様に発生する。

-> 論点3への波及:
    Case C（Projectionとは独立）との結びつきが強い
    （PHASE10_3_REASONING_DEFINITION_OPTIONS_v1.md
    「Projectionとの境界: 最も遠い」）。候補生成が結果の一部に
    過ぎないため、Projection層の責務（候補生成そのもの）との
    分離が他のOptionより明確になる可能性がある。

-> 論点4への波及:
    意味的推論の結果として候補が生じる場合でも、生成という
    事実自体は変わらないため、論点4の空白はOption A/Bと同様に
    存在する。ただし生成が「主目的」ではないため、生成頻度や
    生成規模がOption A/Bと異なる可能性があり、これが
    collision増幅の実際の影響度を変える可能性がある
    （本文書ではこの影響度の大小を判定しない）。

-> 論点5への波及:
    Advisorとの差分は最小（PHASE10_3_REASONING_DEFINITION_
    OPTIONS_v1.md「Advisorとの差分: 最小」）。Advisor Nodeの
    役割2〜4（候補の説明/代替案の提示/矛盾点の指摘）との重複が
    最も大きいため、論点5の機能境界整理が3 Option中最も複雑に
    なる可能性が高い。
```

## Option横断の波及パターン比較表

```
波及先論点        | Option A        | Option B          | Option C
--------------------|-------------------|---------------------|-------------------
論点2との整合      | Model A         | Model B           | A〜D全て定義上
  しやすいModel      | （最小）         | （中）             | 矛盾しにくい
論点3との結びつき   | Case A/B        | Case A/B（特にB）  | Case C
論点4の問題化度     | 中（生成由来）   | 高（生成+派生由来）| 不明
                                                              （頻度・規模が
                                                               未確定要因）
論点5の複雑性       | 最小            | 中                 | 最大
```

## 結論

```
本文書はOption A/B/Cそれぞれの論点2〜5への波及を整理したのみ
であり、いずれのOptionも推奨・採択していない。次工程（Step6
Decision Readiness Report）で本文書を含む分析結果を集約する。
```
