# Capability Registry v1 (Phase5 Step3)

Status: FROZEN
Date: 2026-06-22
Source: `phi_os/api/time_api.py` (_QUERY_HANDLERS, _QUERY_CAPABILITIES) / `GET /time/capabilities` の実返却値と一致する。

## event_count

- Description: total number of events recorded in EventRepository
- Input: `{"query": "event_count"}` (Time Query) または自然言語(「イベント数」「event数」「event count」「総イベント数」)
- Output: `{"ok": true, "event_count": <int>}`

## last_snapshot

- Description: the most recent snapshot id and its creation timestamp
- Input: `{"query": "last_snapshot"}` または自然言語(「最後のsnapshot」「最新snapshot」「snapshot情報」)
- Output: `{"ok": true, "snapshot_id": <str|null>, "created_at": <int|null>}`

## current_state

- Description: the kernel's current in-memory state
- Input: `{"query": "current_state"}` または自然言語(「現在状態」「current state」「状態」)
- Output: `{"ok": true, "state": {...}}`

## replay_state

- Description: the reconstructed state from running RelayKernel.replay()
- Input: `{"query": "replay_state"}` または自然言語(「再構築」「replay」「再生状態」)
- Output: `{"ok": true, "state": {...}}`

## audit_status

- Description: the most recent replay audit match result and drift count
- Input: `{"query": "audit_status"}` または自然言語(「監査状態」「audit」「drift」)
- Output: `{"ok": true, "last_match": <bool|null>, "drift_count": <int>}`

## 自然言語マッピング解決順序

`phi_os/semantic/query_resolver.py` はキーワードを長さ降順でスキャンする
(短い汎用キーワードが先に誤マッチしないようにするため)。
