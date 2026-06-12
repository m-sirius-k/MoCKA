# ISE データライフサイクル v1

ISE（Institution State Engine）が管理するデータは、生成から廃棄まで以下の5段階を経る。
判定ロジックの正本は [lifecycle_manager.py](../../PlanningCaliber/workshop/phi-os/ise/lifecycle_manager.py)。

| Stage | 説明 | 保持期間 |
|-------|------|----------|
| RAW | イベント受信直後 | 即時処理 |
| ACTIVE | current_state.json | 常時 |
| SNAPSHOT | gzip圧縮済み | 10世代 |
| ARCHIVED | sealed状態 | 永続 |
| PURGED | 保持期間超過 | — |

## 各ステージの詳細

### RAW
イベントが ISE に到達した直後の状態。永続化前に Event Taxonomy（[taxonomy.md](taxonomy.md)）
に基づく分類が行われ、`state_change` 系イベントであれば Institution State の更新に進む。

### ACTIVE
`current_state.json` として保持される、最新の Institution State。
常に1つのみ存在し、Revisionが更新されるたびに上書きされる。

### SNAPSHOT
`maybe_create_snapshot` / `save_snapshot` によって生成される世代管理対象データ。
[snapshot_manager.py](../../PlanningCaliber/workshop/phi-os/ise/snapshot_manager.py) の
`SNAPSHOT_MAX_GENERATIONS`（10世代）を超えた古い世代は gzip 圧縮される。

### ARCHIVED
ISEState.SEALED に遷移したスナップショット・State。封印後は変更不可とし、永続的に保持する。

### PURGED
SNAPSHOT_MAX_GENERATIONS * 2 世代を超えた圧縮済みスナップショットなど、
保持期間を超過したデータ。`_rotate_generations` により削除される。
