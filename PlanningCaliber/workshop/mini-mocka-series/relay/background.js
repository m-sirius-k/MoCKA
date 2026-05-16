/**
 * Relay for Claude — background.js (standalone, no ES module imports)
 */

const INDEX_KEY = 'mocka_relay_sessions_index';
const NS = 'mocka_relay_';

// ── Session storage ────────────────────────────────────────────────────────

async function getIndex() {
  return new Promise(resolve => {
    chrome.storage.local.get(INDEX_KEY, r => resolve(r[INDEX_KEY] || []));
  });
}

async function saveSession(data) {
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  const session = {
    id, product: 'relay',
    title: data.title || 'Untitled',
    url: data.url || '',
    turns: data.messages?.length || 0,
    messages: data.messages || [],
    createdAt: now, updatedAt: now
  };
  await new Promise(resolve => {
    chrome.storage.local.set({ [NS + id]: session }, resolve);
  });
  const index = await getIndex();
  index.unshift({ id, title: session.title, turns: session.turns, createdAt: now });
  await new Promise(resolve => {
    chrome.storage.local.set({ [INDEX_KEY]: index }, resolve);
  });
  return id;
}

async function getStats() {
  const index = await getIndex();
  return {
    sessions: index.length,
    messages: index.reduce((s, e) => s + (e.turns || 0), 0)
  };
}

// ── Message handler ────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {

  if (msg.type === 'RELAY_SAVE_SESSION') {
    saveSession(msg.payload).then(id => sendResponse({ ok: true, id }));
    return true;
  }

  if (msg.type === 'RELAY_GET_STATS') {
    getStats().then(stats => sendResponse(stats));
    return true;
  }

  if (msg.type === 'RELAY_OPEN_NEW_CHAT') {
    const text = msg.payload.text;
    chrome.tabs.create({ url: 'https://claude.ai/new' }, (tab) => {
      const listener = (tabId, info) => {
        if (tabId !== tab.id || info.status !== 'complete') return;
        chrome.tabs.onUpdated.removeListener(listener);
        setTimeout(() => {
          chrome.tabs.sendMessage(tab.id, { type: 'RELAY_INJECT', payload: { text } });
        }, 2000);
      };
      chrome.tabs.onUpdated.addListener(listener);
    });
    sendResponse({ ok: true });
    return true;
  }
});
