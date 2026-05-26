# sirius-lab シリーズ 共通仕様書 v1.0
# Orchestra / Relay / Memory
# 作成: 2026-05-26 / きむら博士 × Claude

---

## 0. シリーズ概要

```
sirius-lab = mini MoCKA Series
「AIを使う痛み」を解決するChrome拡張シリーズ

Orchestra  → 広げる（多AI合議・会話アーカイブ）
Relay      → 繋げる（chat間の文脈継続・引き継ぎ）
Memory     → 覚える（ファイル・エラー・状態の永続化）
```

### 3製品の役割分担

| 製品 | 保持する情報 | 粒度 | 解決する痛み |
|---|---|---|---|
| Orchestra | 会話全文・設計議論 | 原文 | 「会話が消える」 |
| Relay | 決定事項・会話要約 | 中程度 | 「また説明し直し」 |
| Memory | ファイル状態・既知エラー | 圧縮 | 「さっきのファイルどこ？」 |

---

## 1. フォルダ構成（共通）

```
{product}-product/          ← 製品ルート（planningcaliber/workshop/配下）
├── extension/              ← Chrome拡張本体（CWS提出ZIPの対象）
│   ├── manifest.json
│   ├── background.js       ← Service Worker
│   ├── content.js          ← DOM監視
│   ├── popup.html          ← ポップアップUI
│   ├── popup.js            ← ポップアップロジック
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
├── backend/                ← Cloudflare Workers（ライセンス発給）
│   └── worker.js
├── DESIGN_v1.md            ← 設計書
└── CHANGELOG.md            ← 変更履歴
```

### 製品別パス

```
Orchestra: C:\Users\sirok\MoCKA\PlanningCaliber\workshop\orchestra-product\
Relay:     C:\Users\sirok\MoCKA\PlanningCaliber\workshop\relay\
Memory:    C:\Users\sirok\MoCKA\PlanningCaliber\workshop\memory\
```

---

## 2. manifest.json 共通仕様

```json
{
  "manifest_version": 3,
  "version": "1.0.0",
  "permissions": [
    "storage",
    "contextMenus",
    "activeTab",
    "scripting",
    "alarms"
  ],
  "host_permissions": [
    "https://claude.ai/*"
  ],
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": ["https://claude.ai/*"],
      "js": ["content.js"],
      "run_at": "document_idle"
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  }
}
```

### 製品別name・description

| 製品 | name | description |
|---|---|---|
| Orchestra | Orchestra — AI Conductor | Save, search, and deliberate with multiple AIs |
| Relay | Relay — AI Handoff | Never explain yourself again |
| Memory | Memory — AI Work State | AI remembers your files, errors, and decisions |

---

## 3. ファイル生成ルール（共通・絶対遵守）

```
【禁止】bash_tool での echo/heredoc/cat によるJS/HTML/JSON生成
【必須】create_file ツールのみ使用
【理由】cp932混入によるUTF-8破壊を構造的に防止
        E20260519_007インシデント（Relay content.jsが正規表現全滅）の再発防止
```

### チェックリスト（Claude Code実装時に毎回確認）

```
□ 全JSファイルの冒頭に 'use strict'; を記載
□ create_file のみでファイル生成（bash heredoc禁止）
□ template literal を使用（文字列 += 禁止）
□ innerHTML は escHtml() 必須・innerText を優先
□ JSON操作は try-catch で囲む
□ chrome.storage 操作は async/await で統一
□ import/export は ES Module形式（type="module"）
□ PowerShell文字列操作禁止（Set-Content/Out-File禁止）
```

---

## 4. chrome.storage 設計（共通）

### ストレージキー命名規則

```
{product}_registry      ← メインデータ
{product}_settings      ← ユーザー設定
{product}_license       ← ライセンス情報
{product}_session       ← 現在セッション

例:
orchestra_registry
relay_registry
memory_registry
```

### 共通フィールド（全製品）

```javascript
{
  schema_version: "1.0",          // マイグレーション管理
  workspace_id: "default",        // ワークスペース識別子
  updated_at: "ISO8601",          // 最終更新日時
  plan: "free"                    // free / pro / one
}
```

### プラン定義（共通）

| プラン | 価格 | 基本方針 |
|---|---|---|
| Free | $0 | 製品の本質的価値を無料で体験させる |
| Pro | $10/月 | 精度・容量・AI連携を強化 |
| One | $10/月 | 最大化・他製品との連携・無制限 |

---

## 5. ライセンスキー仕様（共通）

### キー形式

```
{PREFIX}-{16桁HMAC署名}

Orchestra Pro:  OPR-XXXXXXXXXXXXXXXX
Orchestra One:  ONE-XXXXXXXXXXXXXXXX
Relay Pro:      RLP-XXXXXXXXXXXXXXXX
Relay One:      RLO-XXXXXXXXXXXXXXXX
Memory Pro:     MEP-XXXXXXXXXXXXXXXX
Memory One:     MEO-XXXXXXXXXXXXXXXX
```

### 検証ロジック（共通）

```javascript
async function validateLicense(key) {
  // プレフィックスでプラン判定
  const PREFIXES = {
    'OPR': { product: 'orchestra', plan: 'pro' },
    'ONE': { product: 'orchestra', plan: 'one' },
    'RLP': { product: 'relay',     plan: 'pro' },
    'RLO': { product: 'relay',     plan: 'one' },
    'MEP': { product: 'memory',    plan: 'pro' },
    'MEO': { product: 'memory',    plan: 'one' }
  };

  const prefix = key.split('-')[0];
  const info = PREFIXES[prefix];
  if (!info) return { valid: false, plan: 'free' };

  // HMAC検証（各製品background.jsに実装）
  const signature = key.split('-')[1];
  const valid = await verifyHMAC(signature, prefix);
  
  return {
    valid,
    plan: valid ? info.plan : 'free',
    product: info.product
  };
}
```

---

## 6. Stripe + Cloudflare Workers パイプライン（共通）

### アーキテクチャ

```
購入者 → Stripe Payment Link
  ↓ checkout.session.completed
Cloudflare Workers（worker.js）
  ↓ プラン判定 → HMACキー生成
Resend API
  ↓ noreply@nsjp.org からメール送信
購入者のメールにライセンスキー到着
```

### worker.js 製品別エンドポイント

```
Orchestra: https://orchestra-license.{account}.workers.dev
Relay:     https://relay-license.{account}.workers.dev
Memory:    https://memory-license.{account}.workers.dev
```

### クロスクーポン設計（TODO_179）

```
Orchestra購入 → Relay 20%OFFクーポン発行
Relay購入     → Orchestra 20%OFFクーポン発行
Memory購入    → Orchestra/Relay 各20%OFFクーポン発行
Orchestra/Relay購入 → Memory 20%OFFクーポン発行
```

---

## 7. DOM監視（content.js 共通設計）

### ストリーミング安定化

```javascript
// 全製品共通: 1200ms debounce
const STREAM_IDLE_MS = 1200;

let debounceTimer = null;

const observer = new MutationObserver(() => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(onStableText, STREAM_IDLE_MS);
});
```

### claude.ai セレクタ（共通・2026-05-26時点）

```javascript
const SELECTORS = {
  // AIの応答テキスト（優先順）
  ASSISTANT_MESSAGE: [
    '[data-testid="assistant-message"] .prose',
    '.font-claude-message',
    '[data-is-streaming="false"] .prose'
  ],
  // ユーザー入力欄
  INPUT_BOX: [
    '[contenteditable="true"]',
    'div[aria-label="Write your prompt"]'
  ],
  // ターンカウント
  TURN_COUNTER: [
    '[data-testid="user-message"]',
    '.font-user-message'
  ]
};

// セレクタが壊れた時のフォールバック
function getAssistantText() {
  for (const sel of SELECTORS.ASSISTANT_MESSAGE) {
    const els = document.querySelectorAll(sel);
    if (els.length > 0) {
      return els[els.length - 1].innerText || '';
    }
  }
  return '';
}
```

### セレクタ壊れ検知

```javascript
// 定期的にセレクタの有効性を確認
setInterval(() => {
  const text = getAssistantText();
  if (document.querySelector('[data-testid="assistant-message"]') && !text) {
    console.warn('[sirius-lab] Selector may be broken. Please update SELECTORS.');
  }
}, 30000);
```

---

## 8. ポップアップ UI（共通デザイントークン）

```css
:root {
  --bg-primary:    #0f0f11;
  --bg-secondary:  #1a1a1f;
  --bg-card:       #22222a;
  --text-primary:  #f0f0f5;
  --text-secondary:#9090a8;
  --text-muted:    #505068;
  --border:        #2a2a35;
  --success:       #3ddc84;
  --warning:       #f5a623;
  --danger:        #ff4d4d;
  --radius-sm:     6px;
  --radius-md:     10px;
  --font:          'Inter', -apple-system, sans-serif;
  --popup-width:   380px;
}
```

### 製品別アクセントカラー

```css
/* Orchestra */
--accent: #f5a623;   /* ゴールド */

/* Relay */
--accent: #3ddc84;   /* グリーン */

/* Memory */
--accent: #7c6aff;   /* パープル */
```

### 共通UIコンポーネント

```
ヘッダー: ロゴ + タイトル + サブタイトル + プランバッジ
タブ: 製品固有（3〜4タブ）
コンテンツ: カード形式・max-height:360px・スクロール可
フッター: メインアクションボタン + サブボタン
トースト: 操作フィードバック（2秒表示）
```

---

## 9. i18n 対応（共通5言語）

```javascript
// 対応言語
const SUPPORTED_LANGS = ['ja', 'en', 'de', 'fr', 'es'];

// 言語自動検出
function getLang() {
  const lang = navigator.language.split('-')[0];
  return SUPPORTED_LANGS.includes(lang) ? lang : 'en';
}
```

### 共通翻訳キー（全製品必須）

```javascript
{
  title:        // 製品名
  subtitle:     // キャッチコピー
  plan_free:    // 無料プラン
  plan_pro:     // Proプラン
  plan_one:     // Oneプラン
  upgrade:      // アップグレード
  settings:     // 設定
  copy_success: // コピー完了メッセージ
}
```

---

## 10. コンテキストメニュー（共通）

### 全製品共通メニュー

```javascript
// 全製品に必ず存在するメニュー
chrome.contextMenus.create({
  id: '{product}_copy_inject',
  title: '📋 {製品名}ブロックをコピー',
  contexts: ['all']
});
```

### 製品固有メニュー

| 製品 | 固有メニュー |
|---|---|
| Orchestra | 💾 この会話を保存 / 🎼 AI合議を開始（Pro/One） |
| Relay | 🔄 引き継ぎを準備 / 📖 Logbookに保存 |
| Memory | ⚙️ 環境制約として記録 / 🔴 エラー解決策として記録 / ✅ 決定事項として記録 |

---

## 11. プラン制限の実装パターン（共通）

```javascript
// 機能ロックの共通パターン
async function checkPlan(requiredPlan) {
  const data = await chrome.storage.local.get('{product}_registry');
  const plan = data['{product}_registry']?.plan || 'free';
  
  const PLAN_RANK = { free: 0, pro: 1, one: 2 };
  return PLAN_RANK[plan] >= PLAN_RANK[requiredPlan];
}

// 使用例
if (!await checkPlan('pro')) {
  showUpgradePrompt();
  return;
}
```

### ロックUI表示パターン

```javascript
// Proロックオーバーレイ
function showLockOverlay(element, requiredPlan) {
  element.style.position = 'relative';
  element.style.opacity = '0.4';
  element.style.pointerEvents = 'none';
  
  const overlay = document.createElement('div');
  overlay.className = 'lock-overlay';
  overlay.innerHTML = `
    <div class="lock-msg">
      🔒 ${requiredPlan.toUpperCase()}プランで利用可能
      <br><a href="#" onclick="openUpgrade()">アップグレード</a>
    </div>
  `;
  element.appendChild(overlay);
}
```

---

## 12. 製品間連携仕様（sirius-lab Complete）

### 起動時注入ブロック（統合版）

```
[MEMORY]
最終作業ファイル:
  - {filename} ({status}) → {path}
既知エラー（未解決）:
  ⚠️ {error_pattern} ({count}回)
  → 対策: {solution}
環境制約:
  • {constraint}
未完了TODO:
  [ ] {id}: {title}

[RELAY]
前回決定: {decision}
未完了: {todo_ids}

[ORCHESTRA]
詳細検索: 利用可能
```

### 製品間通信

```javascript
// chrome.storage経由での製品間データ共有
// Memory → Relay への注入ブロック提供
chrome.storage.local.get('memory_registry', (data) => {
  const memoryBlock = buildMemoryInjectBlock(data.memory_registry);
  chrome.storage.local.set({ memory_inject_block: memoryBlock });
});

// Relay が Memory ブロックを読んで統合
chrome.storage.local.get(['relay_registry', 'memory_inject_block'], (data) => {
  const combined = data.memory_inject_block + '\n' + buildRelayBlock(data.relay_registry);
  injectToNewChat(combined);
});
```

---

## 13. CWS提出チェックリスト（共通）

```
□ manifest.json のversionを更新
□ 全JSファイルのcreate_file生成確認（cp932混入ゼロ）
□ アイコン3サイズ（16/48/128px）配置確認
□ extension/フォルダをZIP圧縮
□ Chrome Developer Dashboard にアップロード
□ ストア説明文（日本語・英語）を記入
□ スクリーンショット5枚
□ プライバシーポリシーURL: https://m-sirius-k.github.io/sirius-lab/privacy
□ サポートURL: https://m-sirius-k.github.io/sirius-lab/support
□ Stripe Payment Linkを説明文に記載
□ 審査提出（通常1〜3営業日）
```

---

## 14. 開発ロードマップ（全製品）

```
完了済み:
  Orchestra v1.0  CWS公開済み（2026-05-26）
  Memory Free     実装完了（2026-05-26）

進行中:
  Relay Free      TODO_174（次のフェーズ）

未着手:
  Relay Pro       TODO_175
  Relay One       TODO_176/177
  Memory Pro      TODO_182
  Memory One      TODO_183
  全製品CWS登録   TODO_178/184
  クロスクーポン   TODO_179
  製品間Logbook連携 TODO_180
  Memory×Relay統合 TODO_185
```

---

## 15. 変更履歴

```
v1.0  2026-05-26  初版作成（Orchestra/Relay/Memory設計を統合）
```

---

*sirius-lab シリーズ共通仕様書 v1.0*
*C:\Users\sirok\MoCKA\PlanningCaliber\workshop\SIRIUS_LAB_COMMON_SPEC_v1.md*
