# TIC Layer 2-4 Architecture Specification

## Overview

Technology Intelligence Caliber (TIC) の第2-4層実装仕様。
Perception Layer（認識層）完成への最終3層。

### Current State

- Layer 0: health_check.py (7点モーニングチェック) ✓ 稼働中
- Layer 1: tech_watcher.py v3.0 (意味差分検知) ✓ 稼働中  
- Layer 2: tech_lab/ Sandbox (隔離実験) - 本仕様
- Layer 3: impact_analyzer.py (影響分析) - 本仕様
- Layer 4: COMMAND CENTER UI (可視化) - 本仕様

### Target

外部技術変化に対する4層防衛（Defense in Depth）
→ JARVIS Perception Layer 完成

---

## Layer 2: Tech Lab Sandbox

### Purpose

新規技術・ツール・ライブラリの安全な試行環境。
隔離 + 検証 + リスク評価 → 本番統合判断

### Architecture

```
External Tech Change
        ↓
   Tech Watcher (L1)
        ↓
   [SANDBOX GATE]
        ↓
   /tech_lab/ (isolated)
     ├── /candidates/     (新規ツール試行)
     ├── /experiments/    (変更影響検証)
     ├── /roll_back/      (復帰用スナップショット)
     └── /report/         (試行結果記録)
        ↓
   Risk Assessment
        ↓
   Impact Analysis (L3)
```

### Implementation Details

#### 2.1 Sandbox Manager

**File:** `interface/sandbox_manager.py`

```python
class TechLabSandbox:
    """隔離環境管理・検証"""
    
    - create_experiment(tech_name, version, description)
      → /candidates/tech_name_vX.X/ 作成
      → isolation_level 設定 (FULL / PARTIAL / MONITORING)
      → roll_back snapshot 記録
    
    - run_candidate_test(experiment_id)
      → 隔離環境で試行実行
      → stdout/stderr キャプチャ
      → system_state δ測定
    
    - assess_compatibility(experiment_id, target_component)
      → 対象コンポーネントとの互換性検査
      → Breaking change detection
      → API signature 差分分析
    
    - generate_report(experiment_id)
      → 試行結果をJSONL出力
      → /report/experiment_id.jsonl
      → 後続L3への入力
```

#### 2.2 Isolation Levels

| Level | Scope | リスク | 用途 |
|-------|-------|--------|------|
| FULL | 完全隔離コンテナ | 最小 | 未検証ツール |
| PARTIAL | Shared lib only | 中 | minor version update |
| MONITORING | In-process + logging | 高 | 既存ツール minor fix |

#### 2.3 Sandbox State Tracking

- `/tech_lab/.sandbox_state.json`
  ```json
  {
    "experiment_id": "exp_20260813_001",
    "tech_name": "dependency_tool_vX.Y",
    "isolation_level": "FULL",
    "status": "in_progress|passed|failed|rolled_back",
    "created_at": "2026-08-13T...",
    "snapshot_hash": "sha256:...",
    "risk_assessment": {
      "breaking_changes": 0,
      "api_incompatibility": false,
      "performance_delta": 0.05
    }
  }
  ```

---

## Layer 3: Impact Analyzer

### Purpose

技術変化の依存波及を自動解析。
"この変更は何に影響するか" → 行動決定ベース提供

### Architecture

```
Sandbox Report (L2)
        ↓
[IMPACT ANALYZER]
        ↓
    ├─ Dependency Graph Build
    ├─ Breakage Detection
    ├─ Risk Propagation Model
    └─ Confidence Scoring
        ↓
  Impact Matrix (N×M)
        ↓
  Recommendation
  (ignore / test / integrate / reject)
```

### Implementation Details

#### 3.1 Dependency Intelligence

**File:** `interface/impact_analyzer.py`

```python
class ImpactAnalyzer:
    """依存関係 → 波及リスク分析"""
    
    - build_dependency_graph()
      → MoCKA components: app.py, evaluator_*.py, essence_*.py
      → External deps: requirements.txt parsing
      → Graph representation: NetworkX or custom
    
    - detect_breakage(candidate_tech)
      → Breaking changes search
      → API signature breaking
      → Behavioral incompatibility
      → Dependency version mismatch
    
    - propagate_risk(breakage_set)
      → BFS/DFS from breakage node
      → Transitively affected components
      → Risk attenuation model (distance-based)
    
    - generate_impact_matrix(candidate_tech)
      → rows: affected components
      → cols: risk type (breaking, perf, subtle)
      → value: confidence score 0-1
      
    - recommend_action(impact_matrix, Z_current)
      → Z_governance_stability 参照
      → リスク・安定性トレードオフ評価
      → (ignore / test_more / integrate / block) 推奨
```

#### 3.2 Impact Matrix Output

**File:** `/data/tic/impact_matrix_YYYYMMDD_HHMM.jsonl`

```json
{
  "candidate_id": "exp_20260813_001",
  "tech_name": "tool_vX.Y",
  "analysis_timestamp": "2026-08-13T...",
  "dependency_graph": {
    "nodes": 42,
    "edges": 87,
    "criticality_score": 0.63
  },
  "breakage_detection": {
    "breaking_changes": 0,
    "api_incompatibilities": 1,
    "behavioral_changes": 0
  },
  "risk_propagation": {
    "primary_affected": ["evaluator_dynamic.py", "essence_classifier.py"],
    "secondary_affected": ["app.py", "router.py"],
    "tertiary_affected": []
  },
  "impact_matrix": [
    {
      "component": "evaluator_dynamic.py",
      "breaking_risk": 0.15,
      "perf_risk": 0.03,
      "subtle_risk": 0.08,
      "confidence": 0.92
    }
  ],
  "recommendation": {
    "action": "test_more",
    "rationale": "API change in secondary component. Compatibility layer required.",
    "Z_governance_stability": 0.819,
    "integration_cost": 0.5
  }
}
```

---

## Layer 4: COMMAND CENTER UI Panel

### Purpose

TIC 4層の可視化 + リアルタイム警告 + 意思決定支援

### Architecture

```
COMMAND CENTER (Flask app.py)
        ↓
  /api/tic/status
  /api/tic/layer_N
  /api/tic/alert
        ↓
  TIC Panel (frontend)
     ├─ Health Gauge (L0)
     ├─ Tech Watch Feed (L1)
     ├─ Sandbox Status (L2)
     ├─ Impact Heatmap (L3)
     └─ Recommendation Engine (L3→L4)
```

### Implementation Details

#### 4.1 Backend API Endpoints

**File:** `app.py` additions (or separate `interface/tic_api.py`)

```python
@app.route('/api/tic/status', methods=['GET'])
def tic_status():
    """TIC全層の統合ステータス"""
    return {
        "layer0": health_check_latest(),      # last 7 points
        "layer1": tech_watch_recent(),        # last 10 changes
        "layer2": sandbox_current_state(),    # in-progress experiments
        "layer3": latest_impact_analysis(),   # most recent recommendation
        "overall_risk": calculate_composite_risk(),
    }

@app.route('/api/tic/layer/<int:n>', methods=['GET'])
def tic_layer_status(n):
    """特定層の詳細"""
    ...

@app.route('/api/tic/alert', methods=['GET'])
def tic_alerts():
    """リアルタイム警告（WebSocket準備）"""
    alerts = [
        {
            "layer": 1,
            "severity": "warning",
            "message": "Python 3.12 compatibility issue detected in dependency X",
            "timestamp": "...",
            "action_required": true,
        }
    ]
    return alerts
```

#### 4.2 Frontend Panel

**File:** `static/tic_panel.html` / `js/tic_dashboard.js`

```html
<div class="tic-panel">
  <!-- Layer 0: Health -->
  <section class="tic-layer-0">
    <h3>System Health (L0)</h3>
    <gauge value="0.78"></gauge>
    <detail-table>7 checks, last: 2026-08-13 13:15</detail-table>
  </section>

  <!-- Layer 1: Tech Watch -->
  <section class="tic-layer-1">
    <h3>Tech Intelligence Watch (L1)</h3>
    <feed>
      <item timestamp="...">Python 3.12.1 released</item>
      <item timestamp="...">Flask 3.1.0 available (minor)</item>
    </feed>
  </section>

  <!-- Layer 2: Sandbox -->
  <section class="tic-layer-2">
    <h3>Tech Lab Experiments (L2)</h3>
    <experiment-list>
      <exp id="exp_001" status="in_progress" risk="low">
        Testing dependency_tool v2.1
      </exp>
    </experiment-list>
  </section>

  <!-- Layer 3: Impact Analysis -->
  <section class="tic-layer-3">
    <h3>Impact Analysis (L3)</h3>
    <heatmap rows="components" cols="risk_types"></heatmap>
    <recommendation action="test_more" confidence="0.92">
      Compatibility layer required for evaluator_dynamic.py
    </recommendation>
  </section>

  <!-- Risk Gauge -->
  <section class="composite-risk">
    <h3>Overall TIC Risk Level</h3>
    <gauge value="0.34"></gauge>
    <thresholds>
      <threshold level="safe" value="0.30"></threshold>
      <threshold level="caution" value="0.60"></threshold>
      <threshold level="alert" value="0.80"></threshold>
    </thresholds>
  </section>
</div>
```

#### 4.3 Real-time Updates

- Polling: `/api/tic/status` 30秒間隔
- WebSocket (future): `/ws/tic/stream` 即時通知

---

## Integration with JARVIS

### Perception Layer (L1) Completion

```
TIC Layer 0: System Health Observation
TIC Layer 1: Semantic Diff Detection
TIC Layer 2: Sandbox Isolation & Validation
TIC Layer 3: Impact Propagation Analysis
TIC Layer 4: Decision Support Dashboard
        ↓
   JARVIS Perception Layer ✓ COMPLETE
        ↓
   Context Reasoning (XYZ+TS)
   Evidence Validation (BEE)
   Governance (Human Gate)
   Execution Safety (Event Gate)
```

### Signal Flow to JARVIS

1. Layer 0 alert: "Memory usage 95%" → L1 anomaly detection
2. Layer 1 alert: "Dependency X update available" → L2 sandbox
3. Layer 2 result: "Breaking change in L2 experiment" → L3 impact
4. Layer 3 result: Impact matrix + recommendation → L4 dashboard → Human Gate
5. Human Gate decision → Event Gate → P-DERS recording

---

## Implementation Roadmap

### Phase 1 (Days 1-2): Layer 2 Sandbox

- [ ] `sandbox_manager.py` implementation
- [ ] FULL/PARTIAL/MONITORING isolation levels
- [ ] Snapshot & rollback mechanism
- [ ] CLI: `python sandbox_manager.py create <tech_name>`

### Phase 2 (Days 3-4): Layer 3 Impact Analyzer

- [ ] Dependency graph builder
- [ ] Breakage detection algorithms
- [ ] Risk propagation model
- [ ] Impact matrix generation
- [ ] Recommendation engine

### Phase 3 (Day 5): Layer 4 UI

- [ ] Flask API endpoints `/api/tic/*`
- [ ] Frontend HTML/CSS/JS
- [ ] Gauge/heatmap visualization
- [ ] Real-time polling integration
- [ ] COMMAND CENTER integration

### Phase 4 (Optional): Advanced

- [ ] WebSocket real-time push
- [ ] Historical TIC state tracking
- [ ] Machine learning anomaly detection
- [ ] Integration with Connector Framework

---

## Success Criteria

- [ ] Layer 2: 3+ experiments safely isolated & analyzed
- [ ] Layer 3: Impact matrix accurate (validated by manual review)
- [ ] Layer 4: Dashboard displays all 4 layers + alerts
- [ ] Integration: JARVIS Perception Layer marked COMPLETE
- [ ] Z-axis (Governance Stability) stability within ±0.05 throughout

---

## References

- MOCKA_OVERVIEW.json: tic_roadmap section
- JARVIS Architecture Mapping v1.0: Perception Layer (L1)
- TODO_205, TODO_206, TODO_207
