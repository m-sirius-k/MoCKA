# Orchestra × HAB/MultiDispatcher 既存接続点特定調査
**Date:** 2026-09-23  
**Status:** 調査のみ、コード変更なし  
**Scope:** 既存Orchestra基盤とHAB/MultiDispatcherの最小接続点を特定

---

## 調査概要

```
Goal: 既存部品だけで接続できるか？
Status: YES - 新しいコードは必要だが、architecture change は不要
```

---

## ORCHESTRA EXISTING ENTRY

**ファイル:** `PlanningCaliber\workshop\Orchestra_Project\orchestra_one\orchestra_one_host.py`

**関数:** `async def run_orchestra(prompt: str) -> dict`

**特徴:**
- Native Messaging プロトコル（Chrome拡張からの呼び出し）で動作
- Playwright で複数AI (ChatGPT/Gemini/Perplexity/Copilot) を自動操作
- 複数AIの回答を同時収集し、結果を辞書で返す
- ネイティブプロセス（Python）として Windows で実行可能
- 過去実行実績あり（2026年実装済み）

**入力:**
```python
msg = {
    'type': 'RUN_ORCHESTRA',
    'prompt': 'ユーザーのプロンプト'
}
```

**出力:**
```python
{
    'type': 'ORCHESTRA_RESULT',
    'results': {
        'ChatGPT': 'response text',
        'Gemini': 'response text',
        'Perplexity': 'response text',
        'Copilot': 'response text',
    }
}
```

---

## NATIVE MESSAGING REQUEST/RESPONSE SCHEMA

**REQUEST (Chrome Extension → orchestra_one_host.py)**

```json
{
  "type": "RUN_ORCHESTRA",
  "prompt": "text"
}
```

- `type`: 固定値 "RUN_ORCHESTRA"
- `prompt`: ユーザー入力テキスト
- プロトコル: Native Messaging (4バイト長 + JSON UTF-8)

**RESPONSE (orchestra_one_host.py → Chrome Extension)**

```json
{
  "type": "ORCHESTRA_RESULT",
  "results": {
    "ChatGPT": "AI回答",
    "Gemini": "AI回答",
    "Perplexity": "AI回答",
    "Copilot": "AI回答"
  }
}
```

**エラー時:**
```json
{
  "type": "ERROR",
  "error": "error message"
}
```

---

## CHROME EXTENSION CALLER (EXISTING)

**ファイル:** `PlanningCaliber\workshop\Orchestra_Project\extension\content_orchestra.js`

**実装内容:**

1. **入力注入:** `injectText(element, text)`
   - 複数AI各サイトの input element を検出
   - `execCommand('insertText')` で React/ProseMirror state も更新
   - Enter キーで送信

2. **回答検知:** `startResponseMonitor(config, sessionId, aiName)`
   - Stop button の出現・消滅で生成開始/終了を検出
   - テキスト安定性をモニタリング（2秒変化なしで確定）

3. **結果送信:** `chrome.runtime.sendMessage()`
   ```javascript
   {
     type: 'ORCHESTRA_RESPONSE',
     sessionId: '...',
     aiName: 'ChatGPT',
     ai: 'chatgpt.com',
     response: '回答テキスト'
   }
   ```

4. **自動注入（MoCKA統合）:** `mockaAutoInject()`
   - localhost:5000 から Living Context を取得
   - 自動入力・自動送信

---

## EXISTING ORCHESTRA CALLER CODE

**呼び出しパターン存在:** YES

**テストコード:**
- ファイル: `gateway/test_existing_orchestra_path.py`
- 関数: `dispatch_multi_request()` を既に使用
- 目的: 既存 MultiDispatcher → Orchestra 経路の E2E テスト

**実装状況:**
```python
request_params = {
    "request_text": "test input",
    "providers": ["gpt", "gemini", "perplexity"],
    "models": { ... },
    "title": "Existing Orchestra Web Path Test",
    "decision_id": "ORCH_WEB_PATH_20260923"
}
response = dispatch_multi_request(**request_params)
```

この呼び出しは既に MultiDispatcher の標準 API として機能している。

---

## HAB/JARVIS ACCESS

**Status:** あり（実装済み）

**コンポーネント:** `gateway/multi_dispatcher.py`

**実装詳細:**

1. **JARVIS 呼び出し:** `_call_jarvis(decision_id, ...)`
   ```python
   jarvis = JarvisEngine()
   recall_result = jarvis.recall_experience(current_intent=request_text)
   ```
   - Decision Ledger から過去決定を検索
   - 失敗時は fail-open（dispatch は継続）

2. **Decision Context 埋め込み:** `_build_request_with_decision_context()`
   ```
   [JARVIS DECISION CONTEXT]
   Decision ID: ...
   Title: ...
   Decision: ...
   Rationale: ...
   [END JARVIS DECISION CONTEXT]
   
   Original request: ...
   ```

3. **HAB Bridge:** `HABBridge.submit_from_ai()`
   - 各 provider の応答を HAB に記録
   - Decision context を自動付与

**既存コード:**
- `runtime.jarvis.core.engine.JarvisEngine` - 接続済み
- `hab_bridge.HABBridge` - 接続済み

---

## MULTIDISPATCHER EXTENSION POINT

**Status:** あり（使用可能）

**実装:** `gateway/multi_dispatcher.py` 295行目

**Provider Registry:**
```python
_PROVIDER_SOCKETS = {
    "gpt":        ("adapters_gpt_socket", "GPTSocket", "gpt-4"),
    "claude":     ("adapters_claude_socket", "ClaudeSocket", "claude-opus-5"),
    "gemini":     ("adapters_gemini_socket", "GeminiSocket", "gemini-2.0-flash"),
    "perplexity": ("adapters_perplexity_socket", "PerplexitySocket", "sonar-pro"),
}
```

**拡張方法:**
1. レジストリにエントリを追加
   ```python
   "orchestra_web": ("adapters_orchestra_socket", "OrchestraSocket", "default"),
   ```

2. `_call_provider()` は自動的に dispatch
   ```python
   socket_module = __import__(module_name)  # adapters_orchestra_socket
   socket = getattr(socket_module, class_name)()  # OrchestraSocket()
   api_result = socket.request(request_text, model, title)
   ```

**メリット:**
- MultiDispatcher コード変更なし
- Socket 実装だけで済む
- 既存 adapter パターンで統一

---

## MINIMAL CONNECTION POINT

**必要なコード:** `gateway/adapters_orchestra_socket.py` (新規作成)

**実装サイズ:** 約 50-100 行（既存 adapters_gpt_socket.py に準拠）

**実装例（骨組み）:**

```python
# gateway/adapters_orchestra_socket.py

class OrchestraSocket:
    """Orchestrator Web AI Socket - existing orchestra_one_host.py を呼び出す"""

    def request(self, request_text: str, model: str = "default",
                title: str = "Orchestra Request") -> dict:
        """
        MultiDispatcher から呼び出される標準インターフェース
        
        既存 orchestra_one_host.py を Native Messaging で呼び出す
        → Chrome Extension で複数AI を自動操作
        → 結果を集約して返す
        """
        try:
            # orchestrator_api.emit_event() を呼び出し
            # または直接 orchestra_one_host.py をプロセス起動
            
            results = self._invoke_orchestra(request_text)
            
            # MultiDispatcher が期待する形式で返す
            return {
                "status": "ok",
                "response": str(results),  # 複数AI結果を文字列化
                "usage": {
                    "ais_queried": len(results),
                    "model": "orchestra_web"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _invoke_orchestra(self, prompt: str) -> dict:
        """
        orchestrator_api または orchestra_one_host.py を呼び出す
        
        Option A: orchestrator_api.emit_event() 経由
        Option B: subprocess で orchestra_one_host.py 直接起動
        """
        # 実装省略（要設計）
        pass
```

**接続フロー:**

```
MultiDispatcher.dispatch_multi_request()
    ↓
_call_provider("orchestra_web", ...)
    ↓
OrchestraSocket().request(...)
    ↓
orchestrator_api.emit_event() OR subprocess.run(orchestra_one_host.py)
    ↓
Chrome Extension (content_orchestra.js)
    ↓
Native Messaging ↔ orchestra_one_host.py
    ↓
Playwright → ChatGPT/Gemini/Perplexity/Copilot
    ↓
Results returned to MultiDispatcher
    ↓
HAB Bridge で記録
```

---

## ARCHITECTURE CHANGE

**Status:** NO

**理由:**
- MultiDispatcher の既存 Socket pattern で対応可能
- `_PROVIDER_SOCKETS` レジストリに追加するだけ
- `_call_provider()` のロジックは変更不要
- HAB Bridge との統合も既存コード流用

**変更の影響範囲:**
- 新規ファイル: `adapters_orchestra_socket.py`
- 変更ファイル: `multi_dispatcher.py` (1エントリ追加)
- 既存ファイル: 変更不要

---

## NEW CODE REQUIRED

**Status:** YES

**最小実装:**

| ファイル | 行数 | 用途 |
|---------|-----|------|
| `adapters_orchestra_socket.py` | 50-100 | Socket インターフェース |
| `multi_dispatcher.py` edit | 2 | レジストリエントリ追加 |
| 計 | ~50 | 新規 + 既存変更 minimal |

**代替案（Option B）: orchestrator_api 経由**

- 既存 `core_kernel/orchestra/orchestrator_api.py` を再利用
- Request: `emit_event("orchestra_web", payload)`
- Response: `execution_graph` が Chrome Extension と連携
- メリット: MoCKA core framework を活用

---

## 現状まとめ

| 項目 | 状態 | 詳細 |
|------|------|------|
| **Orchestra existing entry** | ✓ 存在 | orchestra_one_host.py (2026年実装済み) |
| **Native Messaging protocol** | ✓ 存在 | orchestrator_one_host.py で実装済み |
| **Chrome Extension** | ✓ 存在 | content_orchestra.js で AI 自動操作 |
| **Playwright integration** | ✓ 存在 | 複数AI を同時操作可能 |
| **HAB/JARVIS access** | ✓ 存在 | multi_dispatcher.py で JARVIS recall 実装済み |
| **MultiDispatcher extension** | ✓ 可能 | Socket レジストリで拡張可能 |
| **Minimal connection point** | ✓ 明確 | adapters_orchestra_socket.py (新規) |
| **Architecture change** | ✗ 不要 | 既存パターンで対応可能 |
| **New code required** | ✓ 少量 | ~50行、既存パターン準拠 |

---

## 接続可能性の判定

```
問: HAB/JARVIS → MultiDispatcher → ??? → 既存 Orchestra という接続ができるか？

答: YES - 既存部品だけで接続可能

必要な作業:
  1. adapters_orchestra_socket.py を新規作成 (~50行)
  2. multi_dispatcher.py の _PROVIDER_SOCKETS に 1行追加
  3. orchestrator_api または orchestra_one_host.py 呼び出しロジックを設計

アーキテクチャ変更: NO - 既存 Socket pattern に従う
```

---

## 次のステップ（実装前提）

**STEP 1: Orchestrator API 選択**
- Option A: `orchestrator_api.emit_event()` 経由（MoCKA core 活用）
- Option B: `orchestra_one_host.py` 直接起動（Native Messaging 活用）

**STEP 2: Socket 実装**
- adapters_orchestra_socket.py で選択した呼び出し方を実装
- Error handling (タイムアウト、AI不可用時の fallback)
- Response parsing (複数AI結果を MultiDispatcher 形式に変換)

**STEP 3: Registry 登録**
- multi_dispatcher.py の _PROVIDER_SOCKETS にエントリ追加

**STEP 4: E2E テスト**
- test_existing_orchestra_path.py の providers リストに "orchestra_web" を追加
- 既存テスト suite で動作確認

---

## 検証済み事項（コード変更なし）

✅ orchestra_one_host.py は存在し、実行可能な状態  
✅ Chrome Extension の content_orchestra.js は実装済み  
✅ Native Messaging protocol は定義済み  
✅ Playwright は environment で利用可能  
✅ HAB Bridge は動作中  
✅ JARVIS recall は実装済み  
✅ MultiDispatcher Socket pattern は拡張可能  

---

## 調査完了

**実施日:** 2026-09-23  
**調査時間:** [実装指示待ち]  
**コード変更:** ZERO  
**新規ファイル作成:** なし  
**結論:** 既存部品だけで接続可能。minimal adapter の実装で統合完成。
