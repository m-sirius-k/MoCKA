# Phase7-B-4: Order Normalization Contract v1

Status: DRAFT (Phase7-B-4。整列+衝突検知のみ。衝突の自動解消は禁止)
Date: 2026-06-23

本文書はPhase7-B-3（[phase7_b3_structural_recovery_v1.md](phase7_b3_structural_recovery_v1.md)）
で発見した「実データにsession_id/timestamp/textのintentが存在しない」
という構造的事実を受けて、Phase7-B-4を「履歴の安定化」ではなく
**「非時間的グラフの整列（Order Normalization）」**として再定義する。
既存`StructuralTraceReader`のメソッド・出力構造は変更しない。本契約は
その上位ラッパー`OrderNormalizer`を新規追加する。

## 0. 構造的事実の確認（B-3からの継承）

```
session_id  -> 実体が存在しない（クエリ識別子のプレースホルダー）
timestamp   -> 実データに存在しない（生成禁止を継続）
intent      -> intent_score（数値）のみ、テキストは存在しない
```

このシステムは「時間を持たない意味ネットワーク」である。Phase7-B-4は
この事実を前提に再設計する。

## 1. Pseudo-Temporal Layer（契約・実装ではない）

```
temporal_span / gap_seconds  -> 時間ではなく「順序キー(order_key)」として扱う
session_id                   -> 局所グループID（クラスタリングキー）としてのみ使用
timestamp                    -> 生成しない（禁止継続）
```

`decision_trace.json`/`merge_graph.json`が持つ`gap_seconds`は、本契約
において絶対時間量としては解釈しない。同一from_clusterから複数の
merge試行を相対的に並べる**順序キー**としてのみ使用する。

## 2. 競合定義の再定義（重要）

Phase7-B-3の検証で、同一`(from_cluster, to_cluster)`組に対して
`decision_trace.json`由来と`merge_graph.json`由来の2レコードが異なる
`relation_type`を報告するケースが実際に観測された
（例: 同一edgeに対し`rejected_diameter_limit`と`rejected`が両方
出力される。原因はmerge_graph.jsonが`diameter_limit_hit`フィールドを
持たないこと）。

これを**「構造的重複」ではなく「順序衝突（order collision）」**として
再定義する: 同一edgeに対し複数ソースの構造が一致しない状態。

```
order collision = 同一(from_cluster, to_cluster)に対し、
                  decision_trace.json由来とmerge_graph.json由来の
                  relation_typeが一致しない
```

## 3. OrderNormalizerの責務

1. **整列（normalize）**: `StructuralTraceReader`が読み込み済みの
   `decision_trace`/`merge_graph`indexを参照し（追加ファイルI/Oなし）、
   同一from_clusterのmerge試行をorder_key（`gap_seconds`）昇順に並べる。
2. **衝突検知（detect conflicts）**: 同一edgeに対するrelation_type不一致
   を検出し、`OrderCollision`として記録する。
3. **解消しない**: 検知した衝突をどちらが正しいか判定・自動解消する
   ことは行わない（意味判断に該当するため）。Drift Monitor契約が
   確立した「記録のみ・自動修復なし・Human Gateへ」の原則を継承する。

## 4. 出力構造

```
{
    session_id: str,                     # 契約2章継承(クエリ識別子そのまま)
    ordered_merge_links: [
        {from_cluster, to_cluster, relation_type, order_key, source},
        ...                               # order_key(gap_seconds)昇順
    ],
    collisions: [
        {from_cluster, to_cluster, relation_types: [...], sources: [...]},
        ...
    ],
}
```

`source`は`"decision_trace"`または`"merge_graph"`のいずれか（データの
出自を明示するだけで、優劣判定ではない）。

## 5. 絶対禁止 / 許可

禁止:
- timestamp・絶対時刻の生成（gap_secondsを時間として解釈すること自体も禁止）
- 衝突（collision）の自動解消・どちらが正しいかの判定
- session_idを実体として意味的に復元すること（クラスタリングキー以外の用途禁止）
- decision_trace.json / merge_graph.json / adapter_enrichment.jsonlへの書き込み
- 既存StructuralTraceReaderのメソッド・出力構造の変更

許可:
- 既存reader内のin-memory indexの参照（追加ファイルI/Oなし）
- order_key（gap_seconds）によるソート（整列のみ、新規計算なし）
- 衝突の検知・記録（解消はしない）

## 6. 段階フロー

1. **Phase7-B-4（本文書 + OrderNormalizer実装）**: 完了対象。
2. Phase7-B-5（未着手・要承認）: 衝突解消ポリシーの設計（Human Gateへの
   委譲経路を含む。Drift Monitor契約のHumanGateHookとの接続も検討）。

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。
