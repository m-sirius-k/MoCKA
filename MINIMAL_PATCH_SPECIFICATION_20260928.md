# adapter_gpt.py → PHI-OS 最小パッチ仕様書

**作成日**: 2026-09-28  
**対象**: gateway/adapter_gpt.py の handle_function_call()  
**目的**: PHI-OS 5W1H Event Contract への最小変更対応  
**制約**: コード変更禁止（仕様確定のみ）

---

## I. WHO（行為者・セッション）

### 1.1 who_actor

**現在**: adapter は `actor.model` を "GPT"/"gemini" 等で受け取る

**必要な値**: PHI-OS expects "Claude-sonnet-4-6" 形式  
**例**: "Claude-gpt-4", "Claude-gemini-2.0", "Claude-perplexity-sonar"

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| who_actor | f"Claude-{model.lower()}" | handle_function_call(model=...) | NEW_VALUE_REQUIRED |

**根拠**:
- mocka_mcp_server.py:89 → _DEFAULT_ACTOR = "Claude-code-sonnet-4-6"
- mocka_mcp_server.py:856 → legacy value補填ロジック (Claude/claude → _DEFAULT_ACTOR)
- runtime/action_executor.py:147 → "runtime_executor" (context-specific)
- adapter_gpt.py:70-72 → model parameter available

**実装形式**:
```python
# adapter_gpt.py L70-72 の model パラメータから構築
model_name = model.lower() if model else "gpt"  # default
who_actor = f"Claude-{model_name}"
```

---

### 1.2 who_role

**必要な値**: "executor" | "governance" | "auditor" | "automation"  
**adapter_gpt.py の役割**: Function Call event recording → **executor**

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| who_role | "executor" | adapter context | NEW_VALUE_REQUIRED |

**根拠**:
- mocka_mcp_server.py:859 → mocka_write_event: who_role="executor"
- mocka_mcp_server.py:301 → governance block: who_role="governance"
- runtime/action_executor.py:148 → (implicit executor role)
- adapter_gpt.py → GPT Function Call execution = executor role

**実装形式**:
```python
who_role = "executor"  # Fixed for adapter events
```

---

### 1.3 who_session

**必要な値**: "SESSION_YYYYMMDD_HHMMSS" 形式（REJECT-02）

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| who_session | "SESSION_" + datetime now | adapter startup context | NEW_VALUE_REQUIRED |

**根拠**:
- mocka_mcp_server.py:88 → SESSION_ID = "SESSION_" + datetime.now().strftime("%Y%m%d_%H%M%S")
- gateway.py:35 imports adapter_gpt → separate process, separate session
- adapter_gpt.py can generate own session_id at module load time

**実装形式** (module level):
```python
import datetime

# At module load time (like mocka_mcp_server.py:88)
_SESSION_ID = "SESSION_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def handle_function_call(...):
    # Use _SESSION_ID in payload
    who_session = _SESSION_ID
```

---

## II. WHAT（何を変更したか）

### 2.1 what_type

**必要な値**: Enum from gate_schema.py:8-12  
**適切な値**: "claude_mcp" (MCP tool event type)

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| what_type | "claude_mcp" | adapter context | NEW_VALUE_REQUIRED |

**根拠**:
- gate_schema.py:8-12 → ALLOWED_WHAT_TYPES list includes "claude_mcp"
- mocka_mcp_server.py:861 → mocka_write_event uses what_type="claude_mcp"
- mocka_mcp_server.py:1189 → mocka_decision_write companion also uses "claude_mcp"
- adapter events are MCP-tool-like events (GPT API recording)

**実装形式**:
```python
what_type = "claude_mcp"  # Fixed for adapter events
```

---

### 2.2 what_title

**現在**: adapter has `title` from GPT

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| what_title | title (parameter) | handle_function_call(title=...) | REUSE_AS_IS |

**根拠**:
- adapter_gpt.py:70 → title parameter
- adapter_gpt.py:83 → payload["title"] = title
- mocka_mcp_server.py:862 → what_title: _title (direct mapping)
- phi_os/tests/test_event_gate.py:80 → what_title: '...'

**実装形式**:
```python
what_title = title  # Direct pass-through
```

---

## III. WHERE（どこに影響するか）

### 3.1 where_path

**必要な値**: Absolute path or URL  
**adapter context**: Source code path of adapter

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| where_path | "gateway/adapter_gpt.py" | adapter source location | NEW_VALUE_REQUIRED |

**根拠**:
- mocka_mcp_server.py:863 → where_path: "mocka_mcp_server.py"
- mocka_mcp_server.py:305 → where_path: "governance_pipeline.py"
- runtime/action_executor.py:150 → where_path: "runtime/action_executor.py"
- adapter_gpt.py is the primary actor

**実装形式**:
```python
where_path = "gateway/adapter_gpt.py"  # Fixed
```

---

### 3.2 where_component

**必要な値**: Module name  
**adapter context**: Adapter module name

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| where_component | "gpt_adapter" | adapter module role | NEW_VALUE_REQUIRED |

**根拠**:
- mocka_mcp_server.py:864 → where_component: "mcp_caliber"
- mocka_mcp_server.py:306 → where_component: "ba04_execution_gate"
- runtime/action_executor.py:151 → where_component: "runtime"
- adapter_gpt.py is function calling adapter

**実装形式**:
```python
where_component = "gpt_adapter"  # Or "ai_adapter" depending on naming convention
```

---

## IV. WHY（なぜ、どの目的で）

### 4.1 why_purpose

**現在**: adapter has `description` from GPT

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| why_purpose | description[:80] or title | handle_function_call(description=...) | DERIVE_FROM_EXISTING |

**制約**: 10文字以上必須（REJECT-03）

**根拠**:
- mocka_mcp_server.py:865 → why_purpose: args.get("why_purpose") or _desc[:80] or _title
- mocka_mcp_server.py:307 → why_purpose: "Authority Decision Enforcement" (fixed meaningful)
- runtime/action_executor.py:152 → why_purpose: f"Execute {step}: record result"
- adapter_gpt.py:84 → description parameter available

**実装形式**:
```python
why_purpose_candidate = description if len(description) >= 10 else None
why_purpose = why_purpose_candidate or title
if len(why_purpose) < 10:
    why_purpose = f"GPT {model}: {why_purpose[:60]}"  # Ensure 10+ chars
```

---

### 4.2 how_trigger

**必要な値**: Who/what triggered this event  
**adapter context**: Function call mechanism

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| how_trigger | "gpt_function_call" or f"function_call_{model}" | adapter context | NEW_VALUE_REQUIRED |

**根拠**:
- mocka_mcp_server.py:866 → how_trigger: args.get("how_trigger") or "mcp_tool_call"
- mocka_mcp_server.py:308 → how_trigger: "before_tool() BLOCK"
- runtime/action_executor.py:153 → how_trigger: "execute_action_gate"
- adapter is responding to GPT function call

**実装形式**:
```python
# Option A: Simple
how_trigger = "gpt_function_call"

# Option B: Model-specific
how_trigger = f"{model.lower()}_function_call"
```

---

## V. WHEN（いつ）

### 5.1 when_ts (via event_gate auto-generation)

**Policy**: event_gate.py:131 が自動生成  
**adapter role**: Provide nothing or override if needed

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| when_ts | (auto) datetime.now(UTC) | process_event() | DO_NOT_USE |

**根拠**:
- event_gate.py:131 → payload['when_ts'] = datetime.now(timezone.utc).isoformat()
- adapter_gpt.py:78 → now = datetime.now(timezone.utc).isoformat() (optional)
- Should NOT be in adapter payload, PHI-OS will set it

**実装形式**:
```python
# adapter_gpt.py should NOT include when_ts in gate_payload
# Leave it to process_event() to auto-generate
```

---

## VI. REPLAY保証（before/after）

### 6.1 before_state / after_state

**必要**: いずれかが必須（REJECT-07）

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| after_state | "recorded" or "event_created" | adapter semantic | NEW_VALUE_REQUIRED |
| before_state | (omit) | adapter context | DO_NOT_USE |

**根拠**:
- mocka_mcp_server.py:309 → after_state: "Execution BLOCKED" (meaningful state)
- mocka_mcp_server.py:867 → after_state: _desc[:200] or _title
- runtime/action_executor.py:154-155 → before_state: "pending", after_state: f"status=...;reason=..."
- adapter doesn't track before state, only records event outcome

**実装形式**:
```python
# Simple approach
after_state = "recorded"

# Or more descriptive
after_state = f"event_recorded_{len(tags)}_tags"
```

---

## VII. メタデータ（追加フィールド）

### 7.1 description

**現在**: adapter has `description` parameter  
**PHI-OS**: `description` field (optional)

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| description | description (parameter) | handle_function_call(description=...) | REUSE_AS_IS |

**根拠**:
- gate_schema.py:38 → description: str = ''
- mocka_mcp_server.py:868 → description: _desc
- adapter_gpt.py:84 → description parameter available

---

### 7.2 tags

**現在**: adapter has `tags: list` parameter  
**PHI-OS**: `tags` field (string, not array)

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| tags | ",".join(tags) or "" | handle_function_call(tags=[...]) | DERIVE_FROM_EXISTING |

**根拠**:
- gate_schema.py:39 → tags: str = ''
- mocka_mcp_server.py:869 → tags: args.get("tags", "")
- adapter_gpt.py:77,85 → tags list (need stringify)
- event_gate.py:67 → tags처리: filter(None, [...]) 

**実装形式**:
```python
tags_str = ",".join(tags) if tags else ""
```

---

### 7.3 request_id

**現在**: adapter generates uuid  
**PHI-OS**: `request_id` field (optional metadata)

| フィールド | 値 | 由来 | 分類 |
|-----------|-----|------|------|
| request_id | str(uuid.uuid4()) | adapter generation | REUSE_AS_IS |

**根拠**:
- adapter_gpt.py:80 → rid = str(uuid.uuid4())
- mocka_mcp_server.py:870 → request_id: req_id
- event_gate.py:75 → request_id: payload.get("request_id")
- Useful for tracing

---

## VIII. 現在の adapter_gpt.py との比較

### 8.1 adapter_gpt.py に既に存在する値

```python
# adapter_gpt.py:70-95 で生成されている
title        → what_title ✓ (REUSE_AS_IS)
description  → description + why_purpose ✓ (REUSE_AS_IS + DERIVE)
tags         → tags (stringify needed) ~ (DERIVE_FROM_EXISTING)
model        → who_actor prefix ✓ (DERIVE)
runtime      → (not used in 5W1H)
source       → (not used in 5W1H)
request_id   → request_id ✓ (REUSE_AS_IS)
timestamp    → when_ts (process_event handles)
nonce        → (not used in 5W1H)
```

### 8.2 adapter_gpt.py に新たに追加が必要な値

```python
who_actor           ← model から新規生成
who_role            ← "executor" 固定
who_session         ← モジュール起動時に生成
what_type           ← "claude_mcp" 固定
where_path          ← "gateway/adapter_gpt.py" 固定
where_component     ← "gpt_adapter" 固定
why_purpose         ← description を10字以上に調整
how_trigger         ← "gpt_function_call" 固定
after_state         ← "recorded" 固定
```

---

## IX. MINIMAL_PATCH_BOUNDARY

### 9.1 修正対象コード

**ファイル**: gateway/adapter_gpt.py  
**関数**: handle_function_call()  
**行**: L82-99 (payload構築とPOST)

### 9.2 最小パッチアプローチ

**Option A: 最小化（payload直前の変換層）**

```python
def handle_function_call(title: str, description: str, tags: list = None,
                         model: str = "GPT", runtime: str = "ChatGPT",
                         source: str = "Orchestra") -> dict:
    # ... 既存コード L77-95 ...
    
    payload = { ... }  # 既存構造保持
    
    # --- 最小パッチ: POST直前に PHI-OS payload へ変換
    gate_payload = _transform_to_phi_os_payload(payload, model, title, description, tags)
    
    try:
        r = requests.post(
            "http://localhost:5000/api/gate/event",  # c9effe8で変更済み
            json=gate_payload,  # 変換済みpayload
            headers={"X-MoCKA-Key": MOCKA_API_KEY, "Content-Type": "application/json"},
            timeout=5,
        )
        ...
```

**Option B: 直接埋め込み（最小行数）**

```python
# No new function, construct gate_payload directly in handle_function_call()
gate_payload = {
    "who_actor": f"Claude-{model.lower()}",
    "who_role": "executor",
    "who_session": _SESSION_ID,
    "what_type": "claude_mcp",
    "what_title": title,
    "where_path": "gateway/adapter_gpt.py",
    "where_component": "gpt_adapter",
    "why_purpose": (description if len(description) >= 10 else "") or title,
    "how_trigger": "gpt_function_call",
    "after_state": "recorded",
    "description": description,
    "tags": ",".join(tags) if tags else "",
    "request_id": rid,
}
```

### 9.3 モジュールレベル初期化

```python
# At module top level (after imports, before handle_function_call definition)
import datetime as _dt

_SESSION_ID = "SESSION_" + _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
```

---

## X. EVIDENCE（コード証拠一覧）

### モジュール起動時SESSION_ID生成
- **mocka_mcp_server.py:88** → SESSION_ID = "SESSION_" + datetime.now().strftime("%Y%m%d_%H%M%S")

### who_actor例
- **mocka_mcp_server.py:89** → _DEFAULT_ACTOR = "Claude-code-sonnet-4-6"
- **mocka_mcp_server.py:300** → who_actor: _DEFAULT_ACTOR
- **mocka_mcp_server.py:858** → who_actor: _actor (補填ロジック)
- **runtime/action_executor.py:147** → who_actor: "runtime_executor"

### who_role例
- **mocka_mcp_server.py:859** → who_role: "executor"
- **mocka_mcp_server.py:301** → who_role: "governance"

### who_session形式
- **phi_os/gate_validator.py:17** → who_session.startswith('SESSION_')
- **phi_os/tests/test_event_gate.py:78** → who_session: 'SESSION_20260616_091900'

### what_type enum
- **gate_schema.py:8-12** → ALLOWED_WHAT_TYPES list
- **mocka_mcp_server.py:861** → what_type: "claude_mcp"
- **mocka_mcp_server.py:1189** → what_type: "claude_mcp" (companion event)

### what_title
- **mocka_mcp_server.py:862** → what_title: _title
- **phi_os/tests/test_event_gate.py:80** → what_title: '...'

### where_path
- **mocka_mcp_server.py:863** → where_path: "mocka_mcp_server.py"
- **runtime/action_executor.py:150** → where_path: "runtime/action_executor.py"

### where_component
- **mocka_mcp_server.py:864** → where_component: "mcp_caliber"
- **runtime/action_executor.py:151** → where_component: "runtime"

### why_purpose
- **mocka_mcp_server.py:865** → why_purpose: args.get("why_purpose") or _desc[:80] or _title
- **phi_os/gate_validator.py:21** → len(why_purpose) >= 10 必須
- **runtime/action_executor.py:152** → why_purpose: f"Execute {step}: record result"

### how_trigger
- **mocka_mcp_server.py:866** → how_trigger: args.get("how_trigger") or "mcp_tool_call"
- **runtime/action_executor.py:153** → how_trigger: "execute_action_gate"

### after_state
- **mocka_mcp_server.py:867** → after_state: _desc[:200] or _title
- **runtime/action_executor.py:155** → after_state: f"status={status};reason={reason}"

### Replay要件
- **phi_os/gate_validator.py:37-41** → before/after どちらか必須
- **runtime/action_executor.py:154** → before_state: "pending"

### tags string化
- **mocka_mcp_server.py:869** → tags: args.get("tags", "")
- **event_gate.py:67** → tags処理: filter(None, [...])

---

## XI. 確定項目サマリ

| 項目 | 分類 | 値/源 | 根拠 |
|------|------|-------|------|
| **WHO** | | | |
| who_actor | DERIVE_FROM_EXISTING | f"Claude-{model.lower()}" | mocka_mcp_server.py:89, :856 |
| who_role | NEW_VALUE_REQUIRED | "executor" | mocka_mcp_server.py:859 |
| who_session | NEW_VALUE_REQUIRED | _SESSION_ID (module init) | mocka_mcp_server.py:88 |
| **WHAT** | | | |
| what_type | NEW_VALUE_REQUIRED | "claude_mcp" | gate_schema.py:12, mocka_mcp:861 |
| what_title | REUSE_AS_IS | title parameter | adapter_gpt.py:70 |
| **WHERE** | | | |
| where_path | NEW_VALUE_REQUIRED | "gateway/adapter_gpt.py" | mocka_mcp:863 |
| where_component | NEW_VALUE_REQUIRED | "gpt_adapter" | mocka_mcp:864 |
| **WHY/HOW** | | | |
| why_purpose | DERIVE_FROM_EXISTING | description[:80] or title | mocka_mcp:865 |
| how_trigger | NEW_VALUE_REQUIRED | "gpt_function_call" | mocka_mcp:866 |
| **REPLAY** | | | |
| after_state | NEW_VALUE_REQUIRED | "recorded" | mocka_mcp:867, action_exec:155 |
| before_state | DO_NOT_USE | (omit) | - |
| **META** | | | |
| description | REUSE_AS_IS | description parameter | adapter_gpt.py:84 |
| tags | DERIVE_FROM_EXISTING | ",".join(tags) | adapter_gpt.py:85 |
| request_id | REUSE_AS_IS | rid (uuid) | adapter_gpt.py:80 |
| when_ts | DO_NOT_USE | (process_event auto-gen) | event_gate.py:131 |

---

**仕様確定日**: 2026-09-28 UTC  
**コード変更**: 禁止（仕様書のみ）  
**次フェーズ**: 実装 → PHI-OS validator通過確認
