# PHI OS 設計書 v1.0 — 3AI合議反映版

**TODO:** TODO_186  
**確定イベント:** E20260526_044  
**作成日:** 2026-06-01  
**分類:** PRIVATE — PlanningCaliber 資産

---

## 1. PHI OS とは何か

PHI OS（Platform Hub Integration OS）は Chrome 拡張機能群（Orchestra / Relay / Memory / Prism 等）の**共有神経系**として機能するサービスワーカー常駐型ランタイム層である。

UI を持たず、イベントバス・状態ストア・スキーマ管理・権限管理の 4 機能のみを提供する。各製品は PHI OS を通じて相互にデータを共有しつつ、PHI OS 未インストール時でも単体動作を保証する。

---

## 2. アーキテクチャ全体図

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Chrome ブラウザ                                │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  Orchestra  │  │    Relay    │  │   Memory    │  ... 各製品      │
│  │ (extension) │  │ (extension) │  │ (extension) │                 │
│  │             │  │             │  │             │                 │
│  │ phi-adapter │  │ phi-adapter │  │ phi-adapter │  ← 各製品同梱  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                        │
│         └────────────────┴────────────────┘                        │
│                          │                                         │
│              chrome.storage.local (イベントバス)                     │
│                          │                                         │
│  ┌───────────────────────▼──────────────────────────────────────┐  │
│  │                     PHI OS (extension)                       │  │
│  │                  service worker 常駐                         │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ event-bus.js │  │state-store.js│  │schema-registry.js│  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │               permission-manager.js                  │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                              │  │
│  │  adapters/                                                   │  │
│  │  ┌──────────────┐  ┌────────────┐  ┌──────────────────┐    │  │
│  │  │orchestra-    │  │relay-      │  │memory-adapter.js │    │  │
│  │  │adapter.js    │  │adapter.js  │  └──────────────────┘    │  │
│  │  └──────────────┘  └────────────┘                          │  │
│  │                                                              │  │
│  │  sync/                                                       │  │
│  │  ┌──────────────────┐                                        │  │
│  │  │ mocka-bridge.js  │ ← MoCKA localhost:5000 連携           │  │
│  │  └──────────────────┘                                        │  │
│  │                                                              │  │
│  │  options.html  ← CWS審査対策・単体動作デモ                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                          │                                         │
│              MoCKA localhost:5000                                   │
│              /api/phi-os-event                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. フォルダ構成

```
phi-os/
├── extension/
│   ├── core/
│   │   ├── event-bus.js          ← onMessageExternal + ALLOWED_EXTENSIONS
│   │   ├── state-store.js        ← L1 in-memory / L2 chrome.storage / L3 IndexedDB
│   │   ├── schema-registry.js    ← バージョン管理・製品タイプ定義
│   │   └── permission-manager.js ← 拡張ID認証・権限レベル管理
│   ├── adapters/
│   │   ├── orchestra-adapter.js
│   │   ├── relay-adapter.js
│   │   ├── memory-adapter.js
│   │   └── _template-adapter.js  ← Prism/Vault 向けテンプレート
│   ├── capture/                  ← 各製品 content.js 同梱用
│   │   └── phi-adapter.js        ← isPHIOsAvailable() + captureEvent()
│   ├── sync/
│   │   └── mocka-bridge.js       ← MoCKA localhost:5000 連携
│   ├── debug/
│   │   ├── health-check.js
│   │   └── debug-panel.js
│   ├── ui/
│   │   └── options.html          ← CWS審査対策・単体動作保証
│   ├── background.js             ← Service Worker エントリポイント
│   └── manifest.json
├── test/
├── Dockerfile
└── DESIGN_v1.md                  ← 本ファイル
```

---

## 4. onMessageExternal + ALLOWED_EXTENSIONS 完全仕様

### 4.1 なぜ chrome.storage.local をバスとして使うか

`chrome.runtime.sendMessage` による cross-extension 通信は Extension ID のハードコードが必要で、CWS 審査・ID 変更時に壊れるリスクがある。

**代替設計:**  
`chrome.storage.local` のキー `phi_event_bus` をイベントキューとして使用し、`chrome.storage.onChanged` で全製品がリアルタイム購読する。

```
emit(type, payload)
  → chrome.storage.local.set({ phi_event_bus: [...] })
  → 全製品の storage.onChanged が即時発火
  → subscribe(types, callback) が型フィルタして callback 実行
```

### 4.2 ALLOWED_EXTENSIONS（将来の onMessageExternal 対応）

CWS 審査後、各製品の本番 Extension ID が確定した段階で `background.js` の `ALLOWED_EXTENSIONS` リストに登録する。それまでは storage ベースのバスを使用する。

```javascript
// background.js に将来追加する定義
const ALLOWED_EXTENSIONS = [
  // Orchestra
  'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
  // Relay
  'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy',
  // Memory
  'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
];

chrome.runtime.onMessageExternal.addListener((msg, sender, sendResponse) => {
  if (!ALLOWED_EXTENSIONS.includes(sender.id)) {
    sendResponse({ error: 'UNAUTHORIZED' });
    return;
  }
  // メッセージ処理...
});
```

---

## 5. Storage Key 空間分離ルール

製品プレフィックスによるキー名前空間の完全分離。衝突防止のため全製品で遵守する。

| プレフィックス | 担当製品 | 例 |
|---|---|---|
| `phi_` | PHI OS 共通 | `phi_event_bus`, `phi_schema_version` |
| `phi_orchestra_` | Orchestra | `phi_orchestra_conversation_latest` |
| `phi_relay_` | Relay | `phi_relay_session_latest`, `phi_relay_todos_latest` |
| `phi_memory_` | Memory | `phi_memory_entry_<ts>` |
| `phi_prism_` | Prism（将来） | `phi_prism_*` |
| `phi_vault_` | Vault（将来） | `phi_vault_*` |

### 5.1 禁止事項
- プレフィックスなしのキー（`session_data` 等）は禁止
- 他製品のプレフィックスのキーへの直接書き込みは禁止（adapter 経由のみ）

---

## 6. PHI OS 未インストール時のフォールバック仕様

各製品の `phi-adapter.js` は `isPHIOsAvailable()` で PHI OS の存在を確認する。

```
isPHIOsAvailable() → false の場合:
  - write() → chrome.storage.local のみに書き込む
  - read()  → chrome.storage.local から読み込む
  - notify() → chrome.storage.local の phi_event_latest に書き込む
  - 例外は吐かない（製品単体動作を保証）
```

### 6.1 フォールバック時のデータ損失について

PHI OS 経由の製品間共有データ（Orchestra ↔ Relay 間のセッション引き継ぎ等）はフォールバック時に利用不可となるが、**製品単体の機能は完全に維持される**。

---

## 7. MoCKA localhost:5000 連携プロトコル

### 7.1 エンドポイント

```
POST http://localhost:5000/api/phi-os-event
Content-Type: application/json

{
  "event_type": "ARTIFACT_SAVED | SESSION_HANDOFF | DECISION_RECORDED | ...",
  "product":    "relay | orchestra | memory",
  "payload":    { ... 製品固有データ },
  "ts":         1234567890123
}
```

### 7.2 mocka-bridge.js の役割

- PHI OS 内部イベントを MoCKA に転送する
- MoCKA 未起動時（localhost:5000 不在）は静かに失敗する（AbortSignal.timeout(500)）
- 転送対象: `ARTIFACT_SAVED`, `SESSION_HANDOFF`, `DECISION_RECORDED`, `PHI_COMMIT_DONE`

### 7.3 MoCKA 側の記録

転送されたイベントは `mocka_events.db` に `HEALTH_OK / PHI_OS_EVENT` として記録される。

---

## 8. CWS 審査通過戦略 — options.html デモ機能仕様

PHI OS はバックグラウンドのみで動作するため CWS 審査でリジェクトされるリスクがある。`options.html` に以下のデモ機能を実装して単体動作を証明する。

### 8.1 options.html が実装すべき機能

1. **接続状態ダッシュボード**  
   - 登録済み製品の Extension ID 一覧と接続状態（online/offline）を表示  
   - MoCKA localhost:5000 への疎通状態

2. **イベントバス モニター**  
   - `phi_event_bus` の直近10件をリアルタイム表示

3. **Storage Key エクスプローラー**  
   - `phi_` プレフィックスの全キーとサイズを表示  
   - クリアボタン（開発用）

4. **手動テスト送信**  
   - 製品を選んでテストイベントを発火できる入力フォーム

### 8.2 CWS 記載テキスト（en）

```
PHI OS is a background runtime hub for the MoCKA product suite
(Orchestra, Relay, Memory). It provides a shared event bus and state
store via chrome.storage.local. Use the options page to monitor
connections and event traffic between products.
```

---

## 9. artifact_type 一覧（schema-registry.js 定義）

| artifact_type | 説明 | 生成製品 |
|---|---|---|
| `message` | 会話メッセージ | Relay, Orchestra |
| `decision` | 確定した決定事項 | Orchestra, Relay |
| `todo` | 未完了タスク | Relay |
| `note` | メモ・違和感 | Memory |
| `export` | エクスポートデータ | 全製品 |
| `share` | 製品間共有データ | PHI OS |

---

## 10. バージョン管理と migration

### 10.1 現在バージョン

`phi_os_version: "1.0.0"`

### 10.2 migration テーブル（将来）

```javascript
const MIGRATIONS = {
  '1.0.0': null,           // 初版
  '1.1.0': migrateV1toV1_1, // commit スキーマ拡張
  '2.0.0': migrateV1toV2,   // storage key 再編
};
```

migration は `ensureSchemaVersion()` 内で自動実行。データが `phi_os_version < current` の場合に適用される。

---

*設計確定: E20260526_044 / 3AI合議（Claude・ChatGPT・Gemini）/ きむら博士承認*
