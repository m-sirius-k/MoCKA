# Phase10-3 Candidate Lifecycle Audit v1

Status: STRUCTURING ONLY（構造化のみ。結論禁止・契約作成禁止）
Date: 2026-06-23

本文書はcandidate（EventCandidate/NLCandidate）が「生成」
「比較」「観測」「裁定」の各局面でどの層（Phase7/8/9/10）に
帰属すべきかを、既存契約の記述に基づいて構造化する。結論
（どの層がどの局面を担うべきという確定）は出さない。

## Candidate Lifecycle 4局面 × 既存層の対応表

```
局面    | Phase7        | Phase8         | Phase9          | Phase10
--------|---------------|----------------|-----------------|------------------
生成    | ExplanationBuilder | (該当なし)  | SemanticProjection | Reasoning Node
        | が説明候補を生成    |              | Layer（NotImplemented | （論点B-1〜B-4、
        | （Phase7-A3）       |              | Error固定、Phase9-3A | 未確定・本契約
        | decision_trace構造  |              | で生成境界を契約化） | 不在）
        | 自体はB3/B4で復元   |              |                       |
        | （生成ではなく復元）|              |                       |

比較    | (該当なし)    | (該当なし)     | (該当なし、Projection | Advisor Node
        |               |                | 層は生成のみ・比較は   | （候補比較を
        |               |                | 規定されていない）     | 明記、Phase10-2
        |               |                |                       | 第2章）

観測    | Drift Monitor | Observation Surface | ProjectionLogEntry | Observer Node
        | （C: 意味レベル | （4 View Channel:  | （append-only前提、 | （4 View Channel
        | drift観測）    | trace/cluster/      | Phase9-1第5章）      | を読取専用で
        |               | collision/          |                       | 参照、Phase10-1）
        |               | ruling_view）        |                       |

裁定    | Human Gate    | (該当なし、       | (該当なし、         | (該当なし、
        | （B6/B7:       | Orchestratorは     | Ranking Policyで    | Phase10-0第4章
        | accept/reject/ | ルーティングのみ・  | 「採択するのは        | 三分離により
        | defer/split、  | 裁定権を持たない）  | Projection層ではない」 | Reasoning Node
        | mergeは恒久除外)|                    | と明記、Phase9-3A）  | も裁定不可）
```

## 各局面の構造的観察（結論ではなく整理）

```
生成局面:
    既存実装はPhase7（説明候補生成・既存trace復元）とPhase9
    （EventCandidate/NLCandidate生成、ただし実装は
    NotImplementedError固定）の2箇所に分散している。
    Phase10-3で論点となっている「Reasoning Nodeが新規candidateを
    生成してよいか」（候補B-1）は、この既存分散構造のどちらに
    位置づくのか、あるいは第3の生成点になるのかが未整理のまま
    残っている。

比較局面:
    既存契約でcandidate比較を明記しているのはAdvisor Node
    （Phase10-2第2章「候補比較」）のみであり、Phase7/8/9のいずれ
    にも比較機能の記述は存在しない。Reasoning Nodeが比較を担う場合、
    Advisor Nodeの「候補比較」とどう機能的に区別されるか
    （PHASE10_3_REASONING_PREPARATION_NOTE_v1.md論点A-2参照）が
    未整理。

観測局面:
    Phase7（Drift Monitor）・Phase8（Observation Surface）・
    Phase9（ProjectionLogEntry）・Phase10（Observer Node）の
    4層すべてに観測機能が存在する。これらは互いに統合されておらず
    （Phase8-4第1章「統合・比較・差分表示は提供しない」）、各層が
    独立して観測対象を持つ構造になっている。Reasoning Nodeが
    観測局面に関与する場合、既存4層のいずれかを参照するのか、
    第5の観測点を新設するのかが論点として残る。

裁定局面:
    Phase7（Human Gate）にのみ裁定権が存在し、Phase8/9/10の
    いずれにも裁定権は存在しない。これはPhase10-0第4章
    Reasoning Ownership Ruleの三分離（Reasoning/Adoption/
    Execution）が既存契約全体で一貫して守られていることの
    構造的確認である。Reasoning Nodeが追加されても、この裁定局面
    の唯一性（Human Gateのみ）は既存契約上揺らいでいない。
```

## 未整理のまま残す論点（結論を出さない）

```
論点D-1（生成）: Reasoning Nodeの「生成」がPhase9 Projection層の
    生成と同一の操作なのか、別の操作（既存candidateからの派生・
    拡張・再構成）なのかが構造的に未分離。

論点D-2（比較）: Advisor Nodeの「候補比較」とReasoning Nodeの
    比較行為（仮）が機能的に重複するのか、異なる粒度の比較
    （Advisorは提示のための比較、Reasoningは生成判断のための
    比較、等）なのかが未整理。

論点D-3（観測）: 既存4観測層（Phase7 Drift Monitor/Phase8
    Observation Surface/Phase9 ProjectionLogEntry/Phase10
    Observer Node）とReasoning Nodeの関係性が未整理。
```

## 結論

```
本文書はcandidate lifecycle 4局面（生成/比較/観測/裁定）を
既存層との対応関係として構造化したのみであり、Reasoning Nodeが
どの局面をどう担うべきかについて結論を出していない。
```
