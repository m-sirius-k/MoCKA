# MCP Bug Fact Verification Report

作成日: 2026-07-08
作成者: くろこ (Claude Code, claude-sonnet-5)
目的: claude.ai MCP Connector経由でのtool利用不可症状について、原因断定を行わず、事実台帳と仮説評価表を作成する

対象範囲の限定事項（最初に明記）:
本調査はClaude Code CLI（ターミナル、Windows）から、MoCKA MCPサーバー本体（ローカル/トンネル経由）へ直接HTTPリクエストを送ることで得られる事実のみを扱う。claude.ai web chatのConnector UI自体の挙動（Connected表示・tool_search結果・実際のchat内invocation可否）は、このセッションからは直接観測できない。したがって「Connector→Chat session」層の症状は、ユーザーからの申告事実として扱い、くろこ側での直接再現はしていない。

---

## 1. Confirmed Facts

### 1.1 MCPサーバー実装
- 対象: `C:\Users\sirok\MoCKA\mocka_mcp_server.py`（v1.5.0、1055行）
- 実装形態: `fastmcp`パッケージは不使用。Flask + flask_corsによる自前実装
- `/mcp`エンドポイント（GET/POST）はステートレスなHTTPリクエスト・レスポンス方式（SSE/WebSocket等の永続ストリームではない）。これはこのファイルを扱うプロジェクトのCLAUDE.md自体にも既述の既知仕様
- transport: streamable-httpではなく、単純なJSON-RPC over HTTP POST（`initialize` / `tools/list` / `tools/call`の3メソッドのみ手動分岐）

### 1.2 tool数
- ローカル`/health`（http://localhost:5002/health）の実測レスポンスで確認したtools配列の要素数: 23個
  （`mocka_get_overview`, `mocka_get_essence`, `mocka_get_todo`, `mocka_add_todo`, `mocka_update_todo`, `mocka_list_events`, `mocka_read_event`, `mocka_search`, `mocka_write_event`, `mocka_seal`, `mocka_get_incidents`, `mocka_get_guidelines`, `mocka_get_command_center`, `mocka_check_utf8`, `mocka_registry_get`, `mocka_registry_add`, `mocka_registry_current_state`, `mocka_decision_write`, `mocka_decision_get`, `mocka_decision_list`, `mocka_integrity_write`, `mocka_integrity_get`, `mocka_integrity_list`）
- 参考: ソース内`"name":`の単純grepでは25件ヒットしたが、これはTOOLS配列外の他レコード（integrity classification等）を含むため、23個が正しい値

### 1.3 バージョン文字列の不一致（サーバー内部の食い違い）
同一稼働プロセス内で、エンドポイントごとに異なるバージョン文字列を返す:
- ファイル先頭コメント: v1.5.0
- `/health`のJSON: `"version": "1.5.0"`
- `/mcp`のGET、および`initialize`応答内`serverInfo.version`: `"1.3.0"`（ハードコード）
この不一致自体が不具合の直接原因かは不明だが、外部からサーバーの版を識別する際に情報源によって異なる値が返る状態は事実として存在する。

### 1.4 tunnel/公開経路
- Named Tunnel（Cloudflare）: `mcp.nsjp.org` -> localhost:5002。`cloudflare/setup_named_tunnel.bat`によりTODO_266で構築（固定URL運用が目的）
- `cloudflared.exe`は現在Windowsサービスとして稼働中（tasklistで確認済み）
- `.env`の`MOCKA_ENDPOINT`は現在 `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev`（ngrok無料枠URL）に設定されている
- 外部からの実測:
  - `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp` -> **HTTP 404、`Ngrok-Error-Code: ERR_NGROK_3200`**（このホスト名に対応するngrokエージェントセッションが現在存在しない、すなわちこのURLは死んでいる）
  - `https://mcp.nsjp.org/mcp` -> HTTP 200、正常なJSONレスポンス（`{"name": "mocka-memory-caliber", "version": "1.3.0"}`）

### 1.5 OAuth関連メタデータの内容
`mcp.nsjp.org`（生きている方の経路）に対して直接確認:
- `GET /.well-known/oauth-protected-resource` -> `{"resource": "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev", "authorization_servers": []}`
  - すなわち、稼働中でクライアントが実際に接続する先は`mcp.nsjp.org`であるにもかかわらず、サーバー自身が申告する`resource`識別子は死んでいる方のngrok URLになっている（不一致）
  - `authorization_servers`は空配列
- `GET /.well-known/oauth-authorization-server` -> `{}`（完全に空）
- `POST /register`（Dynamic Client Registration相当のエンドポイント）はリクエスト内容に関わらず固定値 `{"client_id": "mocka-mcp", "client_secret": "none"}` を返す実装（`mocka_mcp_server.py`内で確認、リクエストボディ未使用）

### 1.6 JSON-RPCレベルでの実動作
`mcp.nsjp.org`に対し直接HTTP POSTで検証:
- `tools/list` -> 正常応答（23ツールのスキーマを含むJSONを返却）
- `tools/call`（`mocka_get_overview`）-> 正常応答（実データを含むcontentを返却）
これにより、サーバー本体・トランスポート・生きている方のtunnelについては、生のHTTPクライアント（curl相当）からは正常に機能していることを確認した。

### 1.7 既存メモリとの関連
- TODO_421（Configuration SSOT監査）にて「ngrok URL 4箇所のハードコードはConfirmed Drift」と既に記録されている
- TODO_422（ngrok SSOT再統合）は未着手のまま
- 本調査で確認した「MOCKA_ENDPOINTが死んでいるngrok URLを指しており、かつoauth-protected-resourceの`resource`値としてそのまま外部露出している」という事実は、TODO_421/422の対象と同一系統の問題だが、「単なるURL重複」ではなく「稼働中の経路(mcp.nsjp.org)と申告される識別子(ngrok URL)が食い違っている」という、より具体的な形として確認できた

---

## 2. Reproduction Steps（くろこが実施した検証手順）

1. `C:\Users\sirok\MoCKA\mocka_mcp_server.py`を直接読み、実装方式（Flask/独自実装、fastmcp不使用）を確認
2. `curl http://localhost:5002/health` によりローカルプロセスの稼働状態とtools一覧を確認
3. `curl http://localhost:5002/mcp`（GET）によりバージョン文字列の食い違いを確認
4. `.env`の`MOCKA_ENDPOINT`値を確認
5. `curl https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp` および同ドメインの`/.well-known/oauth-protected-resource`に対し外部からGETし、ERR_NGROK_3200（404）を確認
6. `curl https://mcp.nsjp.org/mcp`、同ドメインの`/.well-known/oauth-protected-resource`、`/.well-known/oauth-authorization-server`に対し外部からGETし、正常応答および`resource`値の不一致を確認
7. `curl -X POST https://mcp.nsjp.org/mcp` で`tools/list`・`tools/call`（`mocka_get_overview`）を実行し、JSON-RPCレベルでの実動作を確認

実施していないこと（重要な限定）:
- claude.ai web chatのConnector UIでの実際の接続・tool_search・invocation操作は未実施（このセッションからはブラウザ操作ができないため）
- 最小構成FastMCPサーバー（FastMCP 3.4.2 / streamable-http / tool 1個 / 新規Cloudflare Quick Tunnel）による比較用の再現環境は未構築（ユーザー側での準備・実行が必要）

---

## 3. Failure Boundary（成功/失敗の切り分け）

```
MCP Server (Flask実装)          -> 成功（/health, /mcp GETとも正常）
   |
Transport (JSON-RPC over HTTP)  -> 成功（tools/list, tools/callとも正常応答、curlで確認済み）
   |
Tunnel (mcp.nsjp.org経由)        -> 成功（cloudflared稼働中、外部から200応答）
   |
Tunnel (ngrok経由, MOCKA_ENDPOINT)-> 失敗（ERR_NGROK_3200、トンネル自体が不通）
   |
OAuth Protected Resource Metadata -> 内容に不整合あり（resource値が不通の方のngrok URLを指す）
   |
Connector handshake（claude.ai側）-> 未検証（ユーザー申告ではConnected表示）
   |
Tool discovery（claude.ai側）    -> 未検証（ユーザー申告では表示あり）
   |
Chat session tool availability  -> 未検証（ユーザー申告では利用不可）
   |
Tool execution                  -> 未検証（ユーザー申告では利用不可）
```

くろこが直接確認できたのは「MCP Server」から「Tunnel」までの4段。「Connector handshake」以降はユーザー申告のみであり、直接の技術的証拠はまだない。

---

## 4. Hypothesis（原因断定ではなく、評価対象としての仮説）

| 仮説 | 内容 | 現時点の評価材料 |
|---|---|---|
| A: MCPサーバー実装問題 | Flask自前実装のJSON-RPC処理に不具合がある | curlによる直接テストでtools/list・tools/callとも正常応答。可能性は低いと見られるが、claude.ai Connector特有のリクエストヘッダ・シーケンス（例: initialize直後の特定パラメータ）でのみ失敗する経路は未検証のため完全には否定できない |
| B: Transport/Tunnel問題 | handshake/tool list取得自体が失敗している | mcp.nsjp.org経由では成功。ただし、claude.ai ConnectorがどのURL（mcp.nsjp.orgか、それとも別途設定されたURLか）に対して実際に接続しているかは本調査では未確認。仮にConnector設定側が死んでいるngrok URLを向いている場合はこの仮説が有力になる |
| C: Connector→Chat session tool registration問題 | 接続確認・tool discoveryまでは成功するが、chatセッションでの利用可能化処理で失敗する | OAuth Protected Resource Metadataの`resource`値が、実際にクライアントが到達する経路（mcp.nsjp.org）と異なる値（不通のngrok URL）を返している事実を確認した。MCP Authorization仕様（RFC 8707 resource indicators準拠のクライアント実装）では、クライアントがこの`resource`値と実際の接続先URLの一致を検証する場合がある。一致検証を行う実装であれば、初期のdiscovery（tools/list相当）は通っても、認可を要する後続のセッション処理で不一致により弾かれる、という経路が理論上あり得る。ただし、claude.ai側の実装がこの検証を実際に行っているかどうかはくろこの手元では確認できておらず、あくまで仕様上あり得る経路として提示するに留める |
| D: tool_search index/cache問題 | 新規chat・cache削除・別workspace等で症状が変わる | 未検証。ユーザー側での比較試験が必要 |

### 参考: 関連しそうで実は前提が異なる公開Issue
GitHub `anthropics/claude-code#55914`（"[BUG] All claude.ai-connected MCP integrations show Connected but expose zero tools"）を確認した。

症状の表面的な一致点:
- Connector側は「Connected」と表示される
- 実際のtool利用ができない

前提が異なる点（重要、同一バグと断定しない理由）:
- #55914はClaude Code **CLI（ターミナル）** セッションの`claude mcp list` / `ToolSearch`層の話であり、今回問題にしているclaude.ai **web chatのConnector UI**とは異なるクライアント面
- #55914の対象はGmail/Google Drive/Notion等、claude.ai account側でOAuth管理される**ネイティブ統合コネクタ**であり、今回のMoCKA MCPサーバーのような**カスタム/セルフホストMCPサーバー**とは種類が異なる。同issue本文でも「ローカル設定のカスタムstdio/HTTPサーバーは同一セッションで問題なく動く」と明記されている
- #55914では「tool一覧自体が最初から一切表示されない」（discovery自体が失敗）のに対し、今回の申告は「discoveryまでは表示される、invocationだけ失敗する」であり、失敗している段階が異なる
- #55914はGitHub Actionsのbotにより自動的に **#51736の重複** として3日後にクローズされているが、issue本文自身は「#51736はこれの逆症状（stdioが失敗しclaude.aiは動く）」と明記しており、bot判定と投稿者の主張が食い違っている。この点も踏まえ、#55914を「同一バグの追加証拠」として引用するのは不適切と判断する

結論（この節のみ）: #55914は「類似の見た目の症状を報告した既存issueが存在する」以上の意味づけはできない。同一バグである根拠にはならない。

---

## 5. Not Confirmed（未確認事項、今後の検証が必要）

- claude.ai ConnectorがMoCKA MCPサーバーに対して実際にどのURL（mcp.nsjp.orgか、別のURLか）で登録されているか
- claude.ai Connector側のtool_search結果・実際のchat内invocation失敗の再現（ユーザー側でのブラウザ操作による直接確認が必要）
- 最小構成FastMCPサーバーでの同一症状の再現有無（比較対象として未実施）
- claude.ai側のMCPクライアント実装が、OAuth Protected Resource Metadataの`resource`値と接続先URLの一致検証を実際に行っているか（Anthropic内部実装の推測はしない。公開仕様上あり得る経路としてのみ提示）
- バージョン文字列の不一致（1.3.0 vs 1.5.0）が今回の症状に影響しているかどうか

---

## 6. Suggested Investigation Area（次の検証ステップ、修正実装は含まない）

1. claude.ai Connector設定画面で、MoCKA MCPサーバーとして実際に登録されているURLを確認し、`mcp.nsjp.org`かngrok URLかを特定する
2. 特定できたURLに対して、claude.ai chat UI上で実際にtool_search・invocationを試行し、症状を再現する（ブラウザ操作が必要、くろこ単独では実施不可）
3. `.env`の`MOCKA_ENDPOINT`を、実際に稼働している`mcp.nsjp.org`に合わせて修正すべきかどうかを、TODO_422のスコープ内で改めて評価する（本調査はこの是正の実施を含まない。実施にはHuman Gate承認が必要）
4. 最小構成FastMCPサーバー（FastMCP 3.4.2 / streamable-http / tool 1個 / 新規Cloudflare Quick Tunnel）を用意し、正しいoauth-protected-resource（resourceと接続先URLが一致する状態）で同一症状が再現するかを比較する
