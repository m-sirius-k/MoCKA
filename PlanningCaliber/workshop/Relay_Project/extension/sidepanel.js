'use strict';
// Relay v4.1.0 — sidepanel.js (i18n対応)

// ─── I18N ────────────────────────────────────────────────────────────────────
const SP_I18N = {
  ja: {
    tab_todo: 'TODO', tab_handoff: '引き継ぎ',
    sp_placeholder: 'TODOを手動追加...',
    sp_add: '追加', sp_active: '未完了', sp_done: '完了済', sp_all: 'すべて',
    sp_list: 'TODO一覧', sp_preview: '引き継ぎプレビュー',
    sp_loading: '生成中...', sp_handoff: '⚡ 今すぐ引き継ぎ',
    sp_nodata: '（データなし）', sp_notask: 'タスクはありません',
    sp_feedback_ok: '✓ 新規chatで引き継ぎ', sp_feedback_err: 'エラー',
    sp_nodata_fb: '引き継ぎデータなし',
  },
  en: {
    tab_todo: 'TODO', tab_handoff: 'Hand off',
    sp_placeholder: 'Add a task manually...',
    sp_add: 'Add', sp_active: 'Active', sp_done: 'Done', sp_all: 'All',
    sp_list: 'Task list', sp_preview: 'Handoff preview',
    sp_loading: 'Generating...', sp_handoff: '⚡ Hand off now',
    sp_nodata: '(No data)', sp_notask: 'No tasks yet',
    sp_feedback_ok: '✓ Handed off to new chat', sp_feedback_err: 'Error',
    sp_nodata_fb: 'No handoff data',
  },
  de: {
    tab_todo: 'AUFGABEN', tab_handoff: 'Übergabe',
    sp_placeholder: 'Aufgabe manuell hinzufügen...',
    sp_add: 'Hinzuf.', sp_active: 'Offen', sp_done: 'Erledigt', sp_all: 'Alle',
    sp_list: 'Aufgabenliste', sp_preview: 'Übergabevorschau',
    sp_loading: 'Generiere...', sp_handoff: '⚡ Jetzt übergeben',
    sp_nodata: '(Keine Daten)', sp_notask: 'Noch keine Aufgaben',
    sp_feedback_ok: '✓ An neuen Chat übergeben', sp_feedback_err: 'Fehler',
    sp_nodata_fb: 'Keine Übergabedaten',
  },
  fr: {
    tab_todo: 'TÂCHES', tab_handoff: 'Transfert',
    sp_placeholder: 'Ajouter une tâche...',
    sp_add: 'Ajouter', sp_active: 'En cours', sp_done: 'Terminé', sp_all: 'Tout',
    sp_list: 'Liste des tâches', sp_preview: 'Aperçu du transfert',
    sp_loading: 'Génération...', sp_handoff: '⚡ Transférer maintenant',
    sp_nodata: '(Aucune donnée)', sp_notask: 'Aucune tâche',
    sp_feedback_ok: '✓ Transféré vers un nouveau chat', sp_feedback_err: 'Erreur',
    sp_nodata_fb: 'Aucune donnée de transfert',
  },
  ko: {
    tab_todo: '할일', tab_handoff: '인계',
    sp_placeholder: '할일을 직접 추가...',
    sp_add: '추가', sp_active: '진행중', sp_done: '완료', sp_all: '전체',
    sp_list: '할일 목록', sp_preview: '인계 미리보기',
    sp_loading: '생성 중...', sp_handoff: '⚡ 지금 인계하기',
    sp_nodata: '(데이터 없음)', sp_notask: '할일이 없습니다',
    sp_feedback_ok: '✓ 새 채팅으로 인계됨', sp_feedback_err: '오류',
    sp_nodata_fb: '인계 데이터 없음',
  },
};

let spLang = 'ja';
function st(key) { return (SP_I18N[spLang] || SP_I18N.ja)[key] || key; }

function applySpLang() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = st(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = st(el.dataset.i18nPlaceholder);
  });
}

async function initSpLang() {
  const stored = await chrome.storage.local.get(['relay_lang']);
  spLang = stored.relay_lang || navigator.language.slice(0,2) || 'ja';
  if (!SP_I18N[spLang]) spLang = 'ja';
  applySpLang();
}


const $ = id => document.getElementById(id);

let currentFilter = 'active';
let feedbackTimer = null;

// ─── Boot ─────────────────────────────────────────────────────────────────────

async function init() {
  await initSpLang();
  bindTabs();
  bindFilters();
  bindAddTodo();
  bindHandoffTab();
  bindToPopup();
  listenStorage();

  await loadStats();
  await loadTodos();
}

// ─── Stats ────────────────────────────────────────────────────────────────────

async function loadStats() {
  const stats = await sendMsg({ type: 'RELAY_GET_STATS' });
  if (!stats) return;

  const cpiEl = $('sp-cpi');
  if (cpiEl) {
    const cpi = stats.cpi || 0;
    cpiEl.textContent = cpi > 0 ? cpi.toFixed(2) : '—';
    cpiEl.className = 'stat-val mono';
    if      (cpi >= 2.5) cpiEl.classList.add('danger');
    else if (cpi >= 1.8) cpiEl.classList.add('warn');
    else if (cpi > 0)    cpiEl.classList.add('safe');
  }

  const tok = stats.estimated_tokens || 0;
  const tokEl = $('sp-tokens');
  if (tokEl) tokEl.textContent = tok >= 1000 ? (tok / 1000).toFixed(1) + 'K' : tok;

  const turnsEl = $('sp-turns');
  if (turnsEl) {
    turnsEl.textContent = stats.turn_count || 0;
    turnsEl.className = 'stat-val mono';
    if ((stats.turn_count || 0) >= 20) turnsEl.classList.add('warn');
  }

  // Break-even
  if (stats.break_even) {
    const be = stats.break_even;
    const bar = $('sp-be-bar');
    if (bar) {
      bar.style.width = Math.min(100, be.progress * 100) + '%';
      bar.classList.toggle('over', be.progress >= 1.0);
    }
    const pctEl = $('sp-be-pct');
    if (pctEl) pctEl.textContent = Math.round(be.progress * 100) + '%';
    const marginEl = $('sp-be-margin');
    if (marginEl) {
      if (be.progress >= 1.0) {
        marginEl.textContent = '⚠ 切替を推奨します';
        marginEl.style.color = 'var(--danger)';
      } else {
        const m = be.margin >= 1000 ? (be.margin / 1000).toFixed(1) + 'K' : be.margin;
        marginEl.textContent = `推奨切替まで: ~${m} tok`;
        marginEl.style.color = '';
      }
    }
    const tstarEl = $('sp-be-tstar');
    if (tstarEl) {
      const tK = be.T_star >= 1000 ? (be.T_star / 1000).toFixed(0) + 'K' : be.T_star;
      tstarEl.textContent = `T*=${tK}`;
    }
  }
}

// ─── TODO ─────────────────────────────────────────────────────────────────────

async function loadTodos() {
  const res = await sendMsg({ type: 'RELAY_GET_TODOS' });
  const all = res?.todos || [];
  renderTodos(all);
}

function renderTodos(all) {
  const list = $('sp-todo-list');
  const countEl = $('sp-todo-count');
  if (!list) return;

  let filtered;
  if (currentFilter === 'active') filtered = all.filter(t => t.status === 'active');
  else if (currentFilter === 'done') filtered = all.filter(t => t.status === 'done');
  else filtered = all;

  if (countEl) countEl.textContent = filtered.length;

  if (!filtered.length) {
    list.innerHTML = `<div class="todo-empty">${st('sp_notask')}</div>`;
    return;
  }

  list.innerHTML = filtered.map(t => `
    <div class="todo-item${t.status === 'done' ? ' done' : ''}" data-id="${esc(t.id)}">
      <div class="todo-check${t.status === 'done' ? ' checked' : ''}"
           data-action="complete" data-id="${esc(t.id)}"
           title="${t.status === 'done' ? '完了済' : '完了にする'}">
        ${t.status === 'done' ? '<svg width="9" height="9" viewBox="0 0 9 9"><path d="M1.5 4.5L3.5 6.5L7.5 2.5" stroke="#0a0e1a" stroke-width="1.5" stroke-linecap="round" fill="none"/></svg>' : ''}
      </div>
      <span class="todo-num">${esc(t.id)}</span>
      <span class="todo-text">${esc(t.text)}</span>
      <div class="todo-del" data-action="delete" data-id="${esc(t.id)}" title="削除">✕</div>
    </div>
  `).join('');

  // Delegate click
  list.onclick = async (e) => {
    const target = e.target.closest('[data-action]');
    if (!target) return;
    const { action, id } = target.dataset;

    if (action === 'complete') {
      await sendMsg({ type: 'RELAY_COMPLETE_TODO', id });
      await loadTodos();
    }
    if (action === 'delete') {
      await sendMsg({ type: 'RELAY_DELETE_TODO', id });
      await loadTodos();
    }
  };
}

// ─── Add TODO ─────────────────────────────────────────────────────────────────

function bindAddTodo() {
  const input = $('sp-todo-input');
  const btn   = $('sp-todo-add');
  if (!input || !btn) return;

  const doAdd = async () => {
    const text = input.value.trim();
    if (text.length < 3) return;
    await sendMsg({ type: 'RELAY_ADD_TODO', text, source: 'manual' });
    input.value = '';
    await loadTodos();
  };

  btn.addEventListener('click', doAdd);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') doAdd(); });
}

// ─── Filters ──────────────────────────────────────────────────────────────────

function bindFilters() {
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', async () => {
      document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentFilter = chip.dataset.filter;
      await loadTodos();
    });
  });
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────

function bindTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', async () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const panel = $('tab-' + tab.dataset.tab);
      if (panel) panel.classList.add('active');

      if (tab.dataset.tab === 'handoff') {
        await loadHandoffPreview();
        await loadStats();
      }
    });
  });
}

// ─── Handoff tab ──────────────────────────────────────────────────────────────

function bindHandoffTab() {
  $('sp-refresh-handoff')?.addEventListener('click', loadHandoffPreview);

  $('sp-btn-handoff')?.addEventListener('click', async () => {
    const btn = $('sp-btn-handoff');
    btn.disabled = true;
    try {
      const res = await sendMsg({ type: 'RELAY_GET_HANDOFF' });
      if (!res?.packet) { showFeedback(st('sp_nodata_fb'), 'error'); btn.disabled = false; return; }
      await sendMsg({ type: 'RELAY_STORE_HANDOFF', packet: res.packet });
      await chrome.tabs.create({ url: 'https://claude.ai/new', active: true });
      showFeedback(st('sp_feedback_ok'), '');
    } catch (err) {
      showFeedback('エラー: ' + err.message, 'error');
      btn.disabled = false;
    }
  });
}

async function loadHandoffPreview() {
  const box = $('sp-handoff-preview');
  if (!box) return;
  box.textContent = '生成中...';
  const res = await sendMsg({ type: 'RELAY_GET_HANDOFF' });
  box.textContent = res?.packet || st('sp_nodata');
}

function showFeedback(text, cls) {
  const el = $('sp-feedback');
  if (!el) return;
  clearTimeout(feedbackTimer);
  el.textContent = text;
  el.className = 'feedback' + (cls ? ' ' + cls : '');
  el.style.opacity = '1';
  feedbackTimer = setTimeout(() => { el.style.opacity = '0'; }, 3000);
}

// ─── To Popup button ──────────────────────────────────────────────────────────

function bindToPopup() {
  $('btn-to-popup')?.addEventListener('click', () => {
    // サイドパネルを閉じる（Chrome APIではサイドパネル単体のcloseは不可のため
    // action.openPopupでポップアップを開く）
    chrome.runtime.sendMessage({ type: 'RELAY_OPEN_POPUP' }).catch(() => {});
    window.close();
  });
}

// ─── Storage listener ─────────────────────────────────────────────────────────

function listenStorage() {
  chrome.storage.onChanged.addListener(async (changes, area) => {
    if (area !== 'local') return;
    if (changes.relay_todos)   await loadTodos();
    if (changes.relay_metrics || changes.relay_current) await loadStats();
    if (changes.relay_lang) { spLang = changes.relay_lang.newValue || 'ja'; applySpLang(); }
  });
}

// ─── Utils ────────────────────────────────────────────────────────────────────

function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function sendMsg(msg) {
  return chrome.runtime.sendMessage(msg).catch(() => null);
}

document.addEventListener('DOMContentLoaded', init);
