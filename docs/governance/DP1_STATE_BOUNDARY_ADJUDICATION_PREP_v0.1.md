# DP-1 State Boundary Adjudication Prep v0.1

## MoCKA内 State 概念の位置付け整理 — JARVIS Institutional Runtime 基礎境界

**文書番号:** (未採番)
**作成日:** 2026-08-07
**工程:** DP-1 State Boundary Definition 裁定準備
**状態:** **裁定前資料。判断なし / 推奨なし / 優劣評価なし / 最適解なし / Human Authority判断待ち**
**CHANGE_START:** E20260807_8023474020011

**基礎資料:**
- STATE_DIFF_ENGINE_CORE_DECISION_PREP_v0.1 (会話上ドラフト、未ファイル化)
- STATE_BOUNDARY_AUDIT_v0.2 (会話上ドラフト、未ファイル化)

**上位方針 (きむら博士、HAB_CORE_DEFINITION_v0.1.md 0.1 より引用):**

> 既存システムの全面改修は禁止。まず制度境界を固定し、その後 JARVIS 能力を拡張する。

---

## 0. 禁止事項の遵守状況

| # | 禁止事項 | 遵守状況 |
|---|---|---|
| 1 | 推奨案作成 | 遵守 (本資料に推奨は一切含まれない) |
| 2 | 最適解決定 | 遵守 |
| 3 | 優劣評価 | 遵守 |
| 4 | 結論付与 | 遵守 (第2章は整理のみ) |
| 5 | 実装変更 | 遵守 (コード・スキーマ・データのいずれも変更していない) |
| 6 | 既存Decision supersede | 遵守 (supersede の提案も行っていない) |
| 7 | Decision Ledger 登録 | 遵守 (未登録) |
| 8 | 既存ファイルの変更 | 遵守 (本ファイル1件の新規作成のみ) |
| 9 | commit / push | 遵守 (未実施) |
| 10 | AJ項目への追加判断 | 遵守 (第6章は転記のみ) |

---

## 1. 目的

JARVIS計画における Institutional Runtime の基礎境界として、MoCKA内に存在する各 State 概念の位置付けを整理する。

本資料が行うこと:

1. State に言及する既存 Decision の内容整理 (結論付与なし)
2. DP-1 候補 A / B / C の既存 Decision との整合点・衝突点・必要変更範囲・前提条件の列挙
3. 既存コンポーネントの4層 (Memory / State / Authority / Action) への対応候補の提示
4. Adjudication Required Item (AJ-1〜AJ-5) の管理

本資料が行わないこと: 上記いずれについても選択・推奨・結論を与えない。

---

## 2. 既存Decision証拠

### 2.1 DC_20260712_008 — DU#008: Event Store Trust Boundary Decision (Option C採択確定)

| 項目 | 値 |
|---|---|
| status | **Active** |
| approved_by | **きむら博士 (Human Gate)** |
| supersedes | **DC_20260712_008 (自己参照)** |
| superseded_by | null |

#### 定義している State 概念 (逐語)

> **MoCKA Memory Model(2層):**
> **[Durable Layer / 正本]** 対象=Decision Ledger, Integrity Ledger, Anchor Record, Governance Decision。用途=制度判断/長期記憶/監査基準。
> **[Observation Layer / 観測層]** 対象=Event, Runtime Trace, Experiment Log。用途=実験証跡/状態観測/再現補助。**単独ではload-bearing記録として扱わない。**

#### Durable Layer との関係

対象4件を正本として指定する。Decision Ledger は本層に属する。

#### Observation Layer との関係

Event を本層に置く。用途は実験証跡・状態観測・再現補助であり、単独では load-bearing 記録として扱わないと明記されている。

Observation から Durable への昇格条件が4件確定している (逐語):

> Condition 1 Identity: event_id固定 / actor識別可能(who_actor) / timestamp保持。session_idは識別用途に使用禁止
> Condition 2 Visibility: 複数read経路で確認 / id指定取得可能 / 内容一致確認
> Condition 3 Integrity Reference: Integrity Ledger参照あり / 境界条件記録済み
> Condition 4 Decision Relevance: 判断に使用された / 再利用対象である / 後続判断へ影響する

#### Human Gate との関係 (逐語)

> Event昇格(Observation->Durable)は本Decisionの範囲外であり、上記4条件充足を実測した上で**別途Human Gate Decisionを要する**。

*(転記注記: 原文の矢印記号を、CLAUDE.md CP932汚染防止規約に従い ASCII の `->` へ置換している。他の文字は原文どおり。)*

同決定は `status:ok` の定義も確定している (逐語):

> status:ok=write処理受付成功のみ。保証対象外=永続取得/第三者検証/Durable採用。制度記憶採用条件=write成功 + Durable Ledger記録 + id取得確認(3点セット)。

---

### 2.2 DC_20260705_008 / DC_20260705_009 — Human Gate = State Management Layer

| 項目 | DC_20260705_008 | DC_20260705_009 |
|---|---|---|
| status | **Active** | **Active** |
| approved_by | きむら博士 | きむら博士 |
| supersedes | null | **DC_20260705_008** |
| superseded_by | null | null |

#### 定義している State 概念 (DC_20260705_008 逐語)

> Human Gate を Decision Engine(判断主体)ではなく **State Management Layer(非決定系の状態保留装置)** として定義する。責務を以下のように分離固定する。
> (1) 自動検知系(audit_trigger.py/health_check.py/tech_watcher.py等prevention_queueへの投入元)は、**PENDING状態への投入のみ**を担当し、可否判断には一切関与しない。
> (2) Human Gate(phi_os/human_gate.py)は、**PENDING状態の保持・一覧表示・状態遷移の受付窓口としてのみ**機能する。それ自体が判断や自動応答を行うことは禁止する。
> (3) approve()/reject()の呼び出しは、**実際に人間がUI/APIを操作した場合にのみ**許可する。自動ロジック・推論結果による呼び出し経路は一切設けない。

#### DC_20260705_009 の内容 (逐語)

> DC_20260705_008の実質的な結論(...)は**変更せず維持する**。参照先のみ TODO_387 から PHI-OS-HUMAN-GATE-STATE-MODEL-V1 に訂正する。

#### Durable Layer / Observation Layer との関係

**両決定とも Durable Layer / Observation Layer に言及していない。** DC_20260712_008 (2026-07-12) より前 (2026-07-05) の記録である。

#### Human Gate との関係

Human Gate 自身を対象とする決定である。実装上の対応は `phi_os/human_gate.py`:

- `:23` `STATES = {"PENDING","APPROVED","REJECTED","EXPIRED","CANCELED"}`
- `:26-32` `TRANSITIONS` テーブル (submit / approve / reject / expire / cancel)
- `:64-65` DB列 `previous_state` / `next_state`

---

### 2.3 その他 State 関連 Decision

いずれも status = Active。

| decision_id | title (抜粋) | 定義している State 概念 | Human Gate との関係 |
|---|---|---|---|
| `DC_20260731_003` | INCパイプライン是正 RC-B採択 — INC Lifecycle State Model の導入 | INC Lifecycle State Model v0.1 | 承認相当の状態への遷移を実行できる主体は人間に限定。機械が承認を出せる設計としない |
| `DC_20260731_005` | RC-B承認軸は既存Human Gate基盤を再利用する | **2軸モデル** — INC進行軸(DETECTED/ANALYZED/PUBLISHED/CLOSED、機械が進める) / 承認軸(PENDING/APPROVED/REJECTED、人間のみ) | 承認軸は `phi_os/human_gate.py` および `data/mocka_events.db` の `human_gate_events` を**再利用**。INC専用状態機械は導入しない |
| `DC_20260713_003` | AUTO_SEAL Boundary Design v1.0 Model B採用 | Seal 授権の状態境界 | `approved_by=human` を AUTO_SEAL 成立条件として必須化 (`approved_by != human` は Seal不可)。GL7 は承認者ではなく事前境界フィルタ |
| `DC_20260712_005` | Decision Unit #002 — Pre-First-Blood Working Tree State Declaration | Working Tree State (Baseline固定) | Option A採択 |
| `DC_20260724_008` | MCP Recovery State Baseline Fixed for Root Cause Investigation | Recovery State (Baseline固定) | — |

#### Decision Ledger 全件検索結果 (203件対象)

| 検索語 | 件数 |
|---|---|
| `single source of truth` | **1** (DC_20260724_001。Decision Ledger 自身を正本と宣言する文脈) |
| `authoritative` | **0** |
| `event history` / `Event history` | **0** |
| `Current View` | **0** |
| `current_view` | 1 (DC_20260715_004) |
| `Snapshot` / `snapshot` | 9 (いずれも SSOT監査・正本確定の文脈。Snapshot を制度語として定義した決定は確認できない) |
| `正本` | 78 |
| `canonical` | 63 |

**確認できる事実:** 憲法原則5の文言 "Event history is the single source of truth" は Decision Ledger 203件中に一度も出現しない。

---

### 2.4 Decision 以外の一次証拠 (未裁定文書)

| 文書 | Status | 日付 | State に関する記述 | Ledger 参照 |
|---|---|---|---|---|
| `docs/governance/minimal_safe_architecture_v1.md` | **PROPOSED (設計提案)** | 2026-06-23 | `:31-38` `[STATE LAYER] event_store(source of truth) / working_memory(cache) / todo.json(projection)`。`:44` "真実の位置は `event_store` のみとする" | **0件** |
| `docs/governance/HAB_CORE_DEFINITION_v0.1.md` | **DRAFT(未裁定)** | 2026-08-04 | 副題: Human Authority Boundary — 最小定義(**Canonical State** / Actor / Transition Ledger / JARVIS 権限境界)。同文書は Decision Ledger 登録なし・実装なしを明記 | なし |
| `docs/governance/execution_gate_v1.md` | — | — | `:16` "State Layer健全性" / `:119` "State Layer  FIXED" | — |
| `docs/governance/mocka_full_static_structure_map_v1.md` | — | — | `:51` `[HAB STATE LAYER]` を最上位に配置 | — |
| `docs/governance/mocka_phase10_human_gate_insertion_map_v1.md` | — | — | `:27` `[HAB State Layer]` | — |

---

### 2.5 時系列 (記述の並置のみ)

以下は各文書の記述を時系列に並べたものであり、整合判定・優劣評価・結論付与は行っていない。

| 日付 | 出典 | Status | event_store / Event の位格に関する記述 |
|---|---|---|---|
| 2026-06-23 | `minimal_safe_architecture_v1.md` | PROPOSED | `event_store` を STATE LAYER の **source of truth** とする |
| 2026-07-05 | `DC_20260705_008` / `_009` | **Active** | Human Gate を State Management Layer と定義 (Event の位格には言及なし) |
| 2026-07-12 | `DC_20260712_008` | **Active** | Event を **Observation Layer** に置き、**単独では load-bearing 記録として扱わない** |
| 2026-07-31 | `DC_20260731_005` | **Active** | 承認軸は `human_gate_events` を再利用。2軸モデル |
| 2026-08-04 | `HAB_CORE_DEFINITION_v0.1.md` | DRAFT(未裁定) | Canonical State を新たに定義し、既存状態との mapping を作る |

---

## 3. State関連構造

### 3.1 State を保持する実体の一覧

| # | 実体 | 所在 | 書込経路 | 本環境での可用性 |
|---|---|---|---|---|
| 1 | Event Store | `data/mocka_events.db` | `phi_os/event_gate.process_event()` (単一経路、TODO_322) | **不在** (MCP経由の間接観測のみ) |
| 2 | Decision Ledger | `data/decisions/decision_ledger.jsonl` | `mocka_decision_write` | **不在** (MCP経由の間接観測のみ) |
| 3 | Human Gate events | `data/mocka_events.db` の `human_gate_events` テーブル | `phi_os/human_gate.py` `_record_transition()` | **不在** |
| 4 | Registry (KN-004) | `PlanningCaliber/workshop/registry_kn004` | `mocka_registry_add` | **リポジトリ外・不在** |
| 5 | `current_view` | 永続先 `data/MOCKA_OVERVIEW_CURRENT.json` | `overview_current_generator.write_output()` | **ファイル不在**。MCP応答内にのみ存在 |
| 6 | `runtime/state.json` | `runtime/state.json` | **複数 (3.2参照)** | **存在 (6,187 bytes)** |
| 7 | Context Snapshot | `data/context_snapshots/` | `phi_os/context/context_snapshot.py` | **ディレクトリ不在** |

### 3.2 `runtime/state.json` の書込元競合

| コード | 参照行 | 動作 | スキーマ |
|---|---|---|---|
| `runtime/action_selector.py` | `:14`, `:118-119` | **書込** | `{actions, weights, last_actions, history}` |
| `scripts/state/state_engine.py` | `:10`, `:42` | **書込** | `{event_count, last_event}` |
| `scripts/ledger/decision_recorder.py` | `:9`, `:26` | 読取のみ | `last_actions` を期待 |
| `scripts/state/multi_state_sync.py` | `:8` | 複製元 | — |

実ファイルの内容: `{actions, weights, last_actions, history}`、history 32件、最古 2026-03-24T08:37、**最新 2026-04-05T03:22**。

**確認できる事実:**
1. 実ファイルは `action_selector.py` のスキーマである。
2. 同一パスに相互に互換性のない2つの書込元が存在する。
3. 最終更新から約4か月間、内容が更新されていない。
4. 内容は行動選択 (action / weight / history) であり、Event Store・Decision Ledger のいずれとも参照関係を持たない。

### 3.3 `event_replay.replay()` の実装実態

`phi_os/event_replay.py:64-72` 逐語:

```
state = {}
for row in rows:
    r = dict(row)
    key = r.get("what_type") or "_untyped"
    state.setdefault(key, []).append(
        {col: r.get(col) for col in _STATE_COLUMNS}
    )
return state
```

**確認できる事実:** `replay()` は `what_type` によるグループ化であり、イベント列を単一の状態値へ縮約する畳み込み (fold) ではない。

`_STATE_COLUMNS` (`:18-22`) の利用実態 (標本: `data/events_latest.json` 200件、2026-08-05〜06):

| 列 | null | 値あり | 値の実態 |
|---|---|---|---|
| `before_state` | **194 (97.0%)** | 6 | 全件 `AUTO_SEAL_PENDING` の固定文字列 "accumulating" |
| `after_state` | 13 | 187 | `short_summary` の複製と一致する自由文 |
| `change_type` | **200 (100%)** | **0** | — |
| `impact_scope` | **200 (100%)** | **0** | — |
| `impact_result` | **200 (100%)** | **0** | — |

標本は `claude_mcp` が181件 (90.5%) を占め、DB全体 19,360件 (25型) に対する代表性はない。

### 3.4 DP-1 候補整理

#### 候補 A: State = Event history fold

| 観点 | 内容 |
|---|---|
| **既存Decisionとの整合点** | 憲法原則5 (`data/MOCKA_OVERVIEW.json:33`) の文言と一致する。`phi_os/event_replay.py:5` の "唯一の真実層は phi_os.event_gate.process_event() / data/mocka_events.db のまま" という自己宣言と一致する。`minimal_safe_architecture_v1.md:31-44` (PROPOSED) の記述と一致する |
| **衝突点** | `DC_20260712_008` (Active、Human Gate承認) が Event を Observation Layer に置き、**単独では load-bearing 記録として扱わない**と明記している。同決定は Decision Ledger 等4件を Durable Layer / 正本 としている |
| **必要変更範囲** | (a) `DC_20260712_008` との関係整理 (b) fold 実装 — 3.3 により既存資産として存在しない (c) `_STATE_COLUMNS` の運用開始 — `change_type`/`impact_scope`/`impact_result` は標本内で使用実績ゼロ (d) Decision Ledger / Human Gate events / Registry を fold 対象に含めるか否かの規定 |
| **前提条件** | Event が Durable 相当として扱えること。`DC_20260712_008` は昇格に4条件の実測と別途Human Gate Decision を要すると定めている |

#### 候補 B: State = 複数系統State集合

| 観点 | 内容 |
|---|---|
| **既存Decisionとの整合点** | `DC_20260712_008` の2層モデル (Durable / Observation) が複数系統の並立を前提としている。`DC_20260705_008`/`_009` が Human Gate を State Management Layer と定義済み。`DC_20260731_005` が2軸モデル (INC進行軸 / 承認軸) を採用済み |
| **衝突点** | 憲法原則5 "Event history is the single source of truth" との関係について、`docs/governance/VOCABULARY_AUDIT_EVALUATION_v0.1.md:171` が既に "文書上明示的に解消されていない緊張がある" と記録している。同記録は Ledger 4候補 (`ledger.json` / `mocka_events.db`+`audit_trigger.py` / `decision_ledger.jsonl` / `KN_SERIES_LEDGER`) が `VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md` で**4候補とも判定保留**とされている状態を指す |
| **必要変更範囲** | (a) 系統の列挙の確定 — `DC_20260712_008` の Durable 4対象と、Event Store / Human Gate / Registry を含む集合は一致しない (b) 系統間の整合検証機構 (c) 各系統の "現在状態" 導出規定 |
| **前提条件** | Decision Ledger について、現在有効な決定集合を機械的に導出できること。**現状は導出できない** — `superseded_by` が全203件 null、supersede 対象13件中11件が Active のまま、相反する2決定 (`DC_20260724_001` / `_002`) が併存 |

#### 候補 C: 別案

既存文書に現れている第三の記述形として、以下2案を整理する。いずれも本資料が新たに提案するものではない。

**C-1: `DC_20260712_008` の2層モデルをそのまま State 定義とする**

| 観点 | 内容 |
|---|---|
| **既存Decisionとの整合点** | `DC_20260712_008` (Active) の記述をそのまま採るため、同決定との衝突が発生しない |
| **衝突点** | 憲法原則5 との関係は `VOCABULARY_AUDIT_EVALUATION_v0.1.md:171` が記録する未解消の緊張のまま残る。`minimal_safe_architecture_v1.md` (PROPOSED) の `event_store = source of truth` とは異なる記述になる |
| **必要変更範囲** | (a) Human Gate / Registry / `current_view` / `runtime/state.json` / Context Snapshot の2層への割当規定 — `DC_20260712_008` はこれら5件に言及していない |
| **前提条件** | `DC_20260712_008` の自己参照 supersedes (supersedes 値が自分自身) の意味の確定 |

**C-2: State 定義を行わない**

| 観点 | 内容 |
|---|---|
| **既存Decisionとの整合点** | `VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md:54` — "四観点のうち1つでも未調査であれば機械的に判定保留とし、本体監査でその観点を埋めるまで結論を出さない" |
| **衝突点** | 確認できない |
| **必要変更範囲** | なし |
| **前提条件** | DP-2 (Snapshot) / DP-3 (Delta) が DP-1 に依存するため、両者も定義しない選択に連動しうる |

---

## 4. JARVIS Architectureとの関係

### 4.1 JARVIS の既存境界定義 (一次証拠・逐語)

`phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md`:

> **Principle**
> **JARVIS is an intelligence layer.**
> **Human Gate is an authority layer.**

同文書 Allowed / Restricted:

| Allowed | Restricted |
|---|---|
| Search context / Explain system state / Detect inconsistencies / Prepare proposals | Execute decisions / Change authority state / Modify audit history |

`phi_os/hab/jarvis_authority_boundary.md`:

> **Principle**
> JARVIS assists human decisions.
> JARVIS does not own human authority.

| Allowed | Forbidden |
|---|---|
| Evidence collection / Context analysis / State explanation / Risk detection / Decision proposal | Human decision replacement / Automatic approval / Automatic rejection / Authority escalation / **Ledger modification** |

**確認できる事実:** Authority Layer = Human Gate は既に明文化されている。JARVIS は intelligence layer として Authority Layer の外側に置かれている。

### 4.2 4層名称の既存参照先 (衝突確認)

| 層名 | MoCKA内の既存出現 | 既存の指示対象 | 衝突の有無 |
|---|---|---|---|
| **Memory Layer** | 37件。`MEMORY_LAYER.md`、`memory/` モジュール群 | **Decision Layer が生成する DecisionResult を持続させる層**。4種記憶 (episodic / semantic / procedural / skill)。`memory_registry` / `memory_store` / `memory_index` / `memory_writer` / `memory_retriever` / `memory_context_builder` | **衝突あり** — 既存の Memory Layer は Event Store / Decision Ledger そのものではない |
| **State Layer** | 5件。`mocka_full_static_structure_map_v1.md:51` `[HAB STATE LAYER]`、`mocka_phase10_human_gate_insertion_map_v1.md:27`、`minimal_safe_architecture_v1.md:31`、`execution_gate_v1.md:16,119` | HAB STATE LAYER (Human Gate Core の上位) / minimal_safe_architecture の STATE LAYER (event_store + working_memory + todo.json) | **衝突あり** — 2つの異なる STATE LAYER が存在 |
| **Authority Layer** | 13件。`JARVIS_OPERATING_RULES_v0.1.md` ほか | **Human Gate** | 衝突なし |
| **Action Layer** | **2件のみ**。`MOCKA_FULL_ECOSYSTEM_UNDERSTANDING.md` / `docs/governance/phase3_execution_runtime_design_v1.md` | 確定した指示対象を確認できない | **証拠不足** |

### 4.3 コンポーネント配置 (対応候補。確定ではない)

以下は各コンポーネントについて、根拠となる一次証拠が存在する層を対応候補として示したものである。**割当の確定・選択・推奨は行っていない。**

| コンポーネント | 対応候補となる層 | 根拠 (一次証拠) | 状態 |
|---|---|---|---|
| **Decision Ledger** | Memory Layer (Durable 側) | `DC_20260712_008` (Active): Durable Layer / 正本 の対象4件に含まれる | **根拠あり** |
| **Event Store** | Memory Layer (Observation 側) | `DC_20260712_008` (Active): Observation Layer の対象に含まれる | **要裁定** — `minimal_safe_architecture_v1.md:31` (PROPOSED) は同じ `event_store` を STATE LAYER の source of truth に置く。2文書で層が異なる |
| **Human Gate** | Authority Layer | `JARVIS_OPERATING_RULES_v0.1.md` (逐語): "Human Gate is an authority layer" | **要裁定** — `DC_20260705_008`/`_009` (Active) は同じ Human Gate を **State Management Layer** と定義しており、2層にまたがる |
| **Context Snapshot** | (対応候補を確定できない) | 根拠文書を確認できない。`phi_os/context/context_snapshot.py` docstring は "Context全体を定期的にJSONとして保存する" とのみ記す | **要裁定** |
| **runtime/state.json** | (対応候補を確定できない) | 内容は行動選択 (actions / weights / last_actions / history)。Event Store・Decision Ledger と参照関係なし。最終更新 2026-04-05 | **要裁定** — 3.2 の書込元競合が未解消 |
| **current_view** | State Layer (Projection 側) | `overview_current_generator.py:116` docstring: "一次データを再集計して結果dictを返す(ファイルへの書込は行わない)"。`minimal_safe_architecture_v1.md:31-38` が `todo.json(projection)` を STATE LAYER に置く記述と同型 | **要裁定** — 根拠文書が PROPOSED であり裁定されていない |

**確認できる事実:** 6コンポーネント中、根拠が単一で確定的なのは Decision Ledger の1件のみ。他5件は要裁定である。

### 4.4 Institution Runtime との関係 (参考)

`INSTITUTION_RUNTIME_v1.md` (文書番号 PHI-OS-RUNTIME-001、2026-06-16、状態 **IMPLEMENTED v1**) が定義する `phi_os/runtime/` の構成:

| モジュール | 役割 (同文書より) |
|---|---|
| `institution_runtime.py` | Runtime統合入口 (シングルトン対応) |
| `meaning_registry.py` | Meaning辞書 |
| **`authority_manager.py`** | **Authority管理** |
| `institution_registry.py` | Institution管理 |
| `gate_registry.py` | Gate管理 |
| `binding_engine.py` | Binding Layer実行エンジン |
| `compliance_engine.py` | 制度監査エンジン |

**確認できる事実:** Authority を管理するモジュールが Institution Runtime 内に既に実装されている (`authority_manager.py`)。本資料は同モジュールと 4.1 の Authority Layer との関係を判定していない。

---

## 5. 未解決境界

### 5.1 本資料で新たに確認された境界

| ID | 境界 | 一次証拠 |
|---|---|---|
| **B-1** | `minimal_safe_architecture_v1.md` (PROPOSED、2026-06-23) と `DC_20260712_008` (Active、2026-07-12) が `event_store` / Event の位格について異なる記述を持つ | 2.4 / 2.5 |
| **B-2** | Human Gate が Authority Layer (`JARVIS_OPERATING_RULES_v0.1.md`) と State Management Layer (`DC_20260705_008`/`_009`) の双方に位置付けられている | 4.3 |
| **B-3** | 層名 "Memory Layer" が既存の別概念 (`MEMORY_LAYER.md`、`memory/` の4種記憶) と衝突する | 4.2 |
| **B-4** | 層名 "State Layer" が2つの異なる既存 STATE LAYER (HAB STATE LAYER / minimal_safe_architecture の STATE LAYER) と衝突する | 4.2 |
| **B-5** | 層名 "Action Layer" の既存参照が2件のみで、確定した指示対象を確認できない | 4.2 |
| **B-6** | `HAB_CORE_DEFINITION_v0.1.md` が DRAFT (未裁定・Ledger登録なし・実装なし) のまま Canonical State を定義している | 2.4 |
| **B-7** | `INSTITUTION_RUNTIME_v1.md` の `authority_manager.py` (IMPLEMENTED v1) と `JARVIS_OPERATING_RULES_v0.1.md` の Authority Layer の関係が未整理 | 4.4 |

### 5.2 STATE_BOUNDARY_AUDIT_v0.2 から継続する未解決事項

| # | 事項 |
|---|---|
| 1 | `superseded_by` が Decision Ledger 全203件で null である理由 |
| 2 | `DC_20260712_008` の自己参照 supersedes の意図 |
| 3 | `DC_20260724_001` / `_002` の相反する内容が両者 Active である状態の扱い |
| 4 | Decision Ledger の "現在有効な決定集合" の機械的導出規定の不在 |
| 5 | Decision Ledger 実体の生の行構造 (203 unique ID に対し `current_view` は 210行を計上。差7行の内容が未確認) |
| 6 | 過去イベントにおける `before_state` / `change_type` 等の利用実態 |
| 7 | `handshake` / `HANDSHAKE` (大小異なる同語) が同一概念か否か |
| 8 | `event_signatures` テーブルの内容 |
| 9 | `runtime/state.json` の2書込元のうち稼働中のもの |
| 10 | `runtime/shadow_1|2|3/` の稼働状況 |
| 11 | `MOCKA_OVERVIEW_CURRENT.json` の生成実績 |
| 12 | Ledger 4候補の判定保留状態 (`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md:68-71`) |
| 13 | `registry_store` (KN-004) の実体 — リポジトリ外パス `PlanningCaliber/workshop/registry_kn004` |
| 14 | "PHL(最小設問生成)" の隔離状態 — `DC_20260730_009` (Evidence Supremacy) 適用中。解除は Human Authority のみ |

---

## 6. Human Gate判断項目

### 6.1 Adjudication Required Item (AJ-1〜AJ-5)

以下は STATE_BOUNDARY_AUDIT_v0.2 で確認された項目の**転記**である。Decision 候補ではなく、裁定を要する項目として管理する。**本資料は各項目に追加判断を与えていない。**

---

**AJ-1: `DC_20260712_008` の Memory Model と DP-1 候補の関係**

`DC_20260712_008` (Active、きむら博士 Human Gate 承認) は Event を Observation Layer (単独では load-bearing 記録として扱わない)、Decision Ledger 等4対象を Durable Layer / 正本 と分類している。

裁定を要する事項: DP-1 の候補 A (State = Event history fold) を、この既存 Active 決定と併存させられるか。

```
判断: _________________________________________________
```

---

**AJ-2: `DC_20260712_008` の2層分割と DP-1 候補 B の系統集合の関係**

| | Durable Layer (DC_20260712_008) | 候補 B が想定する系統 |
|---|---|---|
| 共通 | Decision Ledger | Decision Ledger |
| DC のみ | Integrity Ledger / Anchor Record / Governance Decision | — |
| 候補Bのみ | — | Event Store / Human Gate / Registry |
| 分類の相違 | Event は Observation Layer | Event Store は並列 State の1つ |

裁定を要する事項: 両者を同一の分割として扱うか、別軸として併存させるか。

```
判断: _________________________________________________
```

---

**AJ-3: `DC_20260705_008` / `_009` (Human Gate = State Management Layer) との関係**

Human Gate は既に State Management Layer として定義済み (Active)。ただし State Management Layer は State そのものとは異なる語である。加えて `JARVIS_OPERATING_RULES_v0.1.md` は Human Gate を authority layer と規定している (B-2)。

裁定を要する事項: DP-1 における Human Gate の位置付けが、既存定義 (管理層 / authority layer) と一致するか、State 本体としての新たな位置付けを与えるか。

```
判断: _________________________________________________
```

---

**AJ-4: Decision Ledger の現在状態の導出可能性**

`superseded_by` が全203件 null、supersede 対象13件中11件が Active のまま残存、相反する2決定 (`DC_20260724_001` / `_002`) が併存する。Decision Ledger から現在有効な決定集合を機械的に導出する経路は現状存在しない。

裁定を要する事項: DP-1 で Decision Ledger を State または State の構成要素として扱う場合、この導出不能状態を先に解消するか、未解消のまま裁定するか。

```
判断: _________________________________________________
```

---

**AJ-5: fold 実装の不在**

3.3 により、Event から状態への畳み込み実装は既存資産として存在しない (`replay()` はグループ化)。畳み込みの入力となる `before_state` / `change_type` / `impact_scope` / `impact_result` は標本内で実質未使用である。

裁定を要する事項: DP-1 候補 A を採る場合、fold の実装と `_STATE_COLUMNS` の運用開始を前提条件とするか、定義のみ先行させるか。

```
判断: _________________________________________________
```

---

### 6.2 B-1〜B-7 の扱い

第5.1章の B-1〜B-7 を AJ 項目へ昇格させるか否かは、本資料では判断しない。

```
判断: _________________________________________________
```

### 6.3 DP-1 裁定記入欄

```
選択:               _____________________________________
                    ( A / B / C-1 / C-2 / 指定 )

Decision Authority: _____________________________________

Decision Date:      _____________________________________

Reason:             _____________________________________
                    _____________________________________

Ledger:             未登録
```

---

## 7. 本資料の限界

1. 本資料は Claude Code Web 環境から作成された。リポジトリの clone は shallow (50コミット / 直近24時間) である。
2. `data/decisions/decision_ledger.jsonl` および `data/mocka_events.db` は本環境に不在であり、Decision Ledger (203件) と Event の観測は MCP 応答を経由した間接観測である。
3. `data/tic/mcp_schema_hash.json` が本環境に存在しないため、MCP schema drift のセッション基準ハッシュを取得できていない (CLAUDE.md IC_20260705_018 の手順が実行不能)。
4. Event の標本は `data/events_latest.json` の200件 (2026-08-05〜06) であり、DB全体 19,360件に対する代表性はない。
5. `registry_store` (KN-004) の実体は本環境で確認できていない。
6. 本資料の作成日 (2026-08-07) は CHANGE_START イベント `E20260807_8023474020011` の記録時刻 (JST基準) に基づく。同イベントの `when_ts` は UTC 表記 (`2026-08-06T22:41:27+00:00`) であり、実行環境のシステム日付 (2026-08-06) との差はタイムゾーン差である。
7. 本ファイルは新規作成のみである。既存ファイルの変更は行っていない。commit は CLAUDE.md TODO_382 (CHANGE_DONE記録後は該当変更を必ず正しいリポジトリへcommitする) に従い、ブランチ `claude/mocka-diff-state-comparison-5w2xt1` に対して実施する。**main への直接 commit は行わない。Decision Ledger への登録は行っていない。**

---

## 8. 参照文書

### 8.1 Decision (すべて Active)

- `DC_20260712_008` — DU#008: Event Store Trust Boundary Decision (Option C採択確定)
- `DC_20260705_008` — TODO_387解決: Human Gate を State Management Layer として定義する
- `DC_20260705_009` — DC_20260705_008 訂正: 参照先ID修正
- `DC_20260731_003` — INC Lifecycle State Model の導入
- `DC_20260731_005` — RC-B承認軸は既存 Human Gate 基盤を再利用する
- `DC_20260713_003` — AUTO_SEAL Boundary Design v1.0 Model B採用
- `DC_20260712_005` — Pre-First-Blood Working Tree State Declaration
- `DC_20260724_008` — MCP Recovery State Baseline Fixed
- `DC_20260724_001` / `DC_20260724_002` — DC-WP-001 Notion記録の位置付け
- `DC_20260730_009` — 未検証文脈 (Unverified Context) の隔離ルール確立

### 8.2 制度文書

- `data/MOCKA_OVERVIEW.json:28-34` — 憲法5原則 (`CONSTITUTION.md` は Encoding Policy であり憲法5原則を含まない)
- `docs/governance/FIRST_PRINCIPLES_AUDIT_v0.1.md:13` — 憲法5原則の所在の明記
- `docs/governance/G5_DECISION_CRITERIA_DEFINITION_v0.6.md:204` — 憲法原則1の基準化 (I-1)
- `docs/governance/VOCABULARY_AUDIT_EVALUATION_v0.1.md:171` — 憲法原則5と Ledger 4候補の未解消の緊張
- `docs/governance/VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md:54,68-71` — 判定保留ルールと Ledger 4候補
- `docs/governance/VOCABULARY_CONSTITUTION_v0.1.md:33,36` — 正本未確定の記録
- `docs/governance/HAB_CORE_DEFINITION_v0.1.md` — HAB 最小定義 (DRAFT未裁定)
- `docs/governance/minimal_safe_architecture_v1.md` — Minimal Safe Architecture v1 (PROPOSED)
- `docs/governance/execution_gate_v1.md:16,119` — State Layer健全性 / State Layer FIXED
- `docs/governance/mocka_full_static_structure_map_v1.md:51` — HAB STATE LAYER
- `INSTITUTION_RUNTIME_v1.md` — PHI-OS Institution Runtime (IMPLEMENTED v1)
- `MEMORY_LAYER.md` — Memory Layer (Phase 2-3) の既存定義

### 8.3 実装 (一次証拠)

- `phi_os/event_replay.py:5,18-22,31,37,64-72,78-93`
- `phi_os/integrity.py:121,154,161,168,175,185,192,207,222,227,234`
- `phi_os/human_gate.py:23,26-32,64-65`
- `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md`
- `phi_os/hab/jarvis_authority_boundary.md`
- `phi_os/context/context_snapshot.py`
- `phi_os/runtime/` (institution_runtime / authority_manager / gate_registry ほか)
- `scripts/state/overview_current_generator.py:26,116,138`
- `scripts/state/state_engine.py:10,42`
- `runtime/action_selector.py:14,118-119`
- `scripts/ledger/decision_recorder.py:9,26`
- `mocka_mcp_server.py:45-51,471,514-522,957`
