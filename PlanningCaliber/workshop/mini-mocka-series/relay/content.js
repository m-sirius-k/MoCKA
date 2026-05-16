/**
 * Relay for Claude — content.js (standalone, no imports)
 * All Core SDK logic inlined for Chrome extension compatibility.
 */

(function() {
  'use strict';

  // ── Config ─────────────────────────────────────────────────────────────────
  let TURN_LIMIT = 20;
  let warningShown = false;
  let badge = null;
  let turnCount = 0;
  let lastUrl = location.href;
  let observer = null;

  // ── Load prefs ─────────────────────────────────────────────────────────────
  chrome.storage.sync.get('mocka_global_prefs', (result) => {
    const prefs = result?.mocka_global_prefs || {};
    TURN_LIMIT = prefs.turnLimit || 20;
  });

  // ── DOM helpers ────────────────────────────────────────────────────────────
  function countTurns() {
    return document.querySelectorAll('[data-testid="conversation-turn"]').length;
  }

  function getMessages() {
    const turns = [...document.querySelectorAll('[data-testid="conversation-turn"]')];
    return turns.map((el, i) => {
      const isUser = !!el.querySelector('[data-testid="user-human-turn"]');
      return { role: isUser ? 'user' : 'assistant', text: el.innerText?.trim() || '', turn: i + 1 };
    });
  }

  function isOnChatPage() {
    return /claude\.ai\/(chat|new)/.test(location.href);
  }

  // ── Badge ──────────────────────────────────────────────────────────────────
  function getBadge() {
    if (badge && document.body.contains(badge)) return badge;
    badge = document.createElement('div');
    badge.id = 'relay-badge';
    Object.assign(badge.style, {
      position: 'fixed', bottom: '20px', right: '20px', zIndex: '99999',
      background: '#1a1a2e', color: '#e2e8f0',
      fontFamily: '-apple-system,sans-serif', fontSize: '12px', fontWeight: '500',
      padding: '6px 12px', borderRadius: '20px',
      border: '1px solid #334155', pointerEvents: 'none', opacity: '0.85',
      transition: 'opacity .2s'
    });
    document.body.appendChild(badge);
    return badge;
  }

  function updateBadge(count) {
    const b = getBadge();
    const pct = Math.min(100, Math.round((count / TURN_LIMIT) * 100));
    const color = pct >= 100 ? '#ef4444' : pct >= 80 ? '#f59e0b' : '#10b981';
    b.style.borderColor = color;
    b.textContent = `Relay · ${count}/${TURN_LIMIT} turns`;
  }

  // ── Summary generator (no API needed) ─────────────────────────────────────
  function generateSummary(messages) {
    const userMsgs = messages.filter(m => m.role === 'user');
    const last = userMsgs[userMsgs.length - 1]?.text?.slice(0, 200) || '';
    const count = messages.length;

    const decisions = [];
    const todos = [];
    const decPat = /\b(decided|we'll|let's|confirmed|agreed|going with|will use)\b/i;
    const todoPat = /\b(need to|should|next step|todo|will implement|remember to)\b/i;

    messages.forEach(m => {
      if (!m.text) return;
      m.text.split(/[.!?]/).forEach(s => {
        const t = s.trim();
        if (t.length < 10 || t.length > 200) return;
        if (decPat.test(t)) decisions.push(t);
        if (todoPat.test(t)) todos.push(t);
      });
    });

    const parts = [`[Relay — continuing from ${count} turns]`];
    if (decisions.length) parts.push(`Decisions:\n${[...new Set(decisions)].slice(0,3).map(d=>`• ${d}`).join('\n')}`);
    if (todos.length) parts.push(`Next steps:\n${[...new Set(todos)].slice(0,3).map(t=>`• ${t}`).join('\n')}`);
    if (last) parts.push(`Last message: "${last}"`);
    parts.push('---\nPlease continue from where we left off.');

    return parts.join('\n\n');
  }

  // ── Injector ───────────────────────────────────────────────────────────────
  function injectText(text) {
    const selectors = [
      'div[contenteditable="true"][data-placeholder]',
      'div[contenteditable="true"].ProseMirror',
      'textarea'
    ];
    let el = null;
    for (const s of selectors) {
      el = document.querySelector(s);
      if (el) break;
    }
    if (!el) return false;

    el.focus();
    if (el.tagName === 'TEXTAREA') {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      nativeSetter.call(el, text);
    } else {
      el.textContent = text;
    }
    el.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  }

  // ── Handoff ────────────────────────────────────────────────────────────────
  function triggerHandoff() {
    const messages = getMessages();
    const summary = generateSummary(messages);
    const title = document.title?.replace(' - Claude', '').trim() || 'Untitled';

    // Save session
    chrome.runtime.sendMessage({
      type: 'RELAY_SAVE_SESSION',
      payload: { title, url: location.href, messages }
    });

    // Open new chat and inject
    chrome.runtime.sendMessage({
      type: 'RELAY_OPEN_NEW_CHAT',
      payload: { text: summary }
    });
  }

  // ── Warning overlay ────────────────────────────────────────────────────────
  function showWarning(count) {
    if (warningShown) return;
    warningShown = true;

    const overlay = document.createElement('div');
    overlay.id = 'relay-warning';
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', zIndex: '999999',
      background: 'rgba(0,0,0,0.6)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: '-apple-system,sans-serif'
    });

    overlay.innerHTML = `
      <div style="background:#0f172a;color:#e2e8f0;border:1px solid #334155;
        border-radius:16px;padding:32px;max-width:420px;width:90%;text-align:center;">
        <div style="font-size:32px;margin-bottom:12px">⚡</div>
        <h2 style="margin:0 0 8px;font-size:20px;color:#f1f5f9">${count} turns reached</h2>
        <p style="margin:0 0 24px;font-size:14px;color:#94a3b8;line-height:1.5">
          Relay will summarise this conversation and continue in a new chat.
        </p>
        <div style="display:flex;gap:10px;justify-content:center">
          <button id="relay-btn-continue" style="background:#3b82f6;color:#fff;border:none;
            padding:10px 24px;border-radius:8px;font-size:14px;cursor:pointer;font-weight:500;">
            Continue in new chat ↗
          </button>
          <button id="relay-btn-dismiss" style="background:transparent;color:#64748b;
            border:1px solid #334155;padding:10px 20px;border-radius:8px;font-size:14px;cursor:pointer;">
            Stay here
          </button>
        </div>
        <p style="margin:16px 0 0;font-size:11px;color:#475569">Context will be preserved automatically</p>
      </div>
    `;

    document.body.appendChild(overlay);

    document.getElementById('relay-btn-continue').onclick = () => {
      overlay.remove();
      triggerHandoff();
    };
    document.getElementById('relay-btn-dismiss').onclick = () => {
      overlay.remove();
      warningShown = false;
    };
  }

  // ── URL change detection ───────────────────────────────────────────────────
  function checkUrlChange() {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      turnCount = 0;
      warningShown = false;
      updateBadge(0);
    }
  }

  // ── MutationObserver ───────────────────────────────────────────────────────
  function startObserver() {
    if (observer) observer.disconnect();
    observer = new MutationObserver(() => {
      checkUrlChange();
      if (!isOnChatPage()) return;
      const count = countTurns();
      if (count !== turnCount) {
        turnCount = count;
        updateBadge(count);
        if (count >= TURN_LIMIT && !warningShown) showWarning(count);
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // ── Handle inject message from background ─────────────────────────────────
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'RELAY_INJECT') {
      setTimeout(() => injectText(msg.payload.text), 1000);
    }
    if (msg.type === 'RELAY_MANUAL_HANDOFF') {
      triggerHandoff();
    }
  });

  // ── Init ───────────────────────────────────────────────────────────────────
  if (isOnChatPage()) {
    turnCount = countTurns();
    updateBadge(turnCount);
    startObserver();
  }

})();
