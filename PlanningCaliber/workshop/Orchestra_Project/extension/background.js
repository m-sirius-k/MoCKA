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
      for (const target of targets) {
        await injectTextToAI(target, text, false); // Enter押さない
      }
      notifyTab(tab.id, `→ ${targets.map(t => t.name).join(' / ')} に送りました`);
      break;
    }

    // ── 協議（合議）────────────────────────────────────────────────────────
    case 'orchestra-deliberate': {
      const targets = await getSelectedTargets();
      const sessionId = 'delib_' + Date.now();
      const responseMap = {};

      notifyTab(tab.id, `⚡ 協議開始: ${targets.map(t => t.name).join(' / ')}`);

      // 並列で各AIに送信→回答回収
      const promises = targets.map(async (target) => {
        try {
          const response = await injectAndCollect(target, text, sessionId);
          responseMap[target.name] = response;
        } catch (e) {
          responseMap[target.name] = `[エラー: ${e.message}]`;
        }
      });

      await Promise.all(promises);

      // 回答をClaudeに返す
      await injectResponsesToClaude(tab.id, text, responseMap);
      break;
    }
  }
});

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

// ── 協議: AIに送信して回答を回収する ─────────────────────────────────────────

async function injectAndCollect(target, text, sessionId) {
  const tabs = await chrome.tabs.query({});
  let targetTab = tabs.find(t => t.url && t.url.includes(target.domain));

  if (!targetTab) {
    targetTab = await chrome.tabs.create({ url: target.url, active: false });
    await waitForTabLoad(targetTab.id);
    await sleep(3000);
  }

  // テキストを書き込んでEnter送信
  await chrome.scripting.executeScript({
    target: { tabId: targetTab.id },
    func: (injectedText) => {
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

      if (!el) return false;

      el.focus();

      if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
        el.value = injectedText;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
      } else {
        el.innerText = injectedText;
        el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: injectedText }));
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
    args: [text],
  });

  // 回答ストリーム完了を待機してテキスト取得
  const response = await waitForResponse(targetTab.id);
  return response;
}

// ── 協議: ストリーム完了検知 → 回答テキスト取得 ───────────────────────────────
// テキスト変化が STABLE_MS 間止まったら完了と判定

async function waitForResponse(tabId, timeout = 90000, stableMs = 2500) {
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
            // Gemini
            '.model-response-text',
            'model-response',
            // Perplexity
            '[data-testid="answer"]',
            '.prose',
            // Copilot
            '[class*="response"]',
            // 汎用
            '[role="presentation"] p',
          ];

          let best = '';
          for (const sel of selectors) {
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
              const last = els[els.length - 1];
              const t = last.innerText || last.textContent || '';
              if (t.trim().length > best.length) best = t.trim();
            }
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

    if (currentText.length > 0) {
      if (currentText === lastText) {
        if (!stableStart) stableStart = Date.now();
        if (Date.now() - stableStart >= stableMs) {
          // stableMs間変化なし → ストリーム完了
          return currentText;
        }
      } else {
        lastText = currentText;
        stableStart = null; // 変化があったのでリセット
      }
    }
  }

  // タイムアウト: 最後に取得できたテキストを返す
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

function buildOrchestraPrompt(text) {
  return `以下の内容について、あなたの見解と詳細な分析を教えてください。独自の視点を活かして回答してください。\n\n---\n${text.slice(0, 3000)}\n---`;
}

async function runOrchestraPro(conversationText, sourceTabId) {
  const plan = await getLicensePlan();
  if (!isPro(plan)) {
    return { ok: false, error: 'Pro plan required. Please activate your license key.' };
  }

  const sessionId = createOrchestraSession(sourceTabId);
  const session = orchestraSessions.get(sessionId);
  const prompt = buildOrchestraPrompt(conversationText);

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
    }).catch(() => {});
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

  const prompt = buildOrchestraPrompt(conversationText);

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
