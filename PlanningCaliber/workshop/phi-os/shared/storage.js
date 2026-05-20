/**
 * PHI OS — storage.js
 * Unified chrome.storage.local API for all products.
 * All keys are prefixed with 'phi_' to avoid collisions.
 */

const PhiStorage = (() => {

  function get(key) {
    return new Promise((resolve) => {
      chrome.storage.local.get(key, (data) => resolve(data[key] ?? null));
    });
  }

  function set(key, value) {
    return new Promise((resolve) => {
      chrome.storage.local.set({ [key]: value }, resolve);
    });
  }

  function remove(key) {
    return new Promise((resolve) => {
      chrome.storage.local.remove(key, resolve);
    });
  }

  function getAll() {
    return new Promise((resolve) => {
      chrome.storage.local.get(null, resolve);
    });
  }

  // ── Sessions ──────────────────────────────────────────────────────────────

  async function saveSession(sessionData) {
    const INDEX = 'phi_sessions_index';
    const NS    = 'phi_session_';
    const MAX   = 50;

    const session = {
      ...sessionData,
      updated_at: new Date().toISOString(),
    };

    await set(NS + session.id, session);

    let index = (await get(INDEX)) || [];
    index = index.filter(e => e.id !== session.id);
    index.unshift({
      id:         session.id,
      product:    session.product,
      title:      session.title,
      turns:      session.turns,
      created_at: session.created_at,
      updated_at: session.updated_at,
    });

    if (index.length > MAX) {
      const removed = index.splice(MAX);
      removed.forEach(e => chrome.storage.local.remove(NS + e.id));
    }

    await set(INDEX, index);
    return session.id;
  }

  async function getSession(id) {
    return get('phi_session_' + id);
  }

  async function getSessionIndex(product) {
    const index = (await get('phi_sessions_index')) || [];
    return product ? index.filter(e => e.product === product) : index;
  }

  // ── TODOs ─────────────────────────────────────────────────────────────────

  async function getTodos() {
    return (await get('phi_todos')) || [];
  }

  async function saveTodo(todo) {
    const todos = await getTodos();
    const existing = todos.find(t => t.content === todo.content);
    if (existing) return; // deduplicate
    todos.push(todo);
    await set('phi_todos', todos.slice(-200));
  }

  async function updateTodoStatus(id, status) {
    const todos = await getTodos();
    const t = todos.find(x => x.id === id);
    if (t) {
      t.status = status;
      t.updated_at = new Date().toISOString();
      await set('phi_todos', todos);
    }
    return t;
  }

  async function deleteTodo(id) {
    const todos = await getTodos();
    await set('phi_todos', todos.filter(t => t.id !== id));
  }

  async function archiveTodo(id) {
    const todos = await getTodos();
    const idx = todos.findIndex(t => t.id === id);
    if (idx === -1) return;
    const done = { ...todos[idx], status: 'done', completed_at: new Date().toISOString() };
    todos.splice(idx, 1);
    await set('phi_todos', todos);
    const log = (await get('phi_log')) || [];
    log.unshift(done);
    await set('phi_log', log.slice(0, 500));
  }

  async function getLog() {
    return (await get('phi_log')) || [];
  }

  // ── Stats ─────────────────────────────────────────────────────────────────

  async function getStats(product) {
    const index = await getSessionIndex(product);
    const todos = await getTodos();
    return {
      sessions: index.length,
      messages: index.reduce((s, e) => s + (e.turns || 0), 0),
      todos:    todos.filter(t => t.status !== 'done').length,
    };
  }

  // ── Prefs ─────────────────────────────────────────────────────────────────

  async function getPrefs() {
    return (await get('phi_prefs')) || {};
  }

  async function setPrefs(prefs) {
    const current = await getPrefs();
    await set('phi_prefs', { ...current, ...prefs });
  }

  return {
    get, set, remove, getAll,
    saveSession, getSession, getSessionIndex,
    getTodos, saveTodo, updateTodoStatus, deleteTodo, archiveTodo, getLog,
    getStats,
    getPrefs, setPrefs,
  };
})();

if (typeof module !== 'undefined') module.exports = { PhiStorage };