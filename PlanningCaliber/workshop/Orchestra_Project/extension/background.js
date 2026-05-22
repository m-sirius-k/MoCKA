// Orchestra - background.js
// IndexedDB management, message routing, export, right-click menu
// v0.2.1: + Right-click Orchestra menu (Save / Send / Deliberate)

// ── Free: IndexedDB ───────────────────────────────────────────────────────────

const DB_NAME = 'orchestra_db';
const DB_VERSION = 1;
const STORE_NAME = 'messages';

let db = null;

function initDB() {
  return new Promise((resolve, reject) => {
    if (db) { resolve(db); return; }
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const database = e.target.result;
      if (!database.objectStoreNames.contains(STORE_NAME)) {
        const store = database.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('session_id', 'session_id', { unique: false });
        store.createIndex('timestamp', 'timestamp', { unique: false });
        store.createIndex('service', 'service', { unique: false });
        store.createIndex('role', 'role', { unique: false });
      }
    };
    req.onsuccess = (e) => { db = e.target.result; resolve(db); };
    req.onerror = () => reject(req.error);
  });
}

async function saveMessage(record) {
  const database = await initDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.put(record);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  });
}

async function getAllMessages(limit = 500) {
  const database = await initDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const index = store.index('timestamp');
    const req = index.openCursor(null, 'prev');
    const results = [];
    req.onsuccess = (e) => {
      const cursor = e.target.result;
      if (cursor && results.length < limit) {
        results.push(cursor.value);
        cursor.continue();
      } else {
        resolve(results);
      }
    };
    req.onerror = () => reject(req.error);
  });
}

async function searchMessages(query, limit = 200) {
  const database = await initDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const req = store.openCursor();
    const results = [];
    const q = query.toLowerCase();
    req.onsuccess = (e) => {
      const cursor = e.target.result;
      if (cursor) {
        const msg = cursor.value;
        if (msg.content.toLowerCase().includes(q)) results.push(msg);
        if (results.length < limit) cursor.continue();
        else resolve(results.sort((a, b) => b.timestamp.localeCompare(a.timestamp)));
      } else {
        resolve(results.sort((a, b) => b.timestamp.localeCompare(a.timestamp)));
      }
    };
    req.onerror = () => reject(req.error);
  });
}

async function getStats() {
  const database = await initDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const countReq = store.count();
    countReq.onsuccess = () => {
      const total = countReq.result;
      const sessionSet = new Set();
      const cursorReq = store.openCursor();
      cursorReq.onsuccess = (e) => {
        const cursor = e.target.result;
        if (cursor) {
          sessionSet.add(cursor.value.session_id);
          cursor.continue();
        } else {
          resolve({ total, sessions: sessionSet.size });
        }
      };
      cursorReq.onerror = () => resolve({ total, sessions: 0 });
    };
    countReq.onerror = () => reject(countReq.error);
  });
}

async function exportJSON() {
  const msgs = await getAllMessages(10000);
  return JSON.stringify(msgs, null, 2);
}

async function exportCSV() {
  const msgs = await getAllMessages(10000);
  const header = 'id,service,role,timestamp,session_id,content';
  const rows = msgs.map(m => {
    const content = '"' + m.content.replace(/"/g, '""').replace(/\n/g, '\\n') + '"';
    return `${m.id},${m.service},${m.role},${m.timestamp},${m.session_id},${content}`;
  });
  return '\uFEFF' + [header, ...rows].join('\n');
}

async function clearAll() {
  const database = await initDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.clear();
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  });
}

// ── Right-click: AI targets config ───────────────────────────────────────────

const ALL_AI_TARGETS = [
  { name: 'ChatGPT',    url: 'https://chatgpt.com',              domain: 'chatgpt.com' },
  { name: 'Gemini',     url: 'https://gemini.google.com/app',    domain: 'gemini.google.com' },
  { name: 'Perplexity', url: 'https://www.perplexity.ai',        domain: 'perplexity.ai' },
  { name: 'Copilot',    url: 'https://copilot.microsoft.com',    domain: 'copilot.microsoft.com' },
  { name: 'Genspark',  url: 'https://www.genspark.ai',           domain: 'genspark.ai' },
];

// デフォルト: 全AI有効
const DEFAULT_TARGETS = ALL_AI_TARGETS.map(t => t.name);

async function getSelectedTargets() {
  return new Promise(resolve => {
    chrome.storage.sync.get(['orchestra_targets'], data => {
      const saved = data.orchestra_targets;
      // 保存済みがあればそれを使う、なければ全AI
      if (Array.isArray(saved) && saved.length > 0) {
        resolve(ALL_AI_TARGETS.filter(t => saved.includes(t.name)));
      } else {
        resolve(ALL_AI_TARGETS);
      }
    });
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ── 応答待機時間: スライダー設定値をmsに変換 ──────────────────────────────────
const WAIT_LEVEL_MAP = {
  1: 5000, 2: 4500, 3: 4000, 4: 3000, 5: 2000,
  6: 1800, 7: 1500, 8: 1200, 9: 1000, 10: 800,
};

async function getWaitTime() {
  return new Promise(resolve => {
    chrome.storage.sync.get(['orchestra_wait_level'], data => {
      const lv = data.orchestra_wait_level || 5;
      resolve(WAIT_LEVEL_MAP[lv] || 2000);
    });
  });
}

// ── Right-click: Context menu setup ──────────────────────────────────────────

function setupContextMenus() {
  chrome.contextMenus.removeAll(() => {
    // 親メニュー
    chrome.contextMenus.create({
      id: 'orchestra-root',
      title: '◈ Orchestra',
      contexts: ['selection'],
    });

    // 保存
    chrome.contextMenus.create({
      id: 'orchestra-save',
      parentId: 'orchestra-root',
      title: '💾 保存',
      contexts: ['selection'],
    });

    // 送る（共有）
    chrome.contextMenus.create({
      id: 'orchestra-send',
      parentId: 'orchestra-root',
      title: '→ 送る（共有）',
      contexts: ['selection'],
    });

    // 協議（合議）
    chrome.contextMenus.create({
      id: 'orchestra-deliberate',
      parentId: 'orchestra-root',
      title: '⚡ 協議（合議）',
      contexts: ['selection'],
    });
  });
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create('keepAlive', { periodInMinutes: 0.4 });
  setupContextMenus();
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keepAlive') {
    initDB().catch(console.error);
  }
});

chrome.alarms.get('keepAlive', (alarm) => {
  if (!alarm) {
    chrome.alarms.create('keepAlive', { periodInMinutes: 0.4 });
  }
});

// SW再起動時もメニュー再構築
try { setupContextMenus(); } catch(e) { console.warn('[Orchestra] contextMenus setup skipped:', e.message); }
initDB().catch(console.error);

// ── Right-click: Handler ──────────────────────────────────────────────────────

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const text = info.selectionText || '';
  if (!text.trim()) return;

  switch (info.menuItemId) {

    // ── 保存 ────────────────────────────────────────────────────────────────
    case 'orchestra-save': {
      const record = {
        id: 'sel_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
        service: 'manual',
        role: 'user',
        timestamp: new Date().toISOString(),
        session_id: 'manual_' + new Date().toISOString().slice(0, 10),
        content: text,
      };
      await saveMessage(record);
      notifyTab(tab.id, '💾 保存しました');
      break;
    }

    // ── 送る（共有）────────────────────────────────────────────────────────
    case 'orchestra-send': {
      const targets = await getSelectedTargets();
      // ステータスオーバーレイ表示（全AI: 黄色=送信中）
      chrome.tabs.sendMessage(tab.id, { type: 'ORCHESTRA_STARTED', targets: targets.map(t => t.name), mode: 'collaboration' });
      for (const target of targets) {
        await injectTextToAI(target, text, false);
        chrome.tabs.sendMessage(tab.id, { type: 'ORCHESTRA_AI_DONE', ai: target.name }).catch(()=>{});
      }
      setTimeout(() => hideStatusOverlay(tab.id), 3000);
      notifyTab(tab.id, `→ ${targets.map(t => t.name).join(' / ')} に送りました`);
      break;
    }

    // ── 協議（合議）────────────────────────────────────────────────────────
    case 'orchestra-deliberate': {
      const targets = await getSelectedTargets();
      const sessionId = 'delib_' + Date.now();
      const responseMap = {};

      // ステータスオーバーレイ表示（全AI: 黄色=回答待ち）
      chrome.tabs.sendMessage(tab.id, { type: 'ORCHESTRA_STARTED', targets: targets.map(t => t.name), mode: 'deliberation' });

      // 並列で各AIに送信→回答回収（タブは残す）
      const promises = targets.map(async (target) => {
        try {
          const response = await injectAndCollect(target, text, sessionId);
          responseMap[target.name] = response;
          chrome.tabs.sendMessage(tab.id, { type: 'ORCHESTRA_AI_DONE', ai: target.name }).catch(()=>{});
        } catch (e) {
          responseMap[target.name] = `[エラー: ${e.message}]`;
          chrome.tabs.sendMessage(tab.id, { type: 'ORCHESTRA_AI_DONE', ai: target.name }).catch(()=>{});
        }
      });

      await Promise.all(promises);

      await injectResponsesToClaude(tab.id, text, responseMap);
      setTimeout(() => hideStatusOverlay(tab.id), 4000);
      break;
    }
  }
});

// ── リアルタイムステータスオーバーレイ ──────────────────────────────────────────
// 共有・協議中に右下に各AIの状態を表示する
// 状態: pending=黄色(待機中) / done=青(完了) / error=灰(エラー)

function showStatusOverlay(tabId, aiNames, initialStatus) {
  chrome.scripting.executeScript({
    target: { tabId },
    func: (names) => {
      // 既存オーバーレイを削除
      const existing = document.getElementById('__orchestra_status__');
      if (existing) existing.remove();

      const panel = document.createElement('div');
      panel.id = '__orchestra_status__';
      panel.style.cssText = [
        'position:fixed', 'bottom:20px', 'right:20px', 'z-index:999999',
        'background:#0d0d0f', 'border:1px solid #222228',
        'border-radius:8px', 'padding:12px 16px',
        'font-family:monospace', 'font-size:12px',
        'box-shadow:0 4px 20px rgba(0,0,0,0.6)',
        'min-width:180px',
      ].join(';');

      // タイトル
      const title = document.createElement('div');
      title.style.cssText = 'color:#e8ff47;font-size:10px;font-weight:bold;letter-spacing:1px;margin-bottom:8px;';
      title.textContent = '◈ ORCHESTRA';
      panel.appendChild(title);

      // 各AIの行
      names.forEach(name => {
        const row = document.createElement('div');
        row.id = `__orch_ai_${name.replace(/\s/g,'')}__`;
        row.style.cssText = 'display:flex;align-items:center;gap:8px;padding:3px 0;';

        const dot = document.createElement('div');
        dot.style.cssText = [
          'width:10px', 'height:10px', 'border-radius:50%',
          'background:#e8c547',  // 黄色=待機中
          'flex-shrink:0',
          'animation:orch_pulse 1s infinite',
        ].join(';');

        const label = document.createElement('span');
        label.style.cssText = 'color:#e8e8ec;font-size:11px;';
        label.textContent = name;

        row.appendChild(dot);
        row.appendChild(label);
        panel.appendChild(row);
      });

      // パルスアニメCSS
      if (!document.getElementById('__orch_style__')) {
        const style = document.createElement('style');
        style.id = '__orch_style__';
        style.textContent = `
          @keyframes orch_pulse {
            0%,100% { opacity:1; }
            50% { opacity:0.3; }
          }
        `;
        document.head.appendChild(style);
      }

      document.body.appendChild(panel);
    },
    args: [aiNames],
  }).catch(() => {});
}

function updateStatusOverlay(tabId, aiName, status) {
  // status: 'done'=青 / 'error'=灰
  chrome.scripting.executeScript({
    target: { tabId },
    func: (name, st) => {
      const row = document.getElementById(`__orch_ai_${name.replace(/\s/g,'')}__`);
      if (!row) return;
      const dot = row.querySelector('div');
      if (!dot) return;
      if (st === 'done') {
        dot.style.background = '#47d4ff';  // 青=完了
        dot.style.animation = 'none';
      } else if (st === 'error') {
        dot.style.background = '#555566';  // 灰=エラー
        dot.style.animation = 'none';
      }
    },
    args: [aiName, status],
  }).catch(() => {});
}

function hideStatusOverlay(tabId) {
  chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const el = document.getElementById('__orchestra_status__');
      if (el) {
        el.style.transition = 'opacity 0.5s';
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 500);
      }
    },
  }).catch(() => {});
}

// ── 共通: タブへの通知 ────────────────────────────────────────────────────────

function notifyTab(tabId, message) {
  chrome.scripting.executeScript({
    target: { tabId },
    func: (msg) => {
      const el = document.createElement('div');
      el.style.cssText = [
        'position:fixed', 'top:16px', 'right:16px', 'z-index:999999',
        'background:#1a1a2e', 'color:#e8ff47', 'border:1px solid #e8ff47',
        'border-radius:6px', 'padding:10px 16px', 'font-size:13px',
        'font-family:monospace', 'box-shadow:0 4px 16px rgba(0,0,0,0.5)',
        'pointer-events:none', 'max-width:360px',
      ].join(';');
      el.textContent = '◈ Orchestra: ' + msg;
      document.body.appendChild(el);
      setTimeout(() => el.remove(), 3000);
    },
    args: [message],
  }).catch(() => {});
}

// ── 送る: AIのchat欄にテキストを書き込む ─────────────────────────────────────
// enterSend=false → 書き込みのみ
// enterSend=true  → 書き込み後Enter送信

async function injectTextToAI(target, text, enterSend) {
  // 既存タブを探す
  const tabs = await chrome.tabs.query({});
  let targetTab = tabs.find(t => t.url && t.url.includes(target.domain));

  if (!targetTab) {
    // なければ新規タブ作成
    targetTab = await chrome.tabs.create({ url: target.url, active: false });
    // ページロード完了まで待機
    await waitForTabLoad(targetTab.id);
    await sleep(3000); // JSフレームワーク初期化待ち
  } else {
    // 既存タブ再利用時もDOMが安定するまで待機
    // Perplexity等は前の応答生成中や遷移中の場合があるため
    let reuseWait = 1500;
    if (target.domain.includes('perplexity')) reuseWait = 2500; // クッキーダイアログ残存対策
    await sleep(reuseWait);
  }

  await chrome.scripting.executeScript({
    target: { tabId: targetTab.id },
    func: (injectedText, shouldSend) => {
      // 汎用的なchat入力欄セレクタ
      const selectors = [
        'div[contenteditable="true"]',
        'textarea',
        'input[type="text"]',
        '[role="textbox"]',
      ];

      let el = null;
      for (const sel of selectors) {
        const candidates = document.querySelectorAll(sel);
        for (const c of candidates) {
          const rect = c.getBoundingClientRect();
          if (rect.width > 100 && rect.height > 20) {
            el = c;
            break;
          }
        }
        if (el) break;
      }

      if (!el) {
        console.warn('[Orchestra] chat input not found');
        return false;
      }

      el.focus();

      if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
        el.value = injectedText;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      } else {
        // contenteditable
        el.innerText = injectedText;
        el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: injectedText }));
      }

      if (shouldSend) {
        setTimeout(() => {
          el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
          // Enterボタンを探してクリック（フォールバック）
          const sendBtn = document.querySelector(
            'button[data-testid="send-button"], button[aria-label*="send" i], button[aria-label*="送信"], ' +
            'button[type="submit"]'
          );
          if (sendBtn) sendBtn.click();
        }, 300);
      }

      return true;
    },
    args: [text, enterSend],
  });
}

// ── タブロード完了待機 ────────────────────────────────────────────────────────

function waitForTabLoad(tabId, timeout = 30000) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      chrome.tabs.onUpdated.removeListener(listener);
      reject(new Error('Tab load timeout'));
    }, timeout);

    const listener = (id, changeInfo) => {
      if (id === tabId && changeInfo.status === 'complete') {
        clearTimeout(timer);
        chrome.tabs.onUpdated.removeListener(listener);
        resolve();
      }
    };
    chrome.tabs.onUpdated.addListener(listener);
  });
}

// ── プリフライト: UIブロッカー検知 ───────────────────────────────────────────
// CAPTCHA / クッキーダイアログ / ログイン画面 を検知してtrueを返す

async function detectUIBlocker(tabId) {
  try {
    const results = await chrome.scripting.executeScript({
      target: { tabId },
      func: () => {
        const body = document.body;
        const html = body ? body.innerText.toLowerCase() : '';
        const url  = location.href.toLowerCase();

        // ── Copilot 固有 ────────────────────────────────────────────────────
        // ロボット確認ページ (challenges.cloudflare.com へのリダイレクト含む)
        if (url.includes('challenges.cloudflare') || url.includes('cloudflare')) return 'captcha';
        // Copilot の「続行」/「サインイン」ボタン画面
        if (document.querySelector('#b2c_form, [data-testid="sign-in-btn"], .c-form__input[type="password"]')) return 'login';
        // Copilot の利用規約同意
        if (document.querySelector('[data-testid="tos-accept-btn"], button[id*="accept"], button[id*="agree"]')) return 'cookie';

        // ── Perplexity 固有 ─────────────────────────────────────────────────
        // Perplexity のクッキーバナー
        if (document.querySelector('[data-testid="cookie-banner"], #onetrust-accept-btn-handler, .ot-sdk-container')) return 'cookie';
        // OneTrust 汎用（Perplexityが使用）
        if (document.querySelector('#onetrust-banner-sdk, .onetrust-accept-btn-handler')) return 'cookie';
        // Perplexity ログイン
        if (url.includes('perplexity.ai/login') || document.querySelector('input[name="email"][type="email"]')) return 'login';

        // ── Genspark 固有 ───────────────────────────────────────────────────
        if (url.includes('genspark.ai/login') || url.includes('genspark.ai/auth')) return 'login';
        if (document.querySelector('[class*="login-modal"], [class*="LoginModal"], [class*="auth-modal"]')) return 'login';
        // Genspark CAPTCHA (hCaptcha)
        if (document.querySelector('iframe[src*="hcaptcha"], .h-captcha, #hcaptcha')) return 'captcha';

        // ── 汎用: ログイン画面 ───────────────────────────────────────────────
        if (url.includes('login') || url.includes('signin') || url.includes('/auth')) return 'login';
        if (document.querySelector('input[type="password"]')) return 'login';
        // モーダル内のログインフォーム
        if (document.querySelector('[role="dialog"] input[type="email"], [role="dialog"] input[type="password"]')) return 'login';

        // ── 汎用: CAPTCHA ────────────────────────────────────────────────────
        if (html.includes('robot') || html.includes('captcha') || html.includes('verify you are human')) return 'captcha';
        if (document.querySelector('iframe[src*="recaptcha"], iframe[src*="captcha"], iframe[src*="hcaptcha"]')) return 'captcha';
        // Cloudflare Turnstile
        if (document.querySelector('iframe[src*="challenges.cloudflare"], .cf-turnstile')) return 'captcha';

        // ── 汎用: クッキー同意 ───────────────────────────────────────────────
        const cookieKeywords = ['cookie', 'consent', 'accept all', 'すべて受け入れ', 'クッキー', 'we use cookies'];
        if (cookieKeywords.some(k => html.includes(k))) {
          const btns = Array.from(document.querySelectorAll('button, a[role="button"]'));
          const acceptBtn = btns.find(b => {
            const t = (b.innerText || '').toLowerCase();
            return t.includes('accept') || t.includes('agree') || t.includes('受け入れ') || t.includes('同意') || t.includes('allow');
          });
          if (acceptBtn) return 'cookie';
        }

        return null; // ブロッカーなし
      },
    });
    return (results && results[0] && results[0].result) || null;
  } catch (e) {
    return null;
  }
}

// ── プリフライト: ブロッカー自動突破を試みる ──────────────────────────────────

async function tryAutoBypass(tabId, blockerType) {
  if (blockerType === 'cookie') {
    try {
      await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
          // ── Perplexity: OneTrust ────────────────────────────────────────
          const oneTrust = document.querySelector(
            '#onetrust-accept-btn-handler, .onetrust-accept-btn-handler, #accept-recommended-btn-handler'
          );
          if (oneTrust) { oneTrust.click(); return true; }

          // ── Copilot: 利用規約同意ボタン ─────────────────────────────────
          const copilotAccept = document.querySelector(
            '[data-testid="tos-accept-btn"], button[id*="accept"], button[id*="agree"]'
          );
          if (copilotAccept) { copilotAccept.click(); return true; }

          // ── 汎用: テキストマッチ ─────────────────────────────────────────
          const btns = Array.from(document.querySelectorAll('button, a[role="button"]'));
          const acceptBtn = btns.find(b => {
            const t = (b.innerText || '').toLowerCase();
            return t.includes('accept all') || t.includes('accept cookies') ||
                   t.includes('agree') || t.includes('allow all') ||
                   t.includes('受け入れ') || t.includes('同意') || t.includes('allow');
          });
          if (acceptBtn) { acceptBtn.click(); return true; }
          return false;
        },
      });
      await sleep(2000); // クッキー処理後の再描画待ち
      return true;
    } catch (e) { return false; }
  }
  return false; // CAPTCHA/ログインは自動突破不可（ユーザーに委ねる）
}

// ── プリフライト: PREFLIGHT_OKチェック ───────────────────────────────────────
// 定型文を送信してORCHESTRA_PREFLIGHT_OKが返るか確認する

async function runPreflightCheck(tabId, aiName) {
  const PREFLIGHT_PROMPT =
    `接続確認テストです。以下の3点に答えてください。\n` +
    `Q1. 現在、ロボット確認・ログイン・クッキーダイアログは表示されていますか？（はい/いいえ）\n` +
    `Q2. 入力欄は操作可能な状態ですか？（はい/いいえ）\n` +
    `Q3. 末尾に「ORCHESTRA_PREFLIGHT_OK」と記載してください。`;

  // プリフライトプロンプトを送信
  await chrome.scripting.executeScript({
    target: { tabId },
    func: (prompt) => {
      const selectors = ['div[contenteditable="true"]', 'textarea', 'input[type="text"]', '[role="textbox"]'];
      let el = null;
      for (const sel of selectors) {
        const candidates = document.querySelectorAll(sel);
        for (const c of candidates) {
          const rect = c.getBoundingClientRect();
          if (rect.width > 100 && rect.height > 20) { el = c; break; }
        }
        if (el) break;
      }
      if (!el) return false;
      el.focus();
      if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
        el.value = prompt;
        el.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        el.innerText = prompt;
        el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: prompt }));
      }
      setTimeout(() => {
        el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
        const sendBtn = document.querySelector(
          'button[data-testid="send-button"], button[aria-label*="send" i], button[aria-label*="送信"], button[type="submit"]'
        );
        if (sendBtn) sendBtn.click();
      }, 300);
      return true;
    },
    args: [PREFLIGHT_PROMPT],
  });

  // 回答を待機してPREFLIGHT_OKを確認
  const response = await waitForResponse(tabId, 45000, 2000);
  const ok = response.includes('ORCHESTRA_PREFLIGHT_OK');
  console.log(`[Orchestra] Preflight ${aiName}: ${ok ? 'OK' : 'FAILED'} — ${response.slice(0, 80)}`);
  return ok;
}

// ── 協議: AIに送信して回答を回収する ─────────────────────────────────────────

async function injectAndCollect(target, text, sessionId) {
  // ── 協議: 既存ログイン済みタブを優先再利用 ───────────────────────────
  // ログインが必要なAI（ChatGPT/Genspark等）は新規タブだとログイン画面になる場合がある。
  // 既存の同ドメインタブがあれば target.url へ遷移させて再利用（古い会話への追記を防ぐ）。
  // タブは閉じずに残し、次回合議でも同じタブを再利用する。
  const allTabs = await chrome.tabs.query({});
  const existingTab = allTabs.find(t => t.url && t.url.includes(target.domain));

  let targetTab;

  if (existingTab) {
    // 既存タブを新規chatページへ遷移させて再利用
    targetTab = existingTab;
    await chrome.tabs.update(targetTab.id, { url: target.url, active: false });
    await waitForTabLoad(targetTab.id);
  } else {
    // 既存タブなし → 新規タブ作成（次回以降はこのタブを再利用）
    targetTab = await chrome.tabs.create({ url: target.url, active: false });
    await waitForTabLoad(targetTab.id);
  }

  // サービス別初期化待ち（スライダー設定値をベースに調整）
  const baseWait = await getWaitTime();
  let initWait = baseWait;
  if (target.domain.includes('perplexity')) initWait = Math.max(baseWait, 3000); // クッキーダイアログ対策
  if (target.domain.includes('genspark'))   initWait = Math.max(baseWait, 3000); // ログイン確認対策
  if (target.domain.includes('chatgpt'))    initWait = Math.max(baseWait, 3000); // ログイン確認対策
  await sleep(initWait);

  // ── プリフライトチェック ──────────────────────────────────────────────────
  // 1. UIブロッカー検知
  const blocker = await detectUIBlocker(targetTab.id);
  if (blocker) {
    console.log(`[Orchestra] UIBlocker detected for ${target.name}: ${blocker}`);
    // 2. 自動突破を試みる（クッキーのみ）
    const bypassed = await tryAutoBypass(targetTab.id, blocker);
    if (!bypassed) {
      // 自動突破不可 → タブをアクティブにしてユーザーに知らせる
      await chrome.tabs.update(targetTab.id, { active: true });
      await sleep(15000); // ユーザーが手動で処理する時間（15秒）
      await chrome.tabs.update(targetTab.id, { active: false });
    }
  }

  // 3. プリフライトOK確認（ブロッカーがあった場合のみ実行）
  if (blocker) {
    const preflightOk = await runPreflightCheck(targetTab.id, target.name);
    if (!preflightOk) {
      return `[プリフライト失敗: ${target.name} — UIブロッカー(${blocker})が解除されていない可能性があります]`;
    }
    // プリフライト後は少し待機してから本題を送信
    await sleep(2000);
  }

  // ── 注入前のテキスト長を記録（Genspark等の古データ誤取得防止）────────
  // 注入後に増えた部分のみを新しい回答として返す
  let baseTextLength = 0;
  try {
    const baseResults = await chrome.scripting.executeScript({
      target: { tabId: targetTab.id },
      func: () => {
        const selectors = [
          '[data-message-author-role="assistant"] .markdown',
          '[data-message-author-role="assistant"]',
          '.model-response-text', 'model-response',
          '[data-testid="answer"]', '.prose',
          '[class*="answer-content"]', '[class*="AgentResponse"]',
          '[class*="response-content"]', '[class*="spark-answer"]',
          '[class*="chat-answer"]', '[class*="message-content"]',
          'div[class*="assistant"]', '[data-role="assistant"]',
        ];
        let best = '';
        for (const sel of selectors) {
          try {
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
              const t = (els[els.length - 1].innerText || '').trim();
              if (t.length > best.length) best = t;
            }
          } catch(e) {}
        }
        return best.length;
      },
    });
    baseTextLength = (baseResults && baseResults[0] && baseResults[0].result) || 0;
  } catch(e) { baseTextLength = 0; }

  // テキストを書き込んでEnter送信
  await chrome.scripting.executeScript({
    target: { tabId: targetTab.id },
    func: (injectedText, domain) => {
      // ── 入力欄を探す ────────────────────────────────────────────────────
      const selectors = [
        '[role="textbox"]',          // Perplexity優先（role=textbox DIV）
        'div[contenteditable="true"]',
        'textarea',
        'input[type="text"]',
      ];

      let el = null;
      for (const sel of selectors) {
        const candidates = document.querySelectorAll(sel);
        for (const c of candidates) {
          const rect = c.getBoundingClientRect();
          if (rect.width > 100 && rect.height > 20) {
            el = c;
            break;
          }
        }
        if (el) break;
      }

      if (!el) return false;

      el.focus();

      if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
        // 通常フォーム
        el.value = injectedText;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      } else {
        // contenteditable / role=textbox DIV
        // ── 方式1: execCommand（ProseMirror/Draft.js対応）─────────────────
        try {
          el.focus();
          // 既存テキストを全選択して削除
          document.execCommand('selectAll', false, null);
          document.execCommand('delete', false, null);
          // テキスト挿入
          const inserted = document.execCommand('insertText', false, injectedText);
          if (!inserted) throw new Error('execCommand failed');
        } catch(e) {
          // ── 方式2: innerText直接代入（フォールバック）──────────────────
          el.innerText = injectedText;
          el.dispatchEvent(new InputEvent('input', {
            bubbles: true, inputType: 'insertText', data: injectedText
          }));
        }
      }

      // ── 送信ボタンを探してクリック ────────────────────────────────────
      setTimeout(() => {
        // Perplexity固有の送信ボタン
        const perplexitySend = document.querySelector(
          'button[aria-label="Submit"], button[data-testid="submit-button"], ' +
          'button svg[data-icon="arrow-right"], ' +
          'button[class*="submit"], button[class*="send"]'
        );

        // 汎用送信ボタン
        const genericSend = document.querySelector(
          'button[data-testid="send-button"], button[aria-label*="send" i], ' +
          'button[aria-label*="送信"], button[type="submit"]'
        );

        const sendBtn = perplexitySend || genericSend;

        if (sendBtn) {
          sendBtn.click();
        } else {
          // フォールバック: Enterキー
          el.dispatchEvent(new KeyboardEvent('keydown', {
            key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true
          }));
        }
      }, 500);

      return true;
    },
    args: [text, target.domain],
  });

  // 回答ストリーム完了を待機してテキスト取得（注入前テキスト長を基準に増分のみ返す）
  const response = await waitForResponse(targetTab.id, 90000, 2500, baseTextLength);
  return response;
}

// ── 協議: ストリーム完了検知 → 回答テキスト取得 ───────────────────────────────
// テキスト変化が STABLE_MS 間止まったら完了と判定

async function waitForResponse(tabId, timeout = 90000, stableMs = 2500, baseTextLength = 0) {
  const start = Date.now();

  // 少し待ってからポーリング開始（送信→応答開始ラグ）
  await sleep(4000);

  let lastText = '';
  let stableStart = null;

  while (Date.now() - start < timeout) {
    await sleep(800);

    let currentText = '';
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
          // 各AIの最終アシスタントメッセージを取得する汎用セレクタ
          const selectors = [
            // ChatGPT
            '[data-message-author-role="assistant"] .markdown',
            '[data-message-author-role="assistant"]',
            // Gemini
            '.model-response-text',
            'model-response',
            // Perplexity
            '[data-testid="answer"]',
            '.prose',
            // Copilot (copilot.microsoft.com) 複数候補
            '[data-content="ai-response"]',
            'cib-message[source="bot"] cib-message-content',
            '[data-testid="conversationTurnBotMessage"]',
            '.ac-textBlock',
            'div[class*="responseText"]',
            'div[class*="message"][class*="bot"]',
            // Genspark
            '[class*="answer-content"]',
            '[class*="AgentResponse"]',
            '[class*="response-content"]',
            '[class*="spark-answer"]',
            '[class*="chat-answer"]',
            '[class*="message-content"]',
            'div[class*="assistant"]',
            '.agent-response p',
            '[data-role="assistant"]',
            // 汎用フォールバック
            'main [role="presentation"] p',
            'main p',
            '[role="main"] p',
          ];

          let best = '';
          for (const sel of selectors) {
            try {
              const els = document.querySelectorAll(sel);
              if (els.length > 0) {
                const last = els[els.length - 1];
                const t = last.innerText || last.textContent || '';
                if (t.trim().length > best.length) best = t.trim();
              }
            } catch(e) {}
          }

          // Copilot フォールバック: p/liタグ全結合
          if (best.length < 50) {
            const allP = Array.from(document.querySelectorAll('p, li'));
            const combined = allP
              .map(el => (el.innerText || '').trim())
              .filter(t => t.length > 30)
              .join('\n');
            if (combined.length > best.length) best = combined;
          }

          return best;
        },
        args: [],
      });
      currentText = (results && results[0] && results[0].result) || '';
    } catch (e) {
      // タブが閉じられた等
      break;
    }

    if (currentText.length > 0 && currentText.length > baseTextLength) {
      if (currentText === lastText) {
        if (!stableStart) stableStart = Date.now();
        if (Date.now() - stableStart >= stableMs) {
          // stableMs間変化なし → ストリーム完了
          // baseTextLength分は古いデータなので除去して返す
          return currentText.length > baseTextLength
            ? currentText.slice(baseTextLength).trim() || currentText
            : currentText;
        }
      } else {
        lastText = currentText;
        stableStart = null; // 変化があったのでリセット
      }
    }
  }

  // タイムアウト: 最後に取得できたテキストを返す
  // ログイン画面テキストを誤取得した場合はタイムアウト扱い
  const loginPatterns = [
    'ログインすると', 'log in to', 'sign in to', 'create an account',
    'アカウントを作成', 'サインイン', 'パスワードを入力',
    'continue with google', 'continue with microsoft',
  ];
  if (loginPatterns.some(p => lastText.toLowerCase().includes(p.toLowerCase()))) {
    return '[タイムアウト: ログイン画面が検出されました。事前にログインしてください]';
  }
  return lastText || '[タイムアウト: 回答を取得できませんでした]';
}

// ── 協議: 回答をClaudeのchat欄に返す ─────────────────────────────────────────

async function injectResponsesToClaude(sourceTabId, originalText, responseMap) {
  // 回答をまとめてフォーマット
  const parts = Object.entries(responseMap)
    .map(([ai, resp]) => `## ${ai}\n\n${resp}`)
    .join('\n\n---\n\n');

  const synthesisText =
    `【Orchestra 協議結果】\n\n` +
    `【質問・テーマ】\n${originalText.slice(0, 500)}\n\n` +
    `---\n\n${parts}\n\n---\n\n` +
    `上記の各AIの回答を比較・統合してください。重要な一致点・相違点・結論をまとめてください。`;

  // Claudeのタブを探す（送信元優先）
  const claudeTabs = await chrome.tabs.query({ url: 'https://claude.ai/*' });
  const targetTab = claudeTabs.find(t => t.id === sourceTabId) || claudeTabs[0];

  if (!targetTab) {
    console.warn('[Orchestra] Claude tab not found');
    return;
  }

  // Claudeのchat欄に書き込んでEnter
  await chrome.scripting.executeScript({
    target: { tabId: targetTab.id },
    func: (text) => {
      // claude.aiのchat入力セレクタ
      const el =
        document.querySelector('div[contenteditable="true"].ProseMirror') ||
        document.querySelector('div[contenteditable="true"]') ||
        document.querySelector('textarea');

      if (!el) {
        console.warn('[Orchestra] Claude input not found');
        return false;
      }

      el.focus();

      if (el.tagName === 'TEXTAREA') {
        el.value = text;
        el.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        // ProseMirror用
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(el);
        selection.removeAllRanges();
        selection.addRange(range);
        document.execCommand('insertText', false, text);
      }

      // 少し待ってからEnter
      setTimeout(() => {
        el.dispatchEvent(new KeyboardEvent('keydown', {
          key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true
        }));
        const sendBtn = document.querySelector(
          'button[aria-label*="Send" i], button[data-testid="send-button"], ' +
          'button[aria-label*="送信"]'
        );
        if (sendBtn) sendBtn.click();
      }, 500);

      return true;
    },
    args: [synthesisText],
  });

  // Claudeタブをフォーカス
  await chrome.tabs.update(targetTab.id, { active: true });
  chrome.windows.update(targetTab.windowId, { focused: true }).catch(() => {});
}

// ── Free: Message router ──────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    try {
      switch (msg.type) {
        case 'SAVE_MESSAGE':
          await saveMessage(msg.payload);
          sendResponse({ ok: true });
          break;
        case 'GET_MESSAGES':
          const messages = msg.query
            ? await searchMessages(msg.query)
            : await getAllMessages(msg.limit || 200);
          sendResponse({ ok: true, data: messages });
          break;
        case 'GET_STATS':
          const stats = await getStats();
          sendResponse({ ok: true, data: stats });
          break;
        case 'EXPORT_JSON':
          const json = await exportJSON();
          sendResponse({ ok: true, data: json });
          break;
        case 'EXPORT_CSV':
          const csv = await exportCSV();
          sendResponse({ ok: true, data: csv });
          break;
        case 'CLEAR_ALL':
          await clearAll();
          sendResponse({ ok: true });
          break;
        case 'PING':
          sendResponse({ ok: true });
          break;

        // ── 送り先AI設定の保存/取得 ──────────────────────────────────────
        case 'SET_TARGETS':
          await chrome.storage.sync.set({ orchestra_targets: msg.targets });
          sendResponse({ ok: true });
          break;
        case 'GET_TARGETS': {
          const data = await new Promise(r => chrome.storage.sync.get(['orchestra_targets'], r));
          sendResponse({ ok: true, targets: data.orchestra_targets || DEFAULT_TARGETS });
          break;
        }

        // ── Pro/One: License ─────────────────────────────────────────────
        case 'GET_PLAN':
          const plan = await getLicensePlan();
          sendResponse({ ok: true, plan });
          break;
        case 'SET_LICENSE': {
          const detectedPlan = validateLicense(msg.key);
          await chrome.storage.sync.set({
            license_key: msg.key.trim(),
            license_plan: detectedPlan,
          });
          sendResponse({ ok: true, plan: detectedPlan });
          break;
        }
        case 'REMOVE_LICENSE':
          await chrome.storage.sync.remove(['license_key', 'license_plan']);
          sendResponse({ ok: true, plan: 'free' });
          break;

        // ── Pro: Orchestra launch ────────────────────────────────────────
        case 'START_ORCHESTRA': {
          const result = await runOrchestraPro(msg.text, sender.tab?.id);
          sendResponse(result);
          break;
        }

        // ── One: Orchestra One launch ────────────────────────────────────
        case 'START_ORCHESTRA_ONE': {
          const resultOne = await runOrchestraOne(msg.text, sender.tab?.id);
          sendResponse(resultOne);
          break;
        }

        default:
          sendResponse({ ok: false, error: 'Unknown message type' });
      }
    } catch (err) {
      sendResponse({ ok: false, error: err.message });
    }
  })();
  return true;
});

// ── Pro/One: License management ───────────────────────────────────────────────

function getLicensePlan() {
  return new Promise(resolve => {
    chrome.storage.sync.get(['license_plan'], data => {
      resolve(data.license_plan || 'free');
    });
  });
}

function validateLicense(key) {
  if (!key || typeof key !== 'string') return 'free';
  const k = key.trim().toUpperCase();
  if (k.startsWith('ONE-')) return 'one';
  if (k.startsWith('OPR-')) return 'pro';
  return 'free';
}

function isPro(plan) {
  return plan === 'pro' || plan === 'one';
}

function isOne(plan) {
  return plan === 'one';
}

// ── Pro: Orchestra session state ──────────────────────────────────────────────

const orchestraSessions = new Map();
const pendingInjections = new Map();

function createOrchestraSession(sourceTabId) {
  const id = 'orch_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6);
  orchestraSessions.set(id, {
    id,
    sourceTabId,
    status: 'running',
    responses: {},
    tabIds: [],
    createdAt: Date.now(),
  });
  return id;
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status !== 'complete') return;
  if (!pendingInjections.has(tabId)) return;

  const data = pendingInjections.get(tabId);
  pendingInjections.delete(tabId);

  setTimeout(() => {
    chrome.tabs.sendMessage(tabId, {
      type: 'ORCHESTRA_INJECT',
      prompt: data.prompt,
      sessionId: data.sessionId,
      aiName: data.aiName,
    }).catch(err => {
      console.warn('[Orchestra] Inject failed for', data.aiName, err.message);
    });
  }, 5000);
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type !== 'ORCHESTRA_RESPONSE') return;

  const session = orchestraSessions.get(msg.sessionId);
  if (!session) return;

  const label = msg.aiName || msg.ai || 'Unknown AI';
  session.responses[label] = msg.response;

  // 各AI完了をパネルに通知（カウントアップ停止・✓表示）
  if (session.sourceTabId) {
    chrome.tabs.sendMessage(session.sourceTabId, {
      type: 'ORCHESTRA_AI_DONE',
      ai: label,
      sessionId: msg.sessionId,
    }).catch(() => {});
  }

  const collected = Object.keys(session.responses).length;
  if (collected >= AI_TARGETS.length) {
    session.status = 'complete';
    synthesizeAndInject(session);
  }
});

const AI_TARGETS = [
  { name: 'ChatGPT',    url: 'https://chatgpt.com' },
  { name: 'Gemini',     url: 'https://gemini.google.com/app' },
  { name: 'Perplexity', url: 'https://www.perplexity.ai' },
  { name: 'Copilot',    url: 'https://copilot.microsoft.com' },
];


async function runOrchestraPro(conversationText, sourceTabId) {
  const plan = await getLicensePlan();
  if (!isPro(plan)) {
    return { ok: false, error: 'Pro plan required. Please activate your license key.' };
  }

  const sessionId = createOrchestraSession(sourceTabId);
  const session = orchestraSessions.get(sessionId);
  const prompt = conversationText;

  for (const target of AI_TARGETS) {
    try {
      const tab = await chrome.tabs.create({ url: target.url, active: false });
      session.tabIds.push(tab.id);
      pendingInjections.set(tab.id, {
        sessionId,
        aiName: target.name,
        prompt,
      });
    } catch (e) {
      console.warn('[Orchestra] Tab creation failed for', target.name, e.message);
    }
  }

  if (sourceTabId) {
    chrome.tabs.sendMessage(sourceTabId, {
      type: 'ORCHESTRA_STARTED',
      sessionId,
      targets: AI_TARGETS.map(t => t.name),
      mode: 'deliberation',
    }).catch(e => console.error("[Orchestra] STARTED failed:", e.message));
  }

  return { ok: true, sessionId };
}

async function synthesizeAndInject(session) {
  const parts = Object.entries(session.responses)
    .map(([ai, resp]) => `## ${ai}\n\n${resp.slice(0, 2000)}`)
    .join('\n\n---\n\n');

  const synthesisPrompt =
    `以下は同じ質問・テーマに対する4つのAIの回答です。` +
    `それぞれの視点を統合・比較分析し、最も重要な洞察・一致点・相違点・結論をまとめてください。\n\n` +
    `${parts}`;

  const claudeTabs = await chrome.tabs.query({ url: 'https://claude.ai/*' });
  const targetTab = claudeTabs.find(t => t.id === session.sourceTabId) || claudeTabs[0];

  if (targetTab) {
    chrome.tabs.sendMessage(targetTab.id, {
      type: 'ORCHESTRA_SYNTHESIZE',
      prompt: synthesisPrompt,
      sessionId: session.id,
    }).catch(() => {});

    await chrome.tabs.update(targetTab.id, { active: true });
    chrome.windows.update(targetTab.windowId, { focused: true }).catch(() => {});
  }

  const removeIds = session.tabIds.filter(id => id != null);
  if (removeIds.length > 0) {
    chrome.tabs.remove(removeIds).catch(() => {});
  }
}

async function runOrchestraOne(conversationText, sourceTabId) {
  const plan = await getLicensePlan();
  if (!isOne(plan)) {
    return { ok: false, error: 'Orchestra One plan required.' };
  }

  const prompt = conversationText;

  return new Promise(resolve => {
    let port;
    try {
      port = chrome.runtime.connectNative('com.sirius_lab.orchestra_one');
    } catch (e) {
      resolve({ ok: false, error: 'Native host not installed. Please run install.bat.' });
      return;
    }

    port.onMessage.addListener(async (response) => {
      port.disconnect();
      if (response.type === 'ORCHESTRA_RESULT' && response.results) {
        const fakeSession = {
          id: 'one_' + Date.now(),
          sourceTabId,
          responses: response.results,
          tabIds: [],
        };
        await synthesizeAndInject(fakeSession);
        resolve({ ok: true });
      } else {
        resolve({ ok: false, error: response.error || 'Unknown error from native host' });
      }
    });

    port.onDisconnect.addListener(() => {
      if (chrome.runtime.lastError) {
        resolve({ ok: false, error: 'Native host disconnected: ' + chrome.runtime.lastError.message });
      }
    });

    port.postMessage({ type: 'RUN_ORCHESTRA', prompt });
  });
}
