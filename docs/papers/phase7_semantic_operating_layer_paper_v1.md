# MoCKA Phase7: The Semantic Operating Layer

## A Formal Specification of Meaning Generation, Fixation, Audit, and Execution over an Immutable Event Core

Status: INSTITUTIONALIZED (Phase7論文形式テンプレート v1。実データ接続前の制度化文書)
Date: 2026-06-23

本文書は[meaning_query_engine_contract_v1.md](../contracts/meaning_query_engine_contract_v1.md)、
[explanation_builder_contract_v1.md](../contracts/explanation_builder_contract_v1.md)、
[decision_replay_system_contract_v1.md](../contracts/decision_replay_system_contract_v1.md)、
[drift_monitor_contract_v1.md](../contracts/drift_monitor_contract_v1.md) /
[drift_monitor_scoring_v1.md](../contracts/drift_monitor_scoring_v1.md)、
[semantic_execution_layer_contract_v1.md](../contracts/semantic_execution_layer_contract_v1.md)、
[phase7_architecture_seal_v1.svg](../architecture/phase7_architecture_seal_v1.svg)
の内容を学術論文形式に再構成した制度文書である。新規の設計判断は含まない
（「設計」→「仕様」→「制度」への変換のみ）。

---

## Abstract

MoCKAはこれまで、PHI-OS（不変イベントコア）上にcluster生成・dictionary・
Time OS Contractを積み上げる「分析パイプライン」として発展してきた。
Phase7は、この分析パイプラインを「意思決定・説明・再現ができる意味OS」
（Semantic Operating Layer）へ昇格させる。本論文は、Meaning Generation
（A）・Meaning Fixation（B）・Meaning Audit（C）・Semantic Execution（D）
の4層構造、それらを結ぶMeaning Lifecycleの6ステップ実行モデル、および
構造を保護する禁止境界（Prohibited Boundaries）を制度として記述する。
本文書時点では全層がFake実装による実行証明（Phase7-D-2）を完了しており、
実データ接続（PHI-OS/cluster index/decision_trace storeへの具象接続）
は意図的に未着手のまま保持されている。

## 1. Introduction

### 1.1 Motivation

クラスタリングと記録だけでは「なぜこの意味になったか」を説明できない。
MoCKAの制度哲学（`mocka_get_essence`が示す「AIを信じるな、システムで縛れ」
「記録なき作業はMoCKAとして存在しない」）をPhase7に適用すると、意味生成
そのものにも同じ規律が要求される: 生成された意味は記録され、説明可能で、
再現可能で、かつ劣化を検知できなければならない。

### 1.2 Position within MoCKA

```
PHI-OS（immutable event core）
    -> Adapter Layer（既存・非侵入）
    -> Canonical Meaning Layer（Phase5: cluster / dictionary）
    -> Semantic Operating Layer（Phase7、本論文）
```

Phase7はPhase5が確立したcanonical meaning layerの上位に位置し、それを
変更しない。Time OS Contract v1（FROZEN）とも非干渉である。

## 2. Architecture

[phase7_architecture_seal_v1.svg](../architecture/phase7_architecture_seal_v1.svg)
が示す4層構造を以下に形式化する。

| 層 | 名称 | 責務 | 実装 |
|---|---|---|---|
| A | Meaning Generation | canonical座標決定 + intent意味場展開 | `semantic/query_engine/meaning_query_engine.py` |
| B | Meaning Fixation | explanation再構築 + 不変スナップショット化 | `semantic/query_engine/explanation_builder.py`, `decision_replay.py` |
| C | Meaning Audit | 意味レベルdrift検知・記録 | `semantic/query_engine/drift_monitor.py` |
| D | Semantic Execution | A/B/Cを1サイクルとして実行 | `semantic/query_engine/execution_layer.py` |

## 3. Layer A: Meaning Generation

### 3.1 Definition

Meaning Generationは「意味を作る」のではなく「意味を引く」層である。
入力`canonical_trace_id`に対して単独の座標決定（anchor）を行う
`canonical_search`と、そのanchorを基準に意味場（intentに沿った複数
cluster参照）を展開する`intent_search`から成る。

### 3.2 Formal Rule (Dependency Direction)

```
canonical_search: canonical_trace_id -> CanonicalSearchResult        (independent)
intent_search:     (text_or_key, anchor) -> IntentSearchResult        (anchor-dependent)
```

anchorが存在しない状態でのintent単独展開は許可されるが、結果には
`anchor: None`が明示される。canonicalとintentが並列ではなく
「anchor確定 -> 意味場展開」の順序であることが、Phase7-A-1で確定した
唯一の構造的制約である。

## 4. Layer B: Meaning Fixation

### 4.1 Explanation as Meaning Reconstruction

ExplanationはMeaning Reconstruction Layerとして定義される。入力は
`canonical`（必須・主軸）、`intent`（任意・補強）、`trace_path`
（必須）。出力は固定順4要素である:

```
ExplanationResult = (
    why_this_meaning,        # なぜこの意味として確定したか
    activated_structures,    # どの構造が活性化したか（canonical一致分のみ）
    compression_process,     # 意味圧縮の過程（trace_pathの段階列）
    final_judgement,         # 統合された最終判断
)
```

`activated_structures`はintent側のnoise除去規則を持つ:
`intent.cluster_refs`のうち`canonical.cluster_id`と一致するものだけが
採用される。

### 4.2 Decision Replay as Time-Stability

Decision Replay Systemは「意味の時間構造」を担う。`canonical`は
time-stable anchor（baseline 6,563クラスタの範囲内で時間に対して
安定）として扱われ、`explanation`はsnapshotとしてappend-only保存
される。replayは状態の再構築ではなく、決定過程の再現である点で
既存Relay層のReplay（`relay/replay_engine.py`、RelayKernelの状態
再構築）と区別される。

## 5. Layer C: Meaning Audit (Drift Monitor)

### 5.1 Drift Taxonomy

```
Canonical Drift:   canonical_trace_id -> cluster_id の解決結果が変化
Explanation Drift: 同一canonicalのスナップショット間でwhy_this_meaning
                    またはfinal_judgementの趣旨が変化
Intent Drift:      canonical一致分のactivated_structuresが時間変化
```

### 5.2 Consistency Vector and Scoring

```
consistency_vector = (canonical, intent, explanation, replay)
score = sum(weight[drift_type] * count[drift_type])
weight = {canonical_drift: 3, explanation_drift: 2, intent_drift: 1}
```

スコアリングは記録・分類のみを行う。検知された異常への対応は
常にHuman Gate（`HumanGateHook.notify`、v1では空実装）に委ねられ、
自動修復・自動ロールバック・自動cluster再計算は制度として恒久的に
禁止される。

## 6. Layer D: Semantic Execution (Meaning Lifecycle)

### 6.1 The Six-Step Cycle

```
1. canonical_search(canonical_trace_id)              -> A
2. intent_search(text_or_key, anchor)        [任意]   -> A
3. ExplanationBuilder.build(canonical, intent)         -> B
4. DecisionReplaySystem.snapshot_explanation(...)      -> B
5. ConsistencyVector構成 + DriftMonitor.observe(...)
                                       [2回目以降のみ] -> C
6. MeaningCycleResult
```

### 6.2 Halt Semantics

サイクルは2種の停止条件を持ち、いずれも未到達フィールドを`None`の
まま明示する（推測しない）:

```
CYCLE_HALTED:CANONICAL_NOT_FOUND   (Step1でcanonicalが未確定)
CYCLE_HALTED:INSUFFICIENT_TRACE    (Step3でtrace_pathが取得不能)
```

### 6.3 Empirical Validation (Phase7-D-2)

Fake実装による統合テストで以下が確認された:

| サイクル | 入力 | status | drift_score |
|---|---|---|---|
| 1回目 | 正常canonical+intent | OK | None（初回・前回ベクトル無し） |
| 2回目 | 同一canonical+intent | OK | 0（変化なし） |
| 未知canonical | 存在しないcanonical_trace_id | CYCLE_HALTED:CANONICAL_NOT_FOUND | - |
| 空trace | trace_path空 | CYCLE_HALTED:INSUFFICIENT_TRACE | - |

4パターンとも契約通りの結果が得られ、A/B/C/Dの1サイクル完走が
実行レベルで証明された。

## 7. Prohibited Boundaries as Institutional Law

以下はPhase7全層に共通する制度的禁止事項であり、いずれかの層の
実装変更によっても解除されない（変更には「Phase変更レベル」の
ユーザー承認を要する）。

```
第1条（PHI-OS非侵入）   PHI-OSへの書き込みを行わない。
第2条（再計算禁止）     cluster再計算・embedding再生成を行わない。
第3条（trace不可侵）    decision_traceの再実行・改変を行わない。
第4条（Relay非統合）    既存Relay層(relay/replay_*.py)とは統合しない。
                       両者は対象が異なる別概念として永続的に分離される。
第5条（append-only）    既存スナップショットの上書き・削除を行わない。
第6条（自動修復禁止）   drift検知後の自動修復・自動ロールバック・
                       自動cluster再計算を行わない。判断はHuman Gateへ。
第7条（baseline固定）   6,563クラスタのベースラインと6h diameter制約を
                       変更しない。
```

## 8. Future Work

```
Phase7-A-4 / B-3 / C-3 / D-3: 実データ接続
    ClusterReader / TraceReader(2系統) / SnapshotStore /
    HumanGateHookの具象実装。本論文が固定した制度の範囲内でのみ実施する。

Phase8相当: 長期運用フェーズ
    実データ接続後の運用知見をもとに、本論文の重み(weight)・閾値・
    Human Gate通知経路を見直す。見直しは本論文の改訂として行う。
```

## 9. References (Contracts)

```
meaning_query_engine_contract_v1.md       (Phase7-A-1, 2026-06-23)
explanation_builder_contract_v1.md        (Phase7-A-3, 2026-06-23)
decision_replay_system_contract_v1.md     (Phase7-B-1, 2026-06-23)
drift_monitor_contract_v1.md              (Phase7-C-1, 2026-06-23)
drift_monitor_scoring_v1.md               (Phase7-C-2, 2026-06-23)
semantic_execution_layer_contract_v1.md   (Phase7-D-1, 2026-06-23)
phase7_architecture_seal_v1.svg           (Architecture Seal, 2026-06-23)
```

## 改訂ルール

本文書に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。本文書は引用元の各契約文書を上書きするものでは
なく、それらの公式な統合記述（institutional summary）として併存する。
