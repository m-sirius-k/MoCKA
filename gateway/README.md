# MoCKA AI Connector Framework v1

役割: AI Connector Framework（各AI固有差異を吸収するアダプタ層）。
MoCKA MCP（port:5002）への接続口として、GPT / Gemini / Copilot 各AIの
Function Calling / OpenAPI差異を吸収する。

## Layer構成

```
Layer 0: MoCKA Core       events.db / Memory / Relay / Orchestra / Caliber / Essence
Layer 1: MoCKA MCP         mocka_mcp_server.py (port:5002) — 内部標準I/F
Layer 2: MoCKA API         OpenAPI / REST / 認証 (gateway.py port:5010)
Layer 3: AI Connector      adapter_gpt / adapter_gemini / adapter_copilot — 各AIアダプタ
```

## ファイル構成

| ファイル | 役割 |
|---|---|
| gateway.py | Flask API本体 port:5010 |
| context_builder.py | Context生成 3モード |
| auth.py | HMAC + nonce + timestamp |
| adapter_gpt.py | OpenAI Function Calling |
| adapter_gemini.py | Google Function Calling |
| adapter_copilot.py | Power Automate / Copilot Studio向け |
| openapi.yaml | Copilot Custom Connector登録用 |
| cloudflare/ | リバースプロキシ（TODO_266保留により未使用） |

## 各アダプタの役割

- **adapter_gpt.py**: ChatGPT の Function Calling から MoCKA API への橋渡し。
- **adapter_gemini.py**: Gemini の functionDeclarations 形式に対応した橋渡し。
- **adapter_copilot.py**: Power Automate / Copilot Studio Custom Connector向けレスポンス変換。

各アダプタは `MOCKA_GATEWAY_URL` 環境変数（デフォルト `http://localhost:5010`）で
接続先を切り替え可能。Named Tunnel確立後もコードの書き換えなしで対応できる。

## 関連

- TODO_268: AI Connector Framework v1確立
- ref: E20260610_010
