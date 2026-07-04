# Integration Layer Audit(第5トラック)— Phase 1: Fact Collection v0.1

位置づけ: R01(GPT)/博士指示「Integration Layer Audit(第5トラック)Phase 1: Fact Collection」に基づく。役割は制度書記官・実装調整官。分類の妥当性判断・修正案・設計は行わない。MoCKAの連携基盤(MCP/Connector/ツール伝播)について、events.db記録・拡張機能設定・ログファイルから事実を収集し、指示書が示す4分類(仮)にそのまま機械的に当てはめる。分類自体の妥当性検証・追加・統合は行わない(Phase 2以降)。

---

## ① 事実収集

### 各MoCKA拡張のMCP接続先・ポート・プロトコル現状一覧

| 拡張 | 接続先/設定根拠(file:line) | 事実 |
|---|---|---|
| MCPサーバー本体 | `mocka_mcp_server.py:778`(`app.run(host="0.0.0.0", port=5002)`)、`:776`、`:749` | ポート5002で稼働 |
| Endpoint Registry | `data/MOCKA_ENDPOINTS.json`、`interface/mocka_endpoints.py` | `mocka_event_gateway`: connect_host=127.0.0.1、port=5002、path `write_event`=`/agent/mocka_write_event`(2026-07-02追加) |
| グローバルngrok設定 | `.claude/mocka_config.json:2`(`"mcp_endpoint"`)、`.env:1`(`MOCKA_ENDPOINT=`) | 共通のngrok URL(`https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev`) |
| Orchestra | `PlanningCaliber/workshop/Orchestra_Project/extension/manifest.json:30`、`content.js:463` | 上記ngrok URLへのhost_permission。`content.js:463`は`/api/handshake`(後述・別概念)への参照 |
| Relay | `PlanningCaliber/workshop/Relay_Project/extension/manifest.json:11,20` | host_permissionsは`https://claude.ai/*`のみ。現行manifest.json内にngrok/MCPエンドポイントへの言及は確認されなかった |
| Memory | `PlanningCaliber/workshop/memory/`配下(extension/icons) | MCP/ngrok/connectorという語を含むファイルは調査範囲内で確認されなかった |
| PHI-OS | `PlanningCaliber/workshop/phi-os/adapters/mocka-bridge.js:2,8,15` | `cfg.mcp_endpoint`を`.claude/mocka_config.json`から動的に読み込む設計(コード内コメント「TODO_218: ngrok URLはmocka_config.jsonに集約」) |

### 直近の接続関連イベント(events.db、時系列)

主要なものを日時順に記載する。

- 2026-06-04: `E20260604_186`「APIサーバー:接続失敗」(対象システムの詳細は本調査で確認できず)
- 2026-06-22T00:11:01Z: `E20260622_601144445e7a6`「MoCKA Architecture Map v1.0 + MCP Integration Specification v1.0 確定」(MCPを外部I/O境界層・大半の層で読み取り専用と定義)
- 2026-06-26T01:57:19Z: `E20260626_039499337e3be`(user_voice、「MCP接続(MoCKA Memory Caliber)はまだ...」、文言途中で切れている)
- 2026-06-30T03:17:42Z〜03:36:46Z: `E20260630_4622299395aa9`→`E20260630_6317439936e81`→`E20260630_089475895de71`→`E20260630_606983189f7fc`(TODO_390連鎖、詳細下記)
- 2026-07-02T03:27:18Z: `E20260702_8382502960909`(user_voice、IPv4/IPv6がMCP接続やコネクタ通信を間接的に壊しうるかという発言記録)
- 2026-07-02: `E20260702_756523253adf1`・`E20260702_91381477693d1`(起点`E20260702_1595449490459`、Endpoint Registry追加、localhost→127.0.0.1名前解決不一致の修正)
- 2026-07-03T09:12:20Z: `E20260703_940641396d615`(MoCKA Memory Caliber2.01 Connector接続障害調査、詳細下記)

### 直近の接続エラー・タイムアウト・ツール呼び出し失敗の実例

- `tools/auto_record.log`: `[2026-06-19T12:26:09.374404] WARN url=http://localhost:5002/agent/mocka_write_event tool=Bash error=timed out` → `[2026-06-19T12:26:09.375017] OFFLINE tool=Bash cmd_or_file='...' (記録未送信・作業は継続)`。同様のペアが`12:26:37`(tool=Write)にも存在。
- `mocka_mcp_server_vps.py:423,527,569,571,735`: `requests.post(..., timeout=5)`・`urllib.request.urlopen(..., timeout=3)`等のタイムアウト設定(エラーログではなく設定値)。
- `tools/mocka_orchestra_v10.py`: 複数のPlaywrightページロード/要素待機タイムアウト(39,46,61,74,79,90,127,131,136,159,187行)。ChatGPT/Gemini/Perplexity等のブラウザ自動操作に関するものでMCPプロトコル自体とは別文脈。

---

## ② 4分類への事実の当てはめ

出力形式: `[分類(1〜4/未分類)] / [対象拡張] / [発生日時] / [file:line/ログ根拠] / [事実記述のみ]`

```
[分類1] / [MoCKA本体(Claude.ai Web連携)] / [2026-06-30T03:36:46Z] / [event: E20260630_606983189f7fc、関連: E20260630_4622299395aa9/6317439936e81/089475895de71] / [mocka_get_todo()がClaude.ai側で69件(旧構造)を返し続けた。サーバー側(プロセスPID・ngrokトンネル・接続URL)はバイトレベル検証で47件返却を確認し正常と判定。原因はClaude.ai側のMCPコネクタキャッシュと特定。コネクタ設定画面「ツールリストを更新」操作で解消]

[分類1] / [MoCKA Memory Caliber2.01 Connector(claude.ai Web)] / [2026-07-03T09:12:20Z] / [event: E20260703_940641396d615、参照: X:\down\MoCKA_Connector_Investigation_Report_2026-07-03.md] / [Settings画面では「接続済み・全ツール許可」と表示される一方、claude.ai Web chatセッション(新旧とも)のtool_searchがMoCKAツールを0件と認識。ngrok Inspector(127.0.0.1:4040)でclaude.aiバックエンドからのPOST/GET /mcpに200 OKが返っていることを確認済み。文書内の有力仮説として「claude.aiバックエンド側でのハンドシェイク成功後のツール一覧伝播失敗」と記載。Anthropicバグ報告チャンネルへ報告済み・回答待ち]

[分類1] / [同上(比較対象クライアント)] / [2026-07-03T09:12:20Z] / [event: E20260703_940641396d615] / [同一Connector(ID 724b556c-6b48-401e-91a3-035b280e9f30)に対し、同一調査内でClaude Code CLI(別クライアント)からのtool_searchは17件全てのツールを正しく返し、mocka_get_overview呼び出しも成功。サーバー・トンネル・登録が健全であることを示す記録]

[分類2] / [MoCKA Memory Caliber2.01 Connector(claude.ai Web、特定クライアント視点)] / [2026-07-03T09:12:20Z] / [event: E20260703_940641396d615] / [claude.ai Web chatセッションのtool_search結果として、17件登録されているはずのMoCKAツールが0件しか認識されなかった(同時刻の別クライアントでは全件認識、上記分類1参照)]

[分類2] / [Relay] / [(現時点、日時記録なし)] / [PlanningCaliber/workshop/Relay_Project/extension/manifest.json:11,20] / [host_permissionsが"https://claude.ai/*"のみで、ngrok MCPエンドポイント("...ngrok-free.dev/*")への言及が現行manifest.json内に確認されなかった(Orchestra・PHI-OSには同エンドポイントへの参照が確認されている)]

[分類2] / [Memory] / [(現時点、日時記録なし)] / [PlanningCaliber/workshop/memory/配下(extension/icons)] / [MCP/ngrok/connectorという語を含むファイルが調査範囲内で確認されなかった]

[分類3] / [MCP Server(mocka_mcp_server_vps.py)] / [(現行コード時点、日時なし)] / [mocka_mcp_server_vps.py:21-27(EVENTS_FIELDS定義"when")、:61-62(読み出し時フォールバックマッピング)、:77(SQL INSERT文"when_ts")] / [MCPツール契約上のイベントフィールド名は"when"だが、内部DB層(SQL)は"when_ts"カラムを使用し、読み出し時に`if "when_ts" in row and "when" not in row: row["when"]=row["when_ts"]`という補完処理で差異を吸収している]

[分類3] / [Endpoint解決(mocka_event_gateway)] / [2026-07-02] / [event: E20260702_756523253adf1, E20260702_91381477693d1(起点E20260702_1595449490459)、data/MOCKA_ENDPOINTS.json、interface/mocka_endpoints.py] / [localhost→127.0.0.1という名前解決の不一致を修正するためEndpoint Registryが追加された]

[分類4] / [MCP Server(mocka_mcp_server_vps.py)] / [(現行コード時点)] / [mocka_mcp_server_vps.py:123(search_knowledge_gate内`except: pass`)] / [ファイルのparse/encode失敗時にログを残さず空の結果を返す]

[分類4] / [MCP Server(mocka_mcp_server_vps.py)] / [(現行コード時点)] / [mocka_mcp_server_vps.py:137(next_event_id内`except: nums=[]`)] / [DBクエリ・正規表現解析失敗時に記録を残さずevent_id採番をデフォルト値(E{today}_001)にフォールバックする]

[分類4] / [MCP Server(mocka_mcp_server_vps.py)] / [(現行コード時点)] / [mocka_mcp_server_vps.py:153(auto_log内`except: pass`)] / [ロギング失敗を記録せず処理を継続する]

[分類4] / [MCP Server(mocka_mcp_server_vps.py)] / [(現行コード時点)] / [mocka_mcp_server_vps.py:284,288(`.get("author","Claude")`、`.get("why_purpose","")`)] / [必須フィールド欠落時に警告なくデフォルト値へ置換してDB書き込みを完了する]

[分類4] / [ローカルgit操作記録(mocka_write_event経由)] / [2026-06-19T12:26:09,12:26:37] / [tools/auto_record.log(WARN行+OFFLINE行のペア、tool=Bash/Write、"error=timed out"、"記録未送信・作業は継続")] / [MoCKAサーバー(localhost:5002)への記録送信タイムアウト時、WARNログは残るが送信は行われずOFFLINEとして記録、後続作業はブロックされず継続する(.claude/CLAUDE.md記載の設計通りの挙動である旨の記載もあり、完全な無記録ではない)]

[未分類] / [MoCKA本体(制度層)] / [2026-06-10〜2026-06-11、2026-06-17、2026-06-20] / [interface/handshake.py、event: E20260610_010ほか、E20260617_105、E20260620_106] / [「Institution Handshake Protocol」(POST /api/handshake)は、複数AIペルソナ(claude/gpt-4o等)とロール(R01/R02、後にR03-R06)間の制度的ハンドシェイクであり、MCPプロトコルレベルのハンドシェイクとは別概念であることが確認された]

[未分類] / [Orchestra] / [(現時点)] / [PlanningCaliber/workshop/Orchestra_Project/extension/manifest.json:30、content.js:463] / [host permissionにngrok URLを含み、content.js内にも同URL+"/api/handshake"への参照がある(この参照は上記の制度ハンドシェイクエンドポイントであり、MCPツールエンドポイントとは別)]

[未分類] / [PHI-OS] / [(現時点)] / [PlanningCaliber/workshop/phi-os/adapters/mocka-bridge.js:2,8,15] / [`cfg.mcp_endpoint`を`.claude/mocka_config.json`から動的に読み込む設計。Orchestra・PHI-OSは同一ngrok URLを参照している]

[未分類] / [MoCKA本体] / [2026-06-04] / [event: E20260604_186「APIサーバー:接続失敗」] / [どのシステムに対する接続失敗かの詳細情報は本調査で確認できなかった]

[未分類] / [MoCKA本体] / [2026-06-22T00:11:01Z] / [event: E20260622_601144445e7a6「MoCKA Architecture Map v1.0 + MCP Integration Specification v1.0 確定」] / [MCPを外部I/O境界層(Input/Output/Observation Bridge)、大半の層で読み取り専用と定義する設計文書が確定した記録(障害ログではなく設計確定記録)]

[未分類] / [MoCKA本体] / [2026-06-26T01:57:19Z、2026-07-02T03:27:18Z] / [event: E20260626_039499337e3be、E20260702_8382502960909] / [それぞれ「MCP接続(MoCKA Memory Caliber)はまだ...」(文言途中で切れている)、IPv4/IPv6がMCP接続やコネクタ通信を間接的に壊しうるかという発言記録。いずれも会話上の言及であり、接続試行・失敗の実測ログではない]

[未分類] / [MCP Server(ファイル名相違)] / [(現行コード時点)] / [mocka_mcp_server.py:778,776,749(ポート5002稼働)] / [「mocka_mcp_server.py」と「mocka_mcp_server_vps.py」という2つの異なるファイル名が別々の調査で報告された。両者の関係(同一ファイルの別名か、別ファイルか、どちらが本番稼働中か)は本調査では確認していない]
```

---

## 除外事項の明記

失敗モード分類自体の妥当性検証・追加・統合、修正案・設計案の提示は一切行っていない。上記の分類への当てはめは機械的な振り分けであり、分類の正しさの判断は含まない。

---

以上、収集した事実の提示をもって本フェーズの作業を停止する。R01(GPT)と博士の判断を待つ。

---

## 改訂履歴

- v0.1(2026-07-04): R01(GPT)/博士指示「Integration Layer Audit(第5トラック)Phase 1: Fact Collection」に基づき新規作成。くろこ起草。
