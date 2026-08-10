# JARVIS Runtime Beta Decision Package for Human Gate Review v0.1

## Human Authority が裁定可能な形に、State / Authority / Context / Runtime Acceptance の論点を整理する

**文書番号:** 未採番  
**作成日:** 2026-08-09  
**Status:** Human Gate Review 用の判断材料（裁定なし）  
**Decision Ledger 登録:** なし  
**Seal:** 未生成  
**実装:** なし  
**変更範囲:** 本文書の新規作成のみ。コード・Schema・Database・Ledger・既存ファイルは変更しない。

---

## 0. 位置付けと制約

### 0.1 本文書であるもの

Human Authority が JARVIS Runtime Beta の実装開始前に裁定すべき論点を、確認済みEvidence、未裁定事項、裁定の依存関係、および裁定後の実装境界として整理した Review 用文書である。

### 0.2 本文書でないもの

- Human Gate の裁定記録
- Decision Ledger の登録対象
- 実装承認、実装指示、Migration Plan
- 既存 Decision、DP-1、Human Gate の接続先の変更
- 未裁定事項の解決または推測による補完

### 0.3 固定前提

| ID | 固定前提 | Evidence |
|---|---|---|
| FP-01 | State は Event history の fold として導出され、独立に保持される第一級実体ではない | `DC_20260807_001` DP-1-A（Active） |
| FP-02 | Event Store (`data/mocka_events.db`) は State Layer の Primary Source である | `DC_20260807_001` DP-1-B（Active） |
| FP-03 | Human Gate は Authority Layer、State Management は Execution Layerに属する | `DC_20260807_001` DP-1-C（Active） |
| FP-04 | JARVIS は advisory であり、Human Authority は finalization を担う | `phi_os/hab/actor_model.json` / `jarvis_authority_boundary.md` |
| FP-05 | Architecture 承認は実装承認ではない。JARVIS 実装開始は未許可である | `JARVIS_RUNTIME_BETA_HUMAN_GATE_REVIEW_RECORD_v0.1.md` FC-03 / FC-12 |
| FP-06 | Evidence 不足または矛盾する事項は Unknown のまま保持する | 同 Review Record FC-04 / `DC_20260730_009` |

---

## 1. Decision 対象

### Package-01: State Boundary

| ID | Human Gate が裁定する対象 |
|---|---|
| S-01 | JARVIS Runtime Beta が説明対象とする State の範囲 |
| S-02 | Event history から導出する生成物（State / Snapshot / Delta）の定義 |
| S-03 | fold の責務主体、入力Eventの範囲、順序、決定性要件 |
| S-04 | Snapshot / Delta の正本・Derived View・保存可否・更新規則 |

### Package-02: Authority Boundary

| ID | Human Gate が裁定する対象 |
|---|---|
| A-01 | JARVIS が実行できる read、分析、提案、停止・報告の範囲 |
| A-02 | JARVIS が実行してはならない裁定、状態遷移、権限昇格、書込みの範囲 |
| A-03 | JARVIS が接続可能な唯一の Human Gate 実体 |
| A-04 | finalization の actor 本人性と認証・監査方法 |

### Package-03: Context Boundary

| ID | Human Gate が裁定する対象 |
|---|---|
| C-01 | JARVIS が読む Context の正本と Derived View の区別 |
| C-02 | 制度判断に用いる根拠ソースの範囲 |
| C-03 | Context 更新候補、更新権限、承認手順 |
| C-04 | 会話文脈を Event として扱うか、その粒度・保存期間・隔離規則 |
| C-05 | Evidence 不一致時の Unknown、停止、Human Gate 提示の規則 |

### Package-04: Runtime Acceptance

| ID | Human Gate が裁定する対象 |
|---|---|
| R-01 | JARVIS Runtime Beta の完成条件と受入基準 |
| R-02 | Unit / Integration / Authority / Replay / Regression の必須検証範囲 |
| R-03 | 受入に必要なEvidence trace と監査可能性の水準 |

---

## 2. 現在確認済み Evidence

### 2.1 State / Event

| Evidence | 確認済み事実 |
|---|---|
| `phi_os/event_gate.py` | Event の検証・記録を担う `process_event()` が存在する。 |
| `phi_os/event_replay.py` | `EventReplayer.replay()` は Event を `what_type` 別に集約する読み取り専用実装である。State を縮約する fold は実装していない。 |
| `DC_20260807_001` impact | fold 実装は存在せず、同 Decision は実装変更を直接許可しない。 |
| `phi_os/context/context_snapshot.py` | Context Snapshot は JSON を保存し、最新ファイルを上書きする。State Snapshot の正本としての位置付けは確認できない。 |

### 2.2 Authority / Human Gate

| Evidence | 確認済み事実 |
|---|---|
| `phi_os/hab/actor_model.json` | `jarvis.authority = advisory`、`jarvis.can_finalize = false`、`human.can_finalize = true`。 |
| `phi_os/human_gate.py` | `human_gate_events` から PENDING / APPROVED / REJECTED / EXPIRED / CANCELED を再構築する。HTTP Blueprint は定義されている。 |
| `app.py` | `gate_bp` は登録される。`human_gate_bp` の登録は本調査範囲で確認できない。一方、`/decision/approve` と `/decision/reject` は prevention queue を更新する。 |
| `semantic/query_engine/human_gate.py` | collision用 ruling をインメモリの append-only list に保持する。 |
| `JARVIS_HGJ04_EVIDENCE_M1_M2_M3_v0.1.md` | Human Gate 5系統は状態記録先と状態語彙がすべて異なる。 |

### 2.3 Context / Knowledge

| Evidence | 確認済み事実 |
|---|---|
| `phi_os/context/context_runtime.py` | Institution / Working / Memory / Execution の4層を統合する Context Runtime が存在する。更新・Snapshot保存のメソッドも持つ。 |
| `gateway/context_builder.py` | Overview、TODO、Essence、直近 Event を読み込み、Gateway用 Context を組み立てる。 |
| `gateway/adapter_gpt.py` | Gateway 経由で Context を読む Function Calling handler と Event 記録 handler が存在する。 |
| `mocka_mcp_server.py` | `mocka_search` は Event と Knowledge Gate を検索する。docs/governance の Markdown 本文を検索する処理は本調査範囲で確認できない。 |

### 2.4 接続境界 / テスト

| Evidence | 確認済み事実 |
|---|---|
| `JARVIS_RUNTIME_BETA_ARCHITECTURE_DRAFT_v0.1.md` | JRB-1〜JRB-5、read R-1〜R-4、write W-1〜W-7、禁止経路 X-1〜X-5 を設計として記載する。ただし Status は DRAFT。 |
| `phi_os/tests/test_event_gate.py` | Event Gate の入力検証・拒否・health を確認する。 |
| `phi_os/tests/test_human_gate.py` | HG-1 のイベントソーシング状態遷移を確認する。 |
| `phi_os/tests/test_hab_jarvis_boundary.py` | JARVIS が advisory で finalizer ではないことを確認する。 |
| `JARVIS_RUNTIME_BETA_HUMAN_GATE_REVIEW_RECORD_v0.1.md` | Architecture 承認は実装承認を含まず、JARVIS 実装開始を禁止することを記録する。 |

---

## 3. 未裁定事項

| ID | 未裁定事項 | 影響する Package |
|---|---|---|
| U-01 | fold の意味論、入力Event、State / Snapshot / Delta の定義 | Package-01 |
| U-02 | Execution Layer と Action Layer の関係（DP-1 A-1） | Package-01 / Package-02 |
| U-03 | JARVIS が接続する Human Gate の正本。5系統のいずれを接続対象にするか | Package-02 |
| U-04 | Human finalization の actor 本人性の確認方法 | Package-02 |
| U-05 | GPT Orchestrator と既存 `gateway/adapter_gpt.py` の責務関係 | Package-02 |
| U-06 | Decision Ledger のみを制度判断ソースとするか、Durable Layer 4件を含むか | Package-03 |
| U-07 | Context 正本、会話文脈の記録有無と粒度、更新権限 | Package-03 |
| U-08 | HAB Runtime の状態語彙、Event記録形式、MCB allowlist、TOLの層帰属 | Package-02 / Package-03 |
| U-09 | JARVIS Runtime Beta の受入基準・非機能要件・完了証跡 | Package-04 |
| U-10 | `JARVIS_CONSTITUTION_DRAFT.md` および `HAB_CORE_DEFINITION_v0.1.md` への依拠の可否 | 全Package |

**Unknown の扱い:** 本文書は上記を解決しない。Evidence が追加されるまで Unknown として保持する。

---

## 4. 推奨裁定順序

この順序は裁定結果の推奨ではなく、後続の論点が先行論点に依存する関係を整理したものである。

1. **Authority Boundary** — JARVIS の非権限、Human Gate 接続先、finalizationの本人性を確定する。  
2. **Context Boundary** — 読む正本、根拠範囲、Unknown・更新候補の扱いを確定する。  
3. **State Boundary** — Authority と根拠範囲を前提に、fold、Snapshot、Delta の意味論を確定する。  
4. **Runtime Acceptance** — 上記の裁定を受入基準、拒否条件、監査証跡、回帰検証へ変換する。  
5. **個別実装承認** — 各実装候補を、変更対象・非変更対象・検証・rollbackを含む別Packageとして Human Gate に提示する。

---

## 5. 承認後の実装境界

実装開始の許可ではない。Human Gate が実装を別途承認する場合に、その承認範囲に含めるべき境界である。

| 境界 | 承認後にも維持すべき制約 |
|---|---|
| Authority | JARVIS は最終裁定、Human Gate の迂回、権限昇格を行わない。 |
| Write | 未承認の Ledger、Schema、Database、TODO、Registry、Seal へ書き込まない。 |
| Event | Event記録が許可される場合も、既定の Gate 経路だけを通す。生SQL・既存Event変更は行わない。 |
| State | State は Event history から導出する。可変Stateを新たな正本にしない。 |
| Context | Contextの更新候補と正本変更を分離する。JARVIS の自動更新を設けない。 |
| Tool | MCB/TOL は Human Gate が裁定した allowlist 外の tool を呼び出さない。 |
| Evidence | 出力、提案、停止、拒否を元Evidenceへ追跡可能にする。根拠不足は Unknown とする。 |
| Safety | 自動承認・自動却下・直接遷移・HAB の意思化を作らない。 |

---

## 6. Reject した場合の影響

Reject は失敗を意味しない。該当する実装候補を開始せず、現行の境界と Unknown を維持する扱いである。

| 対象 | Reject した場合の影響 |
|---|---|
| Package-01 State Boundary | fold、Snapshot、Delta の実装候補は開始しない。JARVIS は DP-1 型のStateを説明可能とは扱わない。 |
| Package-02 Authority Boundary | JARVIS Runtime の Human Gate 接続・GPO/TOL/HABR 実装候補は開始しない。既存の分散Gateを統合対象として扱わない。 |
| Package-03 Context Boundary | JARVIS の正本Context、制度根拠、更新規則を固定しない。Evidence 不足のまま Context 自動更新や制度判断根拠の採用を行わない。 |
| Package-04 Runtime Acceptance | JARVIS Runtime Beta の完成宣言、実装受入、運用開始を行わない。既存コンポーネントの個別運用は本Packageでは変更しない。 |

---

## 7. Human Gate Review 確認票

| Package | 確認する事項 | 裁定結果欄 |
|---|---|---|
| Package-01 | State / fold / Snapshot / Delta の定義と境界 | Human Authority 記入 |
| Package-02 | JARVIS権限、禁止事項、Human Gate接続先、actor本人性 | Human Authority 記入 |
| Package-03 | Context正本、根拠範囲、更新規則、Unknown規則 | Human Authority 記入 |
| Package-04 | 完成条件、必須試験、Evidence trace、監査可能性 | Human Authority 記入 |

**裁定権限:** Human Authority のみ。  
**本書の裁定状態:** 未裁定。  
**実装状態:** 未着手。

---

## Knowledge Lineage

**Primary Evidence:**

- `data/decisions/decision_ledger.jsonl` の `DC_20260807_001`（Active）
- `docs/governance/JARVIS_RUNTIME_BETA_HUMAN_GATE_REVIEW_RECORD_v0.1.md`
- `docs/governance/JARVIS_RUNTIME_BETA_ARCHITECTURE_DRAFT_v0.1.md`（DRAFT）
- `docs/governance/JARVIS_HGJ04_EVIDENCE_M1_M2_M3_v0.1.md`
- `phi_os/{event_gate.py,event_replay.py,human_gate.py}`
- `phi_os/context/{context_runtime.py,context_snapshot.py}`
- `gateway/{gateway.py,context_builder.py,adapter_gpt.py}`
- `mocka_mcp_server.py`
- `phi_os/tests/{test_event_gate.py,test_human_gate.py,test_hab_jarvis_boundary.py}`

**未参照の推測:** なし。  
**Ledger操作:** なし。  
**コード・Schema・Database変更:** なし。
