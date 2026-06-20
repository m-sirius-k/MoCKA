# Unified Event Entry v1（Phase5-2.1）

## 結論

MoCKAにおけるevents保存経路は `phi_os.event_gate.process_event()` のみである。
これ以外にeventsテーブルへ書き込みを行う正規の保存経路は制度上存在しない。

`process_event()` は呼び出されると必ず以下を順に実行する。

1. Gate Policy（`event_source` の確定。live / buffered / direct_allowed:{channel}）
2. Validation（`gate_validator.validate()`）
3. Event Signature（`integrity.sign_event()`）
4. Hash Chain（前件 `current_hash` を `previous_hash` として連結）
5. Integrity Registration（`event_signatures` テーブルへの記録）
6. Database Commit（`events` テーブルへの確定書き込み）

## 呼び出し元（トランスポートは問わない）

| 呼び出し元 | トランスポート | event_source |
|---|---|---|
| `POST /api/gate/event` | HTTP（外部AI・他プロセス） | `live` |
| `POST /api/gate/event/batch` | HTTP（Local Event Buffer） | `buffered` |
| `mocka_write_event` MCP（Gate応答時） | HTTP | `live` |
| `mocka_write_event` MCP（Gate ConnectionError時のfallback） | インプロセス直接呼び出し（`phi_os.event_gate.process_event`） | `direct_allowed:recovery` |

旧実装では、Gateサーバー（HTTP）が応答不能な場合の `mocka_write_event` のfallbackが
`events` テーブルへ生SQL `INSERT OR IGNORE` を直接実行し、Validation/Signature/Hash Chain
を経由していなかった（`mocka_mcp_server.py` の旧 `_db_write_event()`）。これにより
当該イベントは `event_signatures` に対応行を持たず、`scripts/migrate_event_integrity.py`
による事後の署名バックフィルが必要だった。

Phase5-2.1でこの経路を撤廃し、HTTPが使えない場合でも同一プロセス内で
`phi_os.event_gate.process_event()` を直接呼び出す方式に統合した。これにより
トランスポートの可否に関わらず、書き込み時点で必ず署名・ハッシュチェーンが
完成し、事後補完は不要になる。

## 例外（許可されたDirect Write）

`interface/gate_policy.py` の `ALLOWED_DIRECT_CHANNELS`（bootstrap / maintenance /
migration / restore / recovery）に該当する場合のみ、`db_helper.write_event(channel=...)`
経由でのDirect Writeが許容される。この経路もPhase5-2で signature/hash chain 必須化済み
であり、Unified Event Entryと同じ整合性保証を提供する。これ以外のDirect Write
（channel未指定・未許可channel）は `_source='direct_violation'` として監査対象になる。

## 関連ファイル

- `phi_os/event_gate.py` — `process_event()`（Unified Event Entry本体）
- `phi_os/gate_validator.py` — Validation
- `phi_os/integrity.py` — Signature / Hash Chain / Verification / Recovery Support
- `interface/gate_policy.py` — Gate Policy（許可Direct Writeチャネル定義）
- `interface/db_helper.py` — 許可チャネル専用のDirect Write API
- `mocka_mcp_server.py` — `mocka_write_event` MCPツール（HTTP優先・インプロセスfallback）
- `scripts/migrate_event_integrity.py` — 歴史的バックログ（Gate確立以前のレガシーイベント）専用の一度限りの署名バックフィル。Unified Event Entry確立後の新規イベントには不要。
