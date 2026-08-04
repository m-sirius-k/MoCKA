# JARVIS Phase 0 — Architecture Inventory (Current State)

**Document:** JARVIS_ARCHITECTURE_CURRENT.md
**Status:** INVESTIGATION(現状記録のみ。設計・提案・改善案を含まない)
**調査日:** 2026-08-04
**調査範囲:** `C:\Users\sirok\MoCKA`(main branch, HEAD=`adb661ddb`)、稼働中プロセス、`C:\Users\sirok\Desktop\aimd\`
**実装変更:** なし(本調査中にコード・設定の変更は一切行っていない)

## 0. 表記規約

| ラベル | 意味 |
|---|---|
| **Confirmed** | 本調査で一次データ(コード本文・DB実測・プロセス実測・HTTP応答)により直接確認した |
| **Hypothesis** | 文書・過去Decisionに記載があるが、本調査では再検証していない |
| **Unknown** | 確認できなかった。存在しないことを意味しない |

範囲限定の否定的所見(「見つからなかった」)は、調査範囲を必ず併記する。

---

## 1. Repository Baseline (Confirmed)

| 項目 | 実測値 |
|---|---|
| Repo root | `C:\Users\sirok\MoCKA` |
| Branch | `main`(他に `ai/codex/fix-content-orchestra` / `archive-cleanup` / `docs-safe-push` / `gl7-safe-push` / `gl_core` / `governance` / `phase19-payloadhash-strict` / `phase22_anchor_fix` / `phase_evolution`) |
| HEAD | `adb661ddb` "auto sync 2026-08-04T05:05:49Z" |
| 未コミット変更 | 4件(`governance/mocka_git_safe_commit_ledger_fallback.log`, `interface/health_baseline.json`, `interface/lever_essence.json`, `structural/beta_registry.json`) |
| 直近commit列 | すべて `auto sync <ISO8601>`(自動同期デーモン由来) |

`current_phase`(`data/MOCKA_TODO.json`、meta.updated=2026-07-29):
> Phase 4: 商用製品展開フェーズ（Orchestra稼働中・Relay未正式運用・vasAI封印済み）+ MoCKAコア改善フェーズ（Caliber検索品質改善・TIC/BEE/PHI OS実装完了）

---

## 2. Live Runtime Processes (Confirmed / 実測 2026-08-04 05:14–05:16 UTC)

`Get-NetTCPConnection` + `Win32_Process` + HTTP プローブによる実測。

| Port | Bind | Process | 応答実測 |
|---|---|---|---|
| 5000 | 127.0.0.1 | `python -X utf8 app.py` (PID 19428) | `GET /health` → `{"status":"ok","port":5000}` |
| 5002 | 0.0.0.0 | `python -X utf8 mocka_mcp_server.py` (PID 18848) | `GET /health` → `version 1.5.0`, `storage:"sqlite"`, `event_count:19013`, tools 23件 |
| 5003 | 127.0.0.1 | `mocka_runtime_b.exe` (PID 19044) | `GET /` → `{"name":"MoCKA Runtime B","runtime":"go","version":"1.0.0","endpoints":"/b/health /b/count /b/events"}` |
| 5010 | 0.0.0.0 | `python -X utf8 gateway.py` (PID 18872) | `GET /` → **401** `X-MoCKA-Key header missing` |
| 5679 | 0.0.0.0 | `python -X utf8 mocka_caliber_server.py` (PID 18948) | `GET /health` → `{"keywords":77,"mode":"api_zero","threshold":0.6,"version":"v5"}` |
| 8750 | 127.0.0.1 | `python -X utf8 app.py` (PID 19112) | `/`, `/health`, `/api/status`, `/status`, `/dashboard`, `/seo`, `/command` すべて **404** |
| 8765 | 127.0.0.1 | `python -X utf8 living_room/hub.py` (PID 18476) | `GET /health` → `{"hub":"living_room v0.1","db_events":19035,"db_ok":true,"dry_run":true}` |
| 6379 | 127.0.0.1 / ::1 | `memurai.exe` (PID 4764) | Redis互換。MoCKAとの接続関係は **Unknown**(本調査で未確認) |

**8750の同定**: プロセスが `app.py` であること・全プローブパスが404であることは Confirmed。
その実体が SEO-OS Command Center(`PlanningCaliber/workshop/seo-os/command_center/app.py`)であることは
`DC_20260713_001` に基づく **Hypothesis**(本調査でプロセスのcwd/ファイル実体は未同定)。
候補ファイルの存在自体は Confirmed(`PlanningCaliber/workshop/seo-os/command_center/app.py`)。

**MoCKA本体 `app.py` のポート**: `app.py:4194` に `app.run(host="127.0.0.1", port=5000, debug=False)`(Confirmed)。

---

## 3. Module Inventory (Confirmed / `.py` 実ファイル数、venv・node_modules除外)

### 3.1 MoCKA repo 直下ディレクトリ

| ディレクトリ | .py数 | 本調査で確認した性格 |
|---|---|---|
| `archive/` | 1515 | 過去資産の退避領域 |
| `PlanningCaliber/` | 365 | 別プロジェクト群のコンテナ(`workshop/` 配下、§4) |
| `runtime/` | 218 | civilization_* 系エンジン群ほか |
| `core_kernel/` | 133 | 構造化サブシステム群(§5でwiring状態を記載) |
| `interface/` | 109 | Flask Blueprint群・essence処理・dashboard等 |
| `scripts/` | 75 | `scripts/ledger/` に台帳操作38スクリプト |
| `tools/` | 66 | — |
| `phi_os/` | 50 | Event Gate / Human Gate / Integrity / event_bus |
| `governance/` | 41 | seal / git安全commit / 各種verify_* |
| `audit/` | 32 | — |
| `semantic/` | 27 | `semantic/query_engine/` に Phase7/8 実装(§5) |
| `structural/` | 24 | GL7(`execution_governance.py`)ほか |
| `mocka_v3_eval/`, `mocka3/`, `mocka-governance-kernel/`, `experiments/` | 24/21/20/20 | — |
| `caliber/`, `relay/`, `mcp/`, `gateway/`, `commercial_hardening/` | 15/14/14/14/14 | — |
| `memory/`, `learning_kernel/`, `reality_sync/`, `feedback/`, `bridge/`, `self_audit/` | 12/12/11/11/10/10 | — |
| `decision/`, `verify/`, `read_layer/`, `ops/`, `ui/` | 8/8/4/4/3 | — |

### 3.2 `core_kernel/` サブパッケージ (Confirmed)

`core_store/`(capability_registry, configuration, lifecycle, metadata, module_loader, persistence_interface, registry)、
`event_contracts/`(event_schema, event_types, replay_contract, validation, versioning)、
`governance/`(audit, contracts, engines, intelligence, runtime, self_verification)、
`memory_core/`(memory_store, record)、
`orchestra/`(event_bus, execution_graph, orchestra_engine, orchestrator_api, replay_engine, session_state, timeline_api, persistence)、
`orchestra_core/`(models, orchestra)、
`phios_integration/`(adapters, error_info, exceptions, external_interfaces, output_contract, prism_bridge)、
`prism/`(analyzer, cognitive_state_engine, context_engine, correlation_engine, observation_engine, pipeline, provider)、
`relay_core/`(relay_session, session_relay)。

### 3.3 `PlanningCaliber/workshop/` (Confirmed / ディレクトリ実在)

`DDP/` `Orchestra_Project/` `Relay_Project/` `cyber_benchmark/` `memory/` `mini-mocka-series/`
`mocka-cloudflare/` `needle_eye_project/` `ntp_insurance/` `phi-os/` `pr-os/` `registry_kn004/`
`scamper_engine/` `seo-os/` `vasAI_Project/`

`workshop/` は MoCKA 本体とは別の git repo root である(既存記録による **Hypothesis**、本調査では未再検証)。

---

## 4. Module Dependency (Confirmed / import実測)

### 4.1 `app.py` (port 5000) が実際に読み込むモジュール

`register_blueprint` 実測(app.py:72–82、11件):

```
interface.ai_session        -> ai_session_bp
interface.handshake         -> handshake_bp
interface.dashboard         -> dashboard_bp
interface.reflection_engine -> reflection_bp
interface.prediction_engine -> prediction_bp
interface.mentor_engine     -> mentor_bp
interface.commission_manager-> commission_bp
interface.context_composer  -> context_bp
phi_os.event_gate           -> gate_bp
phi_os.integrity_routes     -> integrity_bp
phi_os.api.time_api         -> time_api_bp
```

遅延import(関数内):
- `app.py:1005` `from relay.relay_kernel import RelayKernel`
- `app.py:1060` `from mcp.mcp_router import MCPRouterV2`

その他 top-level: `db_helper`, `event_buffer`, `essence_resolver`, `interface.pattern_engine_v2`(try付き)。

`app.py` の Flask route 総数: **109**(`@app.route` grep 実測)。主な系統:
`/api/gate/*`(phi_os経由) `/api/ise/*` `/api/beta/*` `/api/distribution/*` `/api/verification/verify`
`/decision/log` `/decision/approve` `/decision/reject` `/audit/status` `/audit/seal`
`/integrity/status` `/integrity/monitor` `/seal/history` `/search` `/public/*` `/relay/*` `/caliber/*`
`/api/phi-os-event` `/api/phi-os-status` `/api/living-context` `/tic/*` `/scamper/*`

### 4.2 サブシステム別の外部被参照(archive/・venv/除外、import文実測)

| モジュール | 外部からの import | 判定 |
|---|---|---|
| `core_kernel.*` | **0件** | **未配線**(唯一の言及は `interface/ai_capability_registry.py:10` のコメント文) |
| `decision.*` | **0件** | 外部被参照なし |
| `semantic.query_engine.*` | `semantic/` 内部のみ(`observation_surface.py` ← `execution_orchestrator.py`) | パッケージ内で閉じている |
| `structural.*` | 1件(`interface/reflection_engine.py:18` → `structural.morphology`) | 部分配線 |
| `orchestra.*` | 2件(`architecture_verify.py`, `bridge/tests/test_final_architecture.py`) | 検証スクリプト経由のみ、app.pyからは未参照 |
| `relay.*` | 2件(`app.py:1005` 遅延, `phi_os/api/time_api.py:23`) | 配線あり |
| `mcp.*` | 2件(`app.py:1060` 遅延, `relay/mcp_bridge.py:8`) | 配線あり |
| `phi_os.*` | app.py が3 Blueprint登録 + `structural/execution_governance.py` が `phi_os.event_bus` を fail-soft 呼出 | 配線あり |

**注記(範囲限定)**: 上記は `^\s*(from|import)\s+<pkg>` パターンの静的grepによる。
`importlib` / 動的ロード / サブプロセス経由の呼出は本調査で網羅していない。
`app.py:518` に `import importlib.util` の存在は確認済み(用途は未追跡=**Unknown**)。

### 4.3 GL7 (Governance Layer 7)

実体: `structural/execution_governance.py`(Confirmed)。

宣言された固定パイプライン(ファイル冒頭 docstring):
```
Task -> Grounding(GL1) -> Policy確認(GL1) -> Conflict検出
     -> Dry Run -> Approval(Human Gate) -> Execute -> Verify
```

- `FORBIDDEN_EXECUTIONS` に8種の禁止操作(`infer_path` / `bulk_rewrite_without_diff_review` 等)を定義。
- PHI-OS への連絡は `_emit_gl7_event()` から `phi_os.event_bus.append("GL7_EVENT", ...)` の **pure event forwarding のみ**。転送失敗時も GL7 自身の許可/拒否判定はブロックしない(fail-soft、GL7自身は fail-closed 維持)。
- 呼出元(Confirmed): `governance/seal_governance_gate.py`, `governance/seal_governance_wrapper.py`, `structural/consensus.py`, `structural/governance_pipeline.py`, `structural/knowledge_mass.py`, `structural/gl_integration_test.py`。
- `governance/mocka_git_safe_commit.py` は GL7 を **import していない**(コメントで「GL7構造的死角への対応」と言及するのみ)。

---

## 5. Persistence / Data Store (Confirmed / 実測)

### 5.1 `data/mocka_events.db`(143,986,688 bytes, mtime 2026-08-04)

| テーブル | 行数 |
|---|---|
| `claude_sessions` | 97,953 |
| `audit_violations` | 22,539(`RESOLVED_LEGACY_BULK_FIX` 22,533 / `NEW` 6) |
| `events` | 19,037 |
| `event_signatures` | 19,037 |
| `user_voice` | 9,836 |
| `event_bus` | 4,817 |
| `gate_idempotency` | 2,615 |
| `human_gate_events` | 1,779 |
| `error_rows` | 958 |
| `guidelines_reviewed` | 268 |
| `essence` | 3 |
| `gateway_nonces` | 2 |
| `guidelines_review_progress` / `judgement_reason` | 1 / 1 |
| `connector_log` | 0 |

`events` テーブルは 5W1H スキーマ(34カラム):
`event_id, when_ts, who_actor, what_type, where_component, where_path, why_purpose, how_trigger,
channel_type, lifecycle_phase, risk_level, category_ab, target_class, title, short_summary,
before_state, after_state, change_type, impact_scope, impact_result, related_event_id, trace_id,
free_note, _imported_at, _source, ai_actor, session_id, severity, pattern_score, recurrence_flag,
verified_by, data_integrity, integrity_note, recovered_short_summary`

`event_signatures`: `event_id, seq, timestamp, previous_hash, current_hash, signature_version, algorithm`
→ ハッシュ連鎖構造の存在は Confirmed。連鎖の完全性検証は本調査では **未実施**。

`human_gate_events`: `event_id, timestamp, type, action, request_id, payload, previous_state, next_state`
最新5件は 2026-07-31T09:01:43Z(`approve`: PENDING→APPROVED)、2026-07-31T09:00:22Z(`submit`)、2026-07-08、2026-06-23×2。

`events` の what_type 上位: `claude_mcp` 7,951 / `user_voice` 7,331 / `conversation_message` 1,735 /
`essence_update` 375 / `handshake` 375 / `HANDSHAKE` 133 / `AUTO_SEAL_PENDING` 129。
channel_type: `chat` 7,095 / `gate` 7,041 / `mcp` 3,527 / `internal` 624 / NULL 292 / `external` 172 ほか。

### 5.2 `data/decisions/decision_ledger.jsonl` (Confirmed)

- 206行(1行1 Decision、JSONL、append-only運用)
- フィールド14: `decision_id, title, context, alternatives, decision, rationale, impact, related_events, related_documents, approved_by, approved_at, supersedes, superseded_by, status`
- 最新: `DC_20260801_002`(status `Active`, approved_by `human_authority`, approved_at 2026-08-01T01:30:15Z)
- **最新レコードの `context` / `alternatives` フィールドに文字化け(mojibake)が実在する**(Confirmed、既知課題 TODO_423 と整合)

### 5.3 その他

| ファイル | 実測 |
|---|---|
| `data/MOCKA_TODO.json` | todos 92件 / completed 58件 / meta.updated 2026-07-29 / `_snapshot_at` 2026-08-04T05:16:08Z |
| `data/MOCKA_TODO_ACTIVE.json` | todos 92件 / meta.updated 2026-07-29(mtime 2026-07-29) |
| `data/ise/decision_ledger.jsonl` | 4,599 bytes(2026-06-12) — 本体台帳とは別ファイル |
| `PlanningCaliber/workshop/phi-os/data/ise/decision_ledger.jsonl` | 4,088 bytes(2026-07-29) — PHI-OS側の別データストア |
| `data/relay/event_log.db` | 40,960 bytes(2026-07-24) |
| `seal.json` | `{"phase":"Phase5 Foundation","created":"2026-06-16 01:58:52 UTC","commit":"bfc0150f8","status":"VERIFIED"}`(BOM付き) |
| `data/events.db` / `mocka_events.db`(root) | 0 bytes(空) |

`data/MOCKA_TODO.json` の `server_config`(Confirmed):
`app: localhost:5000（COMMAND CENTER）` / `caliber_pipeline: localhost:5679` / `mcp_caliber: localhost:5002` /
`ngrok: https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp`

---

## 6. API / CLI / MCP 接続関係 (Confirmed)

### 6.1 MCP

稼働中のMCPサーバ実体: `mocka_mcp_server.py`(port 5002, version 1.5.0)。
`/health` が返す tools 23件(実測):

```
mocka_get_overview  mocka_get_essence   mocka_get_todo      mocka_add_todo
mocka_update_todo   mocka_list_events   mocka_read_event    mocka_search
mocka_write_event   mocka_seal          mocka_get_incidents mocka_get_guidelines
mocka_get_command_center                mocka_check_utf8
mocka_registry_get  mocka_registry_add  mocka_registry_current_state
mocka_decision_write mocka_decision_get mocka_decision_list
mocka_integrity_write mocka_integrity_get mocka_integrity_list
```

HTTP直接呼出経路 `/agent/<tool_name>` の存在は Confirmed
(`governance/mocka_git_safe_commit.py` が `http://localhost:5002/agent/mocka_write_event` を使用)。

`mcp/` パッケージ(`server.py` / `mcp_router.py` / `mcp_gateway.py` / `router.py` / `transformer.py` / `adapters/`)
は稼働プロセスとは別実体であり、`app.py:1060` の遅延importと `relay/mcp_bridge.py` からのみ参照される(Confirmed)。

### 6.2 Gateway(外部AI接続層、port 5010)

`gateway/gateway.py` の route(Confirmed、9件):
`/api/v1/context` `/api/v1/todo` `/api/v1/phase` `/api/v1/essence` `/api/v1/last_event`
`/api/v1/summary` `/api/v1/health` `/api/v1/event`(POST)、`app.run(host="0.0.0.0", port=5010)`。
認証: `X-MoCKA-Key` ヘッダ必須(未付与で401、実測)。

外部AI アダプタ(Confirmed / ファイル実在): `adapter_gpt.py` `adapter_copilot.py` `adapter_gemini.py`
`adapter_genspark.py` `adapter_perplexity.py`。ほかに `auth.py` `connector_router.py` `connector_caliber.py`
`context_builder.py` `lifecycle_manager.py` `mocka_index_writer.py` `openapi.yaml` `cloudflare/`。

### 6.3 CLI

- `governance/human_gate_cli.py`(`phi_os.human_gate` の `submit/approve/reject/get_state/list_pending` を import)
- `governance/mocka_git_safe_commit.py`(全 git add/commit/push の単一共有ヘルパー、TODO_364)
- `scripts/ledger/` 38スクリプト(`ledger_seal.py` `ledger_verify.py` `ledger_replay.py` `rebuild_chain.py`
  `anchor_update.py` `ledger_audit.py` `ledger_time_travel.py` ほか)
- `MoCKA-START.bat` / `restart_mocka.bat` / `run_mocka.bat` / `run_mocka.vbs` / `start` / `stop`

### 6.4 Cloudflare / 外部公開

`PlanningCaliber/workshop/mocka-cloudflare/`: `export_for_cloudflare.py` `sync_watch.py` `worker.js` `wrangler.toml`。
`sync_watch.py`(Confirmed): `SYNC_INTERVAL = 600`、`GIT_TARGETS` は以下4ファイルのみ:
`data/MOCKA_OVERVIEW.json` `data/MOCKA_TODO.json` `data/lever_essence.json` `data/events_latest.json`。
`git add` はこの allowlist を明示指定(`git add -A` 不使用)。

---

## 7. Runtime構造 まとめ図 (Confirmed な接続のみ)

```
[外部AI: GPT/Copilot/Gemini/Genspark/Perplexity]
        |  HTTP + X-MoCKA-Key
        v
  gateway.py :5010  (/api/v1/*)
        |
        |                [MCP Client (Claude等)]
        |                       |  MCP / HTTP /agent/<tool>
        |                       v
        |                mocka_mcp_server.py :5002  (23 tools)
        |                       |
        |                       |  POST http://localhost:5000/api/gate/event
        v                       v
              app.py :5000  (109 routes, 11 blueprints)
                    |
        +-----------+-----------+------------------+
        |           |           |                  |
  phi_os.event_gate |     interface/* bp     relay.relay_kernel (lazy)
        |           |                              mcp.mcp_router (lazy)
        v           v
   data/mocka_events.db  (events / event_signatures / human_gate_events / ...)
        |
        |  export_for_cloudflare.py + sync_watch.py (600s周期, allowlist 4ファイル)
        v
   git main -> origin (自動push)


[別プロセス・上記経路と本調査で接続未確認]
  mocka_caliber_server.py :5679   mocka_runtime_b.exe :5003
  living_room/hub.py :8765        app.py :8750
```

**Unknown(本調査で接続関係を確認できなかったもの)**:
- `:5679` caliber server と `:5000`/`:5002` の呼出関係
- `:5003` Runtime B(Go実装)がどの経路から書き込み/読み出しされるか
- `:8765` living_room hub(`dry_run:true` で稼働中)の役割と上流/下流
- `:6379` memurai(Redis互換)の利用主体

---

## 8. 本調査で確認できなかった事項 (Unknown)

1. 動的import・サブプロセス経由の依存関係(静的grep範囲外)
2. `event_signatures` ハッシュ連鎖の実際の整合性(検証未実行)
3. `archive/`(1,515 .py)の内容と現行経路との関係
4. `runtime/`(218 .py, civilization_* 系)の稼働状態と呼出元
5. 8750 プロセスのファイル実体
6. `workshop/` 各プロジェクトの稼働状態(`phi-os` 等はポート未検出だが、ライブラリとして常駐しない可能性がある)

---

## Knowledge Lineage

**Document:** JARVIS_ARCHITECTURE_CURRENT.md
**Status:** INVESTIGATION
**Created:** 2026-08-04
**Origin:** JARVIS Phase 0 : Current State Assessment(Investigation 1: Architecture Inventory)
**Evidence Sources:** 稼働プロセス実測(`Get-NetTCPConnection` / `Win32_Process` / HTTP probe)、
`data/mocka_events.db`(sqlite直読)、`data/decisions/decision_ledger.jsonl`、`data/MOCKA_TODO.json`、
`app.py`、`mocka_mcp_server.py`、`gateway/gateway.py`、`structural/execution_governance.py`、
`governance/mocka_git_safe_commit.py`、`PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py`、git log/status
**Affected Components:** なし(調査のみ、変更なし)
**Revision History:**
- R1(2026-08-04): 新規作成。実装・Decision Ledger登録なし。
