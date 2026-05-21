// Relay background.js v3.0.0
// Role: storage read/write, message hub for content.js and popup.js

'use strict';

const STORAGE_KEY_TODOS = 'relay_todos';   // active TODOs
const STORAGE_KEY_LOG   = 'relay_log';     // completed LOG entries
const STORAGE_KEY_TURNS = 'relay_turns';   // current turn count

// -- helpers --
function getStorage(keys) {
  return new Promise(resolve => chrome.storage.local.get(keys, resolve));
}
function setStorage(obj) {
  return new Promise(resolve => chrome.storage.local.set(obj, resolve));
}
function genId() {
  return 'todo_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
}

// -- add todo --
async function addTodo(payload) {
  const { relay_todos: todos = [] } = await getStorage(STORAGE_KEY_TODOS);

  // skip duplicates
  const dup = todos.find(t => t.text.toLowerCase() === payload.text.toLowerCase());
  if (dup) return { ok: false, reason: 'duplicate' };

  const item = {
    id:         genId(),
    text:       payload.text,
    status:     'active',        // active | done
    source:     payload.source,  // assistant | user
    pattern:    payload.pattern,
    created_at: payload.created_at || new Date().toISOString(),
    url:        payload.url || ''
  };

  todos.push(item);
  await setStorage({ [STORAGE_KEY_TODOS]: todos });
  return { ok: true, id: item.id };
}

// -- complete todo -> move to log --
async function completeTodo(id) {
  const data  = await getStorage([STORAGE_KEY_TODOS, STORAGE_KEY_LOG]);
  const todos = data[STORAGE_KEY_TODOS] || [];
  const log   = data[STORAGE_KEY_LOG]   || [];

  const idx = todos.findIndex(t => t.id === id);
  if (idx === -1) return { ok: false, reason: 'not_found' };

  const item = todos.splice(idx, 1)[0];

  // log entry (5W1H format)
  const logEntry = {
    id:           item.id,
    text:         item.text,
    completed_at: new Date().toISOString(),
    created_at:   item.created_at,
    source:       item.source,
    url:          item.url,
    // 5W1H
    who:   item.source === 'assistant' ? 'Claude' : 'User',
    what:  item.text,
    when:  new Date().toISOString(),
    where: item.url,
    why:   '',   // future: infer from conversation context
    how:   'completed via Relay'
  };

  log.unshift(logEntry); // newest first

  await setStorage({
    [STORAGE_KEY_TODOS]: todos,
    [STORAGE_KEY_LOG]:   log
  });
  return { ok: true };
}

// -- delete todo without completing --
async function deleteTodo(id) {
  const { relay_todos: todos = [] } = await getStorage(STORAGE_KEY_TODOS);
  const filtered = todos.filter(t => t.id !== id);
  await setStorage({ [STORAGE_KEY_TODOS]: filtered });
  return { ok: true };
}

// -- get stats --
async function getStats() {
  const data  = await getStorage([STORAGE_KEY_TODOS, STORAGE_KEY_LOG, STORAGE_KEY_TURNS]);
  const todos = data[STORAGE_KEY_TODOS] || [];
  const log   = data[STORAGE_KEY_LOG]   || [];
  const turns = data[STORAGE_KEY_TURNS] || 0;
  return {
    turns,
    todo_count: todos.filter(t => t.status === 'active').length,
    log_count:  log.length
  };
}

// -- message handler --
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {

  if (msg.type === 'RELAY_TURN_UPDATE') {
    setStorage({ [STORAGE_KEY_TURNS]: msg.payload.count })
      .then(() => sendResponse({ ok: true }));
    return true;
  }

  if (msg.type === 'RELAY_ADD_TODO') {
    addTodo(msg.payload).then(sendResponse);
    return true;
  }

  if (msg.type === 'RELAY_COMPLETE_TODO') {
    completeTodo(msg.payload.id).then(sendResponse);
    return true;
  }

  if (msg.type === 'RELAY_DELETE_TODO') {
    deleteTodo(msg.payload.id).then(sendResponse);
    return true;
  }

  if (msg.type === 'RELAY_GET_STATS') {
    getStats().then(sendResponse);
    return true;
  }

  if (msg.type === 'RELAY_GET_TODOS') {
    getStorage(STORAGE_KEY_TODOS).then(data => {
      sendResponse({ todos: data[STORAGE_KEY_TODOS] || [] });
    });
    return true;
  }

  if (msg.type === 'RELAY_GET_LOG') {
    getStorage(STORAGE_KEY_LOG).then(data => {
      sendResponse({ log: data[STORAGE_KEY_LOG] || [] });
    });
    return true;
  }

  if (msg.type === 'RELAY_CLEAR_LOG') {
    setStorage({ [STORAGE_KEY_LOG]: [] }).then(() => sendResponse({ ok: true }));
    return true;
  }
});

console.log('[Relay] v3.0.0 background.js started');
