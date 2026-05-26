// popup.js
import { getLang } from './shared/i18n.js';
import { FILE_STATUS, ERROR_SEVERITY } from './shared/constants.js';

const t = getLang();

// ============================================================
// 初期化
// ============================================================
document.addEventListener('DOMContentLoaded', async () => {
  applyI18n();
  setupTabs();
  await renderAll();
  setupButtons();
});

function applyI18n() {
  document.getElementById('title-text').textContent      = t.title;
  document.getElementById('subtitle-text').textContent   = t.subtitle;
  document.getElementById('label-files').textContent     = t.files;
  document.getElementById('label-errors').textContent    = t.errors;
  document.getElementById('label-todos').textContent     = t.todos;
  document.getElementById('label-decisions').textContent = t.decisions;
  document.getElementById('label-environment').textContent = t.environment;
  document.getElementById('label-no-files').textContent  = t.no_files;
  document.getElementById('label-no-errors').textContent = t.no_errors;
  document.getElementById('btn-copy').textContent        = t.copy_inject;
  document.getElementById('btn-clear').textContent       = t.clear;
  document.getElementById('tab-files').textContent       = '📁 ' + t.files;
  document.getElementById('tab-errors').textContent      = '🔴 ' + t.errors;
  document.getElementById('tab-env').textContent         = '⚙️ ' + t.environment;
}

// ============================================================
// タブ制御
// ============================================================
function setupTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
    });
  });
}

// ============================================================
// データ取得・描画
// ============================================================
async function renderAll() {
  const resp = await chrome.runtime.sendMessage({ type: 'MEMORY_GET_REGISTRY' });
  const registry = resp.registry;
  if (!registry) return;

  document.getElementById('plan-badge').textContent = (registry.plan || 'free').toUpperCase();

  renderFiles(registry);
  renderErrors(registry);
  renderEnvironment(registry);
  renderTodos(registry);
  renderWorkspaceInfo(registry);
}

function renderFiles(registry) {
  const list  = document.getElementById('files-list');
  const count = document.getElementById('files-count');
  const files = registry.files || [];

  count.textContent = files.length + ' files';

  if (files.length === 0) {
    list.innerHTML = `<div class="empty"><div class="empty-icon">📁</div><span>${t.no_files}</span></div>`;
    return;
  }

  list.innerHTML = files.slice(-10).reverse().map(f => `
    <div class="file-item">
      <div class="file-status status-${f.status || 'unknown'}"></div>
      <div class="file-info">
        <div class="file-name">${escHtml(f.filename)}</div>
        <div class="file-path">${escHtml(f.path)}</div>
        ${f.summary ? `<div class="file-summary">${escHtml(f.summary)}</div>` : ''}
      </div>
    </div>
  `).join('');
}

function renderErrors(registry) {
  const list   = document.getElementById('errors-list');
  const count  = document.getElementById('errors-count');
  const errors = registry.known_errors || [];

  count.textContent = errors.length;

  if (errors.length === 0) {
    list.innerHTML = `<div class="empty"><div class="empty-icon">✅</div><span>${t.no_errors}</span></div>`;
    return;
  }

  list.innerHTML = errors.map(e => `
    <div class="error-item">
      <div class="error-header">
        <span class="severity-badge severity-${e.severity}">${e.severity.toUpperCase()}</span>
        <span class="error-pattern">${escHtml(e.error_pattern)}</span>
        <span class="error-count">${e.occurrence_count}回</span>
      </div>
      ${e.solution ? `<div class="error-solution">${escHtml(e.solution)}</div>` : ''}
    </div>
  `).join('');

  const decCard = document.getElementById('decisions-card');
  if (registry.plan === 'free') {
    decCard.classList.add('locked');
  } else {
    const decList = document.getElementById('decisions-list');
    const decs = registry.decisions || [];
    decList.innerHTML = decs.slice(-5).reverse().map(d => `
      <div class="env-item">
        <span class="env-bullet">✓</span>
        <span>${escHtml(d.decided_at)} ${escHtml(d.content)}</span>
      </div>
    `).join('') || `<div class="empty"><span>—</span></div>`;
  }
}

function renderEnvironment(registry) {
  const list = document.getElementById('env-list');
  const envs = registry.environment || [];

  if (envs.length === 0) {
    list.innerHTML = `<div class="empty"><span>—</span></div>`;
    return;
  }

  list.innerHTML = envs.map(e => `
    <div class="env-item">
      <span class="env-bullet">•</span>
      <span>${escHtml(e)}</span>
    </div>
  `).join('');
}

function renderTodos(registry) {
  const list  = document.getElementById('todos-list');
  const todos = registry.pending_todos || [];

  if (todos.length === 0) {
    list.innerHTML = `<div class="empty"><span>—</span></div>`;
    return;
  }

  list.innerHTML = todos.slice(0, 5).map(td => `
    <div class="todo-item">
      <span class="env-bullet">[ ]</span>
      <span>${escHtml(td.id)}: ${escHtml(td.title)}</span>
    </div>
  `).join('');
}

function renderWorkspaceInfo(registry) {
  const el = document.getElementById('workspace-info');
  el.innerHTML = `
    Workspace: <b>${escHtml(registry.workspace_id || 'default')}</b><br>
    Updated: ${escHtml(registry.updated_at ? registry.updated_at.substring(0, 16) : '—')}<br>
    Files: ${(registry.files || []).length} / Errors: ${(registry.known_errors || []).length}
  `;
}

// ============================================================
// ボタン
// ============================================================
function setupButtons() {
  document.getElementById('btn-copy').addEventListener('click', async () => {
    const resp = await chrome.runtime.sendMessage({ type: 'MEMORY_GET_INJECT_BLOCK' });
    await navigator.clipboard.writeText(resp.block);
    showToast(t.copy_success);
  });

  document.getElementById('btn-clear').addEventListener('click', async () => {
    await chrome.runtime.sendMessage({ type: 'MEMORY_CLEAR_SESSION' });
    await renderAll();
    showToast('Cleared');
  });

  document.getElementById('license-apply').addEventListener('click', async () => {
    const key = document.getElementById('license-input').value.trim();
    if (!key) return;
    // TODO: HMACライセンス検証（OrchestrapipelineのvalidateLicense流用）
    showToast('License applied');
  });
}

// ============================================================
// トースト
// ============================================================
function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2000);
}

// ============================================================
// ユーティリティ
// ============================================================
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
