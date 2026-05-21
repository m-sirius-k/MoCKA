/**
 * Relay for Claude — background.js v2.0
 * PHI OS based. Central state manager.
 * UI: English only.
 */

// ── PHI OS Storage (inline for MV3 Service Worker) ────────────────────────

function phiGet(key) {
  return new Promise(resolve =>
    chrome.storage.local.get(key, d => resolve(d[key] ?? null)));
}
function phiSet(key, val) {
  return new Promise(resolve => chrome.storage.local.set({ [key]: val }, resolve));
}

// ── Session save ──────────────────────────────────────────────────────────

async function saveSession(data) {
  const INDEX = 'phi_sessions_index';
  const NS    = 'phi_session_';
  const MAX   = 50;

  const session = {
    ...data,
    id: data.id || data.sessionId || crypto.randomUUID(),
    product: data.product || 'relay',
    updated_at: new Date().toISOString(),
  };

  await phiSet(NS + session.id, session);

  let index = (await phiGet(INDEX)) || [];
  index = index.filter(e => e.id !== session.id);
  index.unshift({
    id: session.id, product: session.product,
    title: session.title, turns: session.turns,
    created_at: session.created_at, updated_at: session.updated_at,
  });
  if (index.length > MAX) {
    const removed = index.splice(MAX);
    removed.forEach(e => chrome.storage.local.remove(NS + e.id));
  }
  await phiSet(INDEX, index);
  return session.id;
}

// ── TODO save ─────────────────────────────────────────────────────────────

async function saveTodos(todos, sessionId) {
  const existing = (await phiGet('phi_todos')) || [];
  const existingSet = new Set(existing.map(t => t.content));
  const newItems = todos
    .filter(c => !existingSet.has(c))
    .map(content => ({
      id: 'TODO_' + Date.now() + '_' + Math.random().toString(36).slice(2, 5),
      content,
      status: 'open',
      priority: 'medium',
      session_id: sessionId || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }));
  if (newItems.length) {
    await phiSet('phi_todos', [...existing, ...newItems].slice(-200));
  }
}

// ── Stats ─────────────────────────────────────────────────────────────────

async function getStats() {
  const index = (await phiGet('phi_sessions_index')) || [];
  const todos = (await phiGet('phi_todos')) || [];
  return {
    sessions: index.length,
    messages: index.reduce((s, e) => s + (e.turns || 0), 0),
    todos: todos.filter(t => t.status !== 'done').length,
  };
}

// ── Export ────────────────────────────────────────────────────────────────

async function exportData(type) {
  const index = (await phiGet('phi_sessions_index')) || [];
  if (type === 'sessions') {
    const sessions = await Promise.all(
      index.map(e => phiGet('phi_session_' + e.id))
    );
    return JSON.stringify(sessions.filter(Boolean), null, 2);
  }
  if (type === 'todos') {
    const todos = (await phiGet('phi_todos')) || [];
    return JSON.stringify(todos, null, 2);
  }
  return '[]';
}

function download(content, filename) {
  const base64 = btoa(unescape(encodeURIComponent(content)));
  const url = `data:application/json;base64,${base64}`;
  const date = new Date().toISOString().slice(0, 10);
  chrome.downloads.download({
    url, filename: `relay-${filename}-${date}.json`, saveAs: false,
  });
}

// ── License ───────────────────────────────────────────────────────────────

function isPro(key) {
  return typeof key === 'string' && key.startsWith('RELAY-PRO-') && key.length >= 20;
}

// ── Message handler ───────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {

  if (msg.type === 'RELAY_AUTO_SAVE') {
    saveSession(msg.payload).then(id => sendResponse({ ok: true, id }));
    return true;
  }

  if (msg.type === 'RELAY_SAVE_TODOS') {
    saveTodos(msg.payload.todos, msg.payload.sessionId)
      .then(() => sendResponse({ ok: true }));
    return true;
  }

  if (msg.type === 'RELAY_GET_STATS') {
    getStats().then(stats => sendResponse(stats));
    return true;
  }

  if (msg.type === 'RELAY_GET_INDEX') {
    phiGet('phi_sessions_index').then(index => sendResponse({ index: index || [] }));
    return true;
  }

  if (msg.type === 'RELAY_GET_SESSION') {
    phiGet('phi_session_' + msg.id).then(session => sendResponse({ session }));
    return true;
  }

  if (msg.type === 'RELAY_OPEN_NEW_CHAT') {
    const text = msg.payload?.text;
    if (!text) { sendResponse({ ok: false }); return true; }
    chrome.tabs.create({ url: 'https://claude.ai/new' }, tab => {
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

  if (msg.type === 'RELAY_POPUP_HANDOFF') {
    chrome.tabs.query({ url: 'https://claude.ai/*' }, tabs => {
      if (!tabs.length) { sendResponse({ ok: false, error: 'no_tab' }); return; }
      chrome.tabs.sendMessage(tabs[0].id, { type: 'RELAY_MANUAL_HANDOFF' }, res => {
        sendResponse(chrome.runtime.lastError ? { ok: false } : { ok: true });
      });
    });
    return true;
  }

  if (msg.type === 'RELAY_EXPORT') {
    exportData(msg.dataType || 'sessions').then(json => {
      download(json, msg.dataType || 'sessions');
      sendResponse({ ok: true });
    });
    return true;
  }

  if (msg.type === 'RELAY_TODO_ARCHIVE') {
    phiGet('phi_todos').then(async todos => {
      const all = todos || [];
      const idx = all.findIndex(t => t.id === msg.id);
      if (idx !== -1) {
        const done = { ...all[idx], status: 'done', completed_at: new Date().toISOString() };
        all.splice(idx, 1);
        await phiSet('phi_todos', all);
        const log = (await phiGet('phi_log')) || [];
        log.unshift(done);
        await phiSet('phi_log', log.slice(0, 500));
      }
      sendResponse({ ok: true });
    });
    return true;
  }

  if (msg.type === 'RELAY_TODO_DELETE') {
    phiGet('phi_todos').then(async todos => {
      await phiSet('phi_todos', (todos || []).filter(t => t.id !== msg.id));
      sendResponse({ ok: true });
    });
    return true;
  }

  if (msg.type === 'RELAY_TODO_UPDATE') {
    phiGet('phi_todos').then(async todos => {
      const all = todos || [];
      const t = all.find(x => x.id === msg.id);
      if (t) { t.status = msg.status; t.updated_at = new Date().toISOString(); }
      await phiSet('phi_todos', all);
      sendResponse({ ok: true });
    });
    return true;
  }

  if (msg.type === 'RELAY_VERIFY_LICENSE') {
    sendResponse({ valid: isPro(msg.key), tier: isPro(msg.key) ? 'pro' : 'free' });
    return true;
  }
});