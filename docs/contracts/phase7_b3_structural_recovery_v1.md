# Phase7-B-3: Structural Recovery Layer Contract v1

Status: DRAFT (Phase7-B-3。read-only構造復元のみ。意味解釈・推論・生成は禁止)
Date: 2026-06-23

本文書はTraceReaderを**Meaning Reconstruction Engineではなく
Structural Recovery Layer**として実データに接続する契約を固定する。
既存の`ExplanationBuilder.TraceReader`（explanation_builder_contract_v1.md）
および`DecisionReplaySystem.DecisionTraceReader`
（decision_replay_system_contract_v1.md）のメソッド署名（`get_trace_path`）
は変更しない。本契約は新規クラス`StructuralTraceReader`を別途追加する。

## 1. データソース（確定・実データ調査結果）

```
canonical/trace/_phase6/decision_trace.json
    形式: { from_cluster_id: [{to, vector_score, gap_seconds,
            diameter_if_merged_seconds, accepted, diameter_limit_hit}, ...], ... }
    件数: 8,259

canonical/trace/_phase5b_v3/merge_graph.json
    形式: [{from, to, vector_score, gap_seconds,
            diameter_if_merged_seconds, accepted}, ...]  (flat edge list)
    件数: 8,259（diameter_limit_hitフィールドを持たない点でdecision_trace.jsonと差異あり）

canonical/trace/_phase6/adapter_enrichment.jsonl
    形式: 1行1event_id: {event_id, canonical_trace_id, cluster_id,
          intent_score, temporal_span, audit_tag}
    件数: 12,922
    注意: このファイル内の"canonical_trace_id"フィールドはcluster_idと
          同値（=クラスタ自身のID）であり、Phase7-A-4契約群が定義した
          「canonical_trace_id=メンバーtrace_id」とは異なる意味で使われて
          いる既存データである。本契約はこの既存フィールド名をそのまま
          読み取るのみで、Phase7-A-4の用語に合わせて改変・再解釈しない
          （データソースの命名は変更不可能な既存事実として扱う）。
```

## 2. 実データに存在しないフィールドの扱い（重要・正直な記録）

指示書が要求する出力構造のうち、以下は実データに対応するフィールドが
**存在しない**。推測・生成で埋めることは「意味解釈」に該当するため
行わない。

| 要求フィールド | 実データの有無 | 本契約の扱い |
|---|---|---|
| `session_id` | 無し | クエリ識別子（呼び出し時に渡されたcluster_id等）をそのまま`session_id`欄に格納する。これは実データのsession概念ではなく、呼び出し識別子のプレースホルダーである旨を出力に含意として記録する（コード上はコメントで明示）。 |
| `trace_chain[].timestamp` | 無し（`temporal_span`は絶対時刻ではなく相対時間文字列） | 常に`null`を返す。 |
| `trace_chain[].intent` | テキストのintentは無し（`intent_score`数値のみ） | `intent_score`の値をそのまま`intent`欄に格納する（数値のまま、テキスト化・意味解釈は行わない）。 |

## 3. 出力構造（確定・指示書通り）

```
{
    session_id: str,              # 呼び出し識別子そのまま(プレースホルダー、2章参照)
    trace_chain: [
        {
            intent: float | None,           # adapter_enrichment.jsonlのintent_scoreそのまま
            canonical_cluster_id: str,       # adapter_enrichment.jsonlのcluster_idそのまま
            timestamp: None,                 # 実データに存在しないため常にnull
        },
        ...
    ],
    merge_links: [
        {
            from_cluster: str,
            to_cluster: str,
            relation_type: "accepted" | "rejected_diameter_limit" | "rejected",
        },
        ...
    ],
}
```

`relation_type`の3値は`accepted`/`diameter_limit_hit`フラグの単純な
ラベル化であり、意味の解釈・推論を含まない（construct logの構造的
書き換えのみ）:

```
accepted=True                          -> "accepted"
accepted=False and diameter_limit_hit  -> "rejected_diameter_limit"
accepted=False (diameter_limit_hit無しまたはFalse) -> "rejected"
```

merge_graph.json由来のedge（`diameter_limit_hit`フィールドを持たない）
は`accepted=False`の場合すべて`"rejected"`として扱う（情報が無い以上、
limit_hitであるとは推測しない）。

## 4. 絶対条件（くろこ指示・確定）

1. **TraceReaderは推論禁止**: 意味解釈・confidence判定・最適経路選択は行わない。生データの列挙のみ。
2. **intentは再評価に使わない**: `intent_score`はルーティング目的の参照値として渡すのみで、本契約内で再計算・補正・正規化は行わない。
3. **merge_graphは新規意味生成禁止**: 既存のmerge試行記録を読み取るだけで、新たなmerge判定・cluster再計算は行わない。
4. **書き込み禁止**: decision_trace.json / merge_graph.json / adapter_enrichment.jsonlへの書き込みは行わない（書き込みメソッドは構造的に存在しない）。

## 5. 検証方針（最小・くろこ指示）

- decision_trace.jsonに該当cluster_idが無い場合: `merge_links`への
  decision_trace由来の追加は単に行われない（エラーにしない）。
- merge_graph.jsonに該当edgeが無い場合: 同様に追加されないだけ（エラーにしない）。
- adapter_enrichment.jsonlに該当cluster_idのevent_id行が1件も無い場合:
  `trace_chain`は空リスト`[]`を返す（nullではなくempty listとする。
  trace_chainは「列」であるため、要素無し=空リストが構造的に正しい）。
- 意味的な不一致（例: 同一cluster_idに矛盾するintent_scoreが複数存在する等）
  はPhase7-B-3では検出・解消しない（Phase7-B-4で扱う、本契約の対象外）。

## 6. 段階フロー

1. **Phase7-B-3（本文書 + StructuralTraceReader実装）**: 完了対象。
2. Phase7-B-4（未着手・要承認）: 履歴競合の解消・意味の揺れの統計化・merge graphの安定化。

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。
