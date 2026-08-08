# JARVIS Runtime beta - Architecture Definition Draft v0.1

## GPT Orchestration / Conversation Context / Tool Orchestration / Human Authority Boundary Runtime と MoCKA 接続境界の定義

**文書番号:** (未採番)
**作成日:** 2026-08-07
**Status:** **DRAFT (未裁定)**
**Decision Ledger 登録:** **なし**
**Seal:** **未生成**
**実装:** **なし** (コード・スキーマ・データのいずれも変更していない)
**起草:** くろこ (Claude-opus-5)
**Decision Authority:** Human Authority (きむら博士) - 本文書は裁定を受けていない

**Freeze Point (前提条件):**
`DC_20260807_001` DP-1 State Boundary Decision (status: Active、approved_at 2026-08-07T02:52:36Z)
Freeze Point commit: `d7129bf303060470c43d1fc78eed3206eeba77a3`

**CHANGE_START:** E20260807_4445695662543

---

## 0. 本文書の位置付け

### 0.1 何であり、何でないか

| | |
|---|---|
| **本文書である** | JARVIS Runtime beta を制度上どう構成するかの **Architecture Definition の起草案**。Human Gate への提示材料 |
| **本文書でない** | 承認された設計 / Decision / 要件定義 / 実装指示 / Migration 計画 / 既存 Decision の変更・supersede / DP-1 の再設計 |

本文書は **Architecture Definition** であり、実装を前提とした設計文書ではない。
本文書の存在によって、コード・スキーマ・データ・プロセス構成のいかなる変更も許可されない。

### 0.2 表記規約

本規約は `JARVIS_CONSTITUTION_DRAFT.md` 0.2 および `HAB_CORE_DEFINITION_v0.1.md` 0.3 の様式を踏襲する。

| ラベル | 意味 |
|---|---|
| **[継承]** | 既存の Active な Decision / RATIFIED 文書 / 実測済み事実から引き写した記述。本文書は内容を変更していない。出典を必ず併記する |
| **[起案]** | 本文書が新たに提案する記述。**未裁定。Human Gate の判断対象** |
| **[未裁定]** | 一次資料間に不一致があるか、既存の裁定が Pending であるため、本文書では確定させない事項 |
| **[Unknown]** | 一次資料が存在せず、確定の材料自体がない事項 |
| **[実測]** | 本工程または既存調査文書で一次データにより直接確認した事実 |

**[起案] は提案であって事実ではない。** 本文書を引用する際、[継承] と [起案] を混同してはならない。

### 0.3 禁止事項の遵守状況

| # | 禁止事項 (指示) | 遵守状況 |
|---|---|---|
| 1 | 既存 Decision の変更 | **未実施** (変更・supersede とも行っていない。参照のみ) |
| 2 | DP-1 の再設計 | **未実施** (DP-1-A / DP-1-B / DP-1-C を前提条件として引き写し、内容に一切手を加えていない) |
| 3 | Migration Plan の作成 | **未実施** (第10章は参考情報であり、手順・順序・期限を含まない) |
| 4 | コード変更 | **未実施** |
| 5 | 実装を前提とした設計 | **未実施** (本文書は責務境界と接続点の定義に留まる) |
| 6 | Decision Ledger 登録 / Seal 生成 | **未実施** |

### 0.4 対象とする "HAB" の特定 (重要)

`JARVIS_BOUNDARY_ANALYSIS.md` §1 (R2訂正後) および `HAB_CORE_DEFINITION_v0.1.md` §0.4 のとおり、
"HAB" は少なくとも4つの異なる対象を指す [実測]。

| # | 呼称 | 一次出典 | 制度状態 | 本文書との関係 |
|---|---|---|---|---|
| **HAB-A** | **Human Authority Boundary** | `docs/governance/mocka_hab_v1_contract.md` / `HAB_CORE_DEFINITION_v0.1.md` | DRAFT | **本文書の対象** |
| HAB-B | HAB spine (`semantic/query_engine/`) | `docs/contracts/phase8_hab_runtime_integration_v1.md` | DRAFT / コード未配線 | 対象外 |
| HAB-C | PHI-HAB (構想) | `Desktop\aimd\ジャビス.md` | 未登録 | 対象外 (HG-J03 裁定待ち) |
| HAB-D | PHI-HAB (制度) | `DC_20260729_008` | **Active** | 対象外 (HG-J03 裁定待ち) |

**本文書の "Human Authority Boundary (HAB) Runtime" は HAB-A を指す。**
本文書は HG-J03 を先取りしない。HAB-C / HAB-D の帰属は依然 Human Gate 裁定事項である。

### 0.5 本文書が依拠する資料の制度状態 (先に明示する)

本文書は、制度状態の異なる資料の上に構成されている。**この非対称性は設計上の重要な前提である。**

| 資料 | 制度状態 | 本文書での扱い |
|---|---|---|
| `DC_20260807_001` (DP-1) | **Active** | **前提条件 (Freeze Point)。変更しない** |
| `DC_20260712_008` / `DC_20260705_008` / `DC_20260705_009` / `DC_20260728_003` / `DC_20260729_013` / `DC_20260730_009` / `DC_20260713_003` / `DC_20260801_002` | **Active** | [継承]。変更しない |
| `DC_20260729_001` (JARVIS 構想の扱い = Deferred) / `DC_20260729_009` (Authority Flow = Pending) | **Active (内容は Pending / Deferred)** | 未解決のまま維持。解消を前提としない |
| `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md` / `jarvis_authority_boundary.md` | Status 行なし。DP-1 が基準文書として参照 | [継承] として扱う。制度位格の確定は未裁定 |
| `JARVIS_CONSTITUTION_DRAFT.md` | **DRAFT (HG-J01..J09 未裁定)** | 参照するが、確定した規範として扱わない |
| `HAB_CORE_DEFINITION_v0.1.md` | **DRAFT (HG-H01..H10 未裁定)** | 同上 |
| `JARVIS_{ARCHITECTURE_CURRENT,RUNTIME_FLOW,BOUNDARY_ANALYSIS,GAP_ANALYSIS,CAPABILITY_INVENTORY}.md` | INVESTIGATION (調査記録) | [実測] の出典として参照 |
| `Desktop\aimd\ジャビス.md` | **Decision Ledger 未登録** | 定義の出典としては採用しない (HG-J01 未裁定) |

**帰結:** 本文書が定義する Runtime beta は、**Active な Decision に裏付けられた層 (DP-1 の State / Authority / Execution / Memory) の上に、
未裁定の層 (JARVIS Constitution / HAB Core Definition) を経由して構成される。**
したがって本文書自身も、下位の未裁定事項が裁定されるまで確定しない。

---

## 1. 目的

### 1.1 本文書の目的

**JARVIS Runtime beta の構成要素・責務境界・接続点を、制度上の言葉で定義すること。**

具体的には次の6点を定義する (指示された設計対象)。

| # | 設計対象 | 本文書の該当章 |
|---|---|---|
| 1 | JARVIS Runtime 全体アーキテクチャ | 第4章 / 第5.1章 |
| 2 | Conversation Context Engine | 第5.2章 |
| 3 | GPT Orchestrator | 第5.3章 |
| 4 | Tool Orchestration Layer | 第5.4章 |
| 5 | Human Authority Boundary (HAB) Runtime | 第5.5章 / 第7章 |
| 6 | Runtime と MoCKA の接続境界 | 第5.6章 / 第8章 |

### 1.2 JARVIS Runtime beta が解こうとしている問題 [継承]

`DP1_STATE_BOUNDARY_DECISION_RECORD_DRAFT_v1.0.md` 1.1 は、DP-1 の必要性を次のように記録している (逐語)。

> JARVIS が `Explain system state` を担うためには、**何が State であるかが確定している必要がある。**

DP-1 により State の定義は確定した (`DC_20260807_001`)。
**Runtime beta が解く問題は、確定した State 定義を、人間との対話経路の上でどう扱うかである。**

`JARVIS_BOUNDARY_ANALYSIS.md` §3.3 の実測 (B-08):

> JARVIS に一意に帰属する実装は、本調査範囲で0件である。

すなわち Runtime beta は、**既存資産の再配置ではなく、責務境界の新規定義**を対象とする。

### 1.3 本文書が目的としないこと

| # | 事項 | 理由 |
|---|---|---|
| N-1 | 実装 (プロセス・ポート・DB・コード) の決定 | Architecture Definition の範囲外。`JARVIS_CONSTITUTION_DRAFT.md` §4.3 / HG-J05 が未裁定 |
| N-2 | Migration Plan の作成 | 指示により禁止。`DC_20260807_001` impact も"Migration Plan は別 Decision の対象"と定める |
| N-3 | 既存 Human Gate 5系統の統合・是正 | `HAB_CORE_DEFINITION_v0.1.md` N-1 と同じ。"既存システムの全面改修は禁止" |
| N-4 | DP-1 の A-1..A-8 の解決 | DP-1 が未解決事項として保持することを承認時に指示済み (7.2) |
| N-5 | HG-J01..J09 / HG-H01..H10 の先取り | いずれも Human Gate 裁定事項 |
| N-6 | 受入基準・完了条件の定義 | 一次資料が存在しない [Unknown]。`JARVIS_CONSTITUTION_DRAFT.md` N-6 と同じ |

---

## 2. 前提条件

### 2.1 DP-1 Freeze Point [継承 - `DC_20260807_001`、Active]

**以下3項は Human Authority が確定した判断であり、本文書はこれを変更しない。**

```
DP-1-A   State は Event history の fold 型として定義する。
         Runtime における State は Event history を畳み込んだ結果として
         導出され、独立に保持される第一級の実体ではない。

DP-1-B   Event Store (data/mocka_events.db) は State Layer の
         Primary Source である。

DP-1-C   Human Gate は Authority Layer に属し、
         State Management は Execution Layer に属する。
         両者は別層とし、同一層として扱わない。
```

同 Decision が定める併存関係も、そのまま維持する。

- `DC_20260712_008` は **supersede されない**。Memory Governance Model 軸における Event = Observation Layer 分類は維持される。
- Runtime State Reconstruction Model 軸における Event Store = Primary Source 指定と、上記は **併存する**。
- `DC_20260705_008` / `DC_20260705_009` は維持される。DP-1-C は層としての記述であり、`phi_os/human_gate.py` のモジュール分割を意味しない。

### 2.2 DP-1 が定めた層構造 [継承 - `DP1_STATE_BOUNDARY_DECISION_RECORD_DRAFT_v1.0.md` 第4章]

| 層 | DP-1 における裁定範囲 |
|---|---|
| **JARVIS** (intelligence layer) | DP-1 の裁定範囲外。既存証拠 (`JARVIS_OPERATING_RULES_v0.1.md`) による |
| **Authority Layer** | **DP-1 が定める。** Human Gate が属する |
| **Execution Layer** (State Management) | **DP-1 が定める。** 状態の保持・遷移の実行 |
| **State Layer** | **DP-1 が定める。** State = Event history fold 型 / Primary Source = Event Store |
| **Memory Layer** | DP-1 は内容を定めない。`DC_20260712_008` の定めが適用される |
| **Action Layer** | **DP-1 は内容を定めない。** 既存参照2件のみ |

**A-1 (未解決、承認時の指示により保持):**
Decision Statement の **Execution Layer** と Architecture Boundary の **Action Layer** が同一層を指すか別層かは未解決である。
**本文書は A-1 を解決しない。** 本文書は Execution Layer の語のみを用い、Action Layer への言及を行わない。
この選択自体が A-1 の解決を意味しないことを明記する (第9章 RB-09)。

### 2.3 本文書が変更しない Active Decision [継承]

`DC_20260807_001` / `DC_20260712_008` / `DC_20260705_008` / `DC_20260705_009` /
`DC_20260728_003` / `DC_20260729_008` / `DC_20260729_009` / `DC_20260729_013` /
`DC_20260730_009` / `DC_20260731_003` / `DC_20260731_005` / `DC_20260713_003` /
`DC_20260712_005` / `DC_20260724_008` / `DC_20260801_002` / `DC_20260729_001` / `DC_20260725_003`

**本文書はこれらのいずれも supersede せず、変更を提案しない。**

### 2.4 実測済みの Runtime 事実 [実測 - `JARVIS_ARCHITECTURE_CURRENT.md` / `JARVIS_RUNTIME_FLOW.md`、2026-08-04]

Runtime beta の接続先となる既存実体。**本文書はこれらの構成を変更しない。**

| 実体 | 実測値 |
|---|---|
| `app.py` :5000 | Flask route 109件 / blueprint 11件。`phi_os.event_gate` の `gate_bp` を登録済み |
| `mocka_mcp_server.py` :5002 | MCP tools 23件。`/mcp` (MCP プロトコル) と `/agent/<tool_name>` (HTTP 直接) の2経路 |
| `gateway/gateway.py` :5010 | route 9件。`X-MoCKA-Key` ヘッダ必須 (未付与で401)。外部AI adapter 5種 |
| `phi_os/event_gate.py` `process_event()` | "これ以外に events 保存を行う経路は制度上存在しない"と自己宣言 |
| `data/mocka_events.db` | `events` / `event_signatures` / `human_gate_events` ほか |
| `data/decisions/decision_ledger.jsonl` | append-only。3ストアに分散して同名ファイルが存在する (B-04) |
| `structural/execution_governance.py` (GL7) | 固定パイプライン。`app.py` / `mocka_mcp_server.py` は GL7 を import していない |

**未接続・不在として実測されている事項:**

- ミッション上の "HAB" 段に該当する **実行時コンポーネントは存在しない** (`JARVIS_RUNTIME_FLOW.md` §10)
- `core_kernel/` (133 .py) は外部からの import 0件 (未配線)
- `phi_os/human_gate.py` の `human_gate_bp` は `app.py` に未登録 (HTTP 到達不能)
- fold の実装は存在しない。`phi_os/event_replay.py` の `replay()` は `what_type` によるグループ化であり畳み込みではない (`DC_20260807_001` impact 事実1)

---

## 3. 設計原則

各原則について、[継承] は出典を、[起案] は未裁定であることを明記する。

### 3.1 State に関する原則

| # | 原則 | 区分 | 出典 |
|---|---|---|---|
| **P-01** | Runtime は State を独立に保持しない。State は Event history の fold 結果として導出する | **[継承]** | `DC_20260807_001` DP-1-A |
| **P-02** | State の一次供給源は Event Store である | **[継承]** | `DC_20260807_001` DP-1-B |
| **P-03** | Runtime が生成する要約・整形・提示物はすべて Derived View であり、制度上の権威を持たない | **[継承]** | 憲法原則5 / `JARVIS_CONSTITUTION_DRAFT.md` §5.1 |
| **P-04** | 会話文脈と Event Ledger が矛盾する場合、Event Ledger が優先する | **[継承]** | 憲法原則1 / `JARVIS_CONSTITUTION_DRAFT.md` §5.1 |

### 3.2 Authority に関する原則

| # | 原則 | 区分 | 出典 |
|---|---|---|---|
| **P-05** | Human Gate は Authority Layer に属し、State Management (Execution Layer) とは別層である | **[継承]** | `DC_20260807_001` DP-1-C |
| **P-06** | APPROVE / HOLD / REJECT / DEFER の確定は Human Gate Finalization (きむら博士本人) のみが行う | **[継承]** | `mocka_human_gate_decision_definition_v1.md` §7 |
| **P-07** | approve() / reject() の呼出は、実際に人間が UI/API を操作した場合にのみ許可する。自動ロジック・推論結果による呼出経路を一切設けない | **[継承]** | `DC_20260705_008` (3) |
| **P-08** | 禁止3構造 (直接遷移 / 自動裁定ループ / HAB の意思化) を作らない | **[継承]** | `mocka_hab_human_gate_relation_v1.md` §4 |
| **P-09** | **Runtime beta のいかなる構成要素も、出力に `decision` フィールドを含めてはならない** | **[起案]** | `mocka_human_gate_decision_definition_v1.md` §6 の JARVIS への適用。`JARVIS_CONSTITUTION_DRAFT.md` §2.2 と同旨。未裁定 |

### 3.3 Orchestration に関する原則

| # | 原則 | 区分 | 出典 |
|---|---|---|---|
| **P-10** | **Orchestration は Authority ではない。** GPT Orchestrator は"どの順序で何を照会するか"を扱い、"それを許可してよいか"を扱わない | **[起案]** | `JARVIS_CONSTITUTION_DRAFT.md` §1.4 (JARVIS は"それを許可できるか"を判断しない) の適用。未裁定 |
| **P-11** | Runtime beta は新規プロセス・新規ポート・新規 DB を定義しない | **[起案]** | `JARVIS_CONSTITUTION_DRAFT.md` §4.3 と同姿勢。未裁定 (HG-J05) |
| **P-12** | Runtime beta は自身の権限範囲・禁止事項を変更する提案を、自ら実行してはならない | **[継承+起案]** | 自己適用原則 (憲法原則2) / `JARVIS_CONSTITUTION_DRAFT.md` §3.3 |

### 3.4 記録と証拠に関する原則

| # | 原則 | 区分 | 出典 |
|---|---|---|---|
| **P-13** | events 保存は `phi_os/event_gate.py: process_event()` 経由のみとする | **[継承]** | `phi_os/event_gate.py` 自己宣言 / `DC_20260725_003` |
| **P-14** | 継続前提が提示された場合、5段階確認 (会話履歴 -> 実ファイル -> Decision Ledger -> Event Ledger -> その他履歴) を行い、一致する証拠がなければ未検証文脈として隔離し作業を進めない | **[継承]** | `DC_20260730_009` |
| **P-15** | 記録なき Runtime の動作は制度として存在しない (沈黙の禁止) | **[継承]** | 憲法原則1 / `PHI_OS_CONSTITUTION_v1.md` 1.2 |
| **P-16** | 境界越えの参照は read-only を既定とする。Runtime beta が write できるのは自身の入出力を記録する Event のみとする | **[起案]** | `DC_20260728_003` / RC-011 の様式適用。`JARVIS_CONSTITUTION_DRAFT.md` §4.2 と同旨。未裁定 |

### 3.5 制度判断ソースに関する原則

| # | 原則 | 区分 | 出典 |
|---|---|---|---|
| **P-17** | **Decision Ledger を唯一の制度判断ソースとする。** Runtime beta は制度判断の根拠を Decision Ledger 以外から取得しない | **[起案 - 指示による]** | 本工程の必須条件。下記の未解決点あり |

**P-17 に関する記録上の確認事項 (本文書では確定させない):**

`DC_20260712_008` (Active) は Durable Layer / 正本 の対象を **4件** と定めている (逐語)。

> 対象=Decision Ledger, Integrity Ledger, Anchor Record, Governance Decision。用途=制度判断/長期記憶/監査基準。

指示された P-17 (Decision Ledger を唯一の制度判断ソースとする) と、`DC_20260712_008` が挙げる Durable Layer 4件との対応関係は、
いずれの一次資料にも記載がない。**本文書はこれを断定せず、両表記をそのまま記録する** (第9章 RB-02)。

---

## 4. システム構成図

### 4.1 全体構成

各要素について、本文書が定めるものを `[起案]`、既存の Active Decision / 実測に基づくものを `[継承]`、
DP-1 が定めた層を `[DP-1]`、裁定範囲外を `[範囲外]` と表記する。

```
  ===================================================================
   HUMAN AUTHORITY  (きむら博士)                          [継承]
   Human Gate Finalization
   APPROVE / HOLD / REJECT / DEFER の確定
   出典: mocka_human_gate_decision_definition_v1.md 7
  ===================================================================
        ^                                     |
        | 提示のみ (decision を含まない)      | 裁定結果
        | P-09                                | (人間の操作のみ) P-07
        |                                     v
  +=================================================================+
  |  JARVIS RUNTIME beta   (intelligence layer)          [起案]     |
  |  JARVIS is an intelligence layer.                    [継承]     |
  |  出典: phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md                |
  +-----------------------------------------------------------------+
  |                                                                 |
  |  JRB-1  Conversation Context Engine  (CCE)           [起案]     |
  |         人間の発話 -> 制度環境が扱える要求形式への変換          |
  |         保持する文脈は Derived View (P-03)                      |
  |         5段階確認と未検証文脈の隔離 (P-14)                      |
  |                          |                                      |
  |                          v                                      |
  |  JRB-2  GPT Orchestrator  (GPO)                      [起案]     |
  |         照会の順序づけ / 分解 / 統合                            |
  |         Orchestration は Authority ではない (P-10)              |
  |         出力に decision を含めない (P-09)                       |
  |                          |                                      |
  |          +---------------+---------------+                      |
  |          v                               v                      |
  |  JRB-3  Tool Orchestration      JRB-4  HAB Runtime   [起案]     |
  |         Layer  (TOL)     [起案]        (Human Authority         |
  |         既存 tool の呼出のみ            Boundary Runtime)       |
  |         新規 tool を定義しない          Authority 境界の         |
  |         write は自身の Event のみ       検査と提示に限る         |
  |          |                               |                      |
  +----------|-------------------------------|----------------------+
             |                               |
             |  JRB-5  MoCKA Connection Boundary  (MCB)   [起案]
             |         read は allowlist / write は event_gate 経由のみ
             v                               v
  +=================================================================+
  |  AUTHORITY LAYER                                      [DP-1]    |
  |    Human Gate  (approve / reject の権限行使)                    |
  |    人間操作のみ  DC_20260705_008 (3)                  [継承]    |
  |    approved_by=human が Seal 成立条件 DC_20260713_003 [継承]    |
  |    authority_manager.py                              [範囲外]   |
  +=================================================================+
        ^  権限行使 (人間のみ)        |  承認済みの状態遷移
        |                              v
  +=================================================================+
  |  EXECUTION LAYER  (State Management)                  [DP-1]    |
  |    状態の保持 / 一覧表示 / 状態遷移の受付窓口                   |
  |    自動検知系は PENDING 投入のみ  DC_20260705_008 (1) [継承]    |
  |    判断・自動応答は禁止           DC_20260705_008 (2) [継承]    |
  +=================================================================+
        ^  状態の読み出し
        |
  +=================================================================+
  |  STATE LAYER                                          [DP-1]    |
  |    State = Event history fold 型                                |
  |    Primary Source: Event Store (data/mocka_events.db)           |
  |    current_view / runtime/state.json /                          |
  |    Context Snapshot の位置                           [範囲外]   |
  +=================================================================+
        ^  fold  (実装は DP-1 の範囲外。実装は存在しない)
        |
  +=================================================================+
  |  MEMORY LAYER                                         [継承]    |
  |  Memory Governance Model - DC_20260712_008 (Active)             |
  +-----------------------------+-----------------------------------+
  |  Durable Layer / 正本       |  Observation Layer / 観測層       |
  |   Decision Ledger           |   Event                           |
  |   Integrity Ledger          |   Runtime Trace                   |
  |   Anchor Record             |   Experiment Log                  |
  |   Governance Decision       |   昇格には4条件 + 別途            |
  |   用途: 制度判断 / 長期記憶 |   Human Gate Decision を要する    |
  |         / 監査基準          |                                   |
  +-----------------------------+-----------------------------------+

  注1: Event は Memory Governance Model の軸で Observation Layer に
       分類され、同時に Runtime State Reconstruction Model の軸で
       State Layer の Primary Source である。両者は併存する
       (DC_20260807_001 / 2.1.3)。
  注2: ACTION LAYER は DP-1 が内容を定めていない [範囲外]。
       Execution Layer との対応関係は A-1 として未解決である。
       本図は Execution Layer の語のみを用いる (2.2)。
  注3: 本図は責務境界の図であり、プロセス構成図ではない。
       JRB-1..JRB-5 が単一プロセスか複数プロセスかは
       本文書では確定しない (P-11 / HG-J05)。
```

### 4.2 図が意図的に描いていない線

推測で線を引かないため、以下は **描いていない**。

| 描いていない線 | 理由 |
|---|---|
| JARVIS Runtime beta から Authority Layer への **下向きの実行線** | P-06 / P-07。Runtime が Authority を実行する経路は存在してはならない |
| JARVIS Runtime beta から State Layer / Memory Layer への **直接線** | すべて JRB-5 (MoCKA Connection Boundary) を経由する。バイパス経路を設けない |
| Runtime beta から Decision Ledger への **write 線** | P-16。Runtime beta は Decision Ledger に書き込まない |
| GL7 (`structural/execution_governance.py`) との接続線 | `app.py` / `mocka_mcp_server.py` が GL7 を import していないことが実測済み [実測]。Runtime beta と GL7 の関係は [Unknown] (第9章 RB-11) |
| PHI-OS / Orchestra / P-DERS との接続線 | `DC_20260729_009` により Authority Flow が Pending。確定できない (HG-J02) |

---

## 5. コンポーネント責務

### 5.0 共通制約 [起案]

**JRB-1 から JRB-5 のすべてに、以下が例外なく適用される。**

| # | 共通制約 | 根拠 |
|---|---|---|
| C-1 | 出力に `decision` フィールドを含めない | P-09 |
| C-2 | APPROVE / HOLD / REJECT / DEFER を確定しない | P-06 |
| C-3 | 自身を `actor_type = human_authority` として記録しない | `HAB_CORE_DEFINITION_v0.1.md` P-5 |
| C-4 | `evidence_reference` を伴わない状態説明・提案を行わない | P-14 / `HAB_CORE_DEFINITION_v0.1.md` P-6 |
| C-5 | 検出した不整合を自動是正しない。一括修正を行わない | `HAB_CORE_DEFINITION_v0.1.md` P-7 |
| C-6 | 既存記録の欠落を推測で補完しない | `HAB_CORE_DEFINITION_v0.1.md` P-8 |
| C-7 | 自身の権限範囲を自ら拡張しない | P-12 |
| C-8 | events 書込は `process_event()` 経由のみ | P-13 |
| C-9 | 範囲限定の否定的所見を述べる際は、調査範囲を必ず併記する | `JARVIS_ARCHITECTURE_CURRENT.md` §0 の様式 |

---

### 5.1 JARVIS Runtime beta 全体 (JRB-0)

| 項目 | 内容 |
|---|---|
| **層** | intelligence layer [継承 - `JARVIS_OPERATING_RULES_v0.1.md`] |
| **責務** | 人間の意図を制度環境が扱える形へ変換し、その結果を提示すること。**変換より下流のいかなる責務も持たない** [継承 - `JARVIS_CONSTITUTION_DRAFT.md` §1.3] |
| **答える問い** | "人間は何を意図しているか"[起案 - `JARVIS_CONSTITUTION_DRAFT.md` §1.4、未裁定] |
| **答えてはならない問い** | "次に何をするか"(Sequence Controller) / "それを許可できるか"(MoCKA) [継承 - 同 §1.4] |
| **許可行為** | Search context / Explain system state / Detect inconsistencies / Prepare proposals / Evidence collection / Context analysis / State explanation / Risk detection / Decision proposal [継承 - `JARVIS_OPERATING_RULES_v0.1.md` / `jarvis_authority_boundary.md`] |
| **禁止行為** | Execute decisions / Change authority state / Modify audit history / Human decision replacement / Automatic approval / Automatic rejection / Authority escalation / Ledger modification [継承 - 同上] |
| **状態** | **[起案] 定義のみ。実装なし。JARVIS に一意帰属する実装は実測0件 (B-08)** |

**Runtime beta が全体として満たすべき性質 [起案]:**

1. Runtime beta の出力は、すべて Derived View である (P-03)。制度上の事実を生成しない。
2. Runtime beta は Authority Layer の入力側にのみ接続し、出力側 (裁定の実行) には接続しない。
3. Runtime beta を経由しない経路で既存システムが動作し続けることを妨げない (既存システムの全面改修は禁止)。

---

### 5.2 JRB-1 Conversation Context Engine (CCE)

| 項目 | 内容 |
|---|---|
| **責務 [起案]** | (a) 人間の発話を、制度環境が扱える要求形式へ変換する (b) 変換にあたり継続前提を検出する (c) 検出した継続前提について5段階確認を実行する (d) 一致する証拠が得られない前提を未検証文脈として隔離する |
| **入力** | 人間の発話 / 直近の会話履歴 |
| **出力 [起案]** | 要求候補 (複数可) + 各候補に紐づく `evidence_reference` + 未検証文脈のラベル一覧。**`decision` を含まない (C-1)** |
| **保持するもの** | 会話文脈。**これは Derived View であり制度上の事実ではない (P-03)** |
| **保持しないもの** | 制度上の State。State は Event history の fold 結果として State Layer から取得する (P-01 / P-02) |
| **禁止 [起案]** | 推測・記憶による文脈接続 (P-14) / 会話文脈を制度的事実として引用すること (P-03) / 未検証文脈のまま作業を継続すること |
| **既存の近接資産 [実測]** | `interface/context_composer.py` (`context_bp` 登録済み) / `gateway/context_builder.py` / `/api/living-context`。いずれも帰属未裁定 (B-01 / `JARVIS_BOUNDARY_ANALYSIS.md` §3.4) |
| **状態** | **[起案] 定義のみ。既存実装との対応は未裁定** |

**未検証文脈の扱い [継承 - `DC_20260730_009` / `JARVIS_CONSTITUTION_DRAFT.md` §5.2]:**

一致する証拠が得られない場合、CCE は次を行う。

```
1. 当該前提を"未検証文脈 (Unverified Context)"として明示的にラベル付けする
2. 作業を進めない
3. 隔離したことを人間に報告する
```

**推測で補完して会話を継続してはならない。** 隔離の解除は Human Authority のみが行える。

**会話文脈の制度的位置 [未裁定]:**
会話文脈そのものを Event として記録するか否かは、いずれの一次資料にも記載がない。
`JARVIS_CONSTITUTION_DRAFT.md` §6.2 は記録すべき事象 R-1..R-5 を [起案] しているが未裁定である (HG-J06)。
**本文書はこれを確定させない** (第9章 RB-04)。

---

### 5.3 JRB-2 GPT Orchestrator (GPO)

| 項目 | 内容 |
|---|---|
| **責務 [起案]** | (a) CCE が出力した要求候補を、実行可能な照会の列へ分解する (b) 照会の順序を決める (c) 複数照会の結果を統合し、提示形式へ整形する (d) 照会が Runtime beta の権限外である場合、実行せず拒否として記録する |
| **入力** | CCE の出力 (要求候補 + evidence_reference + 未検証文脈ラベル) |
| **出力 [起案]** | 提示材料 (統合結果 + 出所参照)。**`decision` を含まない (C-1)** |
| **扱うもの** | "どの順序で何を照会するか" |
| **扱わないもの** | "それを許可してよいか"(MoCKA の責務) / "次に何をするか"(Sequence Controller の責務) [継承 - `JARVIS_CONSTITUTION_DRAFT.md` §1.4] |
| **禁止 [起案]** | 照会結果に基づく自動実行 / 権限外要求の代替経路探索 / 拒否を回避するための要求の言い換え / 閾値による自動承認 |
| **既存の近接資産 [実測]** | `gateway/adapter_gpt.py` (接続実装であって役割定義ではない)。JARVIS との関係を定める文書は存在しない [Unknown] (`JARVIS_CONSTITUTION_DRAFT.md` N-7) |
| **状態** | **[起案] 定義のみ。実装なし** |

**"GPT を司令塔とする"ことの制度上の読み方 [起案 - 未裁定]:**

指示は GPT を司令塔とする AI オーケストレーション基盤を対象としている。
本文書はこれを **Orchestration の司令塔** と読み、**Authority の司令塔** とは読まない。根拠は次のとおり。

| 観点 | 本文書の読み | 根拠 |
|---|---|---|
| 照会の順序・分解・統合 | **GPO が担う** | 指示された設計対象 |
| 可否の判断 | **担わない** | `JARVIS_CONSTITUTION_DRAFT.md` §1.4 (MoCKA の問い) |
| 次に何をするかの決定 | **担わない** | 同 §1.4 (Sequence Controller の問い) |
| Runtime Coordination / Execution Control / Human Gate Routing | **担わない** | `DC_20260729_013` D-03 (Active) が PHI-OS の Authority Ownership として定める |

**記録上の確認事項:** `DC_20260729_013` D-03 (Active) は Runtime Coordination / Execution Control / Human Gate Routing を
**PHI-OS の Authority Ownership** と定めている。"GPT を司令塔とする"がこの範囲に及ぶか否かは、いずれの一次資料にも記載がない。
**本文書はこれを断定せず、上表の読みを [起案] として提示するに留める** (第9章 RB-01)。

---

### 5.4 JRB-3 Tool Orchestration Layer (TOL)

| 項目 | 内容 |
|---|---|
| **責務 [起案]** | (a) GPO が決めた照会を、既存の tool 呼出へ写像する (b) 呼出結果を、加工せずに GPO へ返す (c) 呼出が allowlist 外である場合、実行せず拒否する (d) 自身の呼出と拒否を Event として記録する |
| **入力** | GPO が決めた照会列 |
| **出力** | tool 応答 (加工なし) + 拒否記録 |
| **呼出可能な対象 [起案]** | **既存の tool のみ。** 実測済みの経路 (第8章) の範囲に限る |
| **禁止 [起案]** | 新規 tool の定義 / 新規エンドポイントの追加 / 応答の要約による意味変更 / allowlist 外呼出の代替経路探索 / `process_event()` を経由しない events 書込 (C-8) |
| **write 権限 [起案]** | **自身の入出力を記録する Event のみ。** Decision Ledger / TODO / Registry / Integrity 台帳への書込は権限外 (P-16) |
| **既存の近接資産 [実測]** | MCP tools 23件 (`mocka_mcp_server.py` :5002) / gateway route 9件 (:5010)。`mcp/` パッケージは稼働プロセスとは別実体 |
| **状態** | **[起案] 定義のみ。実装なし** |

**Adapter 制約の適用 [継承 - `DC_20260729_013` D-02、Active]:**

Adapter = Translation Boundary であり、次を禁止する。

```
意思決定生成 / ポリシー変更 / 権限判断 / Human Gate 代替 / 証跡改変
```

**TOL はこの制約を満たす範囲に留まる。** TOL は変換のみを行い、内容の付加・省略をしない。

**帰属層の未確定 [未裁定]:**
TOL が Execution Layer に属するか、それとも intelligence layer 内部の構成要素に留まるかは、
A-1 (Execution Layer と Action Layer の対応関係) が未解決であるため確定できない。
**本文書は TOL を JARVIS Runtime beta の内部構成要素として記述し、Execution Layer への帰属を主張しない** (第9章 RB-09)。

---

### 5.5 JRB-4 Human Authority Boundary (HAB) Runtime

**対象は HAB-A (Human Authority Boundary) である (0.4)。**

| 項目 | 内容 |
|---|---|
| **責務 [起案]** | (a) 要求が Authority Layer の裁定を要するか否かを判定材料として整理する (b) 裁定を要する場合、Human Gate への提示材料を整形する (c) 提示材料に `decision` を含めないことを保証する (d) Runtime beta の各構成要素が C-1..C-9 に抵触していないかを検査する (e) 抵触を検出した場合、実行を止め記録する |
| **入力** | GPO / TOL の出力 |
| **出力 [起案]** | Human Gate 提示材料 (`decision` を含まない) / 抵触検出時の停止記録 |
| **決して行わないこと** | 裁定そのもの (P-06) / 裁定の先取り / 裁定の代行 / 期限切れ以外の自動状態遷移 |
| **状態** | **[起案] 定義のみ。実装なし。実行時にイベントが通過する HAB 実装は実測で不在 (`JARVIS_RUNTIME_FLOW.md` §10)** |

**HABR は"判断"ではなく"境界検査"である [起案]:**

`mocka_hab_human_gate_relation_v1.md` §4 は **HAB の意思化 (状態記述層が判断主体になる構造)** を禁止している [継承]。
HABR は次を扱う。

| HABR が扱う | HABR が扱わない |
|---|---|
| 境界に抵触しているか (検査) | 許可してよいか (判断) |
| 提示材料の形式要件を満たしているか | 提示材料の内容の妥当性 |
| actor が Authority を持つか (記録上の識別) | actor に Authority を与えること |

**Canonical State との関係 [未裁定]:**
`HAB_CORE_DEFINITION_v0.1.md` §2 は canonical state 8値 (`IDLE` / `EVALUATING` / `PENDING_HUMAN_GATE` /
`APPROVED` / `REJECTED` / `DEFERRED` / `EXPIRED` / `CANCELLED`) を定義しているが、同文書は **DRAFT (未裁定)** である。
`HOLD` に対応する状態が存在しない点は HG-H01 として未裁定である。
**本文書は canonical state を確定した語彙として扱わず、HABR がどの状態語彙を用いるかを確定しない** (第9章 RB-05)。

**Human Gate 接続先の未確定 [未裁定]:**
Human Gate 実装は実測で5系統に分散している (HG-1..HG-5、`HAB_CORE_DEFINITION_v0.1.md` §1 F-1)。
**HABR がどの Human Gate に接続するかは HG-J04 として未裁定であり、本文書は確定しない。**

---

### 5.6 JRB-5 MoCKA Connection Boundary (MCB)

| 項目 | 内容 |
|---|---|
| **責務 [起案]** | (a) Runtime beta と MoCKA の間の唯一の通過点となる (b) read 要求を allowlist に照合する (c) write 要求を `process_event()` 経由に限定する (d) 通過したすべての要求と拒否を記録する |
| **read 経路 [継承 - 実測]** | 第8章の実測済み経路のみ |
| **write 経路 [継承]** | `phi_os/event_gate.py: process_event()` のみ (P-13 / C-8) |
| **禁止 [起案]** | MCB を経由しない直接接続 / MoCKA 本体への直接 import (`DC_20260728_003`) / 生 SQL による events 書込 / Decision Ledger への write |
| **状態** | **[起案] 定義のみ。実装なし** |

**read-only allowlist 様式の適用 [継承 - `DC_20260728_003` / RC-011]:**

PHI-OS Core から MoCKA への接続は、既に read-only allowlist 強制がコード実測で確認されている
(`PlanningCaliber/workshop/phi-os/phios/phl/relay_client.py`)。

```
MCP_URL        = "http://localhost:5002/mcp"
GATE_AUDIT_URL = "http://localhost:5000/api/gate/audit"
raise RelayError(f"refused: '{tool_name}' is not in the read-only allowlist")
```

**MCB はこの様式を踏襲する [起案]。** ただし allowlist の具体的内容は本文書では確定しない
(確定は実装を前提とするため。第9章 RB-08)。

---

## 6. データフロー

以下は責務境界上のフローであり、**プロセス間通信の設計ではない**。
既存の実測済み経路 (`JARVIS_RUNTIME_FLOW.md`) を変更しない。

### 6.1 F-1: 状態説明 (Explain system state) [起案]

```
[人間]  発話
   |
   v
JRB-1 CCE
   |  要求候補への変換
   |  継続前提の検出 -> 5段階確認 (P-14)
   |  一致する証拠なし -> F-4 へ分岐
   v
JRB-2 GPO
   |  照会の分解と順序づけ
   v
JRB-3 TOL
   |  既存 tool 呼出へ写像
   v
JRB-5 MCB
   |  allowlist 照合 -> 不一致は拒否 (F-4 へ)
   v
[MoCKA]  State Layer から状態を取得
   |     State = Event history fold 型 (P-01)
   |     Primary Source = Event Store (P-02)
   |
   |  注: fold の実装は存在しない (2.4)。
   |      本フローは fold が成立している前提の責務図であり、
   |      現時点で実行可能であることを意味しない (RB-07)。
   v
JRB-3 TOL   応答を加工せず返す
   |
   v
JRB-2 GPO   統合・整形  (decision を含まない: C-1)
   |
   v
JRB-4 HABR  境界検査 (C-1..C-9 への抵触有無)
   |
   v
[人間]  提示  (Derived View である旨を明示: P-03)
```

### 6.2 F-2: Runtime beta 自身の動作記録 [起案]

```
JRB-1..JRB-4 の各動作
   |
   v
JRB-5 MCB
   |  write 要求は process_event() 経由に限定 (P-13 / C-8)
   v
[MoCKA]  phi_os/event_gate.py  process_event()
   |     validate -> event_id 採番 -> when_ts 補完
   |     -> event_source 付与 -> _write()
   |     -> events / event_signatures へ INSERT
   v
data/mocka_events.db

  記録形式 (what_type の新設要否等) は未裁定 (HG-J06 / RB-06)。
  本文書は記録先を process_event() 経由と定めるのみで、
  スキーマ・値域を定めない。
```

### 6.3 F-3: 裁定を要する要求 [起案]

```
[人間]  発話 (裁定を要する事項を含む)
   |
   v
JRB-1 CCE -> JRB-2 GPO
   |
   v
JRB-4 HABR
   |  裁定を要する事項として整理
   |  提示材料を整形 (decision フィールドを含めない: C-1 / P-09)
   v
[Human Gate]  Authority Layer                        [DP-1-C]
   |
   |  APPROVE / HOLD / REJECT / DEFER の確定は
   |  Human Gate Finalization (きむら博士本人) のみ  (P-06)
   |  approve() / reject() は人間の UI/API 操作のみ  (P-07)
   |
   |  Runtime beta からこの遷移を起こす経路は存在しない
   |  (図に線を引いていない: 4.2)
   v
[Execution Layer]  承認済みの状態遷移               [DP-1-C]
   |
   v
[State Layer]  Event として記録される -> State に反映
```

**この経路において Runtime beta が行えるのは提示までである。**
裁定の実行、裁定結果の予測、裁定の代行、沈黙を承認とみなすことは、いずれも行わない。

### 6.4 F-4: 拒否経路 [起案]

Runtime beta が要求を実行しない場合の経路。**拒否も記録対象である (P-15)。**

| 拒否事由 | 検出箇所 | 動作 |
|---|---|---|
| 未検証文脈 (5段階確認で証拠不一致) | JRB-1 CCE | 隔離ラベル付与 -> 作業停止 -> 人間へ報告 (P-14) |
| Runtime beta の権限外の要求 | JRB-2 GPO | 実行せず拒否として記録 |
| allowlist 外の tool 呼出 | JRB-5 MCB | 実行せず拒否 |
| C-1..C-9 への抵触 | JRB-4 HABR | 実行を止め記録 |

**拒否の際に行ってはならないこと [起案]:** 代替経路の探索 / 要求の言い換えによる再試行 /
拒否理由の推測による補完 / "軽微だから"という理由での通過。

---

## 7. Human Authority の位置付け

### 7.1 Human Authority は Runtime beta の外側にある [継承]

**Human Authority は Runtime beta の構成要素ではない。**

| 出典 | 内容 |
|---|---|
| `DC_20260807_001` DP-1-C (Active) | Human Gate は Authority Layer に属する。State Management (Execution Layer) とは別層 |
| `phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md` | JARVIS is an intelligence layer. Human Gate is an authority layer. |
| `mocka_human_gate_decision_definition_v1.md` §7 | APPROVE/HOLD/REJECT/DEFER の確定は Human Gate Finalization (博士本人) のみが行う |
| `DC_20260705_008` (3) | approve()/reject() の呼出は、実際に人間が UI/API を操作した場合にのみ許可する |
| `DC_20260729_013` D-03 (Active) | Human = Architecture Authority / Policy Change Approval / Irreversible Decision |
| `DC_20260713_003` (Active) | `approved_by=human` を Seal 成立条件として必須化 |
| `phi_os/hab/actor_model.json` | human: authority=decision, can_finalize=true / jarvis: authority=advisory, can_finalize=false / system: authority=execution, can_finalize=false |

### 7.2 Authority 境界の維持方法 [起案]

Runtime beta は次の4点により Authority 境界を維持する。

| # | 方法 | 根拠 |
|---|---|---|
| M-1 | Runtime beta の出力に `decision` フィールドを設けない (C-1 / P-09) | 出力が裁定とみなされる経路を構造的に作らない |
| M-2 | Runtime beta から Authority Layer への実行線を定義しない (4.2) | 経路が存在しなければ迂回も存在しない |
| M-3 | Runtime beta の actor_type を `human_authority` としない (C-3) | 記録上も Authority を詐称しない |
| M-4 | 閾値・条件・軽微性による自動通過条項を一切設けない | `mocka_hab_human_gate_relation_v1.md` §4 自動裁定ループ禁止 |

### 7.3 自動裁定化リスクの自己点検 [起案]

`mocka_hab_human_gate_relation_v1.md` §4 が禁止する3構造に該当しないことを確認する。

| 禁止構造 | 本文書での扱い |
|---|---|
| **直接遷移** (Human Gate を経由しない ACTIVE 遷移) | 6.3 において Runtime beta から Authority Layer への遷移線を **定義していない** |
| **自動裁定ループ** (Core -> 自動 APPROVE 確定) | 閾値・条件による自動承認条項を **一切設けていない** (M-4) |
| **HAB の意思化** (状態記述層が判断主体になる) | JRB-4 HABR を"境界検査"に限定し、判断ロジックを **定義していない** (5.5) |

| 追加点検 | 結果 |
|---|---|
| Runtime beta が承認を確定できる条項 | **なし** (P-06 / C-2) |
| Runtime beta の出力が承認とみなされる経路 | **なし** (C-1、出力に decision を持たない) |
| Human Gate をスキップできる条件条項 | **なし** (条件付きスキップ条項を設けていない) |
| "軽微な変更は自動承認"等の閾値条項 | **なし** (意図的に設けていない) |
| 沈黙・無応答が承認とみなされる条項 | **なし** |
| Runtime beta が自身の権限を拡張できる条項 | **なし** (P-12 / C-7) |
| 既存データを書き換える設計 | **なし** (C-5 / C-6) |
| GPT Orchestrator が"司令塔"であることを根拠に判断権を得る条項 | **なし** (P-10 / 5.3) |

**本点検は起草者による自己申告であり、検証の代替にならない。** 検証は第9.3章 HG-RB-06 に提示する。

---

## 8. MoCKA との接続点

**本章に列挙するのは、既に実測済みの経路のみである。新規経路を定義しない (P-11)。**

### 8.1 read 接続点 [実測 - `JARVIS_ARCHITECTURE_CURRENT.md` / `JARVIS_RUNTIME_FLOW.md`]

| # | 接続点 | 実体 | Runtime beta での用途 [起案] |
|---|---|---|---|
| R-1 | MCP tools (read 系) | `mocka_mcp_server.py` :5002。`mocka_get_overview` / `mocka_get_essence` / `mocka_get_todo` / `mocka_list_events` / `mocka_read_event` / `mocka_search` / `mocka_get_incidents` / `mocka_get_guidelines` / `mocka_get_command_center` / `mocka_registry_get` / `mocka_registry_current_state` / `mocka_decision_get` / `mocka_decision_list` / `mocka_integrity_get` / `mocka_integrity_list` | 状態照会 / Evidence 収集 |
| R-2 | HTTP 直接呼出 | `POST /agent/<tool_name>` (:5002) | MCP セッション不通時の代替経路 |
| R-3 | Gate audit read | `GET /api/gate/audit` (:5000) | 監査情報の参照 |
| R-4 | Gateway read route | `/api/v1/{context,todo,phase,essence,last_event,summary,health}` (:5010、`X-MoCKA-Key` 必須) | 外部AI 経路からの参照 |

**制度判断ソースとしての read [起案 - P-17]:**
制度判断の根拠を取得する read は **R-1 の `mocka_decision_get` / `mocka_decision_list` に限る**。
他の read はいずれも Observation Layer の参照であり、制度判断の根拠としない。
ただし P-17 と `DC_20260712_008` Durable Layer 4件との関係は未解決である (RB-02)。

### 8.2 write 接続点 [継承]

| # | 接続点 | 実体 | Runtime beta での可否 |
|---|---|---|---|
| W-1 | `process_event()` 経由の Event 書込 | `mocka_write_event` (MCP) -> `POST localhost:5000/api/gate/event` | **可。ただし自身の入出力の記録のみ** (P-16) |
| W-2 | Decision Ledger 書込 | `mocka_decision_write` | **不可** (P-16 / C-2) |
| W-3 | Integrity 台帳書込 | `mocka_integrity_write` | **不可** (P-16) |
| W-4 | TODO 書込 | `mocka_add_todo` / `mocka_update_todo` | **不可** (P-16) |
| W-5 | Registry 書込 | `mocka_registry_add` | **不可** (P-16) |
| W-6 | Seal 実行 | `mocka_seal` | **不可**。`approved_by=human` が Seal 成立条件 (`DC_20260713_003`) |
| W-7 | 生 SQL による events 書込 | - | **不可** (P-13。`gateway/gateway.py` も Phase5-1 で禁止済み) |

### 8.3 接続してはならない経路 [起案]

| # | 経路 | 理由 |
|---|---|---|
| X-1 | MoCKA 本体パッケージへの直接 import | `DC_20260728_003` (Active) |
| X-2 | `phi_os/human_gate.py` の HTTP API | `human_gate_bp` が `app.py` に未登録で到達不能 [実測]。到達可能化は本文書の範囲外 |
| X-3 | `core_kernel/` 配下 | 外部 import 0件の未配線資産 [実測]。配線は本文書の範囲外 |
| X-4 | `data/mocka_events.db` への直接アクセス | P-13 |
| X-5 | `data/decisions/decision_ledger.jsonl` への直接書込 | P-16。3ストア分散問題 (B-04) にも触れない |

### 8.4 接続境界の性質 [起案]

| 性質 | 内容 |
|---|---|
| **単一通過点** | Runtime beta と MoCKA の間の通過点は JRB-5 MCB のみとする。バイパスを設けない |
| **非対称** | read は allowlist 制、write は `process_event()` 単一経路制。両者は同じ規律ではない |
| **既存経路の不変** | 本文書は既存の経路A (MCP) / 経路B (外部AI Gateway) / 経路C (PHI-OS read-only) のいずれも変更しない |
| **fail する側** | allowlist 不一致・権限外要求は **実行せず拒否**する。fail-open にしない |

---

## 9. 未解決事項

**本章は解決を提案しない。未解決であることの記録である。**

### 9.1 既存の未解決事項 (継承。本文書は解決しない)

| 出典 | ID | 内容 |
|---|---|---|
| `DC_20260807_001` / DP-1 7.2 | **A-1** | Execution Layer と Action Layer の対応関係。**承認時の指示により未解決事項として保持** |
| 同 | A-2 | 層名 Memory Layer と既存 `MEMORY_LAYER.md` / `memory/` (4種記憶) の関係 |
| 同 | A-3 | 層名 State Layer と既存2用法 (HAB STATE LAYER / `minimal_safe_architecture_v1.md`) の関係 |
| 同 | A-4 | `INSTITUTION_RUNTIME_v1.md` の `authority_manager.py` と Authority Layer の関係 |
| 同 | A-5 | `current_view` / `runtime/state.json` / Context Snapshot の State Layer 内における位置 |
| 同 | A-6 | 分類B 5件 (PROPOSED、Decision Ledger 参照0件) の処遇 |
| 同 | A-7 | `HAB_CORE_DEFINITION_v0.1.md` の Canonical State と DP-1 の State 定義の関係 |
| `JARVIS_CONSTITUTION_DRAFT.md` §9 | HG-J01..J09 | JARVIS の定義出典・帰属 Institution・PHI-HAB の指す対象・接続する Human Gate・実装形態・Event 記録形式・権限境界の採否・自己点検の検証・Ledger 登録単位 |
| `HAB_CORE_DEFINITION_v0.1.md` §10 | HG-H01..H10 | `HOLD` の扱い・`EXPIRED` 期限条件・`NEW` の対応・`split` の扱い・`WAITING_FOR_HUMAN_GATE` の対応・HG-3 mapping・`evidence_hash` 仕様・Transition Ledger 記録先・自己点検の検証・Status 変更 |
| `JARVIS_BOUNDARY_ANALYSIS.md` §5 | B-01..B-08 | HAB の多義性・PHI-HAB と Memory の関係・Human Gate 5系統分散・Decision Ledger 3ストア分散・Orchestra/Adapter/Memory の複数実体・`core_kernel/` 未配線・P-DERS・JARVIS 帰属実装0件 |
| `DC_20260729_009` (Active) | - | PHI-Con / PHI-Core 間の Authority 階層は Option D (条件付き Pending Resolution) として未解決保持 |
| `DC_20260729_001` (Active) | - | JARVIS 構想の扱いは Deferred (将来の PHI-OS 全体再設計時に再評価) |

### 9.2 本文書が新たに提起する未解決事項

| ID | 未解決事項 | 観測根拠 | 影響 |
|---|---|---|---|
| **RB-01** | "GPT を司令塔とする"ことと `DC_20260729_013` D-03 (Active) が定める PHI-OS の Authority Ownership (Runtime Coordination / Execution Control / Human Gate Routing) との関係。同一範囲を指すか、別範囲か | 5.3 | GPO の責務上限が確定しない |
| **RB-02** | "Decision Ledger を唯一の制度判断ソースとする"ことと `DC_20260712_008` (Active) が定める Durable Layer 4件 (Decision Ledger / Integrity Ledger / Anchor Record / Governance Decision) との関係 | 3.5 | 制度判断の根拠として read してよい対象が確定しない |
| **RB-03** | `HAB_CORE_DEFINITION_v0.1.md` が `docs/governance/` と `phi_os/hab/` の2箇所に同名で存在し、**内容が異なる**。前者は HAB-A の最小定義 (DRAFT、10章構成)、後者は HG-J04 Evidence の要約 (27行)。DP-1 は前者の 0.1 を"上位方針"として引用している | 本工程で実測 | 参照先の同定が場面ごとに変わりうる |
| **RB-04** | 会話文脈そのものを Event として記録するか否か。記録する場合の粒度 | 5.2 | CCE の記録義務が確定しない |
| **RB-05** | HABR が用いる状態語彙。`HAB_CORE_DEFINITION_v0.1.md` の canonical state 8値は DRAFT であり、`HOLD` 不在問題 (HG-H01) が未裁定 | 5.5 | HABR の出力形式が確定しない |
| **RB-06** | Runtime beta の Event 記録形式。`what_type` の新設要否 (HG-J06 と同一論点) | 6.2 | 記録の検索性・分類が確定しない |
| **RB-07** | fold の実装が存在しない (`DC_20260807_001` impact 事実1)。DP-1-A が定める State 定義を Runtime 上で成立させる手段が現時点で存在しない | 6.1 | F-1 (状態説明) が現時点で実行可能でない |
| **RB-08** | MCB の allowlist の具体的内容。tool 単位か、tool 群単位か、応答フィールド単位か | 5.6 | 接続境界の粒度が確定しない |
| **RB-09** | TOL の帰属層。A-1 (Execution Layer / Action Layer) が未解決であるため確定できない | 5.4 | 層構造上の位置が確定しない |
| **RB-10** | GPO と既存 `gateway/adapter_gpt.py` の関係。帰属を定める文書が存在しない (`JARVIS_CONSTITUTION_DRAFT.md` N-7 と同一論点) | 5.3 | 既存資産との重複・競合が判定できない |
| **RB-11** | Runtime beta と GL7 (`structural/execution_governance.py`) の関係。`app.py` / `mocka_mcp_server.py` は GL7 を import していない [実測] | 4.2 | Runtime beta の動作が GL7 の統制下にあるか否かが確定しない |
| **RB-12** | 本文書が依拠する `JARVIS_CONSTITUTION_DRAFT.md` / `HAB_CORE_DEFINITION_v0.1.md` がいずれも DRAFT (未裁定) である。本文書の [継承] のうち、これら2文書由来のものは厳密には継承ではない | 0.5 | 本文書自身の確定条件に関わる |

### 9.3 Human Gate 提示事項

**本節は `decision` フィールドを含まない** (`mocka_human_gate_decision_definition_v1.md` §6)。

| ID | 判断事項 | 依存 |
|---|---|---|
| **HG-RB-01** | "GPT を司令塔とする"の制度上の範囲 (5.3 の読みを採用するか) | RB-01 / `DC_20260729_013` |
| **HG-RB-02** | 制度判断ソースの範囲 (Decision Ledger のみか、Durable Layer 4件か) | RB-02 / `DC_20260712_008` |
| **HG-RB-03** | 第3章 設計原則のうち [起案] 分 (P-09..P-12 / P-16 / P-17) の採否 | 第3章 |
| **HG-RB-04** | 第5章 コンポーネント責務 (JRB-1..JRB-5) および共通制約 C-1..C-9 の採否 | 第5章 |
| **HG-RB-05** | 第8章 接続点のうち write 可否表 (W-1..W-7) の採否 | 第8章 |
| **HG-RB-06** | 7.3 自己点検表の妥当性検証 (起草者の自己点検は検証の代替にならない) | 7.3 |
| **HG-RB-07** | `HAB_CORE_DEFINITION_v0.1.md` 同名2文書の正本の同定 | RB-03 |
| **HG-RB-08** | 本文書の Status を DRAFT から変更するか。Decision Ledger 登録の要否と分割単位 | 全体 |
| **HG-RB-09** | 本文書が DRAFT 文書 (Constitution Draft / HAB Core Definition) に依拠していることの可否。先行して下位文書の裁定を要するか | RB-12 / 0.5 |

---

## 10. 将来の実装候補 (参考情報のみ)

> **本章は参考情報である。**
> 本章のいかなる記載も、実装指示・着手許可・優先順位・期限・順序の決定を意味しない。
> **Migration Plan ではない。** 実装の着手は別 Decision を要する。

### 10.1 実装以前に確認を要する既知の事実 [継承 - `DC_20260807_001` impact]

以下は DP-1 が"Migration Plan を扱う別 Decision の入力"として記録した事実である。**本文書は対処を定めない。**

| # | 事実 |
|---|---|
| 1 | fold の実装は存在しない。`phi_os/event_replay.py` の `replay()` は `what_type` によるグループ化であり畳み込みではない |
| 2 | `_STATE_COLUMNS` のうち `change_type` / `impact_scope` / `impact_result` は標本200件で使用実績ゼロ。`before_state` は194件 (97.0%) が null |
| 3 | 標本は `claude_mcp` が181件 (90.5%) を占め、DB全体 19,360件 (25型) に対する代表性はない |
| 4 | `runtime/state.json` に互換性のない2つの書込元が存在する |
| 5 | `current_view` の永続先 `data/MOCKA_OVERVIEW_CURRENT.json` は生成されていない |
| 6 | Decision Ledger の現在有効な決定集合を機械的に導出する経路は現状存在しない (`superseded_by` が全203件 null、supersede 対象13件中11件が Active のまま) |
| 7 | `registry_store` (KN-004) の実体はリポジトリ外 |

**特に事実6は P-17 (Decision Ledger を唯一の制度判断ソースとする) に直接影響する。**
"現在有効な Decision の集合"を機械的に得る手段が存在しないため、
P-17 を実装上成立させる方法は現時点で確定していない。

### 10.2 実装候補として記録される事項 (選定・推奨・優先順位づけは行っていない)

| # | 候補 | 対応する未解決事項 | 状態 |
|---|---|---|---|
| I-1 | fold の実装 | RB-07 / `DC_20260807_001` impact 事実1 | **候補。`DC_20260807_001` impact により明示的に不許可 (実装着手は別 Decision)** |
| I-2 | Decision Transition Ledger の設置 | HG-H08 / `HAB_CORE_DEFINITION_v0.1.md` §5 | 候補。記録先は未裁定 |
| I-3 | Runtime beta 用 `what_type` の新設 | RB-06 / HG-J06 | 候補。既存値使用との比較は未実施 |
| I-4 | MCB allowlist の具体化 | RB-08 | 候補。粒度が未確定 |
| I-5 | 現在有効な Decision 集合の導出経路 | 10.1 事実6 | 候補。`superseded_by` の運用に関わるため既存 Decision への影響を要確認 |
| I-6 | `human_gate_bp` の到達可能化 | X-2 / HG-J04 | 候補。ただし Human Gate 5系統のどれを正本とするかが先行して未裁定 |

**上記はいずれも [起案] ですらなく、観測された選択肢の列挙である。**
本文書はどれを採るべきかを述べない。

### 10.3 本章が意図的に含めないもの

| 含めないもの | 理由 |
|---|---|
| 実装の順序・段階・期限 | Migration Plan に該当する。指示により禁止 |
| 各候補の工数・難易度の見積り | 一次資料が存在しない [Unknown] |
| 既存資産の移行方針 | Migration Plan に該当する |
| 推奨・優先順位 | 裁定の先取りに当たる |

---

## 11. 本文書の限界

1. 本文書は Architecture Definition であり、実装可能性を検証していない。
   特に RB-07 (fold 未実装) により、第6.1章 F-1 は現時点で実行可能ではない。
2. 本文書は `JARVIS_CONSTITUTION_DRAFT.md` および `HAB_CORE_DEFINITION_v0.1.md` に依拠しているが、
   両者は **DRAFT (未裁定)** である (0.5 / RB-12)。
3. DP-1 の成果物4文書はローカル `main` 作業ツリーに存在せず、
   ブランチ `claude/mocka-diff-state-comparison-5w2xt1` (Freeze Point `d7129bf`) を fetch して読解した。
   Decision Ledger の実データは MCP `mocka_decision_get` で `DC_20260807_001` を直接取得し確認済み。
4. 既存 Runtime の実測値は `JARVIS_ARCHITECTURE_CURRENT.md` / `JARVIS_RUNTIME_FLOW.md` (2026-08-04 時点) に依拠している。
   本工程では稼働プロセスの再実測を行っていない。**2026-08-04 以降の変化は反映されていない。**
5. 本文書は新規ファイルの作成のみである。既存ファイルの変更は行っていない。
6. **Decision Ledger 登録および Seal 生成は行っていない。**
7. 範囲限定の否定的所見 ("存在しない""発見できなかった") は、いずれも調査範囲を併記している。
   範囲外に存在しないことを意味しない。

---

## Knowledge Lineage

**Document:** JARVIS_RUNTIME_BETA_ARCHITECTURE_DRAFT_v0.1.md
**Status:** DRAFT (未裁定、Decision Ledger 未登録、Seal 未生成、実装なし)
**Created:** 2026-08-07
**Origin:** きむら博士指示"JARVIS Runtime beta の Architecture Definition を開始する。DP-1 を Freeze Point として前提条件とする"
**Freeze Point:** `DC_20260807_001` (DP-1 State Boundary Decision、Active) / commit `d7129bf303060470c43d1fc78eed3206eeba77a3`
**Parent Documents:**
- `docs/governance/DP1_STATE_BOUNDARY_DECISION_RECORD_DRAFT_v1.0.md` (DP-1: APPROVED)
- `docs/governance/DP1_STATE_BOUNDARY_CLOSURE_RECORD_v1.0.md` (DP-1 工程 CLOSED)
- `docs/governance/JARVIS_CONSTITUTION_DRAFT.md` (DRAFT、HG-J01..J09 未裁定)
- `docs/governance/HAB_CORE_DEFINITION_v0.1.md` (DRAFT、HG-H01..H10 未裁定)
- `docs/audits/JARVIS_ARCHITECTURE_CURRENT.md` / `JARVIS_RUNTIME_FLOW.md` / `JARVIS_BOUNDARY_ANALYSIS.md`
- `phi_os/hab/` (JARVIS_OPERATING_RULES_v0.1.md / jarvis_authority_boundary.md / AUTHORITY_POLICY_v0.1.md /
  HUMAN_GATE_CONTRACT_v0.1.md / actor_model.json / canonical_states.json / transition_ledger_schema.json ほか)
**Referenced Decisions:** `DC_20260807_001` (前提条件) / `DC_20260712_008` / `DC_20260705_008` / `DC_20260705_009` /
`DC_20260728_003` / `DC_20260729_001` / `DC_20260729_008` / `DC_20260729_009` / `DC_20260729_013` /
`DC_20260730_009` / `DC_20260731_003` / `DC_20260731_005` / `DC_20260713_003` / `DC_20260712_005` /
`DC_20260724_008` / `DC_20260801_002` / `DC_20260725_003`
**Supersedes:** なし (本文書はいかなる既存 Decision も supersede しない)
**Affected Components:** なし (コード・スキーマ・データ・プロセス構成のいずれも変更していない)
**Revision History:**
- R1 (2026-08-07): 新規作成。DP-1 (`DC_20260807_001`) を Freeze Point として前提条件に設定。
  JRB-0..JRB-5 の責務、設計原則 P-01..P-17、共通制約 C-1..C-9、データフロー F-1..F-4、
  MoCKA 接続点 R-1..R-4 / W-1..W-7 / X-1..X-5 を記載。
  [継承] [起案] [未裁定] [Unknown] [実測] を分離表記。
  未解決事項 RB-01..RB-12 を新規提起し、Human Gate 提示事項 HG-RB-01..HG-RB-09 を提示。
  実装・Decision Ledger 登録・Seal・Migration Plan・既存 Decision の変更は、いずれも行っていない。
