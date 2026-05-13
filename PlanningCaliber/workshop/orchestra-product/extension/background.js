// AI Conversation Logger - background.js
// IndexedDB management, message routing, export

const DB_NAME = 'ai_logger_db';
const DB_VERSION = 1;
const STORE_NAME = 'messages';

let db = null;

// Initialize IndexedDB
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

    req.onsuccess = (e) => {
      db = e.target.result;
      resolve(db);
    };

    req.onerror = () => reject(req.error);
  });
}

// Save a single message record
async function saveMessage(record) {
  const database = await initDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    const req = store.put(record); // put = upsert (idempotent)
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  });
}

// Get all messages, newest first
async function getAllMessages(limit = 500) {
  const database = await initDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const index = store.index('timestamp');
    const req = index.openCursor(null, 'prev'); // descending
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

// Search messages by keyword
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
        if (msg.content.toLowerCase().includes(q)) {
          results.push(msg);
        }
        if (results.length < limit) cursor.continue();
        else resolve(results.sort((a, b) => b.timestamp.localeCompare(a.timestamp)));
      } else {
        resolve(results.sort((a, b) => b.timestamp.localeCompare(a.timestamp)));
      }
    };
    req.onerror = () => reject(req.error);
  });
}

// Get stats
async function getStats() {
  const database = await initDB();
  return new Promise((resolve, reject) => {
    const tx = database.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const countReq = store.count();

    countReq.onsuccess = () => {
      const total = countReq.result;
      // Get sessions count via cursor
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

// Export all messages as JSON string
async function exportJSON() {
  const msgs = await getAllMessages(10000);
  return JSON.stringify(msgs, null, 2);
}

// Export as CSV
async function exportCSV() {
  const msgs = await getAllMessages(10000);
  const header = 'id,service,role,timestamp,session_id,content';
  const rows = msgs.map(m => {
    const content = '"' + m.content.replace(/"/g, '""').replace(/\n/g, '\\n') + '"';
    return `${m.id},${m.service},${m.role},${m.timestamp},${m.session_id},${content}`;
  });
  return [header, ...rows].join('\n');
}

// Delete all data
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

// Message router
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

        default:
          sendResponse({ ok: false, error: 'Unknown message type' });
      }
    } catch (err) {
      sendResponse({ ok: false, error: err.message });
    }
  })();
  return true; // keep channel open for async
});

// Init on startup
initDB().catch(console.error);

// ── 右クリックメニュー（共有・協議・ヒント・グレイト）──────────────────────
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({ id:'orch_share',       title:'MoCKAで共有',         contexts:['selection'] });
    chrome.contextMenus.create({ id:'orch_collaborate', title:'MoCKAで協議',         contexts:['selection'] });
    chrome.contextMenus.create({ id:'orch_hint',        title:'ヒント！',             contexts:['selection','page'] });
    chrome.contextMenus.create({ id:'orch_great',       title:'グレイト！',           contexts:['selection','page'] });
    chrome.contextMenus.create({ id:'orch_mataka',      title:'またか！（再発）',      contexts:['selection','page'] });
    chrome.contextMenus.create({ id:'orch_claim',       title:'クレーム！（インシデント）', contexts:['selection','page'] });
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const text = info.selectionText || '';
  const url  = tab ? tab.url : '';

  if (info.menuItemId === 'orch_share') {
    if (!text) return;
    try {
      await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ c:'B', o:text, memo:'Orchestraから共有' })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'共有完了', message:'MoCKAに送信しました' });
    } catch(e) { console.error('share error:', e); }
    return;
  }

  if (info.menuItemId === 'orch_collaborate') {
    if (!text) return;
    try {
      await fetch('http://127.0.0.1:5000/orchestra', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ prompt:text, mode:'orchestra' })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'協議開始', message:'4AI合議を開始しました' });
    } catch(e) { console.error('collaborate error:', e); }
    return;
  }

  if (info.menuItemId === 'orch_hint' || info.menuItemId === 'orch_great') {
    const outcome = info.menuItemId === 'orch_great' ? 'success_great' : 'success_hint';
    const label   = info.menuItemId === 'orch_great' ? 'グレイト！' : 'ヒント！';
    try {
      await fetch('http://127.0.0.1:5000/success', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ text:text, what_type:outcome, source:url, label:label, timestamp:new Date().toISOString() })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:Orchestra , message:(text||url).slice(0,60) });
    } catch(e) { console.error('success error:', e); }
    return;
  }

  if (info.menuItemId === 'orch_mataka') {
    try {
      await fetch('http://127.0.0.1:5000/mataka', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ text:text, url:url, timestamp:new Date().toISOString() })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'またか！記録', message:(text||'').slice(0,60) });
    } catch(e) { console.error('mataka error:', e); }
    return;
  }

  if (info.menuItemId === 'orch_claim') {
    try {
      await fetch('http://127.0.0.1:5000/claim', {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ text:text, url:url, timestamp:new Date().toISOString() })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'クレーム！記録', message:(text||'').slice(0,60) });
    } catch(e) { console.error('claim error:', e); }
    return;
  }
});
