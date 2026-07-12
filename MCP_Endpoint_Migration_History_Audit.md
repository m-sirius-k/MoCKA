# MCP Endpoint Migration History Audit

作成日: 2026-07-08
作成者: くろこ (Claude Code, claude-sonnet-5)
関連: MCP_Final_Recovery_Report.md / MCP_Recovery_Verification_Report.md / MCP_Endpoint_Identity_Alignment_Plan.md / MCP_Bug_Fact_Verification_Report_v2.md / TODO_421 / TODO_422

**冒頭に最重要事項を記載する。** 本監査の過程で、今回の一連の「識別子不整合の是正」作業とは独立に、**2026-07-03時点できむら博士自身が実施した詳細調査により、本件は既にclaude.aiバックエンド側の問題として切り分け済みで、Anthropicへ公式報告済みだった**という事実が判明した（`X:\down\MoCKA_Connector_Investigation_Report_2026-07-03.md`）。これは本監査で得た他のどの発見よりも重要度が高いため、末尾ではなく冒頭に記載する。

---

## 0. 最重要発見: 2026-07-03調査報告書との関係

### 発見の経緯

`data/events.db`内の記録（`event_id: E20260703_940641396d615`、2026-07-03 09:12 JST）を辿り、参照元ファイル`X:\down\MoCKA_Connector_Investigation_Report_2026-07-03.md`を直接確認した。

### 2026-07-03報告書の要点（原文の要約、改変なし）

- 対象は今回と**同一のConnector**「MoCKA Memory Caliber2.01」（`724b556c-6b48-401e-91a3-035b280e9f30`）
- 当時のngrok URLで、以下を**全て検証の上で否定**している:
  - ngrok無料プラン警告ページ説
  - 旧チャットのツールスナップショット固定説
  - Connector二重登録説（きむら博士がSettings画面を直接目視確認: 「Connectorは1件のみ、URLも正しい」）
  - OAuth/認証トークン不整合説（サーバーは無認証で動作、そもそも検証対象が存在しない）
  - MCPサーバー未到達・停止説
- **ngrok Inspector(`127.0.0.1:4040`)による実測**で、claude.aiのバックエンドが実際に`POST /mcp`×3・`GET /mcp`×1を送信し、**全て200 OK**で応答を受け取っていることを確認
- それにもかかわらず、直後に同じチャットで`tool_search`を実行しても**MoCKA系ツールはゼロ件のまま**
- 結論（未確定だが最有力）: **「claude.aiバックエンド側でのハンドシェイク成功後のツール一覧伝播失敗」**
- Anthropic公式のバグ報告窓口（GitHub `anthropics/claude-ai-mcp`）へ**既に報告済み・回答待ち**（2026-07-03時点）
- 本監査時点（2026-07-08）で、その後のAnthropicからの回答記録は見当たらない（events.db検索で確認、続報なし）

### この発見が意味すること

2026-07-03時点で、**サーバー・ネットワーク経路・Connector設定（URLを含む）はすべて正しく機能していた**ことが、ngrok Inspectorでのパケットレベルの実測によって確認されている。つまり、当時のConnector登録URLは（ngrok経由ではあったが）正しく、ハンドシェイクも成功していた。それでもtool_search/invocationは失敗していた。

一方、くろこが本日（2026-07-08）までに発見・是正した「`.env`のMOCKA_ENDPOINTが死んでいるngrok URLを指し、OAuth resource metadataと不一致だった」問題は、**2026-07-03の調査時点ではまだ発生していなかった、あるいは無関係だった可能性が高い**。この識別子不整合は、TODO_266（Cloudflare Named Tunnel構築、2026-07-06完了）以降にMoCKAの公開経路がngrokからmcp.nsjp.orgへ移行する過程で新たに生じた、**別の・より新しい**問題と見るのが整合的である。

したがって、以下の2つは区別して扱うべき、独立した事象である可能性が高い:

1. **claude.ai Web UI側のtool一覧伝播バグ**（2026-07-03に確認・Anthropicへ報告済み。MoCKA側の設定とは無関係と、きむら博士自身がパケットレベルの実測で結論済み）
2. **MoCKA側のOAuth resource識別子不整合**（本日くろこが発見・是正。TODO_266移行に伴う`.env`是正漏れ）

**本日の`.env`是正（#2）は、正当な設定衛生上の是正ではあるが、#1が実際にclaude.ai側のバグであった場合、tool discovery/invocationの症状そのものを解消する保証はない。** この点を過大評価しないよう、この監査報告の冒頭で明記する。

---

## 1. Migration Timeline（①→②→③）の証跡化

### ① 旧endpoint: `https://taekwondo-glove-womb.ngrok-free.dev/mcp`（想定）

| 項目 | 内容 |
|---|---|
| 作成時期 | 2026-04-14以前（正確な作成日は不明。同日のTODO_022完了記録が最古の言及） |
| 利用開始時期 | 不明（2026-04-14時点で「旧ドメイン」として言及されているため、それ以前から使用） |
| 用途 | `interface/ping_generator.py`の`NGROK_URL`変数（ngrokトンネル生存監視・index.html上のステータス表示用）。**MCPサーバー本体(`mocka_mcp_server.py`)のMOCKA_ENDPOINTとして直接使われていた一次証跡は確認できていない**（ping監視用途との関連が確認できた範囲） |
| 廃止状態 | **完全廃止・現在404**（本日curlで再確認）。2026-04-14のTODO_022（commit `4a8ede7`）で`arnulfo-pseudopopular-unvirulently.ngrok-free.app`へ置換され、`ping_generator.py`は全文書き直しされた |
| 記録上の根拠 | `PlanningCaliber/Experiment_v2.0/essence_out/master_essence.json`内のevent記録（`E20260414_013`）: 「TODO_022完了: NGROK_URL修正・ping_generator.py全文書き直し...taekwondo-glove-womb（旧ドメイン）のままだったため...arnulfo-pseudopopular-unvirulently.ngrok-free.appに修正」 |
| git履歴 | `git log -S"taekwondo-glove-womb"`で3コミットがヒット（`90b9d280a`2026-04-16、`b7da3dc47`2026-06-11、`64d09f190`2026-06-11）。いずれもイベントログ・essenceファイル内の過去記録としての言及であり、稼働中設定ファイルとしての言及ではない |

補足（重要な留保）: ①がMCPサーバー本体の公開URLとして実際に使われていたかどうかは、今回確認できた一次データ（ping_generator.py関連の記録）からは断定できない。ただし、ngrok無料プランの固定サブドメインは同一トンネル全体に対して割り当てられる性質上、ping監視対象のドメインとMCPサーバー公開ドメインが同一であった可能性は高いが、これは推定であり確定事実ではない。

### ② 移行試験endpoint: `https://mcp.nsjp.org/mcp`

| 項目 | 内容 |
|---|---|
| 作成時期 | `cloudflare/setup_named_tunnel.bat`（TODO_266）によるNamed Tunnel構築。project memoryにより2026-07-06完了と記録 |
| 利用開始時期 | 2026-07-06以降。cloudflared Named Tunnel（tunnel ID: `efb26375-013a-48d3-a31b-a2f70e10e5a6`、実体名`mocka-gateway`）のingress設定（`C:\Users\sirok\.cloudflared\config.yml`）で`mcp.nsjp.org -> localhost:5002`とルーティング |
| 用途 | `mocka_mcp_server.py`（port 5002）への公開経路そのもの |
| 現状 | **現役・完全に正常動作**。本日の検証で`/mcp`のGET/POST（initialize, tools/list, tools/call）すべて正常応答を確認済み |
| DNS/tunnel設定履歴 | `config.yml`のコメントに、当初「存在しないtunnel名`mocka-mcp`」を指す設定不備があり、2026-07-05に実体`mocka-gateway`へ是正された経緯が記録されている（これも同種の識別子不整合の前例） |

### ③ 現行候補endpoint: `https://mcp.nsjp.org`（パスなし、root）

| 項目 | 内容 |
|---|---|
| 実測結果 | **本日curlで確認: HTTP 404 Not Found**（Cloudflare経由でFlaskアプリまで到達しているが、`/`に対応するルートハンドラが存在しないため404） |
| 結論 | root URL単体は**有効なMCPエンドポイントではない**。実際に機能するのは`/mcp`パスを含む②のみ |

---

## 2. 接続経路確認

- Claude側が参照していたURL: 2026-07-03時点ではngrok URL（当時「Settings画面上ではURL正」と確認されていた、具体的などのngrokサブドメインかは報告書に明記なし）。本日時点でclaude.ai Connector設定画面に実際に登録されているURLは、くろこの手元からは確認不能（claude.ai側の設定はローカルファイルに保存されないため）
- サーバー側で受信していたendpoint: `mocka_mcp_server.py`の`/mcp`ルートのみ（GET/POST）。root(`/`)への対応ルートは存在しない
- tools discovery結果: 2026-07-03のCLIセッションでのくろこの実証では17ツール全てが正常表示・呼び出し成功（当時の合計tool数は17件。本日時点では23件に増加しており、この間にtoolが追加されていることが分かる。これは移行そのものとは無関係な、通常の機能追加による差分）
- endpoint path差異: `/mcp`ありが正、rootのみは404。この差異が今回の監査で新たに判明した最も具体的な技術的事実である

---

## 3. 移行判断

### A: 旧endpoint①は完全廃止対象か

**Yes。** 本日のcurlで404（`ERR_NGROK_3200`相当、ドメイン自体が無応答）を確認済み。加えて、2026-04-14の時点で既に一度置換されており、その後継（`arnulfo-pseudopopular-unvirulently`）も本日までに死んでいたことをくろこが確認・是正済み（`.env`修正、MCP_Recovery_Verification_Report.md参照）。①・その後継とも、現在生きている設定ファイルの中に残存していない（`.env`は是正済み、`.claude/mocka_config.json`は本日07:33のcommitで是正済み、`ping_generator.py`は2026-04-14に是正済み）。

### B: ②`/mcp`は内部endpointなのか公開canonical endpointなのか

**公開canonical endpointそのものである。** 「内部」ではない。curlによる外部からの直接検証で、`initialize`・`tools/list`・`tools/call`すべてが`/mcp`パスに対して正常応答することを確認済み。`mcp.nsjp.org`ドメインの公開APIとして、`/mcp`パスがそのまま実体である。

### C: ③root URLがClaude Connector登録用canonical URLなのか

**いいえ。** root URL単体（`https://mcp.nsjp.org`）は404であり、Connector登録用のURLとしては機能しない。**登録すべきは`/mcp`パスを含む`https://mcp.nsjp.org/mcp`である。**

### 追加で判明した懸念事項（新規発見）

本日くろこが是正した`.env`の`MOCKA_ENDPOINT`は`https://mcp.nsjp.org`（**パスなし**）に設定されている。これは`oauth_resource()`関数（`mocka_mcp_server.py:990-991`）で生成されるOAuth Protected Resource Metadataの`resource`値としてそのまま使われる。しかし、OAuth 2.0 Protected Resource Metadata（RFC 9728）およびMCP Authorization仕様の一般的な想定では、`resource`値は実際に保護されているリソースの正確なURI（パス込み）を指すべきとされる場合がある。今回の是正で`resource`値をngrokの死んだURLから`mcp.nsjp.org`（root）へ変更したことで従来より改善はしたが、**厳密には`https://mcp.nsjp.org/mcp`（パス込み）にすべきではないか、という新たな検討点が残る。** これは原因断定ではなく、追加で確認・判断が必要な事項として提示する。今回のIMMUTABLE制約の範囲外（設定変更を伴う）のため、くろこはこの追加変更を実施していない。

---

## 4. 最終報告

```
Migration Timeline:
① https://taekwondo-glove-womb.ngrok-free.dev (ping_generator.py用、2026-04-14以前～2026-04-14に是正・現在404で完全廃止)
  ↓
(中間: arnulfo-pseudopopular-unvirulently.ngrok-free.dev/.app 系、2026-04-14是正で導入、.envにも長期間残存、本日2026-07-08に是正・現在404)
  ↓
② https://mcp.nsjp.org/mcp (Cloudflare Named Tunnel、2026-07-06本稼働開始、現役・正常動作)
  ↓
③ https://mcp.nsjp.org (root、パスなし。404であり実際にはendpointとして機能しない)

Current Canonical Endpoint:
https://mcp.nsjp.org/mcp

Claude Connector Recommended Registration:
https://mcp.nsjp.org/mcp （root単体ではなく、/mcpパスを含む形）

旧設定削除可否:
Yes（実質的にはすでに完了。①・その後継のngrok URLは生きている設定ファイルからは既に排除済み。残るのは.env.exampleのプレースホルダーとgovernance文書1件の記述更新のみで、いずれも軽微・任意）

根拠:
- curl実測（①③は404、②は200 OK・正常JSON-RPC応答）
- git log -S によるコミット履歴（2026-04-14 commit 4a8ede7、2026-07-08 commit 4de3f46b4）
- events.db内の一次記録（E20260414_013、E20260703_940641396d615）
- X:\down\MoCKA_Connector_Investigation_Report_2026-07-03.md（きむら博士による2026-07-03の直接実証）
- cloudflared config.yml（ingress設定、tunnel ID・実体名の是正履歴を含む）
```

---

## 5. 未解決・要確認事項（今回新たに判明したもの）

1. **最重要**: 2026-07-03の調査で「claude.aiバックエンド側のツール一覧伝播バグ」と切り分け済みであり、Anthropicへ報告済み・回答待ちのまま。本日のMoCKA側是正がこの症状自体を解消するかは未確認（0節参照）
2. `.env`の`MOCKA_ENDPOINT`（および連動するOAuth resource値）が現在パスなしの`https://mcp.nsjp.org`になっている点。`/mcp`パスを含めるべきかどうかは追加の検討・Human Gate判断が必要
3. commitメッセージが引用する`TODO_370/371`の一次データ（`data/MOCKA_TODO_ACTIVE.json`）を確認したところ、実際の内容は「events.db/mocka_write_event経由の正本記録の信頼性実測」という、**エンドポイント移行とは無関係な別テーマ**だった。前回報告した`IC_20260707_006`の不一致（AUTO_SEALバイパス関連 vs 今回のendpoint是正）に続き、**2件目の「commitメッセージの引用ID」と「一次データの内容」の不一致**である。これは偶発的な誤記の可能性もあるが、複数件重なっているため、commitメッセージのTODO/IC引用そのものの信頼性について、別途確認する価値がある
4. 2026-07-03報告書内の副次的発見（COMMAND CENTER静的HTML問題、`.claude.json`内のGitHub PAT平文記載）は今回未着手のまま。特に後者はセキュリティ上の推奨事項（トークンローテーション）であり、本監査の対象外だが記録として残す
