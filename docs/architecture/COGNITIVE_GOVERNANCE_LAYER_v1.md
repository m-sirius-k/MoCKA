# COGNITIVE GOVERNANCE LAYER v1.0（Step 4: Activation）

## 0. ステータスと位置づけ

本書は [ARCHITECTURE_MOCKA_2_0_v1.md](ARCHITECTURE_MOCKA_2_0_v1.md)（①固定）、[INTENT_SCHEMA_v1.md](INTENT_SCHEMA_v1.md)（②固定）、[INTENT_GRAPH_v1.md](INTENT_GRAPH_v1.md)（Step2確定）、[SEMANTIC_DRIFT_ENGINE_v1.md](SEMANTIC_DRIFT_ENGINE_v1.md)（Step3確定）を前提とする、実装順序Step 4（Cognitive Governance Layer Activation）の基準仕様である。

Step 1〜3はすべて**観測系**である（Intent=存在、Graph=関係、Drift=変化）。Step 4で初めて、観測から**判断生成**へ移行する。

## 1. Cognitive Governance Layerの定義（再確認）

ARCHITECTURE_MOCKA_2_0_v1.md Layer 3はIntentを「生成する側」のレイヤである。Step 4はこのLayer 3を**活性化**し、観測結果（Step 1〜3の出力）を入力としてDecision Objectを生成する機能を定義する。

## 2. 入力と出力

### 入力

- INTENT_GRAPH（[INTENT_GRAPH_v1.md](INTENT_GRAPH_v1.md)：G0/G1/G2）
- SEMANTIC_DRIFT_ENGINE出力（[SEMANTIC_DRIFT_ENGINE_v1.md](SEMANTIC_DRIFT_ENGINE_v1.md) §7：drift_events / intent_stability_map / semantic_change_graph / evolution_vectors）
- Constraint Layer（ARCHITECTURE Layer 1：Validation Engine / Compliance Model / Audit System / Traceability Graph）
- Evolution Graph（G2）

### 出力

- Decision Objects（decision_graph）
- Intent Proposals（synthesized_intents[]）
- Conflict Resolutions（conflict_resolution_map）
- System Direction Vector（future_projection_vector）

## 3. Decision Object（中核データ）

Step 4の中心構造は**Decision = 意図生成単位**である。

```json
{
  "decision_id": "string",
  "generated_intents": ["INTENT_SCHEMA-compliant object"],
  "source_intent_set": ["intent_id"],
  "drift_context": ["drift_id"],
  "constraint_result": {
    "status": "pending | passed | rejected",
    "constraint_check_id": "string | null"
  },
  "confidence": 0.0,
  "rationale_graph": {
    "nodes": ["string"],
    "edges": [
      {"from": "string", "to": "string", "relation": "string"}
    ]
  },
  "created_at": "ISO8601"
}
```

- `generated_intents`: Decisionが生成する1つ以上のIntent候補。各候補はINTENT_SCHEMA_v1に準拠し、`lifecycle_state: draft`、`source.origin: "layer3.synthesis"`として生成される。
- `source_intent_set`: この生成の起点となった既存Intentのid群（G1由来）。
- `drift_context`: この生成の根拠となったDrift Event（Step3出力）のid群（G4由来の場合に必須）。
- `constraint_result`: ARCHITECTURE §3 P4（Layer 3はLayer 1を経由しない限り実行・記録に反映されない）に対応する。`status`が`passed`になるまで、`generated_intents`は`draft`のまま実行系に影響を与えない。
- `confidence`: §8 P2（Governance is probabilistic）に対応する確率値。
- `rationale_graph`: 「なぜこのDecisionが生成されたか」を表すグラフ。Layer 2 Decision Reason Graphへの登録単位となる（INTENT_SCHEMA §2.8 `traceability.reason_graph_node_id`との接続点）。

## 4. Cognitive Governanceの4機能

### G1: Intent Synthesis

- 分散Intent（INTENT_GRAPH上の複数Intent）を統合して新Intentを生成する。
- 入力: `source_intent_set`（INTENT_GRAPH G1上で関連するIntent群）。
- 出力: `generated_intents`。

### G2: Intent Prioritization

- priority drift（SEMANTIC_DRIFT_ENGINE D2）とConstraint（Layer 1）を統合評価し、既存・新規Intentの`priority`（INTENT_SCHEMA §2.3）を再評価する。
- G2の出力は既存Intentの`priority`変更案であり、これもDecision Objectとして表現される（`generated_intents`に既存Intentの更新版を含む）。

### G3: Conflict Resolution

- INTENT_GRAPH の`conflicts_with`エッジ（conflict edge）を「解消」ではなく**「選択構造化」**する。
- 出力（`conflict_resolution_map`）は、競合するIntent群に対して「どちらを選択するか」ではなく、両者を保持したまま優先関係・適用条件を構造化したものである。INTENT_GRAPH R2（Conflictは削除しない）・SEMANTIC_DRIFT_ENGINE P3（Conflict is preserved in structure）と整合する。
- `resolution_intent_id`（INTENT_SCHEMA §2.6）はこのConflict Resolutionが生成する新Intentのidを指す。

### G4: Direction Projection

- G2 Evolution Graph + Drift（evolution_vectors）から未来Intentを生成する。
- ARCHITECTURE Layer 3 Design Drift Projectionの実体。出力は`future_projection_vector`であり、長期的設計方向を示す。

## 5. 重要な設計転換（Step 3との差分）

| Step 3 | Step 4 |
|---|---|
| Drift検出 | 意図生成 |
| 分析 | 合成 |
| 過去ベース | 未来生成 |
| 観測 | 制御 |

## 6. Governance Loop（新しい閉ループ）

Step 4により以下のサイクルが成立する。

```
Intent生成（Layer 3 / Step4）
  → Constraint評価（Layer 1）
  → Execution（Layer 0）
  → Drift観測（Layer 2 / Step3）
  → Decision再生成（Layer 3 / Step4）
  → ...（自己更新ループ）
```

このループはARCHITECTURE_MOCKA_2_0_v1.md §4のシステムフロー（Intent → Constraint → Execution → Reason Graph）の具体化であり、Reason GraphからIntentへのフィードバック経路がDrift観測→Decision再生成として実体化されたものである。

## 7. 最重要原則（P1〜P3）

### P1: Decision is not selection, but synthesis

DecisionはIntent候補群からの「選択」ではなく、新たなIntent（またはIntentの更新版）の「生成」である。G1〜G4はいずれも合成（synthesis）として定義される。

### P2: Governance is probabilistic

すべてのDecisionは`confidence`（確率構造）を持つ。確定的な真偽判定ではない。`confidence`の算出方法は本書では値域を定義せず、実装フェーズで確定する。

### P3: Conflict is preserved in structure

G3で述べた通り、競合は削除されず構造として保持される（INTENT_GRAPH R2 / SEMANTIC_DRIFT_ENGINE P3の継承）。

## 8. Cognitive Engine構造（Core Modules）

- **Intent Synthesizer**: G1を担う。
- **Conflict Resolver**: G3を担う。
- **Priority Aggregator**: G2を担う。
- **Direction Predictor**: G4を担う。
- **Rationale Graph Builder**: 各Decision Objectの`rationale_graph`を構築し、Layer 2 Decision Reason Graphへ登録する。

## 9. 出力構造（v1）

```json
{
  "decision_graph": {
    "decisions": ["Decision Object"],
    "edges": [
      {"from": "decision_id", "to": "decision_id", "relation": "string"}
    ]
  },
  "synthesized_intents": ["INTENT_SCHEMA-compliant object (lifecycle_state: draft)"],
  "conflict_resolution_map": {
    "conflict_pair": ["intent_id", "intent_id"],
    "resolution_intent_id": "string",
    "structure": "string"
  },
  "future_projection_vector": {
    "based_on": ["evolution_vector id"],
    "direction": "string",
    "horizon": "string",
    "confidence": 0.0
  }
}
```

- `decision_graph`: 複数のDecision Objectとその相互関係。
- `synthesized_intents`: G1〜G3が生成するIntent候補（すべて`draft`、Layer 1検証待ち）。
- `conflict_resolution_map`: G3の出力。
- `future_projection_vector`: G4の出力。ARCHITECTURE Layer 3 Design Drift Projectionの出力形式に対応する。

## 10. システムの意味変化

| before | after |
|---|---|
| 意味を記録する | 意味を生成する |
| 状態システム | 意思システム |
| 分析エンジン | ガバナンスエンジン |

## 11. 次ステップへの接続

Step 4の次はStep 5（Full Governance Loop Closure）に移行する。Step 5で自己再設計・長期進化・システム主導意思決定が完成する。

## 12. 状態整理

- ARCHITECTURE v1 → 固定済み
- INTENT_SCHEMA v1 → 固定済み
- INTENT_GRAPH v1 → 確定済み
- SEMANTIC_DRIFT_ENGINE v1 → 確定済み
- COGNITIVE_GOVERNANCE_LAYER v1（本書） → Step 4 構造定義として確定（Decision生成）
