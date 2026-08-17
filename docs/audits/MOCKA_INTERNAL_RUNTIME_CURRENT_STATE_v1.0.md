# MoCKA Internal Runtime — Current State Report v1.0

Status: INVESTIGATION REPORT (READ-ONLY)
作成日: 2026-08-17
対応 CHANGE_START: E20260817_496729438ded2
指示: きむら博士 — 内部リポジトリ調査 / 公開Web調査の二系統照合

---

## 0. 実行環境と証拠の性質

本報告書の一次証拠は2種類あり、性質が異なるため分離して記載する。

- 証拠種別 A (repo実測): Claude Code Web 隔離コンテナ上の main クローン (HEAD = da4d4db) に対する
  静的解析・grep・pytest 実行結果。Windowsホスト C:/Users/sirok/MoCKA ではない。
- 証拠種別 B (runtime実測): MCP サーバー mocka_MCP 経由で本番Runtimeから取得した実データ。
  本セッションで localhost:5002 (MCP) と localhost:5000 (COMMAND CENTER) の応答を実測。

重要な前提: 本クローンには data/ 配下の実体が存在しない (.gitignore の `data/*` により
Cloudflare同期用の8ファイル以外は全除外)。したがって repo実測だけでは Ledger 系の中身は
検証できない。この制約自体が本報告書の主要な発見の一つである (第4章)。

runtime実測で確認した稼働証拠:
- events 総件数: 20,608 / 最新イベント: 2026-08-17T02:51:03Z
- Decision Ledger: 240件 / 最新 DC_20260816_001 (approved_at 2026-08-16T07:38:08Z)
- essence 更新: 2026-08-16T22:42:52Z
- 最終 seal: 2026-07-07T11:03:41Z (hash 37b603b8b0d5782b)

---

## 1. 結論サマリ — 9軸マトリクス

凡例: OK=成立 / NO=不成立 / PART=部分的 / N/A=対象外
接続 = リポジトリ内で他モジュールからimportされているか
Runtime到達性 = app.py (5000) または mocka_mcp_server.py (5002) の実行経路から到達するか

| # | Component | 存在 | 実装 | 接続 | Runtime到達性 | テスト | 検証 | 承認 | Active |
|---|-----------|------|------|------|---------------|--------|------|------|--------|
| 1 | MoCKA本体 (app.py/MCP) | OK | OK | OK | OK | PART | OK | OK | ACTIVE |
| 2 | Event Ledger | OK | OK | OK | OK | OK | OK | OK | ACTIVE |
| 3 | Decision Ledger | OK | OK | OK | OK | NO(repo) | PART | OK | ACTIVE |
| 4 | Human Gate | OK | OK | PART | PART | OK | OK | OK | PART |
| 5 | PHI-OS | OK | OK | OK | OK | OK | OK | OK | ACTIVE |
| 6 | Context Runtime | OK | OK | OK | OK | OK | OK | PART | ACTIVE |
| 7 | Relay | OK | OK | OK | OK | NO | PART | PART | PART |
| 8 | Memory | OK | OK | NO | NO | OK(自己) | OK(自己) | NO | INACTIVE |
| 9 | Orchestra (制度側) | OK | OK | PART | NO | OK | OK | PART | INACTIVE |
| 10 | HAB | OK(文書) | NO | NO | NO | PART | PART | OK(Freeze) | DESIGN |
| 11 | JARVIS | OK | PART | NO | NO | OK | PART | PART(Arch) | DESIGN |
| 12 | Gateway / GPT | OK | OK | OK | PART | NO | NO | PART | DORMANT |
| 13 | core_kernel / semantic | OK | OK | NO | NO | PART | NO | NO | UNWIRED |

要点を1行で言うと: MoCKA は"動いている制度カーネル(1-6)""片足だけ動いている伝送層(7)"
"実装済みだが配線されていない能力群(8,9,13)""設計だけ確定している権限層(10,11)"
"起動対象だがほぼ使われていない外部接続層(12)"の5階層で構成されている。

---

## 2. コンポーネント別 詳細

### 2.1 MoCKA本体 (COMMAND CENTER + MCP Server)

- 存在/実装: app.py 4,194行 / mocka_mcp_server.py 1,471行 (repo実測)
- 接続: app.py が 11個の Blueprint を登録 (app.py:72-82)
  ai_session / handshake / dashboard / reflection / prediction / mentor / commission /
  context / gate (phi_os.event_gate) / integrity (phi_os.integrity_routes) / time_api (phi_os.api)
- Runtime到達性: 本セッションから MCP ツール呼び出しが成功。mocka_get_command_center が
  localhost:5000 の loop_status / risk / heinrich を返した = 両サーバーが同時稼働中
- MCPエンドポイント: /mcp 本番 + /mcp-test /mcp-core-test /mcp-memory-test
  /mcp-governance-test /mcp-admin-test の5分割テスト面 (mocka_mcp_server.py:1126-1327)
- Active: ACTIVE
- 停止点 (最上位リスク): TODO_437 /agent/mocka_write_event 応答遅延(実測約5秒)と
  timeout=3 の不一致。risk_score 0.55 / HIGH / 優先度=最高 / status=進行中

### 2.2 Event Ledger

- 実装: phi_os/event_gate.py に単一書込点 `_write()` (:46) と `process_event()` (:115)
- 接続/到達性: app.py:80 で gate_bp 登録済み。mocka_mcp_server.py:277 および :725 で
  process_event を直接呼出。書込は Gate 経由に一本化されている
- 実データ: 20,608件 (runtime実測)。type分布上位は claude_mcp 9,138 / user_voice 7,376 /
  conversation_message 1,796
- 検証: Heinrich比 実測 1:6.5:54.8 (理論 1:29:300)、capture_rate layer2=22.4% layer3=18.3%
- 公開性: repo上の mocka_events.db は **0バイト** (プレースホルダのみ)。実体は非公開
- 停止点: 最終 seal が 2026-07-07T11:03:41Z。以降約40日分が未 seal 状態
  (anchor_type=manual_external_post)

### 2.3 Decision Ledger

- 実データ: 240件 / 最新 DC_20260816_001 (runtime実測、MCP経由)
- 実装: mocka_decision_write / mocka_decision_get / mocka_decision_list が
  本セッションのツール一覧に存在 (MCP Tool Registry Drift は本セッションでは発生せず)
- 正本パス: data/decisions/decision_ledger.jsonl
- 分散状況 (repo実測): 参照点が複数存在する
  - governance/seal_governance_gate.py:39 — DECISION_LEDGER_PATH 定義、:148 で追記(append)
  - governance/seal_governance_wrapper.py:72 — sandbox ledger へ分岐
  - governance/write_path/runtime/adapter.py:19 — read-only 参照 (書込禁止を明記)
  - governance/human_gate_continuity.py:30 — Pending Decision Unit の永続化先として参照
- **公開リポジトリ上には実体が存在しない** (.gitignore `data/*`)
- 停止点:
  - MCP-TOOL-REGISTRY-DRIFT-DECISION-WRITE-PATH (未着手/高): DC_20260705_006 の Ledger正式反映が未完
  - TODO_423 (保留/中): Decision Ledger 文字化け原因追跡
  - TODO_W2 (未着手/中): reverse traceability model design

### 2.4 Human Gate

repo上に5系統の実装が併存する (repo実測)。

| 実装 | 経路 | 到達性 |
|------|------|--------|
| phi_os/human_gate.py (11,916 bytes) | Flask Blueprint 5ルート | **HTTP到達不能** |
| governance/human_gate_cli.py (5,353 bytes) | CLI (TTY限定) | 到達可能 |
| governance/human_gate_continuity.py (9,290 bytes) | 状態遷移ガード | 到達可能 |
| runtime/jarvis/gate/human_gate.py (682 bytes) | JARVIS内部 | JARVIS未配線のため不達 |
| semantic/query_engine/human_gate.py | semantic層 | semantic未配線のため不達 |

- 独立再検証結果: `human_gate_bp` は phi_os/human_gate.py:18 で定義され
  /api/human_gate/submit, /approve, /reject, /status/<id>, /pending の5ルートを持つが、
  app.py の register_blueprint 11件のいずれにも含まれていない。
  したがって **Human Gate の HTTP API は現在到達不能** である。
  これは JARVIS Phase 0 調査 (JARVIS_CAPABILITY_INVENTORY.md) の指摘を本セッションで
  独立に再現したものである。
- ただし同調査の R2 精緻化どおり、モジュール本体は CLI 経路で稼働実績がある
  (HG20260731_* の submit/approve が DC_20260731_007 に対応)。未配線なのは HTTP面のみ。
- テスト: phi_os/tests/test_human_gate.py 通過 (本セッション実行)
- 停止点: TODO_429 (制度整理/未着手), TODO_397 (命名衝突リネーム検討/未着手),
  TODO_441 (執行官自己承認の正規性判定/status=要判定), TODO_444 (保留/高)

### 2.5 PHI-OS

- 存在/実装: phi_os/ 配下に event_gate / human_gate / integrity / gate_validator /
  gate_schema / event_replay / event_bus / dictionary / reference_resolver /
  process_manager / audit_trigger / phi_bridge_governance + サブパッケージ
  api / context / hab / runtime / semantic / tests
- 接続/到達性: app.py に gate_bp / integrity_bp / time_api_bp の3系統が登録済み = ACTIVE
- phi_os/runtime/ には authority_manager / binding_engine / compliance_engine /
  gate_registry / institution_registry / institution_runtime / meaning_registry /
  production_bridge / production_observation が存在
- テスト (本セッション実測): `python -m pytest phi_os/tests -q` -> **148 passed / 8 failed**
  - 失敗8件はすべて data/decisions/decision_ledger.jsonl の不在が原因 (第4章で詳述)
  - 参考: HAB_FREEZE_RECORD_v1.md は commit 1c6d02c9e 時点で 153 passed と記録。
    現在の総数は156件であり、Freeze以降に3件追加されている
- 停止点:
  - TODO_325 (保留/高): Trust Boundary確立 (Windows ACL)
  - GL7-UNENFORCED-CONDITIONS-BUG (未着手/高): GL7安全条件3点が実行経路に未接続
  - PHI-OS-HUMAN-GATE-STATE-MODEL-V1 (進行中/高): 確定仕様だが未実装
  - TODO_368 (未着手/高): Orchestra から PHI-OS への書き込み経路が未実装
- 製品PHI-OS (Chrome拡張) の実体は PlanningCaliber/workshop/phi-os/ = 公開repoに不在

### 2.6 Context Runtime

- 存在/実装: phi_os/context/ に11モジュール
  context_runtime / working_context / execution_context / institution_context /
  memory_context / context_snapshot / context_scheduler / context_validator /
  access_gate / control_gate / permissions
- 接続/到達性 (repo実測):
  - app.py:4187-4188 — `ContextRuntime.boot()` を起動時に実行
  - mocka_mcp_server.py:223-238 — WorkingContext / maybe_snapshot /
    emit_event_to_context_runtime を呼出
  - **app と MCP の両方から到達する唯一のサブシステム**
- テスト: phi_os/tests/test_context_permissions.py 通過
- 承認: PART (context_runtime_version=v2 が実装済み。制度文書上の裁定は個別に追跡が必要)
- 停止点: TODO_430 (未着手/高) inject_context経由データの Indirect Prompt Injection 耐性監査

### 2.7 Relay

ユーザー仮説"ほぼ使われていない Relay"は、正確には半分だけ正しい。

- 存在/実装: relay/ に14モジュール
  relay_kernel / relay_bootstrap / replay_engine / replay_engine_v2 / replay_router /
  replay_audit / policy_engine / action_router / event_queue / mcp_bridge /
  repositories / repositories_sqlite / main
- 接続/到達性 (repo実測、2経路):
  1. app.py:1002-1013 `_get_relay_kernel()` シングルトン -> :1062 で `/collect` から
     `ingest()` を呼出。IDR-003 Phase2 の state projection。失敗しても collect は成功扱い
  2. phi_os/api/time_api.py:23,29 — RelayKernel を唯一の入口とする設計。
     time_api_bp は app.py:82 で登録済み = **/time/replay は実際に到達可能**
- したがって Runtime としての RelayKernel は稼働経路上にある (INACTIVE ではない)
- 一方、製品Relay (Chrome拡張 / Free-Pro-One / RLY- prefix) は収益化保留で停止中
- テスト: relay/ 配下に専用テストなし。core_kernel/relay_core/tests/ は存在するが
  core_kernel 自体が未配線 (2.13)
- 停止点: TODO_178 / TODO_179 / TODO_180 いずれも保留。TODO_383 (判定方式比較/未着手),
  TODO_W1 (provenance model統一/未着手)

### 2.8 Memory

- 存在/実装: memory/ に13ファイル
  memory_writer / memory_store / memory_index / memory_retriever / memory_context_builder /
  memory_pipeline / memory_registry / memory_model / memory_ingestor + 自己テスト3件
- 設計思想 (memory_pipeline.py 冒頭より): Event/Decision -> Writer -> Store -> Index ->
  Retriever -> Context Builder -> enriched_context。
  Governance/Semantic/Decision Layer のロジックには変更を加えない (読み取りのみ)
- **接続: NO** — リポジトリ全体を対象に `from memory.` / `import memory` を検索した結果、
  memory パッケージを import している外部モジュールは **0件**
- Runtime到達性: NO
- 自己検証 (本セッション実測): `python memory/memory_integration_test.py` -> **14/14 checks passed**
  つまり実装は健全であり、壊れているのではなく"配線されていない"
- Active: INACTIVE
- 製品Memory (MEM- prefix, Free実装完了 E20260526_041) の実体は workshop配下 = 公開repoに不在
- 停止点: 配線先の裁定が存在しない。実質的な後継が TODO_433
  (Knowledge Unit Governance Pipeline Phase A / 未着手/高)

### 2.9 Orchestra (制度側)

- 本体repo上の実体は orchestra/conflict_interpreter.py の1モジュールのみ。
  役割は Conflict + Decision から人間可読の説明文を生成する翻訳層。
  自己記載の禁止事項: conflict state の変更 / 意味の書き換え / Bridge・PHI-OS へのフィードバック
- 接続: architecture_verify.py:23 と bridge/tests/test_final_architecture.py:36 の2箇所のみ。
  **app.py / mocka_mcp_server.py からの到達経路なし**
- 検証 (本セッション実測): `python architecture_verify.py` 実行成功。
  Bridge -> PHI-OS -> Orchestra -> UI の Integration が OK 判定。
  成功条件4件 (conflictが永続する / どの層も意味を変更しない / 判断はあるが介入しない /
  観測だけで全構造が成立) すべて OK
- 製品Orchestra は本番稼働中 (Stripe -> Cloudflare Workers -> Resend) だが、
  そのコードは PlanningCaliber/workshop/Orchestra_Project/ = 公開repoに不在
- 停止点: **TODO_368 (未着手/高) — Orchestra から PHI-OS への書き込み経路が未実装**。
  すなわち現時点で"本番稼働中の製品Orchestra"と"制度カーネルMoCKA"は接続されていない。
  他に TODO_160 (export正規化/未着手), TODO_166 (UIブロッカー対策/未着手),
  TODO_425 (Configuration Sync Pipeline設計/進行中)

### 2.10 HAB (Human Authority Boundary)

- 存在: phi_os/hab/ に13ファイル。内訳は .md 9件 + .json 4件。
  **Pythonファイルは0件** = Runtime実体を持たない
  - AUTHORITY_POLICY_v0.1.md / HAB_CORE_DEFINITION_v0.1.md / HAB_AUDIT_CHECKLIST.md /
    HAB_CHANGELOG.md / HAB_OPEN_QUESTIONS.md / HUMAN_GATE_CONTRACT_v0.1.md /
    JARVIS_OPERATING_RULES_v0.1.md / jarvis_authority_boundary.md /
    STATE_MAPPING_TABLE_v0.1.md / README.md
  - actor_model.json / canonical_states.json / transition_ledger_schema.json
- 実装: NO
- テスト: phi_os/tests/ に test_hab_audit_checklist / test_hab_evidence_boundary /
  test_hab_jarvis_boundary / test_hab_state_transition の4ファイル。
  ただし内容は"文書と Ledger の整合検査"であり、コード実装の振る舞いテストではない
- 承認: HAB_FREEZE_RECORD_v1.md により Phase 9 Transition で Freeze 済み。
  権限境界の定義は確定している:
  - Human: authority=decision / finalization=allowed
  - JARVIS: authority=advisory / finalization=prohibited
  - System: authority=execution / decision authority=prohibited
- 未解決の語義問題: HAB は4つの異なる対象を指す (Human Authority Boundary /
  Phase8 HAB spine / PHI-HAB / HAB-D = DC_20260729_008)。
  さらに HAB_CORE_DEFINITION_v0.1.md が docs/governance/ と phi_os/hab/ の2箇所に
  同名で存在し内容が異なる (RB-03 として記録済み、未解消)
- 停止点: HAB-3FIELD-TRANSFORM-MIN-SPEC (未着手/高),
  TODO_HAB_5LAYER_DESIGN_PENDING (進行中/中), HG-H01..H10 未裁定

### 2.11 JARVIS

- 存在/実装: runtime/jarvis/ に12ファイル。構成は core/engine.py, gate/human_gate.py,
  record/ledger.py, record/adapter/{decision,ledger_adapter}.py,
  record/persistence/ledger_store.py, record/schema/decision_record.py
- 実装規模: 最小骨格。gate/human_gate.py は 682 bytes
- **接続: NO** — `runtime.jarvis` を import しているのは runtime/jarvis 内部の4行のみ
  (engine -> gate, gate -> ledger_adapter, ledger_adapter -> schema/persistence)。
  app.py / mocka_mcp_server.py からの参照は0件
- テスト (本セッション実測): `python -m pytest tests/jarvis -q` -> **8 passed**
  (test_decision_ledger / test_decision_record / test_decision_state_transition /
  test_ledger_adapter / test_ledger_persistence / test_ledger_record / test_ledger_store /
  test_runtime_smoke)
- 設計文書は大量に存在する (repo実測、いずれも tracked):
  - docs/audits/ : JARVIS_ARCHITECTURE_CURRENT / CAPABILITY_INVENTORY /
    BOUNDARY_ANALYSIS / GAP_ANALYSIS / RUNTIME_FLOW の5件
  - docs/governance/ : JARVIS_CONSTITUTION_DRAFT / JARVIS_RUNTIME_BETA_ARCHITECTURE_DRAFT_v0.1
    (62,572 bytes) / JARVIS_RUNTIME_BETA_DECISION_PACKAGE_FOR_HUMAN_GATE_REVIEW_v0.1 /
    JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1 / HGJ03 Evidence 4件 / HGJ04 Evidence 1件
- 承認状態: **Architecture承認のみ**。実装承認ではない (FC-03 として明文化済み)。
  Freeze Point は DP-1 = DC_20260807_001 (status=Active, approved_by=きむら博士)
- 停止点:
  - HG-J01..J04 未裁定 / HG-RB-01..HG-RB-09 未裁定
  - RB-07: fold の実装が存在しないため、DP-1-A の State 定義を Runtime 上で成立させる
    手段が現時点で存在せず、F-1 (状態説明) は現時点で実行可能でない
  - RB-12: 依拠する JARVIS_CONSTITUTION_DRAFT と HAB_CORE_DEFINITION がいずれも DRAFT 未裁定

### 2.12 Gateway / GPT

- 存在/実装: gateway/gateway.py (port 5010, 内部専用と自己宣言)。
  adapters は gpt / gemini / copilot / perplexity / genspark の5系統 (gateway.py:48-53)。
  周辺に auth.py / context_builder.py / connector_router.py / connector_caliber.py /
  lifecycle_manager.py / openapi.yaml
- 接続: phi_os/process_manager.py:93 に mocka_connector として起動定義あり
  (daemon=True, restart=True)
- Runtime到達性: PART。起動対象ではあるが、events 20,608件のうち
  **gateway_event はわずか10件** (Heinrich type_distribution 実測)。実質的にほぼ未使用
- GPT の位置づけ: ai_roster の正式メンバー。監査役としての実績あり
  (2026-06-17 GPT監査による Semantic Score Vector 実装)。
  同時に最古の重大インシデント群の主体でもある (E20260328_001..004 ai_violation
  "GPT無断ファイル上書き"4件 = Heinrich Layer1 critical に分類)
- テスト/検証: gateway/ 配下に専用テストなし
- 停止点: TODO_334 (Perplexity実機疎通/未着手), TODO_335 (Genspark実機疎通/未着手),
  TODO_417 (Copilot Studio Custom Connector実登録/保留), TODO_424 (mocka-api Worker
  廃止候補判定/未着手), TODO_430 (Indirect Prompt Injection耐性監査/未着手/高)

### 2.13 未配線の大規模資産 (追加発見)

調査対象13件の外にあるが、現状証明として無視できない規模の未配線資産が2件ある。

- **core_kernel/ : Pythonファイル134件、外部importは0件**
  サブパッケージ: core_store / event_contracts / governance / memory_core / orchestra /
  orchestra_core / phios_integration / prism / relay_core。
  唯一の repo内ヒットは interface/ai_capability_registry.py:10 のコメント行のみ
  ("既存の capability_registry.py (core_kernel/core_store/) は"という言及であり import ではない)
- **semantic/ : query_engine 20モジュール、外部importは0件**
  collision_governance / decision_replay / drift_monitor / drift_recorder /
  execution_layer / execution_orchestrator / explanation_builder / human_gate /
  human_gate_interface / meaning_query_engine / observation_surface / order_normalizer /
  projection_candidate / projection_result / runtime_bridge / semantic_projection_layer /
  structural_recovery ほか

いずれも JARVIS Phase 0 調査の指摘 (core_kernel 133 .py で外部import 0件 /
semantic/query_engine は HAB spine で未配線) を、本セッションで独立に再現した。
ファイル数の差 (133 -> 134) は調査時点の差分と考えられる。

---

## 3. Active / Inactive の実測根拠

| 状態 | 対象 | 実測根拠 |
|------|------|----------|
| ACTIVE | app.py / MCP / Event Gate / Context Runtime / PHI-OS | 本セッションからMCP経由で応答取得。最新イベント 2026-08-17T02:51 |
| ACTIVE | Decision Ledger | 最新 DC_20260816_001 (前日) |
| PART | Human Gate | CLI経路は稼働実績あり / HTTP面は未登録で到達不能 |
| PART | Relay | RelayKernel は /collect と /time/replay の経路上 / 製品Relayは収益化保留 |
| DORMANT | Gateway | 起動定義あり / gateway_event 累計10件のみ |
| INACTIVE | Memory | 外部import 0件。自己テストは 14/14 pass |
| INACTIVE | Orchestra (制度側) | 外部importは検証スクリプトのみ。Runtime経路なし |
| DESIGN | HAB / JARVIS | 文書とテストは存在。Runtime配線なし。Architecture承認のみ |
| UNWIRED | core_kernel / semantic | 外部import 0件 (計154モジュール規模) |

---

## 4. 公開と非公開の境界 — 実測

この章が、公開側調査との照合における中心的な材料である。

### 4.1 公開リポジトリ (m-sirius-k/MoCKA) に存在するもの

制度カーネルのソースコードはほぼ全量が公開されている。
app.py / mocka_mcp_server.py / phi_os/ / relay/ / memory/ / decision/ / orchestra/ /
gateway/ / runtime/ (jarvis含む) / governance/ / core_kernel/ / semantic/ /
CONSTITUTION.md / PHI_OS_CONSTITUTION_v1.md / 各種 ARCHITECTURE 文書 /
docs/audits/ の JARVIS 監査5文書 / docs/governance/ の JARVIS・HAB 統治文書。

### 4.2 公開リポジトリに存在しないもの

.gitignore の実測結果:

```
1: # data/ 内は全除外。Cloudflare 同期用4ファイルのみ例外追跡
2: data/*
   (例外は MOCKA_OVERVIEW / MOCKA_TODO / lever_essence / events_latest /
    MOCKA_TODO_ACTIVE / MOCKA_TODO_REFERENCE_LOCKED / MOCKA_TODO_ARCHIVE /
    MOCKA_ENDPOINTS の8件のみ)
63: # workshop配下は非公開化（TODO_354）。以後はmocka-workshop-private側で管理する。
65: PlanningCaliber/workshop/
```

結果として非公開なのは以下である。

1. **Event Ledger の実体** — events.db 20,608件。repo上の mocka_events.db は0バイト
2. **Decision Ledger の実体** — decision_ledger.jsonl 240件。repo上に存在しない
3. **recurrence_registry / essence / trajectory 等の運用データ**
4. **製品実体の全量** — PlanningCaliber/workshop/ 配下が丸ごと除外されているため、
   Orchestra / Relay / Memory / PHI-OS の Chrome拡張コードは公開repoに1行も存在しない
   (本クローンでも PlanningCaliber/workshop/ ディレクトリ自体が不在)

### 4.3 この境界がもたらす検証上の帰結 (実証済み)

本セッションで `python -m pytest phi_os/tests -q` を実行した結果は **148 passed / 8 failed**。
失敗8件の内訳と原因は完全に一致している。

```
test_hab_evidence_boundary.py::test_decision_ledger_exists
test_hab_evidence_boundary.py::test_decision_ledger_has_records
test_hab_evidence_boundary.py::test_decision_ledger_contains_timestamp
test_hab_jarvis_boundary.py::test_ledger_exists_as_external_decision_record
test_hab_state_transition.py::test_state_transition_record_exists
test_hab_state_transition.py::test_previous_state_exists
test_hab_state_transition.py::test_next_state_exists
test_hab_state_transition.py::test_transition_has_evidence_reference

原因(全件共通): FileNotFoundError / assert False
  -> /home/user/MoCKA/data/decisions/decision_ledger.jsonl が存在しない
```

すなわち:

**MoCKA の権限境界 (HAB) の検証は、公開リポジトリのクローン単体では成立しない。**
HAB の Evidence Boundary / JARVIS Boundary / State Transition を検証する8テストは
いずれも Decision Ledger の実体を必要とし、その実体は .gitignore により非公開である。
HAB_FREEZE_RECORD_v1.md が記録する"153 passed"は、きむら博士のホスト環境でのみ再現可能であり、
第三者が独立に再現することは現時点で不可能である。

これは欠陥の指摘ではなく、境界の位置の実測である。
現在の MoCKA は"制度の骨格は公開・制度が実際に動いた証拠は非公開"という構成になっている。
公開側が掲げる evidence supremacy / append-only records / multi-audit といった原則に対し、
外部からその原則の履行を検証する手段は、現状 seal hash と anchor record に限られる。

---

## 5. 検出した整合性の穴

### 5.1 記録は存在するが成果物が存在しない (要判定)

イベント E20260813_788518366811d
(when 2026-08-13T04:19:48Z / who_actor Claude-haiku-4-5-20251001)
title: `CHANGE_DONE: JARVIS Architecture Consolidation Period - Priority 1-4完了`

同イベントは以下5件の成果物の完成を主張している。本セッションで HEAD=da4d4db に対し
`find` による全数検索を行った結果、**5件すべてリポジトリ上に存在しない**。

| 主張された成果物 | repo実測 |
|------------------|----------|
| docs/jarvis/JARVIS_RUNTIME_INTERFACE_v1.md | NOT FOUND (docs/jarvis/ 自体が不在) |
| context_vector.py | NOT FOUND |
| evaluator_dynamic_v2.py | NOT FOUND |
| tic_layers_2_4_spec.md | NOT FOUND |
| DECISION_A_B_2_PROBLEM.md | NOT FOUND |

留意事項 (過大主張を避けるため明記する): JARVIS 系文書は過去にも untracked のまま
Windowsホスト上に保持され、後日 commit された前例がある (E20260807 系)。
したがって本件も"ホスト上に untracked で存在する"可能性は排除できない。
確定できるのは次の一点である — **これらは公開リポジトリの main に到達しておらず、
第三者から検証可能な形では存在しない。** 一方で同イベントは実装完了 ("実装完了したもの"
"すぐに運用可能") を宣言している。記録と公開状態の間に差がある。

さらに同イベントの主張と、本調査の実測は矛盾する。
同イベントは L1-L5 の5層で JARVIS Runtime を"統合架橋確定"としているが、
実測では runtime/jarvis/ は外部から一度も import されていない (2.11)。

判断は行わない。Human Gate 提示事項として第6章に記載する。

### 5.2 Human Gate HTTP面の未登録

2.4 のとおり。phi_os/human_gate.py が Blueprint と5ルートを実装しながら
app.py に登録されていない。JARVIS_CAPABILITY_INVENTORY.md の指摘を独立再現。
対応 TODO は TODO_429 (未着手)。

### 5.3 HAB_CORE_DEFINITION_v0.1.md の二重存在

docs/governance/ と phi_os/hab/ に同名ファイルが存在し内容が異なる。
RB-03 として記録済みだが未解消。DP-1 は前者を上位方針として引用している。

### 5.4 UTF8_MANDATE 違反の疑い (軽微)

docs/governance/HAB_FREEZE_RECORD_v1.md の先頭に BOM が存在する。
UTF8_MANDATE.md および TODO_155 は BOM を禁止している。
本調査では READ-ONLY のため修正していない。

---

## 6. Human Gate 提示事項

いずれも本報告書では裁定せず、選択肢の列挙にとどめる
(mocka_human_gate_decision_definition_v1.md の規約に従い decision フィールドを含めない)。

- HG-CS-01: E20260813_788518366811d (5.1) の扱い。
  観測される選択肢: (a) ホスト上の untracked 実体の有無を確認する
  (b) Integrity Classification に Unknown として登録する
  (c) 記録の後退 (R2訂正) を行う (d) 現状のまま保持する
- HG-CS-02: 未配線資産 (core_kernel 134 / semantic 20 / memory 13 / decision 8 /
  orchestra 1 / runtime/jarvis 12 = 計188モジュール規模) の制度上の位置づけ。
  観測される選択肢: (a) 配線対象として TODO 化 (b) Design Asset として凍結宣言
  (c) 廃止判定 (d) 現状のまま保持
- HG-CS-03: 4.3 の検証不可能性の扱い。
  観測される選択肢: (a) Decision Ledger の一部を公開可能な形で切り出す
  (b) HAB テストを Ledger 非依存に書き換える (c) 検証は内部限定と明示的に宣言する
  (d) 現状のまま保持
- HG-CS-04: 最終 seal が 2026-07-07 で停止している件 (2.2) の扱い

---

## 7. 本報告書が行っていないこと

コード変更なし / スキーマ変更なし / データ変更なし / TODO status変更なし /
Decision Ledger 登録なし / Integrity Classification 登録なし / Seal 生成なし /
Human Gate 代行なし / 既存ファイルの変更なし。
新規作成は本ファイル1件のみ。

pip install (pytest / flask / flask-cors / python-dotenv / requests) は
隔離コンテナ内の実行環境整備であり、リポジトリには影響しない。

---

## 8. 一次証拠の再現手順

```
# 未配線の確認
grep -rn "core_kernel" --include="*.py" . | grep -v "^./core_kernel/"
grep -rn "from memory\.\|import memory\b" --include="*.py" .
grep -rn "runtime.jarvis" --include="*.py" .

# Human Gate HTTP面の未登録確認
grep -n "register_blueprint" app.py
grep -n "human_gate_bp" phi_os/human_gate.py

# テスト再現
python -m pytest phi_os/tests -q      # 148 passed / 8 failed
python -m pytest tests/jarvis -q      # 8 passed
python memory/memory_integration_test.py     # 14/14
python decision/decision_integration_test.py # 59/59
python architecture_verify.py                # Integration OK

# 公開境界の確認
grep -n "data\|workshop" .gitignore
ls -la mocka_events.db    # 0 bytes
```
