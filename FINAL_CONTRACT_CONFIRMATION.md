# 最終契約確認：Human Gate / JARVIS / T2 の実際の API

**Date:** 2026-09-22  
**重要:** Adapter → Bridge → HAB Core → JARVIS → T2 の実際の責務を確認

---

## A. phi_os/human_gate.py の実際の API契約

### submit(payload) の実際の流れ
```python
def submit(payload: dict) -> dict:
    """新規Human Gateリクエストを生成し、PENDING状態のeventを記録する。"""
    request_id = payload.get("request_id") or _next_event_id()
    # ... validation ...
    return _record_transition(conn, "submit", request_id, payload, previous_state=None)
```

**入力:**
```python
{
    "decision_id": "DECISION_AI_A_001",  # 必須
    "actor": "AI_AGENT_A",               # 必須
    "scope": ["component_A"],            # 必須
    "authority_role": "AI_AUTHORITY",    # 必須
}
```

**出力:**
```python
{
    "event_id": "HG20260922_...",
    "request_id": "HG20260922_...",
    "timestamp": "2026-09-22T...",
    "next_state": "PENDING",  # ← PENDING状態で返る
    "type": "HUMAN_GATE_EVENT",
    "action": "submit",
    ...
}
```

**重要:** submit() は PENDING 状態のリクエストを**生成するだけ**。

---

### approve(request_id, payload) の実際の流れ
```python
def approve(request_id: str, payload: dict | None = None) -> dict:
    """
    Human Gate approval with HG-AS-01 Authorization State issuance.
    """
    # Step 1: State transition: PENDING → APPROVED
    event = _transition("approve", request_id, payload, conn=conn)
    
    # Step 2: HG-AS-01 Authorization State Issuance (自動)
    if HG_AS_01_AVAILABLE and event.get("next_state") == "APPROVED":
        success, auth_error, authorization_id = issue_authorization_state(request_id, conn=conn)
        if success:
            event["authorization_id"] = authorization_id
            
            # Step 3: Fetch decision_id for JARVIS
            decision_id = get_decision_id_from_hg_event(event["event_id"], conn=conn)
            event["decision_id"] = decision_id
    
    return event
```

**入力:**
```python
request_id="HG20260922_...",
payload={
    "decision_id": "DECISION_AI_A_001",
    "actor": "AI_AGENT_A",
    "scope": ["component_A"],
    "authority_role": "AI_AUTHORITY",
}
```

**出力:**
```python
{
    "event_id": "HG20260922_...",
    "request_id": "HG20260922_...",
    "next_state": "APPROVED",  # ← APPROVED状態
    "authorization_id": "550e8400-e29b-...",  # ← 自動生成
    "decision_id": "DECISION_AI_A_001",
    "authorization_state_issued": True,
    ...
}
```

**重要:** approve() は PENDING → APPROVED への遷移 + Authorization State の自動生成を行う。

---

## B. 重大な契約発見：approval の責務

### STEP 3 テストのコード
```python
# Line 50-62 in test_hab_jarvis_t2_integration_step3.py

# Step 1: HAB.submit() 
submit_result = submit(submit_payload)
request_id = submit_result["request_id"]
# → PENDING状態のリクエストが生成される

# Step 2: Human.approve()
approval_result = approve(request_id, approval_payload)
authorization_id = approval_result.get('authorization_id')
# → PENDING → APPROVED に遷移
# → Authorization State が自動生成される
# → decision_id が返される

# Step 3: JARVIS.receive_decision_from_hab()
jarvis_result = jarvis.receive_decision_from_hab(decision_id)
# → authorization_state lookup → /runtime/approve呼出し
```

### 重大な発見：approve() は누가 呼ぶのか？

現在のSTEP 3 テストでは：
- テストコード内で手動で approve() を呼ぶ

つまり：
- **submit() は AI adapter が呼べる**（request を生成）
- **approve() は Human Authority が呼ぶ** → 自動ではない
- **JARVIS.receive_decision_from_hab() は authorization_state をlookup** → 既にAPPROVED必須

**Bridge の責務の制限:**
```
❌ Bridge が自動で approve() を呼んではいけない
❌ Bridge が JARVIS を自動で呼んではいけない
✓ Bridge は submit() だけを呼ぶ
✓ approve() と JARVIS routing は別の層の責務
```

---

## C. runtime/jarvis/core/engine.py の実際のAPI

### receive_decision_from_hab(decision_id) の実際の流れ
```python
def receive_decision_from_hab(self, decision_id: str) -> Dict[str, Any]:
    """
    STEP 3: Receive decision from HAB and route to T2 Runtime if authorized.
    """
    # Step 1: Check authorization_state for this decision_id
    authorized, reason, authorization_id = self.gate.receive_decision_and_authorize(decision_id)
    
    if not authorized:
        # Fail-Closed
        return {"decision_id": decision_id, "status": "DENIED", ...}
    
    # Step 2: Authorization valid - call /runtime/approve to execute
    return self._trigger_runtime_execution(decision_id, authorization_id)
```

**入力:**
```python
decision_id="DECISION_AI_A_001"
# ※ この decision_id は authorization_state に既に存在していることが前提
#   つまり HAB.approve() が先に呼ばれていることが必須
```

**出力:**
```python
{
    "decision_id": "DECISION_AI_A_001",
    "status": "AUTHORIZED",  # or "DENIED"
    "authorization_id": "550e8400-e29b-...",
    "execution_id": "fa39faa5-971e-...",
    "tool_name": "mocka_get_overview",
    "execution_status": "ok",
}
```

**重要:** receive_decision_from_hab() は authorize_state が既に APPROVED されていることが前提。

---

## D. 状態遷移図

```
AI Adapter
  ↓
HAB.submit(payload with decision_id)
  ↓
human_gate_events: PENDING 状態のリクエスト生成
  ↓
[Human Authority が承認を判定]  ← ここが重要
  ↓
HAB.approve(request_id, payload)
  ↓
human_gate_events: PENDING → APPROVED 遷移
authorization_state: 自動生成（APPROVED）
  ↓
[何が JARVIS を呼ぶのか？]  ← ここが未定義
  ↓
JARVIS.receive_decision_from_hab(decision_id)
  ↓
authorization_state lookup → /runtime/approve呼出し
  ↓
execution_log記録
```

---

## E. Bridge の正しい責務（訂正版）

### Bridge は submit() だけを呼ぶ
```python
class HABBridge:
    def submit_from_ai(self, ai_identity, context):
        """AI request を HAB.submit() へ渡す（PENDING状態のリクエスト生成）"""
        payload = {
            "decision_id": context["decision_id"],
            "actor": ai_identity,
            "scope": context["scope"],
            "authority_role": context["authority_role"],
        }
        event = submit(payload)
        return event["request_id"]  # ← PENDING状態のrequest_idを返す
```

### approve() と JARVIS routing は Bridge の外
```
Bridge: submit() only
  ↓
[External: Human Authority approval]
  ↓
[External: HAB.approve() 呼出し]
  ↓
[External: JARVIS.receive_decision_from_hab() 呼出し]
```

---

## F. 実装対象ファイル

### 新規作成
- [ ] `gateway/hab_bridge.py`
  - **HABBridge.submit_from_ai()** のみ実装
  - approve() は実装しない
  - JARVIS routing は実装しない

### 変更
- [ ] `gateway/adapter_gpt.py`
  - handle_function_call() の内部で HABBridge.submit_from_ai() を呼ぶ

### 変更なし
- phi_os/human_gate.py （submit/approve は変更しない）
- runtime/jarvis/core/engine.py （変更しない）
- app.py （T2 Runtime、変更しない）

---

## G. 重大な契約変更

**当初の想定（誤解）:**
```
Adapter → Bridge → submit() → approve() → JARVIS → T2
```

**実際の契約（訂正）:**
```
Adapter → Bridge → submit() → [PENDING]
（approve() と JARVIS routing は Bridge 外の責務）
```

**理由:**
- Bridge は AI adapter layer
- Human Authority approval は Bridge のスコープ外
- JARVIS routing も Bridge のスコープ外

---

## H. 実装判定

**判定:** Bridge の scope を制限する必要がある

**修正内容:**
1. Bridge は submit() だけを呼ぶ（PENDING状態のリクエスト生成）
2. Bridge は approval を呼ばない
3. Bridge は JARVIS を呼ばない

**次のステップ:**
- 最小 HABBridge.submit_from_ai() のみ実装
- 実装後、テストは STEP 3 と同じく：
  - submit() → PENDING
  - 外部で approve() を呼ぶ（テスト用）
  - 外部で JARVIS.receive_decision_from_hab() を呼ぶ（テスト用）

---

**最終契約確認完了**

Bridge の責務が明確になった。
- submit() のみ
- approve() は呼ばない
- JARVIS routing は呼ばない

これで実装可能。
