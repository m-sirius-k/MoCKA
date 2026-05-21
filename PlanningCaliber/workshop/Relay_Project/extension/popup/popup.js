// Relay popup.js v3.0.0
// Role: render popup UI, handle user actions, send messages to background.js

'use strict';

// -- DOM refs --
const turnBadge  = document.getElementById('turn-badge');
const todoCount  = document.getElementById('todo-count');
const logCount   = document.getElementById('log-count');
const todoEmpty  = document.getElementById('todo-empty');
const todoList   = document.getElementById('todo-list');
const logEmpty   = document.getElementById('log-empty');
const logList    = document.getElementById('log-list');
const clearLogBtn = document.getElementById('clear-log-btn');

// -- tab switching --
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
  });
});

// -- send message helper --
function send(type, payload) {
  return new Promise(resolve => {
    chrome.runtime.sendMessage({ type, payload }, resolve);
  });
}

// -- format helpers --
function fmtTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// -- render TODO list --
function renderTodos(todos) {
  const active = todos.filter(t => t.status === 'active');
  todoCount.textContent = active.length;
  todoEmpty.style.display = active.length ? 'none' : 'block';
  todoList.innerHTML = '';

  for (const t of active) {
    const item = document.createElement('div');
    item.className = 'todo-item';
    item.innerHTML = `
      <div class="todo-check" data-id="${t.id}" title="Mark done">&#10003;</div>
      <div class="todo-body">
        <div class="todo-text">${escHtml(t.text)}</div>
        <div class="todo-meta">
          <span class="source-badge ${t.source}">${t.source === 'assistant' ? 'Claude' : 'You'}</span>
          ${fmtTime(t.created_at)}
        </div>
      </div>
      <button class="todo-del" data-id="${t.id}" title="Remove">✕</button>
    `;
    todoList.appendChild(item);
  }

  // complete on check
  todoList.querySelectorAll('.todo-check').forEach(el => {
    el.addEventListener('click', async () => {
      await send('RELAY_COMPLETE_TODO', { id: el.dataset.id });
      loadAll();
    });
  });

  // delete
  todoList.querySelectorAll('.todo-del').forEach(el => {
    el.addEventListener('click', async () => {
      await send('RELAY_DELETE_TODO', { id: el.dataset.id });
      loadAll();
    });
  });
}

// -- render LOG list --
function renderLog(log) {
  logCount.textContent = log.length;
  logEmpty.style.display = log.length ? 'none' : 'block';
  logList.innerHTML = '';

  for (const entry of log) {
    const item = document.createElement('div');
    item.className = 'log-item';
    item.innerHTML = `
      <div class="log-text">✅ ${escHtml(entry.text)}</div>
      <div class="log-5w1h">
        <span>Who</span>${escHtml(entry.who || '-')}<br>
        <span>What</span>${escHtml(entry.what || entry.text)}<br>
        <span>When</span>${fmtTime(entry.completed_at)}<br>
        <span>Where</span>${escHtml(trimUrl(entry.where || ''))}<br>
        <span>How</span>${escHtml(entry.how || 'completed via Relay')}
      </div>
    `;
    logList.appendChild(item);
  }
}

// -- load everything --
async function loadAll() {
  // turns
  const stats = await send('RELAY_GET_STATS', {});
  if (stats) {
    const turns = stats.turns || 0;
    turnBadge.textContent = `${turns} / 20 turns`;
    turnBadge.className = 'turn-badge' + (turns >= 20 ? ' warn' : '');
  }

  // TODOs
  const td = await send('RELAY_GET_TODOS', {});
  if (td) renderTodos(td.todos || []);

  // LOG
  const lg = await send('RELAY_GET_LOG', {});
  if (lg) renderLog(lg.log || []);
}

// -- clear log --
clearLogBtn.addEventListener('click', async () => {
  if (confirm('Clear all log entries?')) {
    await send('RELAY_CLEAR_LOG', {});
    loadAll();
  }
});

// -- utils --
function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
function trimUrl(url) {
  try { return new URL(url).pathname.slice(0, 40) || url.slice(0, 40); }
  catch { return url.slice(0, 40); }
}

// -- init --
loadAll();
