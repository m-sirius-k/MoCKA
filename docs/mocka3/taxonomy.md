# Event Taxonomy v1

ISE（Institution State Engine）が扱う全イベントを4つのカテゴリに分類する。
分類定義の正本は [taxonomy.json](taxonomy.json)。

## カテゴリ一覧

### state_change（制度状態の変化）
制度状態（Institution State）の更新につながるイベント。
- 例: `knock`, `ack`, `state_update`
- severity: `info` 〜 `warning`

### audit（監査・検証）
スナップショット生成や整合性検証など、監査トレイルに関わるイベント。
- 例: `seal`, `verify`, `snapshot`
- severity: `info` 〜 `critical`

### lifecycle（AIセッションのライフサイクル）
AI Runtime Domain側のセッション開始・終了・ハンドシェイク。
- 例: `session_start`, `session_end`, `handshake`
- severity: `info` 〜 `warning`

### incident（インシデント・異常検知）
契約違反や状態のずれ、タイムアウトなどの異常系イベント。
- 例: `violation`, `drift`, `timeout`
- severity: `warning` 〜 `critical`

## 利用方針

- 新規イベント種別を追加する際は、まず4カテゴリのいずれかに分類できるか検討する。
- 既存4カテゴリに収まらない種別が必要になった場合は taxonomy.json の `version` を上げ、
  Version Policy（[version_policy.py](../../PlanningCaliber/workshop/phi-os/ise/version_policy.py)）の
  `major_version_triggers` に `taxonomy_breaking_change` として記録する。
