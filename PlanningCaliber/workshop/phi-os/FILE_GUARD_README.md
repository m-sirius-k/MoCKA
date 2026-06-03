# file-guard — ファイル操作完全記録制度

> 「ルールがある ≠ 実行される。構造で縛る。」  
> E20260603_070 / TODO_153 主力 / 2026-06-03

---

## 4TODO統合の全体像

```
┌─────────────────────────────────────────────────────────────┐
│                      ファイル操作発生                         │
│          create_file / Edit / present_files 等               │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │    tool-hook.js          │  ← TODO_217
              │  (自動イベント捕捉)       │  方式A/B/C
              └────────────┬────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
┌─────────▼──────────┐          ┌──────────▼──────────┐
│   file-guard.js     │         │  change-tracker.js   │  ← TODO_144
│  (FILE_CREATED /    │         │  (CHANGE_DONE 記録)  │  （既存資産）
│   FILE_PRESENTED)   │         └──────────┬───────────┘
│   TODO_153 主力     │                    │
└─────────┬───────────┘                    │
          │                                │
┌─────────▼───────────┐                   │
│  utf8-checker.js     │                  │  ← TODO_155
│  (cp932混入検出)     │                  │
└─────────┬───────────┘                  │
          │                               │
          └──────────────┬────────────────┘
                         │
           ┌─────────────▼─────────────┐
           │      mocka-bridge.js       │  ← TODO_144
           │   (MoCKA MCP 送信)         │  （既存資産）
           └─────────────┬─────────────┘
                         │
           ┌─────────────▼─────────────┐
           │  chrome.storage.local      │
           │  (ローカル蓄積・フォール   │
           │   バック)                  │
           └────────────────────────────┘
```

---

## インストール / 初期化

```javascript
import { FileGuard }    from './core/file-guard.js';
import { ChangeTracker } from './core/change-tracker.js';
import { UTF8Checker }   from './validators/utf8-checker.js';
import { ToolHook }      from './adapters/tool-hook.js';
import { MocKABridge }   from './adapters/mocka-bridge.js';

// フック登録（初期化時に1回）
ToolHook.register();
```

---

## 基本的な使い方

### create_file 後の記録

```javascript
// ファイル生成後に呼ぶ
await FileGuard.onFileCreated('src/my-feature.js', {
  todo_ref: 'TODO_153',
  reason:   '新機能の実装',
});
```

### present_files 後の記録

```javascript
await FileGuard.onFilePresented(['src/a.js', 'src/b.js'], {
  reason: 'レビュー用ファイル提示',
});
```

### 手動フック通知（フェーズ1）

```javascript
// ToolHook.notify() でツール完了を手動通知
await ToolHook.notify('create_file', {
  path:   'src/new-file.js',
  reason: '新規作成',
});
```

---

## PHI-OS統合時 vs 単独動作時

| 状況 | 動作 |
|------|------|
| PHI-OS 接続あり (`window.PHI_OS_ADAPTER` 存在) | mocka-bridge 経由でリアルタイム送信 |
| ngrok エンドポイントに疎通あり | 直接 MoCKA へ送信 |
| 未接続 | `chrome.storage.local` に `mocka_synced: false` で蓄積 |
| `chrome.storage` 未使用環境 | メモリ内蓄積 |
| 送信失敗 | 自動でローカルフォールバック（例外を投げない） |

接続回復後: `FileGuard.forceSync()` または `ChangeTracker.flush()` で未送信分を一括送信。

---

## デバッグスニペット集

```javascript
// 1. FileGuard 単体テスト
await FileGuard.onFileCreated('test/debug.js', {
  todo_ref: 'TODO_153',
  reason:   'デバッグテスト'
});
console.log('未送信ファイル:', await FileGuard.getUnsyncedFiles());

// 2. UTF-8 正常テスト
const ok = UTF8Checker.scanContent('const x = "テスト";');
console.log('UTF-8 normal:', ok); // { ok: true, issues: [] }

// 3. UTF-8 異常テスト（cp932混入模擬）
const bad = UTF8Checker.scanContent('const x = "�";');
console.log('UTF-8 bad:', bad); // { ok: false, issues: [...] }

// 4. ToolHook 状態確認
ToolHook.register();
console.log('フック履歴:', ToolHook.getHookLog());

// 5. MoCKA 接続確認
console.log('MoCKA接続:', await MocKABridge.isConnected());

// 6. 強制送信
const result = await FileGuard.forceSync();
console.log('forceSync:', result); // { sent: N, failed: N }

// 7. ChangeTracker ログ確認
console.log('変更ログ:', await ChangeTracker.getLog());

// 8. PHI-OS 統合確認
console.log('PHI-OS:',
  typeof window.PHI_OS_ADAPTER !== 'undefined' ? '統合モード' : '単独モード');
```

---

## よくあるエラーと対処法

| エラー | 原因 | 対処 |
|-------|------|------|
| `import failed: change-tracker.js` | パス解決失敗 | 相対パスを確認 (`./` vs `../`) |
| `UTF8Checker is not defined` | ロード順序 | validators/ を core/ より先に初期化 |
| `chrome.storage is not available` | 拡張外環境 | メモリ fallback が自動動作（正常） |
| `fetch failed to ngrok` | ngrok切断 | 単独モードに自動フォールバック。回復後 `forceSync()` |
| `ToolHook: no events captured` | Claude Code 未統合 | `ToolHook.notify()` で手動通知（フェーズ1） |
| `UTF-8 WARNING` | cp932混入 | ファイル生成ツールを UTF-8 明示指定に変更 |
| `AbortError` | タイムアウト3秒 | MoCKA 側の応答を確認。単独モードで継続 |

---

## ToolHook 実装フェーズ

| フェーズ | 方式 | 状態 |
|---------|------|------|
| フェーズ1 | 手動 `ToolHook.notify()` + 方式A/B/C 登録 | ✅ 実装済み（今回） |
| フェーズ2 | `window.claude:tool:complete` 公式イベント検証 | TODO_217 本実装 |
| フェーズ3 | Claude Code PostToolUse 公式 hooks 対応 | 将来 |

方式A（window カスタムイベント）・方式B（chrome.runtime.onMessage）・方式C（MutationObserver）の3方式を同時登録。利用可能な方式が自動的に発火する。

---

## レコードフォーマット

```json
{
  "id": "FG_1717401234567_A3BC",
  "type": "FILE_CREATED",
  "file_path": "src/app.js",
  "file_name": "app.js",
  "extension": ".js",
  "context": {
    "todo_ref": "TODO_153",
    "reason": "新機能実装",
    "session_id": ""
  },
  "utf8_verified": true,
  "utf8_issues": [],
  "mocka_synced": false,
  "timestamp": "2026-06-03T10:00:00.000Z",
  "phi_os_connected": false
}
```

---

## 今後の自動化ロードマップ（TODO_217将来像）

```
現在（フェーズ1）
  Claude Code がファイルを作成
  → 人間 or Claude が ToolHook.notify() を手動呼び出し
  → FileGuard が記録

フェーズ2（TODO_217本実装）
  Claude Code がファイルを作成
  → window.claude:tool:complete イベント自動発火
  → ToolHook が自動捕捉
  → FileGuard が記録（ゼロ手動操作）

フェーズ3（将来）
  Claude Code PostToolUse 公式 hooks が提供される
  → settings.json の hooks 設定でネイティブ統合
  → 最高信頼性・最低遅延での完全自動記録
```

---

*TODO_153 主力 / TODO_144・155・217 連携 / E20260603_070 / きむら博士 × Claude*
