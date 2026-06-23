# Phase10-3 Collision Governance Study v1

Status: STRUCTURING ONLY（調査のみ。採択禁止・契約作成禁止）
Date: 2026-06-23

本文書はReasoning Nodeが「collision生成可能か」「collision増幅
可能か」「collision解消禁止か」について、既存の固定原則（Phase7
Collision Governance、Phase9 Projection禁止事項、Phase10-2
Advisor禁止事項）を確認元として調査する。本文書は採択を行わない。

## 確認元1: Phase7固定原則（Collision Governance, Phase7-B5）

```
原則: 「衝突は解消しない」
分類: structural / semantic / source_collision の3種
権限分離: Layer A（Algorithmic、提案のみ）/ Layer B（System、
          保留のみ）/ Layer C（Human Gate、最終裁定のみ）
絶対禁止4項目: 自動マージ / スコアリング決定 / 最適解生成 /
              collision log圧縮削除（完全禁止）
```

Phase7-B5はcollisionの「解消」を一貫して禁止しているが、
collisionの「生成」自体について明示的な記述は無い。Phase7-B5が
扱うcollisionは既存データ（decision_trace.json/merge_graph.json）
間の構造的不一致から検出されたものであり、Nodeの能動的な行為に
よって新たなcollisionが生まれる場面は想定範囲外にある。

## 確認元2: Projection禁止事項（Phase9-1, Phase9-3A, Phase9-2）

```
Phase9-1絶対禁止: 単一候補への収束禁止、ログ上書き削除禁止
Phase9-3A Collision Policy: 「候補間競合は解消しない」
                            （Phase7-B5の直接継承）
Phase9-2恒久禁止6項目: 自動採択/confidence最大選択/候補削除/
                       candidate merge/Human Gate代行/
                       Runtime直接起動
```

Projection層（SemanticProjectionLayer）がcandidateを生成する
行為そのものは、複数candidateを同時生成することを前提とした
設計（ProjectionResult.candidatesは常にSequence）であり、
これは構造的に「collisionを生み得る生成」を許容している
（生成された複数候補が互いに矛盾しても、それは禁止されていない。
禁止されているのはその矛盾を解消すること）。

## 確認元3: Advisor禁止事項（Phase10-2）

```
Phase10-2第2章禁止: 採択/実行/candidate削除/candidate統合/
                    collision解消/ranking改変
Phase10-2第1章役割4: 「矛盾点の指摘」
                     （指摘は記述であり解消ではないと明記）
```

Advisor Nodeは「矛盾点の指摘」という形でcollisionに関与するが、
これは既存collisionの観測・言及であり、新たなcollisionを生成する
行為ではない（Advisor Nodeはcandidate生成自体が禁止されている
ため、生成起因のcollision増幅は構造的に発生しない）。

## Reasoning Nodeに関する3つの確認事項（調査結果、採択ではない）

```
確認事項1: Reasoning Nodeがcollision生成可能か

    既存3確認元のいずれも「Nodeによるcollision生成」を直接
    禁止する条文を持たない。一方、Phase9層の既存設計（複数
    candidateを同時生成し、矛盾の解消を禁止する構造）が
    「生成行為自体がcollisionを生み得ること」を前提としている
    ことから、Reasoning Nodeが候補を生成する権限を持つ場合
    （PHASE10_3_REASONING_AUTHORITY_MATRIX_v1.md「未確定」項目
    generate_candidate等）、その生成によって新たなcollisionが
    生まれる可能性は構造的に排除されていない。
    ただし、これを「禁止しない」と確定するか「明示的に許可する」
    と確定するかは、本文書では判断しない。

確認事項2: Reasoning Nodeがcollision増幅可能か

    「増幅」（既存collisionを悪化させる、または新規生成により
    既存collisionの数・複雑性を増やす行為）について、既存3確認元
    のいずれにも直接の言及は無い。Phase7-B5の絶対禁止4項目
    （自動マージ/スコアリング決定/最適解生成/collision log
    圧縮削除）はいずれも「collisionを減らす・隠す」方向の禁止であり、
    「collisionを増やす」方向についての制約は既存契約に存在しない。
    これは制度的な空白であり、本文書はこの空白の存在を指摘するに
    留める（埋める判断は行わない）。

確認事項3: Reasoning Nodeがcollision解消禁止であるべきか

    Phase7-B5「衝突は解消しない」、Phase9-3A Collision Policy
    「候補間競合は解消しない」、Phase10-1/10-2双方の
    「Collision解消」禁止事項は、いずれも一貫してNode種別を問わず
    collision解消を禁止する構造になっている。
    PHASE10_3_REASONING_AUTHORITY_MATRIX_v1.mdのObservation
    （観察1）で確認した通り、resolve_collisionはObserver/Advisor
    双方で既に「不可」が確定しており、この一貫性から類推すれば
    Reasoning Nodeにも同様の禁止が及ぶと考えることは可能である。
    しかし「類推可能」と「契約として確定」は異なるため、本文書は
    この禁止をまだ確定事項として記録しない。
```

## 結論

```
本文書はReasoning Nodeのcollision生成可能性・増幅可能性・
解消禁止の3点について、既存3確認元の記述に基づき調査したのみで
あり、いずれも採択していない。

特に「collision増幅の禁止」については既存契約に直接の規定が
存在しない制度的空白が確認された。この空白をどう扱うかは
Phase10-3契約設計時の論点として残る。
```
