# MoCKA Naming Convention — Official Specification
# NAMING_CONVENTION.md
# Created: 2026-03-29
# Authority: nsjp_kimura
# Status: FIXED — do not change without governance approval

---

## 1. Core Principle

> "Names are the language of civilization.
>  When names drift, civilization drifts."

---

## 2. Architecture Overview
```
mocka_Receptor
      ↓
┌─────────────────────────────┐
│     mocka_insight_system    │
│                             │
│  mocka_Movement             │
│  (primary · cell cluster)   │
│                             │
│  shadow_Movement            │
│  (second heart · 75% guarantee · parallel verification) │
└─────────────────────────────┘
      ↓               ↓
acceptor:infield   acceptor:outfield
(store · memory)   (share · publish)
      ↓
  caliber群
(specialist modules)
```

---

## 3. Canonical Names (Fixed)

### 3.1 Entry Point

| Canonical Name  | Display Name    | Role                                          |
|-----------------|-----------------|-----------------------------------------------|
| mocka_receptor  | mocka_Receptor  | Single entry point. Receives any stimulus from outside. State is undefined until processed. Not 0 or 1 — it transforms based on context. |

### 3.2 Core System

| Canonical Name        | Display Name        | Role                                        |
|-----------------------|---------------------|---------------------------------------------|
| mocka_insight_system  | mocka_insight_system | Collective name for mocka_Movement + shadow_Movement |
| mocka_movement        | mocka_Movement      | Primary governance loop · cell cluster      |
| shadow_movement       | shadow_Movement     | Second heart · 75% resilience · parallel verification |

### 3.3 Acceptor Layer

| Canonical Name      | Display Name       | Role                              |
|---------------------|--------------------|-----------------------------------|
| acceptor_infield    | acceptor:infield   | Internal storage · memory · accumulation |
| acceptor_outfield   | acceptor:outfield  | External sharing · publishing · proof |

### 3.4 Loop Steps (Fixed)

| Step | Canonical Name | Description              |
|------|----------------|--------------------------|
| ①   | observation    | Detect · Input · Monitor |
| ②   | record         | Ledger · Structured storage |
| ③   | incident       | Detect anomaly · Flag event |
| ④   | recurrence     | Analyze failure patterns |
| ⑤   | prevention     | Learn · Institutionalize |
| ⑥   | decision       | Deliberate · Approve     |
| ⑦   | action         | Execute · Deploy         |
| ⑧   | audit          | Verify · Sign · Seal     |

### 3.5 Repository Names (Fixed)

| Canonical Name           | Role Classification  | Loop Position              |
|--------------------------|----------------------|----------------------------|
| MoCKA                    | heart                | ① Observe · ⑧ Audit        |
| mocka-knowledge-gate     | institutional_memory | ② Record                   |
| mocka-transparency       | transparency         | ③ Incident · ④ Recurrence  |
| mocka-external-brain     | orchestrator_bus     | ⑥ Decision                 |
| mocka-civilization       | blueprint            | ⑧ Audit → Institutionalize |
| mocka-runtime            | execution            | ⑦ Action                   |
| mocka-public             | public_proof         | ⑧ Audit output             |
| mocka-outfield           | public_network       | ① Observe input            |

---

## 4. Naming Rules

### File names (code)
```
mocka_receptor.py
shadow_movement.py
acceptor_infield.py
acceptor_outfield.py
```

### Display names (README / docs)
```
mocka_Receptor
mocka_Movement
shadow_Movement
acceptor:infield
acceptor:outfield
```

### Variables / functions (Python)
```
mocka_receptor
shadow_movement
acceptor_infield
acceptor_outfield
```

### Constants
```
MOCKA_RECEPTOR
SHADOW_MOVEMENT
ACCEPTOR_INFIELD
ACCEPTOR_OUTFIELD
```

---

## 5. Deprecated Names — Do Not Use

| Deprecated           | Canonical Replacement  |
|----------------------|------------------------|
| Ecosystem            | mocka_Movement         |
| InsertSystem         | mocka_Receptor         |
| insert_system        | mocka_Receptor         |
| mockaInsert          | mocka_Receptor         |
| ShadowMovement       | shadow_Movement        |
| PrimaryMovement      | mocka_Movement         |
| MoCKA Ecosystem      | mocka_Movement         |
| infield              | acceptor:infield       |
| outfield             | acceptor:outfield      |

---

## 6. Biological Analogy (Design Philosophy)
```
Receptor   = 細胞膜上の受容体
             外界の刺激を受け取る唯一の接点
             何になるかは文脈で決まる · 0-1ではない

Acceptor   = 受け取った信号の処理機構
  infield  = 内側へ · 記憶 · 蓄積
  outfield = 外側へ · 共有 · 展開

mocka_insight_system = 細胞核
  mocka_Movement   = 主機構（細胞の集まり）
  shadow_Movement  = 第二の心臓（免疫・冗長）

caliber群 = 細胞小器官
  各専門機能を独立して担う
```

---

## 7. Authority

This document is the single source of truth for all naming in MoCKA.
Changes require governance approval and must be recorded in the ledger.

Source: docs/SHADOW_MOVEMENT_PRINCIPLE.md
Map:    MOCKA_MOVEMENT_MAP.json
Date:   2026-03-29
