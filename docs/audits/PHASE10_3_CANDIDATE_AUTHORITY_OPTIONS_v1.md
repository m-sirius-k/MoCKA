# Phase10-3 Candidate Authority Options v1

Status: OPTIONS STUDY ONLY（並列比較のみ。採択禁止・契約作成禁止）
Date: 2026-06-23

本文書はPHASE10_3_REASONING_PREPARATION_NOTE_v1.md候補B-1〜B-4
（generate_candidate/derive_candidate/expand_candidate/
reconstruct_candidate）について、累積的な4モデル（A〜D）を
並列比較する。いずれも採択しない。

## Model定義

```
Model A: generateのみ
Model B: generate + derive
Model C: generate + derive + expand
Model D: generate + derive + expand + reconstruct
```

## 比較表

```
比較項目        | Model A      | Model B        | Model C          | Model D
------------------|---------------|-----------------|-------------------|------------------
制度整合性        | 最高。       | 中。           | 低。              | 最低。
                  | Phase9層が    | deriveは既存    | expandは        | reconstructは
                  | 既に担う      | candidateを起点  | candidateに      | 複数candidateの
                  | 「生成」と     | とするため、    | メタデータを      | 情報を組み合わせ
                  | 機能的に最も   | Phase9-1の     | 付与する操作で    | るため、Phase9-2
                  | 重複するが、   | 「単一解への    | あり同一性は     | 恒久禁止
                  | 単一操作のみ   | 収束禁止」      | 変えない          | 「candidate merge」
                  | のため境界が   | 原則との抵触    | （PHASE10_3_     | との境界が
                  | 最も単純。     | リスクは低い。  | REASONING_       | 最も不明瞭。
                  |               |                 | PREPARATION_    | mergeと
                  |               |                 | NOTE_v1.md候補   | reconstructが
                  |               |                 | B-3）。          | 同一視されうる
                  |               |                 |                  | リスクが指摘
                  |               |                 |                  | 済み（同ノート
                  |               |                 |                  | 候補B-4）。
collision影響     | 低〜中。      | 中。           | 低。              | 高。
                  | 新規生成のみ  | 派生candidateが | メタデータ付与    | 複数candidateの
                  | であれば      | 既存candidateと | のみであれば     | 組み合わせは
                  | Phase9層の    | 矛盾する場合、  | candidate自体の  | 新たな矛盾を
                  | 既存パターン  | collisionが     | 矛盾構造は       | 生み出す可能性が
                  | （複数候補    | 増える          | 変化しない       | 最も高い
                  | 同時生成）と  | （PHASE10_3_   | （ただしメタ     | （PHASE10_3_
                  | 同型。        | COLLISION_      | データの矛盾は   | COLLISION_
                  |               | GOVERNANCE_     | 別途検討要）。   | GOVERNANCE_
                  |               | STUDY_v1.md     |                  | STUDY_v1.md
                  |               | 確認事項1）。   |                  | 確認事項1の
                  |               |                 |                  | 懸念が最も
                  |               |                 |                  | 顕著）。
Projection影響    | 高。          | 高。           | 中。              | 中〜高。
                  | Phase9        | 派生元が        | 既存candidateの   | 複数candidateの
                  | SemanticProjection | Phase9生成    | 構造（why_       | 出自が異なる
                  | Layerの責務   | candidateの場合 | generated等）に  | 場合、Projection
                  | と直接重複    | Projection層の  | 変更を加える     | 層が保証する
                  | する可能性    | データを入力と  | ため、Phase9-1   | 「候補の出自
                  | が最も高い    | するため        | の出力構造        | 追跡性」が
                  | （Option A    | Projection層との | （Phase9-1第5章）| 失われる可能性。
                  | と同一論点）。| 依存が生じる。  | の整合性が論点。 |
Human Gate影響    | 低〜中。      | 中。           | 低。              | 高。
                  | 生成物が      | 派生履歴の      | メタデータ追加   | 複数candidateの
                  | 単純なほど    | 追跡が必要に    | のみであれば     | 組み合わせ結果は
                  | Human Gateの  | なり、裁定時の  | Human Gate裁定   | Human Gateが
                  | 裁定材料も    | 参照情報量が    | の負荷増加は     | 「何が元の候補で
                  | 単純。        | 増える。        | 最小。          | 何が合成結果か」
                  |               |                 |                  | を区別する負荷が
                  |               |                 |                  | 最も高くなる。
```

## モデル間の累積関係（事実整理）

```
Model A ⊂ Model B ⊂ Model C ⊂ Model D
（各モデルは前のモデルの操作を含み、新たな操作を1つ追加する
構造になっている）
```

```
この累積構造から観察できること（結論ではない）:
    - 制度整合性・collision影響・Human Gate影響はいずれもA→Dの
      順で単調に複雑化する傾向が表中で確認できる。
    - Projection影響はA/Bで高く、Cで一旦下がり、Dで再度上がる
      という非単調な傾向が見られる（生成・派生はProjection層との
      重複が直接的だが、メタデータ付与のみのexpandは独立性が高く、
      reconstructは複数出自の混在により別の形でProjection層との
      整合性問題を生む）。
```

## 結論

```
本文書はModel A〜Dを4観点で並列比較したのみであり、いずれも
採択していない。次工程（Step6 Human Gate Decision Package）で
本文書の論点を集約する。
```
