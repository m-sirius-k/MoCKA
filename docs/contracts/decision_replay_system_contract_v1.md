# Decision Replay System Contract v1 (Phase7-B-1)

Status: DRAFT (Phase7-B-1。コードゼロ。最小スケルトンはユーザー承認後)
Date: 2026-06-23

本文書はPhase7-B（Decision Replay System）の外部契約を固定する。
Phase7-A（[meaning_query_engine_contract_v1.md](meaning_query_engine_contract_v1.md)、
[explanation_builder_contract_v1.md](explanation_builder_contract_v1.md)）と
Time OS Contract v1（FROZEN）はいずれも本文書によって変更されない。

## 0. 移行の本質

Phase7-Aは「意味生成」（純粋モデル層: canonical/intent/explanationの
意味空間）を確立した。Phase7-Bはこれを「意味の時間構造」へ移行する。

```
意味生成（Phase7-A・確立済み） -> 意味の時間構造（Phase7-B）
```

現実データへの接続（Phase7-A-4）より先にPhase7-Bを行う理由:
意味空間が安定した直後にデータへ降りると歪みやすい。再現性
（一度作った意味を再構成できること）こそが「意味OS」としての
完成条件であり、データ接続より優先する。

## 1. 重要な用語整理（混同防止・必読）

MoCKAには既に「Replay」という語を使う層が存在する
（`relay/replay_engine.py` / `relay/replay_engine_v2.py` /
`relay/replay_router.py`、Phase4/4.5、Time OS Contract v1の
`POST /time/replay`）。これと本契約のDecision Replay Systemは
**対象が異なる別概念**であり、両者は統合しない。

| | 既存Replay（Relay層） | Decision Replay System（Phase7-B） |
|---|---|---|
| 対象 | RelayKernelの状態（state/queue/snapshot） | 意味生成の決定過程（canonical/intent/explanationが確定するまでの経緯） |
| 再構築するもの | kernel.state（event_logからのfinal_state） | decision_traceのreasoning（なぜこの意味に至ったか） |
| 依存層 | Event Log / Snapshot / Queue（Layer A構造契約） | Meaning Query Engine（Phase7-A） |
| 契約 | Time OS Contract v1（FROZEN） | 本文書 |

本契約内で単に「Replay」と書く場合は常にDecision Replay System
（意味生成過程の再現）を指す。Relay層のReplayと呼ぶ場合は必ず
「Relay Replay」と明示する。

## 2. 初動の3要素（確定）

### 2.1 decision_trace -> replayable trace model
- `explanation_builder_contract_v1.md`が定義した`trace_path`
  （TraceReader.get_trace_path()が返す経路）を、単発の説明生成入力
  としてだけでなく「再実行可能なモデル」として扱う。
- replayable trace modelは経路（ステップ列）+各ステップの入力スナップ
  ショット（2.2参照）から成る。trace_path自体は読み取りのみで
  改変しない。

### 2.2 explanation -> snapshot化
- `ExplanationResult`（why_this_meaning/activated_structures/
  compression_process/final_judgement）を、生成時点で固定された
  スナップショットとして保存可能にする。
- スナップショットは生成後不変（append-only、上書き禁止）。
  再生成は新規スナップショットとして追加する（既存スナップショット
  の置換は禁止）。

### 2.3 canonical -> time-stable anchor
- `CanonicalSearchResult`を「時間に対して安定した参照点」として
  扱う。同一`canonical_trace_id`に対する`cluster_id`解決結果は、
  baseline（6,563クラスタ固定）の範囲内では時間が経過しても
  変化しない前提を契約として置く。
- 変化が観測された場合はPhase7-C（Drift Monitor）の検知対象であり、
  本契約の対象外（Drift Monitorに委譲）。

## 3. 提供機能（Phase7-B-2以降で実装予定・本文書では契約のみ）

### 3.1 replay_decision(canonical_trace_id)
- canonical anchorを起点に、explanation生成に至ったtrace_pathを
  再実行可能な形で返す。
- 「再実行」とは新しい決定を行うことではなく、既存trace_pathに
  沿って既存の中間状態を再構成すること（読み取りのみ、決定の
  改変なし）。

### 3.2 snapshot_explanation(explanation_result)
- 既存のExplanationResultを不変スナップショットとして登録する。
- 同一canonicalに対する複数スナップショットは時系列で保持し、
  最新を上書きしない。

### 3.3 compare_snapshots(canonical_trace_id, snapshot_id_a, snapshot_id_b)
- 同一canonicalに対する2時点のスナップショットを比較し、差分を
  返す（Drift Monitorの前段データとして利用可能、Phase7-Cで接続）。

## 4. 絶対禁止 / 許可

禁止:
- PHI-OSへの書き込み
- cluster再計算・embedding再生成
- decision_traceの改変（再現はするが変更はしない）
- 既存スナップショットの上書き・削除
- 既存Relay Replay層（relay/replay_engine.py等）への変更・統合

許可:
- 既存trace_path・既存ExplanationResult・既存canonical結果の読み取り
- スナップショットの新規追加（append-only）
- スナップショット間の比較（読み取りのみ）

## 5. 段階実装フロー

1. **Phase7-B-1（本文書）**: 契約設計のみ。コードゼロ。
2. Phase7-B-2（未着手・要承認）: replayable trace model + snapshot
   の最小スケルトン（`semantic/query_engine/decision_replay.py`想定）。
3. Phase7-B-3（未着手）: compare_snapshots実装。Phase7-C
   （Drift Monitor）の前段として接続。

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。既存Time OS Contract v1・Meaning Query Engine
Contract v1・Explanation Builder Contract v1のいずれも、本契約に
よって変更されない。
