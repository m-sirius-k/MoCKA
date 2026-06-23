# Phase9-3A: Projection Strategy Contract v1

Status: DRAFT (Phase9-3A。契約先行。コードゼロ。実装はPhase9-3B以降)
Date: 2026-06-23

本文書はPhase9-1（Semantic Projection Layer Contract v1）およびPhase9-2
（SemanticProjectionLayer最小スケルトン、`semantic/query_engine/
semantic_projection_layer.py`）の上に、候補生成（candidate generation）
そのものの境界を固定する。Phase9-2で確定した型構造
（`ProjectionResult.candidates`は常にSequence、`best_candidate`等の
単一解フィールドは存在しない）、および同ファイル冒頭の恒久禁止6項目
（自動採択/confidence最大選択/候補削除/candidate merge/Human Gate
代行/Runtime直接起動）は本契約においても無条件で継続する。

## 0. 位置づけ

```
Phase9-1: 投影とは何か（契約）
Phase9-2: 投影の構造（スケルトン・コードゼロ）
Phase9-3A: 候補生成とは何か（本契約）
Phase9-3B: Intent Projection（最小候補生成器・実装）
Phase9-3C: Explanation Projection（実装）
Phase9-3D: Hybrid Projection（実装）
```

Phase9-2までは「構造」の話だった。Phase9-3から初めて「意味の生成
方法」の話になる。ここで契約を飛ばして実装に入ると、将来の実装者が
「候補生成→ランキング→上位1件採択」を自然に書き始める危険がある。
これはPhase7-B5（Collision Governance）が確立した「衝突は解消しない」
原則と衝突する。したがって本契約で固定すべきは、アルゴリズムの中身
ではなく「候補生成とは何か」という境界である。

## 1. Purpose（確定）

Projectionは裁定器ではない。役割は以下の2方向のみ。

```
自然言語 -> 候補群（EventCandidateのSequence）
イベント -> 説明候補群（NLCandidateのSequence）
```

候補生成器（candidate generator）は「正解を1つ決める装置」ではなく
「可能性の集合を提示する装置」である。この区別がPhase9-3全体の
判断基準になる。

## 2. Candidate Generation Sources（確定）

候補源を3つに分類し、それぞれの実装範囲を固定する。

```
Source-A: Intent Path
    text -> RealClusterReader.find_clusters_by_intent() -> candidate群
    （Phase7-A4-Intentで実データ接続済み。最も安全。）

Source-B: Explanation Path
    text -> ExplanationResult（Phase7-A3）の既存フィールド参照 -> candidate群
    （説明可能性が高い。Phase9-1で読み取り専用参照として既に確定済み。）

Source-C: Hybrid Path
    Intent + Explanation + Namespace（Phase8-2のNamespaceRegistry）の複合
    （MoCKA思想に最も近いが、複数経路生成のため評価が最も複雑。
      Source-A/Bがそれぞれ独立に動作確認できるまで着手しない。）
```

進行順序はA→B→Hybridに固定する（Phase9-3B→9-3C→9-3D）。理由は
Source-Aが既に実データ接続済みであり、単独で評価可能な最小単位
だからである。Hybridを先に実装すると、投影層そのものの評価が
困難になる。

## 3. Collision Policy（最重要・確定）

```
候補間競合は解消しない
```

- Source-A/B/Cいずれから生成された候補も、互いに矛盾・重複・
  スコア差があっても、その場で解消・統合・削除してはならない。
- これはPhase7-B5「衝突は解消しない」、Phase9-1「単一解を作らず、
  複数候補を保持したまま流す」の直接継承である。Phase9-3はこの
  原則をアルゴリズム実装の中で破ってはならない。

## 4. Ranking Policy（最重要・確定）

```
許可:
    score / confidence / source_count の付与
    （候補に補助情報を付けることは許容する）

禁止:
    top-1選択
    winner選択
    自動採択
    （スコアに基づいて候補群を1件に絞り込む操作は一切禁止）
```

スコアは「候補を理解する助け」としてのみ存在し、「候補を選別する
権限」を持たない。スコアの使い道を決めるのはHuman Gate（Phase7-B6/
B7）であり、Projection層ではない。

## 5. Explainability（確定・推奨事項）

```
全CandidateにWhy_generatedを持たせる
```

- 各候補（EventCandidate/NLCandidate）に、どのSourceから・どの
  入力から生成されたかを示す`why_generated`相当の情報を持たせる
  ことを推奨する。
- 理由: 将来の監査（Drift Monitor・Human Gate）において「なぜこの
  候補が出たのか」を追跡可能にするため。これはPhase9-2監査で評価
  された「禁止事項のコード近接配置」と同じ思想であり、説明可能性
  を後付けではなく生成時点で確保する。
- 必須フィールドの確定はPhase9-3Bの実装時に行う（本契約では方向性
  のみ固定）。

## 6. 既存コンポーネントとの関係（変更禁止・確定）

本契約はPhase9-2のクラス・型定義（`EventCandidate`/`NLCandidate`/
`ProjectionResult`/`SemanticProjectionLayer`の2メソッドシグネチャ）
を変更しない。Phase9-3B以降は`SemanticProjectionLayer`の
`NotImplementedError`を、本契約の境界内でのみ実装に置き換える。

以下は引き続き読み取り専用参照のみであり、内部実装・閾値には
一切手を入れない。

```
RealClusterReader.find_clusters_by_intent()（Phase7-A4-Intent）
ExplanationResult（Phase7-A3）
NamespaceRegistry（Phase8-2、Source-Cでのみ参照）
```

## 7. 段階フロー（確定）

```
Phase9-3A（本文書）: Projection Strategy Contract。コードゼロ。
Phase9-3B（未着手）: Source-A（Intent Projection）の最小候補生成器実装。
Phase9-3C（未着手）: Source-B（Explanation Projection）の実装。
Phase9-3D（未着手）: Source-C（Hybrid Projection）の実装。
```

各段階は前段階の動作確認（Fake/実データでのテスト）完了後にのみ
着手する。Phase9-2までの段階実装ルール（1ステップずつ確認してから
次へ進む）を継続する。

## 8. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、
ユーザーの明示的承認を要する。第3章（Collision Policy）・第4章
（Ranking Policy）は他のいかなる変更からも独立して維持される。
