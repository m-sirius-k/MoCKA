# Time OS Contract v1 (Phase5 Step3 Freeze)

Status: FROZEN（Phase5 Step4着手前の基準線として固定）
Date: 2026-06-22

本文書はPhase5 Step3完了時点でのMoCKA Time OS外部契約を固定する。
これらのエンドポイント・クエリ名・マッピングは、Phase5 Step4(GPT/MCP Adapter)
設計においても変更せず、Adapterはこの契約を「呼び出すだけ」とする。

## Time API（読み取り専用・localhost限定）

```
GET  /time/state
GET  /time/events
POST /time/replay
GET  /time/audit
```

- 全てRelayKernelを唯一の入口とする。
- 状態破壊・ReplayMode変更・Queue/Snapshot/Event追加APIは含まれない。

## Time Query（固定コマンド方式）

```
event_count
last_snapshot
current_state
replay_state
audit_status
```

- `POST /time/query` の body `{"query": "<上記5種のいずれか>"}` のみ受理。
- 未知のqueryは `{"ok": false, "error": "unknown query"}` (HTTP 400)。

## Semantic Query（固定マッピングのみ・LLM不使用）

```
イベント数 → event_count
最後のsnapshot → last_snapshot
状態 → current_state
監査 → audit_status
```

- `POST /time/semantic_query` の body `{"query": "<自然言語文>"}`。
- 内部実装は `phi_os/semantic/query_resolver.py` の固定キーワード部分文字列一致のみ。
- 未解決の入力は推測せず `{"ok": false, "error": "UNRESOLVED_QUERY"}` (HTTP 400)。
- 完全な対応表は `docs/contracts/capability_registry_v1.md` を参照。

## 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの明示的承認を要する。
