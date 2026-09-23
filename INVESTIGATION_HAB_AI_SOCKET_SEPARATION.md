# HAB COMMON CORE / AI SOCKET 分離 — 調査報告書

**Date:** 2026-09-22  
**Scope:** 既存 AI Adapter/Socket パターンと HAB 接続の可能性調査

---

## A. 既存 Socket/Adapter 実装一覧

### 1. mocka_hub/adapters/ (Adapter Framework)

| ファイル | AI Provider | 目的 | 状態 |
|---------|-----------|------|------|
| claude_adapter.py | Claude (R02) | MCP 経由で MoCKA イベント変換 | ACTIVE |
| chatgpt_adapter.py | ChatGPT (R01) | Human Gate 経由のイベント変換 | ACTIVE |
| gemini_adapter.py | Gemini | Adversarial Reviewer ロール | ACTIVE |

**特性:**
- 各 Adapter は `to_mocka_event()` を実装
- 各 Adapter は `validate_authority()` を実装
- channel_type の区別あり（"mcp" vs "human_relay"）

### 2. gateway/ (Connector Framework) — Port 5010

| ファイル | 機能 | 状態 |
|---------|------|------|
| gateway.py | Connector メイン、複数 Adapter 登録 | ACTIVE |
| connector_caliber.py | Caliber 層、AI ルーティング、Capability registry | ACTIVE |
| adapter_gpt.py | GPT Function Calling インターセプター | ACTIVE |
| adapter_gemini.py | Gemini API connector | TODO_* |
| adapter_copilot.py | Copilot connector | ACTIVE |
| adapter_perplexity.py | Perplexity connector | TODO_269 |
| adapter_genspark.py | GenSpark connector | TODO_270 |

**入口:** `/api/v1/connector/query` → AI parameter で adapter 選択

### 3. orchestrator/

| ファイル | 機能 |
|---------|------|
| agent_router.py | Task → Agent 割り当て |

---

## B. HAB Core 候補

**ファイル:** `phi_os/human_gate.py`  
**メソッド:**
- `submit(payload)` — request 生成
- `approve(request_id, payload)` — approval + authorization_state 生成
- `reject(request_id, payload)` — rejection
- `list_pending()` — PENDING 一覧

**責務:**
- Request state management (PENDING → APPROVED/REJECTED)
- Authorization State 生成（HG-AS-01 bridge 経由）
- Event logging

**現在の入口:**
- HTTP API: `/api/human_gate/submit`, `/api/human_gate/approve`
- 直接呼び出し: `from phi_os.human_gate import submit, approve`

---

## C. AIごとの接続位置

### 現在の実装状態

| AI | 既存接続 | Gateway | HAB 接続 | 分類 |
|----|---------|---------|---------|------|
| Claude (R02) | MCP 直接 | adapter (mocka_hub) | なし | EXISTING_ADAPTER |
| ChatGPT (R01) | Function Call | adapter (gateway/adapter_gpt.py) | なし | EXISTING_ADAPTER |
| Gemini | 不明 | adapter (mocka_hub) | なし | EXISTING_ADAPTER |
| Copilot | 不明 | adapter (gateway) | なし | EXISTING_ADAPTER |
| Perplexity | なし | TODO_269 | なし | MISSING |
| GenSpark | なし | TODO_270 | なし | MISSING |

### 接続の流れ

#### 経路 A: Gateway 経由（現在）
```
AI (GPT/Gemini/Copilot)
  ↓
gateway/adapter_*.py
  ↓
/api/v1/connector/query (gateway.py)
  ↓
MoCKA Event テーブル
  ↓
(HAB に接続していない)
```

#### 経路 B: 既存テスト（STEP 3/Multi-AI）
```
AI-A / AI-B (Direct Python import)
  ↓
HAB.submit() / HAB.approve() (phi_os/human_gate.py)
  ↓
Authorization State
  ↓
JARVIS
  ↓
T2 Runtime
```

---

## D. 不足しているもの

### 1. Gateway → HAB 接続なし

現在、gateway/connector 経由で AI からの入力は MoCKA Event テーブルに直接記録されます。

HAB（Human Gate）には接続していません。

**問題:**
- Gateway 経由の AI 入力が、Approval/Authorization State を生成しない
- JARVIS/T2 への経路がない

### 2. HAB の socket インターフェース不在

現在、HAB は Python 直接呼び出しと HTTP API のみです。

通用 socket インターフェースがなく、各 AI から同じ入口を使いにくい。

### 3. AI Identity の標準化不在

AI-A / AI-B テストでは actor_id を payload に含めていますが、これは adhoc です。

AI からの request に対して、統一された `ai_identity` フィールドがない。

---

## E. Socket 分離の可能性評価

### 現状の分析

**HAB Core:** 既存の submit/approve/reject インターフェース  
**Socket/Adapter:** 各 AI の差分（API形式、認証、データ変換）

**境界が明確か:**
- ✓ HAB Core の責務は明確（state management + auth state generation）
- ✓ Adapter Framework（gateway/）は既に存在
- ✗ HAB と Gateway が接続していない

### 実装可能性

**最小実装で実現可能:** YES

**必要なもの:**
1. Gateway → HAB への bridge
   - `/api/v1/connector/query` から HAB.submit() を呼ぶ adapter
   - Decision ID の生成・伝播

2. HAB の共通 Socket インターフェース定義
   ```
   class HABSocket:
       def submit_from_ai(ai_identity, request_payload) -> decision_id
       def approve_decision(decision_id, approval_payload) -> authorization_id
   ```

3. AI Adapter の標準化
   - Gateway adapter が AI output を HAB Socket に変換

**NOT 必要なもの:**
- ✗ 新しい HAB 実装（既存 submit/approve を再利用）
- ✗ AI ごとの Authorization system
- ✗ 新しい ID 体系
- ✗ Recovery/Monitoring 拡張

---

## F. 実装方針

### Option 1: Gateway Bridge 追加（最小実装）

```python
# gateway/hab_bridge.py (新規)
class HABBridge:
    def submit_from_ai(ai_identity, payload):
        from phi_os.human_gate import submit
        return submit({
            **payload,
            "actor": ai_identity,  # AI name/ID
        })
    
    def approve_decision(decision_id):
        # HAB approval → authorization_state → JARVIS
        pass
```

**利点:**
- 既存 HAB コードを変更しない
- Gateway と HAB を loose coupling で接続
- 各 Adapter で HABBridge を呼ぶだけで OK

### Option 2: HAB HTTP API 拡張

```python
# app.py に新 endpoint
@app.route('/api/human_gate/from_ai', methods=['POST'])
def submit_from_ai():
    # Gateway から呼ばれるエンドポイント
    # request_id → decision_id → execution_id を返す
```

**利点:**
- Loose coupling が強い
- Gateway がプロセス外でもよい

**欠点:**
- HTTP overhead

---

## 結論

### 現在の状態

```
   Gateway Framework ← ← → MoCKA Event Store
   (adapter_gpt, 等)
   
   HAB Framework ← → JARVIS ← → T2 Runtime
   (phi_os/human_gate.py)
   
   （この2つが接続していない）
```

### 実現可能な目標構造

```
             ┌── GPT Socket ──────┐
             ├── Gemini Socket ───┤
             ├── Claude Socket ───┤
AI Providers ├── Perplexity Socket┤
             └── Other Socket ────┘
                         ↓
                   ┌─────────────────┐
                   │ HAB Bridge      │
                   │ (新規、最小)      │
                   └────────┬────────┘
                            ↓
                      ┌──────────────┐
                      │ HAB Core     │
                      │ (既存、変更なし)│
                      └────────┬─────┘
                               ↓
                             JARVIS
                               ↓
                           T2 Runtime
```

### 実装判定

**A = 実装可能。最小 Bridge で socket 分離実現。**

最小変更で多様な AI を同じ HAB/JARVIS/T2 パイプラインに接続できます。

---

## 次のステップ（IF 指示あれば）

1. HABBridge を実装（gateway/hab_bridge.py）
2. 各 Adapter（adapter_gpt.py等）を HABBridge 経由に変更
3. テスト: GPT/Gemini/Perplexity それぞれから HAB → JARVIS → T2 を通す

ただし、今回の指示「最小実装のみ」に従い、実装は実施しません。

---

**Report Status:** INVESTIGATION COMPLETE  
**Action:** Awaiting further instruction
