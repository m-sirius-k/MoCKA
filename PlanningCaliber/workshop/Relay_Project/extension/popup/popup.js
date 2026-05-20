/**
 * Relay for Claude — popup.js v2.0
 * PHI OS based. Background-only communication.
 * UI: English only.
 */

function send(type, payload) {
  return new Promise(resolve =>
    chrome.runtime.sendMessage({ type, payload }, r => resolve(r))
  );
}

// ── Init ──────────────────────────────────────────────────────────────────

async function init() {
  await checkLicense();
  loadStats();
  loadTurnLimit();
  bindTabs();
  bindButtons();
}

// ── License ───────────────────────────────────────────────────────────────

let isPro = false;

async function checkLicense() {
  const prefs = await getPrefs();
  const res = await send('RELAY_VERIFY_LICENSE', { key: prefs.licenseKey || '' });
  isPro = res?.valid === true;
  const badge = document.getElementById('tier-badge');
  if (badge) {
    badge.textContent = isPro ? 'PRO ★' : 'FREE';
    badge.className = 'tier-badge ' + (isPro ? 'tier-pro' : 'tier-free');
  }
}

async function getPrefs() {
  return new Promise(resolve =>
    chrome.storage.local.get('phi_prefs', d => resolve(d.phi_prefs || {}))
  );
}

// ── Stats ─────────────────────────────────────────────────────────────────

function loadStats() {
  send('RELAY_GET_STATS').then(stats => {
    if (!stats) return;
    document.getElementById('stat-sessions').textContent = stats.sessions || 0;
    document.getElementById('stat-messages').textContent = stats.messages || 0;
    document.getElementById('stat-todos').textContent    = stats.todos    || 0;
  });
}

// ── Turn limit ────────────────────────────────────────────────────────────

function loadTurnLimit() {
  getPrefs().then(prefs => {
    const el = document.getElementById('turn-limit');
    if (el) el.value = prefs.turnLimit || 20;
  });
  document.getElementById('turn-limit')?.addEventListener('change', e => {
    getPrefs().then(prefs =>
      chrome.storage.local.set({ phi_prefs: { ...prefs, turnLimit: +e.target.value } })
    );
  });
}

// ── Tabs ──────────────────────────────────────────────────────────────────

function bindTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = document.getElementById('panel-' + tab.dataset.tab);
      if (panel) panel.classList.add('active');
      const name = tab.dataset.tab;
      if (name === 'todos')    loadTodos();
      if (name === 'log')      loadLog();
      if (name === 'logbook')  loadLogbook();
    });
  });
}

// ── Buttons ───────────────────────────────────────────────────────────────

function bindButtons() {
  document.getElementById('btn-handoff')?.addEventListener('click', () => {
    send('RELAY_POPUP_HANDOFF').then(() => window.close());
  });

  document.getElementById('btn-view-todos')?.addEventListener('click', () => {
    document.querySelector('[data-tab="todos"]')?.click();
  });

  document.getElementById('btn-add-todo')?.addEventListener('click', addTodo);
  document.getElementById('todo-input')?.addEventListener('keydown', e => {
    if (e.key === 'Enter') addTodo();
  });

  document.getElementById('btn-verify-license')?.addEventListener('click', () => {
    const key = document.getElementById('license-input').value.trim();
    send('RELAY_VERIFY_LICENSE', { key }).then(res => {
      const status = document.getElementById('license-status');
      if (res?.valid) {
        getPrefs().then(prefs =>
          chrome.storage.local.set({ phi_prefs: { ...prefs, licenseKey: key } })
        );
        status.textContent = '✓ Pro activated!';
        status.className = 'license-status license-ok';
        isPro = true;
        document.getElementById('tier-badge').textContent = 'PRO ★';
        document.getElementById('tier-badge').className = 'tier-badge tier-pro';
      } else {
        status.textContent = '✗ Invalid license key';
        status.className = 'license-status license-err';
      }
    });
  });

  document.getElementById('btn-export-sessions')?.addEventListener('click', () => {
    send('RELAY_EXPORT', { dataType: 'sessions' });
  });

  document.getElementById('btn-export-todos')?.addEventListener('click', () => {
    send('RELAY_EXPORT', { dataType: 'todos' });
  });
}

// ── TODOs ─────────────────────────────────────────────────────────────────

function addTodo() {
  const input = document.getElementById('todo-input');
  const content = input?.value?.trim();
  if (!content) return;
  chrome.storage.local.get('phi_todos', data => {
    const todos = data.phi_todos || [];
    todos.push({
      id: 'TODO_' + Date.now() + '_' + Math.random().toString(36).slice(2, 5),
      content, status: 'open', priority: 'medium',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
    chrome.storage.local.set({ phi_todos: todos }, () => {
      input.value = '';
      loadTodos();
      loadStats();
    });
  });
}

function loadTodos() {
  chrome.storage.local.get('phi_todos', data => {
    const todos = (data.phi_todos || []).filter(t => t.status !== 'done');
    const container = document.getElementById('todo-list');
    if (!todos.length) {
      container.innerHTML = '<div class="empty">No open TODOs.</div>';
      return;
    }
    container.innerHTML = todos.map(t => `
      <div class="todo-item" data-id="${t.id}">
        <div class="todo-content">${escHtml(t.content)}</div>
        <div class="todo-actions">
          <button class="todo-btn" data-action="done" data-id="${t.id}">✓ Done</button>
          <button class="todo-btn" data-action="delete" data-id="${t.id}">✕ Delete</button>
        </div>
      </div>`).join('');
    container.querySelectorAll('.todo-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        const { action, id } = btn.dataset;
        if (action === 'done') {
          send('RELAY_TODO_ARCHIVE', { id }).then(() => { loadTodos(); loadStats(); });
        } else if (action === 'delete') {
          send('RELAY_TODO_DELETE', { id }).then(() => { loadTodos(); loadStats(); });
        }
      });
    });
  });
}

// ── Log ───────────────────────────────────────────────────────────────────

function loadLog() {
  chrome.storage.local.get('phi_log', data => {
    const log = data.phi_log || [];
    document.getElementById('log-count').textContent = log.length;
    const container = document.getElementById('log-list');
    if (!log.length) {
      container.innerHTML = '<div class="empty">No completed TODOs.</div>';
      return;
    }
    container.innerHTML = log.slice(0, 50).map(t => `
      <div class="log-item">
        <div>${escHtml(t.content)}</div>
        <div class="log-done">✓ ${t.completed_at ? new Date(t.completed_at).toLocaleString() : ''}</div>
      </div>`).join('');
  });
}

// ── Logbook ───────────────────────────────────────────────────────────────

function loadLogbook() {
  send('RELAY_GET_INDEX').then(res => {
    const index = res?.index || [];
    const container = document.getElementById('logbook-list');
    if (!index.length) {
      container.innerHTML = '<div class="empty">No sessions yet.</div>';
      return;
    }
    container.innerHTML = index.slice(0, 30).map(s => `
      <div class="session-item">
        <div class="session-title">${escHtml(s.title || 'Untitled')}</div>
        <div class="session-meta">${s.turns || 0} turns · ${s.updated_at ? new Date(s.updated_at).toLocaleDateString() : ''}</div>
      </div>`).join('');
  });
}

// ── Utils ─────────────────────────────────────────────────────────────────

function escHtml(str) {
  return (str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.addEventListener('DOMContentLoaded', init);