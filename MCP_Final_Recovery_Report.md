# MCP Final Recovery Report

作成日: 2026-07-08
作成者: くろこ (Claude Code, claude-sonnet-5)
関連: MCP_Recovery_Verification_Report.md / MCP_Bug_Fact_Verification_Report_v2.md / MCP_Endpoint_Identity_Alignment_Plan.md / MCP_FINAL_RECOVERY_BEFORE.md / TODO_421 / TODO_422

IMMUTABLE制約の遵守状況: 新規設計・MCP仕様変更・Gate/Policy変更・app.py変更・restart_mocka.bat実行・不要プロセス停止・`.env`以外の設定変更・記録なしの変更は、いずれも行っていない。本セッションでのファイル変更は前回セッションで実施済みの`.env`1行のみで、今回は追加の変更を一切行わず、検証のみを実施した。

---

## 復旧対象

MoCKA MCP Server（`mocka_mcp_server.py`、port 5002、公開経路`mcp.nsjp.org`）が、claude.ai MCP Connector経由でtool利用不可となっていた問題。

## 発見原因（識別子不整合。claude.ai側との因果関係は断定しない）

`.env`の`MOCKA_ENDPOINT`が死んでいるngrok URL（`ERR_NGROK_3200`）を指しており、これがそのままOAuth Protected Resource Metadataの`resource`値として外部に提示され、実際に到達可能な公開URL（`mcp.nsjp.org`）と一致していなかった。

git履歴確認により、本日07:33のcommit `4de3f46b4`で`.claude/mocka_config.json`と`MoCKA-START.bat`（ngrok起動タブ）は既に是正済みだったが、`.env`はgitignore対象のためこのコミットの範囲外となり、是正が漏れていたことを確認済み（詳細: MCP_Endpoint_Identity_Alignment_Plan.md）。

## 修正内容

- `C:\Users\sirok\MoCKA\.env`の`MOCKA_ENDPOINT`を1行のみ変更（`https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev` → `https://mcp.nsjp.org`）
- 変更前バックアップ: `.env.bak_20260708`
- `mocka_mcp_server.py`プロセスのみを狙い撃ちで再起動（旧PID 1768 → 新PID 7056）。gateway.py・cloudflared・app.pyは無停止
- PHL記録: CHANGE_START(`E20260708_703503351484a`) / CHANGE_DONE(`E20260708_831489052a761`)、いずれも読み戻し確認済み

---

## 検証結果

### MCP Server

- `/health`: `version: 1.5.0, tools: 23`（是正前と同一、リグレッションなし）
- `mocka_mcp_server.py`プロセス: PID 7056で単一稼働（重複プロセスなし）
- `gateway.py`（port 5010）: `/api/v1/health`で`{"status":"ok","version":"1.1"}`、無変更・無停止

判定: **PASS**

### OAuth Identity

| 参照点 | 値 |
|---|---|
| `.env` MOCKA_ENDPOINT | `https://mcp.nsjp.org` |
| OAuth resource（localhost経由） | `https://mcp.nsjp.org` |
| OAuth resource（mcp.nsjp.org経由、外部トンネル込み） | `https://mcp.nsjp.org` |
| 公開endpoint（実際に到達したURL） | `https://mcp.nsjp.org`（HTTP 200） |
| MCP endpoint（`/mcp` GET応答） | `{"name": "mocka-memory-caliber", "version": "1.3.0"}`（応答自体は正常。バージョン文字列が`/health`の1.5.0と異なる点は既知の別事項として残存、identity一致には影響なし） |

4点すべてが`https://mcp.nsjp.org`で一致していることを確認した。

判定: **PASS**

### tools/list

- 23件、前回是正時と同数（リグレッションなし）
- 全23ツールのschema（`required`/`properties`）を取得・確認。異常なし
- 一覧: `mocka_get_overview`, `mocka_get_essence`, `mocka_get_todo`, `mocka_add_todo`, `mocka_update_todo`, `mocka_list_events`, `mocka_read_event`, `mocka_search`, `mocka_write_event`, `mocka_seal`, `mocka_get_incidents`, `mocka_get_guidelines`, `mocka_get_command_center`, `mocka_check_utf8`, `mocka_registry_get`, `mocka_registry_add`, `mocka_registry_current_state`, `mocka_decision_write`, `mocka_decision_get`, `mocka_decision_list`, `mocka_integrity_write`, `mocka_integrity_get`, `mocka_integrity_list`

判定: **PASS**

### tools/call

- `mocka_get_overview`: HTTP 200
- `mocka_get_todo`: HTTP 200
- `mocka_list_events`（n=1）: `"isError": false`、実データ（直前のCHANGE_DONEイベント自体）を正常返却。exceptionなし

判定: **PASS**

### Claude Connector

**未確認（USER確認待ち）**。くろこ（Claude Code CLI）からはclaude.ai web chatのConnector UIを直接操作・観測できないため、この層はきむら博士による確認が必要。

分類基準（今回の指示に基づく）:
- **Case A**: tool discovery成功 → invoke成功 → MCP復旧完了
- **Case B**: tool discovery成功 → invoke失敗 → execution/auth層の調査継続
- **Case C**: tool discovery失敗 → Connector登録/chat session index層の調査継続

### Tool Discovery / Tool Invocation（claude.ai chat内）

同上、未確認。STEP4はユーザー側の操作結果を待って判定する。

---

## もしConnector再登録が必要な場合の手順（STEP5、提示のみ）

対象: `claude_ai_MoCKA_Memory_Caliber2_01`

1. claude.ai の Connector設定画面で対象ConnectorをDisconnect
2. 再度Connect（登録済みURLが`mcp.nsjp.org`になっているか、新規登録時に確認）
3. 新規chatを作成
4. `mocka_`系toolの一覧が表示されるか確認（`tool_search`または利用可能tool一覧）
5. 表示された場合、読み取り専用tool（例: `mocka_get_overview`）を実際に呼び出し、正常応答するか確認

---

## 未解決事項

- Claude Connector層の実際の挙動（Case A/B/Cのいずれか、ユーザー確認待ち）
- `/mcp`のGET・`initialize`応答内`serverInfo.version`が`1.3.0`固定のまま、`/health`の`1.5.0`と不一致（今回のスコープ外、identity一致には影響しないことを確認済みだが、値自体は未是正）
- `.env.example`のプレースホルダーがngrok前提のまま（軽微、任意対応、未実施）
- `docs/governance/CONFIGURATION_SSOT_INVENTORY_v0.1.md`の`.claude/mocka_config.json`旧値引用（軽微、任意対応、未実施）
- commit引用の`IC_20260707_006`とくろこの記憶（「AUTO_SEALバイパス」）の不一致（Integrity Classification台帳一次データでの確認が別途必要）
- `mocka.nsjp.org`（nginx経由の別サブドメイン）との関係性（今回のOAuth resource是正とは無関係と判断、未調査のまま）

## GitHub追記案

現時点ではMoCKA側の是正が完了し、くろこが直接検証できる範囲（MCP Server / OAuth Identity / tools/list / tools/call）はすべてPASSであることのみが確定している。Claude Connector層の結果が出るまでは、GitHubへの追記は行わない。

- Case Aだった場合: 復旧完了。GitHub追記は不要と判断する（そもそも本件はGitHub issue #55914等の既存報告とは前提が異なると既に整理済みのため、新規報告自体が不要になる可能性が高い）
- Case BまたはCだった場合: 「MoCKA側のOAuth resource識別子不整合（`.env`経由でresource値が実稼働URLと不一致だった状態）を是正し、MCP Server/Transport/Tunnel/OAuth Identity/tools list/tools callがすべて直接検証でPASSした後も、claude.ai Connector側で同一症状（Case B: invoke失敗 / Case C: discovery失敗）が再現する」という、原因を断定しない形の追記案を別途作成する

---

## 完了条件

```
MCP Server:        PASS
Endpoint Identity: PASS
OAuth:             PASS
tools/list:        PASS
tools/call:        PASS
Claude Connector:  USER確認待ち

総合判定: PARTIAL（MoCKA側は復旧完了、claude.ai Connector側の最終確認のみ残存）
```
