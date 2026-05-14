// Orchestra - background.js
// IndexedDB management, message routing, export

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

        default:
          sendResponse({ ok: false, error: 'Unknown message type' });
      }
    } catch (err) {
      sendResponse({ ok: false, error: err.message });
    }
  })();
  return true;
});


// Alarms-based keepAlive (MV3 Service Worker自動停止対策)
chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create('keepAlive', { periodInMinutes: 0.4 }); // 24秒間隔
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keepAlive') {
    initDB().catch(console.error); // DB接続でSWを維持
  }
});

// 起動時にアラームが消えていたら再登録
chrome.alarms.get('keepAlive', (alarm) => {
  if (!alarm) {
    chrome.alarms.create('keepAlive', { periodInMinutes: 0.4 });
  }
});

initDB().catch(console.error);
