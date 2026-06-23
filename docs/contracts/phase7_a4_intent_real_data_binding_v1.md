# Phase7-A-4-Intent: Real Data Binding Contract v1 (Meaning Input Layer, completion)

Status: DRAFT (Phase7-A-4-Intent。anchor必須の限定スコープ)
Date: 2026-06-23

本文書は[phase7_a4_real_data_binding_v1.md](phase7_a4_real_data_binding_v1.md)
（canonical解決のみ・完了済み）に続き、`find_clusters_by_intent()`の
実データ接続を固定する。これによりMeaning Input Layer（canonical+intent）
が完結する。B層（Decision Replay System・実データ接続）より先に本ステップ
を行う理由: 記憶層を先に現実接続すると意味の保存構造がデータに引っ張られる
リスクがあるため、入力層を完全に閉じて安定性を検証してから先に進む。

## 1. データソース（確定）

```
canonical/trace/_phase5b_v3/embedding_index.json
    形式: { trace_id: { bigram: weight, ... }, ... }
    サイズ: 約20MB（一括読み込み可能）
    用途: 各trace_idの文字bigram重みベクトル（既存ツールが生成した
          静的embedding。本契約では一切変更しない）
```

## 2. 意味圧縮の焦点（設計判断・確定）

intentの実データ接続で最も重要な論点は「どこまで意味を圧縮するか」
である。本v1では以下の限定スコープを採用する。

- **anchor必須**: `anchor_cluster_id`が`None`の場合は`NotImplementedError`
  のままとする（anchor無しのintent単独展開・他clusterへの探索的拡張は
  本v1の対象外。理由: 探索範囲を無限定にすると意味の境界が現実データの
  ノイズに引っ張られるため）。
- **検証のみ、拡張なし**: 本v1のintent_searchは「query textがanchor
  clusterの意味と一致するか」を検証するだけであり、他clusterへの
  拡張的な意味場展開は行わない。一致する場合は`cluster_refs=(anchor_cluster_id,)`、
  一致しない場合は`cluster_refs=()`を返す。
- これは意図的な圧縮判断である: Phase7-A-4-Intentの役割は「入力層を
  閉じる」ことであり、「意味場を広げる」ことではない。意味場の拡張
  （複数cluster探索）は将来の別フェーズ（要承認）に委ねる。

## 3. Query Vector計算とEmbedding再生成の区別（重要・必読）

既存契約群が禁止する「embedding再生成」は、`embedding_index.json`に
**永続化されている既存trace_idのembeddingを書き換える・新規trace_idの
embeddingを追加して永続化する**ことを指す。

本契約が新たに行う「query textの文字bigram化」は、呼び出しごとに
発生する**一時的（ephemeral）な計算**であり、

- `embedding_index.json`への書き込みを行わない
- 既存trace_idのembeddingエントリを変更・追加しない
- 計算結果はメソッド呼び出しのスコープ内でのみ存在し、永続化されない

という条件を満たす限り、絶対禁止の「embedding再生成」には該当しない
（本契約で明示的に区別・許可する）。

## 4. 類似度判定方式

```
query_vector = bigram_vector(text_or_key)          # ephemeral, 文字2-gram頻度
anchor_vector = mean(embedding_index[m] for m in anchor_clusterのmember一覧)
similarity = cosine_similarity(query_vector, anchor_vector)
match = similarity >= INTENT_MATCH_THRESHOLD       # 初期値 0.15（仮置き）
```

- `INTENT_MATCH_THRESHOLD`は運用データが無い段階の仮置きであり、
  Phase7-A-4-Intent運用後に見直す（変更は本文書の更新としてユーザー
  承認を要する）。
- `anchor_vector`はanchor clusterの既存メンバーembeddingの平均であり、
  新規embeddingの生成・永続化ではない（メンバーembedding自体は
  読み取りのみ、呼び出しごとに再計算するが保存しない）。

## 5. 絶対禁止 / 許可

禁止:
- embedding_index.jsonへの書き込み・既存entryの変更
- anchor無しでの探索的intent展開（本v1の対象外）
- 他clusterへの拡張探索（本v1の対象外）

許可:
- embedding_index.jsonの読み取りのみ
- query textのephemeralなbigram化（永続化しない）
- anchor clusterのメンバーembeddingとのコサイン類似度計算（読み取りのみ、
  計算結果は永続化しない）

## 6. 段階フロー

1. Phase7-A-4（canonical解決のみ、完了）
2. **Phase7-A-4-Intent（本文書）**: anchor必須のintent一致検証のみ。完了対象。
3. Phase7-A-4-Intent-Expand（未着手・要承認）: 他clusterへの拡張探索。
4. Phase7-B-3（未着手）: decision_trace.json/merge_graph.jsonへの接続。

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。
