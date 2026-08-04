# JARVIS Phase 0 — Runtime Flow (Current State)

**Document:** JARVIS_RUNTIME_FLOW.md
**Status:** INVESTIGATION(現状記録のみ。設計・提案・改善案を含まない)
**調査日:** 2026-08-04
**実装変更:** なし

## 0. 本文書が記録するもの

「人間が依頼してから記録されるまで」の実際の経路を、コード本文とDB実測から復元する。
存在しない経路は「存在しない」と記録する。推測で線を引かない。

---

## 1. 制度上の唯一の保存経路 (Confirmed / コード本文の自己宣言)

`phi_os/event_gate.py:115` `process_event()` の docstring(原文):

> Unified Event Entry（Phase5-2.1）。
> Validation -> Gate Policy(event_source付与) -> Signature -> Hash Chain ->
> Integrity Registration -> DB Commit を一体で実行する唯一の保存経路。
> Flask route(/api/gate/event)とMCP server(mocka_write_event)のいずれの
> 呼び出し元からも、トランスポート(HTTP/インプロセス)を問わずこの関数を
> 経由しなければならない。**これ以外にevents保存を行う経路は制度上存在しない。**

`gateway/gateway.py:170` のコメント(原文):
> Phase5-1: 生SQL INSERT INTO events禁止 → Local Buffer経由でGateへ統一

**注記:** これは「制度としてそう宣言されている」ことの Confirmed であって、
「実際に他経路が存在しない」ことの証明ではない。全書込経路の網羅監査は本調査では **未実施**。

---

## 2. 実測された Runtime Flow(全体)

```
                          [ 人間 ]
                             |
        +--------------------+--------------------+
        |                                         |
   (経路A) MCP Client                        (経路B) 外部AI
   Claude / MCP対応クライアント          GPT / Copilot / Gemini /
        |                              Genspark / Perplexity
        | MCP または HTTP                        |
        | POST /agent/<tool_name>                | HTTP + X-MoCKA-Key
        v                                        v
  mocka_mcp_server.py :5002              gateway.py :5010
  (tools 23件)                           POST /api/v1/event
        |                                        |
        | 必須検証:                              | 必須検証: title 非空
        |  title / description / author          |  -> 400
        |  いずれか空 -> gate_rejected           |
        |                                        v
        | POST http://localhost:5000             interface/event_buffer.py
        |      /api/gate/event                   get_buffer().push()
        |      (GATE_URL, mocka_mcp_server.py:87)     |
        |                                        | BATCH_SIZE到達 or
        |                                        | FLUSH_INTERVAL経過
        |                                        | POST http://localhost:5000
        |                                        |      /api/gate/event/batch
        |                                        | 失敗時 -> fallbackへ永続化
        |                                        |          + exponential backoff再試行
        v                                        v
      +------------------------------------------------+
      |   app.py :5000  /  phi_os/event_gate.py         |
      |   gate_bp (app.py:80 で register_blueprint 済)   |
      +------------------------------------------------+
                             |
                             v
                    process_event(payload)
                             |
        1. validate(payload)  -- 失敗 -> {'status':'rejected'} / HTTP 422
        2. event_id 採番      -- _next_event_id()
        3. when_ts 補完       -- datetime.now(timezone.utc).isoformat()
        4. event_source 付与  -- 'live'
                             |
                             v
                        _write(payload)
                             |
        - GATEペイロード -> events スキーマ列へマッピング
        - channel_type = 'gate' に固定上書き
          (元のchannel_typeは free_note に orig_channel= として保存)
        - lifecycle_phase = 'in_operation' 固定
        - risk_level = 'normal' 固定
        - 空文字列 -> NULL 変換
        - INSERT OR IGNORE INTO events (...)
        - integrity.sign_event(conn, row)
            -> event_signatures (previous_hash / current_hash / algorithm)
        - UPDATE events SET trace_id=current_hash, related_event_id=previous_hash
                             |
                             v
                data/mocka_events.db
                  events (19,037行)
                  event_signatures (19,037行)
                             |
        +--------------------+---------------------+
        |                                          |
        v                                          v
  export_for_cloudflare.py                  監査・検証系
  + sync_watch.py (600秒周期)               audit_violations (22,539行)
  allowlist 4ファイルのみ git add           /audit/status /audit/seal
        |                                   /integrity/status
        v                                   verify_*.py / scripts/ledger/*
  mocka_git_safe_commit(push=True)
        |
        v
  git main -> origin (公開)
```

---

## 3. 経路A: MCP 経由(Confirmed / 実測)

### 3.1 入口

- `mocka_mcp_server.py`(port 5002, version 1.5.0)。tools 23件。
- 呼出方法は2系統(いずれも Confirmed):
  - MCP プロトコル(`/mcp`)
  - HTTP 直接(`/agent/<tool_name>`)— `governance/mocka_git_safe_commit.py` が
    `http://localhost:5002/agent/mocka_write_event` を実際に使用

### 3.2 `mocka_write_event` の処理(`mocka_mcp_server.py:666`〜)

```python
_title  = args.get("title", "").strip()
_desc   = args.get("description", "").strip()
_actor_raw = args.get("author", "").strip()
if not _title:      -> {"status":"gate_rejected","errors":["title is required (empty)"]}
if not _desc:       -> {"status":"gate_rejected","errors":["description is required (empty)"]}
if not _actor_raw:  -> {"status":"gate_rejected","errors":["author is required (empty)"]}
_actor = _DEFAULT_ACTOR if _actor_raw in ("Claude","claude") else _actor_raw
```

コード内コメントに、この検証が後から加えられた経緯が明記されている(原文):
> GL7-VALIDATION-MISSING-BUG是正: title/description/author はツール定義上 required …
> であるにもかかわらず、空文字が自動補填されvalidate()まで隠蔽されていた。
> フォールバックを「補完」から「検知して拒否」へ変更

### 3.3 Gate へ渡されるペイロード(固定値を含む)

```
who_actor       = <author>(レガシー値のみ正規化)
who_role        = "executor"          (固定)
who_session     = SESSION_ID
what_type       = "claude_mcp"        (固定)
what_title      = <title>
where_path      = "mocka_mcp_server.py"   (固定)
where_component = "mcp_caliber"           (固定)
why_purpose     = <why_purpose> or <desc先頭80字> or <title>
how_trigger     = <how_trigger> or "mcp_tool_call"
after_state     = <desc先頭200字> or <title>
description     = <description>
tags            = <tags>
```

→ この固定値の存在は、`events` の実測分布と整合する:
`what_type='claude_mcp'` **7,951件**、`channel_type='gate'` **7,041件**、
最新イベント `E20260804_581872629c8a6` の `where_component='mcp_caliber'`(実測)。

---

## 4. 経路B: 外部AI(GPT等)経由(Confirmed / 実測)

### 4.1 入口: `gateway.py` :5010

- 認証: `X-MoCKA-Key` ヘッダ必須。未付与のリクエストは **401**(`X-MoCKA-Key header missing`、実測)。
- `POST /api/v1/event` の処理(`gateway/gateway.py:142`〜):
  - `title` 必須(空なら 400)
  - `who_actor = "{vendor}/{model}"` 形式に整形
  - `ai_actor = actor.source`(Orchestra等)
  - `what_type = "gateway_event"`(固定)
  - `where_component = "gateway"`(固定)
  - `lifecycle_phase = "in_operation"`(固定)
  - タグ専用カラムがないため `free_note` へ格納
  - **生SQL INSERT は行わず** `get_buffer().push({...})` で Local Buffer に積む

### 4.2 Local Buffer(`interface/event_buffer.py`)

- `GATE_BATCH_URL = "http://localhost:5000/api/gate/event/batch"`
- flush 条件: キューが `BATCH_SIZE` に達した時、または `FLUSH_INTERVAL` 秒経過時
- 失敗時: fallback へ永続化し、次回 flush サイクルで再試行(exponential backoff)
- shutdown 時: `drain(timeout)` で可能な限り flush、残りは fallback へ永続化

### 4.3 read 経路

`gateway.py` の GET route(Confirmed、8件):
`/api/v1/context` `/api/v1/todo` `/api/v1/phase` `/api/v1/essence`
`/api/v1/last_event` `/api/v1/summary` `/api/v1/health`

---

## 5. 経路C: PHI-OS からの参照(Confirmed / コード実測)

`PlanningCaliber/workshop/phi-os/phios/phl/relay_client.py`:

```
MCP_URL        = "http://localhost:5002/mcp"
GATE_AUDIT_URL = "http://localhost:5000/api/gate/audit"
# read-only allowlist を強制
raise RelayError(f"refused: '{tool_name}' is not in the read-only allowlist")
```

→ **PHI-OS Core から MoCKA への経路は read-only であり、この経路では events を書き込めない。**

---

## 6. Ledger(Decision)への記録経路

Event(§2-4)とは **別経路** である(Confirmed)。

```
[人間] --(裁定)--> approved_by = "human_authority"
                        |
                        v
              mocka_decision_write (MCP tool, :5002)
              または /decision/approve, /decision/reject (app.py :5000)
                        |
                        v
        data/decisions/decision_ledger.jsonl   (206行, append-only)
        フィールド14: decision_id, title, context, alternatives, decision,
                      rationale, impact, related_events, related_documents,
                      approved_by, approved_at, supersedes, superseded_by, status
                        |
                        | related_events で events を参照
                        v
        data/mocka_events.db events
```

実測例(`DC_20260801_002`):
`approved_by = "human_authority"` / `approved_at = "2026-08-01T01:30:15Z"` / `status = "Active"` /
`related_events = ['E20260801_29957676217f1', 'E20260801_604460914d0d3', 'E20260801_870543941f74d']` /
`related_documents` に `docs/governance/decision_identity/HUMAN_GATE_DECISION_PACKAGE_v0.1.md` 等

**観測された品質事実:** この最新レコードの `context` / `alternatives` フィールドに文字化けが実在する。

**Decision Ledger は3ストアに分散している**(Confirmed):
`data/decisions/decision_ledger.jsonl`(206行、2026-08-01) /
`data/ise/decision_ledger.jsonl`(2026-06-12) /
`PlanningCaliber/workshop/phi-os/data/ise/decision_ledger.jsonl`(2026-07-29)。

---

## 7. Human Gate の経路(Confirmed / 分岐している)

```
[人間]
   |
   +---(経路1) governance/human_gate_cli.py
   |             from phi_os.human_gate import submit, approve, reject, get_state, list_pending
   |                      |
   |                      v
   |             human_gate_events テーブル (1,779行)
   |             STATES: PENDING / APPROVED / REJECTED / EXPIRED / CANCELED
   |             TRANSITIONS: submit{None} / approve{PENDING} / reject{PENDING} / expire{PENDING}
   |             永続ルール: stateは保存せず event のみ保存、state は event 列から再構築
   |
   +---(経路2) app.py :5000  POST /decision/approve, /decision/reject
   |
   +---(経路3) governance/mocka_git_safe_commit.py の Core System File 除外
   |             phi_os/ interface/ structural/ gateway/ + app.py, index.html,
   |             scripts/ledger/anchor_update.py, sync_watch.py
   |             -> 自動commit対象外。未コミットのまま人間承認待ちとして残す
   |
   +---(経路X) phi_os/human_gate.py の HTTP API  ★到達不能★
                 human_gate_bp が定義する 5 route
                 (/api/human_gate/{submit,approve,reject,status/<id>,pending})
                 -> app.py の register_blueprint 11件に human_gate_bp は含まれない(実測)
```

`phi_os/human_gate.py` 冒頭の宣言(原文):
> 基本原則: PHI-OSがHuman Gateの唯一の状態管理責務を持つ。
> GL7およびApp層はHuman Gate状態を保持しない(本モジュールが単一の真実)。

**観測事実:** この「単一の真実」の宣言に対し、実際には上記の経路1〜3 + `semantic/query_engine/human_gate.py` +
`governance/human_gate_continuity.py` が並存する。同一の裁定概念を指すかは **Unknown**。

`human_gate_events` の最新5件(実測): 2026-07-31T09:01:43Z `approve`(PENDING→APPROVED)、
2026-07-31T09:00:22Z `submit`、2026-07-08T01:16:45Z `submit`、2026-06-23 `submit`×2。

---

## 8. GL7(実行統制)の経路(Confirmed)

```
Task -> Grounding(GL1) -> Policy確認(GL1) -> Conflict検出
     -> Dry Run -> Approval(Human Gate) -> Execute -> Verify
        （structural/execution_governance.py docstring 記載の固定順序）
                             |
                             | _emit_gl7_event()
                             v
                phi_os.event_bus.append("GL7_EVENT", {...})
                    * pure event forwarding のみ
                    * 転送失敗しても GL7 自身の許可/拒否判定はブロックしない
                      (fail-soft。GL7自身は fail-closed 維持)
```

呼出元(Confirmed、6ファイル): `governance/seal_governance_gate.py`,
`governance/seal_governance_wrapper.py`, `structural/consensus.py`,
`structural/governance_pipeline.py`, `structural/knowledge_mass.py`, `structural/gl_integration_test.py`。

**`app.py` と `mocka_mcp_server.py` は GL7 を import していない**(実測)。
`mocka_mcp_server.py:495` に `"error": "GL7_EXECUTION_BLOCKED"` という文字列が存在するが、
GL7 モジュール自体の呼出ではない。

---

## 9. Audit / Publish への流出経路(Confirmed)

### 9.1 Audit

- `audit_violations`(22,539行 / `NEW` 6 / `RESOLVED_LEGACY_BULK_FIX` 22,533)。
- HTTP: `/audit/status` `/audit/seal` `/integrity/status` `/integrity/monitor` `/api/verification/verify`。
- MCP: `mocka_integrity_write` / `get` / `list`、`mocka_get_incidents`。
- 検出タイミング・トリガの実装は本調査では **未追跡(Unknown)**。

### 9.2 Publish(外部公開)

```
data/mocka_events.db 等
   |  export_for_cloudflare.py
   v
data/MOCKA_OVERVIEW.json / data/MOCKA_TODO.json /
data/lever_essence.json / data/events_latest.json   ← GIT_TARGETS(allowlist 4件)
   |  sync_watch.py (SYNC_INTERVAL = 600秒)
   |  git add <allowlist明示指定>  ※ git add -A は不使用
   |  mocka_git_safe_commit(paths=GIT_TARGETS, message='auto sync <ISO>', push=True)
   v
git main -> origin
```

稼働の実証(Confirmed): git log の直近5commitがすべて `auto sync <ISO8601>`。
HEAD = `adb661ddb` "auto sync 2026-08-04T05:05:49Z"。

---

## 10. ミッション提示フローとの対応

調査ミッションが例示した流れとの照合(**Confirmed / Unknown を明示**)。

| ミッション例示 | 実測された対応物 | 判定 |
|---|---|---|
| Human | 人間の依頼(MCPクライアント操作 / 外部AIへの指示 / CLI) | Confirmed |
| ↓ GPT | `gateway.py` :5010 + `adapter_gpt.py`(`X-MoCKA-Key` 必須) | Confirmed |
| ↓ HAB | **該当する実行時コンポーネントは存在しない** | **不在** |
| ↓ MoCKA | `app.py` :5000 → `phi_os/event_gate.py` `process_event()` → `_write()` | Confirmed |
| ↓ Ledger | `events` + `event_signatures`(自動) / `decision_ledger.jsonl`(人間裁定、別経路) | Confirmed |
| ↓ Audit | `audit_violations` / `/audit/*` / `verify_*` | Confirmed(トリガは Unknown) |

**"HAB" 段の不在について(範囲を明示):**
- HAB-A(Human Authority Boundary)は `docs/governance/mocka_hab_v1_contract.md` に **DRAFT** として定義されているが、
  実行時にイベントが通過する実装を発見できなかった。
- HAB-B(`semantic/query_engine/execution_orchestrator.py`、"HAB spine")はコードとして実在するが、
  `semantic/` パッケージ外部からの import は **0件** であり、上記フロー上にない。
- HAB-C(PHI-HAB)は構想メモ `ジャビス.md` にのみ存在し、実装を発見できなかった。
- 調査範囲: MoCKA repo 全体の import 静的解析(`archive/`・`venv/` 除外)+ 稼働プロセス実測 + `Desktop\aimd\`。
  動的import・サブプロセス経由の呼出は範囲外。

---

## 11. 実行時に存在するが本フローへの接続を確認できなかったプロセス (Unknown)

| プロセス | 実測応答 | 接続関係 |
|---|---|---|
| `mocka_caliber_server.py` :5679 | `{"keywords":77,"mode":"api_zero","threshold":0.6,"version":"v5"}` | app.py に `/caliber/*` route は存在するが、5000→5679 の実呼出は未検証 |
| `mocka_runtime_b.exe` :5003 | `{"name":"MoCKA Runtime B","runtime":"go","version":"1.0.0"}` | Unknown |
| `living_room/hub.py` :8765 | `{"hub":"living_room v0.1","db_events":19035,"db_ok":true,"dry_run":true}` | `db_events` が `events`(19,037)に近いが、参照先DBの同定は未実施 |
| `app.py` :8750 | 全プローブパス 404 | プロセス実体未同定(`DC_20260713_001` により SEO-OS Command Center とされる = Hypothesis) |
| `memurai.exe` :6379 | Redis互換 | 利用主体不明 |

---

## 12. 本調査で未実施の検証 (Unknown)

1. `process_event()` を経由しない events 書込経路が実在しないことの網羅監査
2. `event_signatures` ハッシュ連鎖の全走査整合性検証
3. `audit_violations` の検出トリガ実装
4. `/api/gate/audit` の応答内容(PHI-OS read経路の実応答)
5. 外部公開URL(ngrok / cloudflare / gateway.nsjp.org)の現在の到達性
6. Local Buffer の fallback ファイルに未送信イベントが滞留しているか

---

## Knowledge Lineage

**Document:** JARVIS_RUNTIME_FLOW.md
**Status:** INVESTIGATION
**Created:** 2026-08-04
**Origin:** JARVIS Phase 0 : Current State Assessment(Investigation 5: Runtime Flow)
**Parent Documents:** JARVIS_ARCHITECTURE_CURRENT.md / JARVIS_CAPABILITY_INVENTORY.md / JARVIS_BOUNDARY_ANALYSIS.md / JARVIS_GAP_ANALYSIS.md
**Evidence Sources:** `phi_os/event_gate.py`(`process_event` / `_write` / route定義)、
`mocka_mcp_server.py`(GATE_URL / `mocka_write_event` handler)、`gateway/gateway.py`(`post_event`)、
`interface/event_buffer.py`(`GATE_BATCH_URL` / flush / fallback)、`structural/execution_governance.py`、
`phi_os/human_gate.py`、`app.py`(`register_blueprint` 11件)、
`governance/mocka_git_safe_commit.py`、`PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py`、
`PlanningCaliber/workshop/phi-os/phios/phl/relay_client.py`、
`data/mocka_events.db` 実測、`data/decisions/decision_ledger.jsonl` 実測、稼働プロセス・HTTP実測
**Affected Components:** なし(調査のみ、変更なし)
**Revision History:**
- R1(2026-08-04): 新規作成。実装・Decision Ledger登録なし。
