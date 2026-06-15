# SEMANTIC DRIFT ENGINE v1.0

## 0. ステータスと位置づけ

本書は [ARCHITECTURE_MOCKA_2_0_v1.md](ARCHITECTURE_MOCKA_2_0_v1.md)（①固定）、[INTENT_SCHEMA_v1.md](INTENT_SCHEMA_v1.md)（②固定）、[INTENT_GRAPH_v1.md](INTENT_GRAPH_v1.md)（Step2確定）を前提とする、実装順序Step 3（Semantic Drift Engine）の基準仕様である。

- Step 1: Intentの存在定義（静的定義）
- Step 2: Intent間関係の構造化（Graph化）
- Step 3（本書）: **変化そのものの意味**を扱う

Step 1〜2で欠けていたのは「変化そのものの意味」である。Step 3は変更（diff）ではなく、意味のズレ（drift）を検出する。

## 1. Semantic Driftの定義

Semantic Driftとは、**同一Intent空間における「意味の時間的変化」**である。

INTENT_GRAPH_v1 §4のLayer G2（Evolution Graph）は「時間軸付きIntent Graph」であり、Step 3はこれを横方向（構造）・縦方向（時間）の両方で解析する。

## 2. 入力と出力

### 入力

- G2 Evolution Graph（[INTENT_GRAPH_v1.md](INTENT_GRAPH_v1.md) §4）
- INTENT_GRAPH_v1（G0/G1を含む全体構造）
- INTENT_SCHEMA_v1（Intentオブジェクト本体）
- REQ change history（ARCHITECTURE_MOCKA_2_0_v1.md Layer 2: REQ Change History with Intent）

### 出力

- Drift Event Graph
- Intent Evolution Delta
- Semantic Change Score
- Intent Stability Index

これらはLayer 2（Governance Intelligence Layer）のDrift Semantics Engineの実体として機能し、Layer 3 Design Drift Projectionの入力となる。

## 3. Driftの4分類モデル

MoCKA 2.0ではDriftは単一概念ではなく、4種に分類される。

### D1: Structural Drift

- Graph構造の変化。edge追加・削除（INTENT_GRAPH_v1 §3の4種エッジのいずれかの増減）。

### D2: Priority Drift

- `priority`（INTENT_SCHEMA §2.3）の変化。意図の優先順位変動。

### D3: Semantic Drift（狭義）

- 同じIntentでも意味が変わる。解釈の変化。Intentの内容・目的の記述レベルでの変化を指す（構造・優先度・外部環境の変化では説明できない変化）。

### D4: Contextual Drift

- 外部環境による意味変化。システム外依存（例: 1.0のTIC Layerが検知する外部技術変化など）に起因する変化。

D1〜D4は排他ではない。1つのIntentに対して複数のDriftが同時に検出されうる（§5 Semantic scoringはこれを前提とする）。

## 4. Drift検出アルゴリズム（概念）

### Step 3-1: Snapshot比較

- G2(t) vs G2(t-1)。時刻tと直前スナップショットt-1のEvolution Graphを比較する。

### Step 3-2: Intent alignment

- 同一Intentの対応付け。
- 第一に`intent_id`によるIDベース対応付けを行う。
- IDが変化している場合（INTENT_GRAPH_v1 Phase 2-3の重複統合・deprecated遷移を含む）は、semantic similarityによる対応付けを補助的に用いる。

### Step 3-3: Difference extraction

- edge diff: INTENT_GRAPH_v1 §3の4種エッジの増減（D1の入力）。
- attribute diff: `priority` / `stability` / `relations` 等のフィールド差分（D2・D3の入力）。
- lifecycle diff: `lifecycle_state`の遷移（draft→active→resolved/deprecated）。

### Step 3-4: Semantic scoring

各Intentに対して、以下の重み付き合成によりDriftScoreを算出する。

```
DriftScore = w1*(structure) + w2*(priority) + w3*(semantic) + w4*(context)
```

- `structure`はD1（edge diffに基づく）、`priority`はD2、`semantic`はD3、`context`はD4の各成分値を表す。
- 各成分値の算出方法・w1〜w4の重み係数は本書では値域を定義せず、実装フェーズ（Engine構造 §6 Drift Scorer）で確定する。本書はDriftScoreが4分類の合成であることのみを基準仕様として固定する。

## 5. Semantic Drift Engine構造（Core Module）

- **Snapshot Manager**: G2のスナップショットを取得・保持し、Step 3-1の比較対象を管理する。
- **Intent Matcher**: Step 3-2のIntent alignmentを担う。
- **Drift Classifier**: Step 3-3のDifference extractionに基づき、D1〜D4への分類を行う。
- **Drift Scorer**: Step 3-4のSemantic scoringを行い、DriftScore（Semantic Change Score）を算出する。
- **Evolution Tracker**: 算出されたDrift・Scoreを時系列で蓄積し、Intent Stability Index（INTENT_SCHEMA §2.4 `stability`の遷移判定に対応）とEvolution vectorsを生成する。

## 6. 設計原則（P1〜P3）

### P1: Driftはエラーではない

Driftは異常検知の対象ではなく、**変化そのものが正規データ**である。Layer 1の検証（ARCHITECTURE §3 P4）はDriftの発生自体を拒否しない。検証対象はDrift後のIntent構造がConstraintを満たすかどうかである。

### P2: Driftは削除されない

すべてのDriftはDrift Event Graphとして**履歴化**される。INTENT_GRAPH_v1 R2（Conflictは削除しない）と同様の原則をDriftにも適用する。

### P3: Driftは未来予測に使われる

Drift Event Graph・Evolution vectorsは、ARCHITECTURE_MOCKA_2_0_v1.md Layer 3のDesign Drift Projection（長期的設計方向の生成）の入力として用いられる。Step 3はProjection Engineの前段として位置づけられる。

## 7. 出力構造（v1）

```json
{
  "drift_events": [
    {
      "drift_id": "string",
      "intent_id": "string",
      "snapshot_from": "ISO8601",
      "snapshot_to": "ISO8601",
      "drift_types": ["D1", "D2", "D3", "D4"],
      "diff": {
        "edge_diff": {},
        "attribute_diff": {},
        "lifecycle_diff": {}
      },
      "drift_score": 0.0
    }
  ],
  "intent_stability_map": {
    "intent_id": "experimental | provisional | stable"
  },
  "semantic_change_graph": {
    "nodes": ["intent_id"],
    "edges": [
      {"from": "intent_id", "to": "intent_id", "drift_id": "string"}
    ]
  },
  "evolution_vectors": [
    {
      "intent_id": "string",
      "direction": "string",
      "magnitude": 0.0,
      "based_on": ["drift_id"]
    }
  ]
}
```

- `drift_events[]`: Drift Event Graphの要素。各イベントは1つのIntentに対する1回のDrift検出を表す。
- `intent_stability_map`: INTENT_SCHEMA §2.4 `stability`値への反映候補。Engineは値を直接書き換えず、候補（map）として出力する。`stability`の確定遷移はLayer 1検証を経る（ARCHITECTURE §3 P4）。
- `semantic_change_graph`: Intent Evolution Deltaの構造表現。drift_idによりdrift_eventsと紐づく。
- `evolution_vectors[]`: Design Drift Projectionへの入力。各Intentの変化方向・大きさを表す。

## 8. システム的意味

Step 3の導入により、MoCKAは以下のように変化する。

| before | after |
|---|---|
| Graph system | Evolution system |
| Static relations | Temporal meaning |
| State tracking | Meaning tracking |

## 9. 次ステップへの接続

Step 3の次はStep 4（Cognitive Governance Layer Activation）に移行する。Step 4で初めて「意思決定の生成」に入る。

## 10. 状態整理

- ARCHITECTURE v1 → 固定済み
- INTENT_SCHEMA v1 → 固定済み
- INTENT_GRAPH v1 → 確定済み
- SEMANTIC_DRIFT_ENGINE v1（本書） → Step 3 構造定義として確定
- → ここでMoCKAは「動的意味系」に到達
