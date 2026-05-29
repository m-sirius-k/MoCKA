// sidepanel.js — PHI OS サイドパネル UI
'use strict';

import { detectMode }    from '../core/state-store.js';
import { CommitEngine }  from '../core/commit-engine.js';
import { RestoreEngine } from '../core/restore-engine.js';
import { togglePanelMode } from './panel-switch.js';
import { initI18n, setLang, getLang } from '../core/i18n.js';

async function init() {
  await initI18n();
  await refreshMode();
  await refreshTodos();
  bindEvents();
  // 言語セレクターの初期値
  const sel = document.getElementById('lang-select');
  if (sel) sel.value = getLang();
  // 30秒ごとにモードを再確認
  setInterval(refreshMode, 30000);
}

async function refreshMode() {
  const mode  = await detectMode();
  const badge = document.getElementById('mode-badge');
  if (!badge) return;
  badge.textContent = mode;
  badge.className   = `mode-badge${mode === 'CONNECTED' ? ' connected' : ''}`;
}

async function refreshTodos() {
  const stored = await chrome.storage.local.get('relay_todos');
  const todos  = (stored['relay_todos'] || []).filter(t => t.status === 'active');
  const list   = document.getElementById('todo-list');
  if (!list) return;

  if (!todos.length) {
    list.innerHTML = '<div style="color:var(--text3);font-size:11px">TODOなし</div>';
    return;
  }

  list.innerHTML = todos.map(t => `
    <div class="todo-item" data-id="${t.id}">
      <span class="check" data-id="${t.id}">○</span>
      <span class="todo-text">${escHtml(t.text)}</span>
    </div>
  `).join('');

  list.querySelectorAll('.check').forEach(el => {
    el.addEventListener('click', async () => {
      await chrome.runtime.sendMessage({ type: 'RELAY_COMPLETE_TODO', id: el.dataset.id }).catch(() => {});
      await refreshTodos();
    });
  });
}

function bindEvents() {
  // パネル切り換え（サイド→ポップアップ）
  document.getElementById('btn-panel')?.addEventListener('click', async () => {
    await togglePanelMode();
    setStatus('ポップアップモードに切り換えました');
  });

  // 言語切り換え
  document.getElementById('lang-select')?.addEventListener('change', async (e) => {
    await setLang(e.target.value);
  });

  document.getElementById('btn-commit')?.addEventListener('click', async () => {
    setStatus('保存中...');
    try {
      const engine = new CommitEngine();
      const result = await engine.commit({ trigger: 'MANUAL' });
      setStatus(result ? '✓ 保存完了' : 'コンテンツなし');
    } catch {
      setStatus('✗ エラー');
    }
  });

  document.getElementById('btn-restore')?.addEventListener('click', async () => {
    const engine = new RestoreEngine();
    const packet = await engine.buildPacket();
    if (!packet) { setStatus('復元データなし'); return; }
    await navigator.clipboard.writeText(packet);
    setStatus('✓ クリップボードにコピーしました');
  });
}

function setStatus(msg) {
  const el = document.getElementById('status-msg');
  if (el) el.textContent = msg;
  setTimeout(() => { if (el) el.textContent = ''; }, 2500);
}

function escHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

init();
