# Phase7-A-4: Real Data Binding Contract v1 (Meaning Input Layer)

Status: DRAFT (Phase7-A-4。canonical解決のみを対象とする限定スコープ)
Date: 2026-06-23

本文書は[meaning_query_engine_contract_v1.md](meaning_query_engine_contract_v1.md)の
`ClusterReader`抽象インターフェースに対する初の具象実データ接続を固定する。
順序: **A-4（本文書）-> B-3 -> C-3 -> D-3**。理由: 入力層（読み取り中心・
影響範囲限定）から開始し、canonical anchorを最初に現実と一致させ、
他層への波及をA->B->C->Dの順に段階確認する。

## 1. データソース（確定）

```
canonical/trace/_phase5b_v3/compressed_canonical_clusters.json
    形式: { cluster_id: [member_trace_id, ...], ... }
    件数: 6,563クラスタ / 12,922メンバー（baseline完全一致を本日確認済み）
    用途: member_trace_id -> cluster_id の逆引き解決

canonical/trace/_phase6/cluster_summary.json
    形式: { cluster_id: {size, time_span, time_span_seconds, stability_score}, ... }
    用途: 本v1では未使用（将来の検証用に読み取り専用で保持する余地のみ残す）
```

両ファイルは既存ツール（`tools/canonical_trace_merger_phase5b_v3.py`等）が
生成した静的JSONであり、本契約はこれらを**書き込み対象にしない**。

## 2. 読み取り境界（確定・最重要）

- 起動時（`RealClusterReader.__init__`）に1回だけJSONを読み込み、
  `member_trace_id -> cluster_id`の逆引きインデックスをin-memoryで
  構築する。以降の`resolve_canonical()`呼び出しはこのin-memory
  インデックスへの参照のみであり、ファイルへの再アクセスは行わない。
- ファイルへの書き込みメソッドは実装しない（構造的に存在しない）。
- JSON読み込みに失敗した場合は例外を発生させ、空インデックスでの
  起動を許可しない（不完全なbaselineでの稼働を防ぐ）。

## 3. スコープ限定（重要・Phase7-A-4はcanonical解決のみ）

`ClusterReader`は2メソッドを持つが、本v1で実データ接続するのは
`resolve_canonical()`のみとする。

```
resolve_canonical(canonical_trace_id) -> cluster_id | None   [本v1で実装]
find_clusters_by_intent(text_or_key, anchor_cluster_id) -> [...]  [対象外・NotImplementedErrorのまま]
```

理由: intentの実データ接続（embedding検索・意味場展開）は
`embedding_index.json`等への接続を要し、canonical解決より影響範囲が
大きい。順序固定（A-4内をさらに分割: canonical解決を先、intent接続は
別途承認を得て後）を維持し、本v1のスコープには含めない。

## 4. 絶対禁止 / 許可（既存契約からの継承）

禁止:
- compressed_canonical_clusters.json / cluster_summary.jsonへの書き込み
- cluster再計算・embedding再生成（embedding_index.jsonへのアクセス自体も本v1では行わない）
- merge_graph.json / decision_trace.jsonへの書き込み（読み取りもPhase7-B-3で扱う）

許可:
- compressed_canonical_clusters.jsonの起動時読み込み + in-memory逆引きインデックス構築
- resolve_canonical()による読み取りのみの解決

## 5. 段階フロー

1. **Phase7-A-4（本文書 + RealClusterReader.resolve_canonical実装）**: 完了対象。
2. Phase7-A-4-intent（未着手・要承認）: `find_clusters_by_intent`の実データ接続。
3. Phase7-B-3（未着手）: decision_trace.json/merge_graph.jsonへの
   `DecisionTraceReader`/`TraceReader`具象接続。
4. Phase7-C-3 / D-3（未着手）: SnapshotStore永続化 + HumanGateHook具象化。

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。
