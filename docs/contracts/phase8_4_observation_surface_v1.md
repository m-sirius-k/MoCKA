# Phase8-4: Observation Surface Contract v1

Status: DRAFT (Phase8-4。表示のみ。統合・差分・正規化は恒久的に禁止)
Date: 2026-06-23

本文書はPhase8-2（[phase8_2_runtime_bridge_v1.md](phase8_2_runtime_bridge_v1.md)）
が確立した非統合保証（trace_id空間とcluster_id空間は別世界として
固定される）を壊さない形で、Observation Surfaceを定義する。
Observation SurfaceはUIではなく**「分断された意味空間を観測可能に
するだけの層」**である。

## 0. 役割定義（確定）

```
誤解: 理解させるUI
正解: 理解できないまま見えるUI
```

```
❌ しないこと: 解釈 / 比較 / 統合 / 正規化
⭕ すること:   表示 / 分離可視化 / 状態そのまま出す
```

## 1. View Channels（完全分離・4種）

```
trace_view      - Phase7-A4 (RealClusterReader)のcanonical解決結果のみ
cluster_view    - Phase7-B3 (StructuralTraceReader)のrecover_structure結果のみ
collision_view  - Phase7-B7 (CollisionView)のそのまま
ruling_view     - Phase7-B6 (HumanGateRulingStore)の履歴のみ
```

4チャネルは互いに参照しない。同一identifierであっても、
trace_viewとcluster_viewを並べて比較する機能・差分計算・統一表示は
**提供しない**（提供すること自体がPhase8-2の非統合保証を破壊するため）。

## 2. Read-only Snapshot原則

- 各viewは既存reader/store/recordをそのまま読み取って返すだけである。
- 派生データ（集計・要約・スコア化）の生成は禁止する。
- 再計算（cluster再計算・embedding再生成等、既存契約群の絶対禁止を継続）は禁止する。

## 3. Event Feed Mirror

- Phase8-3 `ExecutionOrchestrator.process()`の出力（`OrchestrationResult`）
  をそのまま保持・返す。
- 加工・並び替え・フィルタリングは行わない（受信順のままミラーする）。

## 4. 絶対禁止 / 許可

禁止:
- trace_viewとcluster_viewの統合表示・比較表示・差分表示
- 正規化表示・統一ビューの生成
- 派生データ・要約・スコア化の生成
- Orchestrator出力の加工・並び替え・フィルタリング
- 再計算・推論・補正

許可:
- 4 View Channelsそれぞれの読み取り専用snapshot取得
- Event Feed Mirrorの受信順保持・取得

## 5. HABの構造（本契約完了時点での全体像）

```
Runtime Bridge (8-2)      -> 世界の分割を固定
Execution Orchestrator (8-3) -> 意味の流れを固定
Observation Surface (8-4)  -> 分断のまま可視化
```

本契約の完了により、HAB Runtime Integration Layer（Phase8-1〜8-4）の
外側構造が完成する。

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。第1章のView Channels分離は他のいかなる変更からも
独立して維持される。
