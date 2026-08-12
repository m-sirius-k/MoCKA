# evaluation_log.jsonl Schema

## ファイル形式

`evaluation_log.jsonl` は JSONL（JSON Lines）形式です。

- 1行 = 1つの実験結果JSON
- 追記専用（上書き禁止）
- UFT-8エンコーディング

## スキーマ

各行は以下のフィールドを含むJSON オブジェクト：

```json
{
  "experiment_name": "string",
  "date": "string (YYYY-MM-DD)",
  "result": "string (有効|無効|危険)",
  "verdict": "string (採用|保留|却下)",
  "affected_components": ["array of strings"],
  "event_id": "string (E{date}_{id})",
  "notes": "string",
  "duration_days": "number (optional)",
  "risk_level": "string (low|medium|high, optional)"
}
```

### フィールド説明

| フィールド | 型 | 説明 | 例 |
|-----------|-----|------|-----|
| `experiment_name` | string | 実験/技術名 | `"mcp_v2_schema"` |
| `date` | string | 実験完了日 | `"2026-08-12"` |
| `result` | string | 実験結果（有効/無効/危険） | `"有効"` |
| `verdict` | string | 推奨判定（採用/保留/却下） | `"採用"` |
| `affected_components` | array | 影響を受けるコンポーネント | `["Relay", "Orchestra"]` |
| `event_id` | string | イベントID（mocka_write_event参照） | `"E20260812_3707118838c0b"` |
| `notes` | string | 推奨理由・メモ | `"本体統合ready"` |
| `duration_days` | number | 実験期間（日数、オプション） | `5` |
| `risk_level` | string | リスク評価（オプション） | `"low"` |

### Affected Components

以下から選択（複数選択可）：

- `Relay` - Relay連携機能
- `Orchestra` - Orchestra合議システム
- `PHI-OS` - PHI-OS層
- `Caliber` - Caliber評価機構
- `COMMAND CENTER` - COMMAND CENTER UI
- `Gateway` - Gateway API層
- `MCP` - MCP連携
- `Other` - その他

## 使用例

### 例1: 採用判定

```json
{"experiment_name": "mcp_v2_schema", "date": "2026-08-12", "result": "有効", "verdict": "採用", "affected_components": ["Gateway", "MCP"], "event_id": "E20260812_1234567890ab", "notes": "MCP Schemaの拡張性向上。本体統合ready"}
```

### 例2: 保留判定

```json
{"experiment_name": "claude_agent_view", "date": "2026-08-11", "result": "有効", "verdict": "保留", "affected_components": ["COMMAND CENTER"], "event_id": "E20260811_abcdef123456", "notes": "UX改善が期待できるが、UI設計をきむら博士と再確認してから採用判定", "duration_days": 3}
```

### 例3: 却下判定

```json
{"experiment_name": "nodejs_runtime", "date": "2026-08-10", "result": "危険", "verdict": "却下", "affected_components": ["Relay", "Orchestra"], "event_id": "E20260810_xyz789abc123", "notes": "メモリリーク検出、5年維持が困難。別の軽量言語検討推奨", "risk_level": "high"}
```

## 記録方法

### Manual Append (Python)

```python
import json
from pathlib import Path
from datetime import datetime

log_path = Path("tech_lab/results/evaluation_log.jsonl")

result = {
    "experiment_name": "my_experiment",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "result": "有効",
    "verdict": "採用",
    "affected_components": ["Relay"],
    "event_id": "E20260812_xxxxx",
    "notes": "Example result"
}

with open(log_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(result, ensure_ascii=False) + "\n")
```

### Via mocka_write_event (Recommended)

```python
mocka_write_event(
    title="SANDBOX_RESULT: my_experiment",
    description="Experiment completed. Verdict: 採用. See results/evaluation_log.jsonl",
    tags="sandbox_result,TODO_205",
    why_purpose="TIC evaluation"
)
# Then manually append to evaluation_log.jsonl
```

## クエリ例

### すべての採用判定

```bash
grep '"verdict": "採用"' evaluation_log.jsonl
```

### Relayに影響を与える実験

```bash
grep '"Relay"' evaluation_log.jsonl
```

### 最新10件

```bash
tail -10 evaluation_log.jsonl
```

---

**Important: このファイルは手動で変更しないこと。mocka_write_event + append-only で管理**

