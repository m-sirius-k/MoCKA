# PHI OS + Relay + Orchestra — Architecture

> **このドキュメントを冒頭に渡せば、Claude は即座に全体像を把握して作業を開始できる。**

---

## Purpose
claude.ai 上の会話を保存・引き継ぎ・TODO抽出する Chrome 拡張群の共通基盤。
PHI OS は「保存機能」ではなく、全アプリの**共通契約**として機能する。

---

## アーキテクチャ概観

```
┌─────────────────────────────────────────────────────┐
│                     chrome.ai / claude.ai            │
└────────────────────┬────────────────────────────────┘
                     │ DOM
        ┌────────────▼───────────────┐
        │        Relay (content)      │  観測専用
        │  state → dom → watchers     │
        │  → logbook → ui → main      │
        └────────────┬───────────────┘
                     │ chrome.runtime.sendMessage
        ┌────────────▼───────────────┐
        │      background.js         │  正本保存
        │   router / db / export      │
        └────────────┬───────────────┘
                     │ IndexedDB
        ┌────────────▼───────────────┐
        │       popup.js             │  操作・可視化
        │   search / export-panel     │
        └────────────────────────────┘
                     │
        ┌────────────▼───────────────┐
        │       shared/              │  PHI OS 共通契約
        │  constants / schema /       │
        │  validators / logger        │
        └────────────────────────────┘
```

---

## ファイル一覧と責務

### shared/（PHI OS コア）

| ファイル | 責務 |
|---|---|
| `constants.js` | 全定数（ARTIFACT_TYPE/STAGE_STATUS/SELECTORS/STREAM等） |
| `schema.js` | createArtifact/Session/Workspace/ExportJob + normalize |
| `validators.js` | 検証・サニタイズ・quarantine（全体停止防止） |
| `logger.js` | 統一ロガー + diagnostics バッファ |

### relay/（Relay 拡張）

| ファイル | バージョン | 責務 | Must not |
|---|---|---|---|
| `relay-state.js` | v3.2.0 | globalThis.__RELAY__ 初期化・共有状態唯一の真実源 | 副作用なし |
| `relay-dom.js` | v3.3.0 | セレクタ・テキスト取得・input注入 | state書き込み・chrome API |
| `relay-watchers.js` | v3.2.0 | MutationObserver lifecycle・stream安定化・onUrlChange発火 | TODO抽出・storage |
| `relay-logbook.js` | v3.4.0 | TODO抽出4段階パイプライン・schema v2(status/priority)・updateStatus/deleteTodo追加 | DOM操作 |
| `relay-ui.js` | v3.5.0 | バッジ・トースト・警告ポップアップ | TODO抽出・storage直接 |
| `relay-main.js` | v3.5.0 | 起動・引き継ぎ・handoff・セッション保存・mocka_relay_log書込み | DOM監視・state直接書き込み |

### 注入順（manifest content_scripts[].js）
```
relay-state.js → relay-dom.js → relay-watchers.js
→ relay-logbook.js → relay-ui.js → relay-main.js
```

---

## 共有状態（State Map）

```
globalThis.__RELAY__.state
├── lastAssistantText         生テキスト（watchers が書く）
├── lastStableAssistantText   安定テキスト（watchers が書く）
├── lastUserText              ユーザー入力（watchers が書く）
├── turnCount                 ターン数（watchers が書く）
├── warningShown              警告表示済み（ui が書く）
├── observers.*               Observer ハンドル（watchers が管理）
├── streamIdleTimer           デバウンスタイマー（watchers が管理）
├── sessionId                 起動時UUID（state.js が初期化）
├── initialized               起動完了フラグ（main が書く）
└── lastSavedHash             重複保存防止（logbook が書く）
```

**禁止**: 各モジュールがローカル変数で同じ概念を持たない。必ず __RELAY__.state 経由。

---

## データフロー

```
DOM変化
  → relay-watchers: MutationObserver
  → lastAssistantText 更新
  → streamIdleTimer (1200ms)
  → lastStableAssistantText 確定
  → onStableAssistant コールバック
      ↓
  relay-logbook: processStableText()
  → Stage1: 前処理（コードブロック/テーブル除去）
  → Stage2: フィルタ（コード行/記号/短文除外）
  → Stage3: スコアリング（命令動詞/TODO接頭辞）
  → Stage4: 保存（[RELAY_TODO]最優先 / 閾値以上のみ）
  → chrome.storage.local['relay_todos']
      ↓
  relay-ui: refreshBadge()
  → TODO件数をバッジに表示
```

---

## PHI OS Artifact スキーマ

```json
{
  "phi_os_version": "1.0.0",
  "schema_version": 1,
  "artifact_id":    "art_abc123",
  "artifact_type":  "message",
  "session_id":     "sess_xyz",
  "workspace_id":   "ws_default",
  "source":         { "app": "Orchestra", "service": "claude.ai" },
  "role":           "assistant",
  "content":        "...",
  "tags":           ["todo", "decision"],
  "status":         "draft",
  "created_at":     "2026-05-19T17:00:00.000Z",
  "updated_at":     "2026-05-19T17:00:00.000Z",
  "hash":           "a1b2c3d4"
}
```

---

## Known Traps（やってはいけないこと）

| # | 罠 | 対策 | 状態 |
|---|---|---|---|
| 1 | `let _lastAssistantText` を複数ファイルで宣言 | `__RELAY__.state.lastAssistantText` のみ使う | ✅ 解決済み |
| 2 | Observer を stop() せずに start() を再呼び出し | `_isRunning` フラグで多重登録防止済み | ✅ 解決済み |
| 3 | SPA遷移後に古い Observer が残存 | URL変化を監視して `restart()` する | ✅ 解決済み |
| 4 | bash/heredoc でJSファイルを生成（cp932混入） | **必ず Write ツールを使う（UTF-8強制）** | ✅ 運用ルール化 |
| 5 | `_lastAssistantText` の streamIdle が短すぎる | 1200ms 推奨（config.streamIdleMs） | ✅ 解決済み |
| 6 | storage スキーマの旧形式/新形式が混在 | `schema_ver` + `_normalize()` で自動補完 | ✅ v3.4.0で解決 |
| 7 | popup→content script API がロード前に呼ばれる | エラーを返す前提でフォールバック実装 | ✅ 解決済み |
| 8 | `chrome._relayOpeningChat` SW再起動でリセット | タイムスタンプ付きフラグ（5秒TTL）に変更 | ✅ v3.5.0で解決 |
| 9 | handoffメッセージタイプ不一致（スラッシュ vs アンダースコア） | `RELAY_OPEN_NEW_CHAT` に統一 | ✅ v3.5.0で解決 |
| 10 | TODOスキーマ不一致（done:boolean vs status:string） | schema v2で status/priority を正規フィールドに | ✅ v3.4.0で解決 |

---

## TODO引き継ぎプロトコル

次回 Claude に渡す情報の順序:

1. このARCHITECTURE.mdの先頭（Purpose / ファイル一覧 / Known Traps）
2. 現在の症状と最終ターン
3. 関連するファイルの**変更箇所のみ**（全文は不要）
4. 「触ってはいけない箇所」

---

*最終更新: 2026-05-20 / E20260520_004*
