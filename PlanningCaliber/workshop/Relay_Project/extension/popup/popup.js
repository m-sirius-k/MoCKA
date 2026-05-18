/**
 * Relay - popup.js v3.0
 * Add: Logbook TODO tab — LB_NNN番号管理・status操作・手動追加
 */

let isPro = false;
let currentSessionId = null;

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  await checkLicense();
  loadStats();
  loadTurnLimit();
  loadExportFolder();
  bindTabs();
  bindButtons();
}

// ── License ───────────────────────────────────────────────────────────────────
async function checkLicense() {
  return new Promise(resolve => {
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result.mocka_global_prefs || {};
      const key = prefs.licenseKey || '';
      chrome.runtime.sendMessage({ type: 'RELAY_VERIFY_LICENSE', key }, (res) => {
        isPro = res?.valid === true;
        updateTierUI();
        resolve();
      });
    });
  });
}

function updateTierUI() {
  const badge = document.getElementById('tier-badge');
  if (isPro) {
    badge.textContent = 'PRO ★';
    badge.className = 'tier-badge tier-pro';
  } else {
    badge.textContent = 'FREE';
    badge.className = 'tier-badge tier-free';
  }
}

// ── Stats ─────────────────────────────────────────────────────────────────────
function loadStats() {
  chrome.runtime.sendMessage({ type: 'RELAY_GET_STATS' }, (stats) => {
    if (!stats) return;
    document.getElementById('stat-sessions').textContent = stats.sessions || 0;
    document.getElementById('stat-messages').textContent = stats.messages || 0;
    sendToActiveTab({ type: 'RELAY_LB_GET_TODOS' }, (res) => {
      const todos = res?.todos || [];
      const pending = todos.filter(t => t.status !== '完了').length;
      document.getElementById('stat-todos').textContent = pending;
    });
  });
}

// ── Turn limit ────────────────────────────────────────────────────────────────
function loadTurnLimit() {
  chrome.storage.sync.get('mocka_global_prefs', (result) => {
    const prefs = result.mocka_global_prefs || {};
    document.getElementById('turn-limit').value = prefs.turnLimit || 20;
  });
  document.getElementById('turn-limit').addEventListener('change', (e) => {
    const val = parseInt(e.target.value, 10);
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result.mocka_global_prefs || {};
      chrome.storage.sync.set({ mocka_global_prefs: { ...prefs, turnLimit: val } });
    });
  });
}

// ── Export folder ─────────────────────────────────────────────────────────────
function loadExportFolder() {
  chrome.runtime.sendMessage({ type: 'RELAY_GET_EXPORT_FOLDER' }, (res) => {
    const folder = res?.folder || 'mocka-exports';
    document.getElementById('export-folder').value = folder;
    document.getElementById('folder-preview').textContent = folder;
  });
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
function bindTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const name = tab.dataset.tab;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('panel-' + name).classList.add('active');

      if (name === 'todos')    loadTodos();
      if (name === 'logbook')  loadLogbook();
      if (name === 'vault')    loadVault();
      if (name === 'settings') loadExportFolder();
    });
  });
}

// ── Buttons ───────────────────────────────────────────────────────────────────
function bindButtons() {
  // Handoff
  document.getElementById('btn-handoff').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'RELAY_POPUP_HANDOFF' }, (res) => {
      if (chrome.runtime.lastError || !res?.ok) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (tabs[0]) chrome.tabs.sendMessage(tabs[0].id, { type: 'RELAY_MANUAL_HANDOFF' });
        });
      }
      window.close();
    });
  });

  // Open Todos tab
  document.getElementById('btn-view-logbook')?.addEventListener('click', () => {
    document.querySelector('[data-tab="todos"]')?.click();
  });

  // Detail back
  document.getElementById('detail-back').addEventListener('click', () => {
    document.getElementById('detail-view').style.display = 'none';
    document.getElementById('list-view').style.display  = 'block';
    currentSessionId = null;
  });

  // Save to Vault
  document.getElementById('btn-save-vault').addEventListener('click', () => {
    if (!currentSessionId) return;
    chrome.runtime.sendMessage({ type: 'RELAY_GET_SESSION', id: currentSessionId }, (res) => {
      const s = res?.session;
      if (!s) return;
      const text = buildVaultText(s);
      chrome.runtime.sendMessage({
        type: 'RELAY_VAULT_ADD',
        payload: { label: s.title, text, sessionId: s.id }
      }, (r) => {
        if (r?.ok) {
          document.getElementById('btn-save-vault').textContent = '✓ Saved to Vault!';
          setTimeout(() => {
            document.getElementById('btn-save-vault').textContent = '★ Save to Vault (Pro)';
          }, 2000);
        } else {
          alert('Vault requires Relay Pro. Activate your license in the Vault tab.');
        }
      });
    });
  });

  // Add current chat to Vault
  document.getElementById('btn-add-vault')?.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { type: 'RELAY_GET_SUMMARY_FOR_VAULT' }, (res) => {
        if (!res?.text) { alert('No active Claude chat found.'); return; }
        chrome.runtime.sendMessage({
          type: 'RELAY_VAULT_ADD',
          payload: { label: res.title || 'Current chat', text: res.text }
        }, () => loadVault());
      });
    });
  });

  // License activation
  document.getElementById('btn-verify-license')?.addEventListener('click', activateLicense);

  // Save export folder
  document.getElementById('btn-save-folder').addEventListener('click', () => {
    const folder = document.getElementById('export-folder').value.trim() || 'mocka-exports';
    chrome.runtime.sendMessage({ type: 'RELAY_SET_EXPORT_FOLDER', folder }, () => {
      document.getElementById('folder-preview').textContent = folder;
      const saved = document.getElementById('folder-saved');
      saved.style.display = 'block';
      setTimeout(() => { saved.style.display = 'none'; }, 2000);
    });
  });

  // Export sessions
  document.getElementById('btn-export-sessions').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'RELAY_EXPORT_SESSIONS' }, (res) => {
      if (res?.ok) showExportStatus(`✓ Saved: ${res.filename}`);
    });
  });

  // Export logbook
  document.getElementById('btn-export-logbook').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'RELAY_EXPORT_LOGBOOK' }, (res) => {
      if (res?.ok) showExportStatus(`✓ Saved: ${res.filename}`);
    });
  });

  // TODO手動追加
  document.getElementById('btn-add-todo')?.addEventListener('click', () => {
    const input = document.getElementById('todo-input');
    const content = input?.value?.trim();
    if (!content) return;
    sendToActiveTab({ type: 'RELAY_LB_ADD_TODO', content }, () => {
      input.value = '';
      loadTodos();
    });
  });

  // 入力欄でEnterキー
  document.getElementById('todo-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('btn-add-todo')?.click();
  });

  // 完了済みTODOを全削除
  document.getElementById('btn-clear-done')?.addEventListener('click', () => {
    sendToActiveTab({ type: 'RELAY_LB_CLEAR_DONE' }, () => loadTodos());
  });
}

// ── TODO タブ ─────────────────────────────────────────────────────────────────
function loadTodos() {
  sendToActiveTab({ type: 'RELAY_LB_GET_TODOS' }, (res) => {
    const todos = res?.todos || [];
    renderTodos(todos);
  });
}

function renderTodos(todos) {
  const container = document.getElementById('todos-list');
  if (!container) return;

  if (!todos.length) {
    container.innerHTML = `
      <div class="logbook-empty">
        TODOはまだありません。<br>
        会話中に「〜してください」「TODO:〜」と言うと<br>自動で記録されます。
      </div>`;
    return;
  }

  // ステータス別にグループ化
  const groups = {
    '進行中': todos.filter(t => t.status === '進行中'),
    '未着手': todos.filter(t => t.status === '未着手'),
    '完了':   todos.filter(t => t.status === '完了'),
  };

  const statusColors = {
    '進行中': '#3b82f6',
    '未着手': '#94a3b8',
    '完了':   '#22c55e',
  };
  const statusIcons = { '進行中': '🔵', '未着手': '⬜', '完了': '✅' };

  let html = '';
  Object.entries(groups).forEach(([status, items]) => {
    if (!items.length) return;
    html += `<div class="todo-group">
      <div class="todo-group-label">${statusIcons[status]} ${status} (${items.length})</div>`;
    items.forEach(t => {
      html += `
        <div class="todo-item ${t.status === '完了' ? 'done' : ''}" data-id="${t.id}">
          <div class="todo-item-header">
            <span class="todo-id" style="color:${statusColors[t.status]}">${t.id}</span>
            <div class="todo-actions">
              ${t.status !== '進行中' ? `<button class="todo-btn" data-id="${t.id}" data-action="進行中" title="進行中に">▶</button>` : ''}
              ${t.status !== '完了'   ? `<button class="todo-btn done-btn" data-id="${t.id}" data-action="完了" title="完了にする">✓</button>` : ''}
              ${t.status !== '未着手' ? `<button class="todo-btn" data-id="${t.id}" data-action="未着手" title="未着手に戻す">↩</button>` : ''}
              <button class="todo-btn del-btn" data-id="${t.id}" data-action="delete" title="削除">×</button>
            </div>
          </div>
          <div class="todo-content">${escHtml(t.content)}</div>
        </div>`;
    });
    html += '</div>';
  });

  container.innerHTML = html;

  // イベント登録
  container.querySelectorAll('.todo-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = btn.dataset.id;
      const action = btn.dataset.action;
      if (action === 'delete') {
        sendToActiveTab({ type: 'RELAY_LB_DELETE_TODO', id }, () => loadTodos());
      } else {
        sendToActiveTab({ type: 'RELAY_LB_UPDATE_STATUS', id, status: action }, () => loadTodos());
      }
    });
  });
}

// ── アクティブタブへメッセージ送信ヘルパー ────────────────────────────────────
function sendToActiveTab(msg, callback) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs.find(t => t.url && t.url.includes('claude.ai'));
    if (!tab) {
      if (callback) callback(null);
      return;
    }
    chrome.tabs.sendMessage(tab.id, msg, (res) => {
      if (chrome.runtime.lastError) {
        console.warn('Relay: tab msg error', chrome.runtime.lastError.message);
        if (callback) callback(null);
      } else {
        if (callback) callback(res);
      }
    });
  });
}

function showExportStatus(msg) {
  const el = document.getElementById('export-status');
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
  return parts.join('\n\n') || session.messages?.slice(-2).map(m => m.text).join('\n') || '';
}

// ── Logbook（セッション履歴）タブ ────────────────────────────────────────────
function loadLogbook() {
  document.getElementById('detail-view').style.display = 'none';
  document.getElementById('list-view').style.display  = 'block';

  chrome.runtime.sendMessage({ type: 'RELAY_GET_INDEX' }, (res) => {
    const index = res?.index || [];
    const container = document.getElementById('logbook-list');

    if (!index.length) {
      container.innerHTML = '<div class="logbook-empty">No sessions yet.<br>Start a relay to build your Logbook.</div>';
      return;
    }

    container.innerHTML = index.map(s => {
      const lb = s.logbook || {};
      const chips = [
        lb.decisions ? `<span class="logbook-chip decision">✓ ${lb.decisions}</span>` : '',
        lb.todos     ? `<span class="logbook-chip todo">→ ${lb.todos}</span>` : '',
        lb.insights  ? `<span class="logbook-chip insight">★ ${lb.insights}</span>` : ''
      ].filter(Boolean).join('');
      const date = new Date(s.createdAt).toLocaleDateString('ja', { month:'short', day:'numeric' });
      return `
        <div class="logbook-item" data-id="${s.id}">
          <div class="logbook-item-title">${escHtml(s.title)}</div>
          <div class="logbook-item-meta">
            <span class="logbook-chip">${s.turns}t · ${date}</span>
            ${chips}
          </div>
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
    if (lb.decisions?.length) {
      html += `<div class="detail-section"><h4>✓ Decisions</h4>
        ${lb.decisions.map(d => `<div class="detail-item">${escHtml(d)}</div>`).join('')}</div>`;
    }
    if (lb.todos?.length) {
      html += `<div class="detail-section"><h4>→ Next steps</h4>
        ${lb.todos.map(t => `<div class="detail-item">${escHtml(t)}</div>`).join('')}</div>`;
    }
    if (lb.insights?.length) {
      html += `<div class="detail-section"><h4>★ Key insights</h4>
        ${lb.insights.map(i => `<div class="detail-item">${escHtml(i)}</div>`).join('')}</div>`;
    }
    if (!html) {
      html = '<div class="logbook-empty" style="text-align:left;color:#4a6080;font-size:12px">No structured data extracted from this session.</div>';
    }

    document.getElementById('detail-content').innerHTML = html;
    const vaultBtn = document.getElementById('btn-save-vault');
    vaultBtn.style.display = isPro ? 'flex' : 'none';
    document.getElementById('detail-view').style.display = 'block';
    document.getElementById('list-view').style.display   = 'none';
  });
}

// ── Vault ─────────────────────────────────────────────────────────────────────
function loadVault() {
  const gate    = document.getElementById('vault-gate');
  const content = document.getElementById('vault-content');

  if (!isPro) {
    gate.style.display    = 'block';
    content.style.display = 'none';
    return;
  }

  gate.style.display    = 'none';
  content.style.display = 'block';

  chrome.runtime.sendMessage({ type: 'RELAY_VAULT_LIST' }, (res) => {
    const vault = res?.vault || [];
    const list = document.getElementById('vault-list');

    if (!vault.length) {
      list.innerHTML = '<div class="logbook-empty">No saved contexts yet.</div>';
      return;
    }

    list.innerHTML = vault.map(v => `
      <div class="vault-item ${v.active ? '' : 'inactive'}" data-id="${v.id}">
        <button class="vault-toggle ${v.active ? '' : 'off'}" data-id="${v.id}" data-active="${v.active}">
          ${v.active ? '✓' : ''}
        </button>
        <span class="vault-label">${escHtml(v.label)}</span>
        <button class="vault-del" data-id="${v.id}">×</button>
      </div>`).join('');

    list.querySelectorAll('.vault-toggle').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const active = btn.dataset.active === 'true';
        chrome.runtime.sendMessage({ type: 'RELAY_VAULT_TOGGLE', id: btn.dataset.id, active: !active }, () => loadVault());
      });
    });
    list.querySelectorAll('.vault-del').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm('Remove this Vault entry?')) {
          chrome.runtime.sendMessage({ type: 'RELAY_VAULT_DELETE', id: btn.dataset.id }, () => loadVault());
        }
      });
    });
  });
}

// ── License activation ────────────────────────────────────────────────────────
function activateLicense() {
  const key = document.getElementById('license-input').value.trim();
  const status = document.getElementById('license-status');
  chrome.runtime.sendMessage({ type: 'RELAY_VERIFY_LICENSE', key }, (res) => {
    if (res?.valid) {
      chrome.storage.sync.get('mocka_global_prefs', (result) => {
        const prefs = result.mocka_global_prefs || {};
        chrome.storage.sync.set({ mocka_global_prefs: { ...prefs, licenseKey: key, vaultEnabled: true } }, () => {
          status.textContent = '✓ Pro activated!';
          status.className   = 'license-status license-ok';
          isPro = true;
          updateTierUI();
          setTimeout(() => loadVault(), 500);
        });
      });
    } else {
      status.textContent = '✗ Invalid license key';
      status.className   = 'license-status license-err';
    }
  });
}

// ── Utils ─────────────────────────────────────────────────────────────────────
function escHtml(str) {
  return (str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

document.addEventListener('DOMContentLoaded', init);
