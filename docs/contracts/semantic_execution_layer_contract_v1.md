# Semantic Execution Layer Contract v1 (Phase7-D-1)

Status: DRAFT (Phase7-D-1。コードゼロ。最小スケルトンはユーザー承認後)
Date: 2026-06-23

本文書はPhase7-D（Semantic Execution Layer）の外部契約を固定する。
既存4契約（[meaning_query_engine_contract_v1.md](meaning_query_engine_contract_v1.md)、
[explanation_builder_contract_v1.md](explanation_builder_contract_v1.md)、
[decision_replay_system_contract_v1.md](decision_replay_system_contract_v1.md)、
[drift_monitor_contract_v1.md](drift_monitor_contract_v1.md) /
[drift_monitor_scoring_v1.md](drift_monitor_scoring_v1.md)）が定義した
クラス・メソッド署名はいずれも変更しない。本契約は既存4層を
**呼び出す順序だけ**を定義する統合層である。

## 0. 位置づけ

```
[完了] A: 意味生成（Meaning Query Engine）
[完了] B: 意味固定（Explanation Builder / Decision Replay System）
[完了] C: 意味監査（Drift Monitor）
[本契約] D: 意味実行（Semantic Execution Layer）
```

A/B/Cは個別に静的完成している（=単体で呼べる）が、まだ「流れていない」
（=1サイクルとして連結された実行経路が定義されていない）。本契約は
その流れを定義する。新しい意味判断ロジックは追加しない
（既存4層が確定した結果を順番に受け渡すだけ）。

## 1. Meaning Lifecycle（1サイクルの定義）

1回の意味処理サイクルを以下の固定順で定義する。

```
1. canonical_search(canonical_trace_id)
   -> CanonicalSearchResult                          [A: Meaning Query Engine]

2. intent_search(text_or_key, anchor=canonical_result)
   -> IntentSearchResult                              [A: Meaning Query Engine]
   (任意。intentが提供されない場合は2をスキップしanchor=Noneのまま3へ)

3. ExplanationBuilder.build(canonical_result, trace_path=None, intent=intent_result)
   -> ExplanationResult                               [B: Explanation Builder]
   (canonical_result.found=Falseの場合はサイクルを CYCLE_HALTED:CANONICAL_NOT_FOUND
    として停止し、4以降は実行しない)

4. DecisionReplaySystem.snapshot_explanation(canonical_trace_id, explanation_result)
   -> snapshot_id                                     [B: Decision Replay System]

5. ConsistencyVectorを構成(canonical_result, explanation_result, intent_result)
   -> 前回のConsistencyVectorが存在する場合のみ:
      DriftMonitor.observe(previous, current, detected_at)
   -> score                                            [C: Drift Monitor]
   (前回ベクトルが無い初回サイクルでは6相当の比較は行わず、今回ベクトルを
    次回比較用に保持するだけで終える)

6. サイクル結果(MeaningCycleResult)を返す。
```

## 2. 順序契約（確定・変更不可）

- 1（canonical_search）は常に最初に実行する。2-6はすべて1の結果に依存する
  （契約v1の「canonical=anchor」原則をサイクル順序として再確認する）。
- 3（explanation生成）の前に2（intent_search）を完了させる
  （explanation_builderのintent統合規則を満たすため）。
- 4（snapshot保存）は3の直後、5（drift比較）より前に行う
  （driftが「保存済みのexplanation」を比較対象にするため、未保存の
  explanationをdrift比較に使わない）。
- 5（drift比較）は必ず4の後。比較対象は最新スナップショットと
  直前サイクルのスナップショットであり、本契約のサイクル実行自体が
  比較に新しい計算を持ち込むことはない（既存ConsistencyEvaluatorの
  読み取り比較のみを呼ぶ）。

## 3. MeaningCycleResult（出力）

```
MeaningCycleResult = {
    canonical_trace_id: str,
    status: "OK" | "CYCLE_HALTED:CANONICAL_NOT_FOUND" | "CYCLE_HALTED:INSUFFICIENT_TRACE",
    canonical: CanonicalSearchResult,
    intent: IntentSearchResult | None,
    explanation: ExplanationResult | None,
    snapshot_id: str | None,
    drift_score: int | None,        # 前回ベクトルが無い初回サイクルではNone
}
```

- statusが`CYCLE_HALTED:*`の場合、それ以降のフィールドは取得済みの
  ものまでのみ埋め、未到達のフィールドは`None`のままにする
  （省略せず明示する。explanation_builder_contract_v1.mdの
  「算出不能時も空値で明示する」原則を継承）。

## 4. 絶対禁止 / 許可（既存4契約からの継承・再確認）

禁止:
- PHI-OSへの書き込み
- cluster再計算・embedding再生成
- decision_traceの改変
- 既存スナップショットの上書き・削除
- 自動修復・自動ロールバック・自動cluster再計算
- 既存4層（Meaning Query Engine / Explanation Builder /
  Decision Replay System / Drift Monitor）のメソッド署名変更
- 既存Relay層（relay/replay_*.py）・既存Time API
  （phi_os/api/time_api.py）への変更・統合

許可:
- 既存4層の既存メソッドを1.の固定順で呼び出すこと
- MeaningCycleResultの構成（新規dataclassの追加のみ、既存結果の改変なし）
- 直前サイクルのConsistencyVectorを次回比較用に保持すること
  （実データ永続化ではなく、実行層内でのin-memory保持を想定。
  永続化方式はPhase7-D-3以降で別途契約化する）

## 5. 段階実装フロー

1. **Phase7-D-1（本文書）**: 契約設計のみ。コードゼロ。
2. Phase7-D-2（未着手・要承認）: `semantic/query_engine/execution_layer.py`
   （`MeaningCycleExecutor`想定）の最小スケルトン。各層の呼び出しは
   既存の抽象Reader/Store/Hookに対して行い、実データ接続は含めない
   （Fake実装でのサイクル動作確認のみ）。
3. Phase7-D-3（未着手）: 実データ接続（ClusterReader/TraceReader/
   SnapshotStore/HumanGateHookの具象実装）。本契約完了後に
   Phase7-A-4/B-3/C-3を統合する形で着手する。

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。既存4契約のいずれも、本契約によって変更されない。
