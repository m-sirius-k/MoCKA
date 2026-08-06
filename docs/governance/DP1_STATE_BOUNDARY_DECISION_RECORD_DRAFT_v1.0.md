# DP-1 State Boundary Decision Record Draft v1.0

## JARVIS Institutional Runtime における State Layer / Event Store / Human Authority Boundary

**文書番号:** (未採番)
**確定日:** (Human Authority 記入欄。第7章)
**Status:** **DRAFT — Decision Ledger 登録前**
**Decision Authority:** きむら博士 (Human Authority)
**Decision Ledger:** **未登録** (登録は Human Authority の指示待ち)
**Seal:** **未生成**

**入力資料:**
- `docs/governance/DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md` (commit 2636273)
- `docs/governance/DP1_STATE_BOUNDARY_DECISION_DRAFT_v0.1.md` (commit ee97354)

**基準文書:**
- `data/MOCKA_OVERVIEW.json:28-34` (憲法5原則)
- `DC_20260712_008` (Active) — Memory Governance Model
- `DC_20260705_008` / `DC_20260705_009` (Active) — Human Gate = State Management Layer
- `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md` — JARVIS / Human Gate の層原則

**CHANGE_START:** E20260807_593034273be7c

---

## 0. 本文書の位置付けと禁止事項

### 0.1 何であり、何でないか

| | |
|---|---|
| **本文書である** | Human Authority が下した DP-1 の判断を、Decision Ledger 登録前の裁定文書形式へ整理したもの |
| **本文書でない** | Decision Ledger の登録済みレコード / Seal / 実装指示 / Migration 計画 / 既存 Decision の supersede |

### 0.2 禁止事項の遵守状況

| # | 禁止事項 | 遵守状況 |
|---|---|---|
| 1 | Decision Ledger 登録 | **未実施** |
| 2 | Seal 生成 | **未実施** |
| 3 | 実装変更 | **未実施** (コード・スキーマ・データのいずれも変更していない) |
| 4 | 既存 Decision の supersede | **未実施** (実施・提案とも行っていない) |
| 5 | Migration 開始 | **未実施** |
| 6 | 追加設計判断 | **未実施** (本文書は受領した判断の記録であり、新たな設計判断を含まない) |

### 0.3 記録上の確認事項 (Human Authority 確認待ち)

本文書の作成にあたり、受領した指示の中に用語の対応関係が確定していない箇所が1件ある。**本文書はこれを断定せず、両表記をそのまま記録する。**

| 箇所 | 表記 |
|---|---|
| Decision Statement (第3章) | State Management = **Execution Layer** |
| Architecture Boundary (第4章) | 第4層 = **Action Layer** |

両者が同一層を指すか否かの確定は第7章 A-1 として保持する。

---

## 1. Decision Context

### 1.1 JARVIS Institutional Runtime 構築上の背景

JARVIS の層原則は既に確定している (`phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md`、逐語):

> **JARVIS is an intelligence layer.**
> **Human Gate is an authority layer.**

同文書および `phi_os/hab/jarvis_authority_boundary.md` は JARVIS の境界を次のとおり定める。

| Allowed | Forbidden |
|---|---|
| Search context / Explain system state / Detect inconsistencies / Prepare proposals / Evidence collection / Context analysis / State explanation / Risk detection / Decision proposal | Execute decisions / Change authority state / Modify audit history / Human decision replacement / Automatic approval / Automatic rejection / Authority escalation / Ledger modification |

JARVIS が `Explain system state` を担うためには、**何が State であるかが確定している必要がある。** JARVIS 能力の拡張に先立ち制度境界を固定するという上位方針 (`HAB_CORE_DEFINITION_v0.1.md` 0.1、きむら博士、逐語) が本 Decision の直接の前提である。

> 既存システムの全面改修は禁止。まず制度境界を固定し、その後 JARVIS 能力を拡張する。

### 1.2 既存 State 定義の衝突状況

DP-1 着手前の時点で、State に関する記述が複数の文書に分散し、位格の異なる記述が併存していた。

| 対象 | 記述 | 出典 | Status |
|---|---|---|---|
| Event / event_store | Observation Layer に属する。単独では load-bearing 記録として扱わない | `DC_20260712_008` | **Active** |
| Event / event_store | STATE LAYER の source of truth。真実の位置は event_store のみ | `minimal_safe_architecture_v1.md:31-44` | PROPOSED (Decision Ledger 参照 0件) |
| Human Gate | State Management Layer (非決定系の状態保留装置) | `DC_20260705_008` / `_009` | **Active** |
| Human Gate | authority layer | `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md` | Status 行なし |

加えて、State 関連の実体が層への割当なしに並存していた。

| 実体 | 観測された事実 |
|---|---|
| `runtime/state.json` | 互換性のない2つの書込元が同一パスに存在 (`runtime/action_selector.py` / `scripts/state/state_engine.py`)。実ファイルは前者のスキーマ。最終更新 2026-04-05 |
| `current_view` | 一次データ4系統からの再集計結果。永続先 `data/MOCKA_OVERVIEW_CURRENT.json` は生成されていない |
| Context Snapshot | 層への割当の根拠文書を確認できない |

さらに、`docs/governance/VOCABULARY_AUDIT_EVALUATION_v0.1.md:171` は憲法原則5 と Ledger 4候補の並立について次を記録している (逐語)。

> 文書上明示的に解消されていない緊張がある

### 1.3 DP-1 が必要となった理由

1. JARVIS が `Explain system state` を実行するために、State の正本定義が必要である (1.1)。
2. State に関する記述が Active Decision / PROPOSED / Status 行なし の各位格に分散し、同一対象について異なる層を指す記述が併存していた (1.2)。
3. State 関連の実体7件のうち、層への割当に単一かつ確定的な根拠を持つものは Decision Ledger の1件のみであった (`DP1_STATE_BOUNDARY_DECISION_DRAFT_v0.1.md` 3.2)。
4. DP-2 (Snapshot 定義) および DP-3 (Delta 定義) は DP-1 に依存するため、DP-1 未確定のまま後続を進められない。

---

## 2. Existing Decision Compatibility

### 2.1 `DC_20260712_008` — Memory Governance Model

| 項目 | 値 |
|---|---|
| decision_id | `DC_20260712_008` |
| title | DU#008: Event Store Trust Boundary Decision (Option C採択確定) |
| status | **Active** |
| approved_by | きむら博士 (Human Gate) |

#### 2.1.1 本 Decision における扱い

**`DC_20260712_008` は既存 Memory Governance Model として維持する。**

本 Decision は `DC_20260712_008` を supersede しない。同 Decision の status は Active のまま維持され、その定める Memory Model (2層) は引き続き有効である。

#### 2.1.2 `DC_20260712_008` が定める内容 (逐語)

> **MoCKA Memory Model(2層):**
> **[Durable Layer / 正本]** 対象=Decision Ledger, Integrity Ledger, Anchor Record, Governance Decision。用途=制度判断/長期記憶/監査基準。
> **[Observation Layer / 観測層]** 対象=Event, Runtime Trace, Experiment Log。用途=実験証跡/状態観測/再現補助。単独ではload-bearing記録として扱わない。

Observation から Durable への昇格条件4件 (Condition 1 Identity / 2 Visibility / 3 Integrity Reference / 4 Decision Relevance) および、昇格には別途 Human Gate Decision を要するという規定も、そのまま維持される。

#### 2.1.3 DP-1 との関係 — 別軸定義

**`DC_20260712_008` と DP-1 は、それぞれ異なる軸を定める。**

| | `DC_20260712_008` | DP-1 (本 Decision) |
|---|---|---|
| **モデル名** | **Memory Governance Model** | **Runtime State Reconstruction Model** |
| **軸** | 記録の制度的位格 (何を正本として制度判断・長期記憶・監査基準に用いるか) | Runtime における状態再構成 (何から現在状態を導出するか) |
| **用途** | 制度判断 / 長期記憶 / 監査基準 | Runtime State の再構成 / JARVIS の `Explain system state` |
| **Event の位置** | Observation Layer (観測層) | State Layer の Primary Source |

両者は同一対象 (Event) について異なる軸上の位置を定めるものであり、一方が他方を置き換える関係にない。**Memory Governance Model 上の Observation Layer 分類と、Runtime State Reconstruction Model 上の Primary Source 指定は、併存する。**

この2軸分離は、MoCKA において先例のある形式である (TODO_385: `status` と `contract_status` を、タスク進行度と契約ライフサイクル状態という異なる軸として別 enum に分離)。

#### 2.1.4 維持される制約

`DC_20260712_008` が定める以下は、本 Decision によって変更されない。

| # | 制約 |
|---|---|
| 1 | Durable Layer / 正本 の対象は Decision Ledger / Integrity Ledger / Anchor Record / Governance Decision である |
| 2 | 制度判断・長期記憶・監査基準には Durable Layer を用いる |
| 3 | Observation から Durable への昇格には4条件の充足と別途 Human Gate Decision を要する |
| 4 | `status:ok` は write 処理受付成功のみを意味し、永続取得・第三者検証・Durable 採用を保証しない |
| 5 | 制度記憶採用条件は write 成功 + Durable Ledger 記録 + id 取得確認の3点セットである |

### 2.2 `DC_20260705_008` / `DC_20260705_009` — Human Gate = State Management Layer

| 項目 | 値 |
|---|---|
| status | 両者とも **Active** |
| approved_by | きむら博士 |

#### 2.2.1 本 Decision における扱い

両 Decision は維持される。本 Decision はこれらを supersede しない。

#### 2.2.2 定める内容 (逐語、`DC_20260705_008`)

> (1) 自動検知系は、PENDING状態への投入のみを担当し、可否判断には一切関与しない。
> (2) Human Gate(phi_os/human_gate.py)は、PENDING状態の保持・一覧表示・状態遷移の受付窓口としてのみ機能する。それ自体が判断や自動応答を行うことは禁止する。
> (3) approve()/reject()の呼び出しは、実際に人間がUI/APIを操作した場合にのみ許可する。自動ロジック・推論結果による呼び出し経路は一切設けない。

#### 2.2.3 DP-1 との関係

本 Decision の DP-1-C (二層分離) は、`DC_20260705_008` が定める3つの責務分離を、Authority と Execution の層境界として明示するものである。

| `DC_20260705_008` の記述 | DP-1-C における層 |
|---|---|
| approve() / reject() は人間操作のみ | **Authority Layer** |
| PENDING 状態の保持・一覧表示・状態遷移の受付窓口 | **Execution Layer** (State Management) |

`DC_20260705_008` が同一モジュール (`phi_os/human_gate.py`) 内に置いた2つの責務を、層として分離して記述する。**モジュールの分割を意味しない** (第6章参照)。

### 2.3 その他の Active Decision との関係

| decision_id | 内容 | 本 Decision における扱い |
|---|---|---|
| `DC_20260731_003` | INC Lifecycle State Model v0.1 の導入 | 維持。DP-1 は INC 固有の状態モデルを変更しない |
| `DC_20260731_005` | 2軸モデル (INC進行軸 = 機械 / 承認軸 = 人間のみ)。承認軸は `phi_os/human_gate.py` と `human_gate_events` を再利用 | 維持。DP-1-C の Authority / Execution 分離と同型の分離である |
| `DC_20260713_003` | AUTO_SEAL Model B。`approved_by=human` を Seal 成立条件として必須化 | 維持。Authority Layer の実装済み制約として存続 |
| `DC_20260712_005` | Working Tree State の Baseline 固定 | 維持。対象が異なる |
| `DC_20260724_008` | MCP Recovery State の Baseline 固定 | 維持。対象が異なる |
| `DC_20260730_009` | Evidence Supremacy / 未検証文脈の隔離ルール | 維持。本 Decision の作成過程にも適用済み (第8章参照) |

---

## 3. Decision Statement

**以下は Human Authority (きむら博士) が下した判断である。**

### 3.1 DP-1-A — State の定義

> **State は Event history の fold 型として定義する。**

Runtime における State は、Event history を畳み込んだ結果として導出される。State は独立に保持される第一級の実体ではなく、Event history からの導出結果である。

### 3.2 DP-1-B — Event Store の位置

> **Event Store は State Layer の Primary Source である。**

Runtime State Reconstruction Model において、State Layer の一次供給源は Event Store (`data/mocka_events.db`) とする。

本項は Runtime State Reconstruction Model の軸における指定であり、`DC_20260712_008` が Memory Governance Model の軸において Event を Observation Layer に分類することと併存する (2.1.3)。

### 3.3 DP-1-C — Human Gate と State Management の二層分離

> **Human Gate は Authority Layer に属する。**
> **State Management は Execution Layer に属する。**

両者は別層とし、同一層として扱わない。

| 対象 | 層 | 根拠 |
|---|---|---|
| Human Gate (approve / reject の権限行使) | **Authority Layer** | `JARVIS_OPERATING_RULES_v0.1.md` (逐語): "Human Gate is an authority layer." |
| State Management (状態の保持・遷移の実行) | **Execution Layer** | `DC_20260705_008` (1)(2): 自動検知系は PENDING 投入のみ、Human Gate は受付窓口として機能する |

### 3.4 Decision Statement 一覧 (正式記載)

```
State:
    Event history fold 型

Event Store:
    State Layer の Primary Source

Human Gate:
    Authority Layer

State Management:
    Execution Layer
```

---

## 4. Architecture Boundary

本章は4層構造を整理する。各層について、**既存証拠 (本 Decision 以前から存在するもの)** と **裁定範囲 (本 Decision が定めるもの)** を分離して記載する。

### 4.1 Memory Layer

| 区分 | 内容 |
|---|---|
| **既存証拠** | `DC_20260712_008` (Active) が定める Memory Governance Model 2層。Durable Layer / 正本 = Decision Ledger / Integrity Ledger / Anchor Record / Governance Decision。Observation Layer / 観測層 = Event / Runtime Trace / Experiment Log |
| **裁定範囲** | 本 Decision は Memory Layer の内容を定めない。`DC_20260712_008` の定めがそのまま適用される (2.1.1) |
| **層名に関する既存参照** | `MEMORY_LAYER.md` および `memory/` モジュール群が同名で別概念 (4種記憶: episodic / semantic / procedural / skill) を定義している。両者の関係は本 Decision の裁定範囲外 (第7章 A-2) |

### 4.2 State Layer

| 区分 | 内容 |
|---|---|
| **既存証拠** | `minimal_safe_architecture_v1.md:31-44` (PROPOSED、Decision Ledger 参照 0件) が `[STATE LAYER] event_store(source of truth) / working_memory(cache) / todo.json(projection)` を記述。`mocka_full_static_structure_map_v1.md:51` および `mocka_phase10_human_gate_insertion_map_v1.md:27` (いずれも DRAFT) が `HAB STATE LAYER` を記述 |
| **裁定範囲** | **本 Decision が定める。** State = Event history fold 型 (3.1)。Event Store = State Layer の Primary Source (3.2) |
| **裁定範囲外** | `current_view` / `runtime/state.json` / Context Snapshot の State Layer 内における位置。既存の PROPOSED / DRAFT 記述との統合。層名の既存2用法との関係 (第7章 A-3) |

### 4.3 Authority Layer

| 区分 | 内容 |
|---|---|
| **既存証拠** | `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md` (逐語): "Human Gate is an authority layer."。`jarvis_authority_boundary.md`: Forbidden に Authority escalation / Automatic approval / Automatic rejection / Ledger modification。`DC_20260705_008` (3): approve() / reject() は人間操作のみ。`DC_20260713_003`: `approved_by=human` を Seal 成立条件として必須化 |
| **裁定範囲** | **本 Decision が定める。** Human Gate は Authority Layer に属し、State Management とは別層である (3.3) |
| **裁定範囲外** | `INSTITUTION_RUNTIME_v1.md` (IMPLEMENTED v1) の `authority_manager.py` と Authority Layer の関係 (第7章 A-4) |

### 4.4 Action Layer

| 区分 | 内容 |
|---|---|
| **既存証拠** | 既存参照は2件のみ (`MOCKA_FULL_ECOSYSTEM_UNDERSTANDING.md` / `docs/governance/phase3_execution_runtime_design_v1.md`)。確定した指示対象を確認できない |
| **裁定範囲** | 本 Decision は Action Layer の内容を定めない |
| **記録上の確認事項** | 第3章の Decision Statement は State Management の所属層を **Execution Layer** と記載する。本章の第4層は **Action Layer** である。両者の対応関係は本 Decision で断定せず、第7章 A-1 として保持する |

### 4.5 境界図

各層の記述のうち、本 Decision が定めるものを `[DP-1]`、既存証拠によるものを `[既存]`、裁定範囲外のものを `[範囲外]` と表記する。

```
  =================================================================
   JARVIS  (intelligence layer)                            [既存]
   出典: phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md
   Allowed  : Explain system state / Detect inconsistencies /
              Prepare proposals / Evidence collection ...
   Forbidden: Execute decisions / Change authority state /
              Automatic approval / Ledger modification ...
  =================================================================
        |  read only
        v
  +===============================================================+
  |  AUTHORITY LAYER                                              |
  +---------------------------------------------------------------+
  |  Human Gate                                          [DP-1]   |
  |    approve() / reject() の権限行使                            |
  |    人間操作のみ  (DC_20260705_008 (3))                [既存]  |
  |    approved_by=human が Seal 成立条件 (DC_20260713_003)[既存] |
  +---------------------------------------------------------------+
  |  authority_manager.py                              [範囲外]   |
  |    出典: INSTITUTION_RUNTIME_v1.md (IMPLEMENTED v1)           |
  +===============================================================+
        ^  権限行使 (人間のみ)          |  承認済みの状態遷移
        |                                v
  +===============================================================+
  |  EXECUTION LAYER  (State Management)                          |
  +---------------------------------------------------------------+
  |  State Management                                    [DP-1]   |
  |    状態の保持 / 一覧表示 / 状態遷移の受付窓口                 |
  |    自動検知系は PENDING 投入のみ (DC_20260705_008 (1))[既存]  |
  |    判断・自動応答は禁止 (DC_20260705_008 (2))         [既存]  |
  +===============================================================+
        ^
        |  状態の読み出し
        |
  +===============================================================+
  |  STATE LAYER                                                  |
  +---------------------------------------------------------------+
  |  State = Event history fold 型                       [DP-1]   |
  |                                                               |
  |  Primary Source: Event Store (data/mocka_events.db)  [DP-1]   |
  |                                                               |
  |  current_view / runtime/state.json /                          |
  |  Context Snapshot の位置                            [範囲外]  |
  +===============================================================+
        ^
        |  fold  (実装は本 Decision の範囲外。第6章)
        |
  +===============================================================+
  |  MEMORY LAYER                                                 |
  |  Memory Governance Model — DC_20260712_008 (Active)  [既存]   |
  +----------------------------+----------------------------------+
  |  Durable Layer / 正本      |  Observation Layer / 観測層      |
  |   Decision Ledger          |   Event                          |
  |   Integrity Ledger         |   Runtime Trace                  |
  |   Anchor Record            |   Experiment Log                 |
  |   Governance Decision      |                                  |
  |                            |  昇格には4条件 + 別途            |
  |  用途: 制度判断 /          |  Human Gate Decision を要する    |
  |        長期記憶 / 監査基準 |                                  |
  +----------------------------+----------------------------------+

  +===============================================================+
  |  ACTION LAYER                                      [範囲外]   |
  |  本 Decision は内容を定めない。既存参照2件                    |
  +===============================================================+

  注: Event は Memory Layer において Observation Layer に分類され
      (Memory Governance Model の軸)、同時に State Layer の
      Primary Source である (Runtime State Reconstruction Model の軸)。
      両者は異なる軸上の位置であり、併存する (2.1.3)。
```

---

## 5. Rejected Alternatives

本章は、DP-1 の裁定において**採用されなかった方式**を記録する。理由は比較可能な範囲に限る。

### 5.1 State を可変 DB として保持する方式

| 項目 | 内容 |
|---|---|
| **方式** | State を独立した可変ストアに保持し、更新操作によって現在状態を書き換える |
| **不採用の理由** | 憲法原則1 (`data/MOCKA_OVERVIEW.json:29`) は "Event ledger is append only" を定める。可変ストアを State の保持先とする方式では、状態の変更が append-only の記録を経由しない経路が生じる。採用された fold 型 (3.1) は、状態を導出結果として扱うため、この経路が発生しない |
| **観測されている事実** | `runtime/state.json` は可変ストア方式の実例である。同一パスに互換性のない2つの書込元が存在し (`runtime/action_selector.py` / `scripts/state/state_engine.py`)、最終更新は 2026-04-05 で停止している。また `working_memory.json` 破損インシデント (State Cache Corruption) に対する事後対応として、2026-06-22 から 06-23 に5件の PROPOSED 文書が作成されている |

### 5.2 Event Store を Observation Layer に限定する方式

| 項目 | 内容 |
|---|---|
| **方式** | Runtime State Reconstruction においても Event Store を観測用途に限定し、State Layer の Primary Source としない |
| **不採用の理由** | 本方式では、State Layer の Primary Source を別に定める必要が生じる。1.2 に示すとおり、State を保持する実体7件のうち層への割当に単一かつ確定的な根拠を持つものは Decision Ledger の1件のみであり、Event Store に代わる Primary Source の候補が確定していない。採用された方式 (3.2) は、既に単一書込経路 (`phi_os/event_gate.process_event()`、TODO_322) を持つ Event Store を Primary Source とする |

> **重要 — 本項の適用範囲:**
> 本項の不採用は、**DP-1 の軸 (Runtime State Reconstruction Model) における候補**に対するものである。
> `DC_20260712_008` が **Memory Governance Model の軸**において Event を Observation Layer に分類することは、本 Decision によって維持される (2.1.1 / 2.1.4)。両者は異なる軸上の記述であり、本項は後者を対象としない。

### 5.3 Human Gate と State Management を同一層化する方式

| 項目 | 内容 |
|---|---|
| **方式** | Human Gate と State Management を単一の層として扱い、権限行使と状態遷移の実行を同一層に置く |
| **不採用の理由** | `DC_20260705_008` (Active) は、Human Gate について (1) 自動検知系は PENDING 投入のみで可否判断に関与しない (2) Human Gate は受付窓口としてのみ機能し判断・自動応答を行わない (3) approve() / reject() は人間操作のみ、という3つの責務分離を既に定めている。同一層化した場合、この分離が層構造上に表現されない。採用された二層分離 (3.3) は、既に確定している責務分離を層境界として明示する |
| **同型の先例** | `DC_20260731_005` (Active) は INC について、進行軸 (機械が進める) と承認軸 (人間のみが進める) の2軸モデルを採用している |

---

## 6. Implementation Boundary

### 6.1 本 Decision の性質

**本 Decision は Architecture Definition であり、実装変更を直接許可しない。**

本 Decision の採択によって、以下はいずれも許可されない。

| # | 対象 |
|---|---|
| 1 | コードの変更 |
| 2 | スキーマの変更 |
| 3 | データの変更・移行 |
| 4 | モジュールの分割・統合 (3.3 の二層分離は層としての記述であり、`phi_os/human_gate.py` の分割を意味しない) |
| 5 | `runtime/state.json` の書込元競合の解消 |
| 6 | `current_view` の永続化の開始 |
| 7 | fold の実装 |
| 8 | `_STATE_COLUMNS` の運用開始 |

### 6.2 Migration Plan の扱い

**Migration Plan は別 Decision の対象とする。** 本 Decision は Migration の開始を許可しない。

### 6.3 実装着手前に確認を要する既知の事実

以下は本 Decision の作成過程で観測された事実である。**本 Decision はこれらに対する対処を定めない。** Migration Plan を扱う別 Decision の入力として記録する。

| # | 事実 | 出典 |
|---|---|---|
| 1 | fold の実装は存在しない。`phi_os/event_replay.py:64-72` の `replay()` は `what_type` によるグループ化であり、状態を縮約する畳み込みではない | `DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md` 3.3 |
| 2 | `_STATE_COLUMNS` のうち `change_type` / `impact_scope` / `impact_result` は標本200件で使用実績ゼロ。`before_state` は194件 (97.0%) が null | 同 3.3 |
| 3 | 標本は `claude_mcp` が181件 (90.5%) を占め、DB全体 19,360件 (25型) に対する代表性はない | 同 7.4 |
| 4 | `runtime/state.json` に互換性のない2つの書込元が存在する | 同 3.2 |
| 5 | `current_view` の永続先 `data/MOCKA_OVERVIEW_CURRENT.json` は生成されていない | 同 3.1 |
| 6 | Decision Ledger の現在有効な決定集合を機械的に導出する経路は現状存在しない (`superseded_by` が全203件 null、supersede 対象13件中11件が Active のまま) | `STATE_BOUNDARY_AUDIT_v0.2` 1.2(c) |
| 7 | `registry_store` (KN-004) の実体はリポジトリ外 (`PlanningCaliber/workshop/registry_kn004`) | `DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md` 3.1 |

---

## 7. Human Authority

### 7.1 承認欄

```
approved_by:   ______________________________________________

approved_at:   ______________________________________________

Decision ID:   ______________________________________________
               (Decision Ledger 登録時に採番。DC_YYYYMMDD_NNN)

Decision Ledger:  未登録
Seal:             未生成
```

### 7.2 本 Decision に伴い確認を要する事項

以下は本 Decision の裁定範囲外であり、確認を要する。

| ID | 事項 | 参照 |
|---|---|---|
| **A-1** | Decision Statement の **Execution Layer** と Architecture Boundary の **Action Layer** の対応関係。同一層を指すか、別層か | 0.3 / 4.4 |
| **A-2** | 層名 Memory Layer と、既存の `MEMORY_LAYER.md` / `memory/` (4種記憶) の関係 | 4.1 |
| **A-3** | 層名 State Layer と、既存の HAB STATE LAYER (DRAFT) および `minimal_safe_architecture_v1.md` の STATE LAYER (PROPOSED) の関係 | 4.2 |
| **A-4** | `INSTITUTION_RUNTIME_v1.md` の `authority_manager.py` (IMPLEMENTED v1) と Authority Layer の関係 | 4.3 |
| **A-5** | `current_view` / `runtime/state.json` / Context Snapshot の State Layer 内における位置 | 4.2 |
| **A-6** | 分類B の5件 (PROPOSED、2026-06-22 から 06-23、Decision Ledger 参照 0件) の処遇 | `DP1_STATE_BOUNDARY_DECISION_DRAFT_v0.1.md` 1.2 |
| **A-7** | `HAB_CORE_DEFINITION_v0.1.md` (DRAFT未裁定) が定義する Canonical State と本 Decision の State 定義の関係 | 同 1.3 |
| **A-8** | Decision Ledger 登録の実施可否と実施時期 | 7.1 |

### 7.3 Decision Ledger 登録時の写像 (参考)

登録が指示された場合の `mocka_decision_write` への写像を示す。**本文書は登録を行わない。**

| Ledger フィールド | 充填元 |
|---|---|
| `title` | 本文書のタイトル |
| `context` | 第1章 Decision Context |
| `alternatives` | 第5章 Rejected Alternatives (3件) |
| `decision` | 第3章 Decision Statement |
| `rationale` | 第2章 Existing Decision Compatibility + 第5章の理由 |
| `impact` | 第6章 Implementation Boundary |
| `related_documents` | 入力資料2件 + 基準文書 |
| `related_events` | E20260807_593034273be7c ほか CHANGE イベント |
| `approved_by` | 7.1 記入欄 |
| `status` | `Active` |
| `supersedes` | **null** (本 Decision はいかなる既存 Decision も supersede しない) |

---

## 8. 本文書の作成条件

### 8.1 Evidence Supremacy の適用

`DC_20260730_009` (Active) が定める5段階確認順序を、本文書の作成過程においても適用した。適用の結果として、以下1件が未検証文脈として隔離されている。

| 対象 | 状態 |
|---|---|
| "PHL (最小設問生成)" | **隔離中。** 一次証拠では PHL = Persistent History Layer (文脈保持・再注入)。"最小設問生成" はリポジトリ全文検索および Event Ledger 検索で 0件。解除は Human Authority のみが行える |

### 8.2 本文書の限界

1. 本文書は Claude Code Web 環境から作成された。リポジトリの clone は shallow (直近24時間) である。
2. `data/decisions/decision_ledger.jsonl` および `data/mocka_events.db` は本環境に不在であり、Decision Ledger (203件) と Event の観測は MCP 応答を経由した間接観測である。
3. Decision Ledger 全203件のうち、本文書が内容を確認したのは State 関連の11件である。
4. 本ファイルは新規作成のみである。既存ファイルの変更は行っていない。commit は CLAUDE.md TODO_382 に従いブランチ `claude/mocka-diff-state-comparison-5w2xt1` に対して実施する。**main への直接 commit は行わない。**
5. **Decision Ledger への登録および Seal 生成は行っていない。**

---

## 9. 参照

### 9.1 維持される Active Decision

`DC_20260712_008` (Memory Governance Model) / `DC_20260705_008` / `DC_20260705_009` (Human Gate = State Management Layer) / `DC_20260731_003` / `DC_20260731_005` / `DC_20260713_003` / `DC_20260712_005` / `DC_20260724_008` / `DC_20260730_009`

**本 Decision はこれらのいずれも supersede しない。**

### 9.2 制度文書

`data/MOCKA_OVERVIEW.json:28-34` (憲法5原則) / `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md` / `phi_os/hab/jarvis_authority_boundary.md` / `docs/governance/HAB_CORE_DEFINITION_v0.1.md` / `docs/governance/minimal_safe_architecture_v1.md` / `docs/governance/VOCABULARY_AUDIT_EVALUATION_v0.1.md:171` / `INSTITUTION_RUNTIME_v1.md` / `MEMORY_LAYER.md`

### 9.3 入力資料

`docs/governance/DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md` (commit 2636273) / `docs/governance/DP1_STATE_BOUNDARY_DECISION_DRAFT_v0.1.md` (commit ee97354)

### 9.4 実装

`phi_os/event_gate.py` (process_event 単一経路) / `phi_os/event_replay.py:5,18-22,64-72` / `phi_os/human_gate.py:23,26-32,64-65` / `phi_os/runtime/authority_manager.py` / `scripts/state/overview_current_generator.py:26,116,138` / `scripts/state/state_engine.py:10,42` / `runtime/action_selector.py:14,118-119`
