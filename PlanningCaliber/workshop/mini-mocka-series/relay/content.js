/**
 * Relay for Claude — content.js v2.1
 * Fix: getMessages() selector aligned with countTurns() (user-message)
 * Fix: injectText() ProseMirror injection strengthened
 */

(function() {
  'use strict';

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
    const selectors = [
      '[data-testid="user-message"]',
      '[data-testid="conversation-turn"]',
      '[data-testid^="conversation-turn"]',
      '[class*="ConversationTurn"]'
    ];
    for (const s of selectors) {
      const nodes = document.querySelectorAll(s);
      if (nodes.length > 0) return nodes.length;
    }
    return 0;
  }

  // ── [FIX v2.1] getMessages: user-message基準に統一 ────────────────────────
  function getMessages() {
    // user-messageを基準に取得（countTurns()と同じセレクタ）
    let userNodes = document.querySelectorAll('[data-testid="user-message"]');

    if (userNodes.length > 0) {
      // user-messageが取れた場合: 親要素を辿ってturn全体を取得
      const messages = [];
      userNodes.forEach((node, i) => {
        const text = node.innerText?.trim() || '';
        if (text) messages.push({ role: 'user', text, turn: i * 2 + 1 });

        // 直後のassistant応答を探す
        let next = node.closest('[data-testid^="conversation"]')?.nextElementSibling;
        if (!next) {
          // フォールバック: DOMツリーで兄弟を探す
          const parent = node.parentElement?.parentElement;
          next = parent?.nextElementSibling;
        }
        if (next) {
          const assistantText = next.innerText?.trim() || '';
          if (assistantText) messages.push({ role: 'assistant', text: assistantText, turn: i * 2 + 2 });
        }
      });
      if (messages.length > 0) return messages;
    }

    // フォールバック: conversation-turnセレクタで取得
    const selectors = [
      '[data-testid="conversation-turn"]',
      '[data-testid^="conversation-turn"]'
    ];
    let turns = [];
    for (const s of selectors) {
      turns = [...document.querySelectorAll(s)];
      if (turns.length > 0) break;
    }
    return turns.map((el, i) => {
      const isUser = !!el.querySelector('[data-testid="user-human-turn"], [class*="humanTurn"]');
      return { role: isUser ? 'user' : 'assistant', text: el.innerText?.trim() || '', turn: i + 1 };
    });
  }

  function isOnChatPage() {
    return /claude\.ai\/(chat|new)/.test(location.href);
  }

  // ── [A] Logbook: 構造化抽出 ────────────────────────────────────────────────
  function extractLogbook(messages) {
    const decisions = [];
    const todos = [];
    const insights = [];

    const decPat = /\b(decided|we'll|let's|confirmed|agreed|going with|will use|決定|採用|確定|方針|選択)\b/i;
    const todoPat = /\b(need to|should|next step|next:|todo|will implement|remember to|次:|次は|やること|TODO|実装予定|対応予定)\b/i;
    const insightPat = /\b(realize|found|discovered|important|key insight|turns out|actually|なるほど|気づき|ポイント|重要|発見)\b/i;

    messages.forEach(m => {
      if (!m.text) return;
      m.text.split(/[.!?。！？\n]/).forEach(s => {
        const t = s.trim();
        if (t.length < 8 || t.length > 250) return;
        if (decPat.test(t)) decisions.push(t);
        else if (todoPat.test(t)) todos.push(t);
        else if (insightPat.test(t)) insights.push(t);
      });
    });

    return {
      decisions: [...new Set(decisions)].slice(0, 5),
      todos: [...new Set(todos)].slice(0, 5),
      insights: [...new Set(insights)].slice(0, 3)
    };
  }

  // ── Summary generator ─────────────────────────────────────────────────────
  function generateSummary(messages, vaultContext) {
    const userMsgs = messages.filter(m => m.role === 'user');
    const last = userMsgs[userMsgs.length - 1]?.text?.slice(0, 200) || '';
    const count = messages.length;
    const logbook = extractLogbook(messages);

    const parts = [`[Relay — continuing from ${count} turns]`];

    if (vaultContext) {
      parts.push(`[Vault context]\n${vaultContext}`);
    }
    if (logbook.decisions.length) {
      parts.push(`Decisions:\n${logbook.decisions.map(d => `• ${d}`).join('\n')}`);
    }
    if (logbook.todos.length) {
      parts.push(`Next steps:\n${logbook.todos.map(t => `• ${t}`).join('\n')}`);
    }
    if (logbook.insights.length) {
      parts.push(`Key insights:\n${logbook.insights.map(i => `• ${i}`).join('\n')}`);
    }
    if (last) {
      parts.push(`Last message: "${last}"`);
    }
    parts.push('---\nPlease continue from where we left off.');

    return parts.join('\n\n');
  }

  // ── [FIX v2.1] injectText: ProseMirror強化版 ─────────────────────────────
  function injectText(text) {
    const selectors = [
      'div[contenteditable="true"][data-placeholder]',
      'div[contenteditable="true"].ProseMirror',
      'div[contenteditable="true"]',
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
      // textarea: nativeSetter経由
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      nativeSetter.call(el, text);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }

    // ProseMirror / contenteditable: 3段階フォールバック

    // 方法1: execCommand (一部環境で動作)
    try {
      el.focus();
      document.execCommand('selectAll', false, null);
      const ok = document.execCommand('insertText', false, text);
      if (ok && el.innerText.trim() === text.trim()) {
        el.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
      }
    } catch (_) {}

    // 方法2: innerText直接書き込み + InputEvent
    try {
      el.focus();
      el.innerText = text;
      el.dispatchEvent(new InputEvent('input', {
        bubbles: true, cancelable: true, inputType: 'insertText', data: text
      }));
      // キャレットを末尾に
      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(el);
      range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
      return true;
    } catch (_) {}

    // 方法3: クリップボード経由 (最終手段)
    try {
      navigator.clipboard.writeText(text).then(() => {
        el.focus();
        document.execCommand('paste');
      });
      return true;
    } catch (_) {}

    return false;
  }

  // ── [B] Vault: 過去文脈を取得して注入 ────────────────────────────────────
  function getVaultContext(callback) {
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result?.mocka_global_prefs || {};
      const isProUser = !!prefs.vaultEnabled;
      if (!isProUser) return callback(null);

      chrome.runtime.sendMessage({ type: 'RELAY_GET_VAULT_CONTEXT' }, (res) => {
        callback(res?.context || null);
      });
    });
  }

  // ── Handoff ────────────────────────────────────────────────────────────────
  function triggerHandoff() {
    const messages = getMessages();
    const title = document.title?.replace(' - Claude', '').trim() || 'Untitled';
    const logbook = extractLogbook(messages);

    chrome.runtime.sendMessage({
      type: 'RELAY_SAVE_SESSION',
      payload: { title, url: location.href, messages, logbook }
    });

    getVaultContext((vaultContext) => {
      const summary = generateSummary(messages, vaultContext);
      chrome.runtime.sendMessage({
        type: 'RELAY_OPEN_NEW_CHAT',
        payload: { text: summary }
      });
    });
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
      border: '1px solid #334155',
      opacity: '0.85', cursor: 'pointer',
      transition: 'all .3s, transform .1s',
      userSelect: 'none'
    });
    badge.title = 'クリックで今すぐ引き継ぎ';
    badge.addEventListener('click', () => {
      if (confirm(`Relay: 今すぐ新しいchatに引き継ぎますか？\n(${turnCount}ターン分の文脈を持ち越します)`)) {
        triggerHandoff();
      }
    });
    badge.addEventListener('mouseenter', () => { badge.style.opacity = '1'; badge.style.transform = 'scale(1.05)'; });
    badge.addEventListener('mouseleave', () => { badge.style.opacity = '0.85'; badge.style.transform = 'scale(1)'; });
    document.body.appendChild(badge);
    return badge;
  }

  function updateBadge(count) {
    const b = getBadge();
    const pct = TURN_LIMIT > 0 ? Math.min(100, Math.round((count / TURN_LIMIT) * 100)) : 0;
    let borderColor, bgColor, textColor;
    if (pct >= 100)     { borderColor = '#ef4444'; bgColor = 'rgba(239,68,68,0.2)';   textColor = '#fca5a5'; }
    else if (pct >= 80) { borderColor = '#f59e0b'; bgColor = 'rgba(245,158,11,0.15)'; textColor = '#fcd34d'; }
    else if (pct >= 60) { borderColor = '#f97316'; bgColor = 'rgba(249,115,22,0.1)';  textColor = '#fdba74'; }
    else                { borderColor = '#10b981'; bgColor = '#1a1a2e';               textColor = '#e2e8f0'; }
    b.style.borderColor = borderColor;
    b.style.background  = bgColor;
    b.style.color       = textColor;
    if (pct >= 100) {
      b.style.animation = 'relay-blink 1s infinite';
      if (!document.getElementById('relay-style')) {
        const st = document.createElement('style');
        st.id = 'relay-style';
        st.textContent = '@keyframes relay-blink{0%,100%{opacity:0.85}50%{opacity:1;box-shadow:0 0 12px #ef4444}}';
        document.head.appendChild(st);
      }
    } else {
      b.style.animation = '';
    }
    b.textContent = `Relay · ${count}/${TURN_LIMIT} turns`;
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
      <div style="background:#0f172a;color:#e2e8f0;border:2px solid #ef4444;
        border-radius:16px;padding:32px;max-width:420px;width:90%;text-align:center;
        box-shadow:0 0 40px rgba(239,68,68,0.3);">
        <div style="font-size:32px;margin-bottom:12px">⚡</div>
        <h2 style="margin:0 0 8px;font-size:20px;color:#f1f5f9">${count} turns reached</h2>
        <p style="margin:0 0 8px;font-size:14px;color:#94a3b8;line-height:1.5">
          コンテキストが限界に近づいています。新しいchatに引き継ぎますか？
        </p>
        <p style="margin:0 0 24px;font-size:12px;color:#64748b;">
          ⚠️ 「後で」を押すと次の ${count} ターンまで通知が出ません
        </p>
        <div style="display:flex;gap:10px;justify-content:center">
          <button id="relay-btn-continue" style="background:#3b82f6;color:#fff;border:none;
            padding:10px 24px;border-radius:8px;font-size:14px;cursor:pointer;font-weight:500;">
            今すぐ引き継ぎ ↗
          </button>
          <button id="relay-btn-dismiss" style="background:transparent;color:#64748b;
            border:1px solid #334155;padding:10px 20px;border-radius:8px;font-size:14px;cursor:pointer;">
            後で
          </button>
        </div>
        <p style="margin:16px 0 0;font-size:11px;color:#475569">
          バッジをクリックすればいつでも強制引き継ぎできます
        </p>
      </div>
    `;
    document.body.appendChild(overlay);
    document.getElementById('relay-btn-continue').onclick = () => { overlay.remove(); triggerHandoff(); };
    document.getElementById('relay-btn-dismiss').onclick  = () => { overlay.remove(); };
  }

  // ── URL change & Observer ──────────────────────────────────────────────────
  function checkUrlChange() {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      turnCount = 0;
      warningShown = false;
      updateBadge(0);
    }
  }

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

  // ── Message handler ────────────────────────────────────────────────────────
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.type === 'RELAY_INJECT') {
      setTimeout(() => injectText(msg.payload.text), 1200);
    }
    if (msg.type === 'RELAY_MANUAL_HANDOFF') {
      triggerHandoff();
    }
    if (msg.type === 'RELAY_GET_SUMMARY_FOR_VAULT') {
      const messages = getMessages();
      const logbook = extractLogbook(messages);
      const text = [
        logbook.decisions.length ? 'Decisions:\n' + logbook.decisions.map(d => `• ${d}`).join('\n') : '',
        logbook.todos.length     ? 'Next steps:\n' + logbook.todos.map(t => `• ${t}`).join('\n') : '',
        logbook.insights.length  ? 'Key insights:\n' + logbook.insights.map(i => `• ${i}`).join('\n') : ''
      ].filter(Boolean).join('\n\n');
      // sendResponseはlistener内では使えないのでruntime経由は不可のため直接返す
    }
  });

  // ── Init ───────────────────────────────────────────────────────────────────
  if (isOnChatPage()) {
    turnCount = countTurns();
    updateBadge(turnCount);
    startObserver();
  }

  let _lastPath = location.pathname;
  setInterval(() => {
    if (location.pathname !== _lastPath) {
      _lastPath = location.pathname;
      if (isOnChatPage()) {
        setTimeout(() => {
          turnCount = countTurns();
          updateBadge(turnCount);
          startObserver();
        }, 500);
      }
    }
  }, 500);

})();
