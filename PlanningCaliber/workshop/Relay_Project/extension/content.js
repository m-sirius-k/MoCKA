'use strict';
// Relay v4.6 — content.js
// Fix v4.1: Extension context invalidated guard + CSP Google Fonts removed
// Fix v4.2: Smart handoff — invisible inject on first send (not pasted into input)

const CONFIG = {
  TURN_WARN:     20,
  SCAN_INTERVAL: 3000,
  IDLE_WAIT:     1500,
  BADGE_ID:      'relay-badge',
  INJECT_DELAY:  1500,
};

const INPUT_SELECTORS = [
  'div[contenteditable="true"][data-testid="composer-input"]',
  'div[contenteditable="true"].ProseMirror',
  'div[contenteditable="true"]',
];

const SEND_BUTTON_SELECTORS = [
  'button[data-testid="send-button"]',
  'button[aria-label="Send message"]',
  'button[aria-label="メッセージを送信"]',
  'button[type="submit"]',
];

// TODO patterns — priority order
const EN_PATTERNS = [
  /^\[RELAY_TODO\]\s*(.+)/i,
  /^-\s*\[\s*\]\s*(.+)/,
  /^(?:TODO|Fix|Add|Update|Create|Check|Review|Implement|Deploy)\s*[:：]?\s*(.+)/i,
];

const JA_PATTERNS = [
  /^(?:TODO|タスク|作業|対応|修正|追加|確認)\s*[:：]\s*(.+)/,
  /^[・•]\s*(.{15,})/,
  /^(\d+[.)]\s*.{15,})/,
];

// ─── Extension Context Guard ──────────────────────────────────────────────────

function isExtensionAlive() {
  try { return !!(chrome?.runtime?.id); } catch (e) { return false; }
}

function safeSendMessage(msg) {
  if (!isExtensionAlive()) return Promise.resolve(null);
  try { return chrome.runtime.sendMessage(msg).catch(() => null); }
  catch (e) { return Promise.resolve(null); }
}

// ─── State ───────────────────────────────────────────────────────────────────

let currentUrl         = location.href;
let turnCount          = 0;
let processedMessages  = new Set();
let streamingTimer     = null;
let badgeEl            = null;
let mutationObserver   = null;
let initialized        = false;

// 不可視注入用
let pendingHandoff     = null;
let sendIntercepted    = false;
let sendButtonObserver = null;

// ─── Init ────────────────────────────────────────────────────────────────────

function init() {
  if (initialized) return;
  initialized = true;

  console.log('[Relay] Initializing on', location.href);
  createBadge();
  observeUrlChanges();
  observeDOM();
  scheduleMetricsPush();

  // URL確定後に1回だけセッション開始通知
  // /new → /chat/xxx の遷移はonUrlChangeが処理するため、
  // ここではchat確定ページのみ通知する（/newは遷移後に任せる）
  if (/\/chat\/[a-z0-9-]+/.test(location.href)) {
    notifySessionStart();
  } else if (/\/new($|\?)/.test(location.href)) {
    // /new は遷移後のonUrlChangeでnotifySessionStart+prepareInvisibleHandoffが走る
    // ただし/newで止まる場合（直接開いた場合）のためフォールバック
    setTimeout(() => {
      if (/\/new($|\?)/.test(location.href)) {
        notifySessionStart();
        prepareInvisibleHandoff();
      }
    }, CONFIG.INJECT_DELAY);
  } else {
    // その他のページ（トップページ等）でも一応通知
    notifySessionStart();
  }
}

// ─── URL / Session Lifecycle ─────────────────────────────────────────────────

function observeUrlChanges() {
  let lastUrl = location.href;

  setInterval(() => {
    if (location.href !== lastUrl) {
      const prev = lastUrl;
      lastUrl    = location.href;
      onUrlChange(prev, location.href);
    }
  }, 100);

  window.addEventListener('popstate', () => {
    if (location.href !== currentUrl) {
      onUrlChange(currentUrl, location.href);
      currentUrl = location.href;
    }
  });
}

function onUrlChange(from, to) {
  console.log('[Relay] URL:', from.split('/').slice(-2).join('/'), '->', to.split('/').slice(-2).join('/'));

  const wasActive = /\/(chat|new)/.test(from);
  const isNew     = /\/new($|\?)/.test(to);
  const isChat    = /\/chat\/[a-z0-9-]+/.test(to);

  if (isNew || isChat) {
    turnCount = 0;
    processedMessages.clear();

    // Fix v4.9: SESSION_START を先に送り relay_current を確立してから
    // SESSION_END を送る。逆順だと popup の RELAY_GET_STATS が
    // relay_current=null の瞬間を踏んで no-session 表示になる。
    notifySessionStart();

    if (wasActive) {
      // 新セッションが storage に書き込まれるのを待ってから旧セッションを閉じる
      setTimeout(() => safeSendMessage({ type: 'RELAY_SESSION_END' }), 150);
    }

    if (isNew) {
      setTimeout(prepareInvisibleHandoff, CONFIG.INJECT_DELAY);
    }
  } else if (wasActive) {
    // chat でも /new でもないページへ移動した場合のみ即時 END
    safeSendMessage({ type: 'RELAY_SESSION_END' });
  }

  currentUrl = to;
  updateBadge();
}

function notifySessionStart() {
  const sessionId = extractSessionId(location.href);
  safeSendMessage({ type: 'RELAY_SESSION_START', sessionId });
}

function extractSessionId(url) {
  const m = url.match(/\/chat\/([a-z0-9-]+)/);
  return m ? m[1] : 'session_' + Date.now();
}

// ─── DOM Observation ──────────────────────────────────────────────────────────

function observeDOM() {
  if (mutationObserver) mutationObserver.disconnect();

  mutationObserver = new MutationObserver(debounce(checkForNewMessages, 600));
  mutationObserver.observe(document.body, { childList: true, subtree: true });
}

function checkForNewMessages() {
  if (!isExtensionAlive()) return;
  const messages = getAIMessages();
  messages.forEach(el => {
    const id = getMessageId(el);
    if (processedMessages.has(id)) return;

    clearTimeout(streamingTimer);
    streamingTimer = setTimeout(() => {
      if (isStreaming()) return;
      const freshId = getMessageId(el);
      if (!processedMessages.has(freshId)) {
        processMessage(el, freshId);
      }
    }, CONFIG.IDLE_WAIT);
  });
}

function getAIMessages() {
  // 2026年版 claude.ai セレクター（優先順）
  const selectors = [
    // 現行 claude.ai DOM
    '[data-testid="assistant-message"]',
    'div.font-claude-message',
    'div[class*="font-claude"]',
    '.font-claude-response',
    // フォールバック群
    '[class*="assistant-message"]',
    '[class*="AssistantMessage"]',
    'div[class*="message-content"]',
  ];

  for (const sel of selectors) {
    try {
      const els = Array.from(document.querySelectorAll(sel));
      if (els.length) return els;
    } catch(e) {}
  }

  // 汎用フォールバック: 会話エリア内の100文字超テキストブロック
  // role="presentation" や article タグも対象
  const containers = [
    document.querySelector('[class*="conversation-content"]'),
    document.querySelector('[class*="ConversationContent"]'),
    document.querySelector('main'),
    document.body,
  ].filter(Boolean);

  for (const conv of containers) {
    const candidates = Array.from(conv.querySelectorAll(
      'div[class*="message"], article, [role="article"]'
    )).filter(el => el.textContent.length > 100);
    if (candidates.length) return candidates;
  }

  return [];
}

function getMessageId(el) {
  const attr = el.dataset?.messageId || el.id;
  if (attr) return attr;
  return hashText((el.textContent || '').slice(0, 120));
}

function isStreaming() {
  return !!(
    document.querySelector('[data-is-streaming="true"]') ||
    document.querySelector('[class*="stop-button"]:not([disabled])') ||
    document.querySelector('button[aria-label*="Stop"]') ||
    document.querySelector('[class*="loading-indicator"]')
  );
}

function processMessage(el, id) {
  if (!isExtensionAlive()) return;
  processedMessages.add(id);
  turnCount++;

  const text   = el.textContent || '';
  const tokens = estimateTokens(text);

  safeSendMessage({ type: 'RELAY_TURN_UPDATE', tokens });

  const todos = extractTodos(text);
  todos.forEach(t => {
    safeSendMessage({ type: 'RELAY_ADD_TODO', text: t, source: 'auto' });
  });

  if (todos.length) console.log('[Relay] Extracted', todos.length, 'TODOs');

  detectAndSetWorkMode(text);
  updateBadge();
  console.log('[Relay] Turn', turnCount, '— tokens ~', tokens);
}

function estimateTokens(text) {
  return Math.round(text.length / 4);
}

// ─── Work Mode Detection ──────────────────────────────────────────────────────

function detectAndSetWorkMode(text) {
  const codeBlocks = (text.match(/```/g) || []).length;
  const hasCode    = codeBlocks > 4;
  const isLarge    = text.length > 5000;

  let mode = 'light';
  if (hasCode || isLarge) {
    mode = 'file';
  } else {
    const heavyKw = ['実装', '設計', 'コード', 'エラー', 'バグ', 'fix', 'implement', 'design', 'debug', 'build'];
    if (heavyKw.some(k => text.toLowerCase().includes(k))) mode = 'heavy';
  }

  safeSendMessage({ type: 'RELAY_SET_MODE', mode });
}

// ─── TODO Extraction ─────────────────────────────────────────────────────────

function extractTodos(text) {
  const lines   = text.split('\n');
  const todos   = [];
  let inCode    = false;

  for (const line of lines) {
    if (line.startsWith('```')) { inCode = !inCode; continue; }
    if (inCode) continue;

    const trimmed = line.trim();
    if (trimmed.length < 15 || trimmed.length > 200) continue;

    // Reject high symbol density (likely code)
    const symbols = (trimmed.match(/[^a-zA-Z0-9぀-龯\s\-:.,]/g) || []).length;
    if (symbols / trimmed.length > 0.30) continue;

    // ★ Reject: Relay引き継ぎブロックの区切り・ヘッダー行
    if (/^━+$/.test(trimmed)) continue;
    if (/^■\s/.test(trimmed)) continue;
    // ★ Reject: [LB_xxx] 形式の引き継ぎTODO行（自己ブロック）
    if (/^\[LB_\d+\]/.test(trimmed)) continue;
    // ★ Reject: Relay引き継ぎセクション識別子
    if (/^\[Relay引き継ぎ/.test(trimmed)) continue;
    if (/^上記を踏まえて/.test(trimmed)) continue;
    // ★ Reject: ターン数・作業・未完了TODOの引き継ぎ記述行
    if (/^(?:ターン数|作業|未完了TODO)\s*[:：]/.test(trimmed)) continue;
    // ★ Reject: MoCKA形式の完了報告行 (TODO_xxx完了, LB_xxx完了, _170完了 等)
    if (/(?:TODO[_-]?\d+|LB[_-]?\d+|_\d+)\s*(?:[（(].*?[)）])?\s*[:：]?\s*.*(?:完了|done|finished)/i.test(trimmed)) continue;
    // ★ Reject: _数字（〜）形式の引き継ぎ行全般
    if (/^_\d+[（(【]/.test(trimmed)) continue;
    // ★ Reject: 🚫 ✅ → 等の記号付き注釈行
    if (/^(?:→|→\s*🚫|→\s*✅|🚫|✅)/.test(trimmed)) continue;
    // ★ Reject: 日付+完了パターン
    if (/20\d\d[-\/]\d\d[-\/]\d\d.*完了/.test(trimmed)) continue;
    // ★ Reject: 表組みの行
    if (/^\|.+\|/.test(trimmed)) continue;
    // ★ Reject: × 数字（補正係数的な記述）
    if (/^[×x]\s*\d/.test(trimmed)) continue;
    // ★ Reject: 数字+ = 〜 のような計算式行
    if (/^\d+[\+\-\*\/]\s*\d/.test(trimmed)) continue;

    let matched = null;

    for (const pat of EN_PATTERNS) {
      const m = trimmed.match(pat);
      if (m) { matched = (m[1] || '').trim(); break; }
    }

    if (!matched) {
      for (const pat of JA_PATTERNS) {
        const m = trimmed.match(pat);
        if (m) { matched = (m[1] || '').trim(); break; }
      }
    }

    // Japanese imperative endings
    if (!matched && /(?:してください|しておく|しておいて|お願いします|必要です)$/.test(trimmed)) {
      matched = trimmed;
    }

    if (matched && matched.length >= 15 && matched.length <= 200) {
      todos.push(matched);
    }
  }

  return [...new Set(todos)]; // dedup
}

// ─── Invisible Handoff (案A) ─────────────────────────────────────────────────

async function prepareInvisibleHandoff() {
  if (!isExtensionAlive()) return;

  // popup経由の手動引き継ぎパケットを優先確認
  const stored = await chrome.storage.local.get(['relay_handoff_packet']);
  let packet = stored.relay_handoff_packet || null;
  if (packet) {
    await chrome.storage.local.remove(['relay_handoff_packet']);
    console.log('[Relay] Handoff packet from popup');
  } else {
    const res = await safeSendMessage({ type: 'RELAY_GET_HANDOFF' });
    packet = res?.packet || null;
  }

  if (!packet) {
    console.log('[Relay] No handoff packet — clean start');
    return;
  }

  // テキストボックスが出現するまで最大5秒待ってから即入力
  console.log('[Relay] Handoff packet ready — waiting for input box...');
  injectWhenReady(packet, 0);
}

function injectWhenReady(packet, attempts) {
  const MAX = 20; // 20 * 250ms = 5秒
  const input = findInputEl();
  if (input) {
    setInputValue(input, packet);
    showBadgeFlash('safe');
    console.log('[Relay] Handoff injected into input box');
    return;
  }
  if (attempts >= MAX) {
    // fallback: 送信ボタン押下時に注入
    pendingHandoff  = packet;
    sendIntercepted = false;
    showBadgeReady();
    console.log('[Relay] Input not found — fallback to send-intercept mode');
    waitForSendButton();
    return;
  }
  setTimeout(() => injectWhenReady(packet, attempts + 1), 250);
}

function waitForSendButton() {
  if (sendButtonObserver) sendButtonObserver.disconnect();
  const btn = findSendButton();
  if (btn) { interceptSendButton(btn); return; }
  sendButtonObserver = new MutationObserver(() => {
    const b = findSendButton();
    if (b) { sendButtonObserver.disconnect(); interceptSendButton(b); }
  });
  sendButtonObserver.observe(document.body, { childList: true, subtree: true });
}

function findSendButton() {
  for (const sel of SEND_BUTTON_SELECTORS) {
    const el = document.querySelector(sel);
    if (el) return el;
  }
  return null;
}

function interceptSendButton(btn) {
  if (!pendingHandoff) return;
  btn.addEventListener('click', onFirstSend, { capture: true, once: true });
  const input = findInputEl();
  if (input) input.addEventListener('keydown', onFirstSendKey, { capture: true });
  console.log('[Relay] Send button intercepted');
}

function onFirstSend() {
  if (sendIntercepted || !pendingHandoff) return;
  sendIntercepted = true;
  prependHandoffToInput();
  clearPendingHandoff();
}

function onFirstSendKey(e) {
  if (e.key !== 'Enter' || e.shiftKey) return;
  if (sendIntercepted || !pendingHandoff) return;
  sendIntercepted = true;
  prependHandoffToInput();
  clearPendingHandoff();
  const input = findInputEl();
  if (input) input.removeEventListener('keydown', onFirstSendKey, { capture: true });
}

function prependHandoffToInput() {
  const input = findInputEl();
  if (!input || !pendingHandoff) return;
  const current  = input.innerText || input.textContent || '';
  const combined = pendingHandoff + '\n\n' + current;
  input.focus();
  const sel = window.getSelection();
  const rng = document.createRange();
  rng.selectNodeContents(input);
  sel.removeAllRanges();
  sel.addRange(rng);
  const ok = document.execCommand('insertText', false, combined);
  if (!ok) {
    input.innerText = combined;
    input.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
  }
  console.log('[Relay] Handoff invisibly prepended');
  showBadgeFlash('safe');
}

function clearPendingHandoff() {
  pendingHandoff  = null;
  sendIntercepted = false;
  if (sendButtonObserver) { sendButtonObserver.disconnect(); sendButtonObserver = null; }
}

function findInputEl() {
  for (const sel of INPUT_SELECTORS) {
    const el = document.querySelector(sel);
    if (el) return el;
  }
  return null;
}

function setInputValue(el, text) {
  el.focus();

  // Select all existing content
  const sel = window.getSelection();
  const rng = document.createRange();
  rng.selectNodeContents(el);
  sel.removeAllRanges();
  sel.addRange(rng);

  // Insert text via execCommand for React compatibility
  const ok = document.execCommand('insertText', false, text);

  // Fallback if execCommand is blocked
  if (!ok) {
    el.innerText = text;
    el.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
}

// ─── Badge ────────────────────────────────────────────────────────────────────

function createBadge() {
  if (document.getElementById(CONFIG.BADGE_ID)) return;

  injectBadgeStyles();

  badgeEl = document.createElement('div');
  badgeEl.id = CONFIG.BADGE_ID;
  badgeEl.innerHTML = `
    <div class="relay-badge-indicator">
      <div class="relay-dot"></div>
      <div class="relay-metric-row">
        <span class="relay-metric-lbl">CPI</span>
        <span class="relay-cpi-val">—</span>
      </div>
      <div class="relay-metric-row">
        <span class="relay-metric-lbl">TOK</span>
        <span class="relay-tok-val">—</span>
      </div>
      <span class="relay-cpi-label">正常</span>
    </div>
    <div class="relay-turns">T:0</div>
  `;

  badgeEl.title = 'Relay — クリックで引き継ぎ注入';
  badgeEl.addEventListener('click', handleBadgeClick);

  document.body.appendChild(badgeEl);
}

function injectBadgeStyles() {
  if (document.getElementById('relay-badge-styles')) return;
  const style = document.createElement('style');
  style.id = 'relay-badge-styles';
  style.textContent = `
    #relay-badge {
      position: fixed !important;
      bottom: 24px !important;
      right: 24px !important;
      width: 72px;
      height: 88px;
      background: #0c1220;
      border: 1px solid #1e3a5f;
      border-radius: 12px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 7px 6px;
      cursor: pointer;
      z-index: 999999 !important;
      box-shadow: 0 4px 24px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.04);
      transition: transform 0.25s cubic-bezier(0.4,0,0.2,1),
                  border-color 0.3s ease,
                  box-shadow 0.3s ease;
      font-family: ui-monospace, 'Cascadia Code', 'Fira Code', monospace;
      user-select: none;
    }
    #relay-badge:hover {
      transform: translateY(-3px) scale(1.04);
      border-color: #38bdf8;
      box-shadow: 0 8px 32px rgba(0,0,0,0.8), 0 0 16px rgba(56,189,248,0.25);
    }
    #relay-badge:active {
      transform: translateY(-1px) scale(1.01);
    }
    .relay-badge-indicator {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 3px;
      width: 100%;
    }
    .relay-metric-row {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      width: 100%;
      gap: 2px;
    }
    .relay-metric-lbl {
      font-size: 8px;
      color: #f0e060;
      opacity: 0.7;
      letter-spacing: 0.3px;
      flex-shrink: 0;
    }
    .relay-dot {
      width: 11px;
      height: 11px;
      border-radius: 50%;
      background: #22c55e;
      box-shadow: 0 0 8px rgba(34,197,94,0.7);
      transition: background 0.4s ease, box-shadow 0.4s ease;
    }
    .relay-dot.warn {
      background: #f59e0b;
      box-shadow: 0 0 8px rgba(245,158,11,0.7);
      animation: relay-pulse 1.8s ease-in-out infinite;
    }
    .relay-dot.ready {
      background: #38bdf8;
      box-shadow: 0 0 8px rgba(56,189,248,0.7);
      animation: relay-pulse 2.5s ease-in-out infinite;
    }
    .relay-dot.danger {
      background: #ef4444;
      box-shadow: 0 0 10px rgba(239,68,68,0.8);
      animation: relay-pulse 0.9s ease-in-out infinite;
    }
    .relay-cpi-val {
      font-size: 13px;
      font-weight: 700;
      color: #f0e060;
      letter-spacing: 0;
      line-height: 1.1;
    }
    .relay-cpi-label {
      font-size: 8px;
      color: #22c55e;
      letter-spacing: 0;
    }
    .relay-cpi-label.warn   { color: #f59e0b; }
    .relay-cpi-label.danger { color: #ef4444; }
    .relay-tokens-row {
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .relay-tok-val {
      font-size: 11px;
      font-weight: 600;
      color: #f0e060;
      letter-spacing: 0;
    }
    .relay-turns {
      font-size: 9px;
      color: #f0e060;
      letter-spacing: 0.4px;
    }
    #relay-badge.handoff-ready {
      border-color: #38bdf8 !important;
      box-shadow: 0 0 16px rgba(56,189,248,0.4) !important;
    }
    #relay-badge.flash-safe {
      border-color: #22c55e !important;
      box-shadow: 0 0 24px rgba(34,197,94,0.6) !important;
      transition: border-color 0.1s ease, box-shadow 0.1s ease;
    }
    @keyframes relay-pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%       { opacity: 0.5; transform: scale(0.9); }
    }
  `;
  document.head.appendChild(style);
}

async function handleBadgeClick() {
  if (!isExtensionAlive()) return;
  try {
    // セッション終了してパケット生成
    await safeSendMessage({ type: 'RELAY_SESSION_END' });
    await new Promise(r => setTimeout(r, 400));

    const res = await safeSendMessage({ type: 'RELAY_GET_HANDOFF' });
    const packet = res?.packet || null;

    if (!packet) {
      showBadgeFlash('warn');
      console.log('[Relay] Badge click — no handoff data');
      return;
    }

    // storageに保存 → 新規タブのcontent.jsが自動取得して注入
    await safeSendMessage({ type: 'RELAY_STORE_HANDOFF', packet });
    await safeSendMessage({ type: 'RELAY_OPEN_TAB' });
    showBadgeFlash('safe');

  } catch (err) {
    console.error('[Relay] Badge click error:', err);
  }
}

function updateBadge() {
  if (!badgeEl || !isExtensionAlive()) return;

  const dot      = badgeEl.querySelector('.relay-dot');
  const cpiValEl = badgeEl.querySelector('.relay-cpi-val');
  const cpiLblEl = badgeEl.querySelector('.relay-cpi-label');
  const tokEl    = badgeEl.querySelector('.relay-tok-val');
  const tEl      = badgeEl.querySelector('.relay-turns');

  if (tEl) tEl.textContent = `T:${turnCount}`;

  safeSendMessage({ type: 'RELAY_GET_STATS' }).then(s => {
    if (!s) return;

    // CPI
    const cpi = s.cpi || 0;
    if (cpiValEl) cpiValEl.textContent = cpi > 0 ? cpi.toFixed(2) : '—';

    // CPI ラベル + 色
    if (cpiLblEl) {
      let label, cls;
      if      (cpi <= 0)   { label = '待機中'; cls = ''; }
      else if (cpi < 1.2)  { label = '正常';   cls = ''; }
      else if (cpi < 1.8)  { label = '注意';   cls = 'warn'; }
      else if (cpi < 2.5)  { label = '警告';   cls = 'warn'; }
      else                 { label = '危険！'; cls = 'danger'; }
      cpiLblEl.textContent = label;
      cpiLblEl.className   = 'relay-cpi-label' + (cls ? ' ' + cls : '');
    }

    // DOT 色
    if (dot) {
      dot.className = 'relay-dot';
      if      (cpi >= 2.5) dot.classList.add('danger');
      else if (cpi >= 1.2) dot.classList.add('warn');
    }

    // TOKENS
    const tok = s.estimated_tokens || 0;
    if (tokEl) {
      tokEl.textContent = tok >= 1000
        ? (tok / 1000).toFixed(1) + 'K'
        : tok > 0 ? tok.toString() : '—';
    }
  }).catch(() => {});
}

function showBadgeReady() {
  if (!badgeEl) return;
  badgeEl.classList.add('handoff-ready');
  badgeEl.title = 'Relay — 引き継ぎ準備完了 (送信時に自動注入)';
  const dot = badgeEl.querySelector('.relay-dot');
  if (dot) dot.className = 'relay-dot ready';
}

function showBadgeFlash(type) {
  if (!badgeEl) return;
  badgeEl.classList.remove('handoff-ready');
  badgeEl.classList.add(`flash-${type}`);
  setTimeout(() => badgeEl.classList.remove(`flash-${type}`), 1600);
}

// ─── Metrics Push ─────────────────────────────────────────────────────────────

function scheduleMetricsPush() {
  setInterval(() => {
    if (!isExtensionAlive()) return;
    const heap    = performance.memory?.usedJSHeapSize || 0;
    const domSize = document.body?.innerHTML?.length   || 0;

    safeSendMessage({ type: 'RELAY_METRICS_UPDATE', heap, domSize });
    updateBadge();
  }, CONFIG.SCAN_INTERVAL);
}

// ─── Message Listener (from popup) ───────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'RELAY_INJECT_HANDOFF') {
    const input = findInputEl();
    if (input && msg.packet) {
      setInputValue(input, msg.packet);
      showBadgeFlash('safe');
      sendResponse({ ok: true });
    } else {
      sendResponse({ error: 'input not found' });
    }
    return true;
  }
});

// ─── Utilities ────────────────────────────────────────────────────────────────

function debounce(fn, ms) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
}

function hashText(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(31, h) + str.charCodeAt(i) | 0;
  }
  return (h >>> 0).toString(36);
}

// ─── Intent Engine v2.0 — 口頭TODO完了 ───────────────────────────────────────
// 「452番終了」「LB3完了」「1〜5 done」などを検知してbackground.jsに送信
// ※ 引き継ぎ注入ロジック (prepareInvisibleHandoff等) には一切触れない

(function() {

  // ── パターン定義 ──────────────────────────────────────────────────────────
  // 単体: 「452番終了」「LB_003完了」「3番おわった」「todo 7 done」
  const SINGLE_RE   = /(?:LB[_-]?)?(\d{1,4})\s*(?:番|番目|号)?\s*(?:終了|完了|おわり|おわった|done|finish(?:ed)?|close[sd]?)/i;
  // 範囲: 「1〜5番完了」「1から3終了」「1-3 done」
  const RANGE_RE    = /(?:LB[_-]?)?(\d{1,4})\s*[〜~\-から]\s*(?:LB[_-]?)?(\d{1,4})\s*(?:番|番目|号)?\s*(?:終了|完了|おわり|おわった|done|finish(?:ed)?|close[sd]?)/i;
  // TODOリスト表示: 「todoリスト」「todo見せて」「what's pending」
  const LIST_RE     = /(?:todo\s*(?:リスト|一覧|見せ|show|list)|pending\s*todo|未完了\s*todo|todo\s*what)/i;

  // ── 番号解析 ─────────────────────────────────────────────────────────────
  function parseIntent(text) {
    const t = text.trim();

    // 範囲チェック（先に）
    const rm = t.match(RANGE_RE);
    if (rm) {
      return { type: 'range', from: parseInt(rm[1]), to: parseInt(rm[2]) };
    }

    // 単体チェック
    const sm = t.match(SINGLE_RE);
    if (sm) {
      return { type: 'single', num: parseInt(sm[1]) };
    }

    // リスト表示
    if (LIST_RE.test(t)) {
      return { type: 'list' };
    }

    return null;
  }

  // ── トースト表示 ─────────────────────────────────────────────────────────
  function showIntentToast(msg, color) {
    const el = document.createElement('div');
    el.textContent = msg;
    el.style.cssText = [
      'position:fixed', 'bottom:100px', 'right:24px',
      `background:${color || '#22c55e'}`, 'color:#fff',
      'padding:9px 16px', 'border-radius:10px', 'font-size:13px',
      'z-index:9999999', 'font-family:ui-monospace,monospace',
      'box-shadow:0 4px 16px rgba(0,0,0,0.5)', 'max-width:320px',
    ].join(';');
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }

  // ── TODO一覧をトーストで表示 ─────────────────────────────────────────────
  async function showTodoList() {
    if (!isExtensionAlive()) return;
    try {
      const res = await safeSendMessage({ type: 'RELAY_GET_TODO_LIST' });
      const todos = res?.todos || [];
      if (!todos.length) {
        showIntentToast('📋 未完了TODOはありません', '#475569');
        return;
      }
      const lines = ['📋 未完了TODO:'];
      todos.slice(0, 8).forEach(t => {
        lines.push(`  ${t.id}: ${t.text.slice(0, 50)}${t.text.length > 50 ? '…' : ''}`);
      });
      if (todos.length > 8) lines.push(`  … 他${todos.length - 8}件`);
      showIntentToast(lines.join('\n'), '#0f172a');
    } catch (e) {
      console.error('[Relay Intent] showTodoList error:', e);
    }
  }

  // ── 完了処理 ─────────────────────────────────────────────────────────────
  async function handleComplete(intent) {
    if (!isExtensionAlive()) return;
    try {
      if (intent.type === 'single') {
        const res = await safeSendMessage({ type: 'RELAY_COMPLETE_BY_NUM', num: intent.num });
        if (res?.ok) {
          showIntentToast(`✓ LB_${String(intent.num).padStart(3,'0')} 完了`);
        } else {
          showIntentToast(`LB_${String(intent.num).padStart(3,'0')} が見つかりません`, '#f59e0b');
        }
      } else if (intent.type === 'range') {
        const res = await safeSendMessage({ type: 'RELAY_COMPLETE_RANGE', from: intent.from, to: intent.to });
        showIntentToast(`✓ LB_${String(intent.from).padStart(3,'0')} 〜 LB_${String(intent.to).padStart(3,'0')} 完了 (${res?.count || 0}件)`);
      }
    } catch (e) {
      console.error('[Relay Intent] handleComplete error:', e);
    }
  }

  // ── Enterキー監視 ─────────────────────────────────────────────────────────
  // ※ 引き継ぎ注入 (onFirstSend/onFirstSendKey) とは独立して動作
  document.addEventListener('keydown', function onIntentKey(e) {
    if (e.key !== 'Enter' || e.shiftKey) return;

    const input = document.querySelector('div[contenteditable="true"]') ||
                  document.querySelector('textarea');
    if (!input) return;

    const text = (input.innerText || input.value || '').trim();
    if (!text || text.length < 2) return;

    const intent = parseIntent(text);
    if (!intent) return;

    // Enterを少し遅らせてから処理（Claudeへの送信後に実行）
    setTimeout(() => {
      if (intent.type === 'list') {
        showTodoList();
      } else {
        handleComplete(intent);
      }
    }, 300);

  }, false);

  console.log('[Relay] Intent Engine v2.0 loaded');

})();

// ─── Manual TODO — 選択テキスト右クリック (半自動) ───────────────────────────
// テキスト選択後Ctrl+Shift+T でTODO登録
// ※ 右クリックはmanifest.jsonのcontextMenusで対応、ここではキーショートカット

(function() {

  document.addEventListener('keydown', function onManualTodo(e) {
    // Ctrl+Shift+T (Windows/Linux) or Cmd+Shift+T (Mac)
    if (!((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T')) return;

    const sel = window.getSelection();
    const text = sel ? sel.toString().trim() : '';

    if (!text || text.length < 5) {
      // 選択なし → TODOリスト表示
      safeSendMessage({ type: 'RELAY_GET_TODO_LIST' }).then(res => {
        const todos = res?.todos || [];
        if (!todos.length) {
          showManualToast('📋 未完了TODOはありません', '#475569');
          return;
        }
        const lines = todos.slice(0, 6).map(t => `${t.id}: ${t.text.slice(0,45)}`);
        showManualToast('📋 ' + lines.join('\n'), '#0f172a');
      }).catch(() => {});
      return;
    }

    if (text.length > 200) {
      showManualToast('選択テキストが長すぎます（200文字以内）', '#f59e0b');
      return;
    }

    safeSendMessage({ type: 'RELAY_ADD_TODO', text, source: 'manual' }).then(() => {
      showManualToast(`📌 TODO登録: ${text.slice(0, 50)}${text.length > 50 ? '…' : ''}`);
    }).catch(() => {});

    e.preventDefault();
  }, false);

  function showManualToast(msg, color) {
    const el = document.createElement('div');
    el.textContent = msg;
    el.style.cssText = [
      'position:fixed', 'bottom:100px', 'right:24px',
      `background:${color || '#3b82f6'}`, 'color:#fff',
      'padding:9px 16px', 'border-radius:10px', 'font-size:13px',
      'z-index:9999999', 'font-family:ui-monospace,monospace',
      'box-shadow:0 4px 16px rgba(0,0,0,0.5)', 'white-space:pre-line',
      'max-width:340px',
    ].join(';');
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3500);
  }

  console.log('[Relay] Manual TODO (Ctrl+Shift+T) loaded');

})();

// ─── Boot ────────────────────────────────────────────────────────────────────

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
