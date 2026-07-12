# MCP Recovery Verification Report

作成日: 2026-07-08
作成者: くろこ (Claude Code, claude-sonnet-5)
承認: きむら博士によるHuman Gate承認済み復旧作業（本人からの指示に基づき実施）
関連: TODO_421 / TODO_422 / MCP_Bug_Fact_Verification_Report.md / MCP_Bug_Fact_Verification_Report_v2.md / MCP_Endpoint_Identity_Alignment_Plan.md

IMMUTABLE制約の遵守状況:
- 記録なしの変更: なし（CHANGE_START/CHANGE_DONEとも実施・読み戻し確認済み）
- PHL記録: 実施済み（下記参照）
- 変更前状態保存: `.env.bak_20260708`として保存済み
- rollback可能状態: 維持（バックアップからの復元＋プロセス再起動のみで戻せる）
- `git add -A`: 実行していない
- 不要ファイル変更: なし（`.env`の1行のみ変更、他プロセス・他ファイルは無変更）
- 原因断定: 行っていない（claude.ai Connector側の症状との因果関係は「未確認」のまま）
- GitHub投稿: 行っていない（本報告書作成の時点で停止）

---

## 1. 修正前状態

| 項目 | 値 |
|---|---|
| `.env` MOCKA_ENDPOINT | `https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev`（ERR_NGROK_3200で不通） |
| MCP endpoint `/mcp`（GET） | `{"name": "mocka-memory-caliber", "version": "1.3.0"}` |
| OAuth resource（`/.well-known/oauth-protected-resource`） | `{"resource": "https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev", "authorization_servers": []}` |
| mocka_mcp_server.pyプロセス | PID 1768（`python -X utf8 mocka_mcp_server.py`、cwd: `C:\Users\sirok\MoCKA`） |
| cloudflared | PID 4704、Windowsサービスとして稼働中（変更対象外） |
| MoCKA-START.bat | 本日07:33のcommit 4de3f46b4で既にngrok起動タブ削除済み（確認のみ、追加変更なし） |

---

## 2. 修正内容

- 対象ファイル: `C:\Users\sirok\MoCKA\.env`（1行のみ変更、他行は無変更をdiffで確認済み）
  - 変更前: `MOCKA_ENDPOINT=https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev`
  - 変更後: `MOCKA_ENDPOINT=https://mcp.nsjp.org`
- バックアップ: `C:\Users\sirok\MoCKA\.env.bak_20260708`として変更前の内容を保存済み
- プロセス再起動: `mocka_mcp_server.py`のみを対象に、狙い撃ちで実施
  - 旧PID 1768を`Stop-Process`で停止
  - `python -X utf8 mocka_mcp_server.py`（cwd: `C:\Users\sirok\MoCKA`）で再起動、新PID 7056
  - `gateway.py`（port 5010）・`cloudflared`・`app.py`等、他の稼働中プロセスは**無停止・無変更**（TASK-4調査で判明した通り、これらはMOCKA_ENDPOINTを参照しないため対象外と判断）
- PHL記録:
  - CHANGE_START: `event_id E20260708_703503351484a`（読み戻し確認済み）
  - CHANGE_DONE: `event_id E20260708_831489052a761`（読み戻し確認済み）

---

## 3. 検証結果（修正後）

| 確認項目 | 結果 |
|---|---|
| `/health`（localhost） | `version: 1.5.0, tools: 23`（修正前と同一、リグレッションなし） |
| `/mcp`（GET、localhost） | `{"name": "mocka-memory-caliber", "version": "1.3.0"}`（変化なし。バージョン文字列不一致は今回のスコープ外の既知事項として残存） |
| OAuth resource（localhost経由） | `{"resource": "https://mcp.nsjp.org", "authorization_servers": []}` **是正確認** |
| OAuth resource（mcp.nsjp.org経由、外部トンネル込み） | `{"resource": "https://mcp.nsjp.org", "authorization_servers": []}` **是正確認（外部到達性込みで一致）** |
| tools/list（mcp.nsjp.org経由） | 23件、変化なし |
| tools/call `mocka_get_overview`（mcp.nsjp.org経由） | HTTP 200、正常応答 |

くろこが直接確認できる範囲（MCP Server〜OAuth Identity層）は、すべて是正・正常動作を確認した。

---

## 4. MCP状態

```
MCP Server                        PASS
Transport                         PASS
Tunnel (mcp.nsjp.org)              PASS
OAuth Identity (resource一致)       PASS （修正前FAILから是正）
```

---

## 5. Claude Connector結果

**未確認（くろこ単独では実施不可）**

理由: claude.ai web chatのConnector UI（Connected表示・tool_search・invocation）はブラウザ操作を要し、Claude Code CLIセッションであるくろこからは直接操作・観測できない。

きむら博士に依頼したい確認事項（TASK-6分類に基づく）:
1. claude.ai Connector設定画面で対象Connector（`claude_ai_MoCKA_Memory_Caliber2_01`）を一度切断・再接続する
2. 新規chatセッションを開始し、`mocka_`系toolに対して`tool_search`を実行する
3. 結果を以下のいずれかで分類して報告いただきたい:
   - **Case A**: tool表示なし → Connector登録層の問題として切り分け（MoCKA側の是正だけでは解決しない別問題の可能性が高い）
   - **Case B**: tool表示あり、invoke成功 → **復旧**（識別子不整合が実質的な原因だったと強く言える）
   - **Case C**: tool表示あり、invoke失敗 → Connector実行層（execution/auth層）の問題として調査継続

この結果次第で、次にGitHubへ追記する内容の精度が大きく変わる。

---

## 6. 未解決事項

- claude.ai Connector層の実際の挙動（上記5参照、ユーザー確認待ち）
- `/mcp`のGET応答・`initialize`応答内`serverInfo.version`が引き続き`1.3.0`固定であり、`/health`の`1.5.0`と不一致のまま（今回の修正スコープ外、影響有無は未確認）
- `.env.example`のプレースホルダーが依然`https://your-ngrok-url.ngrok-free.app`のまま（Alignment Planで軽微・任意対応と分類、今回は未実施）
- `docs/governance/CONFIGURATION_SSOT_INVENTORY_v0.1.md`が`.claude/mocka_config.json`の旧ngrok値を引用したままで一次データと乖離（同上、今回は未実施）
- commitメッセージが引用する`IC_20260707_006`と、くろこの記憶にある同番号の要約（「AUTO_SEALバイパス」）との不一致（Integrity Classification台帳の一次データでの確認が別途必要、本作業のスコープ外）
- `mocka.nsjp.org`（nginx経由の別サブドメイン）との関係性は未調査のまま（今回のOAuth resource是正とは無関係と判断し対象外としたが、念のため未解決事項として記録）

---

## 7. 次判断

- MoCKA側で確認可能な範囲（MCP Server / Transport / Tunnel / OAuth Identity）はすべてPASSに是正済み。これ以上MoCKA側だけで進められる調査・修正はない
- 次のアクションは、きむら博士による claude.ai Connector側の再接続・tool_search・invocation確認（上記5節）
- Case Bだった場合: 復旧完了として扱い、GitHub追記は不要（そもそも今回のIssue #55914等は同一バグではないと既に整理済みのため、新規報告自体が不要になる可能性が高い）
- Case AまたはCだった場合: MoCKA側の識別子不整合は是正済みという事実を踏まえた上で、残った症状のみを対象にGitHub追記を検討する（原因断定はせず、「MoCKA側のOAuth resource識別子不整合を是正した後もこの症状が再現する」という、より強い証拠を添えて報告できる）

---

## 完了条件

```
.env修正:        完了
PHL:             CHANGE_START=E20260708_703503351484a / CHANGE_DONE=E20260708_831489052a761（いずれも読み戻し確認済み）

MCP Server:      PASS
OAuth Identity:  PASS
Connector:       未確認
tool invocation: 未確認
```
