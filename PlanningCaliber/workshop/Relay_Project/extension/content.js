/**
 * Relay for Claude — content.js v2.0
 * PHI OS based. Single file. DOM collection only.
 * UI: English only.
 */
(() => {
  'use strict';

  if (window.__RELAY_LOADED__) return;
  window.__RELAY_LOADED__ = true;

  // ── Config ────────────────────────────────────────────────────────────────
  const PRODUCT       = 'relay';
  const TURN_LIMIT    = 20;
  const STREAM_IDLE   = 1200;
  const SAVE_INTERVAL = 60000;

  // ── State ─────────────────────────────────────────────────────────────────
  let turnCount     = 0;
  let lastText      = '';
  let lastHash      = '';
  let streamTimer   = null;
  let warningShown  = false;
  let sessionId     = crypto.randomUUID();
  let messages      = [];

  // ── DOM helpers ───────────────────────────────────────────────────────────
  const $ = s => document.querySelector(s);

  function getAssistantText() {
    const el = $('[data-is-streaming="false"] .font-claude-message') ||
               $('.font-claude-message') ||
               $('[class*="prose"]');
    return el ? (el.innerText || '').trim() : '';
  }

  function getInput() {
    return $('div[contenteditable="true"][data-testid]') ||
           $('div[contenteditable="true"]');
  }

  function countTurns() {
    const els = document.querySelectorAll(
      '[data-testid*="human-turn"],[data-testid*="assistant-turn"],' +
      '.font-user-message,.font-claude-message'
    );
    return Math.floor(els.length / 2);
  }

  function hash(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++)
      h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
    return String(h);
  }

  // ── TODO extraction ───────────────────────────────────────────────────────
  function extractTodos(text) {
    // Remove code blocks first
    const clean = text.replace(/```[\s\S]*?```/g, '').replace(/`[^`]+`/g, '');
    const lines = clean.split('\n');
    const results = [];

    const pattern = /^[-*\d.\s]*(\[RELAY_TODO\]|TODO[:\s]|Please\s+(confirm|check|verify|fix|add|update)|Next\s+step|Action\s+item)/i;

    function isCode(line) {
      if (/^(const|let|var|function|return|if|for|class|import|export)\s/.test(line)) return true;
      if (/Write-Host|Get-Content|Copy-Item|chrome\.|console\.|document\./.test(line)) return true;
      if (/^(PS |cd |git |python |pip |npm |\$)/.test(line)) return true;
      const syms = (line.match(/[^a-zA-Z0-9぀-鿿\s]/g) || []).length;
      return syms / Math.max(line.length, 1) > 0.35;
    }

    for (const line of lines) {
      const t = line.trim();
      if (t.length < 12 || isCode(t)) continue;
      if (t.match(pattern) || t.startsWith('[RELAY_TODO]')) {
        const content = t.replace(/^\[RELAY_TODO\]\s*/, '').replace(/^[-*\d.]+\s*/, '').trim();
        if (content.length >= 12) results.push(content);
        if (results.length >= 5) break;
      }
    }
    return results;
  }

  // ── Send to background ────────────────────────────────────────────────────
  function send(type, payload) {
    if (typeof chrome === 'undefined' || !chrome.runtime) return;
    chrome.runtime.sendMessage({ type, payload }).catch(() => {});
  }

  // ── Auto save ─────────────────────────────────────────────────────────────
  function autoSave() {
    if (!messages.length) return;
    const data = { product: PRODUCT, title: document.title, url: location.href,
                   messages, turns: turnCount, sessionId,
                   id: sessionId, created_at: new Date().toISOString() };
    const h = hash(JSON.stringify(data));
    if (h === lastHash) return;
    lastHash = h;
    send('RELAY_AUTO_SAVE', data);
  }

  // ── Badge ─────────────────────────────────────────────────────────────────
  function refreshBadge() {
    if (typeof chrome === 'undefined' || !chrome.storage) return;
    chrome.storage.local.get('phi_todos', (data) => {
      if (chrome.runtime.lastError) return;
      const open = ((data.phi_todos) || []).filter(t => t.status !== 'done');
      const pct  = turnCount / TURN_LIMIT;
      const color = pct >= 0.8 ? '#ef4444' : pct >= 0.5 ? '#f97316' : '#22c55e';

      let badge = document.getElementById('__relay_badge__');
      if (!badge) {
        badge = document.createElement('div');
        badge.id = '__relay_badge__';
        Object.assign(badge.style, {
          position: 'fixed', bottom: '16px', right: '16px',
          zIndex: '2147483647', background: '#0d0d1a',
          border: '1.5px solid ' + color, borderRadius: '20px',
          padding: '4px 12px', fontFamily: 'monospace',
          fontSize: '12px', fontWeight: 'bold', color,
          cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.4)',
          userSelect: 'none', transition: 'all 0.3s',
        });
        badge.addEventListener('click', showHandoffPopup);
        document.body.appendChild(badge);
      }
      badge.style.borderColor = color;
      badge.style.color = color;
      badge.textContent = open.length
        ? `${turnCount}/${TURN_LIMIT} 📋${open.length}`
        : `${turnCount}/${TURN_LIMIT}`;

      if (pct >= 0.8) {
        if (!document.getElementById('__relay_style__')) {
          const s = document.createElement('style');
          s.id = '__relay_style__';
          s.textContent = '@keyframes relay-blink{0%,100%{opacity:1}50%{opacity:0.3}}';
          document.head.appendChild(s);
        }
        badge.style.animation = 'relay-blink 1s step-end infinite';
      } else {
        badge.style.animation = '';
      }
    });
  }

  // ── Handoff popup ─────────────────────────────────────────────────────────
  function showHandoffPopup() {
    if (document.getElementById('__relay_popup__')) return;
    chrome.storage.local.get('phi_todos', (data) => {
      const open = ((data.phi_todos) || []).filter(t => t.status !== 'done');
      const todoHtml = open.length
        ? `<div style="font-size:11px;color:#888;margin:8px 0 4px">Open TODOs:</div>
           <div style="font-size:12px;background:#1a1a2e;border:1px solid #333;
                       border-radius:6px;padding:8px;max-height:80px;overflow-y:auto">
             ${open.slice(0, 3).map(t => `• ${t.content}`).join('<br>')}
             ${open.length > 3 ? `<br>+${open.length - 3} more` : ''}
           </div>` : '';

      const popup = document.createElement('div');
      popup.id = '__relay_popup__';
      Object.assign(popup.style, {
        position: 'fixed', bottom: '60px', right: '20px',
        zIndex: '2147483647', background: '#0d0d1a',
        border: '1.5px solid #e2c97e', borderRadius: '12px',
        padding: '16px', width: '260px', fontFamily: 'monospace',
        boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
      });
      popup.innerHTML = `
        <div style="color:#e2c97e;font-size:13px;font-weight:bold;margin-bottom:6px">
          ⚡ Relay: ${turnCount} turns reached
        </div>
        <div style="color:#94a3b8;font-size:11px;line-height:1.6;margin-bottom:8px">
          Context is getting long. Continue in a new chat?
        </div>
        ${todoHtml}
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:12px">
          <button id="__relay_dismiss__"
            style="background:none;border:1px solid #555;color:#888;
                   border-radius:6px;padding:6px 14px;cursor:pointer;font-size:12px">
            Later
          </button>
          <button id="__relay_handoff__"
            style="background:#e2c97e;border:none;color:#0d0d1a;
                   border-radius:6px;padding:6px 14px;cursor:pointer;
                   font-size:12px;font-weight:bold">
            New Chat →
          </button>
        </div>`;
      document.body.appendChild(popup);
      document.getElementById('__relay_dismiss__')
        ?.addEventListener('click', () => { popup.remove(); warningShown = true; });
      document.getElementById('__relay_handoff__')
        ?.addEventListener('click', () => { popup.remove(); warningShown = true; triggerHandoff(); });
    });
  }

  // ── Handoff ───────────────────────────────────────────────────────────────
  function triggerHandoff() {
    autoSave();
    chrome.storage.local.get('phi_todos', (data) => {
      const open = ((data.phi_todos) || []).filter(t => t.status !== 'done');
      const lines = [
        '[Relay Handoff]',
        `Session: ${sessionId}`,
        `Turns: ${turnCount}`,
        `URL: ${location.href}`,
      ];
      if (open.length) {
        lines.push('', 'Open TODOs:');
        open.slice(0, 5).forEach(t => lines.push(`- ${t.content}`));
      }
      send('RELAY_OPEN_NEW_CHAT', { text: lines.join('\n') });
    });
  }

  // ── Streaming complete ────────────────────────────────────────────────────
  function onStreamStable() {
    const text = getAssistantText();
    if (!text || text === lastText) return;
    lastText = text;

    messages.push({ role: 'assistant', content: text.slice(0, 2000), ts: Date.now() });
    if (messages.length > 200) messages.splice(0, messages.length - 200);

    const todos = extractTodos(text);
    if (todos.length) send('RELAY_SAVE_TODOS', { todos, sessionId });

    const t = countTurns();
    if (t !== turnCount) {
      turnCount = t;
      refreshBadge();
      if (turnCount >= TURN_LIMIT && !warningShown) showHandoffPopup();
    }

    autoSave();
  }

  // ── MutationObserver ──────────────────────────────────────────────────────
  new MutationObserver(() => {
    clearTimeout(streamTimer);
    streamTimer = setTimeout(onStreamStable, STREAM_IDLE);
  }).observe(document.body, { childList: true, subtree: true, characterData: true });

  // ── Auto save triggers ────────────────────────────────────────────────────
  window.addEventListener('beforeunload', autoSave);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') autoSave();
  });
  setInterval(autoSave, SAVE_INTERVAL);
  setInterval(refreshBadge, 3000);

  // ── Message listener ──────────────────────────────────────────────────────
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'RELAY_INJECT') {
      const el = getInput();
      if (!el) { sendResponse({ ok: false }); return true; }
      el.focus();
      document.execCommand('selectAll');
      document.execCommand('insertText', false, msg.payload?.text || '');
      sendResponse({ ok: true });
      return true;
    }
    if (msg.type === 'RELAY_MANUAL_HANDOFF') {
      triggerHandoff(); sendResponse({ ok: true }); return true;
    }
    return false;
  });

  refreshBadge();
  console.info('[Relay] content.js v2.0 loaded. session:', sessionId);
})();