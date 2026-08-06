# DP-1 State Boundary Decision Draft v0.1

## JARVIS Institutional Runtime における State Layer 境界

**文書番号:** (未採番)
**作成日:** 2026-08-07
**工程:** DP-1 State Boundary Definition — Human Gate 裁定用 Decision Draft
**状態:** **裁定前資料。裁定結果なし / 推奨なし / 選択なし / Human Authority 判断待ち**
**CHANGE_START:** E20260807_9775174934c0b

**基礎資料:** `docs/governance/DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md` (commit 2636273)

**上位方針 (きむら博士、`HAB_CORE_DEFINITION_v0.1.md` 0.1 より引用):**

> 既存システムの全面改修は禁止。まず制度境界を固定し、その後 JARVIS 能力を拡張する。

---

## 0. 禁止事項の遵守状況

| # | 禁止事項 | 遵守状況 |
|---|---|---|
| 1 | 裁定結果の付与 | 遵守 (第2章の裁定必要事項は問いのみ。答えを記載していない) |
| 2 | 推奨案の選択 | 遵守 (候補間の選択・推奨・優劣評価を一切行っていない) |
| 3 | 既存Decision supersede | 遵守 (supersede の実施・提案とも行っていない) |
| 4 | 実装変更 | 遵守 (コード・スキーマ・データのいずれも変更していない) |
| 5 | Decision Ledger 登録 | 遵守 (未登録) |
| 6 | 既存ファイルの変更 | 遵守 (本ファイル1件の新規作成のみ) |

### 0.1 用語の区別 (重要)

本資料には2種類の A / B / C が現れる。混同を避けるため以下のとおり表記を固定する。

| 表記 | 指すもの | 記載箇所 |
|---|---|---|
| **分類A / 分類B / 分類C** | State関連定義の**文書ステータス区分** (Active Decision / Proposed Architecture / Draft未裁定) | 第1章 |
| **候補A / 候補B / 候補C-1 / 候補C-2** | **DP-1 の裁定候補** (State の正本定義) | 第2章 |

---

## 1. State関連定義の3分類

### 1.1 分類A — Active Decision

Decision Ledger に記録され、`status = Active` のもの。全件 Human Gate 承認済み。

| # | decision_id | 定義している State 概念 | approved_by |
|---|---|---|---|
| A-1 | `DC_20260712_008` | **MoCKA Memory Model (2層)** — Durable Layer / 正本 (Decision Ledger, Integrity Ledger, Anchor Record, Governance Decision) と Observation Layer / 観測層 (Event, Runtime Trace, Experiment Log)。Observation は単独では load-bearing 記録として扱わない | きむら博士 (Human Gate) |
| A-2 | `DC_20260705_008` | **Human Gate = State Management Layer** (非決定系の状態保留装置)。自動検知系は PENDING 投入のみ。approve/reject は人間操作のみ | きむら博士 |
| A-3 | `DC_20260705_009` | A-2 の参照先ID訂正 (TODO_387 -> PHI-OS-HUMAN-GATE-STATE-MODEL-V1)。**結論は変更せず維持** | きむら博士 |
| A-4 | `DC_20260731_003` | **INC Lifecycle State Model v0.1** の導入。承認相当の状態への遷移を実行できる主体は人間に限定 | きむら博士 |
| A-5 | `DC_20260731_005` | **2軸モデル** — INC進行軸 (DETECTED/ANALYZED/PUBLISHED/CLOSED、機械が進める) / 承認軸 (PENDING/APPROVED/REJECTED、人間のみ)。承認軸は `phi_os/human_gate.py` と `human_gate_events` を再利用。INC専用状態機械は導入しない | きむら博士 |
| A-6 | `DC_20260713_003` | AUTO_SEAL Boundary Design v1.0 Model B。`approved_by=human` を Seal 成立条件として必須化 | きむら博士 |
| A-7 | `DC_20260712_005` | Working Tree State の Baseline 固定 (Option A) | きむら博士 |
| A-8 | `DC_20260724_008` | MCP Recovery State の Baseline 固定 | きむら博士 |

**分類A の性質:** 裁定済み。本資料はこれらを変更・supersede しない。

### 1.2 分類B — Proposed Architecture

`Status: PROPOSED` を持つ設計提案。**いずれも Decision Ledger 参照 0件。裁定されていない。**

| # | 文書 | Date | Status (逐語) | State に関する記述 |
|---|---|---|---|---|
| B-1 | `minimal_safe_architecture_v1.md` | 2026-06-23 | PROPOSED (設計提案。即時コード変更を伴わない) | `:31-38` `[STATE LAYER] event_store(source of truth) / working_memory(cache) / todo.json(projection)`。`:44` "真実の位置は `event_store` のみとする" |
| B-2 | `execution_gate_v1.md` | 2026-06-23 | PROPOSED (working_memory.json破損インシデントの事後対応) | `:16` "State Layer健全性" / `:119` "State Layer  FIXED" |
| B-3 | `state_dependency_risk_map_v1.md` | 2026-06-23 | PROPOSED (同インシデントの事後分析) | State 依存のリスクマップ |
| B-4 | `runtime_boundary_v1.md` | 2026-06-23 | PROPOSED (制度規約案) | Runtime 境界 |
| B-5 | `import_safety_rule_v1.md` | 2026-06-22 | PROPOSED (制度規約案) | import 安全規約 |

**分類B の性質:** B-1 から B-5 は同一インシデント (working_memory.json 破損 / State Cache Corruption) への一連の事後対応として 2026-06-22 から 06-23 に作成された文書群である。**5件とも PROPOSED のまま裁定されていない。**

### 1.3 分類C — Draft / 未裁定資料

| # | 文書 | Date | Status (逐語) | State に関する記述 |
|---|---|---|---|---|
| C-1 | `HAB_CORE_DEFINITION_v0.1.md` | 2026-08-04 | **DRAFT(未裁定)**。Decision Ledger 登録: なし。実装: なし | 副題に **Canonical State** / Actor / Transition Ledger / JARVIS 権限境界 |
| C-2 | `mocka_full_static_structure_map_v1.md` | 2026-06-24 | DRAFT (参照文書として追加。**pre-authorization state を解除しない**) | `:51` `[HAB STATE LAYER]` を最上位に配置 |
| C-3 | `mocka_phase10_human_gate_insertion_map_v1.md` | 2026-06-24 | DRAFT (同上) | `:27` `[HAB State Layer]` |
| C-4 | `DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md` | 2026-08-07 | 裁定前資料 (commit 2636273) | 本資料の基礎資料 |
| C-5 | `STATE_DIFF_ENGINE_CORE_DECISION_PREP_v0.1` | 2026-08-06 | 裁定前資料。**会話上のドラフト、未ファイル化** | DP-1/DP-2/DP-3 第一裁定資料 |
| C-6 | `STATE_BOUNDARY_AUDIT_v0.2` | 2026-08-06 | 監査結果。**会話上のドラフト、未ファイル化** | AJ-1 から AJ-5 の初出 |
| C-7 | **本資料** | 2026-08-07 | 裁定前資料 | — |

### 1.4 3分類に収まらないもの

以下は Active Decision でも PROPOSED でも DRAFT でもない。**分類の確定を Human Gate 判断項目とする (第4章 HG-6)。**

| 文書 | Status | 内容 |
|---|---|---|
| `INSTITUTION_RUNTIME_v1.md` | **IMPLEMENTED v1** (2026-06-16) | PHI-OS Institution Runtime。`authority_manager.py` / `gate_registry.py` / `compliance_engine.py` 等を含む。Decision Ledger 記録の有無は未確認 |
| `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md` | **Status行なし** | "JARVIS is an intelligence layer. Human Gate is an authority layer." |
| `phi_os/hab/jarvis_authority_boundary.md` | **Status行なし** | JARVIS の Allowed / Forbidden 境界 |

### 1.5 分類間の記述の並置

以下は各分類の記述を並置したものであり、整合判定・優劣評価・裁定は行っていない。

| 対象 | 分類A の記述 | 分類B の記述 |
|---|---|---|
| **Event / event_store の位格** | A-1 (`DC_20260712_008`, Active, 2026-07-12): **Observation Layer**。単独では load-bearing 記録として扱わない | B-1 (`minimal_safe_architecture_v1.md`, PROPOSED, 2026-06-23): **STATE LAYER の source of truth**。真実の位置は event_store のみ |
| **Human Gate の位格** | A-2 / A-3 (Active): **State Management Layer** | 1.4 `JARVIS_OPERATING_RULES_v0.1.md`: **authority layer** |

---

## 2. DP-1 候補の整理

以下は各候補について、前提 / 依存Decision / 変更範囲 / 影響範囲 / 裁定必要事項のみを記載する。**優劣評価・推奨・選択は行っていない。**

### 2.1 候補A — State = Event history fold

| 項目 | 内容 |
|---|---|
| **前提** | (1) Event が Durable 相当として扱えること。(2) Event から状態への畳み込み (fold) が実装されること。(3) 畳み込みの入力となる `before_state` / `change_type` / `impact_scope` / `impact_result` が運用されること |
| **依存Decision** | **A-1 `DC_20260712_008`** (Event を Observation Layer に置き、単独では load-bearing 記録として扱わないと明記。Observation から Durable への昇格には4条件の実測と別途 Human Gate Decision を要する) |
| **変更範囲** | (a) A-1 との関係整理 (b) fold の新規実装 — `phi_os/event_replay.py:64-72` の `replay()` は `what_type` によるグループ化であり fold ではない (c) `_STATE_COLUMNS` の運用開始 (d) Decision Ledger / Human Gate events / Registry を fold 対象に含めるか否かの規定 |
| **影響範囲** | (i) A-1 の Memory Model 2層構造 (ii) `phi_os/event_replay.py` (iii) `phi_os/event_gate.process_event()` の書込経路 — `_STATE_COLUMNS` 運用開始時に全書込元が影響を受ける (iv) 分類B の B-1 (記述が一致する) (v) DP-2 (Snapshot) / DP-3 (Delta) の定義基盤 |
| **裁定必要事項** | Q-A1: A-1 と併存させられるか。併存できない場合、DP-1 の裁定は A-1 に対して何を行うか (本資料は supersede を提案しない)。Q-A2: fold の実装と `_STATE_COLUMNS` の運用開始を前提条件とするか、定義のみ先行させるか |

**観測されている事実 (参考):** `data/events_latest.json` 200件の標本において、`before_state` は 194件 (97.0%) が null、`change_type` / `impact_scope` / `impact_result` は 200件 (100%) が null である。標本は `claude_mcp` が181件 (90.5%) を占め、DB全体 19,360件 (25型) に対する代表性はない。

### 2.2 候補B — State = 複数系統State集合

| 項目 | 内容 |
|---|---|
| **前提** | (1) 系統の列挙が確定していること。(2) 各系統について現在状態を導出できること。(3) 系統間の整合を検証する手段があること |
| **依存Decision** | **A-1** (Durable / Observation の2層が複数系統の並立を前提とする)、**A-2 / A-3** (Human Gate を State Management Layer と定義済み)、**A-5** (2軸モデルを採用済み) |
| **変更範囲** | (a) 系統集合の確定 — A-1 の Durable 4対象 (Decision Ledger / Integrity Ledger / Anchor Record / Governance Decision) と、Event Store / Human Gate / Registry を含む集合は一致しない (b) 系統間の整合検証機構 (c) 各系統の現在状態の導出規定 |
| **影響範囲** | (i) 憲法原則5 との関係 — `VOCABULARY_AUDIT_EVALUATION_v0.1.md:171` が "文書上明示的に解消されていない緊張がある" と既に記録している (ii) Ledger 4候補 (`ledger.json` / `mocka_events.db`+`audit_trigger.py` / `decision_ledger.jsonl` / `KN_SERIES_LEDGER`) — `VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md:68-71` で**4候補とも判定保留** (iii) `registry_store` (KN-004) — 実体がリポジトリ外 (`PlanningCaliber/workshop/registry_kn004`) |
| **裁定必要事項** | Q-B1: 系統集合をどう確定するか。Q-B2: Decision Ledger の現在有効な決定集合を機械的に導出できない状態 (`superseded_by` が全203件 null、supersede 対象13件中11件が Active のまま、相反する2決定 `DC_20260724_001` / `_002` が併存) を先に解消するか、未解消のまま裁定するか。Q-B3: Ledger 4候補の判定保留状態のまま裁定可能か |

### 2.3 候補C-1 — `DC_20260712_008` の2層モデルをそのまま State 定義とする

| 項目 | 内容 |
|---|---|
| **前提** | (1) A-1 の自己参照 supersedes (`supersedes` の値が自分自身) の意味が確定していること |
| **依存Decision** | **A-1 のみ** (同決定の記述をそのまま採る) |
| **変更範囲** | (a) A-1 が言及していない5件 — Human Gate / Registry / `current_view` / `runtime/state.json` / Context Snapshot — の2層への割当規定 |
| **影響範囲** | (i) 憲法原則5 との緊張は `VOCABULARY_AUDIT_EVALUATION_v0.1.md:171` が記録するまま残る (ii) 分類B の B-1 とは異なる記述になる (iii) A-2 / A-3 の Human Gate = State Management Layer との関係整理が必要 |
| **裁定必要事項** | Q-C1: A-1 が言及していない5件をどう割り当てるか。Q-C2: A-1 の自己参照 supersedes の意味 |

### 2.4 候補C-2 — State 定義を行わない

| 項目 | 内容 |
|---|---|
| **前提** | なし |
| **依存Decision** | なし。`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md:54` の原則 (四観点のうち1つでも未調査であれば機械的に判定保留とし、本体監査でその観点を埋めるまで結論を出さない) と整合する |
| **変更範囲** | なし |
| **影響範囲** | (i) DP-2 (Snapshot) / DP-3 (Delta) が DP-1 に依存するため、両者も定義しない選択に連動しうる (ii) 分類B / 分類C の文書が PROPOSED / DRAFT のまま残る (iii) 1.5 の記述の並置が未解消のまま残る |
| **裁定必要事項** | Q-C3: 定義しない状態を保留として記録するか、定義対象外として確定するか |

---

## 3. JARVIS Operating Model — 4層境界図

### 3.1 境界図

各層への配置は**確定ではない**。根拠の有無と裁定要否を各欄に明示する。

```
  =================================================================
   JARVIS  (intelligence layer)
   根拠: phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md (逐語)
         "JARVIS is an intelligence layer."
         "Human Gate is an authority layer."

   Allowed  : Search context / Explain system state /
              Detect inconsistencies / Prepare proposals
   Forbidden: Execute decisions / Change authority state /
              Modify audit history / Automatic approval /
              Automatic rejection / Authority escalation /
              Ledger modification
  =================================================================
        |  read only (提案の生成まで)
        v
  +===============================================================+
  |  AUTHORITY LAYER                          [層名: 衝突なし]    |
  |  根拠: JARVIS_OPERATING_RULES_v0.1.md (逐語)                  |
  +---------------------------------------------------------------+
  |  Human Gate                          [配置根拠あり / 要裁定]  |
  |    STATES: PENDING / APPROVED / REJECTED / EXPIRED / CANCELED |
  |    approve() / reject() は人間操作のみ  (A-2 DC_20260705_008) |
  |    要裁定理由: A-2 は同じ Human Gate を                       |
  |                State Management Layer と定義 (HG-3)           |
  +---------------------------------------------------------------+
  |  authority_manager.py                          [分類未確定]   |
  |    出典: INSTITUTION_RUNTIME_v1.md (IMPLEMENTED v1)           |
  |    要裁定理由: Authority Layer との関係が未整理 (HG-7)         |
  +===============================================================+
        ^                                    |
        | approve / reject                   | 承認済みの状態遷移
        | (人間のみ / A-2, A-5, A-6)         v
  +===============================================================+
  |  STATE LAYER                    [層名: 既存2用法と衝突 HG-4]  |
  |  既存用法1: HAB STATE LAYER (C-2 / C-3、DRAFT)                |
  |  既存用法2: minimal_safe_architecture の STATE LAYER (B-1)    |
  +---------------------------------------------------------------+
  |  current_view                                    [要裁定]     |
  |    生成: overview_current_generator.generate()                |
  |          (一次データ4系統から再集計。書込は行わない)          |
  |    要裁定理由: 根拠文書 B-1 が PROPOSED                       |
  |    現況: 永続先 data/MOCKA_OVERVIEW_CURRENT.json は不在       |
  +---------------------------------------------------------------+
  |  runtime/state.json                              [要裁定]     |
  |    要裁定理由: 書込元が2系統存在し互換性がない                |
  |      runtime/action_selector.py                               |
  |        -> {actions, weights, last_actions, history}           |
  |      scripts/state/state_engine.py                            |
  |        -> {event_count, last_event}                           |
  |    現況: 実ファイルは前者。最終更新 2026-04-05 (約4か月停止)  |
  |          Event Store / Decision Ledger と参照関係なし         |
  +---------------------------------------------------------------+
  |  Context Snapshot                                [要裁定]     |
  |    出典: phi_os/context/context_snapshot.py (_MAX_HISTORY=20) |
  |    要裁定理由: 配置の根拠文書を確認できない                   |
  |    現況: data/context_snapshots/ は不在                       |
  +===============================================================+
        ^
        |  fold / projection
        |  [AJ-5: fold 実装は存在しない。replay() はグループ化]
        |
  +===============================================================+
  |  MEMORY LAYER            [層名: 既存の別概念と衝突 HG-3(B-3)] |
  |  既存用法: MEMORY_LAYER.md / memory/ モジュール群             |
  |            (4種記憶 episodic / semantic / procedural / skill) |
  |  根拠: A-1 DC_20260712_008 (Active)                           |
  +----------------------------+----------------------------------+
  |  Durable Layer / 正本      |  Observation Layer / 観測層      |
  |                            |                                  |
  |   Decision Ledger  [確定]  |   Event Store         [要裁定]   |
  |   Integrity Ledger [確定]  |   Runtime Trace       [確定]     |
  |   Anchor Record    [確定]  |   Experiment Log      [確定]     |
  |   Governance Decision[確定]|                                  |
  |                            |  単独では load-bearing 記録と    |
  |  用途: 制度判断 /          |  して扱わない (A-1 逐語)         |
  |        長期記憶 / 監査基準 |                                  |
  |                            |  Event Store 要裁定理由:         |
  |                            |   B-1 (PROPOSED) は同じ          |
  |                            |   event_store を STATE LAYER の  |
  |                            |   source of truth とする (HG-1)  |
  +----------------------------+----------------------------------+
  |         ^                                                      |
  |         |  昇格 (Observation -> Durable)                       |
  |         |  Condition 1 Identity / 2 Visibility /               |
  |         |  3 Integrity Reference / 4 Decision Relevance        |
  |         |  + 別途 Human Gate Decision を要する (A-1, HG-1)     |
  +===============================================================+

  +===============================================================+
  |  ACTION LAYER                        [証拠不足: 既存参照2件]  |
  +---------------------------------------------------------------+
  |  配置候補となるコンポーネントを本資料では特定できない (HG-5)  |
  |  既存参照:                                                    |
  |    MOCKA_FULL_ECOSYSTEM_UNDERSTANDING.md                      |
  |    docs/governance/phase3_execution_runtime_design_v1.md      |
  +===============================================================+
```

### 3.2 配置の確定状況

| コンポーネント | 対応候補となる層 | 状態 | 根拠 |
|---|---|---|---|
| Decision Ledger | Memory Layer (Durable) | **確定** | A-1 (Active) が明示 |
| Event Store | Memory Layer (Observation) | **要裁定** | A-1 は Observation。B-1 (PROPOSED) は STATE LAYER |
| Human Gate | Authority Layer | **要裁定** | JARVIS 規則は authority layer。A-2 は State Management Layer |
| current_view | State Layer (Projection) | **要裁定** | 根拠文書 B-1 が PROPOSED |
| runtime/state.json | (特定できない) | **要裁定** | 書込元競合が未解消 |
| Context Snapshot | (特定できない) | **要裁定** | 根拠文書なし |
| authority_manager.py | Authority Layer | **要裁定** | 分類未確定 (1.4) |

**確認できる事実:** 7件中、根拠が単一で確定的なのは Decision Ledger の1件のみである。

### 3.3 層名の衝突状況

| 層名 | MoCKA内の既存出現 | 衝突 |
|---|---|---|
| Memory Layer | 37件。`MEMORY_LAYER.md` / `memory/` の4種記憶 | **あり** — 既存の Memory Layer は Decision Layer の出力を記録・検索・コンテキスト生成する層であり、Event Store / Decision Ledger そのものではない |
| State Layer | 5件。HAB STATE LAYER (C-2 / C-3) と minimal_safe_architecture の STATE LAYER (B-1) | **あり** — 2つの異なる STATE LAYER が併存 |
| Authority Layer | 13件 | なし |
| Action Layer | **2件のみ** | **証拠不足** — 確定した指示対象を確認できない |

---

## 4. Human Gate 判断項目

以下は判断を要する項目の**列挙のみ**である。本資料は各項目に答えを与えていない。

### 4.1 State 定義の裁定

| ID | 判断項目 |
|---|---|
| **HG-0** | DP-1 の State 正本定義として、候補A / 候補B / 候補C-1 / 候補C-2 / 指定 のいずれを採るか |

### 4.2 既存 Decision との関係 (AJ-1 から AJ-5 の転記)

| ID | 判断項目 | 出典 |
|---|---|---|
| **HG-1** | 候補A を A-1 (`DC_20260712_008`, Active) と併存させられるか。併存できない場合、DP-1 の裁定は A-1 に対して何を行うか | AJ-1 |
| **HG-2** | A-1 の Durable 4対象と、候補B が想定する系統集合 (Event Store / Human Gate / Registry を含む) を同一の分割として扱うか、別軸として併存させるか | AJ-2 |
| **HG-3** | Human Gate の位置付け — Authority Layer (JARVIS 規則) と State Management Layer (A-2 / A-3、Active) の双方に現れる状態をどう扱うか | AJ-3 / B-2 |
| **HG-4** | Decision Ledger の現在有効な決定集合を機械的に導出できない状態を、DP-1 裁定の前に解消するか、未解消のまま裁定するか | AJ-4 |
| **HG-5** | 候補A を採る場合、fold の実装と `_STATE_COLUMNS` の運用開始を前提条件とするか、定義のみ先行させるか | AJ-5 |

### 4.3 層名と分類 (本資料で新たに提示)

| ID | 判断項目 |
|---|---|
| **HG-6** | 層名 Memory Layer を採用するか。既存の `MEMORY_LAYER.md` / `memory/` の Memory Layer (4種記憶) との関係をどう規定するか |
| **HG-7** | 層名 State Layer を採用するか。既存の HAB STATE LAYER (C-2 / C-3、DRAFT) および minimal_safe_architecture の STATE LAYER (B-1、PROPOSED) との関係をどう規定するか |
| **HG-8** | Action Layer を4層モデルに含めるか。含める場合、配置対象を何とするか (既存参照は2件のみ) |
| **HG-9** | 1.4 の3件 (`INSTITUTION_RUNTIME_v1.md` = IMPLEMENTED v1 / `JARVIS_OPERATING_RULES_v0.1.md` / `jarvis_authority_boundary.md`) を分類A / B / C のいずれに属させるか、または第4の分類を設けるか |
| **HG-10** | `INSTITUTION_RUNTIME_v1.md` の `authority_manager.py` (IMPLEMENTED v1) と JARVIS 規則の Authority Layer の関係をどう規定するか |

### 4.4 分類B / 分類C の処遇

| ID | 判断項目 |
|---|---|
| **HG-11** | 分類B の5件 (B-1 から B-5、いずれも 2026-06-22 から 06-23 作成、PROPOSED のまま、Decision Ledger 参照0件) を、DP-1 裁定に際してどう扱うか — 裁定対象に含める / 別工程とする / PROPOSED のまま据え置く |
| **HG-12** | 分類C の C-2 / C-3 が持つ "pre-authorization state を解除しない" という制約が、DP-1 裁定によって影響を受けるか |
| **HG-13** | C-1 (`HAB_CORE_DEFINITION_v0.1.md`、DRAFT未裁定) が定義する Canonical State と、DP-1 の State 定義の関係をどう規定するか |

### 4.5 未解決境界の昇格

| ID | 判断項目 |
|---|---|
| **HG-14** | `DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md` 第5.1章の B-1 から B-7、および第5.2章の未解決事項14件を、Adjudication Required Item へ昇格させるか |
| **HG-15** | Ledger 4候補の判定保留状態 (`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md:68-71`) のまま DP-1 を裁定するか |

### 4.6 隔離中の事項

| ID | 判断項目 |
|---|---|
| **HG-16** | "PHL(最小設問生成)" の隔離解除の可否。`DC_20260730_009` (Evidence Supremacy / 未検証文脈の隔離ルール、Active) により隔離中。一次証拠では PHL = Persistent History Layer (文脈保持・再注入) であり、"最小設問生成" はリポジトリ全文検索および Event Ledger 検索で0件。**解除は Human Authority のみが行える** |

---

## 5. 裁定記入欄

```
HG-0  State定義       選択: ______________________________________
                            ( 候補A / 候補B / 候補C-1 / 候補C-2 / 指定 )

HG-1  A-1との併存     判断: ______________________________________
HG-2  分割の同一性    判断: ______________________________________
HG-3  Human Gateの層  判断: ______________________________________
HG-4  Ledger導出      判断: ______________________________________
HG-5  fold前提条件    判断: ______________________________________
HG-6  Memory Layer名  判断: ______________________________________
HG-7  State Layer名   判断: ______________________________________
HG-8  Action Layer    判断: ______________________________________
HG-9  1.4の分類       判断: ______________________________________
HG-10 authority_mgr   判断: ______________________________________
HG-11 分類Bの処遇     判断: ______________________________________
HG-12 pre-authorization 判断: ____________________________________
HG-13 Canonical State 判断: ______________________________________
HG-14 境界の昇格      判断: ______________________________________
HG-15 判定保留        判断: ______________________________________
HG-16 PHL隔離解除     判断: ______________________________________

Decision Authority: ______________________________________
Decision Date:      ______________________________________
Decision Ledger:    未登録
```

---

## 6. 本資料の限界

1. 本資料は Claude Code Web 環境から作成された。リポジトリの clone は shallow (直近24時間) である。
2. `data/decisions/decision_ledger.jsonl` および `data/mocka_events.db` は本環境に不在であり、Decision Ledger (203件) と Event の観測は MCP 応答を経由した間接観測である。
3. Event の標本は `data/events_latest.json` の200件 (2026-08-05 から 06) であり、DB全体 19,360件に対する代表性はない。
4. `registry_store` (KN-004) の実体は本環境で確認できていない。
5. `INSTITUTION_RUNTIME_v1.md` に対応する Decision Ledger 記録の有無は確認していない。
6. 分類B / 分類C の全件について、Decision Ledger 参照の有無を確認したのは B-1 のみである (0件)。他は未確認。
7. 本ファイルは新規作成のみである。既存ファイルの変更は行っていない。commit は CLAUDE.md TODO_382 に従いブランチ `claude/mocka-diff-state-comparison-5w2xt1` に対して実施する。**main への直接 commit は行わない。Decision Ledger への登録は行っていない。**

---

## 7. 参照

### 7.1 分類A (Active Decision)

`DC_20260712_008` / `DC_20260705_008` / `DC_20260705_009` / `DC_20260731_003` / `DC_20260731_005` / `DC_20260713_003` / `DC_20260712_005` / `DC_20260724_008`

関連: `DC_20260724_001` / `DC_20260724_002` (相反する内容で両者 Active) / `DC_20260730_009` (Evidence Supremacy)

### 7.2 分類B (Proposed Architecture)

`docs/governance/minimal_safe_architecture_v1.md` / `execution_gate_v1.md` / `state_dependency_risk_map_v1.md` / `runtime_boundary_v1.md` / `import_safety_rule_v1.md`

### 7.3 分類C (Draft / 未裁定)

`docs/governance/HAB_CORE_DEFINITION_v0.1.md` / `mocka_full_static_structure_map_v1.md` / `mocka_phase10_human_gate_insertion_map_v1.md` / `DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md`

### 7.4 分類外

`INSTITUTION_RUNTIME_v1.md` / `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md` / `phi_os/hab/jarvis_authority_boundary.md`

### 7.5 監査文書

`docs/governance/VOCABULARY_AUDIT_EVALUATION_v0.1.md:171` / `VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md:54,68-71` / `VOCABULARY_CONSTITUTION_v0.1.md:33,36` / `FIRST_PRINCIPLES_AUDIT_v0.1.md:13` / `G5_DECISION_CRITERIA_DEFINITION_v0.6.md:204`

### 7.6 実装

`phi_os/event_replay.py:5,18-22,31,37,64-72` / `phi_os/integrity.py:121,234` / `phi_os/human_gate.py:23,26-32,64-65` / `phi_os/context/context_snapshot.py` / `phi_os/runtime/` / `scripts/state/overview_current_generator.py:26,116,138` / `scripts/state/state_engine.py:10,42` / `runtime/action_selector.py:14,118-119` / `scripts/ledger/decision_recorder.py:9,26` / `mocka_mcp_server.py:45-51,471,514-522,957`

### 7.7 憲法

`data/MOCKA_OVERVIEW.json:28-34` (憲法5原則。`CONSTITUTION.md` は Encoding Policy であり憲法5原則を含まない)
