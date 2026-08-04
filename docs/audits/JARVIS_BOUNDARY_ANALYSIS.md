# JARVIS Phase 0 — Boundary Analysis (Current State)

**Document:** JARVIS_BOUNDARY_ANALYSIS.md
**Status:** INVESTIGATION(現状記録のみ。設計・提案・改善案を含まない)
**調査日:** 2026-08-04
**実装変更:** なし

## 0. 本文書の限界(先に明示する)

責務分類は「どの文書が、その責務をどの層に割り当てているか」の記録である。
本文書は新たな境界を定めない。文書に割当の記載がないものは **Unknown** とする。
Unknown は「どちらでもよい」ではなく「未裁定」を意味する。

分類ラベルは調査指示の 5分類(`JARVIS` / `HAB` / `MoCKA` / `Shared` / `Unknown`)を用いる。

---

## 1. 用語 "HAB" の三義性 (Confirmed / 本調査の主要発見)

**リポジトリおよび構想文書内で "HAB" は少なくとも3つの異なる対象を指している。**
3者を相互に結びつける記述は、本調査の範囲(MoCKA repo 全文書 + `Desktop\aimd\`)では **発見できなかった**。

| # | 呼称 | 出典(一次) | 定義 |
|---|---|---|---|
| **HAB-A** | **Human Authority Boundary** | `docs/governance/mocka_hab_v1_contract.md`(Status: DRAFT, 2026-06-24) | 「どの層に、いつ、誰の判断で、どの強度で介入できるか」を制御する **MoCKA内部の統治層**。状態モデル `STABLE / DRAFT / REVIEW / STASIS / ACTIVE`、Authority Boundary Matrix(FROZEN/Analytical/index/meta-essence/Loop × 読取/追加/変更/削除)を定義 |
| **HAB-B** | **HAB spine**(Phase8 Runtime統合対象) | `docs/contracts/phase8_hab_runtime_integration_v1.md`(DRAFT, 2026-06-23) + `semantic/query_engine/execution_orchestrator.py` | Phase7 の A(Meaning Generation)〜E(Human Gate Interface)構造を「1つの動く単位」にする実行系。3層 = Runtime Bridge Layer / Execution Orchestrator / Observation Surface |
| **HAB-C** | **PHI-HAB** | `C:\Users\sirok\Desktop\aimd\ジャビス.md`(2026-08-04 09:33) | 「人間とAIが活動する環境」。構成要素 = Context Core / Context Compiler / Context Doctor / AI Adapter。責務 = Context管理・知識継承・AI作業状態管理・Context品質管理 |

**Confirmed な差異:**
- HAB-A は「状態定義(静的、what is)」であり、Human Gate(動的評価)とは一方向依存 `HAB -> Human Gate` である(`mocka_hab_human_gate_relation_v1.md` §2「HABはHuman Gateの入力になるが、Human GateはHABを変更しない」)。
- HAB-B はコードとして実在するが、`semantic/` パッケージ外部からの import は0件(Unwired)。
- HAB-C は実装コードが本調査の範囲で発見できなかった(Design Only)。

**Unknown:** HAB-A / HAB-B / HAB-C が同一概念の異なる段階なのか、同名の別概念なのかは、いずれの文書にも記載がない。

> **【R2 訂正 2026-08-04 — 「三義性」を「四義性」に改める】**
> 本節は3つの HAB を挙げたが、調査範囲に Decision Ledger 本文が含まれていなかった。
> Phase 1 で走査した結果、**4つ目かつ唯一 Active な Decision を持つ定義**が実在する。
>
> | # | 呼称 | 一次出典 | 定義 | 制度状態 |
> |---|---|---|---|---|
> | **HAB-D** | **PHI-HAB(制度)** | **`DC_20260729_008`**(`[DC-PHI-ID-001]`、approved 2026-07-29T01:44:27Z、きむら博士) | **PHI-REG-02(a) = Chrome拡張JSハブスタック(Connection/協調層)。実体は `PlanningCaliber/workshop/phi-os/extension/`, `core/`, `adapters/`** | **Active(Responsibility Classification Alias として採用済み)** |
>
> **重要:** HAB-C(`ジャビス.md` の「人間とAIが活動する環境」= Context Core/Compiler/Doctor/AI Adapter)と
> HAB-D(Chrome拡張の接続・協調層)は、**同じ "PHI-HAB" という語を使いながら指す対象が異なる**。
> HAB-D のみが Active な Decision に裏付けられており、HAB-C は Decision Ledger 未登録である。
> `ジャビス.md` の階層図 `JARVIS → PHI-HAB → Institutional Runtime` をどちらで読むかで設計が変わるため、
> これは未裁定事項として `docs/governance/JARVIS_CONSTITUTION_DRAFT.md` §7.1 / HG-J03 に提示した。

**調査ミッション本文の "HAB" の解釈:** ミッションが提示した流れ `Human → GPT → HAB → MoCKA → Ledger → Audit`
および分類軸 `JARVIS / HAB / MoCKA / Shared` は、`ジャビス.md` の階層図と一致するため
**HAB-C(PHI-HAB)を指す**と読める(**Hypothesis**、明示の定義文は未取得)。

---

## 2. 構想文書が定める層構造 (Confirmed / `ジャビス.md` より)

```
PHI-OS
├── PHI-Core   … 原則・状態・統治ルール
├── MoCKA      … 証拠・記録・判断保証
├── Orchestra  … 複数AI協調制御
├── PHI-HAB    … 人間とAIの活動環境
├── P-DERS     … 改善・進化循環
└── JARVIS     … 人間との知的インターフェース
```

責務の明示的記述(いずれも `ジャビス.md` 原文):

| 層 | 割り当てられた責務 |
|---|---|
| **JARVIS** | 「人間の意図をInstitutional AI環境へ接続するインターフェース」。「万能AIではない」と明記。意図理解・対話 |
| **PHI-HAB** | 人間とAIが活動する環境 / Context管理 / 知識継承 / AI作業状態管理 / Context品質管理 |
| **MoCKA** | Event Ledger / Decision Ledger / Audit / Human Gate / Evidence管理 |
| **P-DERS** | パターン検出 / 失敗分析 / 再発防止 / 制度改善(循環: Observe→Record→Incident→Recurrence→Prevention→Decision→Action→Audit) |
| **Orchestra** | Coordination(複数AI協調制御) |

別の一次文書 `PHI-OS_Concept_Memo.md`(2026-07-28)は同じ体系を異なる語彙で記述している(Confirmed):

| 層 | 役割 |
|---|---|
| PHI-OS | シーケンサー / 実行基盤 |
| MoCKA | Runtime Governance |
| Memory | Institutional Memory |
| Orchestra | マルチモジュール協調 |
| Relay | 情報伝達・状態同期 |

**Unknown:** この2文書の間で `PHI-HAB` と `Memory` が同じ層を指すのか、別層なのかは記載がない。
`P-DERS` は `PHI-OS_Concept_Memo.md` には登場しない。

MoCKA repo 側で確立済みの層責務(`docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` §5.1、Confirmed):

| コンポーネント | 問い |
|---|---|
| Sequence Controller | 「次に何をするか」 |
| MoCKA | 「それを許可できるか」「証拠はあるか」 |
| Memory | 「過去に何があったか」 |
| Orchestra | 「どのモデル・能力を使うか」 |
| Relay | 「外部状態を同期する」 |

---

## 3. 既存資産の責務分類

分類の根拠列は「どの文書がその割当を述べているか」を示す。根拠なしのものは Unknown。

### 3.1 MoCKA(証拠・記録・判断保証)

| 資産 | 状態 | 分類根拠 |
|---|---|---|
| `events` / `event_signatures` / `phi_os/event_gate.py` | Operational | `ジャビス.md` §6「Event Ledger」 |
| `data/decisions/decision_ledger.jsonl` / `mocka_decision_*` | Operational | `ジャビス.md` §6「Decision Ledger」 |
| `audit_violations` / `/audit/*` / `audit/` | Operational | `ジャビス.md` §6「Audit」 |
| `human_gate_events` / `phi_os/human_gate.py` / `/decision/approve` | 記録層 Operational / HTTP API Unwired | `ジャビス.md` §6「Human Gate」 |
| Evidence 紐付け(`related_events` / `related_documents`) | Operational | `ジャビス.md` §6「Evidence管理」 |
| GL7 `structural/execution_governance.py` | Operational(呼出元限定) | `PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` §4「Governance Check = MoCKA」 |
| `governance/mocka_git_safe_commit.py` | Operational | MoCKA内 write path 統治(コード自己宣言) |
| `mocka_mcp_server.py`(23 tools) | Operational | MoCKA の対外read/write面 |
| Integrity / Verification 群 | Operational | MoCKA「判断保証」 |
| HAB-A `mocka_hab_v1_contract.md` | Design(DRAFT) | 文書自身が「MoCKAにおける統治層」と明記 |

### 3.2 HAB(PHI-HAB / 活動環境・Context)

| 構成要素(`ジャビス.md` §4) | 現状の実装対応 | 状態 |
|---|---|---|
| **Context Core**(Mission / Architecture Principles / Decision Rules / Evidence Policy を常時保持) | 部分的に散在: `CONSTITUTION.md` `GOVERNANCE_BASELINE.md` `ARCHITECTURE.md` `data/MOCKA_OVERVIEW.json` `AI_BOOT_HUB.md` `AGENTS.md` / `interface/context_composer.py`(`context_bp` 登録済み) / `gateway/context_builder.py` / `/api/living-context` | **単一の Context Core としては未成立(Unknown)** |
| **Context Compiler**(自然言語 → 制度化情報。Human Gate を経て Official Context 化) | 該当実装を本調査範囲で **発見できず** | **Design Only** |
| **Context Doctor**(重複検出 / 古いルール検出 / Context削減 / 矛盾検出) | 部分的に近い資産: `semantic/query_engine/drift_monitor.py`(Unwired)、`cross_layer_consistency/`、`docs/reference/semantic_dictionary/`。ただし「Contextの健康管理」として定義された実装は **発見できず** | **Design Only** |
| **AI Adapter** | `gateway/adapter_{gpt,copilot,gemini,genspark,perplexity}.py`(Operational)、`workshop/phi-os/phios/adapter/`、`core_kernel/phios_integration/adapters.py`(Unwired) | **複数実体が並存(Shared / 帰属未裁定)** |
| HAB-B `semantic/query_engine/`(Phase8 HAB spine) | Implemented / Unwired | **HAB-C との関係 Unknown** |

### 3.3 JARVIS(意図理解・対話インターフェース)

| `ジャビス.md` §9 が定める Phase 0 の層 | 現状の実装対応 | 状態 |
|---|---|---|
| **Identity Layer**(GPTの役割定義: MoCKA/PHI-OS開発支援・設計監査・判断整理・リスク検出) | `gateway/adapter_gpt.py` は接続実装であって役割定義ではない。役割定義の実体を **発見できず** | **Missing** |
| **Context Core Layer**(Mission / Architecture / Principles / Current State / Decision Rules) | §3.2 と同様に散在 | **未成立** |
| **Knowledge Retrieval Layer**(`docs/{architecture,decisions,audits,history,experiments}` 参照) | `docs/audits/` `docs/governance/` `docs/contracts/` `docs/experimental/` 実在。`mocka_search` は events + knowledge_gate を検索するが **docs/ 本文は対象外**(`mocka_mcp_server.py:660-664` 実測) | **部分存在** |
| **Reflection Layer**(判断→評価→改善→次回反映) | `interface/reflection_engine.py`(`reflection_bp` 登録済み、Operational)。ただし JARVIS 用途としての帰属記載は **なし** | **Unknown(帰属未裁定)** |

**JARVIS に一意に帰属する実装は、本調査範囲(MoCKA repo 全体 + `Desktop\aimd\`)で0件である。**

### 3.4 Shared(複数層が同一資産を必要とする / 帰属未裁定)

| 資産 | 競合する帰属 |
|---|---|
| Context 生成系(`interface/context_composer.py` / `gateway/context_builder.py` / `/api/living-context`) | HAB(Context管理) vs MoCKA(状態提示) |
| AI Adapter 群 | HAB(AI Adapter) vs MoCKA(gateway) vs PHI-OS(`phios/adapter/`) |
| Memory | HAB(知識継承) vs `PHI-OS_Concept_Memo.md` の独立層「Memory」 vs MoCKA(`events` そのもの) |
| Search | JARVIS(Knowledge Retrieval) vs MoCKA(`mocka_search`) |
| Human Gate | MoCKA(§3.1)。ただし実装が4〜5系統に分散(`JARVIS_CAPABILITY_INVENTORY.md` §2.4) |
| Orchestra | 構想上は独立層。実装は `MoCKA/orchestra/` / `core_kernel/orchestra*` / `workshop/Orchestra_Project/` に3実体 |
| `core_kernel/`(133 .py) | `orchestra` `memory_core` `relay_core` `prism` `phios_integration` `governance` を内包し、**複数層にまたがる**。外部import 0件のため現時点でどの層にも接続していない |

### 3.5 Unknown(帰属を定める文書が見つからなかった資産)

| 資産 | 備考 |
|---|---|
| `runtime/`(218 .py、civilization_* 系) | 稼働状態・呼出元とも未確認 |
| `mocka_runtime_b.exe`(:5003, Go) | 層帰属の記載を発見できず |
| `mocka_caliber_server.py`(:5679) | 同上。`current_phase` に「Caliber検索品質改善」の記載あり |
| `living_room/hub.py`(:8765, dry_run) | 同上 |
| `archive/`(1,515 .py) | 退避領域。現行経路との関係未確認 |
| `structural/` `decision/` `learning_kernel/` `reality_sync/` `feedback/` `bridge/` `self_audit/` `read_layer/` | 層帰属の明示記載を発見できず |
| `:6379` memurai | 利用主体不明 |
| **P-DERS** | 構想文書に責務記載はあるが、MoCKA repo 内で `P-DERS` を実装として定義する文書・コードは **発見できず**。MoCKA内の言及は `docs/audits/INC_PIPELINE_FAILURE_ANALYSIS_v0.1.md` / `docs/governance/decision_identity/*` / `docs/mocka3/EVENT_FOUNDATION_v1.md` / 語彙辞書のみ(用語出現であり定義ではない) |

---

## 4. 既に裁定済みの境界(Confirmed / Decision Ledger・確定文書由来)

本調査で新たに定めたものではなく、既存の確定事項として実在するもの。

| 境界 | 出典 | 内容 |
|---|---|---|
| PHI-OS Core ↔ MoCKA Governance Runtime | `DC_20260728_003`(`PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`) | 別レイヤー。PHI-OS から MoCKA `phi_os/` パッケージへの直接 import を禁止 |
| PHI-OS → MoCKA の通信経路 | RC-011 `phios/phl/relay_client.py` | `http://localhost:5002/mcp` と `http://localhost:5000/api/gate/audit` のみ、read-only allowlist 強制(**コード実測で Confirmed**) |
| Adapter の権限 | `DC_20260729_013` D-02 | Adapter = Translation Boundary。意思決定生成・ポリシー変更・権限判断・Human Gate代替・証跡改変を禁止 |
| Authority Ownership | `DC_20260729_013` D-03 | PHI-OS = Runtime Coordination / Execution Control / Human Gate Routing、MoCKA = Evidence Management / Decision Evidence / Audit Intelligence / Governance Analysis、Human = Architecture Authority / Policy Change Approval / Irreversible Decision |
| Sequence Controller の権限 | `PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` §5 | 許可しない = 最終判断 / Authority変更 / Evidenceなし実行。実行可能 = 判断候補生成 / 必要Module呼出 / Gate要求 |
| HAB-A → Human Gate | `mocka_hab_human_gate_relation_v1.md` §2-3 | 一方向依存。遷移は HAB(状態) → Human Gate Core(評価) → Human Gate Finalization(裁定) → HAB状態更新 |
| main branch = Publish | 2026-07-14 Human Gate 運用方針(a) | main への commit は sync_watch により約10分以内に origin へ公開される |
| Core System File | `governance/mocka_git_safe_commit.py` | `phi_os/` `interface/` `structural/` `gateway/` + `app.py` `index.html` `scripts/ledger/anchor_update.py` `sync_watch.py` は自動commit対象外、人間承認待ち |

---

## 5. 本調査で観測した境界上の未解決点

いずれも観測事実の記録であり、解決案は本文書に含まない。

| # | 未解決点 | 観測根拠 |
|---|---|---|
| B-01 | "HAB" が3つの異なる対象を指す(HAB-A/B/C)。相互関係の記述なし | §1 |
| B-02 | `PHI-HAB`(`ジャビス.md`)と `Memory`(`PHI-OS_Concept_Memo.md`)の関係が未定義 | §2 |
| B-03 | Human Gate 実装が4〜5系統に分散。単一裁定点であるべきという宣言(`phi_os/human_gate.py` 冒頭、`execution_orchestrator.py` 冒頭)と実装状態が一致しているか未確認 | `JARVIS_CAPABILITY_INVENTORY.md` §2.4 |
| B-04 | Decision Ledger が3ストアに分散(`data/decisions/` / `data/ise/` / `workshop/phi-os/data/ise/`) | 実測 |
| B-05 | Orchestra が3実体、Adapter が3実体、Memory が4実体に分散し、どれが正本か未裁定 | §3.4 |
| B-06 | `core_kernel/`(133 .py)が複数層の責務を内包しつつ外部 import 0件 | 実測 |
| B-07 | P-DERS が構想にのみ存在し、MoCKA 側に対応物が見つからない(調査範囲: MoCKA repo + `Desktop\aimd\`) | §3.5 |
| B-08 | JARVIS に一意帰属する実装が0件 | §3.3 |

---

## Knowledge Lineage

**Document:** JARVIS_BOUNDARY_ANALYSIS.md
**Status:** INVESTIGATION
**Created:** 2026-08-04
**Origin:** JARVIS Phase 0 : Current State Assessment(Investigation 3: Boundary Analysis)
**Parent Documents:** JARVIS_ARCHITECTURE_CURRENT.md / JARVIS_CAPABILITY_INVENTORY.md
**Evidence Sources:** `C:\Users\sirok\Desktop\aimd\ジャビス.md`(2026-08-04)、
`C:\Users\sirok\Desktop\aimd\PHI-OS_Concept_Memo.md`(2026-07-28)、
`docs/governance/mocka_hab_v1_contract.md`、`docs/governance/mocka_hab_human_gate_relation_v1.md`、
`docs/contracts/phase8_hab_runtime_integration_v1.md`、`semantic/query_engine/execution_orchestrator.py`、
`docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`、`data/decisions/decision_ledger.jsonl`(`DC_20260729_001` / `DC_20260729_010`)、
`PlanningCaliber/workshop/phi-os/phios/phl/relay_client.py`
**Affected Components:** なし(調査のみ、変更なし)
**Revision History:**
- R1(2026-08-04): 新規作成。実装・Decision Ledger登録なし。
