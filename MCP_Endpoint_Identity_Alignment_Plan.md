# MCP Endpoint Identity Alignment Plan（修正準備調査）

作成日: 2026-07-08
作成者: くろこ (Claude Code, claude-sonnet-5)
関連: TODO_421 / TODO_422 / MCP_Bug_Fact_Verification_Report.md / MCP_Bug_Fact_Verification_Report_v2.md

本文書は「修正準備調査」であり、実際の変更は一切行っていない。以下は今回のIMMUTABLE制約:
- コード変更なし / OAuth設定変更なし / Endpoint変更なし / GitHub投稿なし
- PHL記録なしの変更は行っていない（本調査自体はファイル変更を伴わない読み取り調査のみ）
- 既存設定の全文置換は行っていない
- 原因断定は行っていない（claude.ai Connector側の症状との因果関係は依然「未確認」のまま扱う）

---

## 1. 現状問題

MoCKA MCPサーバーの公開識別情報が、3つの参照点で一致していない状態にある。

```
実稼働MCP Endpoint (mcp.nsjp.org, cloudflared Named Tunnel経由)
        != 
設定上のMOCKA_ENDPOINT (.env、死んでいるngrok URL)
        ==
OAuth protected resource metadata (mocka_mcp_server.py実行時にMOCKA_ENDPOINTから生成)
```

つまり「実稼働URL」だけが独立して正しく、「設定上のMOCKA_ENDPOINT」と「OAuth resource metadata」は同じ誤った値（死んでいるngrok URL）を指している。後者2つは同一の値なので、実質1箇所（`.env`）を直せば連動して両方是正される構造になっている（詳細はTASK-2参照）。

---

## 2. 確認済み事実（TASK-1〜TASK-4）

### TASK-1: 現在状態の一覧

| 項目 | 現在値 | 確認方法 |
|---|---|---|
| MOCKA_ENDPOINT（`.env`、gitignore対象） | `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev` | `.env`直接読み取り（再確認時点でも同一値） |
| 実公開URL（実際に到達可能） | `https://mcp.nsjp.org` | curl直接アクセスでHTTP 200確認 |
| MCP endpoint（サーバー内部の自己申告） | `/mcp`のGET応答: `{"name": "mocka-memory-caliber", "version": "1.3.0"}` | mcp.nsjp.org経由で確認 |
| cloudflared ingress（`C:\Users\sirok\.cloudflared\config.yml`） | `mcp.nsjp.org -> localhost:5002`、`gateway.nsjp.org -> localhost:5010` | ファイル直接読み取り |
| OAuth resource（`/.well-known/oauth-protected-resource`） | `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev`（MOCKA_ENDPOINTと同値） | mcp.nsjp.org経由で確認 |
| nginx設定（`deploy/nginx-mocka.conf`） | `mocka.nsjp.org`（**mcp.nsjp.orgとは別サブドメイン**）を`localhost:5002`へproxy | ファイル直接読み取り＋外部curlでHTTP 200確認（nginx応答のため、cloudflaredとは別の並行経路） |

補足: `mocka.nsjp.org`（nginx経由）は`mcp.nsjp.org`（cloudflared経由）とは異なるホスト名であり、どちらも`localhost:5002`に到達し得る構成になっている可能性があるが、今回のOAuth resource不整合とは直接関係しない別系統の公開経路として扱い、本計画の対象には含めない（混同注意）。

### TASK-2: OAuth Metadataの生成元確認

- `/.well-known/oauth-protected-resource`の`resource`値は、`mocka_mcp_server.py`の990-991行目で **実行時に`MOCKA_ENDPOINT`環境変数から直接生成**されている（固定値のハードコードではない）
  ```python
  def oauth_resource(subpath):
      return json.dumps({"resource": MOCKA_ENDPOINT or "https://localhost:5002", ...})
  ```
- したがって、このresource値を是正するために**個別のコード修正は不要**であり、`.env`のMOCKA_ENDPOINTを修正すれば連動して自動的に是正される
- `/register`（54行目付近）はリクエスト内容に関わらず固定のダミー値`{"client_id": "mocka-mcp", "client_secret": "none"}`を返す実装であり、こちらは今回の不整合（resource値の誤り）とは無関係
- `auth.py`（gateway/gateway.py側、port 5010用）にはOAuth関連ロジックは存在しない。今回のresource不整合は`mocka_mcp_server.py`（port 5002）側のみの話であり、gateway.py側には影響しない

### TASK-2追加: 今回発見した重要な経緯（git履歴より）

`.claude/mocka_config.json`のgit履歴を確認したところ、**本日 2026-07-08 07:33 JST**（本調査より数時間前）に、以下のコミットが既に存在することを確認した:

```
commit 4de3f46b4
Author: NSJP_kimura <m_kimura@nsjp.org>
Date:   Wed Jul 8 07:33:43 2026 +0900
Memory Caliber (mocka_mcp_server.py) endpoint: replace ngrok exposure with
canonical mcp.nsjp.org route (TODO_370/371, IC_20260707_006)
```

このコミットの実際の変更内容（`git show`で確認済み）:
- `.claude/mocka_config.json`: `mcp_endpoint`をngrok URLから`https://mcp.nsjp.org`へ変更（既に是正済み）
- `MoCKA-START.bat`: 起動時に`ngrok start mocka_mcp`を実行する`MoCKA-NGROK`タブの起動行を削除（ngrok起動自体を廃止）

**しかし`.env`は`.gitignore`に列挙されておりgit管理外**（`git check-ignore -v .env`で確認済み）であるため、このコミットは`.env`のMOCKA_ENDPOINTには一切触れていない。本調査時点で`.env`を直接読み取った結果、依然として古いngrok URLのままであることを確認した。

この事実から、次の点が構造的に説明できる（推測ではなく、gitの仕組み上必然の帰結として）:
- git管理下のファイル（`.claude/mocka_config.json`、`MoCKA-START.bat`）は今朝のコミットで是正済み
- git管理外の`.env`は、コミットという操作の性質上、このコミットでは変更され得なかった
- さらに`MoCKA-START.bat`からngrok起動タブ自体が削除されたため、**今後この`.env`のngrok URLは（誰かが再度ngrokを手動起動しない限り）恒久的に不通のまま**になる

参考（要確認・断定しない）: このコミットメッセージは`IC_20260707_006`を根拠として引用しているが、くろこの永続記憶に残る`IC_20260707_006`の要約は「AUTO_SEALバイパス」に関するものであり、今回のngrok/endpoint是正とは異なる内容を指している。同一IC番号が複数の関連是正をまとめて指しているのか、あるいはメモリの記録内容が不完全なのかは、Integrity Classification台帳（`data/integrity/integrity_classification.jsonl`）の一次データで確認する必要がある。本計画では未確認事項として扱う。

### TASK-3: canonical endpoint候補（mcp.nsjp.org）の各層確認

| 層 | 確認内容 | 結果 |
|---|---|---|
| DNS/接続 | curlによる名前解決＋接続 | 成功（HTTP 200応答を得ている以上、名前解決・接続とも成立） |
| tunnel | cloudflared.exeプロセス稼働、`config.yml`のingressルール一致 | 稼働中、ingress設定は`mcp.nsjp.org -> localhost:5002`で一致 |
| TLS | curl（`-k`なし）でSSLエラーなくHTTP 200を取得 | 有効な証明書チェーンとして扱われている（curlはデフォルトで検証するため、エラー無しの応答自体が証跡） |
| MCP endpoint | `/mcp`のGET/POST（initialize, tools/list, tools/call） | 全て正常応答（前回報告書で確認済み、本調査で再確認） |
| OAuth metadata | `resource`値 | **不一致（死んでいるngrok URLのまま）。これが唯一是正が必要な層** |

結論: `mcp.nsjp.org`はDNS・tunnel・TLS・MCP endpointの4層では既に整合しており、**OAuth metadataの1層のみ**が取り残されている状態。これは「決定」ではなく「現状の技術的整合性の確認」に留める（TASK-3の指示通り）。

### TASK-4: 修正影響範囲

| 修正候補 | 対象ファイル | 現状 | 必要な変更（案、未実施） | リスク目安 |
|---|---|---|---|---|
| MOCKA_ENDPOINT更新 | `.env`（gitignore対象、ローカルのみ） | 死んでいるngrok URL | `https://mcp.nsjp.org`へ書き換え | 中。mocka_mcp_server.pyは起動時にしか環境変数を読まない（54行目）ため、書き換え後はプロセス再起動が必須。再起動により稼働中セッションが一時切断される |
| OAuth resource更新 | 個別ファイルなし（990-991行目で実行時生成） | MOCKA_ENDPOINTに連動して誤り | 追加変更不要 | 低（コード変更ゼロ） |
| README/document更新 | `.env.example` | プレースホルダーが`https://your-ngrok-url.ngrok-free.app`のまま（ngrok前提の記述が残存） | `https://mcp.nsjp.org`系の記述例へ更新 | 低（テンプレートのみ、実行系に影響なし） |
| README/document更新 | `docs/governance/CONFIGURATION_SSOT_INVENTORY_v0.1.md` | 39-42行目で`.claude/mocka_config.json`の**旧ngrok値**を引用したまま（一次データは既に是正済みだが、この文書は追いついていない） | 「2026-07-08 commit 4de3f46b4で是正済み」の追記 | 低（ドキュメントのみ） |
| 起動設定更新 | `MoCKA-START.bat` | 本日のコミットで既にngrokタブ削除済み | 追加変更不要（確認のみで完了） | なし |

対象外として明確に除外するもの（記録の改変になるため触れない）:
- `data/`配下のイベントログ・TODO記録・スナップショット類（`events_latest.json`, `MOCKA_TODO*.json`, `context_snapshots/*`等）に含まれるngrok URLの記述は、過去時点の記録であり書き換え禁止
- `app_backup_*.py` / `app_bak_*.py`等のバックアップファイルは不使用ファイルであり対象外
- `mocka.nsjp.org`（nginx経由の別サブドメイン）は今回のOAuth resource不整合の対象外（TASK-1補足参照）

---

## 3. 修正方法（案、未実施）

1. `.env`の`MOCKA_ENDPOINT`を`https://mcp.nsjp.org`へ書き換える（1行のみの変更、全文置換ではない）
2. `mocka_mcp_server.py`のプロセスを再起動する（環境変数の再読み込みのため必須）
3. 再起動後、TASK-6の検証項目（後述）を実施し、OAuth resource値が`mcp.nsjp.org`に変わったことを確認する
4. （任意・低優先度）`.env.example`のプレースホルダーと`docs/governance/CONFIGURATION_SSOT_INVENTORY_v0.1.md`の記述を実態に合わせて更新する

上記はあくまで案であり、本文書の作成時点では一切実施していない。

---

## 4. リスク

- プロセス再起動に伴い、`mocka_mcp_server.py`（port 5002）が一時的に応答不能になる時間が発生する（稼働中の他クライアント・GPT/Copilot等のgateway経由アクセスには影響しない想定だが、port 5002を直接叩いている経路があれば影響を受ける）
- `.env`書き換え後もclaude.ai Connector側の症状が変わらない場合、「MoCKA側の識別不整合が原因ではなかった」と切り分けられる一方で、変更自体が別の未知の影響を生まないことは保証できない（例: 何らかの別コンポーネントが古いngrok URLを前提に動いている可能性が、TASK-4で洗い出した範囲外に潜在している可能性はゼロではない）
- `.env`はgitignore対象のため、変更前の値を明示的にバックアップしない限りgit経由でのrollbackができない

---

## 5. Rollback方法

- `.env`はgit管理外のため、書き換え前に手動でバックアップを取得する（例: `.env.bak_20260708`として複製）ことで、問題発生時は複製ファイルを戻すだけで即座に復元可能
- `.env.example`・governance文書側の変更は通常のgit管理下にあるため、`git revert`で復元可能
- プロセス再起動によるrollbackは、`.env`を旧値に戻した上で再度プロセスを再起動するのみで完了する（永続的な状態変更を伴わない）

---

## 6. Human Gate要否

| 対象 | Human Gate | 理由 |
|---|---|---|
| `.env`のMOCKA_ENDPOINT書き換え＋プロセス再起動 | **要（きむら博士の承認が必要）** | 認証・識別情報に関わる設定変更であり、かつ現在進行中のバグ調査対象そのものに手を入れる操作のため。実施後は「調査対象の状態が変わった」ことになり、以降の切り分け結果の解釈にも影響する |
| `.env.example`のプレースホルダー更新 | 任意（軽微、ドキュメントのみ） | 実行系に影響しないため、Human Gateなしでも比較的低リスクだが、他のドキュメント更新と合わせてまとめて承認を得るのが望ましい |
| `docs/governance/CONFIGURATION_SSOT_INVENTORY_v0.1.md`の追記 | 任意（軽微、ドキュメントのみ） | 同上 |

---

## TASK-6: 修正後検証項目（実装後に確認する項目、今回は未実施）

1. MCP endpoint response: `GET https://mcp.nsjp.org/mcp` が正常なJSON（name/version）を返すこと
2. tools/list: `POST /mcp` `tools/list`が23個のtoolスキーマを返すこと（是正前と同じ内容で変化がないことも確認）
3. tools/call: `mocka_get_overview`等の読み取り専用toolが正常応答すること
4. OAuth metadata resource: `GET /.well-known/oauth-protected-resource`の`resource`値が`https://mcp.nsjp.org`に変わっていること（死んでいるngrok URLが消えていること）
5. claude.ai Connector reconnect: claude.ai側のConnector設定画面で対象Connector（`claude_ai_MoCKA_Memory_Caliber2_01`）を一度切断・再接続し、Connected表示が引き続き成立すること
6. tool discovery: 新規chatセッション内で`mocka_`系toolに対する`tool_search`が結果を返すこと
7. tool invocation: 新規chatセッション内で実際に読み取り専用tool（例: `mocka_get_todo`）を呼び出し、エラーなく実データが返ること

上記1〜4はくろこ（Claude Code、curl相当の直接検証）で確認可能。5〜7はclaude.ai web chat UIでの操作が必要なため、ユーザー側での実施が必要。

---

## 完了条件（本文書自体の完了判定）

| 項目 | 状態 |
|---|---|
| 現在不整合箇所 | 確定（`.env`のMOCKA_ENDPOINTおよびそれに連動するOAuth resource値。原因はgitignore対象ファイルが今朝のcommitの対象外だったという構造的事実で説明可能） |
| 修正対象 | 確定（`.env`本体、任意で`.env.example`・governance文書1件） |
| 変更ファイル | 一覧化済み（TASK-4表参照） |
| 実装リスク | 評価済み（4節参照。主リスクはプロセス再起動時のダウンタイムと、範囲外の未知依存の可能性） |
| Human Gate対象 | 判定済み（`.env`本体の変更はHuman Gate必須、ドキュメントのみの変更は任意） |

この段階ではまだ何も修正していない。次のアクションは、きむら博士による`.env`書き換え＋再起動の承認可否判断となる。承認された場合、実施はPHL記録（CHANGE_START/CHANGE_DONE）を伴う別作業として行う。
