# MoCKA / HAB Phase 4 — Execution Interface Specification (v1.0)

本仕様は FP_HAB_GPT_CONTRACT_V02_20260622_03.md（Phase 0–3）と整合する形で
Phase 4（stability + runtime control separation）を正式な制御インターフェースとして定義する。
本文書は「実装仕様（contract-compatible runtime layer）」であり、設計メモではない。

## 4.0 Phase 4 定義（全体）

Phase 4は以下の3層分離モデルとして定義される：

- Control Plane（リアルタイム制御）
- Sovereign Plane（override主権 / 制御系の上位停止権）
- Data Plane（遅延観測・batch記録）

## 4.1 Drift監視層（Observation Layer）

**Purpose**: システム状態の期待値と実測値の乖離（drift）を検知する。

- **input**:
  - Relay state snapshot（window_size, slide_step）
  - H2-3 decision log（latest N events）
  - Events.db append stream
- **output**: Drift Event Record（component, expected_state, observed_state, deviation, severity）
- **invariant**:
  - 本層はread-onlyであり、いかなる制御変更も行わない
  - drift検知は状態更新をトリガーしない
- **violation condition**:
  - 観測処理が制御層（Relay / H2-3 / GPT）へ書き込みを行った場合
  - expected_state未定義のまま比較処理が実行された場合
- **recovery rule**:
  - Drift監視プロセス停止
  - Relay経由でHuman Gateへエスカレーション
  - 該当イベントはEvents.dbへincidentとして記録

## 4.2 Relay制御境界（Control Boundary）

**Purpose**: Relayが持つ時間制御パラメータのみに権限を限定する。

- **input**: set_window request（window_size_ms, slide_step_ms, reason_code, source）
- **output**: 更新済みwindow設定 / RELAY_MUTATION_EVENT（Events.db記録）
- **invariant**:
  - Relayが変更可能なのは window_size_ms / slide_step_ms のみ
  - window_sizeは「制御単位ではなく観測単位」である
  - Relayはrouting / decision / semantic layerへ干渉しない
- **violation condition**:
  - window以外のパラメータ変更要求
  - mutation頻度制限超過
- **recovery rule**:
  - 即時reject
  - drift event発火（4.1）
  - rate超過時はRelay freeze（Human Gate解除待ち）

## 4.3 H2-3 Decision Stabilizer（Batch Layer）

**Purpose**: H2-3のリアルタイム判断を維持しつつ、記録・集計のみをbatch化する。

- **input**: L2+ delegate event（リアルタイム） / Events.db batch pull
- **output**: recurrence_registry update (batch) / TRUST_SCORE update (batch) / decision trace（replay可能形式）
- **invariant**:
  - H2-3の判断ロジックはリアルタイム維持
  - batch化対象は記録・集計のみ
  - real_time_mutation = false（Phase 3継続）
- **violation condition**:
  - runtimeでH2-3ロジックが変更された場合
  - replay不能な圧縮が生成された場合
- **recovery rule**:
  - H2-3 freeze
  - Human Gateへ報告
  - raw eventから再構築

## 4.4 Event.db Truth Layer（Immutable Log）

**Purpose**: 全イベントの因果的整合性を保証する単一真実層。

- **input**: GPT telemetry / Relay mutation events / H2-3 decision traces / HAB routing events
- **output**: append-only causal log / ordered event stream
- **invariant**:
  - overwrite禁止 / delete禁止 / modify禁止（append-only）
  - causal link必須
- **violation condition**:
  - 既存イベントの改変検知
  - causal link欠落イベント
- **recovery rule**:
  - snapshot復元
  - quarantine領域へ隔離
  - Human Gate判断待ち（自動補完禁止）

## 4.5 Telemetry圧縮層（Signal Layer）

**Purpose**: GPT出力の完全保存と構造圧縮を両立する。

- **input**: GPT semantic output（real-time）
- **output**: hierarchical compressed telemetry / raw content preserved
- **invariant**:
  - GPT outputは完全保存される
  - 圧縮は構造のみ（意味圧縮禁止）
  - replay可能性維持
- **violation condition**:
  - raw content破棄
  - replay不能圧縮
- **recovery rule**:
  - compression停止
  - raw eventから再生成
  - high entropy flagのみ付与（除外禁止）

## 4.6 Routing Matrix + Override Architecture

**Purpose**: Phase 0 Routing Matrixの即時性を維持しつつ、overrideを制度主権として隔離する。

**main routing (immutable)**:
- L0 → GPT
- L1 → GPT（window制約）
- L2+ → H2-3（即時delegate）

**override model**:
- Level 0（Detection Layer）: Relay = routing failure / deadlock検知、H2-3 = anomaly / inconsistency検知 → 実行権限なし
- Level 1（非存在）: 自動overrideは禁止（設計上存在しない）
- Level 2（Sovereignty Layer）: Human Gate（きむら博士）のみ実行可能。routing / phase / rule変更権限

- **invariant**:
  - L2+ delegateはbatch化されない
  - override実行は必ずHuman Gate経由
  - Relay / H2-3は検知のみ可能
- **violation condition**:
  - 非Human Gateによるrouting変更
  - L2+ delegateのbatch化
- **recovery rule**:
  - routing rollback
  - component freeze
  - Human Gateへ強制報告

## 4.7 Control / Sovereign / Data Plane Separation Axiom（三層分離・修正版）

**Purpose**: リアルタイム制御、主権実行、および遅延記録の三層分離を定義する。

**classification**:

| Layer | Type | Timing |
|---|---|---|
| Control Plane | Control | real-time |
| Sovereign Plane | Override Execution | delayed intentional |
| Data Plane | Data | batch |

**Sovereignの位置づけ（重要）**:

Sovereignは第3の並列機能ではなく、「Control Planeの外側にある、制御そのものを停止・再定義できる層」である。

```
Control = 実行
Data    = 記録
Sovereign = 制御系の上位停止権
```

- **invariant**:
  - control planeは常にリアルタイム
  - data planeは常にbatch
  - Sovereign planeはControl Planeの上位に位置し、Control/Dataの混線を裁定する権限を持つ
  - 三者の混線（control⇄data直結、sovereignの形式化されない迂回）は禁止
- **violation condition**:
  - data planeが制御に影響
  - control planeがbatch化
  - sovereign判断を経ずにcontrol planeのルールが変更される
- **recovery rule**:
  - control plane優先復帰
  - drift eventとして記録
  - Phase 5前提条件として保持

## 5. Status

- Phase 0–3：FP Contract（確定）
- Phase 4：Execution Interface（本仕様）
- status：compatible draft → contract-ready
- events.db commit：未実施（統合フェーズ待ち）

## 最終結論

この仕様で確定した本質は1つだけ：

**Phase 4は「安定化レイヤ」ではなく、制御時間の分離による主権モデルの固定層である。**

必要なら次はそのまま：
- FP群への完全統合版（差分ゼロ整形）
- Phase 5（制度自己更新ループ設計）

どちらでもそのまま繋げられる状態になっている。
