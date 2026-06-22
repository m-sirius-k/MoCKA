# MoCKA / HAB × GPT Integration Spec（Phase 0–2 Snapshot）

## 0. 文書の位置づけ

本文書は以下を統合した**制度スナップショット（FP）**である：

- Phase 0: HAB機能モデル確定
- Phase 1: HAB Output Contract v0.2
- Phase 2: Relay Governance Layer

本仕様は「実装仕様」ではなく：

**構造・権限・観測関係の固定定義**

である。

## 1. システム全体構造

```
[Event Source]
      ↓
    HAB (structural filter)
      ↓
 ┌──────────────┬──────────────┐
 ↓              ↓              ↓
GPT           Relay         H2-3
(L0/L1)     (control)     (L2+ decision)
```

## 2. Phase 0: HAB機能モデル（確定済）

### 2.1 機能定義

HABは以下のみを実行する：

- event受信
- sliding windowによる集合化
- level分離（L0/L1/L2+）
- 重複構造検出
- routing tag付与

### 2.2 非機能制約

HABは禁止：

- 意味判断
- 安全評価
- 正しさ評価
- フィードバック学習
- パラメータ変更

## 3. Phase 1: HAB Output Contract v0.2

### 3.1 Core Output Schema

```json
{
  "event_id": "string",
  "level": "L0 | L1 | L2 | L3 | L4",
  "window": {
    "window_id": "string",
    "membership": "inside | outside",
    "ttl_state": "active | expired | dropped"
  },
  "structure": {
    "duplicate": "exact | partial | none"
  },
  "routing": {
    "target": "GPT | H2-3 | DROP",
    "action": "pass | filter | delegate"
  }
}
```

### 3.2 意味語彙排除規則

以下は禁止（HAB出力に含めない）：

- safe
- verified
- trusted
- correct
- valid（評価的意味）
- unresolved meaning

代替：

| 旧 | 新 |
|---|---|
| safe | structurally_valid |
| verified unique | signature_unique |
| unresolved meaning | delegation_required |

### 3.3 Feedback Adapter（制約済）

GPT → HABへの制御フィードバック禁止。
許可されるのは観測ログのみ。

## 4. Phase 2: Relay Governance Layer

### 4.1 Window Governance Authority

Relay = 唯一の window_size / slide_step 決定主体

### 4.2 Window Parameter Model

```json
{
  "window_size_ms": {
    "value": 5000,
    "status": "provisional",
    "origin": "bootstrap_default"
  },
  "slide_step_ms": {
    "value": 500,
    "status": "provisional",
    "origin": "bootstrap_default"
  }
}
```

### 4.3 Relay Authority Scope

Relayは以下のみ変更可能：

- window_size_ms
- slide_step_ms

### 4.4 非介入原則

以下は変更不可：

- HAB内部ロジック
- GPT動作
- H2-3判断構造

## 5. Mutation Accountability Layer

### 5.1 Events.db（Truth Layer）

すべてのRelay操作は必ず記録される：

```json
{
  "event_type": "window_config_change",
  "actor": "Relay",
  "operation": "set_window",
  "window_size_ms": 5000,
  "slide_step_ms": 500,
  "reason_code": "string",
  "source": "PHI-OS | manual | ops",
  "timestamp": "ISO-8601",
  "trace_id": "string"
}
```

### 5.2 Append-only原則

- overwrite禁止
- delete禁止
- modify禁止
- 追加のみ許可

## 6. SPOF再定義

**Before**

Relay = single point of control（危険）

**After**

Relay = single point of observable control（監査可能）

## 7. Phase境界モデル

- **Phase 0** — 構造定義
- **Phase 1** — 意味排除契約
- **Phase 2** — ガバナンス集中 + 観測強制

## 8. システム責務分離

| 層 | 責務 |
|---|---|
| HAB | 構造観測 |
| GPT | 意味処理 |
| H2-3 | 判断 |
| Relay | 構造制御 |
| Events.db | 真実記録 |

## 9. 完成条件（Phase 0–2）

以下を満たす：

- HABは自己変更不能
- GPTは構造非干渉
- H2-3は時間構造非保持
- Relayのみがwindow制御
- 全変更はEvents.dbに記録

## 10. 本質定義

本システムは以下として定義される：

- HAB = Stateless Structural Filter
- Relay = Observable Control Authority
- Events.db = Immutable Truth Layer

## 11. 状態定義

この時点でシステムは：

「制御集中型システム」ではなく
「観測可能制御システム」に変換済み

---

## 12. Phase 3: Telemetry & Time-Separated Evolution Layer（差分スナップショット）

### 12.0 位置づけ

Phase 0–2は「空間構造（静的契約）」であったのに対し、
Phase 3は「時間構造（進化境界）」を定義する、性質の異なる層である。
そのため独立ブロックとして追加する。

### 12.1 全体構造（更新）

```
HAB       = structural filter (static)
Relay     = control authority (mutable, observable)
GPT       = telemetry generator
H2-3      = batch-learning decision layer
            (real-time frozen, posthoc evolving)
Events.db = truth layer (immutable log)
```

### 12.2 GPT Telemetry Model

GPTは「自由な意味生成器」ではなく、出力が全て記録対象になる観測対象として扱う。

```json
{
  "event_type": "gpt_semantic_output",
  "timestamp": "ISO-8601",
  "input_context": {
    "window_id": "string",
    "event_ids": []
  },
  "output": {
    "content": "string",
    "embedding_hash": "string"
  },
  "classification": {
    "level": "L0 | L1 | L2+",
    "route_hint": "HAB | H2-3"
  }
}
```

- GPT出力は消えない／修正できない
- 意味は「評価」されない、ただ記録される

### 12.3 H2-3 Freeze Contract v2（修正版・確定）

初期案の `memory_update: false` / `self_modification: false` は
「即時学習の禁止」と「長期進化の禁止」を区別せず両方を殺してしまう書き方であったため、
以下のように修正して確定する。

```json
{
  "role": "decision_layer",
  "real_time_mutation": false,
  "learning_scope": {
    "online_learning": false,
    "batch_learning": true,
    "historical_analysis": true
  },
  "self_modification": {
    "runtime": false,
    "posthoc": true
  }
}
```

### 12.4 学習境界定義

```
- online_learning = forbidden
- batch_learning = allowed
- recurrence_registry = update permitted
- real-time feedback loop = frozen
```

禁止領域（リアルタイム危険領域）：
- 実行中の構造変更
- 即時フィードバック反映
- 判断ロジックのリアルタイム更新

許可領域（文明ループ）：
- recurrence_registry更新
- 事後分析
- 統計的学習
- 制度改善・長期最適化

### 12.5 既存MoCKA資産との接続

```
- recurrence_registry → H2-3 batch layer
- prevention_queue    → Events.db derived analytics
- TRUST_SCORE         → posthoc evaluation metric
```

MoCKA文明ループ（事故→記録→分析→制度化→文明進化）との整合：

| フェーズ | 層 |
|---|---|
| 事故 | runtime |
| 記録 | Events.db |
| 分析 | GPT telemetry |
| 制度化 | H2-3 batch learning |
| 進化 | Relay / PHI-OS |

### 12.6 時間分離原則（本質）

```
Real-time domain:
    HAB / GPT / Relay / H2-3 (decision only)

Posthoc domain:
    H2-3 batch learning / system evolution
```

禁止したいのは「学習」ではなく「即時学習」である。
H2-3は死なない。進化も止まらない。ただしリアルタイムでは動かない。

### 12.7 Phase 3完成条件（修正版）

- ✔ H2-3のリアルタイム変更禁止
- ✔ バッチ学習は許可
- ✔ recurrence_registry更新可能
- ✔ フィードバックは即時反映禁止
- ✔ 事後分析は完全許可

### 12.8 Events.db拡張（三層ログ化）

```
1. HAB structural events
2. Relay mutation events
3. GPT semantic telemetry   ← NEW
```

Events.dbは単なるログではなく、システム全体の唯一の"現実定義層"になる。

---

END OF SNAPSHOT (Phase 0–3)

必要なら次はそのまま：

**Phase 4（Operational Stability：drift監視・window安定化・batch learning cycleの運用化・recurrence_registry統合）**

ここで本当に"システム"として運用フェーズに入る。
