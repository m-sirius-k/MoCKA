# MCP Bug Fact Verification Report v2 - 境界特定監査

作成日: 2026-07-08
作成者: くろこ (Claude Code, claude-sonnet-5)
前提: 本文書はv1（MCP_Bug_Fact_Verification_Report.md）の続報であり、TASK-1〜TASK-6の指示に沿って再構成したもの。原因断定・コード変更・OAuth設定変更・Endpoint変更・GitHub投稿はいずれも行っていない。

対象範囲の限定事項（v1と同様、再掲）:
くろこ（Claude Code CLI）からは、MoCKA MCPサーバーへの直接HTTPリクエストによる事実確認のみが可能。claude.ai web chatのConnector UI（Connected表示・tool_search・invocation）自体の直接操作・観測はできない。この層はユーザー申告事実として扱う。

---

## TASK-1: 公開経路整合性確認（最優先）

| 項目 | 現在値 | 実際の到達性 | MOCKA_ENDPOINTとの一致 |
|---|---|---|---|
| MOCKA_ENDPOINT（.env） | `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev` | 404 / `Ngrok-Error-Code: ERR_NGROK_3200`（tunnel不通、再テスト済み） | - |
| 実稼働URL（cloudflared ingress、`C:\Users\sirok\.cloudflared\config.yml`より） | `https://mcp.nsjp.org` -> `http://localhost:5002` | HTTP 200、正常応答（再テスト済み） | 不一致（MOCKA_ENDPOINTとは別ホスト） |
| oauth resource（`/.well-known/oauth-protected-resource`の`resource`値、mcp.nsjp.org経由で取得） | `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev` | 上記の通り404 | 一致（MOCKA_ENDPOINTの値をそのまま反映） |
| issuer（`/.well-known/oauth-authorization-server`） | `{}`（空） | - | 該当なし（issuer自体が未定義） |
| callback関連（redirect_uri / client_id / client_secretの検証ロジック） | `auth.py`内に issuer/callback/redirect_uri/client_id/client_secret のいずれの記述も無し。`/register`は`mocka_mcp_server.py`内でリクエスト内容に関わらず固定値`{"client_id": "mocka-mcp", "client_secret": "none"}`を返すのみ | 実装なし（スタブ） | - |

判明した構図:
- 「実際にクライアントが到達できる入口」= `mcp.nsjp.org`
- 「認証・識別情報（OAuth resource）が示す入口」= 死んでいるngrok URL
この2つが一致していない状態を確認した（TASK-1の確認事項そのもの）。

補足（背景情報、今回の主題ではないが関連履歴として記録）:
`config.yml`のコメントによれば、Named Tunnel自体も過去に「存在しないtunnel名`mocka-mcp`を指していた」設定不備があり、2026-07-05に実体`mocka-gateway`（ID: efb26375-013a-48d3-a31b-a2f70e10e5a6）へ修正された経緯がある。公開経路の識別子まわりでの食い違いは今回が初めてではない。

---

## TASK-2: MCPサーバー健全性確認

外部（mcp.nsjp.org経由）から実行した検証:

| 確認項目 | request | response概要 | 判定 |
|---|---|---|---|
| `/mcp`（GET） | `GET https://mcp.nsjp.org/mcp` | `{"name": "mocka-memory-caliber", "version": "1.3.0"}`、HTTP 200 | OK |
| `tools/list` | `POST /mcp` `{"jsonrpc":"2.0","id":1,"method":"tools/list"}` | tool 23件のスキーマを含む正常なJSON-RPC応答 | OK |
| `tools/call` | `POST /mcp` `{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"mocka_get_overview","arguments":{}}}` | `mocka_get_overview`の実データを含む正常な応答 | OK |

判定:
- Server: OK
- Transport: OK

---

## TASK-3: OAuth Resource整合性確認（重点調査）

確認事項:
- `resource`値: 死んでいるngrok URL（TASK-1に記載の通り）
- MCP endpoint URL（実際にクライアントが接続する先）: `mcp.nsjp.org`
- Connectorへ提示される識別子: サーバーが返す`resource`値がそのままそれにあたる場合、死んでいるngrok URLがConnectorへ提示されていることになる

可能性としての評価（原因断定ではない）:
- 古いngrok URLが`resource`として残っている場合、MCP Authorization仕様（RFC 8707 resource indicators系）に準拠したクライアント実装であれば、「クライアントが実際に接続したURL」と「サーバーが自己申告するresource URL」の不一致を検知し、後続の認可・tool登録処理を拒否する可能性がある
- ただし、`authorization_servers`が空配列かつ`/.well-known/oauth-authorization-server`も空`{}`であるため、そもそもこのサーバーは「OAuth認可を要求しない（認可不要）」ものとしてクライアントに解釈される可能性もある。その場合はresourceの不一致は実質的に無視され、無関係という評価も同時に成立し得る
- したがって「resource不一致がtool登録失敗の原因である」とは断定できず、「resourceが提示されている以上、クライアント実装次第では不一致が影響し得る」という可能性の提示に留める

追加確認: `auth.py`（gateway/gateway.py側で使用、port 5010）にはOAuth関連ロジックが一切存在せず、`require_api_key`という別方式（APIキー方式、TODO_415で強化されたもの）のみが実装されている。`mocka_mcp_server.py`側（port 5002、claude.ai Connectorが実際に接続する対象）のoauth系エンドポイントは、この`auth.py`とは接続されていない独立したスタブ実装である。すなわち、MCP仕様が定めるDiscovery用のエンドポイント（`/.well-known/*`, `/register`）は形だけ用意されているが、実質的な認可ロジックとは連動していない。

---

## TASK-4: claude.ai Connector層切り分け

くろこはこの層を直接観測できないため、ユーザー申告に基づく整理のみ行う。

ユーザーからの申告事実（前回セッションで得たもの）:
- Connector status: Connected
- Tool discovery: 表示あり
- Permission: Always allow
- 通常Chatセッションからの tool_search / tool利用: 不可

分類上の課題:
指示されたケースA/B/Cの分類を行うには、「Connector管理画面でのtool一覧表示」と「実際のchatセッション内でのtool_search結果」が同一のものを指しているか、別々の事象かを区別する必要がある。現状の申告は両者が並記されており、以下のいずれであるかが未確定:
- ケースA相当: 管理画面ではtool一覧が見えるが、chatセッション内のtool_searchでは0件（discovery/register問題寄り）
- ケースB相当: chatセッション内のtool_searchでtoolは見つかるが、実際にinvokeすると失敗する（execution/auth問題寄り）
- ケースC相当: chatセッション内でtool_search自体が機能しない、または一切ヒットしない（chat session index問題寄り）

この区別により、TASK-3で提示した「resource不一致」仮説の妥当性が変わる（ケースBであればexecution/auth層の問題として当該仮説と整合しやすいが、ケースAやCであれば別層の問題である可能性が高まる）。

現時点の暫定分類: 申告内容から最も近いのはケースA/Cの混合（discoveryの表示自体はあるが、chatセッションでの実利用に届いていない）と見られるが、確定はしていない。

---

## TASK-5: 比較実験

比較1（修正前、現在設定）: 実施済み。TASK-1〜TASK-3の通り。

比較2（endpoint/resource完全一致状態、mcp.nsjp.orgに揃えた場合）: **未実施**。
理由: この比較を行うには`.env`の`MOCKA_ENDPOINT`を実際に書き換える必要があるが、これは制約「Endpoint変更禁止」に抵触するため、調査フェーズの範囲内では実施しない。実施する場合は、TODO_422のスコープでHuman Gate承認を経た上で、別途変更作業として行うことが必要。

代替として検討可能な非破壊的な比較方法（今回は未実施、提案のみ）:
- ローカルの`.env`を書き換えず、一時的な別プロセス（ポート変更・別環境変数）でoauth-protected-resourceのみ`mcp.nsjp.org`を返すテスト用インスタンスを本番とは別に起動し、その一時インスタンスに対してのみclaude.ai Connectorを新規登録して比較する方法。ただしこれも「新規Connector登録」という操作を伴うため、実施の可否はユーザー判断による。

---

## Confirmed Facts（事実のみ）

1. MoCKA MCPサーバー（`mocka_mcp_server.py`）はFlask自前実装であり、fastmcpパッケージは使用していない
2. tool数は23個（`/health`実測。ソース内`"name":`grepの25件は別レコードを含むため誤り）
3. サーバー内部でバージョン文字列に不一致がある（`/health`: 1.5.0、`/mcp` GETおよび`initialize`応答: 1.3.0固定）
4. `.env`の`MOCKA_ENDPOINT`は死んでいるngrok URL（`ERR_NGROK_3200`、404）
5. 実際に稼働し到達可能な公開URLは`mcp.nsjp.org`（cloudflared Named Tunnel、HTTP 200）
6. `mcp.nsjp.org`経由で`tools/list`・`tools/call`とも正常応答（JSON-RPCレベルで実動作確認済み）
7. `/.well-known/oauth-protected-resource`の`resource`値は、到達可能な`mcp.nsjp.org`ではなく、死んでいるngrok URLをそのまま返す
8. `/.well-known/oauth-authorization-server`は空`{}`、`authorization_servers`も空配列
9. `/register`エンドポイントはリクエスト内容に関わらず固定のダミー値を返すスタブ実装
10. `auth.py`（gateway/gateway.py, port 5010側）にはOAuth関連ロジックが存在せず、`mocka_mcp_server.py`（port 5002側）のoauth系スタブとは独立している
11. cloudflared Named Tunnelの設定自体も過去に一度、存在しないtunnel名を指す不備があり2026-07-05に是正された履歴がある（config.ymlコメントより）

## Reproduction Conditions（再現条件）

- くろこが確認した範囲: ローカル環境（Windows）から`curl`によるHTTP直接リクエストで、mcp.nsjp.org経由のMCPサーバーの応答を検証。認証ヘッダ等は付与せず、素のGET/POSTのみ
- 未実施: claude.ai web chat上でのConnector登録・tool_search・invocation操作（ブラウザ操作が必要なためくろこ単独では不可）
- 未実施: `.env`変更を伴う比較実験（TASK-5比較2、制約により見送り）

## Failure Boundary（どこまで成功したか）

```
MCP Server                         PASS （curl直接確認）
  |
HTTP Transport                     PASS （JSON-RPC応答正常）
  |
Tunnel / Public Endpoint           MIXED（mcp.nsjp.org: PASS / .envのngrok URL: FAIL・不通）
  |
OAuth Protected Resource Metadata  FAIL （resource値が到達可能URLと不一致。issuer/authorization_serversも未定義）
  |
Connector Registration             NOT CONFIRMED（ユーザー申告: Connected。くろこ未検証）
  |
Tool Discovery                     AMBIGUOUS（ユーザー申告: 表示あり。ただし管理画面表示とchat内tool_searchの区別が未確定）
  |
Chat Session Tool Index            NOT CONFIRMED（TASK-4参照、追加確認が必要）
  |
Tool Invocation                    FAIL （ユーザー申告: 利用不可）
```

## Hypothesis（優先順位付き、原因断定ではない）

優先度1: OAuth resource / endpoint identity mismatch
- 内容: サーバーが申告する`resource`値と、実際に到達可能なURLが一致していない
- 評価材料: TASK-1/TASK-3で事実として確認済み。ただしauthorization_serversが空であるため「そもそも認可必須ではない」と解釈されれば無関係という可能性も残る

優先度2: Connector registration layer
- 内容: claude.ai Connector側の登録処理が、discoveryとchatセッションへのtool伝播の間のどこかで失敗している
- 評価材料: くろこ未検証。TASK-4のケースA/B/C区別待ち

優先度3: Chat session tool propagation
- 内容: 登録済みのtoolが個別のchatセッションへ伝播しない
- 評価材料: くろこ未検証。GitHub #55914はこの層に近い症状だが、対象クライアント（Claude Code CLI）・対象コネクタ種別（claude.aiネイティブ統合）が異なるため、直接の証拠としては使えない（v1報告書で詳述済み、結論は変わらず）

## Not Confirmed（未確認事項）

- claude.ai ConnectorがMoCKA MCPサーバーに対し実際に登録しているURL（mcp.nsjp.orgか、ngrok URLか、それ以外か）
- resource不一致が実際にclaude.ai側のクライアント実装で検証されているか（仕様上あり得るという以上の確証はない）
- TASK-4のケースA/B/C区別（管理画面のtool表示とchat内tool_searchが同一事象かどうか）
- 最小構成FastMCPサーバーによる比較実験（未実施）
- endpoint/resource完全一致状態での比較実験（制約により未実施）
- バージョン文字列不一致（1.3.0 vs 1.5.0）が症状に影響しているか

---

## 調査終了条件チェック

| 項目 | 判定 |
|---|---|
| MCP Server | PASS |
| Transport | PASS |
| Tunnel | MIXED（mcp.nsjp.org PASS / .env記載のngrok URL FAIL） |
| OAuth Identity | FAIL（resource不一致確認済み。ただし影響有無は未確定） |
| Connector | NOT CONFIRMED |
| Tool Discovery | AMBIGUOUS |
| Invocation | FAIL（ユーザー申告） |

全項目が確定していないため、調査は継続中。特にConnector以降の3項目（Connector / Tool Discovery / Invocation）はユーザー側でのclaude.ai chat UI上での再確認が必要であり、くろこ単独では完了できない。

## 変更提案について

本文書は調査のみを目的とし、修正提案は含まない。TASK-1で確認した「MOCKA_ENDPOINTが死んでいるngrok URLを指している」問題への対処（`.env`の是正、TODO_422のスコープ）は、別文書・別の変更作業として、Human Gate承認を経た上で扱うべき事項である。
