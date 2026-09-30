# PHI-OS Validator を通過した既存Event生成経路の調査報告

**調査期間**: 2026-09-28  
**対象**: MoCKA内で PHI-OS `validate()` を実際に通過しているpayload生成箇所  
**禁止条件**: コード変更・validator修正・新schema設計・mock payload

---

## A. VALID_PAYLOAD_EXAMPLE（一次データ）

### 1. 公式テストケース（phi_os/tests/test_event_gate.py:74-88）

```python
def valid_payload(**overrides):
    base = {
        'who_actor':       'Claude-sonnet-4-6',
        'who_role':        'executor',
        'who_session':     'SESSION_20260616_091900',
        'what_type':       'file_write',
        'what_title':      'PHI-OS GATE Phase2 test',
        'where_path':      'C:/Users/sirok/MoCKA/phi_os/event_gate.py',
        'where_component': 'phi_os.event_gate',
        'why_purpose':     'PHI-OS GATE Phase 2 pytestによる動作確認',
        'how_trigger':     'pytest / INSTRUCTION_PHI_OS_GATE_v1',
        'after_state':     'created',
    }
    base.update(overrides)
    return base
```

**特徴**: 最小セット（before_state省略、after_stateのみ）  
**test_happy_path()**: 201 + event_id返却確認済み

---

### 2. mocka_mcp_server.py: Governance Block記録 (L299-313)

```python
gate_payload = {
    "who_actor":       _DEFAULT_ACTOR,  # "Claude-code-sonnet-4-6"
    "who_role":        "governance",
    "who_session":     SESSION_ID,      # "SESSION_YYYYMMDD_HHMMSS"
    "what_type":       "governance_block",
    "what_title":      f"[GOVERNANCE_BLOCK] {tool_name}",
    "where_path":      "governance_pipeline.py",
    "where_component": "ba04_execution_gate",
    "why_purpose":     "Authority Decision Enforcement",
    "how_trigger":     "before_tool() BLOCK",
    "after_state":     "Execution BLOCKED",
    "description":     desc,
    "tags":            f"governance_block,ba04,{tool_name},{decision_reason}",
    "request_id":      req_id,
}
```

**経路**: POST → `requests.post(GATE_URL, json=gate_payload, timeout=5)` (L316)  
**フォールバック**: `process_event(gate_payload, event_source="direct_allowed:recovery")` (L328)  
**成功条件**: `r.status_code == 201` (L317)

---

### 3. mocka_mcp_server.py: mocka_write_event (L857-871)

```python
gate_payload = {
    "who_actor":       _actor,  # "Claude-code-sonnet-4-6" or user-supplied
    "who_role":        "executor",
    "who_session":     SESSION_ID,
    "what_type":       "claude_mcp",
    "what_title":      _title,  # args["title"]
    "where_path":      "mocka_mcp_server.py",
    "where_component": "mcp_caliber",
    "why_purpose":     args.get("why_purpose", "") or _desc[:80] or _title,
    "how_trigger":     args.get("how_trigger", "") or "mcp_tool_call",
    "after_state":     _desc[:200] or _title,
    "description":     _desc,  # args["description"]
    "tags":            args.get("tags", ""),
    "request_id":      req_id,
}
```

**入力検証** (L850-854):
- `_title`: required (空でない)
- `_desc`: required (空でない)
- `_actor_raw`: required (空でない) → legacy補填 (L856)

**経路**: POST → `requests.post(GATE_URL, json=gate_payload, timeout=5)` (L873)  
**フォールバック**: `process_event(gate_payload, event_source="direct_allowed:recovery")` (L899)  
**成功条件**: `r.status_code == 201` (L874)

---

### 4. mocka_mcp_server.py: mocka_decision_write Companion Event (L1185-1198)

```python
gate_payload = {
    "who_actor":       args.get("approved_by", _DEFAULT_ACTOR),
    "who_role":        "executor",
    "who_session":     SESSION_ID,
    "what_type":       "claude_mcp",
    "what_title":      f"[DECISION_MADE] {decision_id}: {title}",
    "where_path":      "mocka_mcp_server.py",
    "where_component": "mcp_caliber",
    "why_purpose":     rationale[:80] or title,
    "how_trigger":     "mcp_tool_call",
    "after_state":     decision[:200] or title,
    "description":     f"decision_id={decision_id}\ncontext={context}\ndecision={decision}\nrationale={rationale}\nimpact={impact}",
    "tags":            f"decision_ledger,{decision_id},{status}",
}
```

**経路**: POST → `requests.post(GATE_URL, json=gate_payload, timeout=5)` (L1199)  
**成功条件**: `r.status_code == 201` (L1200)

---

### 5. runtime/action_executor.py: Action Result Record (L146-161)

```python
event_payload = {
    "who_actor": "runtime_executor",
    "who_session": session_id,
    "what_type": "audit",
    "where_path": "runtime/action_executor.py",
    "where_component": "runtime",
    "why_purpose": f"Execute {step}: record result",
    "how_trigger": "execute_action_gate",
    "before_state": "pending",
    "after_state": f"status={status};reason={reason}",
    "when_ts": now,
    "title": f"ACTION: {step}",
    "short_summary": f"Action: {status}",
    "free_note": "|".join(free_note_parts),
    "request_id": action_id,
}
```

**経路**: Direct call → `gate_process_event(event_payload, event_source="direct_allowed:recovery")` (L163)  
**成功検証** (L164-165): `event_result.get("status") == "ok"`

---

## B. PAYLOAD_GENERATOR（生成責任主体）

| 生成者 | ファイル | 関数 | 呼出経路 | payload用途 |
|--------|---------|------|---------|-----------|
| Authority Enforcement | mocka_mcp_server.py | `_record_governance_block()` | HTTP POST | governance_block記録 |
| MCP Tool Interface | mocka_mcp_server.py | mocka_write_event handler | HTTP POST | claude_mcp イベント |
| Decision Manager | mocka_mcp_server.py | mocka_decision_write handler | HTTP POST | decision companion event |
| Runtime Executor | runtime/action_executor.py | `execute_action()` | Direct call | audit記録 |

---

## C. PHI_OS_CONTRACT（validate()要求仕様）

### 必須フィールド（8個）

| フィールド | 型 | 形式/値 | 由来 |
|-----------|-----|--------|------|
| `who_actor` | str | 例: "Claude-code-sonnet-4-6", "runtime_executor" | gate_validator.py L12-14: REJECT-01 |
| `who_role` | str | "executor", "governance", "auditor", "automation" | gate_schema.py L22 |
| `who_session` | str | "SESSION_YYYYMMDD_HHMMSS" | gate_validator.py L17-18: REJECT-02 |
| `what_type` | str | "file_write", "file_delete", "design", "git_commit", "git_push", "test_run", "deployment", "user_voice", "handshake", "audit", "incident", "todo_update", "governance_block", "claude_mcp" | gate_schema.py L8-12: REJECT-06 |
| `what_title` | str | 変更の一行要約 | gate_schema.py L25 |
| `where_path` | str | 絶対パス or URL | gate_validator.py L29: REJECT-05 |
| `where_component` | str | モジュール名 | gate_validator.py L44: REJECT-08 |
| `why_purpose` | str | 10文字以上必須 | gate_validator.py L21: REJECT-03 |

### Replay用フィールド（いずれか1つ必須）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `before_state` | str | 変更前状態（optional） |
| `after_state` | str | 変更後状態（optional） |
| `before_hash` | str | 変更前hash（optional） |
| `after_hash` | str | 変更後hash（optional） |

**要件**: `(before_state or before_hash) or (after_state or after_hash)` 必須  
**参考**: gate_validator.py L37-41: REJECT-07

### 追加フィールド（任意）

| フィールド | 型 | 説明 | 用例 |
|-----------|-----|------|------|
| `how_trigger` | str | 誰の指示か/何がトリガーか | "before_tool() BLOCK", "mcp_tool_call", "execute_action_gate" |
| `description` | str | 自由記述 | イベント詳細 |
| `tags` | str | タグリスト | "governance_block,ba04,tool_name" |
| `request_id` | str | 要求ID | action_id, req_id等 |
| `when_ts` | str | ISO8601 timestamp | 自動生成される場合が多い |

---

## D. REUSABLE_PATH（adapter_gpt.py再利用可能性）

### 結論: **部分的に再利用可能**

#### 再利用可能な部分

1. **when_ts自動生成**  
   `event_gate.py:131` で `datetime.now(timezone.utc).isoformat()` として自動生成される  
   adapter_gpt.py も同じ生成方式なため再利用可 (L69)

2. **event_id自動生成**  
   `event_gate.py:130` で `_next_event_id()` で生成される  
   adapter_gpt.py の nonce + timestamp 方式より優先

3. **request_id フィールド**  
   adapter_gpt.py の `uuid.uuid4()` を直接渡せる

#### 再利用不可能な部分

adapter_gpt.py のpayload構造全体が異なる：

| adapter_gpt.py | PHI-OS期待 | 不一致 |
|--------------|-----------|--------|
| `title` | `what_title` | フィールド名異なる |
| `description` | `description` | 一致 ✓ |
| `tags` (array) | `tags` (string) | 型異なる |
| `actor` (object) | 分解必要 | - |
| ├─ `vendor` | ― | 不要 |
| ├─ `model` | ― | 不要（who_actorで統合） |
| ├─ `runtime` | ― | 不要 |
| ├─ `source` | ― | 不要 |
| `timestamp` | `when_ts` | フィールド名異なる |
| `nonce` | ― | 不要 |
| ― | `who_actor` | **必須・生成ロジック必要** |
| ― | `who_role` | **必須・生成ロジック必要** |
| ― | `who_session` | **必須・SESSION_IDから取得可** |
| ― | `what_type` | **必須・adapter用に"claude_mcp"固定可** |
| ― | `where_path` | **必須・"gateway/adapter_gpt.py"固定可** |
| ― | `where_component` | **必須・"gpt_adapter"固定可** |
| ― | `why_purpose` | **必須・descriptionから派生可** |
| ― | `how_trigger` | **必須・"gpt_function_call"固定可** |
| ― | `after_state` | **必須（Replay）・"recorded"固定可** |
| ― | `before_hash`/`after_hash` | 提供可能但し計算コスト |

---

## E. MINIMAL_CONNECTION_POINT（修正候補）

### 修正対象ファイル

**gateway/adapter_gpt.py**

### 修正対象関数

`handle_function_call()` (L61-101)

### 修正箇所

**Line 92-101** の HTTP POST部分

### 修正理由

**現状**: adapter が gateway の旧schema で PHI-OS を呼び出している  
**必要**: adapter の payload を PHI-OS 5W1H schema に変換してから POST

### 最小修正方針

1. Line 73-86 のpayloadを **そのまま保持**（既存フィールド）
2. Line 92-93 で POST 直前に payload変換層を挿入
3. PHI-OS期待フィールドのみ新規生成（Session ID、role、type等）
4. フォールバック経路も同一payload で `process_event()` 呼び出し

### 変換マッピング（候補）

```
adapter_gpt.py → PHI-OS Event Gate

title              → what_title
description        → description
tags               → tags (stringify)
timestamp          → when_ts
request_id         → request_id
nonce              → free_note (metadata)

[新規追加]
who_actor:         "Claude-gpt-" + model (e.g., "Claude-gpt-4") or _DEFAULT_ACTOR
who_role:          "executor"
who_session:       SESSION_ID (mocka_mcp_server.py:88から取得)
what_type:         "claude_mcp"
where_path:        "gateway/adapter_gpt.py"
where_component:   "gpt_adapter"
why_purpose:       description[:80] or title
how_trigger:       "gpt_function_call"
after_state:       "recorded" or "event_created"
```

---

## F. EVIDENCE（一次コード証拠）

### 参照ファイル一覧

```
phi_os/gate_schema.py                   (L8-40)  — Event dataclass定義
phi_os/gate_validator.py               (L8-47)  — validate()仕様
phi_os/event_gate.py                   (L116-146)—process_event()実装
phi_os/tests/test_event_gate.py        (L74-88) — 公式テスト valid_payload
mocka_mcp_server.py                    (L87-89) — GATE_URL, SESSION_ID, _DEFAULT_ACTOR
mocka_mcp_server.py                    (L299-313)—_record_governance_block() example
mocka_mcp_server.py                    (L857-871)—mocka_write_event example
mocka_mcp_server.py                    (L1185-1198)—mocka_decision_write example
runtime/action_executor.py             (L146-161)—audit event example
```

### 実行トレース（mocka_write_event）

```
User call: mocka_write_event(title=..., description=..., tags=...)
  ↓
mocka_mcp_server.py:810-899 handler
  ↓
Validation (L850-854)
  ↓
gate_payload construction (L857-871)
  ↓
HTTP POST (L873) or process_event fallback (L899)
  ↓
phi_os/event_gate.py:receive_event()
  ↓
phi_os/event_gate.py:process_event(payload, event_source='live')
  ↓
validate(payload) → errors list or proceed
  ↓
_write(payload) → SQLite insert
  ↓
Return: {"status": "ok", "event_id": ...}
```

---

## 結論

PHI-OS の validator を通過している既存payload構造は **完全に一貫** している。  
すべての例が同一の5W1H schema（who/what/where/when/why/how）に従っている。

adapter_gpt.py の修正は、この既存schema に **化け直す** ことで解決可能。  
新しいschemaを発明する必要はない。
