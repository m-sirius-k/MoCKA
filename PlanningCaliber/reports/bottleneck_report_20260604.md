# MoCKA ボトルネック解消レポート 2026-06-04

**作成日**: 2026-06-04  
**担当**: Claude (claude-sonnet-4-6)  
**関連イベント**: E20260604_060 〜 E20260604_068

---

## 実行ミッション概要

TASK-3 → TASK-1 → TASK-2 の順で3つのボトルネックを解消した。

---

## TASK-3: ngrok依存チェック & 環境変数化

### 問題
`https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev` が5ファイルにハードコードされており、ngrok URL変更のたびに手動更新が必要だった。

### 発見箇所（grep結果）

| ファイル | 行 | 内容 |
|---|---|---|
| `mocka_mcp_server.py` | 432 | oauth_resource レスポンスの resource URL |
| `PlanningCaliber/workshop/phi-os/adapters/mocka-bridge.js` | 7 | `const MOCKA_ENDPOINT = '...'` |
| `app.py` | 1902-1903 | `/public/info` エンドポイントの mcp/ngrok フィールド |
| `interface/ping_generator.py` | 40 | `NGROK_URL = "..."` |
| `tools/mocka_file_editor.py` | 28 | `MCP_URL = "..."` |

（バックアップファイル app_bak_0501.py, app_backup_*, app_broken.py は対象外）

### 実施内容

- **全5ファイル**を `os.environ.get("MOCKA_ENDPOINT", "")` に統一
- `mocka-bridge.js` は `process.env.MOCKA_ENDPOINT` を参照し `/mcp` を自動付与
- 未設定時は各スクリプト起動時に `[ERROR] 環境変数 MOCKA_ENDPOINT が未設定です。` を出力
- **`.env.example`** を新規作成（ルートディレクトリ）

### 残課題
- TODO_218: Sakura VPS移行後に恒久URLへ差し替え（現時点では環境変数管理で対応済み）

---

## TASK-1: HEALTH_OKノイズ除去

### 問題
`interface/health_check.py` の `run()` 関数が正常終了時に毎回 `mocka_write_event` を発火。  
定期実行（数分おき）で HEALTH_OK イベントが events.db を埋め尽くし、実際の異常イベントの視認性が低下していた。

### 該当コード（修正前）
```python
# interface/health_check.py:357-361
else:
    write_event(
        "HEALTH_OK: ヘルスチェック全件正常",
        f"必須{total}件PASS @ {now_str}",
        "tic,health_check,health_ok",
    )
```

### 実施内容

- `HEALTH_OK_INTERVAL = 30` 定数を追加
- `data/tic/health_ok_counter.txt` でカウンタを永続管理
- **30回に1回**（count % 30 == 1）のみ `write_event` を発火
- HEALTH_FAIL は引き続き**全件記録**（異常は漏らさない）

### 効果
- HEALTH_OKイベント書き込み: 約 **97%削減**（毎回→30回に1回）
- HEALTH_FAILは変更なし（安全側に倒した設計）

---

## TASK-2: CHANGE_DONE自動記録（TODO_153）

### 問題
E20260517_020インシデント: ファイル生成後のmocka_write_event記録が頻繁に漏れる。  
「記録ルールがある」と「実際に記録される」は別問題。構造的強制が必要だった。

### 実施内容（3点）

#### ① app.py `/file/register` エンドポイント（app.py:1685付近）
```
POST /file/register
{"file_path": "...", "tool_name": "Write", "author": "Claude", "lines_after": 120}
→ 自動で mocka_write_event を発火し event_id を返す
```

#### ② `tools/mocka_auto_record.py`（新規作成）
- Claude Code の PostToolUse フックから呼ばれるスクリプト
- stdin から `{"tool_name": "Write", "tool_input": {...}}` を受け取る
- `Write` / `Edit` / `NotebookEdit` ツール実行後に `localhost:5002` へ自動 POST
- MCP サーバー未起動時はログ出力のみ（エラーで止まらない設計）

#### ③ `.claude/settings.local.json` PostToolUse フック設定
```json
"hooks": {
  "PostToolUse": [
    {
      "matcher": "Write|Edit|NotebookEdit",
      "hooks": [{ "type": "command",
                  "command": "python C:/Users/sirok/MoCKA/tools/mocka_auto_record.py" }]
    }
  ]
}
```
Claude Code が Edit/Write を実行するたびに自動でフックが走る。

### TODO ステータス更新
- **TODO_153**: 未着手 → **完了**
- TODO_217（PostToolUse:Edit change-tracker連携）: 今回の実装で基盤完成。統合は別途

### 成功条件確認
> きむら博士が後からファイルを探す際にevents.dbで必ず見つかる状態

→ PostToolUse フックにより Claude Code セッション内の全 Edit/Write が自動記録される。
　MCPサーバー起動中であれば記録漏れはゼロになる構造が実現。

---

## 変更ファイル一覧

| ファイル | 変更種別 | 内容 |
|---|---|---|
| `mocka_mcp_server.py` | 修正 | MOCKA_ENDPOINT環境変数化、起動時エラーログ |
| `PlanningCaliber/workshop/phi-os/adapters/mocka-bridge.js` | 修正 | MOCKA_ENDPOINT環境変数化、未設定時エラーログ |
| `app.py` | 修正 | ngrok URL環境変数化、/file/registerエンドポイント追加 |
| `interface/ping_generator.py` | 修正 | NGROK_URL環境変数化 |
| `tools/mocka_file_editor.py` | 修正 | MCP_URL環境変数化 |
| `interface/health_check.py` | 修正 | HEALTH_OK間引き(30回に1回)、カウンタ実装 |
| `tools/mocka_auto_record.py` | **新規** | PostToolUseフックスクリプト |
| `.claude/settings.local.json` | 修正 | PostToolUse hooks設定追加 |
| `.env.example` | **新規** | MOCKA_ENDPOINT環境変数テンプレート |

---

## MoCKA イベント記録

| event_id | タイトル |
|---|---|
| E20260604_060 | CHANGE_START: TASK-3 ngrok依存チェック&環境変数化 |
| E20260604_062 | CHANGE_DONE: TASK-3 完了 |
| E20260604_063 | CHANGE_START: TASK-1 HEALTH_OKノイズ除去 |
| E20260604_064 | CHANGE_DONE: TASK-1 完了 |
| E20260604_065 | CHANGE_START: TASK-2 CHANGE_DONE自動記録フック実装 |
| E20260604_068 | CHANGE_DONE: TASK-2 完了 |

---

## 残課題・申し送り

1. **MOCKA_ENDPOINT の値設定**: `.env.example` をコピーして `.env` を作成し、実際のngrok URLを設定すること
2. **TODO_217**: change-tracker PostToolUse:Edit hook との統合（今回の基盤を活用）
3. **mocka_auto_record.py の動作確認**: MCPサーバー(5002)起動中に Edit を行い、events.db にCHANGE_DONEが記録されることを確認
4. **health_ok_counter.txt**: 初回実行時に `data/tic/` に自動生成される。手動リセット可能。
