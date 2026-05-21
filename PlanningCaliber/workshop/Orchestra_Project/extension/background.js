// Orchestra - background.js
// IndexedDB management, message routing, export
// v0.2.0: + License management, Orchestra Pro/One

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
  return '﻿' + [header, ...rows].join('\n');
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

        // ── Pro/One: License ─────────────────────────────────────────────────
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

        // ── Pro: Orchestra launch ────────────────────────────────────────────
        case 'START_ORCHESTRA': {
          const result = await runOrchestraPro(msg.text, sender.tab?.id);
          sendResponse(result);
          break;
        }

        // ── One: Orchestra One launch ────────────────────────────────────────
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

// ── Free: Keepalive alarm ─────────────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create('keepAlive', { periodInMinutes: 0.4 }); // 24秒間隔
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

initDB().catch(console.error);

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

// tabId -> { sessionId, aiName, prompt } — persists across SW wakeups
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

// ── Pro: Tab load listener (top-level, survives SW restart) ───────────────────

chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status !== 'complete') return;
  if (!pendingInjections.has(tabId)) return;

  const data = pendingInjections.get(tabId);
  pendingInjections.delete(tabId);

  // Give the page's JS frameworks time to initialize
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

// ── Pro: Orchestra response collector ────────────────────────────────────────

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

// ── Pro: Orchestra targets ────────────────────────────────────────────────────

const AI_TARGETS = [
  { name: 'ChatGPT',    url: 'https://chatgpt.com' },
  { name: 'Gemini',     url: 'https://gemini.google.com/app' },
  { name: 'Perplexity', url: 'https://www.perplexity.ai' },
  { name: 'Copilot',    url: 'https://copilot.microsoft.com' },
];

function buildOrchestraPrompt(text) {
  return `以下の内容について、あなたの見解と詳細な分析を教えてください。独自の視点を活かして回答してください。\n\n---\n${text.slice(0, 3000)}\n---`;
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ── Pro: runOrchestraPro ──────────────────────────────────────────────────────

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
      // Register pending injection — will fire when tab finishes loading
      pendingInjections.set(tab.id, {
        sessionId,
        aiName: target.name,
        prompt,
      });
    } catch (e) {
      console.warn('[Orchestra] Tab creation failed for', target.name, e.message);
    }
  }

  // Notify source tab so it can show status overlay
  if (sourceTabId) {
    chrome.tabs.sendMessage(sourceTabId, {
      type: 'ORCHESTRA_STARTED',
      sessionId,
      targets: AI_TARGETS.map(t => t.name),
    }).catch(() => {});
  }

  return { ok: true, sessionId };
}

// ── Pro: synthesize and inject back to claude.ai ──────────────────────────────

async function synthesizeAndInject(session) {
  const parts = Object.entries(session.responses)
    .map(([ai, resp]) => `## ${ai}\n\n${resp.slice(0, 2000)}`)
    .join('\n\n---\n\n');

  const synthesisPrompt =
    `以下は同じ質問・テーマに対する4つのAIの回答です。` +
    `それぞれの視点を統合・比較分析し、最も重要な洞察・一致点・相違点・結論をまとめてください。\n\n` +
    `${parts}`;

  // Find the most recently active claude.ai tab
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

  // Close AI tabs
  const removeIds = session.tabIds.filter(id => id != null);
  if (removeIds.length > 0) {
    chrome.tabs.remove(removeIds).catch(() => {});
  }
}

// ── One: Orchestra One (Native Messaging) ────────────────────────────────────

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
        // Build a fake session for synthesize
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
