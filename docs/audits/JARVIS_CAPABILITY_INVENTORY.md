# JARVIS Phase 0 — Capability Inventory (Current State)

**Document:** JARVIS_CAPABILITY_INVENTORY.md
**Status:** INVESTIGATION(現状記録のみ。設計・提案・改善案を含まない)
**調査日:** 2026-08-04
**実装変更:** なし

## 0. 判定基準

| 状態ラベル | 定義(本文書における厳密な意味) |
|---|---|
| **Operational** | 稼働中プロセスまたは正本コード経路上に存在し、実データの増加/応答を本調査で実測した |
| **Implemented / Unwired** | コードは実在するが、稼働経路(`app.py` 5000 / `mocka_mcp_server.py` 5002)から到達する参照を本調査で確認できなかった |
| **Design Only** | 文書のみ存在。対応する実装コードを本調査で確認できなかった |
| **Unknown** | 実装の有無・配線状態を本調査で判定できなかった |

「参照を確認できなかった」は静的import grep(`archive/`・`venv/` 除外)の範囲での所見であり、
動的import・サブプロセス経由の呼出は本調査の範囲外である。

---

## 1. Capability 一覧(サマリ)

| # | Capability | 状態 | 一次証跡 |
|---|---|---|---|
| C-01 | Event Recording | **Operational** | `events` 19,037行、最新 2026-08-04T05:16:21Z |
| C-02 | Event Hash Chain / Signature | **Operational**(整合性検証は未実施) | `event_signatures` 19,037行 |
| C-03 | Decision Ledger | **Operational** | `decision_ledger.jsonl` 206行、最新 `DC_20260801_002` |
| C-04 | Human Gate(状態モデル) | **Implemented / Unwired**(HTTP API) + Operational(記録層) | `human_gate_events` 1,779行 / `human_gate_bp` 未登録 |
| C-05 | Evidence Management | **Operational** | `related_events` / `related_documents` フィールド、`docs/audits/` |
| C-06 | Audit(違反検出) | **Operational** | `audit_violations` 22,539行(NEW 6) |
| C-07 | Verification / Integrity | **Operational** | `/integrity/status`, `phi_os/integrity.py`, `verify_*.py` 群 |
| C-08 | Runtime Validation(GL7) | **Operational**(呼出元は限定) | `structural/execution_governance.py` |
| C-09 | MCP | **Operational** | port 5002, tools 23件 |
| C-10 | Search | **Operational** | `mocka_search`(events + knowledge_gate), `/search` |
| C-11 | Logging | **Operational** | `_*_stdout.log` / `_*_stderr.log` 群、fallback log |
| C-12 | Seal / Anchor | **Operational**(部分) | `mocka_seal` tool, `/audit/seal`, `scripts/ledger/ledger_seal.py` |
| C-13 | Git Write Governance | **Operational** | `governance/mocka_git_safe_commit.py` |
| C-14 | External AI Gateway | **Operational** | port 5010, adapters 5種 |
| C-15 | Public Sync / Publish | **Operational** | `sync_watch.py` 600秒周期、allowlist 4ファイル |
| C-16 | Registry(KN-004) | **Operational**(MCP tool として) | `mocka_registry_*` 3 tools |
| C-17 | Incident 管理 | **Operational**(read) | `mocka_get_incidents`, `mocka_integrity_*` |
| C-18 | TODO / Phase 管理 | **Operational** | `mocka_get_todo` / `add` / `update`, TODO 92件 |
| C-19 | Essence 抽出 | **Operational** | `essence` 3行, `essence_update` 375件, `interface/essence_*.py` |
| C-20 | Encoding Guard(UTF-8) | **Operational** | `mocka_check_utf8`, `UTF8_MANDATE.md` |
| C-21 | Semantic / Meaning Layer(Phase7-8) | **Implemented / Unwired** | `semantic/query_engine/` 外部被参照0 |
| C-22 | Orchestra(協調制御) | **Operational**(製品側) / **Unwired**(`core_kernel/orchestra`) | 下記 §2.22 |
| C-23 | Relay(状態同期) | **Implemented**(遅延import配線あり) | `app.py:1005`, `phi_os/api/time_api.py:23` |
| C-24 | Memory(Institutional Memory) | **Design Only** + 別実装が分散 | 下記 §2.24 |
| C-25 | core_kernel 構造化サブシステム群 | **Implemented / Unwired** | 外部import 0件 |
| C-26 | Runtime B(Go) | **Operational**(単体) / 接続 **Unknown** | port 5003 |
| C-27 | Caliber(検索/評価) | **Operational**(単体) / 接続 **Unknown** | port 5679 |
| C-28 | PHI-OS Runtime Foundation | **Implemented**(別repo) | `workshop/phi-os/phios/runtime/` |
| C-29 | Prism(観測/認知) | **Implemented / Unwired** | `core_kernel/prism/` |
| C-30 | Living Room Hub | **Operational**(`dry_run:true`) | port 8765 |

---

## 2. 各 Capability の詳細

### 2.1 C-01 Event Recording — Operational

- 実体: `events` テーブル(5W1H 34カラム)、19,037行。
- 最新イベント実測: `E20260804_581872629c8a6` / `2026-08-04T05:16:21Z` / who_actor `script:mocka_git_safe_commit` / what_type `claude_mcp` / where_component `mcp_caliber` / channel_type `gate`。
- 書込入口(Confirmed、§JARVIS_RUNTIME_FLOW に詳細): MCP tool `mocka_write_event` → HTTP POST `http://localhost:5000/api/gate/event` → `phi_os/event_gate.py`。
- 入力必須検証: `title` / `description` / `author` が空文字なら `gate_rejected` を返す(`mocka_mcp_server.py:666-683`)。レガシー値 `"Claude"`/`"claude"` のみ既定Actorへ正規化。
- 冪等制御: `gate_idempotency` テーブル 2,615行、`phi_os/event_gate.py:103 _ensure_idempotency_table()`。

### 2.2 C-02 Event Hash Chain — Operational(検証は未実施)

- `event_signatures`(19,037行): `previous_hash` / `current_hash` / `signature_version` / `algorithm` / `seq`。
- `phi_os/event_gate.py:90` に「後方互換のため signature の current_hash/previous_hash を反映する」処理あり。
- **本調査では連鎖の整合性検証(全走査)を実施していない**。整合しているか否かは **Unknown**。
- 関連資産: `verify_chain.py` `verify_full_chain.py` `verify_full_chain_and_signature.py` `verify_ledger.py` `scripts/ledger/rebuild_chain.py`(いずれもファイル実在を Confirmed、実行はしていない)。

### 2.3 C-03 Decision Ledger — Operational

- 実体: `data/decisions/decision_ledger.jsonl`、206行、14フィールド。
- MCPツール: `mocka_decision_write` / `mocka_decision_get` / `mocka_decision_list`(port 5002 で公開中)。
- HTTP: `/decision/log`, `/decision/log/detail`, `/decision/approve`, `/decision/reject`(app.py)。
- 品質上の実測事実: **最新レコード `DC_20260801_002` の `context` / `alternatives` に文字化けが実在する**。
- 別ストア(Confirmed、統合されていない): `data/ise/decision_ledger.jsonl`(2026-06-12)、
  `PlanningCaliber/workshop/phi-os/data/ise/decision_ledger.jsonl`(2026-07-29)、
  `PlanningCaliber/workshop/phi-os/ise/decision_ledger.py`、`workshop/seo-os/caliber/decision_ledger.py`。

### 2.4 C-04 Human Gate — 記録層 Operational / HTTP API Unwired

**Operational な部分:**
- `human_gate_events` テーブル 1,779行。最新は 2026-07-31T09:01:43Z の `approve`(PENDING→APPROVED)。
- `app.py` の `/decision/approve` `/decision/reject`(route 実在、Confirmed)。
- `governance/human_gate_cli.py` が `phi_os.human_gate` の `submit/approve/reject/get_state/list_pending` を import(CLI経路、Confirmed)。

**Unwired な部分(重要):**
- `phi_os/human_gate.py` は `human_gate_bp` Blueprint を定義し、5 route を持つ:
  `/api/human_gate/submit` `/approve` `/reject` `/status/<request_id>` `/pending`。
- **`app.py` の `register_blueprint` 11件に `human_gate_bp` は含まれていない**(実測)。
  → PHI-OS Human Gate の HTTP API は稼働中の 5000 番から到達不能。

> **【R2 精緻化 2026-08-04 — 「Unwired」の範囲を限定する】**
> 未配線なのは **HTTP Blueprint のみ**であり、**モジュール本体は本番DBに対して稼働実績がある**。
> (初版は「CLI 経路で稼働している」と書いたが、呼出主体は特定できていない。
> `event_id` の `HG` prefix 生成元が `phi_os/human_gate.py:73` である以上、同モジュール経由は Confirmed。
> CLI は `--note` を受け付けるため整合する候補だが断定できず、`phi_os/migrate_prevention_queue.py` は
> note 文字列不一致で除外済み。詳細: `JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md` §4.3 R2)
> `human_gate_events` の実データで確認(Confirmed):
>
> | event_id | timestamp | action | request_id |
> |---|---|---|---|
> | `HG20260731_503234669eed6` | 2026-07-31T09:01:43Z | **approve** | `INC-LIFECYCLE-INC-20260401-001` |
> | `HG20260731_422433419af2d` | 2026-07-31T09:00:22Z | submit | `INC-LIFECYCLE-INC-20260401-001` |
> | `HG20260708_40524292157c2` | 2026-07-08T01:16:45Z | submit | `TEST_CLI_VERIFY_001` |
>
> 2026-07-31 の submit→approve 対は `DC_20260731_007`(Human Gate 実装開始承認 — RC-B最小実装(INC Lifecycle))に対応する。
> したがって本項の状態ラベルは「Implemented / Unwired」ではなく
> **「モジュール本体=Operational(CLI経路) / HTTP API=Unwired」**が正確である。
> 詳細: `docs/governance/JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md` §4.3
- 設計上の宣言(`phi_os/human_gate.py` 冒頭): 「PHI-OSがHuman Gateの唯一の状態管理責務を持つ。GL7およびApp層はHuman Gate状態を保持しない(本モジュールが単一の真実)」「stateそのものは保存しない。eventのみ保存する(イベントソーシング)」。
- 状態: `PENDING / APPROVED / REJECTED / EXPIRED / CANCELED`、遷移表 `TRANSITIONS` 定義あり。

**並存する Human Gate 実装(Confirmed / 4系統):**
| # | 実体 | 経路 |
|---|---|---|
| 1 | `phi_os/human_gate.py` | Blueprint 未登録 + CLI から import |
| 2 | `app.py` `/decision/approve` `/decision/reject` | 稼働中HTTP |
| 3 | `governance/mocka_git_safe_commit.py` の Core System File 除外 | git write path(承認待ちとして未commit保持) |
| 4 | `semantic/query_engine/human_gate.py` + `human_gate_interface.py` | `semantic/` 内部で閉じている |
| 5 | `governance/human_gate_continuity.py` | `tests/test_human_gate_continuity.py` から参照 |

これらが同一の裁定を表現しているかは、本調査では **Unknown**。

### 2.5 C-05 Evidence Management — Operational

- Decision Ledger の `related_events`(event_id配列)/ `related_documents`(パス配列)により証跡が紐付く(Confirmed、`DC_20260801_002` 実測)。
- `docs/audits/` に一次証跡文書群が集積(本文書もここに配置)。
- `phios/adapter/mocka_integration_adapter.py` の `link_evidence_for_event`(PHI-OS側、別repo、既存記録による **Hypothesis**)。

### 2.6 C-06 Audit — Operational

- `audit_violations` 22,539行。status 内訳実測: `RESOLVED_LEGACY_BULK_FIX` 22,533 / **`NEW` 6**。
- HTTP: `/audit/status` `/audit/seal`。`audit/` ディレクトリ 32 .py。
- `cross_audit.py` / `data/cross_audit.db`(28,672 bytes, 2026-04-28)。

### 2.7 C-07 Verification / Integrity — Operational

- `phi_os/integrity.py` / `phi_os/integrity_routes.py`(`integrity_bp` は app.py に **登録済み**、Confirmed)。
- HTTP: `/integrity/status` `/integrity/monitor` `/api/verification/verify`。
- MCP: `mocka_integrity_write` / `mocka_integrity_get` / `mocka_integrity_list`。
- ルート直下の verify 群: `verify_all.py` `verify_chain.py` `verify_ledger.py` `verify_token.py` `architecture_verify.py` ほか。

### 2.8 C-08 Runtime Validation (GL7) — Operational

§JARVIS_ARCHITECTURE_CURRENT §4.3 参照。呼出元は `governance/seal_governance_*` と `structural/*` の6ファイルに限定される(Confirmed)。
`app.py` / `mocka_mcp_server.py` は GL7 を import していない(実測)。両者での GL7 言及はコメントとエラーコード文字列 `GL7_EXECUTION_BLOCKED`(`mocka_mcp_server.py:495`)。

### 2.9 C-09 MCP — Operational

port 5002、version 1.5.0、tools 23件。`/agent/<tool_name>` による直接HTTP呼出も実在(Confirmed)。

### 2.10 C-10 Search — Operational

`mocka_search` は `search_events()` と `search_knowledge_gate()` の2ソースを合成して返す(`mocka_mcp_server.py:660-664` 実測)。app.py 側に `/search` route(app.py:3095)。

### 2.11 C-11 Logging — Operational

`_audit_*` `_final_*` `_trace_*` `_mocka_*_restart_*` の stdout/stderr ログがリポジトリ直下に実在。
`governance/mocka_git_safe_commit_ledger_fallback.log` は event 記録の HTTP 送信失敗時の fallback(コード上 Confirmed、未コミット変更としても検出)。

### 2.12 C-12 Seal / Anchor — Operational(部分)

- MCP tool `mocka_seal` 公開中。HTTP `/audit/seal` `/seal/history`。
- `governance/seal_governance_gate.py` / `seal_governance_wrapper.py` が GL7 を経由(Confirmed)。
- `scripts/ledger/ledger_seal.py` `anchor_update.py` `calc_anchor_bundle_hash.py` 実在。
- `seal.json` は 2026-06-16 の `Phase5 Foundation` / commit `bfc0150f8` / `VERIFIED` で停止している(mtime 2026-06-16)。
- `AUTO_SEAL_PENDING` イベント 129件が `events` に存在(Confirmed)。

### 2.13 C-13 Git Write Governance — Operational

`governance/mocka_git_safe_commit.py`(Confirmed):
- 「全ての git add/commit/push 操作を経由する単一の共有ヘルパー(TODO_364)」と自己宣言。
- `CORE_SYSTEM_DIRS = ("phi_os/", "interface/", "structural/", "gateway/")`、
  `CORE_SYSTEM_FILES_EXTRA = ("app.py", "index.html", "scripts/ledger/anchor_update.py", "PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py")`
  → これらは無条件 `git add -A` から除外し、人間承認待ちとして未コミット保持する。
- デフォルト `push=False`。`push=True` は検証ステップ経由の明示呼出のみ(運用ルールとしてコード内に明記)。
- 記録: `http://localhost:5002/agent/mocka_write_event` へ CHANGE_START/CHANGE_DONE 相当を送信(TODO_413)。

### 2.14 C-14 External AI Gateway — Operational

port 5010、`X-MoCKA-Key` 必須。adapters: GPT / Copilot / Gemini / Genspark / Perplexity。
`openapi.yaml` / `cloudflare/` 同梱。外部公開URL(`gateway.nsjp.org` 等)の現在の到達性は本調査 **未検証**。

### 2.15 C-15 Public Sync / Publish — Operational

`sync_watch.py`: 600秒周期、allowlist 4ファイルのみを `git add`、`mocka_git_safe_commit(paths=GIT_TARGETS, push=True)`。
git log の直近commitが全て `auto sync <ISO>` であることから、実際に稼働していることが Confirmed。

### 2.16 C-16 Registry — Operational(tool として)

`mocka_registry_get` / `mocka_registry_add` / `mocka_registry_current_state` が 5002 で公開中。
`PlanningCaliber/workshop/registry_kn004/` 実在。データ実体・格納先は本調査 **未確認**。

### 2.17 C-17 Incident 管理 — Operational(read)

`mocka_get_incidents` 公開中。`docs/audits/INC_PIPELINE_FAILURE_ANALYSIS_v0.1.md` 等の一次文書実在。

### 2.18 C-18 TODO / Phase 管理 — Operational

`data/MOCKA_TODO.json`: todos 92(未着手52 / 完了15 / 保留13 / 進行中10 / 保留(2026-06-15以降)1 / 廃止1)、completed 58。
`_snapshot_at` は 2026-08-04(sync_watch により更新)だが `meta.updated` は 2026-07-29。
末尾TODO: `TODO_450`〜`TODO_452`, `TODO_W1/W2/W4`, `TODO_456`(保留), `TODO_457`。

### 2.19 C-19 Essence 抽出 — Operational

`essence` テーブル3行、`essence_update` イベント375件。
`interface/essence_extractor.py` `essence_condenser.py` `essence_classifier.py` `essence_pipeline.py`
`essence_auto_updater.py` `essence_resolver.py` `essence_trigger.py` `essence_to_share.py` 実在。
`data/lever_essence.json` は sync_watch allowlist に含まれ、外部公開対象。

### 2.20 C-20 Encoding Guard — Operational

`mocka_check_utf8` tool、`UTF8_MANDATE.md`、`check_utf8_mandate.py` `check_unicode.py`。
全常駐プロセスが `python -X utf8` で起動されている(実測)。

### 2.21 C-21 Semantic / Meaning Layer — Implemented / Unwired

`semantic/query_engine/`(20ファイル): `meaning_query_engine.py` `execution_layer.py` `execution_orchestrator.py`
`order_normalizer.py` `collision_governance.py` `drift_monitor.py` `drift_recorder.py` `human_gate.py`
`human_gate_interface.py` `observation_surface.py` `runtime_bridge.py` `semantic_projection_layer.py`
`decision_replay.py` `structural_recovery.py` `explanation_builder.py` `data_binding.py`
`projection_candidate.py` `projection_result.py`。

`execution_orchestrator.py` 冒頭(Confirmed):
> Phase8-3 - Execution Orchestrator v0 (HAB spine, pass-through only)
> 契約: docs/contracts/phase8_hab_runtime_integration_v1.md (1.2節)
> 判断・裁定・解釈・最適化は一切行わない
> 絶対禁止: merge禁止 / collision削除禁止 / 非破壊構造維持 / Human Gate単一裁定点

外部からの import は本調査で **0件**(`semantic/` 内部の `observation_surface.py` のみが参照)。

### 2.22 C-22 Orchestra — 二重実体

| 実体 | 状態 |
|---|---|
| `MoCKA/orchestra/`(`conflict_interpreter.py`) | `architecture_verify.py` と `bridge/tests/` からのみ参照。app.py 未参照 |
| `core_kernel/orchestra/`(8ファイル) | 外部import 0件 = Unwired |
| `core_kernel/orchestra_core/` | 外部import 0件 = Unwired |
| `PlanningCaliber/workshop/Orchestra_Project/` | 実在。稼働状態は本調査 **Unknown** |

`current_phase` は「Orchestra稼働中」と記載しているが、**どの実体が稼働しているかは本調査で同定できなかった(Unknown)**。

### 2.23 C-23 Relay — Implemented(配線あり)

`relay/`(14 .py): `relay_kernel.py` `policy_engine.py` `action_router.py` `event_queue.py` `mcp_bridge.py`
`replay_engine.py` / `replay_engine_v2.py` / `replay_router.py` / `replay_audit.py` `repositories_sqlite.py`。
`app.py:1005` と `phi_os/api/time_api.py:23` から `RelayKernel` を import(Confirmed)。
`data/relay/event_log.db` 実在(2026-07-24)。
`current_phase` は「Relay未正式運用」と記載。

### 2.24 C-24 Memory — Design Only + 実装分散

| 実体 | 状態 |
|---|---|
| `docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md` ほか設計3文書 | Design(存在 Confirmed) |
| `core_kernel/memory_core/`(memory_store.py / record.py) | 外部import 0件 = Unwired |
| `MoCKA/memory/`(12 .py) | 外部import を本調査で確認できず |
| `workshop/phi-os/phios/runtime/memory_boundary.py` | 既存記録では「テスト以外からの参照ゼロ件=完全未配線」(**Hypothesis**、本調査で未再検証) |
| `workshop/memory/` | Chrome拡張製品(別層)。既存記録による **Hypothesis** |

### 2.25 C-25 core_kernel — Implemented / Unwired

133 .py、9サブパッケージ。**外部からの import 0件**(Confirmed、`archive/`・`venv/` 除外)。
唯一の言及は `interface/ai_capability_registry.py:10` のコメント:
> 既存の capability_registry.py（core_kernel/core_store/）は …

### 2.26 C-26 Runtime B — Operational(単体)

port 5003、Go実装 `mocka_runtime_b.exe` v1.0.0、`/b/health` `/b/count` `/b/events`。
`runtime_b/` ディレクトリ実在。MoCKA本体との接続関係は **Unknown**。

### 2.27 C-27 Caliber — Operational(単体)

port 5679、`mocka_caliber_server.py` v5、`{"keywords":77,"mode":"api_zero","threshold":0.6}`。
`caliber/`(15 .py)、app.py に `/caliber/status` `/caliber/process` `/caliber/scan` `/caliber/queue` route 実在。
5000 から 5679 への実際の呼出は本調査 **未検証**。

### 2.28 C-28 PHI-OS Runtime Foundation — Implemented(別repo)

`PlanningCaliber/workshop/phi-os/phios/`: `runtime/` `core/` `phl/` `adapter/` `meaning/` `registry/`
`context_assembly/` `ledger_gate.py` `boot.py`。
`phios/phl/relay_client.py`(Confirmed 実測):
- `MCP_URL = "http://localhost:5002/mcp"`
- `GATE_AUDIT_URL = "http://localhost:5000/api/gate/audit"`
- read-only allowlist を強制(`refused: '<tool>' is not in the read-only allowlist`)
→ **PHI-OS Core から MoCKA への唯一の許可経路が実装として実在することを Confirmed**。

### 2.29 C-29 Prism — Implemented / Unwired

`core_kernel/prism/`: `analyzer.py` `cognitive_state_engine.py` `context_engine.py` `correlation_engine.py`
`observation_engine.py` `pipeline.py` `provider.py` + `interfaces/` `models/`。外部import 0件。

### 2.30 C-30 Living Room Hub — Operational(dry_run)

port 8765、`living_room/hub.py`、`{"hub":"living_room v0.1","db_events":19035,"db_ok":true,"dry_run":true}`。
`db_events` が `mocka_events.db` の `events`(19,037)と近い値を返すことから同DBを参照している可能性があるが、
**接続先の同定は本調査で未実施(Unknown)**。`dry_run:true` の意味も未確認。

---

## 3. 未確認事項 (Unknown) 一覧

1. `event_signatures` 連鎖の整合性(全走査未実施)
2. Human Gate 4〜5系統が同一の裁定概念を指すか
3. 「Orchestra稼働中」の稼働実体の同定
4. `:5679` `:5003` `:8765` `:6379` と本体経路の接続関係
5. Registry(KN-004)のデータ実体・格納先
6. 外部公開URL(ngrok / cloudflare / gateway.nsjp.org)の現在の到達性
7. `runtime/`(218 .py)と `archive/`(1,515 .py)の稼働・参照状態
8. 動的import / サブプロセス経由の依存(静的grep範囲外)

---

## Knowledge Lineage

**Document:** JARVIS_CAPABILITY_INVENTORY.md
**Status:** INVESTIGATION
**Created:** 2026-08-04
**Origin:** JARVIS Phase 0 : Current State Assessment(Investigation 2: Capability Inventory)
**Parent Documents:** JARVIS_ARCHITECTURE_CURRENT.md
**Evidence Sources:** §各項に記載(DB実測 / HTTP実測 / コード本文 / import grep)
**Affected Components:** なし(調査のみ、変更なし)
**Revision History:**
- R1(2026-08-04): 新規作成。実装・Decision Ledger登録なし。
