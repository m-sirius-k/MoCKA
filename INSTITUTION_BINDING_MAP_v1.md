# INSTITUTION_BINDING_MAP_v1.md
## Artifact → Meaning → Institution → Gate 接続マップ
**作成日:** 2026-06-16
**フェーズ:** MoCKA Phase 4 — Binding Layer制度監査
**状態:** DRAFT v1

---

## マップ構造

```
Artifact
  └─ Meaning
       └─ Institution
            └─ Gate
```

---

## Institution定義

| Institution | 説明 | 主管Gate |
|---|---|---|
| **PHI-OS** | 制度OS。Event Gate・Knowledge Gate・Module Gateの制度権威 | Event Gate, Knowledge Gate, Module Gate |
| **MoCKA** | 中核制度機関。全Artifactの制度登録・ガバナンス主体 | Document Gate, Event Gate, Release Gate |
| **Orchestra** | イベント実行・セッション管理・タイムライン機関 | Event Gate, Module Gate |
| **Relay** | セッション間引き継ぎ・外部インターフェース機関 | Module Gate |
| **Memory** | 知識保全・記憶管理機関 | Knowledge Gate |
| **vasAI** | 自律エージェント実験機関 | Experiment Gate |
| **mini-MoCKA** | MoCKA縮小実験機関 | Experiment Gate |
| **共通制度** | 公開・外部向け制度。複数Institutionが共有 | Release Gate, Document Gate |

---

## Gate定義

| Gate | 説明 | 通過条件 |
|---|---|---|
| **Event Gate** | イベントの制度的受け付け・検証・記録 | EventスキーマへのBinding、Validator通過 |
| **Knowledge Gate** | 知識Artifactの登録・検索・参照制御 | Meaningが KNOWLEDGE/PHASE_RECORD/DESIGN のいずれか |
| **Module Gate** | モジュールの登録・依存関係・Lifecycle管理 | Module Registryへの登録、Interface定義 |
| **Prompt Gate** | プロンプト・指示書の制度的検証と発行 | Governance承認、テンプレート適合 |
| **Release Gate** | 外部公開・配布物の制度的検査 | Version確定、Verify Pack生成、Seal済み |
| **Experiment Gate** | 実験Artifactの登録・評価・昇格管理 | Experiment Record存在、Results記録 |
| **Document Gate** | ドキュメントの制度的登録・版管理 | Meaning確定、Naming Convention準拠 |

---

## 主要接続マップ

---

### PHI-OS 接続ツリー

```
phi_os/event_gate.py
  └─ SYSTEM_CORE
       └─ PHI-OS
            └─ Event Gate [CONNECTED]

phi_os/gate_schema.py
  └─ DESIGN
       └─ PHI-OS
            └─ Event Gate [CONNECTED]

phi_os/gate_validator.py
  └─ SYSTEM_CORE
       └─ PHI-OS
            └─ Event Gate [CONNECTED]

core_kernel/phios_integration/
  └─ SYSTEM_CORE
       └─ PHI-OS
            └─ Module Gate [CONNECTED]

knowledge-gate/
  └─ SYSTEM_CORE
       └─ PHI-OS
            └─ Knowledge Gate [PARTIAL]

mocka-knowledge-gate/
  └─ SYSTEM_CORE
       └─ PHI-OS
            └─ Knowledge Gate [CONNECTED]

PlanningCaliber/workshop/phi-os/
  └─ EXPERIMENT
       └─ PHI-OS
            └─ Experiment Gate [PARTIAL]
```

---

### MoCKA 接続ツリー

```
core_kernel/
  ├─ core_store/         → SYSTEM_CORE → MoCKA → Module Gate [CONNECTED]
  ├─ event_contracts/    → SYSTEM_CORE → MoCKA → Event Gate  [CONNECTED]
  ├─ governance/         → GOVERNANCE  → MoCKA → Module Gate [CONNECTED]
  ├─ prism/              → SYSTEM_CORE → MoCKA → Module Gate [CONNECTED]
  └─ (各サブモジュール)

governance/
  ├─ registry.json       → GOVERNANCE  → MoCKA → Document Gate [CONNECTED]
  ├─ approval_flow.json  → GOVERNANCE  → MoCKA → Document Gate [CONNECTED]
  ├─ governance_event.json → GOVERNANCE → MoCKA → Event Gate  [CONNECTED]
  └─ history/REC-*.md    → PHASE_RECORD → MoCKA → Document Gate [CONNECTED]

docs/CONSTITUTION.md
  └─ GOVERNANCE → MoCKA → Document Gate [CONNECTED]

docs/governance/MODULE_*.md
  └─ REQUIREMENT → MoCKA → Document Gate [CONNECTED]

records/
  └─ PHASE_RECORD → MoCKA → Document Gate [CONNECTED]

outbox/verify_pack/
  └─ RELEASE → MoCKA → Release Gate [CONNECTED]

transparency/
  └─ GOVERNANCE → MoCKA → Document Gate [CONNECTED]

mocka-archive/
  └─ ARCHIVE → MoCKA → (参照時Document Gate) [CONNECTED]

mocka-core-private/
  └─ SYSTEM_CORE → MoCKA → Module Gate [PARTIAL]

mocka-docs/
  └─ REQUIREMENT → MoCKA → Document Gate [CONNECTED]

mocka-transparency/
  └─ GOVERNANCE → MoCKA/共通制度 → Document Gate [CONNECTED]

production_certification/
  └─ GOVERNANCE → MoCKA → Release Gate [PARTIAL]

docs/incidents/INC-*.md
  └─ INCIDENT → MoCKA → Event Gate [CONNECTED]
```

---

### Orchestra 接続ツリー

```
core_kernel/orchestra/
  ├─ event_bus.py        → SYSTEM_CORE → Orchestra → Event Gate  [CONNECTED]
  ├─ orchestra_engine.py → SYSTEM_CORE → Orchestra → Module Gate [CONNECTED]
  ├─ replay_engine.py    → SYSTEM_CORE → Orchestra → Event Gate  [CONNECTED]
  ├─ session_state.py    → SYSTEM_CORE → Orchestra → Module Gate [CONNECTED]
  └─ timeline_api.py     → SYSTEM_CORE → Orchestra → Event Gate  [CONNECTED]

core_kernel/orchestra_core/
  └─ SYSTEM_CORE → Orchestra → Module Gate [PARTIAL]
  ※ orchestra/ と orchestra_core/ が並立 → Version分岐リスク

PlanningCaliber/workshop/Orchestra_Project/
  └─ EXPERIMENT → Orchestra → Experiment Gate [PARTIAL]

caliber/orchestra/
  └─ EXPERIMENT → Orchestra → Experiment Gate [CONNECTED]
```

---

### Relay 接続ツリー

```
core_kernel/relay_core/
  ├─ relay_session.py    → SYSTEM_CORE → Relay → Module Gate [CONNECTED]
  └─ session_relay.py    → SYSTEM_CORE → Relay → Module Gate [CONNECTED]

Relay_Project/ (sirok root)
  └─ SYSTEM_CORE → Relay → Module Gate [ORPHAN]
  ※ core_kernel/relay_core/ との制度接続が未確認

PlanningCaliber/workshop/Relay_Project/
  └─ EXPERIMENT → Relay → Experiment Gate [PARTIAL]

mocka-outfield/
  └─ HANDOFF → Relay/MoCKA → Document Gate [PARTIAL]
```

---

### Memory 接続ツリー

```
core_kernel/memory_core/
  ├─ memory_store.py     → SYSTEM_CORE → Memory → Knowledge Gate [CONNECTED]
  └─ record.py           → SYSTEM_CORE → Memory → Knowledge Gate [CONNECTED]

memory/
  └─ SYSTEM_CORE → Memory → Knowledge Gate [CONNECTED]

mocka-external-brain/
  └─ KNOWLEDGE → Memory → Knowledge Gate [PARTIAL]

PlanningCaliber/workshop/memory/
  └─ EXPERIMENT → Memory → Experiment Gate [PARTIAL]
```

---

### 共通制度 接続ツリー

```
mocka-public/
  ├─ RELEASE → 共通制度 → Release Gate [CONNECTED]
  └─ docs/   → KNOWLEDGE → 共通制度 → Document Gate [CONNECTED]

mocka-civilization/
  └─ KNOWLEDGE → 共通制度/MoCKA → Document Gate [CONNECTED]

mocka-civilization/blueprint/
  └─ DESIGN → 共通制度 → Document Gate [CONNECTED]
```

---

### vasAI / mini-MoCKA 接続ツリー

```
PlanningCaliber/workshop/vasAI_Project/
  └─ EXPERIMENT → vasAI → Experiment Gate [ORPHAN]
  ※ vasAI Institutionへの正式Binding未完了

PlanningCaliber/workshop/mini-mocka-series/
  └─ EXPERIMENT → mini-MoCKA → Experiment Gate [ORPHAN]
  ※ mini-MoCKA Institutionへの正式Binding未完了
```

---

## 全Binding状態サマリー

| Binding状態 | 件数 | 割合 |
|---|---|---|
| CONNECTED | 42 | 36% |
| PARTIAL | 52 | 45% |
| SHADOW | 9 | 8% |
| ORPHAN | 11 | 9% |
| DEPRECATED | 2 | 2% |
| UNKNOWN | 3 | 3% |
| **合計** | **119** | **100%** |

---

## Institution別Artifact分布

| Institution | CONNECTED | PARTIAL | SHADOW/ORPHAN/他 |
|---|---|---|---|
| MoCKA | 28 | 35 | 12 |
| PHI-OS | 7 | 4 | 0 |
| Orchestra | 6 | 3 | 0 |
| Relay | 2 | 2 | 1 |
| Memory | 3 | 2 | 0 |
| 共通制度 | 5 | 2 | 0 |
| vasAI | 0 | 0 | 1 |
| mini-MoCKA | 0 | 0 | 1 |
| 未定 | 0 | 0 | 3 |

---

## 制度接続の設計原則

### 原則1: 一意性
すべてのArtifactは必ず1つの主Meaningを持つ。

### 原則2: 単一Institution帰属
Artifactは1つの主Institutionに帰属する。  
複数Institutionに関与する場合は「主Institution」と「副Institution」を区別して記録する。

### 原則3: Gate単一化
1つのArtifactが通過するGateは1つを主とし、副Gateは参照のみとする。

### 原則4: Binding伝播
親ディレクトリのBindingは子Artifactに原則的に継承される。  
子ArtifactがSHADOWまたはORPHANの場合は親から切断と見なす。

### 原則5: Deprecation不可逆
DEPRECATEDとなったArtifactは後継実装なしにはCONNECTEDに戻らない。

---

*最終更新: 2026-06-16*
