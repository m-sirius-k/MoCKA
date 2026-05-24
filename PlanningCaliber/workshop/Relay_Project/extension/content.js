'use strict';
// Relay v4.2 — content.js
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
  notifySessionStart();
  observeUrlChanges();
  observeDOM();
  scheduleMetricsPush();
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

  if (wasActive) {
    safeSendMessage({ type: 'RELAY_SESSION_END' });
  }

  if (isNew || isChat) {
    turnCount = 0;
    processedMessages.clear();
    notifySessionStart();

    if (isNew) {
      setTimeout(prepareInvisibleHandoff, CONFIG.INJECT_DELAY);
    }
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
  const selectors = [
    '[data-testid="assistant-message"]',
    '.font-claude-response',
    '[class*="assistant-message"]',
    '[data-is-streaming="false"]',
  ];

  for (const sel of selectors) {
    const els = Array.from(document.querySelectorAll(sel));
    if (els.length) return els;
  }

  // Generic fallback: look for large text blocks in the conversation area
  const conv = document.querySelector('[class*="conversation"]') || document.body;
  return Array.from(conv.querySelectorAll('div[class*="message"]'))
    .filter(el => el.textContent.length > 100);
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
  const res = await safeSendMessage({ type: 'RELAY_GET_HANDOFF' });
  if (!res?.packet) {
    console.log('[Relay] No handoff packet — clean start');
    return;
  }
  pendingHandoff  = res.packet;
  sendIntercepted = false;
  showBadgeReady();
  console.log('[Relay] Handoff ready — will inject on first send');
  waitForSendButton();
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
    <div class="relay-badge-logo">R</div>
    <div class="relay-badge-indicator">
      <div class="relay-dot"></div>
      <span class="relay-cpi">—</span>
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
      width: 54px;
      height: 66px;
      background: #0a0e1a;
      border: 1px solid #1e3a5f;
      border-radius: 14px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 7px 5px;
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
    .relay-badge-logo {
      font-size: 20px;
      font-weight: 800;
      color: #38bdf8;
      letter-spacing: -1px;
      line-height: 1;
      text-shadow: 0 0 8px rgba(56,189,248,0.5);
    }
    .relay-badge-indicator {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
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
    .relay-cpi {
      font-size: 9px;
      color: #475569;
      letter-spacing: 0;
    }
    .relay-turns {
      font-size: 9px;
      color: #475569;
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
  if (pendingHandoff) {
    prependHandoffToInput();
    clearPendingHandoff();
    if (badgeEl) badgeEl.classList.remove('handoff-ready');
    return;
  }
  try {
    const res = await safeSendMessage({ type: 'RELAY_GET_HANDOFF' });
    if (!res?.packet) return;
    const input = findInputEl();
    if (input) {
      setInputValue(input, res.packet);
      showBadgeFlash('safe');
    }
  } catch (err) {
    console.error('[Relay] Badge click error:', err);
  }
}

function updateBadge() {
  if (!badgeEl || !isExtensionAlive()) return;

  const dot   = badgeEl.querySelector('.relay-dot');
  const cpiEl = badgeEl.querySelector('.relay-cpi');
  const tEl   = badgeEl.querySelector('.relay-turns');

  if (tEl) tEl.textContent = `T:${turnCount}`;

  safeSendMessage({ type: 'RELAY_GET_METRICS' }).then(m => {
    if (!m) return;
    const cpi = m?.cpi || 0;
    if (cpiEl) cpiEl.textContent = cpi > 0 ? cpi.toFixed(1) : '—';
    if (dot) {
      dot.className = 'relay-dot';
      if (cpi >= 2.5)      dot.classList.add('danger');
      else if (cpi >= 1.2) dot.classList.add('warn');
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

// ─── Boot ────────────────────────────────────────────────────────────────────

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
