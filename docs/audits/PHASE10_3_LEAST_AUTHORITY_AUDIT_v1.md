# Phase10-3 Least Authority Audit v1

Status: COMPARATIVE ANALYSIS ONLY（比較のみ。推奨禁止・採択禁止・
契約作成禁止）
Date: 2026-06-23

本文書はPHASE10_3_CANDIDATE_AUTHORITY_OPTIONS_v1.mdのModel A〜D
について、最小権限/collisionリスク/Projection侵食リスク/
Human Gate侵食リスクの4評価軸で比較する。いずれのModelも
推奨しない。

## 評価軸の定義

```
最小権限:
    付与される操作の数・範囲。操作が少ないほど「最小権限」の
    度合いが高いと評価する（権限の質的な妥当性は評価しない、
    数量的な範囲のみを評価する）。

collisionリスク:
    PHASE10_3_COLLISION_GOVERNANCE_STUDY_v1.md・PHASE10_3_
    COLLISION_AMPLIFICATION_AUDIT_v1.mdで整理した「collision
    増幅の制度的空白」が、各Modelの操作によってどの程度
    実際に問題化しうるかを評価する。

Projection侵食リスク:
    Phase9 SemanticProjectionLayer（Phase9-1〜9-3A）の既存責務
    （候補生成）と機能的に重複・侵食する度合いを評価する。

Human Gate侵食リスク:
    Phase10-0第4章三分離原則（Reasoning/Adoption/Execution）が
    形式的に維持されていても、Human Gateの実質的な裁定負荷・
    裁定材料の複雑化を通じて裁定機能が事実上侵食される度合いを
    評価する。
```

## 比較表

```
評価軸              | Model A    | Model B      | Model C        | Model D
                       (generate)  (+derive)     (+expand)       (+reconstruct)
----------------------|-------------|---------------|-----------------|------------------
最小権限              | 最高        | 高            | 中             | 最低
                      | （単一操作） | （2操作）     | （3操作）       | （4操作、
                      |             |               |                 | merge禁止との
                      |             |               |                 | 境界も不明瞭）

collisionリスク       | 中          | 高            | 低              | 最高
                      | （新規生成   | （派生先と     | （メタデータ    | （複数candidate
                      | のみ、Phase9 | 既存candidate  | 付与のみで       | の組み合わせが
                      | 既存パターン | 間の矛盾が     | candidate自体の  | 最も新規矛盾を
                      | と同型）     | 増える可能性）  | 構造は不変）     | 生む構造）

Projection侵食リスク  | 最高        | 高            | 中              | 中〜高
                      | （Phase9層   | （派生元が     | （既存candidate  | （複数出自の
                      | の責務と     | Phase9生成物   | の構造への変更   | candidateが
                      | 直接重複の   | の場合         | のみ、構造自体   | 混在する場合、
                      | 可能性が     | Projection層    | は不変）        | Projection層の
                      | 最も高い）   | との依存が     |                 | 「出自追跡性」
                      |             | 生じる）       |                 | 保証が失われる
                      |             |               |                 | 可能性）

Human Gate侵食リスク  | 低〜中      | 中            | 低              | 最高
                      | （生成物が   | （派生履歴の   | （メタデータ    | （複数candidateの
                      | 単純なほど   | 追跡が必要に   | 追加のみで       | 組み合わせ結果は
                      | 裁定材料も   | なり参照情報量 | 裁定負荷増加は   | Human Gateが
                      | 単純）       | が増える）     | 最小）           | 「元の候補と
                      |             |               |                 | 合成結果」を
                      |             |               |                 | 区別する負荷が
                      |             |               |                 | 最大）
```

## 軸間の非整合パターン（観察、優劣判断ではない）

```
観察1: 最小権限とProjection侵食リスクは必ずしも同方向に変化しない。
    Model Aは最小権限（最高）でありながらProjection侵食リスクも
    最高という組み合わせになっている。これは「操作数が少ない」
    ことと「既存層との機能重複が小さい」ことが別の評価軸である
    ことを示す。Model Aの唯一の操作（generate）がPhase9層の
    既存責務と最も直接的に重複するため、操作数の少なさが
    侵食リスクの低さを保証しない。

観察2: Model C（expand）は4Modelの中で唯一、collisionリスク・
    Projection侵食リスク・Human Gate侵食リスクの3軸すべてで
    「中」以下（低〜中）の評価になっている。これはexpandが
    既存candidateの同一性を変えない操作（メタデータ付与のみ）
    という性質によるものである。一方、最小権限の観点では
    Model Bより劣る（3操作 vs 2操作）。

観察3: Model Dは4評価軸のうち3軸（最小権限・collisionリスク・
    Human Gate侵食リスク）で最も厳しい評価（最低/最高リスク）
    になっている。Projection侵食リスクのみ「中〜高」とDより
    Model Aの方が高い評価になっており、4軸すべてでModel Dが
    最も厳しいわけではない。
```

## 結論

```
本文書はModel A〜Dを4評価軸で比較したのみであり、いずれの
Modelも推奨していない。観察1〜3は評価軸間の構造的な非整合
パターンの指摘であり、優劣の結論ではない。次工程（Step6
Decision Readiness Report）で本文書を含む分析結果を集約する。
```
