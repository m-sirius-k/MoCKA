# MCP Final Recovery - Before State Snapshot

取得日時: 2026-07-08 20:10 JST
取得者: くろこ (Claude Code, claude-sonnet-5)
位置づけ: 前回の`.env`修正・再起動（MCP_Recovery_Verification_Report.md）が完了した直後の状態。今回の最終検証の起点として固定する。

| 項目 | 値 |
|---|---|
| `.env` MOCKA_ENDPOINT | `https://mcp.nsjp.org` |
| mocka_mcp_server.py PID | 7056（`python -X utf8 mocka_mcp_server.py`） |
| gateway.py PID | 1912（`python -X utf8 gateway.py`、port 5010、`/api/v1/health` 応答: `{"status":"ok","service":"MoCKA Gateway","version":"1.1"}`） |
| cloudflared | PID 4704、Windowsサービスとして稼働中 |
| `/mcp`（GET、localhost） | `{"name": "mocka-memory-caliber", "version": "1.3.0"}` |
| `/health`（localhost） | `version: 1.5.0, tools: 23` |
| OAuth resource（localhost経由） | `{"resource": "https://mcp.nsjp.org", "authorization_servers": []}` |
| OAuth resource（mcp.nsjp.org経由） | `{"resource": "https://mcp.nsjp.org", "authorization_servers": []}` |

この時点でMoCKA側の変更（`.env`修正・プロセス再起動）は既に完了しており、本ファイルは追加の変更を行わない「最終検証」の開始点として記録するのみ。以降のSTEPで新たなファイル変更・プロセス停止は行わない。
