# Phase10-3 Candidate Authority Matrix v1

Status: MATRIX COMPARISON ONLY（比較のみ。採択禁止・契約作成禁止）
Date: 2026-06-24

本文書はPHASE10_3_CANDIDATE_AUTHORITY_OPTIONS_v1.mdおよび
PHASE10_3_LEAST_AUTHORITY_AUDIT_v1.mdで整理されたModel A〜D
（generate/generate+derive/generate+derive+expand/
generate+derive+expand+reconstruct）を、最小権限原則/Human Gate保護/
Projection衝突率/誤作動時被害範囲の4観点のみで再整理する。
採択は行わない。

## Model定義

```
Model A: generateのみ
Model B: generate + derive
Model C: generate + derive + expand
Model D: generate + derive + expand + reconstruct
```

## 比較マトリクス

```
観点          | Model A        | Model B          | Model C           | Model D
---------------|------------------|--------------------|---------------------|--------------------
最小権限原則   | 最高           | 中                | 低                 | 最低
              | (操作1種のみ)   | (操作2種)         | (操作3種)          | (操作4種)
---------------|------------------|--------------------|---------------------|--------------------
Human Gate保護 | 中〜高         | 中                | 高                 | 低
              | 生成物が単純な  | 派生履歴の追跡が   | メタデータ付与     | 複数candidateの
              | ほど裁定材料も  | 必要になり、裁定   | のみであれば       | 組み合わせ結果は
              | 単純。         | 時の参照情報量が   | candidate自体の    | 出自が混在し、
              |                | 増える。           | 同一性は変えない   | Human Gateが
              |                |                    | ため裁定負荷は     | 「何が元の候補で
              |                |                    | 最小。             | 何が合成結果か」を
              |                |                    |                    | 区別する負荷が
              |                |                    |                    | 最も高い。
---------------|------------------|--------------------|---------------------|--------------------
Projection衝突率| 低〜中         | 中                | 低                 | 高
              | 新規生成のみで  | 派生candidateが    | メタデータ付与の   | 複数candidateの
              | あればPhase9層  | 既存candidateと    | みであれば         | 組み合わせは
              | の既存パターン  | 矛盾する場合、     | candidate自体の    | 新たな矛盾を
              | （複数候補同時  | collisionが増える  | 矛盾構造は変化     | 生み出す可能性が
              | 生成）と同型。  | 。                 | しない。           | 最も高い。
---------------|------------------|--------------------|---------------------|--------------------
誤作動時被害範囲| 低             | 中                | 低〜中             | 高
              | 新規生成の単一  | 派生元candidateの  | メタデータの誤り   | 複数candidateの
              | candidateのみが | 誤りが派生先candidate| のみで、candidate  | 合成結果の誤りは
              | 影響を受ける    | に伝播する範囲。   | 構造自体は不変の   | 「何が元で何が
              | （Phase9層と    |                    | ため被害範囲は     | 合成かの区別」を
              | 同型の被害範囲）。|                   | 限定的。           | 不明瞭化し被害
              |                |                    |                    | 範囲が広がる。
```

## モデル間の累積関係（事実整理）

```
Model A 〈 Model B 〈 Model C 〈 Model D
（各モデルは前のモデルの操作を含み、新たな操作を1つ追加する
構造になっている。PHASE10_3_CANDIDATE_AUTHORITY_OPTIONS_v1.md
で確認済みの累積構造を継承。）
```

## 重要な非整合（観察のみ、結論ではない）

```
PHASE10_3_LEAST_AUTHORITY_AUDIT_v1.mdが指摘する通り、Model Aは
最小権限原則で最高評価でありながら、別の評価軸（Projection侵食
リスク、本文書のProjection衝突率とは定義が異なる軸）では最高
リスクとなる非単調な傾向が存在する。操作数の少なさが必ずしも
全観点での安全性を保証しない。
```

## 注記

本文書はModel A〜Dを4観点で再整理したのみであり、採択・推奨は
行っていない。
