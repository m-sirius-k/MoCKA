/**
 * Relay - popup.js v4.0
 * - popup → background直通信（content script依存排除）
 * - chrome.storage.local から直接TODO取得
 */

let isPro = false;
let currentSessionId = null;

async function init() {
  await checkLicense();
  loadStats();
  loadTurnLimit();
  loadExportFolder();
  bindTabs();
  bindButtons();
}

async function checkLicense() {
  return new Promise(resolve => {
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result.mocka_global_prefs || {};
      chrome.runtime.sendMessage({ type: 'RELAY_VERIFY_LICENSE', key: prefs.licenseKey || '' }, (res) => {
        isPro = res?.valid === true;
        updateTierUI();
        resolve();
      });
    });
  });
}

function updateTierUI() {
  const badge = document.getElementById('tier-badge');
  if (!badge) return;
  if (isPro) {
    badge.textContent = 'PRO ★';
    badge.className = 'tier-badge tier-pro';
  } else {
    badge.textContent = 'FREE';
    badge.className = 'tier-badge tier-free';
  }
}

// ── Stats: background直通信 ────────────────────────────────────────────────
function loadStats() {
  chrome.runtime.sendMessage({ type: 'RELAY_GET_STATS' }, (stats) => {
    if (!stats) return;
    document.getElementById('stat-sessions').textContent = stats.sessions || 0;
    document.getElementById('stat-messages').textContent = stats.messages || 0;
    document.getElementById('stat-todos').textContent    = stats.todos    || 0;
  });
}

function loadTurnLimit() {
  chrome.storage.sync.get('mocka_global_prefs', (result) => {
    const prefs = result.mocka_global_prefs || {};
    const el = document.getElementById('turn-limit');
    if (el) el.value = prefs.turnLimit || 20;
  });
  const el = document.getElementById('turn-limit');
  if (el) {
    el.addEventListener('change', (e) => {
      const val = parseInt(e.target.value, 10);
      chrome.storage.sync.get('mocka_global_prefs', (result) => {
        const prefs = result.mocka_global_prefs || {};
        chrome.storage.sync.set({ mocka_global_prefs: { ...prefs, turnLimit: val } });
      });
    });
  }
}

function loadExportFolder() {
  chrome.runtime.sendMessage({ type: 'RELAY_GET_EXPORT_FOLDER' }, (res) => {
    const folder = res?.folder || 'mocka-exports';
    const el = document.getElementById('export-folder');
    const pr = document.getElementById('folder-preview');
    if (el) el.value = folder;
    if (pr) pr.textContent = folder;
  });
}

// ── Tabs ──────────────────────────────────────────────────────────────────
function bindTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const name = tab.dataset.tab;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = document.getElementById('panel-' + name);
      if (panel) panel.classList.add('active');
      if (name === 'todos')    loadTodos();
      if (name === 'log')      loadLog();
      if (name === 'logbook')  loadLogbook();
      if (name === 'vault')    loadVault();
      if (name === 'settings') loadExportFolder();
    });
  });
}

// ── Buttons ───────────────────────────────────────────────────────────────
function bindButtons() {
  document.getElementById('btn-handoff')?.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'RELAY_POPUP_HANDOFF' }, (res) => {
      if (!res?.ok) {
        // background経由でcontent scriptに送信
        chrome.runtime.sendMessage({ type: 'RELAY_TAB_MESSAGE', payload: { type: 'RELAY_MANUAL_HANDOFF' } });
      }
      window.close();
    });
  });

  document.getElementById('btn-view-logbook')?.addEventListener('click', () => {
    document.querySelector('[data-tab="todos"]')?.click();
  });

  document.getElementById('detail-back')?.addEventListener('click', () => {
    document.getElementById('detail-view').style.display = 'none';
    document.getElementById('list-view').style.display  = 'block';
    currentSessionId = null;
  });

  document.getElementById('btn-save-vault')?.addEventListener('click', () => {
    if (!currentSessionId) return;
    chrome.runtime.sendMessage({ type: 'RELAY_GET_SESSION', id: currentSessionId }, (res) => {
      const s = res?.session;
      if (!s) return;
      chrome.runtime.sendMessage({
        type: 'RELAY_VAULT_ADD',
        payload: { label: s.title, text: buildVaultText(s), sessionId: s.id }
      }, (r) => {
        const btn = document.getElementById('btn-save-vault');
        if (r?.ok) {
          btn.textContent = '✓ Saved!';
          setTimeout(() => { btn.textContent = '★ Save to Vault (Pro)'; }, 2000);
        } else {
          alert('Vault requires Relay Pro.');
        }
      });
    });
  });

  document.getElementById('btn-add-vault')?.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'RELAY_TAB_MESSAGE', payload: { type: 'RELAY_GET_SUMMARY_FOR_VAULT' } }, (res) => {
      if (!res?.text) { alert('No active Claude chat found.'); return; }
      chrome.runtime.sendMessage({
        type: 'RELAY_VAULT_ADD',
        payload: { label: res.title || 'Current chat', text: res.text }
      }, () => loadVault());
    });
  });

  document.getElementById('btn-verify-license')?.addEventListener('click', activateLicense);

  document.getElementById('btn-save-folder')?.addEventListener('click', () => {
    const folder = document.getElementById('export-folder').value.trim() || 'mocka-exports';
    chrome.runtime.sendMessage({ type: 'RELAY_SET_EXPORT_FOLDER', folder }, () => {
      const pr = document.getElementById('folder-preview');
      if (pr) pr.textContent = folder;
      const saved = document.getElementById('folder-saved');
      if (saved) { saved.style.display = 'block'; setTimeout(() => { saved.style.display = 'none'; }, 2000); }
    });
  });

  document.getElementById('btn-export-sessions')?.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'RELAY_EXPORT_SESSIONS' }, (res) => {
      if (res?.ok) showExportStatus(`✓ Saved: ${res.filename}`);
    });
  });

  document.getElementById('btn-export-logbook')?.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'RELAY_EXPORT_LOGBOOK' }, (res) => {
      if (res?.ok) showExportStatus(`✓ Saved: ${res.filename}`);
    });
  });

  document.getElementById('btn-add-todo')?.addEventListener('click', () => {
    const input = document.getElementById('todo-input');
    const content = input?.value?.trim();
    if (!content) return;
    // chrome.storage.localに直接追加
    chrome.storage.local.get('relay_todos', (data) => {
      const todos = data.relay_todos || [];
      const nums = todos.map(t => parseInt((t.id || '').replace('LB_', ''), 10)).filter(n => !isNaN(n));
      const nextNum = nums.length ? Math.max(...nums) + 1 : 1;
      const id = 'LB_' + String(nextNum).padStart(3, '0');
      todos.push({
        id, content, status: '未着手', priority: '中',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
      chrome.storage.local.set({ relay_todos: todos }, () => {
        if (input) input.value = '';
        loadTodos();
        loadStats();
      });
    });
  });

  document.getElementById('todo-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('btn-add-todo')?.click();
  });

  document.getElementById('btn-clear-done')?.addEventListener('click', () => {
    chrome.storage.local.get(['relay_todos', 'mocka_relay_log'], (data) => {
      const todos = data.relay_todos || [];
      const log   = data.mocka_relay_log || [];
      const now   = new Date().toISOString();
      const done  = todos.filter(t => t.status === '完了').map(t => ({ ...t, completed_at: t.completed_at || now }));
      const active = todos.filter(t => t.status !== '完了');
      chrome.storage.local.set({ relay_todos: active, mocka_relay_log: done.concat(log) }, () => {
        loadTodos();
        loadStats();
      });
    });
  });

  document.getElementById('btn-clear-log')?.addEventListener('click', () => {
    if (!confirm('完了ログを全て削除しますか？')) return;
    chrome.storage.local.set({ mocka_relay_log: [] }, () => loadLog());
  });
}

// ── TODO タブ (chrome.storage.local直接参照) ──────────────────────────────
function loadTodos() {
  chrome.storage.local.get('relay_todos', (data) => {
    renderTodos(data.relay_todos || []);
  });
}

function renderTodos(todos) {
  const container = document.getElementById('todos-list');
  if (!container) return;
  const active = todos.filter(t => t.status !== '完了');
  if (!active.length) {
    container.innerHTML = '<div class="logbook-empty">アクティブなTODOはありません。</div>';
    return;
  }
  const groups = {
    '進行中': active.filter(t => t.status === '進行中'),
    '未着手': active.filter(t => t.status === '未着手'),
  };
  const statusColors = { '進行中': '#3b82f6', '未着手': '#94a3b8' };
  const statusIcons  = { '進行中': '🔵', '未着手': '⬜' };
  const priorityIcons = { '最高': '🔴', '高': '🟡', '中': '🟢', '低': '⚪' };
  const priorityOrder = { '最高': 0, '高': 1, '中': 2, '低': 3 };
  let html = '';
  Object.entries(groups).forEach(([status, items]) => {
    if (!items.length) return;
    const sorted = [...items].sort((a, b) => (priorityOrder[a.priority] ?? 2) - (priorityOrder[b.priority] ?? 2));
    html += `<div class="todo-group"><div class="todo-group-label">${statusIcons[status]} ${status} (${items.length})</div>`;
    sorted.forEach(t => {
      const pri = t.priority || '中';
      html += `<div class="todo-item" data-id="${t.id}">
        <div class="todo-item-header">
          <span class="todo-id" style="color:${statusColors[t.status]}">${t.id}</span>
          <span class="todo-priority">${priorityIcons[pri] || '⚪'} ${pri}</span>
          <div class="todo-actions">
            ${t.status !== '進行中' ? `<button class="todo-btn" data-id="${t.id}" data-action="進行中">▶</button>` : ''}
            <button class="todo-btn done-btn" data-id="${t.id}" data-action="完了">✓</button>
            <button class="todo-btn del-btn" data-id="${t.id}" data-action="delete">×</button>
          </div>
        </div>
        <div class="todo-content">${escHtml(t.content)}</div>
      </div>`;
    });
    html += '</div>';
  });
  container.innerHTML = html;
  container.querySelectorAll('.todo-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const { id, action } = btn.dataset;
      chrome.storage.local.get(['relay_todos', 'mocka_relay_log'], (data) => {
        let todos = data.relay_todos || [];
        if (action === 'delete') {
          todos = todos.filter(t => t.id !== id);
          chrome.storage.local.set({ relay_todos: todos }, () => loadTodos());
        } else if (action === '完了') {
          const idx = todos.findIndex(t => t.id === id);
          if (idx !== -1) {
            const done = { ...todos[idx], status: '完了', completed_at: new Date().toISOString() };
            todos.splice(idx, 1);
            const log = data.mocka_relay_log || [];
            log.unshift(done);
            chrome.storage.local.set({ relay_todos: todos, mocka_relay_log: log }, () => { loadTodos(); loadStats(); });
          }
        } else {
          const t = todos.find(x => x.id === id);
          if (t) { t.status = action; t.updatedAt = new Date().toISOString(); }
          chrome.storage.local.set({ relay_todos: todos }, () => loadTodos());
        }
      });
    });
  });
}

// ── LOG タブ ──────────────────────────────────────────────────────────────
function loadLog() {
  chrome.storage.local.get('mocka_relay_log', (data) => renderLog(data.mocka_relay_log || []));
}

function renderLog(log) {
  const container = document.getElementById('log-list');
  if (!container) return;
  const countEl = document.getElementById('log-count');
  if (countEl) countEl.textContent = log.length;
  if (!log.length) {
    container.innerHTML = '<div class="logbook-empty">完了したTODOがここに記録されます。</div>';
    return;
  }
  const priorityIcons = { '最高': '🔴', '高': '🟡', '中': '🟢', '低': '⚪' };
  const byDate = {};
  log.forEach(item => {
    const d = item.completed_at
      ? new Date(item.completed_at).toLocaleDateString('ja', { month: 'numeric', day: 'numeric', weekday: 'short' })
      : '不明';
    if (!byDate[d]) byDate[d] = [];
    byDate[d].push(item);
  });
  let html = '';
  Object.entries(byDate).forEach(([date, items]) => {
    html += `<div class="log-date-group"><div class="log-date-label">📅 ${date} (${items.length}件)</div>`;
    items.forEach(item => {
      const pri = item.priority || '中';
      const time = item.completed_at ? new Date(item.completed_at).toLocaleTimeString('ja', { hour: '2-digit', minute: '2-digit' }) : '';
      html += `<div class="log-item">
        <div class="log-item-header">
          <span class="log-id">${escHtml(item.id)}</span>
          <span class="log-priority">${priorityIcons[pri] || '⚪'} ${pri}</span>
          <span class="log-time">✅ ${time}</span>
        </div>
        <div class="log-content">${escHtml(item.content)}</div>
      </div>`;
    });
    html += '</div>';
  });
  container.innerHTML = html;
}

// ── Logbook ───────────────────────────────────────────────────────────────
function loadLogbook() {
  document.getElementById('detail-view').style.display = 'none';
  document.getElementById('list-view').style.display  = 'block';
  chrome.runtime.sendMessage({ type: 'RELAY_GET_INDEX' }, (res) => {
    const index = res?.index || [];
    const container = document.getElementById('logbook-list');
    if (!index.length) {
      container.innerHTML = '<div class="logbook-empty">No sessions yet.</div>';
      return;
    }
    container.innerHTML = index.map(s => {
      const lb = s.logbook || {};
      const date = new Date(s.createdAt).toLocaleDateString('ja', { month:'short', day:'numeric' });
      return `<div class="logbook-item" data-id="${s.id}">
        <div class="logbook-item-title">${escHtml(s.title)}</div>
        <div class="logbook-item-meta"><span class="logbook-chip">${s.turns}t · ${date}</span></div>
      </div>`;
    }).join('');
    container.querySelectorAll('.logbook-item').forEach(el => {
      el.addEventListener('click', () => showDetail(el.dataset.id));
    });
  });
}

function showDetail(id) {
  currentSessionId = id;
  chrome.runtime.sendMessage({ type: 'RELAY_GET_SESSION', id }, (res) => {
    const s = res?.session;
    if (!s) return;
    const lb = s.logbook || {};
    document.getElementById('detail-title').textContent = s.title;
    let html = '';
    if (lb.decisions?.length) html += `<div class="detail-section"><h4>✓ Decisions</h4>${lb.decisions.map(d => `<div class="detail-item">${escHtml(d)}</div>`).join('')}</div>`;
    if (lb.todos?.length)     html += `<div class="detail-section"><h4>→ Next steps</h4>${lb.todos.map(t => `<div class="detail-item">${escHtml(t)}</div>`).join('')}</div>`;
    if (lb.insights?.length)  html += `<div class="detail-section"><h4>★ Key insights</h4>${lb.insights.map(i => `<div class="detail-item">${escHtml(i)}</div>`).join('')}</div>`;
    if (!html) html = '<div class="logbook-empty">No structured data.</div>';
    document.getElementById('detail-content').innerHTML = html;
    const vaultBtn = document.getElementById('btn-save-vault');
    if (vaultBtn) vaultBtn.style.display = isPro ? 'flex' : 'none';
    document.getElementById('detail-view').style.display = 'block';
    document.getElementById('list-view').style.display   = 'none';
  });
}

// ── Vault ─────────────────────────────────────────────────────────────────
function loadVault() {
  const gate    = document.getElementById('vault-gate');
  const content = document.getElementById('vault-content');
  if (!isPro) { gate.style.display = 'block'; content.style.display = 'none'; return; }
  gate.style.display = 'none'; content.style.display = 'block';
  chrome.runtime.sendMessage({ type: 'RELAY_VAULT_LIST' }, (res) => {
    const vault = res?.vault || [];
    const list = document.getElementById('vault-list');
    if (!vault.length) { list.innerHTML = '<div class="logbook-empty">No saved contexts yet.</div>'; return; }
    list.innerHTML = vault.map(v => `
      <div class="vault-item ${v.active ? '' : 'inactive'}" data-id="${v.id}">
        <button class="vault-toggle ${v.active ? '' : 'off'}" data-id="${v.id}" data-active="${v.active}">${v.active ? '✓' : ''}</button>
        <span class="vault-label">${escHtml(v.label)}</span>
        <button class="vault-del" data-id="${v.id}">×</button>
      </div>`).join('');
    list.querySelectorAll('.vault-toggle').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        chrome.runtime.sendMessage({ type: 'RELAY_VAULT_TOGGLE', id: btn.dataset.id, active: btn.dataset.active !== 'true' }, () => loadVault());
      });
    });
    list.querySelectorAll('.vault-del').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm('Remove?')) chrome.runtime.sendMessage({ type: 'RELAY_VAULT_DELETE', id: btn.dataset.id }, () => loadVault());
      });
    });
  });
}

// ── License ───────────────────────────────────────────────────────────────
function activateLicense() {
  const key = document.getElementById('license-input').value.trim();
  const status = document.getElementById('license-status');
  chrome.runtime.sendMessage({ type: 'RELAY_VERIFY_LICENSE', key }, (res) => {
    if (res?.valid) {
      chrome.storage.sync.get('mocka_global_prefs', (result) => {
        const prefs = result.mocka_global_prefs || {};
        chrome.storage.sync.set({ mocka_global_prefs: { ...prefs, licenseKey: key, vaultEnabled: true } }, () => {
          status.textContent = '✓ Pro activated!';
          status.className = 'license-status license-ok';
          isPro = true;
          updateTierUI();
          setTimeout(() => loadVault(), 500);
        });
      });
    } else {
      status.textContent = '✗ Invalid license key';
      status.className = 'license-status license-err';
    }
  });
}

function showExportStatus(msg) {
  const el = document.getElementById('export-status');
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 3000);
}

function buildVaultText(session) {
  const lb = session.logbook || {};
  const parts = [];
  if (lb.decisions?.length) parts.push('Decisions:\n' + lb.decisions.map(d => `• ${d}`).join('\n'));
  if (lb.todos?.length)     parts.push('Next steps:\n' + lb.todos.map(t => `• ${t}`).join('\n'));
  if (lb.insights?.length)  parts.push('Key insights:\n' + lb.insights.map(i => `• ${i}`).join('\n'));
  return parts.join('\n\n') || '';
}

function escHtml(str) {
  return (str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.addEventListener('DOMContentLoaded', init);
