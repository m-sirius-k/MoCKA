'use strict';
// Relay v4.1.0 — popup.js
// Fix v4.9: content.js onUrlChange() の SESSION_START→SESSION_END 順序修正に対応
//           loadAll() リトライは保険として維持（最大3秒）
// Fix v4.8: loadAll() リトライポーリング追加（500ms×6回=最大3秒待機）
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
  sideBtn:        $('side-btn'),
  langSelect:     $('lang-select'),
};

let todoExpanded  = true;
let feedbackTimer = null;
let isPinned      = false;  // ピン留め状態

// ─── Boot ─────────────────────────────────────────────────────────────────────

// ─── i18n ─────────────────────────────────────────────────────────────────────

const I18N = {
  ja: {
    cpi: 'CPI', tokens: 'トークン', breakeven: '切替ポイント',
    mode_light: '軽作業（参照・質問）', mode_heavy: '重作業（設計・実装）', mode_file: 'ファイル多用',
    todo_label: 'TODO', todo_empty: 'タスクはまだありません',
    handoff: '⚡ 今すぐ引き継ぎ',
    no_session: 'Claude.ai でチャットを開いてください',
    no_session_sub: 'Relay が自動的に計測を開始します',
    until_switch: '推奨切替まで: ~{0} tok',
    recommend_switch: '⚠ 切替を推奨します',
    pin_title: 'ピン留め: ONにするとpopupが自動で閉じません',
    side_title: 'サイドパネルで開く',
    feedback_success: '✓ 新規chatで引き継ぎ',
    feedback_nodata: '引き継ぎデータなし',
  },
  en: {
    cpi: 'CPI', tokens: 'TOKENS', breakeven: 'BREAK-EVEN',
    mode_light: 'Light (Q&A / reference)', mode_heavy: 'Heavy (code / design)', mode_file: 'File-heavy',
    todo_label: 'TODO', todo_empty: 'No tasks yet',
    handoff: '⚡ Hand off now',
    no_session: 'Open a chat on Claude.ai',
    no_session_sub: 'Relay will start tracking automatically',
    until_switch: 'Switch recommended in ~{0} tok',
    recommend_switch: '⚠ Switch recommended',
    pin_title: 'Pin: keep popup open after handoff',
    side_title: 'Open side panel',
    feedback_success: '✓ Handed off to new chat',
    feedback_nodata: 'No handoff data',
  },
  de: {
    cpi: 'CPI', tokens: 'TOKEN', breakeven: 'BREAK-EVEN',
    mode_light: 'Leicht (Fragen / Referenz)', mode_heavy: 'Schwer (Code / Design)', mode_file: 'Viele Dateien',
    todo_label: 'AUFGABEN', todo_empty: 'Noch keine Aufgaben',
    handoff: '⚡ Jetzt übergeben',
    no_session: 'Öffne einen Chat auf Claude.ai',
    no_session_sub: 'Relay beginnt automatisch mit der Messung',
    until_switch: 'Wechsel empfohlen in ~{0} Tok',
    recommend_switch: '⚠ Wechsel empfohlen',
    pin_title: 'Anheften: Popup nach Übergabe offen halten',
    side_title: 'Seitenleiste öffnen',
    feedback_success: '✓ An neuen Chat übergeben',
    feedback_nodata: 'Keine Übergabedaten',
  },
  fr: {
    cpi: 'CPI', tokens: 'JETONS', breakeven: 'SEUIL DE RENTABILITÉ',
    mode_light: 'Léger (Q&R / référence)', mode_heavy: 'Lourd (code / design)', mode_file: 'Fichiers intensifs',
    todo_label: 'TÂCHES', todo_empty: "Aucune tâche pour l'instant",
    handoff: '⚡ Transférer maintenant',
    no_session: 'Ouvrez un chat sur Claude.ai',
    no_session_sub: 'Relay commencera le suivi automatiquement',
    until_switch: 'Transfert recommandé dans ~{0} tok',
    recommend_switch: '⚠ Transfert recommandé',
    pin_title: 'Épingler: garder le popup ouvert après transfert',
    side_title: 'Ouvrir le panneau latéral',
    feedback_success: '✓ Transféré vers un nouveau chat',
    feedback_nodata: 'Aucune donnée de transfert',
  },
  ko: {
    cpi: 'CPI', tokens: '토큰', breakeven: '전환 기준점',
    mode_light: '가벼운 작업 (질문/참조)', mode_heavy: '무거운 작업 (코딩/설계)', mode_file: '파일 집약적',
    todo_label: '할일', todo_empty: '아직 할일이 없습니다',
    handoff: '⚡ 지금 인계하기',
    no_session: 'Claude.ai에서 채팅을 열어주세요',
    no_session_sub: 'Relay가 자동으로 측정을 시작합니다',
    until_switch: '전환 권장까지: ~{0} tok',
    recommend_switch: '⚠ 전환을 권장합니다',
    pin_title: '고정: 인계 후 팝업 자동 닫힘 방지',
    side_title: '사이드 패널 열기',
    feedback_success: '✓ 새 채팅으로 인계됨',
    feedback_nodata: '인계 데이터 없음',
  },
};

let currentLang = 'ja';

function t(key, ...args) {
  let str = (I18N[currentLang] || I18N.ja)[key] || key;
  args.forEach((a, i) => { str = str.replace('{' + i + '}', a); });
  return str;
}

function applyLang() {
  // ラベル
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  // mode select options
  const ms = document.getElementById('mode-select');
  if (ms) {
    ms.options[0].text = t('mode_light');
    ms.options[1].text = t('mode_heavy');
    ms.options[2].text = t('mode_file');
  }
  // pin/side titles
  const pin  = document.getElementById('pin-btn');
  const side = document.getElementById('side-btn');
  if (pin)  pin.title  = t('pin_title');
  if (side) side.title = t('side_title');
}

async function initLang() {
  const stored = await chrome.storage.local.get(['relay_lang']);
  currentLang = stored.relay_lang || navigator.language.slice(0,2) || 'ja';
  if (!I18N[currentLang]) currentLang = 'ja';
  const sel = document.getElementById('lang-select');
  if (sel) sel.value = currentLang;
  applyLang();
}

async function init() {
  try {
    // ピン留め状態をストレージから復元
    const stored = await chrome.storage.local.get(['relay_pinned']);
    isPinned = stored.relay_pinned === true;
    updatePinUI();

    await initLang();
    await loadAll();
    bindEvents();
    listenStorageChanges();

    // 言語セレクター
    UI.langSelect?.addEventListener('change', async (e) => {
      currentLang = e.target.value;
      await chrome.storage.local.set({ relay_lang: currentLang });
      applyLang();
    });
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
      UI.beMargin.textContent = t('recommend_switch');
      UI.beMargin.style.color = 'var(--danger)';
    } else {
      const marginK = be.margin >= 1000
        ? (be.margin / 1000).toFixed(1) + 'K'
        : be.margin;
      UI.beMargin.textContent = t('until_switch', marginK);
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
    UI.todoList.innerHTML = `<div class="todo-empty">${t('todo_empty')}</div>`;
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

  // Side Panel button
  UI.sideBtn?.addEventListener('click', async () => {
    // サイドパネルを開く
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.id) {
      await chrome.sidePanel.open({ tabId: tab.id });
    }
    window.close();
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
      showFeedback(fbEl, t('feedback_nodata'), 'warn');
      btn.disabled = false;
      return;
    }

    // 2. packetをstorageに保存
    //    → 新規タブのcontent.jsが prepareInvisibleHandoff() で自動取得して注入
    await sendMsg({ type: 'RELAY_STORE_HANDOFF', packet: res.packet });

    // 3. 新規タブを開く
    await chrome.tabs.create({ url: 'https://claude.ai/new', active: true });

    // 4. フィードバック表示 → ピン留めOFFの時だけ自動クローズ
    showFeedback(fbEl, t('feedback_success'), 'success');
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
