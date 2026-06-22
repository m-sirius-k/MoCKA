# MoCKA / HAB × GPT Integration Spec（Phase 0–4 Snapshot）

> **version note**: 本ファイルは `FP_HAB_GPT_CONTRACT_V02_20260622_02.md`（Phase 0–3 baseline snapshot）の
> civilization state version。02は構造が確定した世界、03は時間（運用安定性）が入り込んだ世界として、
> 02を上書きせず別バージョンとして保持する。

## 0. 文書の位置づけ

本文書は以下を統合した**制度スナップショット（FP）**である：

- Phase 0: HAB機能モデル確定
- Phase 1: HAB Output Contract v0.2
- Phase 2: Relay Governance Layer
- Phase 3: Telemetry & Time-Separated Evolution Layer
- Phase 4: Operational Stability Layer

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

## 13. Phase 4: Operational Stability Layer（差分スナップショット）

### 13.0 位置づけ

Phase 0–3が「構造設計」であったのに対し、Phase 4は
「設計されたシステムが実トラフィック上で長時間壊れずに運用できることの証明」
であり、評価軸が「設計の正しさ」から「長時間壊れないこと」に変わる、
性質の異なる層である。そのため独立ブロックとして追加する。

### 13.1 アーキテクチャ（運用版）

```
[Live Events]
     ↓
   HAB
     ↓
   Relay
     ↓
 ┌──────────────┬──────────────┐
 ↓              ↓              ↓
GPT          H2-3 batch     Events.db
(real-time)   (evolution)   (truth)
```

### 13.2 Phase 4の目的（3つ）

- **安定性**: system crash防止、routing崩壊防止
- **一貫性**: HAB→Relay→H2-3の整合維持、GPT telemetry欠損防止
- **進化ループ維持**: recurrence_registry更新継続、batch learning周期維持

### 13.3 Drift監視レイヤ

Driftの定義：

```
expected_state != observed_state
```

監視対象：

- window_size deviation
- Relay mutation frequency
- H2-3 batch delay
- GPT output entropy
- Events.db growth anomaly

Drift Log Schema：

```json
{
  "timestamp": "ISO-8601",
  "component": "HAB | Relay | GPT | H2-3",
  "metric": "string",
  "expected": "float",
  "observed": "float",
  "deviation": "float",
  "severity": "low | medium | high"
}
```

### 13.4 Events.db運用強化

圧縮ルール：
- semantic aggregation allowed
- raw events immutable
- periodic snapshotting

Snapshot Policy：

```
every N events:
    create aggregated snapshot
    preserve raw log
```

### 13.5 Relay安定化ルール

```
max window changes / hour = bounded
```

異常検知条件：

```
if rapid_reconfiguration detected:
    flag drift_event
```

### 13.6 即時性とbatch化の境界（核心・確定）

初期案の7.1「realtime stream禁止」は「GPTがリアルタイムに思考しない／
H2-3への経路が遅延する」と誤読されうる書き方であり、Phase 0のRouting Matrix
（L2→H2-3 即delegate）やPhase 3のTelemetry原則と矛盾する可能性があったため、
以下のように軸を分離して確定する。

**Generation Layer（即時性を維持するもの）**:
- GPT出力（リアルタイム生成・リアルタイム意味処理）
- L2 → H2-3 routing decision（即時delegate、Phase 0のまま不変）
- Relay制御（windowに基づく即時判定）

**Transport Layer（batch化されるもの）**:
- telemetry commit → Events.db反映
- audit layer反映
- replay index構築

| レイヤ | 即時性 | batch化 |
|---|---|---|
| GPT出力 | 即時 | なし |
| routing (L2→H2-3) | 即時 | なし |
| Relay制御 | 即時 | なし |
| Event.db commit | なし | あり |
| telemetry store | なし | あり |

**結論**: Phase 4のbatch化は「制御遅延」ではなく「記録遅延」である。
制御遅延にすると Relay windowと競合し、H2-3の即時性が崩壊し、
Phase 0のrouting matrixが無効化されるため、これは確定境界として固定する。

### 13.7 GPT運用制御（Telemetry過負荷対策）

- GPT outputはリアルタイム生成されるが、telemetryとしての永続化・
  Events.db反映・replay可能化はbatch化される
- entropy control: high entropy → flagged, not filtered（除外はしない）

### 13.8 H2-3運用（batch安定化）

```
every T interval:
    pull Events.db
    update recurrence_registry
    update TRUST_SCORE
```

制約（Phase 3から継続）：
- real-time禁止（H2-3の判断ロジック自体は維持）
- 過学習禁止（structure固定）

### 13.9 Phase 4成立条件

- ✔ driftが検出可能
- ✔ Relayが暴走しない（mutation rate制限・異常検知）
- ✔ Events.dbが破綻しない（圧縮・snapshot運用）
- ✔ GPT telemetryが欠損しない
- ✔ H2-3 batchが継続する
- ✔ GPT出力・L2 routing・Relay制御の即時性がbatch化によって損なわれない

### 13.10 Phase 4の本質

「設計が正しいこと」ではなく「長時間壊れないこと」が評価軸になる。

```
Phase 0–3 = 構造設計
Phase 4   = 生存試験（stability layer）
```

---

END OF SNAPSHOT (Phase 0–4)

必要なら次はそのまま：

**Phase 5（Governance Feedback Closure：system全体の再評価、policy再生成、
Relay再設計可能性評価、制度再設計・文明ループ確定）**

ここでMoCKAは"自己進化システム"として閉じる。
