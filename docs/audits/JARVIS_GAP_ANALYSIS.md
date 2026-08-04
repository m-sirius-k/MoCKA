# JARVIS Phase 0 — Gap Analysis (Current State)

**Document:** JARVIS_GAP_ANALYSIS.md
**Status:** INVESTIGATION(現状記録のみ。改善案・実装計画・優先順位付けを含まない)
**調査日:** 2026-08-04
**実装変更:** なし

## 0. 分類定義と本文書の限界

| ラベル | 本文書における厳密な定義 |
|---|---|
| **Already Exists** | 構想文書が求める要素に対応する実装が存在し、稼働経路上で動作していることを実測した |
| **Needs Refactoring** | 対応する実装は存在するが、構想文書の記述と観測状態の間に **本調査で確認できた具体的差分** がある。差分の内容のみを記載し、対処方法は記載しない |
| **Missing** | 対応する実装を **本調査の範囲で発見できなかった**。調査範囲を各項に明記する |
| **Unknown** | 実装の有無、または要件そのものが確定していないため判定できない |

**本文書の限界(重要):**
1. JARVIS の要件定義書・受入基準は本調査範囲に存在しない。判定の基準は
   `C:\Users\sirok\Desktop\aimd\ジャビス.md`(2026-08-04 09:33)に記述された構想であり、
   これは Decision Ledger に登録された確定要件ではない(§1 参照)。
2. したがって本文書の「不足」は **構想文書との差分の観測** であって、承認された要求仕様との差分ではない。
3. "Missing" はすべて調査範囲限定の否定的所見である。範囲外に存在する可能性を排除しない。

---

## 1. JARVIS 要件の出所と確定状態 (Confirmed)

### 1.1 一次資料

| 資料 | 日付 | 状態 |
|---|---|---|
| `C:\Users\sirok\Desktop\aimd\ジャビス.md` | 2026-08-04 09:33 | **構想メモ。Decision Ledger 未登録** |
| `C:\Users\sirok\Desktop\aimd\PHI-OS_Concept_Memo.md` | 2026-07-28 09:54 | 構想メモ |
| `docs/audits/PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1.md` §6 | 2026-07-29 | ジャービス化ロードマップ J1〜J5 |
| `docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` §6 | 2026-07-29 | "Future Jarvis Runtime(参考、本文書では未着手)" |
| `docs/audits/PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md` §6 | 2026-07-29 | "Jarvis Runtime Connection(参考、本文書では未着手)" |

### 1.2 Decision Ledger 上の JARVIS 言及(全件 / 206行を走査、Confirmed)

| Decision | status | 言及内容 |
|---|---|---|
| `DC_20260729_001` | Active | 「きむら博士より提示されたPHI-OS構想メモ(Sequence Controller/JARVIS構想、**原本はローカルDesktopのためこのセッションからは未検証**)」を Deferred(将来のPHI-OS全体再設計時に再評価)と裁定 |
| `DC_20260729_010` | Active | 「ジャービス化ロードマップの新Runtime設計へ接続できること」を Option B 選択理由の一つとして記録。「本Decision確定後、フェーズは『監査基盤整備』から『Runtime入口再設計』へ移行する。次工程は PHI Memory Architecture Design Scope(ジャービス化ロードマップPhase J1)」 |

→ **JARVIS そのものを承認・確定した Decision は存在しない**(206行走査の範囲で Confirmed)。
`DC_20260729_001` が参照する「原本」は本調査で所在を特定した(`Desktop\aimd\ジャビス.md`)。

### 1.3 ジャービス化ロードマップ J1〜J5 の進捗 (Confirmed)

```
J1: PHI Memory Architecture      -> 設計文書 PHI_MEMORY_ARCHITECTURE_v1.0.md 作成済み
J2: PHI Sequence Controller Design -> PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md 作成済み
                                      (Status: DESIGN、「Decision Ledger登録・実装はまだ行わない」と明記)
J3: Orchestra統合                 -> 未着手(着手を示す文書を発見できず)
J4: Personal Context Engine       -> 未着手(同上)
J5: Embodied Interface            -> 未着手(同上)
```

`PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md` §7 は Phase J5(Assistant Runtime)対象として
以下を **現時点のスコープ外** と明記している(Confirmed):
自律Agent権限 / 音声UI / 常駐プロセス / 外部デバイス制御 / 完全自動実行。

---

## 2. Gap 一覧 — JARVIS Phase 0 の4層(`ジャビス.md` §9)

`ジャビス.md` §9 は JARVIS Phase 0 の最初の目標を
「GPT能力を最大限引き出す専用環境を作る」とし、4層を挙げている。

### G-01 Identity Layer — **Missing**

- 構想の記述: GPTの役割定義(MoCKA/PHI-OS開発支援・設計監査・判断整理・リスク検出)。
- 観測: `gateway/adapter_gpt.py` は **接続アダプタ** であり、役割定義ではない。
  `gateway/context_builder.py` の内容は本調査で未読。
  役割・責務を宣言する設定/データを、MoCKA repo 全体 grep および `Desktop\aimd\` の範囲で **発見できなかった**。
- 近接資産(存在は Confirmed、帰属は未裁定): `AGENTS.md`, `AI_BOOT_HUB.md`, `PROGRAMS.md`,
  `interface/ai_capability_registry.py`, `core_kernel/core_store/capability_registry.py`(Unwired)。
- 判定: **Missing**(調査範囲: MoCKA repo 全ファイル + `Desktop\aimd\`)

### G-02 Context Core Layer — **Needs Refactoring**

- 構想の記述: 必要最小限の常時コンテキスト = Mission / Architecture / Principles / Current State / Decision Rules。
- 観測(いずれも存在は Confirmed):
  | 構想の項目 | 現存資産 | 観測された差分 |
  |---|---|---|
  | Mission | `CONSTITUTION.md`, `README.md`, `PHI_OS_CONSTITUTION_v1.md` | 複数文書に分散 |
  | Architecture | `ARCHITECTURE.md`(**40行のみ**、INFIELD/OUTFIELD/Observer/Transparency の概要)、`ARCHITECTURE_REGISTRY.json`、`MOCKA_FULL_ECOSYSTEM_UNDERSTANDING.md`(481行) | 稼働中の7プロセス構成(`JARVIS_ARCHITECTURE_CURRENT.md` §2)は `ARCHITECTURE.md` に記載されていない |
  | Principles | `GOVERNANCE_BASELINE.md`, `UTF8_MANDATE.md`, `QUALITY_GATE.md`, `CANONICAL_AUTHORITY_EVALUATION_RULE_v0.1.md` ほか | 分散 |
  | Current State | `data/MOCKA_OVERVIEW.json`, `data/MOCKA_TODO.json`(`current_phase`), `/api/living-context`(app.py:2422) | `MOCKA_TODO.json` の `meta.updated` は **2026-07-29**、`_snapshot_at` は **2026-08-04**(更新主体が異なる) |
  | Decision Rules | `data/decisions/decision_ledger.jsonl`(206件), `DECISION_LAYER.md` | 3ストアに分散(`JARVIS_BOUNDARY_ANALYSIS.md` B-04)、最新レコードに文字化けが実在 |
- 差分の要点(観測事実のみ): 5項目すべてに対応資産が存在するが、**単一の「常時保持されるContext Core」として集約された実体は存在しない**。
- 判定: **Needs Refactoring**

### G-03 Knowledge Retrieval Layer — **Needs Refactoring**

- 構想の記述: 詳細情報は外部参照。`docs/{architecture, decisions, audits, history, experiments}`。
- 観測:
  - 実在するディレクトリ(Confirmed): `docs/audits/` `docs/governance/` `docs/contracts/` `docs/experimental/` `docs/mocka3/` `docs/reference/` `docs/internal/` `docs/images/`。
  - 構想が挙げた `docs/architecture/` `docs/decisions/` `docs/history/` は **本調査では未確認**(`docs/` 直下の全走査は未実施 = Unknown)。
  - 検索能力の差分(Confirmed): `mocka_search` は `search_events()` + `search_knowledge_gate()` の2ソースのみを対象とし、**`docs/` 配下のMarkdown本文は検索対象に含まれない**(`mocka_mcp_server.py:660-664` 実測)。
- 判定: **Needs Refactoring**(文書群は存在するが、MCP経由の検索到達性に差分がある)

### G-04 Reflection Layer — **Unknown**

- 構想の記述: 判断 → 評価 → 改善 → 次回反映。
- 観測: `interface/reflection_engine.py` が実在し `reflection_bp` として `app.py` に **登録済み**(Operational)。
  ほかに `feedback/`(11 .py)、`learning_kernel/`(12 .py)、`FEEDBACK_LOOP.md`、`LEARNING_KERNEL.md`、
  `self_audit/`(10 .py)、`SELF_AUDIT_LAYER.md`。
- 未確認: これらが構想の Reflection Layer に対応するものとして設計されたかを示す記述を発見できなかった。
  各モジュールの実際の挙動も本調査では未検証。
- 判定: **Unknown**(実装は存在するが、要件との対応関係が未裁定)

---

## 3. Gap 一覧 — PHI-HAB 構成要素(`ジャビス.md` §4-5)

### G-05 Context Core(PHI-HAB) — G-02 と同一 → **Needs Refactoring**

### G-06 Context Compiler — **Missing**

- 構想の記述(フロー): `Human Thought → AI Analysis → Principle Extraction → Context Update Candidate → Human Gate → Official Context`。
- 観測: フロー全体に対応する実装を発見できなかった。
- 部分的に対応しうる既存資産(存在は Confirmed、ただし本用途への割当記載なし):
  - `Human Gate` 部分: `phi_os/human_gate.py`(**Blueprint 未登録 = HTTP到達不能**)、`/decision/approve`
  - `Principle Extraction` 近接: `interface/essence_extractor.py` / `essence_condenser.py` / `essence_classifier.py`
  - `Official Context` 近接: `data/lever_essence.json`(sync_watch allowlist、公開対象)
- 判定: **Missing**(調査範囲: MoCKA repo 全ファイル + `Desktop\aimd\`)

### G-07 Context Doctor — **Missing**

- 構想の記述: 重複検出 / 古いルール検出 / 不要なContext削減 / 矛盾検出。
- 観測: 「Contextの健康管理」として定義された実装を発見できなかった。
- 近接資産(存在は Confirmed、Contextではなく別対象を扱う):
  - `semantic/query_engine/drift_monitor.py` / `drift_recorder.py` — **Unwired**
  - `semantic/query_engine/collision_governance.py` / `order_normalizer.py`(identifier衝突検出)— **Unwired**
  - `cross_layer_consistency/`(13 .py)、`docs/reference/semantic_dictionary/`
  - `audit_violations`(22,539行、うち `NEW` 6)
- 判定: **Missing**

### G-08 AI Adapter — **Needs Refactoring**

- 観測: 3実体が並存(いずれも存在 Confirmed):
  | 実体 | 状態 |
  |---|---|
  | `gateway/adapter_{gpt,copilot,gemini,genspark,perplexity}.py` | Operational(:5010、`X-MoCKA-Key` 必須) |
  | `PlanningCaliber/workshop/phi-os/phios/adapter/` + repo root `adapter/` | 別repo。`DC_20260729_013` により責務定義済み |
  | `core_kernel/phios_integration/adapters.py` | **外部import 0件 = Unwired** |
- 差分: どれが正本かを定める記述を発見できなかった。
- 判定: **Needs Refactoring**

---

## 4. Gap 一覧 — Institutional Runtime 構成層

### G-09 MoCKA(Event Ledger / Decision Ledger / Audit / Human Gate / Evidence) — **Already Exists**(一部 Needs Refactoring)

| 構想の要素 | 判定 | 根拠 |
|---|---|---|
| Event Ledger | **Already Exists** | `events` 19,037行、最新 2026-08-04T05:16:21Z、5W1H スキーマ、ハッシュ連鎖テーブル併存 |
| Decision Ledger | **Already Exists**(記録機能) / **Needs Refactoring**(データ品質・分散) | 206行 Operational。ただし最新レコードに文字化け実在、3ストアに分散 |
| Audit | **Already Exists** | `audit_violations` 22,539行、`/audit/*`、`audit/` 32 .py |
| Human Gate | **Needs Refactoring** | 記録層(`human_gate_events` 1,779行)は稼働。**`human_gate_bp` が `app.py` に未登録で HTTP API 到達不能**。実装が4〜5系統に分散 |
| Evidence管理 | **Already Exists** | `related_events` / `related_documents` による紐付けが実データで確認できる |

### G-10 Orchestra 統合(ロードマップ J3) — **Unknown**

- `current_phase` は「Orchestra稼働中」と記載(`data/MOCKA_TODO.json`)。
- 実体が3つ存在(`MoCKA/orchestra/` / `core_kernel/orchestra*` / `workshop/Orchestra_Project/`)し、
  そのうち `core_kernel/orchestra*` は外部import 0件、`MoCKA/orchestra/` は `architecture_verify.py` と
  `bridge/tests/` からのみ参照(app.py 未参照)。
- **どれが「稼働中」なのかを本調査で同定できなかった。**
- 判定: **Unknown**

### G-11 P-DERS — **Missing**

- 構想の記述: 循環 `Observe → Record → Incident → Recurrence → Prevention → Decision → Action → Audit`。
- 観測: 循環の各段に対応しうる資産は個別に存在する(Confirmed):
  | 段 | 既存資産 |
  |---|---|
  | Observe | `core_kernel/prism/observation_engine.py`(Unwired)、`semantic/query_engine/observation_surface.py`(Unwired)、`observer_logger.py` |
  | Record | `events`(Operational) |
  | Incident | `mocka_get_incidents`(Operational)、`docs/audits/INC_*` |
  | Recurrence | `events.recurrence_flag` カラム実在、`pattern_engine.py` / `interface/pattern_engine_v2.py`、`/pattern/status` `/success/patterns` |
  | Prevention | `/prevention/generate` `/prevention/queue`(app.py:2285, 2354)、`phi_os/migrate_prevention_queue.py` |
  | Decision | `decision_ledger.jsonl`(Operational) |
  | Action | `runtime/action_executor.py` `action_selector.py` `action_mapper.py` |
  | Audit | `audit_violations`(Operational) |
- しかし **これらを P-DERS として統合・定義する文書またはコードを発見できなかった**
  (調査範囲: MoCKA repo の `*.md` / `*.py` 全体に対する `P-DERS|PDERS` grep。ヒットは用語出現4文書と語彙辞書のみで、定義文書ではない)。
- 判定: **Missing**(構成部品は存在、統合体としては不在)

> **【R2 訂正 2026-08-04 — 上記 Missing 判定を取り消す】**
> 上記の調査範囲は `*.md` / `*.py` に限定されており、**Decision Ledger(`.jsonl`)を含んでいなかった**。
> Phase 1 で Decision Ledger 206行を走査した結果、以下が実在することを Confirmed した。
>
> | Decision | 内容 |
> |---|---|
> | `DC_20260730_001`(p-DERS 版) | p-DERS 形式理論トラック(Track A)— Causal Projection 選定〜Compositional Safety Theorem 部分証明の成果確定 |
> | `DC_20260730_002`(p-DERS 版) | Sound Local Approximation の証明と「第3の軸」への位置づけ確定 |
> | `DC_20260730_003`(p-DERS 版) | MoCKA Governance Function G の実態調査 — Track A 理論との関係 |
> | `DC_20260730_009` | `pDERS_causal_projection_v0.1.md` / `pDERS_overlap_consistency_v0.1.md` / R_i/Ω_i/Ψ_i 三分割構造 / Local Invariant Gate / Zenodo アーカイブ / Rust プロトタイプ の6件を **「未検証文脈(Unverified Context)」として隔離**し継続対象としないと裁定 |
>
> **訂正後の判定: Missing ではない。** P-DERS は形式理論トラック(Track A)として Active な Decision を持ち、
> かつ一部の前提資料は `DC_20260730_009` により明示的に隔離済みである。
> なお `DC_20260730_001/002/003` は PHI-OS Milestone 系と p-DERS 系で **同一 ID が重複**しており、
> `DC_20260801_002` の P-1「同一 Decision ID の複数行は原則異常」に該当する(観測のみ。HG-1 により自動修復は行わない)。
> 詳細: `docs/governance/JARVIS_CONSTITUTION_DRAFT.md` §7.3

### G-12 Sequence Controller(ロードマップ J2) — **Needs Refactoring**

- 設計文書は存在(`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`、Status: DESIGN)。
- 同文書 §3 が定める9段階と既存実装の対応(**文書自身の記述、Confirmed**):
  ```
  Observation → Classification → Context Retrieval → Verification →
  Planning → Human Gate → Execution → Audit → Memory Update
  ```
  - 部分実装あり: `Observation` / `Classification` / `Planning` / `Execution`
    (`phios/core/orchestrator.py` の `InterpretedEvent → DecisionSynthesizer → SemanticRouter → Executor`)
  - **新規に接続する対象**と文書が明記: `Context Retrieval` / `Verification` / `Human Gate` / `Audit` / `Memory Update`
  - `semantic_router.py` は「文字列ターゲットを返すのみで未接続」と文書に明記
- 判定: **Needs Refactoring**(設計・部分実装は存在、9段階のうち5段が未接続と文書自身が記載)

### G-13 Memory Architecture(ロードマップ J1) — **Needs Refactoring**

- 設計文書は存在(`PHI_MEMORY_ARCHITECTURE_v1.0.md` ほか3文書)。
- 既存記録(**Hypothesis**、本調査で未再検証)による観測:
  `phios/runtime/memory_boundary.py` はテスト以外からの参照ゼロ件 = 完全未配線。
  Access Control Policy の State→Memory Permission Mapping はコードでの強制ゼロ件。
- 本調査で Confirmed した関連事実: `core_kernel/memory_core/` は外部import 0件。
- 判定: **Needs Refactoring**

---

## 5. 設計変更なしで再利用できる資産(Already Exists / Operational)

以下は稼働経路上で動作していることを本調査で実測した資産である。

| 資産 | 実測根拠 |
|---|---|
| Event Recording(`events` + `phi_os/event_gate.py` + `mocka_write_event`) | 19,037行、最新 2026-08-04T05:16:21Z |
| Event 入力バリデーション(title/description/author 必須、空なら `gate_rejected`) | `mocka_mcp_server.py:666-683` |
| 冪等制御(`gate_idempotency`) | 2,615行 |
| Decision Ledger 記録・参照(`mocka_decision_write/get/list`) | 206行、`DC_20260801_002` |
| Audit 違反検出(`audit_violations`) | 22,539行 |
| Integrity(`integrity_bp` 登録済み、`mocka_integrity_*`) | app.py:81 |
| MCP 面 23 tools + `/agent/<tool>` 直接HTTP | port 5002 実測 |
| Git Write Governance(`mocka_git_safe_commit.py`、Core System File 除外) | コード実測 + 未コミット4件の実在 |
| Publish 同期(`sync_watch.py`、600秒、allowlist 4ファイル) | git log の `auto sync` 連続commit |
| 外部AI Gateway(:5010、`X-MoCKA-Key`、adapters 5種) | 401応答 + ファイル実在 |
| PHI-OS → MoCKA read-only 経路(RC-011 `relay_client.py`) | コード実測(allowlist 強制) |
| Human Gate 記録層(`human_gate_events`) | 1,779行、最新 2026-07-31 |
| Encoding Guard(`mocka_check_utf8`、全プロセス `-X utf8`) | プロセス実測 |

---

## 6. Gap サマリ表

| # | 対象 | 分類 |
|---|---|---|
| G-01 | JARVIS Identity Layer | **Missing** |
| G-02 | Context Core Layer | **Needs Refactoring** |
| G-03 | Knowledge Retrieval Layer | **Needs Refactoring** |
| G-04 | Reflection Layer | **Unknown** |
| G-05 | PHI-HAB Context Core | **Needs Refactoring**(G-02と同一) |
| G-06 | PHI-HAB Context Compiler | **Missing** |
| G-07 | PHI-HAB Context Doctor | **Missing** |
| G-08 | PHI-HAB AI Adapter | **Needs Refactoring** |
| G-09 | MoCKA(Ledger/Audit/Evidence) | **Already Exists** |
| G-09b | MoCKA Human Gate | **Needs Refactoring** |
| G-10 | Orchestra 統合(J3) | **Unknown** |
| G-11 | P-DERS | **Missing** |
| G-12 | Sequence Controller(J2) | **Needs Refactoring** |
| G-13 | Memory Architecture(J1) | **Needs Refactoring** |

**要件そのものの Unknown(最上位):**
JARVIS の受入基準・完了条件・非機能要件を定めた文書は本調査範囲に存在しない。
`ジャビス.md` は Decision Ledger 未登録の構想メモであり、`DC_20260729_001` は
その扱いを **Deferred(将来のPHI-OS全体再設計時に再評価)** と裁定している。

---

## Knowledge Lineage

**Document:** JARVIS_GAP_ANALYSIS.md
**Status:** INVESTIGATION
**Created:** 2026-08-04
**Origin:** JARVIS Phase 0 : Current State Assessment(Investigation 4: Missing Components)
**Parent Documents:** JARVIS_ARCHITECTURE_CURRENT.md / JARVIS_CAPABILITY_INVENTORY.md / JARVIS_BOUNDARY_ANALYSIS.md
**Evidence Sources:** `C:\Users\sirok\Desktop\aimd\ジャビス.md`、`data/decisions/decision_ledger.jsonl`(206行走査)、
`docs/audits/PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1.md`、`docs/audits/PHI_SEQUENCE_CONTROLLER_{ARCHITECTURE_v1.0,DESIGN_SCOPE_v0.1}.md`、
`docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md`、`mocka_mcp_server.py`、`app.py`、`phi_os/human_gate.py`、
稼働プロセス実測、`data/mocka_events.db` 実測
**Affected Components:** なし(調査のみ、変更なし)
**Revision History:**
- R1(2026-08-04): 新規作成。実装・Decision Ledger登録なし。
