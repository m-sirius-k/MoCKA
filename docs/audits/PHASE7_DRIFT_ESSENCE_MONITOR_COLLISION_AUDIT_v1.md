# Phase7 Drift Monitor / Essence / Monitor系 機能重複統合監査 v1

Status: COLLISION AUDIT ONLY（既存3系統の機能衝突整理のみ。
新規設計禁止・命名禁止・Reasoning禁止）
Date: 2026-06-24

本文書はPHASE10_3_RESONANCE_NODE_REDEFINITION_v1.mdが指摘した
「Drift/Essence系の既存重複」を、実体ファイルの確認に基づき整理
する。新たな主体の設計・命名・Reasoning概念の適用は行わない。
既存3系統の機能衝突の事実整理のみを行う。

## 0. 監査範囲の確定（事実確認）

```
本文書が対象とする3系統と、その実体ファイル:

1. Drift Monitor（Phase7-C）
   - semantic/query_engine/drift_monitor.py
   - docs/contracts/drift_monitor_contract_v1.md
   - docs/contracts/drift_monitor_scoring_v1.md

2. Essence pipeline
   - interface/essence_classifier.py（分類）
   - interface/essence_extractor.py（抽出）
   - interface/essence_condenser.py（濃縮）
   - interface/essence_pipeline.py
   - interface/essence_auto_updater.py（v4、5分間隔自動更新）
   - interface/essence_to_share.py
   - mocka_v3_eval/essence_to_packet.py
   - interface/lever_essence.json（出力先）

3. Monitor系（名称的に最も近い既存実装）
   - relay/replay_audit.py（Phase4.5、状態レベルdrift検知+Audit
     Log記録）
   - interface/health_check.py（TIC Layer0）
   - interface/tech_watcher.py（TIC Layer1 v3.0、意味差分検知）
```

```
監査範囲外として記録した付随発見（本文書では分析しない）:

grep調査により、上記3系統とは別に以下のモジュールが
「drift」「monitor」「audit」を名称に含むことを確認した:
core_kernel/governance/intelligence/drift_interpreter.py、
core_kernel/governance/self_verification/traceability/
drift_detection.py、mocka3/drift_engine/drift_engine.py、
production_observability/drift_detector.py、
production_observability/system_health_monitor.py、
self_audit/audit_engine.py 等。

これらは現行Phase5〜10進行記録（project memory）に記載が無く、
本文書の対象に含めるかどうかの判定自体が未解決事項である
（6章に記録）。
```

## 1. 各系統の責務（事実確認のみ）

### Drift Monitor（Phase7-C）

```
責務（drift_monitor.pyヘッダーコメントより引用）:
「Phase7-A/Bの既存結果(canonical/intent/explanation/replay)を
束ねたconsistency_vectorを時系列で比較し、意味レベルのdriftを
検知・記録する。新しい意味は作らない。」

drift_definition: Canonical Drift/Explanation Drift/Intent
Driftの3種（DRIFT_WEIGHTS: canonical=3/explanation=2/
intent=1）。
出力: AnomalyRecord（canonical_trace_id/drift_type/
detected_at/before/after/weight）。
Human Gate関与: HumanGateHook.notify()は記録のみ
（具体的通知手段はPhase7-C-3以降で未実装）。
自動修復: 禁止（コード内コメントで明記）。

コード内コメントで既に明記された既存の区別:
「relay/replay_audit.py(状態レベルdrift)とは別概念であり、
統合しない」（drift_monitor.py 12行目）。
```

### Essence pipeline

```
責務: きむら博士の発言・思想・インシデントの特化抽出・蓄積
（essence_auto_updater.py v4ヘッダーコメントより、上書きでは
なく重要発言を積み上げる蓄積型）。

構成: essence_classifier.py(分類)→essence_extractor.py(抽出)
→essence_condenser.py(濃縮)→essence_pipeline.py、
essence_auto_updater.pyが定期実行（essence更新5分間隔/
REDUCING監視1分間隔/Caliber死活監視2分間隔/ping強制実行10分
間隔/RE_REDUCEDアーカイブ1時間間隔）。

出力先: interface/lever_essence.json。INCIDENT/PHILOSOPHY/
OPERATIONの3カテゴリに分類（KIMURA_SIGNAL/INCIDENT_KW/
PHILOSOPHY_KW/OPERATION_KWキーワードによる分類）。

COMMAND CENTERパイプラインstage（MOCKA_OVERVIEW.json）:
RAW→REDUCED→RE_REDUCED→REDUCING→CORE→ESSENCE→OUTBOX/PILS。

Human Gate関与・自動修復に関する明示規定: 既存資料に記載なし
（Essenceは「蓄積」自体が目的であり、Drift Monitor系の
「検知して通知する」という枠組みとは異なる設計思想で構築
されている）。
```

### Monitor系（relay/replay_audit.py + TIC health_check/tech_watcher）

```
relay/replay_audit.py（Phase4.5）:
責務（ヘッダーコメントより引用）「Replayが「実行・比較・記録」
できることを保証する境界部品。スコープは最小限: Drift検知 +
Audit Log記録のみ。」状態レベルdrift（v1/v2 replay不一致）を
検知し、replay_audit_log（SQLite）に記録。自動修復・alert
ルーティングは持たない（明記）。

interface/health_check.py（TIC Layer0）: 7点モーニングチェック
（稼働中）。

interface/tech_watcher.py（TIC Layer1 v3.0）: 意味差分検知
（TODO_208完了、稼働中）。対象は外部技術変化の検知
（MOCKA_OVERVIEW.json tic定義より）。
```

## 2. 機能重複マトリクス（事実整理のみ）

```
項目          | Drift Monitor(7-C)     | Essence pipeline       | Monitor系(replay_audit+TIC)
----------------|--------------------------|--------------------------|-------------------------------
検知対象       | 意味レベルdrift          | 思想・発言の重要度       | 状態レベルdrift
              | (canonical/explanation/  | 分類・蓄積               | (replay v1/v2不一致)+
              | intent)                  |                          | 外部技術文書の意味差分
              |                          |                          | (tech_watcher)
----------------|--------------------------|--------------------------|-------------------------------
入力          | consistency_vector       | 会話ログ・events.db      | replay実行結果(v1/v2)/
              | (Phase7-A/B出力)         |                          | 外部技術文書
----------------|--------------------------|--------------------------|-------------------------------
出力          | AnomalyRecord            | lever_essence.json       | replay_audit_log(SQLite)/
              |                          | (3カテゴリ蓄積)          | tech_watcher検知結果
----------------|--------------------------|--------------------------|-------------------------------
Human Gate関与 | notify()空実装          | 既存資料に明示規定なし   | 記録のみ(replay_audit.py)
              | (記録のみ)               |                          |
----------------|--------------------------|--------------------------|-------------------------------
自動修復有無   | 禁止(明記)              | (該当なし、蓄積自体が    | 禁止(明記、replay_audit.py)
              |                          | 目的)                    |
----------------|--------------------------|--------------------------|-------------------------------
既存の明文化   | drift_monitor.py内コメ  | Essenceとdrift系の関係は | replay_audit.pyとdrift_
された区別     | ントでreplay_audit.pyとの| 既存資料に明記なし       | monitor.pyの非統合は明記。
              | 非統合を明記             |                          | tech_watcherとdrift_
              |                          |                          | monitor.pyの関係は明記なし
```

## 3. 既に明文化されている境界（事実）

```
- drift_monitor.py冒頭コメント（12行目）:
  「relay/replay_audit.py(状態レベルdrift)とは別概念であり、
  統合しない」

- これはdecision_replay_system_contract_v1.md由来パターン
  （「Replay」という同一語でも対象が異なる別概念は明確に分離し
  統合しない）の継承であることが、project memory記録
  （Phase7-B1完了記録）から確認できる。
```

## 4. 未明文化のまま残る境界（事実、本監査の核心発見）

```
- Drift Monitor（意味レベル）とtech_watcher.py（意味差分検知、
  TIC Layer1）の関係は、いずれの既存契約文書にも明記がない。
  両者とも「意味の差分・ズレ」を検知対象とする点で機能的に
  重複する可能性があるが、対象範囲（Drift MonitorはPhase7-A/B
  canonical構造、tech_watcherは外部技術文書）が異なるため、
  単純な重複と断定はできない（観察のみ）。

- Essence pipelineとDrift Monitor/Monitor系の関係も既存資料に
  明記がない。Essenceは「重要発言の蓄積」、Driftは「ズレの
  検知」であり目的は異なるが、いずれも「察知すべきものを記録
  する」という抽象レベルでは共通の機能カテゴリに属する可能性
  がある。

- PHASE10_3_RESONANCE_NODE_REDEFINITION_v1.mdが指摘した
  「Essence Node」候補の命名衝突（既存essence語彙との直接衝突）
  は、本監査により実体ファイル（interface/essence_auto_
  updater.py v4等、現在も5分間隔で稼働中）として確認された。
  既に確立し稼働中のシステムであり、命名再利用は新規システムと
  の混同リスクが具体的に確認された事実として記録する。
```

## 5. 統合 / 分離 の判断材料（判断はしない、材料のみ）

```
統合した場合の利点（観察）:
- 「兆候を検知する」という機能がDrift Monitor/tech_watcher/
  Essenceに分散している現状を一元化できる可能性。

統合した場合のリスク（観察）:
- Drift Monitor契約が既に「relay/replay_audit.pyとは統合
  しない」という分離原則を明文化しており、この原則と矛盾しない
  統合方法の設計が別途必要になる。
- Essenceは「思想蓄積」という全く異なる目的のため、統合は
  目的の希薄化を招く可能性。

分離を維持した場合の利点（観察）:
- 各システムが個別契約・個別コメントで既に明確化された責務を
  保ったまま運用継続できる。

分離を維持した場合のリスク（観察）:
- 「察知系」が3つ以上に分散したまま将来Phase11以降でさらに
  増殖し、どのシステムが何を検知するかの全体像把握コストが
  増加し続ける可能性。
```

## 6. 未解決事項

```
- 監査範囲外として記録した追加モジュール群（core_kernel/
  governance、mocka3/drift_engine、production_observability、
  self_audit）が現行制度の一部か、廃止済み・実験的コードかが
  未確認。
- tech_watcher.pyとDrift Monitorの関係整理の要否が未確定。
- Essence pipelineを「察知系」の一部として扱うべきか、別カテゴリ
  （記憶・蓄積系）として扱うべきかが未確定。
- 上記いずれも、統合するか分離維持するかの判断はHuman Gateに
  委ねられたまま未着手。
```

## 注記

本文書は既存3系統（Drift Monitor/Essence/Monitor系）の実体
ファイルを確認した上での機能衝突整理のみであり、新規設計・命名・
Reasoning概念の適用・統合方針の決定のいずれも行っていない。
