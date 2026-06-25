// popup.js — MoCKA Relay v2.0
'use strict';

const STORAGE = {
  TODOS:           'relay_todos',
  LOGBOOK_CURRENT: 'relay_logbook_current',
};

// ─── DOM参照 ──────────────────────────────────────────────────────────────────

const $ = id => document.getElementById(id);
const turnValueEl   = $('turn-value');
const todoBadgeEl   = $('todo-badge');
const todoListEl    = $('todo-list');
const planSelectEl  = $('plan-select');
const btnHandoff    = $('btn-handoff');
const feedbackEl    = $('feedback');
const packetPreview = $('packet-preview');
const btnCopy       = $('btn-copy');
const btnExtract    = $('btn-extract');
const btnClearDone  = $('btn-clear-done');

// ─── ターン数表示 ──────────────────────────────────────────────────────────────

async function refreshTurnCount() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id || !tab.url?.includes('claude.ai')) {
      turnValueEl.textContent = '—';
      return;
    }
    const resp = await chrome.tabs.sendMessage(tab.id, { type: 'GET_TURN_COUNT' });
    const n = resp?.count ?? 0;
    turnValueEl.textContent = n;
    turnValueEl.className = 'turn-value ' + (n >= 20 ? 'warn' : 'ok');
  } catch {
    turnValueEl.textContent = '—';
  }
}

// ─── TODO表示 ─────────────────────────────────────────────────────────────────

function renderTodos(todos) {
  const active = todos.filter(t => !t.done);
  todoBadgeEl.textContent = active.length;

  if (todos.length === 0) {
    todoListEl.innerHTML = '<div class="todo-empty">タスクはまだありません</div>';
    return;
  }

  todoListEl.innerHTML = '';
  todos.forEach(todo => {
    const item = document.createElement('div');
    item.className = 'todo-item';
    // ホバー tooltip 用にfull textをdata属性に
    item.setAttribute('data-full', todo.text);

    const check = document.createElement('div');
    check.className = 'todo-check' + (todo.done ? ' done' : '');
    check.title = todo.done ? '未完了に戻す' : '完了にする';
    check.addEventListener('click', () => toggleTodo(todo.id));

    const text = document.createElement('div');
    text.className = 'todo-text' + (todo.done ? ' done' : '');
    text.textContent = todo.text;

    const del = document.createElement('div');
    del.className = 'todo-del';
    del.textContent = '✕';
    del.title = '削除';
    del.addEventListener('click', () => deleteTodo(todo.id));

    item.appendChild(check);
    item.appendChild(text);
    item.appendChild(del);
    todoListEl.appendChild(item);
  });
}

function loadTodos() {
  chrome.storage.local.get(STORAGE.TODOS, result => {
    renderTodos(result[STORAGE.TODOS] || []);
  });
}

function toggleTodo(id) {
  chrome.storage.local.get(STORAGE.TODOS, result => {
    const todos = (result[STORAGE.TODOS] || []).map(t =>
      t.id === id ? { ...t, done: !t.done } : t
    );
    chrome.storage.local.set({ [STORAGE.TODOS]: todos }, () => renderTodos(todos));
  });
}

function deleteTodo(id) {
  chrome.storage.local.get(STORAGE.TODOS, result => {
    const todos = (result[STORAGE.TODOS] || []).filter(t => t.id !== id);
    chrome.storage.local.set({ [STORAGE.TODOS]: todos }, () => renderTodos(todos));
  });
}

// ─── TODO抽出（会話から） ─────────────────────────────────────────────────────

btnExtract.addEventListener('click', async () => {
  btnExtract.disabled = true;
  btnExtract.textContent = '抽出中…';
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) { btnExtract.textContent = 'タブ未検出'; return; }
    const resp = await chrome.tabs.sendMessage(tab.id, { type: 'EXTRACT_TODOS' });
    renderTodos(resp?.todos || []);
    btnExtract.textContent = `${(resp?.todos || []).length}件抽出`;
  } catch {
    btnExtract.textContent = '失敗（Claudeページを開いてください）';
  } finally {
    setTimeout(() => {
      btnExtract.textContent = '会話から抽出';
      btnExtract.disabled = false;
    }, 2000);
  }
});

// ─── 完了タスク削除 ───────────────────────────────────────────────────────────

btnClearDone.addEventListener('click', () => {
  chrome.storage.local.get(STORAGE.TODOS, result => {
    const todos = (result[STORAGE.TODOS] || []).filter(t => !t.done);
    chrome.storage.local.set({ [STORAGE.TODOS]: todos }, () => renderTodos(todos));
  });
});

// ─── 引き継ぎパケット生成 ─────────────────────────────────────────────────────

btnHandoff.addEventListener('click', async () => {
  btnHandoff.disabled = true;
  feedbackEl.textContent = '生成中…';
  feedbackEl.className = 'feedback';
  packetPreview.classList.remove('visible');
  btnCopy.classList.remove('visible');

  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id || !tab.url?.includes('claude.ai')) {
      feedbackEl.textContent = 'Claude.ai のタブを開いてください';
      feedbackEl.className = 'feedback error';
      return;
    }

    const plan = planSelectEl.value;
    const resp = await chrome.tabs.sendMessage(tab.id, { type: 'GENERATE_PACKET', plan });
    const packet = resp?.packet;

    if (!packet) {
      feedbackEl.textContent = '生成に失敗しました';
      feedbackEl.className = 'feedback error';
      return;
    }

    packetPreview.textContent = packet;
    packetPreview.classList.add('visible');
    btnCopy.classList.add('visible');
    feedbackEl.textContent = '生成完了';
    feedbackEl.className = 'feedback';

  } catch (e) {
    feedbackEl.textContent = 'エラー: ' + (e.message || '不明');
    feedbackEl.className = 'feedback error';
  } finally {
    btnHandoff.disabled = false;
  }
});

// ─── クリップボードコピー ─────────────────────────────────────────────────────

btnCopy.addEventListener('click', async () => {
  const text = packetPreview.textContent;
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    btnCopy.textContent = '✅ コピーしました';
    setTimeout(() => { btnCopy.textContent = '📋 クリップボードにコピー'; }, 2000);
  } catch {
    btnCopy.textContent = 'コピー失敗';
  }
});

// ─── 初期化 ───────────────────────────────────────────────────────────────────

refreshTurnCount();
loadTodos();

// 直近パケットがあれば復元表示
chrome.storage.local.get(STORAGE.LOGBOOK_CURRENT, result => {
  const packet = result[STORAGE.LOGBOOK_CURRENT];
  if (packet) {
    packetPreview.textContent = packet;
    packetPreview.classList.add('visible');
    btnCopy.classList.add('visible');
  }
});
