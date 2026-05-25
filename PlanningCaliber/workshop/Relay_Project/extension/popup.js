'use strict';
// Relay v4.8 — popup.js
// Fix v4.8: loadAll() リトライポーリング追加（500ms×6回=最大3秒待機）
//   原因: 新規chat遷移直後にcontent.js初期化完了前にpopupを開くと
//         RELAY_GET_STATSがsession_id=nullを返し no-session表示になっていた
// Fix v4.4: doHandoff() — RELAY_SESSION_END除去
//   原因: SESSION_ENDでrelay_currentがnullになり新規タブのpopupが
//         no-session-state（「Claude.aiでチャットを開いてください」）に戻っていた
// Responsibilities: UI control, real-time updates, user interactions

// ─── DOM References ───────────────────────────────────────────────────────────

const $ = id => document.getElementById(id);

const UI = {
  mainContent:    $('main-content'),
  noSession:      $('no-session-state'),
  cpiValue:       $('cpi-value'),
  cpiStatus:      $('cpi-status'),
  cpiSegments:    $('cpi-segments'),
  tokenValue:     $('token-value'),
  beBar:          $('be-bar'),
  bePct:          $('be-pct'),
  beMargin:       $('be-margin'),
  beTstar:        $('be-tstar'),
  modeSelect:     $('mode-select'),
  turnBadge:      $('turn-badge'),
  todoHeader:     $('todo-header'),
  todoList:       $('todo-list'),
  todoCount:      $('todo-count'),
  todoToggle:     $('todo-toggle'),
  btnHandoff:     $('btn-handoff'),
  btnFeedback:    $('btn-feedback'),
  btnHandoffAlt:  $('btn-handoff-alt'),
  btnFeedbackAlt: $('btn-feedback-alt'),
  pinBtn:         $('pin-btn'),
};

let todoExpanded  = true;
let feedbackTimer = null;
let isPinned      = false;  // ピン留め状態

// ─── Boot ─────────────────────────────────────────────────────────────────────

async function init() {
  try {
    // ピン留め状態をストレージから復元
    const stored = await chrome.storage.local.get(['relay_pinned']);
    isPinned = stored.relay_pinned === true;
    updatePinUI();

    await loadAll();
    bindEvents();
    listenStorageChanges();
  } catch (err) {
    console.error('[Relay popup] init error:', err);
  }
}

// ─── Data Loading ─────────────────────────────────────────────────────────────

// 新規chat遷移直後はcontent.js初期化に時間がかかるため
// 500ms × 最大6回（計3秒）リトライしてからno-session表示にフォールバック
async function loadAll() {
  const RETRY_INTERVAL = 500;
  const MAX_RETRIES    = 6;

  for (let i = 0; i < MAX_RETRIES; i++) {
    const [statsRes, todosRes] = await Promise.all([
      sendMsg({ type: 'RELAY_GET_STATS' }),
      sendMsg({ type: 'RELAY_GET_TODOS' }),
    ]);

    if (statsRes?.session_id) {
      // セッション確立済み → 描画して終了
      renderStats(statsRes);
      renderTodos((todosRes?.todos || []).filter(t => t.status === 'active'));
      return;
    }

    // まだ未確立 → 最終試行でなければ待機してリトライ
    if (i < MAX_RETRIES - 1) {
      await new Promise(r => setTimeout(r, RETRY_INTERVAL));
    }
  }

  // 全リトライ失敗 → no-session表示
  showNoSession();
}

async function renderStats(stats) {
  if (!stats || !stats.session_id) {
    showNoSession();
    return;
  }

  showMainContent();

  // CPI
  const cpi = stats.cpi || 0;
  setCPI(cpi);

  // Tokens
  setTokens(stats.estimated_tokens || 0);

  // Break-even
  setBreakEven(stats.break_even, stats.estimated_tokens || 0);

  // Mode
  if (UI.modeSelect) {
    UI.modeSelect.value = stats.work_mode || 'heavy';
  }

  // Turns
  setTurns(stats.turn_count || 0);
}

// ─── CPI Rendering ────────────────────────────────────────────────────────────

function setCPI(cpi) {
  if (!UI.cpiValue) return;

  // Value display
  const prev = UI.cpiValue.textContent;
  const next = cpi > 0 ? cpi.toFixed(2) : '—';
  if (prev !== next) {
    UI.cpiValue.textContent = next;
    flashUpdate(UI.cpiValue);
  }

  // Segments (10 total, filled = position in 1.0→3.0 range)
  const filled    = cpi <= 0 ? 0 : Math.min(10, Math.max(0, Math.round((cpi - 1.0) / 2.0 * 10)));
  const segEls    = UI.cpiSegments?.querySelectorAll('.seg') || [];
  segEls.forEach((seg, i) => {
    seg.classList.toggle('active', i < filled);
  });

  // Status text + color
  if (UI.cpiStatus) {
    let label, cls;
    if (cpi <= 0)        { label = '待機中'; cls = 'safe';   }
    else if (cpi < 1.2)  { label = '正常';   cls = 'safe';   }
    else if (cpi < 1.8)  { label = '注意';   cls = 'warn';   }
    else if (cpi < 2.5)  { label = '警告';   cls = 'danger'; }
    else                 { label = '危険！'; cls = 'danger'; }
    UI.cpiStatus.textContent = label;
    UI.cpiStatus.className = `cpi-status ${cls}`;
  }
}

// ─── Tokens ───────────────────────────────────────────────────────────────────

function setTokens(n) {
  if (!UI.tokenValue) return;
  const formatted = n >= 1000
    ? (n / 1000).toFixed(1) + 'K'
    : n.toString();
  if (UI.tokenValue.textContent !== formatted) {
    UI.tokenValue.textContent = formatted;
    flashUpdate(UI.tokenValue);
  }
}

// ─── Break-Even ───────────────────────────────────────────────────────────────

function setBreakEven(be, currentTokens) {
  if (!be || !UI.beBar) return;

  const pct    = Math.min(1.2, be.progress) * 100;
  const over   = be.progress >= 1.0;

  UI.beBar.style.width = Math.min(100, pct) + '%';
  UI.beBar.classList.toggle('over', over);

  const pctStr = Math.round(be.progress * 100) + '%';
  if (UI.bePct) UI.bePct.textContent = pctStr;

  if (UI.beMargin) {
    if (over) {
      UI.beMargin.textContent = '⚠ 切替を推奨します';
      UI.beMargin.style.color = 'var(--danger)';
    } else {
      const marginK = be.margin >= 1000
        ? (be.margin / 1000).toFixed(1) + 'K'
        : be.margin;
      UI.beMargin.textContent = `推奨切替まで: ~${marginK} tok`;
      UI.beMargin.style.color = '';
    }
  }

  if (UI.beTstar) {
    const tK = be.T_star >= 1000
      ? (be.T_star / 1000).toFixed(0) + 'K'
      : be.T_star;
    UI.beTstar.textContent = `T*=${tK}`;
  }
}

// ─── Turn Badge ───────────────────────────────────────────────────────────────

function setTurns(n) {
  if (!UI.turnBadge) return;
  UI.turnBadge.textContent = `T: ${n}`;
  UI.turnBadge.classList.toggle('warn-turns', n >= 20);
}

// ─── TODO List ────────────────────────────────────────────────────────────────

function renderTodos(todos) {
  if (!UI.todoList) return;

  if (UI.todoCount) UI.todoCount.textContent = todos.length;

  if (!todos.length) {
    UI.todoList.innerHTML = '<div class="todo-empty">タスクはまだありません</div>';
    return;
  }

  UI.todoList.innerHTML = todos.map(t => `
    <div class="todo-item" data-id="${escHtml(t.id)}">
      <div class="todo-check" data-action="complete" data-id="${escHtml(t.id)}" title="完了にする">
        <svg width="8" height="8" viewBox="0 0 8 8" fill="none" style="display:none" class="check-icon">
          <path d="M1 4L3 6L7 2" stroke="#22c55e" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <span class="todo-text">${escHtml(t.text)}</span>
      <div class="todo-del" data-action="delete" data-id="${escHtml(t.id)}" title="削除">✕</div>
    </div>
  `).join('');
}

// ─── Event Binding ────────────────────────────────────────────────────────────

function bindEvents() {
  // TODO header toggle
  UI.todoHeader?.addEventListener('click', () => {
    todoExpanded = !todoExpanded;
    UI.todoList.style.display = todoExpanded ? '' : 'none';
    if (UI.todoToggle) UI.todoToggle.textContent = todoExpanded ? '▼' : '▶';
  });

  // TODO list actions (delegated)
  UI.todoList?.addEventListener('click', async (e) => {
    const target = e.target.closest('[data-action]');
    if (!target) return;

    const { action, id } = target.dataset;

    if (action === 'complete') {
      await sendMsg({ type: 'RELAY_COMPLETE_TODO', id });
      const item = UI.todoList.querySelector(`[data-id="${id}"]`);
      if (item) {
        item.style.opacity = '0.3';
        item.style.textDecoration = 'line-through';
        setTimeout(async () => {
          await reloadTodos();
        }, 400);
      }
    }

    if (action === 'delete') {
      await sendMsg({ type: 'RELAY_DELETE_TODO', id });
      const item = UI.todoList.querySelector(`[data-id="${id}"]`);
      if (item) {
        item.style.opacity = '0';
        item.style.transform = 'translateX(8px)';
        item.style.transition = 'all 0.25s ease';
        setTimeout(async () => {
          await reloadTodos();
        }, 250);
      }
    }
  });

  // Mode selector
  UI.modeSelect?.addEventListener('change', async (e) => {
    await sendMsg({ type: 'RELAY_SET_MODE', mode: e.target.value });
    // Recompute break-even display
    const stats = await sendMsg({ type: 'RELAY_GET_STATS' });
    if (stats?.break_even) {
      setBreakEven(stats.break_even, stats.estimated_tokens || 0);
    }
  });

  // Pin button
  UI.pinBtn?.addEventListener('click', async () => {
    isPinned = !isPinned;
    await chrome.storage.local.set({ relay_pinned: isPinned });
    updatePinUI();
  });

  // Force handoff button
  [UI.btnHandoff, UI.btnHandoffAlt].forEach((btn, i) => {
    if (!btn) return;
    const fbEl = i === 0 ? UI.btnFeedback : UI.btnFeedbackAlt;
    btn.addEventListener('click', () => doHandoff(btn, fbEl));
  });
}

async function doHandoff(btn, fbEl) {
  if (!btn) return;
  btn.disabled = true;

  try {
    // 1. パケット生成（現在のセッション情報+アクティブTODO）
    //    ※ RELAY_SESSION_END は呼ばない
    //      → 呼ぶと relay_current が null になり新規タブのpopupが
    //         「Claude.aiでチャットを開いてください」（no-session状態）になるため
    const res = await sendMsg({ type: 'RELAY_GET_HANDOFF' });
    if (!res?.packet) {
      showFeedback(fbEl, '引き継ぎデータなし', 'warn');
      btn.disabled = false;
      return;
    }

    // 2. packetをstorageに保存
    //    → 新規タブのcontent.jsが prepareInvisibleHandoff() で自動取得して注入
    await sendMsg({ type: 'RELAY_STORE_HANDOFF', packet: res.packet });

    // 3. 新規タブを開く
    await chrome.tabs.create({ url: 'https://claude.ai/new', active: true });

    // 4. フィードバック表示 → ピン留めOFFの時だけ自動クローズ
    showFeedback(fbEl, '✓ 新規chatで引き継ぎ', 'success');
    if (!isPinned) {
      setTimeout(() => window.close(), 800);
    }

  } catch (err) {
    console.error('[Relay popup] handoff error:', err);
    showFeedback(fbEl, 'エラー: ' + err.message, 'error');
    btn.disabled = false;
  }
}

function showFeedback(el, text, type) {
  if (!el) return;
  clearTimeout(feedbackTimer);
  el.textContent  = text;
  el.className    = `btn-feedback ${type === 'error' ? 'error' : ''}`;
  el.style.opacity = '1';
  feedbackTimer = setTimeout(() => {
    el.style.opacity = '0';
    setTimeout(() => { el.textContent = ''; }, 300);
  }, 3000);
}

// ─── Storage Change Listener ──────────────────────────────────────────────────

function listenStorageChanges() {
  chrome.storage.onChanged.addListener(async (changes, area) => {
    if (area !== 'local') return;

    if (changes.relay_metrics || changes.relay_current) {
      const stats = await sendMsg({ type: 'RELAY_GET_STATS' });
      if (stats) {
        setCPI(stats.cpi || 0);
        setTokens(stats.estimated_tokens || 0);
        setBreakEven(stats.break_even, stats.estimated_tokens || 0);
        setTurns(stats.turn_count || 0);
        if (stats.session_id) showMainContent();
        if (UI.modeSelect && stats.work_mode) {
          UI.modeSelect.value = stats.work_mode;
        }
      }
    }

    if (changes.relay_todos) {
      await reloadTodos();
    }
  });
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function reloadTodos() {
  const res   = await sendMsg({ type: 'RELAY_GET_TODOS' });
  const todos = (res?.todos || []).filter(t => t.status === 'active');
  renderTodos(todos);
}

function showMainContent() {
  if (UI.mainContent)  UI.mainContent.style.display  = '';
  if (UI.noSession)    UI.noSession.style.display     = 'none';
}

function showNoSession() {
  if (UI.mainContent)  UI.mainContent.style.display  = 'none';
  if (UI.noSession)    UI.noSession.style.display     = '';
}

function updatePinUI() {
  if (!UI.pinBtn) return;
  if (isPinned) {
    UI.pinBtn.classList.add('pinned');
    UI.pinBtn.title = 'ピン留め中 — クリックで自動クローズに戻す';
  } else {
    UI.pinBtn.classList.remove('pinned');
    UI.pinBtn.title = 'ピン留め: ONにするとpopupが自動で閉じません';
  }
}

function flashUpdate(el) {
  el.classList.remove('flash-update');
  void el.offsetWidth; // reflow
  el.classList.add('flash-update');
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function sendMsg(msg) {
  return chrome.runtime.sendMessage(msg).catch(() => null);
}

// ─── Start ────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', init);
