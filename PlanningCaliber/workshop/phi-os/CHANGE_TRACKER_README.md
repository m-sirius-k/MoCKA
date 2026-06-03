# change-tracker — PHI-OS 変更前後強制記録制度

> 「記録なき変更はMoCKAとして存在しない」  
> E20260603_060 / TODO_144 / 2026-06-03

---

## ファイル構成

```
phi-os/
├── core/
│   ├── change-tracker.js        変更追跡コア（公開API）
│   └── change-record-store.js   ローカルログ管理（chrome.storage.local）
└── adapters/
    └── mocka-bridge.js          MoCKA MCP 送信ブリッジ
```

---

## インストール / インポート

```javascript
// 任意のJS/拡張機能から
import { ChangeTracker } from './core/change-tracker.js';
import { RecordStore }   from './core/change-record-store.js';
import { MocKABridge }   from './adapters/mocka-bridge.js';
```

chrome.storage.local が使えない環境（Node.js 等）ではメモリ内蓄積に自動フォールバックします。

---

## 基本的な使い方

```javascript
// ファイル変更前
await ChangeTracker.beforeChange('src/app.js', 'ログイン処理のバグ修正');

// ... 実際のファイル変更 ...

// ファイル変更後
await ChangeTracker.afterChange('src/app.js', 'success', {
  lines_after: 120,
  diff_summary: 'セッション期限切れ時のリダイレクト先を修正',
});
```

---

## PHI-OS統合時 vs 単独動作時

| 状況 | 動作 |
|------|------|
| PHI-OS 接続あり（`window.PHI_OS_ADAPTER` 存在 または ngrok 疎通） | リアルタイムで MoCKA へ送信 |
| PHI-OS 未接続 | `chrome.storage.local` に `mocka_synced: false` で蓄積 |
| 送信失敗 | 自動でローカル蓄積にフォールバック（エラーを投げない） |

接続が回復したら `ChangeTracker.flush()` を呼ぶことで未送信レコードをまとめて送信できます。

---

## 公開 API 一覧

### ChangeTracker

| メソッド | 説明 |
|---------|------|
| `beforeChange(filePath, reason, opts?)` | 変更前に呼ぶ。CHANGE_START を記録 |
| `afterChange(filePath, result, opts?)` | 変更後に呼ぶ。CHANGE_DONE を記録 |
| `getLog()` | ローカルの全レコードを返す |
| `flush()` | 未送信レコードを MoCKA へ送信 |

`opts` パラメータ:
- `beforeChange` — `{ lines_before?: number }`
- `afterChange` — `{ lines_after?: number, diff_summary?: string }`

`result` の値: `'success'` | `'fail'` | `'partial'`

### RecordStore

| メソッド | 説明 |
|---------|------|
| `append(record)` | レコード追加（200件上限、超過時は古い順削除） |
| `getAll()` | 全レコード取得 |
| `getPending()` | 未送信レコード取得（`mocka_synced: false`） |
| `markSynced(id)` | 送信済みマーク |
| `clear()` | 全削除 |
| `getStats()` | `{ total, pending, synced, total_lifetime, last_flush }` |

### MocKABridge

| メソッド | 説明 |
|---------|------|
| `isConnected()` | MoCKA 接続確認（10秒キャッシュ） |
| `sendChangeStart(record)` | CHANGE_START 送信 |
| `sendChangeDone(record)` | CHANGE_DONE 送信 |
| `flushPending()` | 未送信全件送信 → `{ sent, failed }` |

---

## デバッグ方法

ブラウザ DevTools Console から実行:

```javascript
// ログ全件確認
ChangeTracker.getLog().then(console.log);

// 単体テスト
ChangeTracker.beforeChange('test/sample.js', 'デバッグテスト')
  .then(() => ChangeTracker.afterChange('test/sample.js', 'success'))
  .then(() => ChangeTracker.getLog())
  .then(log => console.table(log));

// pending確認
RecordStore.getPending().then(console.log);

// ストレージ統計
RecordStore.getStats().then(console.log);

// MoCKA接続確認
MocKABridge.isConnected().then(console.log);

// 未送信レコードを強制送信
ChangeTracker.flush().then(result => console.log('flush result:', result));
```

---

## よくあるエラーと対処法

| エラー | 原因 | 対処 |
|-------|------|------|
| `chrome is not defined` | 拡張機能外の環境 | メモリ fallback が自動で動作する（正常） |
| `QuotaExceededError` | storage 容量超過 | 200件上限で古い順に自動削除。手動で `RecordStore.clear()` も可 |
| `fetch failed` (mocka-bridge) | ngrok 切断 / MoCKA停止 | 単独モードにフォールバック。接続回復後に `flush()` を呼ぶ |
| `PHI_OS_ADAPTER undefined` | PHI-OS未接続 | 正常動作（単独モード）。エラーではない |
| `AbortError` | タイムアウト（3秒） | ネットワーク遅延。単独モードにフォールバック |

---

## レコードフォーマット

```json
{
  "id": "CT_1717401234567_A3BC",
  "type": "CHANGE_START",
  "file": "src/app.js",
  "reason": "変更理由（WHY）",
  "lines_before": 98,
  "lines_after": null,
  "diff_summary": "",
  "result": null,
  "timestamp": "2026-06-03T10:00:00.000Z",
  "phi_os_connected": false,
  "mocka_synced": false
}
```

---

*TODO_144 / E20260603_060 / きむら博士 × Claude*
