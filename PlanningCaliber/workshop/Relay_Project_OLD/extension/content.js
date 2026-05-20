/**
 * Relay for Claude - content.js v4.0
 * 完全リアーキテクチャ:
 * - localStorage廃止 → chrome.storage.local統一
 * - debounce MutationObserver でストリーミング完了検知
 * - autosave (ターン増加/離脱/30秒定期)
 * - popup → background直通信 (content script依存排除)
 */

(function() {
  'use strict';

  let TURN_LIMIT = 20;
  let warningShown = false;
  let badge = null;
  let turnCount = 0;
  let lastUrl = location.href;
  let mainObserver = null;
  let intervalId = null;
  let streamingTimer = null;
  let lastProcessedText = '';
  let lastAutoSaveText = '';

  // ── コンテキスト有効チェック ───────────────────────────────────────────────
  function isContextValid() {
    try { return !!(chrome && chrome.runtime && chrome.runtime.id); }
    catch (_) { return false; }
  }

  function teardown() {
    if (mainObserver) { mainObserver.disconnect(); mainObserver = null; }
    if (intervalId)   { clearInterval(intervalId);  intervalId = null; }
    if (streamingTimer) { clearTimeout(streamingTimer); streamingTimer = null; }
    if (badge && badge.parentNode) { badge.remove(); badge = null; }
  }

  // ── prefs ─────────────────────────────────────────────────────────────────
  if (isContextValid()) {
    chrome.storage.sync.get('mocka_global_prefs', (r) => {
      TURN_LIMIT = (r && r.mocka_global_prefs && r.mocka_global_prefs.turnLimit) || 20;
    });
  }

  // ── DOM helpers ───────────────────────────────────────────────────────────
  function countTurns() {
    const sels = [
      '[data-testid="user-message"]',
      '[data-testid="conversation-turn"]',
      '[class*="ConversationTurn"]'
    ];
    for (const s of sels) {
      const n = document.querySelectorAll(s);
      if (n.length > 0) return n.length;
    }
    return 0;
  }

  function getLatestAssistantText() {
    const nodes = document.querySelectorAll('.font-claude-response-body');
    if (!nodes.length) return '';
    return nodes[nodes.length - 1].innerText.trim();
  }

  function getMessages() {
    const userNodes = Array.from(document.querySelectorAll('[data-testid="user-message"]'));
    const assistantNodes = Array.from(document.querySelectorAll('.font-claude-response-body'));
    const messages = [];
    userNodes.forEach((node, i) => {
      const text = node.textContent.trim();
      if (!text) return;
      messages.push({ role: 'user', text, turn: i * 2 + 1 });
      const a = assistantNodes[i];
      if (a) {
        const at = a.innerText.trim();
        if (at) messages.push({ role: 'assistant', text: at.slice(0, 500), turn: i * 2 + 2 });
      }
    });
    return messages;
  }

  function isOnChatPage() {
    return /claude\.ai\/(chat|new)/.test(location.href);
  }

  // ── chrome.storage.local TODO API ─────────────────────────────────────────
  const TODO_KEY = 'relay_todos';

  function loadTodos(cb) {
    chrome.storage.local.get(TODO_KEY, (d) => {
      cb(Array.isArray(d[TODO_KEY]) ? d[TODO_KEY] : []);
    });
  }

  function saveTodosToStorage(todos) {
    chrome.storage.local.set({ [TODO_KEY]: todos });
  }

  function nextTodoId(todos) {
    if (!todos.length) return 'LB_001';
    const nums = todos.map(t => parseInt((t.id || '').replace('LB_', ''), 10)).filter(n => !isNaN(n));
    return 'LB_' + String(Math.max(...nums) + 1).padStart(3, '0');
  }

  // ── TODO抽出フィルター ────────────────────────────────────────────────────
  const CODE_PAT   = /[{};]|=>|\b(const|let|var|function|return|map|filter|import|export|class|async|await)\b/;
  const TODO_PATS  = [
    /(?:^|[。\n])\s*(?:TODO[：:]?\s*|→\s*|次[はに]?[：:]?\s*|やること[：:]?\s*|対応[：:]?\s*|実装[：:]?\s*)(.{5,80})(?=[。\n！？]|$)/gi,
    /(.{5,80})(?:してください|する予定|しておく|実装する|対応する|確認する|作成する|修正する|追加する)(?=[。\n]|$)/gi,
    /(?:^|[\.\n])\s*(?:TODO[：:]?\s*|[-•→]\s*|Next[：:]?\s*|Need to[：:]?\s*|Should[：:]?\s*)(.{5,80})(?=[.\n!?]|$)/gi,
  ];
  const STATUS_PATS = [
    { re: /(?:LB[_-]?)?(\d{3})\s*(?:完了|終わった|done|finished|済み)/gi, status: '完了' },
    { re: /(?:LB[_-]?)?(\d{3})\s*(?:進行中|やってる|作業中|in progress)/gi, status: '進行中' },
    { re: /(?:LB[_-]?)?(\d{3})\s*(?:未着手|戻す|cancel|undo)/gi, status: '未着手' },
  ];

  function isValidTodo(text) {
    if (!text || text.trim().length < 5) return false;
    const t = text.trim();
    if (/^[-=_]{3,}/.test(t)) return false;
    if (/^[`{}();]/.test(t)) return false;
    if (CODE_PAT.test(t)) return false;
    if (t.includes('${') || t.includes('`')) return false;
    return true;
  }

  function extractCandidates(text) {
    const set = new Set();
    TODO_PATS.forEach(pat => {
      pat.lastIndex = 0;
      let m;
      while ((m = pat.exec(text)) !== null) {
        const c = (m[1] || m[0]).trim().replace(/[。！？!?\n]+$/, '').trim();
        if (c.length >= 5 && c.length <= 100 && isValidTodo(c)) set.add(c);
      }
    });
    text.split('\n').forEach(line => {
      const t = line.trim();
      const bm = t.match(/^(?:[-•✓→]\s*|(?:TODO|todo)[：:]\s*|(?:\d+[.)]\s*))(.{5,100})$/);
      if (bm) set.add(bm[1].trim());
    });
    // [RELAY_TODO]タグ
    const tagRe = /\[RELAY_TODO\]([\s\S]*?)\[\/RELAY_TODO\]/g;
    let tm;
    while ((tm = tagRe.exec(text)) !== null) {
      tm[1].trim().split('\n').forEach(line => {
        const parts = line.split('|').map(s => s.trim());
        const content = parts[parts.length - 1];
        if (content && content.length >= 5) set.add(content);
      });
    }
    return [...set].filter(isValidTodo);
  }

  // ── TODO保存 ──────────────────────────────────────────────────────────────
  function addTodosFromText(text) {
    if (!isContextValid()) return;
    const candidates = extractCandidates(text);
    if (!candidates.length) return;
    loadTodos((todos) => {
      const existing = todos.map(t => t.content.toLowerCase());
      let added = 0;
      candidates.forEach(content => {
        if (existing.includes(content.toLowerCase())) return;
        const id = nextTodoId(todos);
        todos.push({
          id, content,
          status: '未着手', priority: '中',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          sessionUrl: location.href,
        });
        existing.push(content.toLowerCase());
        added++;
      });
      if (added > 0) {
        saveTodosToStorage(todos);
        showToast(`📋 TODO ${added}件を記録`);
      }
    });
  }

  // ── ステータスコマンド処理 ────────────────────────────────────────────────
  let _lastUserText = '';
  function processUserInput() {
    const nodes = document.querySelectorAll('[data-testid="user-message"]');
    if (!nodes.length) return;
    const text = nodes[nodes.length - 1].textContent.trim();
    if (!text || text === _lastUserText) return;
    _lastUserText = text;
    loadTodos((todos) => {
      let changed = false;
      STATUS_PATS.forEach(({ re, status }) => {
        re.lastIndex = 0;
        let m;
        while ((m = re.exec(text)) !== null) {
          const id = 'LB_' + String(parseInt(m[1], 10)).padStart(3, '0');
          const t = todos.find(x => x.id === id);
          if (t && t.status !== status) {
            t.status = status;
            t.updatedAt = new Date().toISOString();
            if (status === '完了') t.completed_at = new Date().toISOString();
            changed = true;
          }
        }
      });
      if (changed) {
        saveTodosToStorage(todos);
        showToast('✓ TODOステータスを更新しました');
      }
    });
  }

  // ── debounce ストリーミング完了検知 ───────────────────────────────────────
  function onStreamingStable() {
    const text = getLatestAssistantText();
    if (!text || text.length < 20) return;
    if (text === lastProcessedText) return;
    lastProcessedText = text;
    addTodosFromText(text);
  }

  // ── autosave ──────────────────────────────────────────────────────────────
  function autoSave() {
    if (!isContextValid() || !isOnChatPage()) return;
    const messages = getMessages();
    if (!messages.length) return;
    const text = messages.map(m => m.text).join('|');
    if (text === lastAutoSaveText) return;
    lastAutoSaveText = text;
    const title = (document.title || 'Untitled').replace(' - Claude', '').trim();
    chrome.runtime.sendMessage({
      type: 'RELAY_SAVE_SESSION',
      payload: { title, url: location.href, messages, logbook: extractLogbook(messages) }
    });
  }

  function extractLogbook(messages) {
    const decisions = [], todos = [], insights = [];
    const dPat = /\b(decided|confirmed|agreed|決定|採用|確定|方針)\b/i;
    const tPat = /\b(need to|next step|todo|次:|やること|TODO|実装予定)\b/i;
    const iPat = /\b(realize|found|important|なるほど|気づき|ポイント|重要)\b/i;
    messages.forEach(m => {
      if (!m.text) return;
      m.text.split(/[.!?。！？\n]/).forEach(s => {
        const t = s.trim();
        if (t.length < 8 || t.length > 250) return;
        if (dPat.test(t)) decisions.push(t);
        else if (tPat.test(t)) todos.push(t);
        else if (iPat.test(t)) insights.push(t);
      });
    });
    return {
      decisions: [...new Set(decisions)].slice(0, 5),
      todos: [...new Set(todos)].slice(0, 5),
      insights: [...new Set(insights)].slice(0, 3)
    };
  }

  // ── handoff ───────────────────────────────────────────────────────────────
  function triggerHandoff() {
    if (!isContextValid()) return;
    autoSave();
    const messages = getMessages();
    const title = (document.title || 'Untitled').replace(' - Claude', '').trim();
    loadTodos((todos) => {
      const pending = todos.filter(t => t.status !== '完了');
      const parts = [`[Relay — continuing from ${messages.length} turns]`];
      if (pending.length) {
        parts.push('[Logbook — 積み残し]\n' + pending.slice(0, 10).map(t => `  ${t.id}: ${t.content}`).join('\n'));
      }
      const last = messages.filter(m => m.role === 'user').slice(-1)[0];
      if (last) parts.push(`Last message: "${last.text.slice(0, 200)}"`);
      parts.push('---\nPlease continue from where we left off.');
      chrome.runtime.sendMessage({
        type: 'RELAY_OPEN_NEW_CHAT',
        payload: { text: parts.join('\n\n') }
      });
    });
  }

  // ── MutationObserver（メイン）────────────────────────────────────────────
  function startObserver() {
    if (mainObserver) mainObserver.disconnect();
    mainObserver = new MutationObserver(() => {
      if (!isContextValid()) { teardown(); return; }
      // URL変化チェック
      if (location.href !== lastUrl) {
        lastUrl = location.href;
        turnCount = 0;
        warningShown = false;
        _lastUserText = '';
        lastProcessedText = '';
        updateBadge(0);
      }
      if (!isOnChatPage()) return;
      // ターン監視
      const count = countTurns();
      if (count !== turnCount) {
        turnCount = count;
        updateBadge(count);
        if (count >= TURN_LIMIT && !warningShown) showWarning(count);
      }
      // ストリーミング完了debounce
      clearTimeout(streamingTimer);
      streamingTimer = setTimeout(onStreamingStable, 1200);
      // ユーザー入力監視
      processUserInput();
    });
    mainObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  // ── Badge ─────────────────────────────────────────────────────────────────
  function getBadge() {
    if (badge && document.body.contains(badge)) return badge;
    badge = document.createElement('div');
    badge.id = 'relay-badge';
    Object.assign(badge.style, {
      position: 'fixed', bottom: '20px', right: '20px', zIndex: '2147483647',
      background: '#1a1a2e', color: '#e2e8f0',
      fontFamily: 'monospace', fontSize: '12px', fontWeight: 'bold',
      padding: '4px 10px', borderRadius: '12px',
      border: '1.5px solid #334155', cursor: 'pointer', userSelect: 'none',
    });
    badge.addEventListener('click', () => {
      if (confirm(`Relay: 今すぐ引き継ぎますか？`)) triggerHandoff();
    });
    document.body.appendChild(badge);
    return badge;
  }

  function updateBadge(count) {
    const b = getBadge();
    const pct = TURN_LIMIT > 0 ? Math.min(100, Math.round((count / TURN_LIMIT) * 100)) : 0;
    let borderColor = '#10b981', bgColor = '#1a1a2e', textColor = '#e2e8f0';
    if (pct >= 100)     { borderColor = '#ef4444'; bgColor = 'rgba(239,68,68,0.2)'; textColor = '#fca5a5'; }
    else if (pct >= 80) { borderColor = '#f59e0b'; textColor = '#fcd34d'; }
    else if (pct >= 60) { borderColor = '#f97316'; textColor = '#fdba74'; }
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
    loadTodos((todos) => {
      const pending = todos.filter(t => t.status !== '完了').length;
      b.textContent = `Relay · ${count}/${TURN_LIMIT}${pending > 0 ? ` · 📋${pending}` : ''}`;
    });
  }

  // ── Warning popup ─────────────────────────────────────────────────────────
  function showWarning(count) {
    if (warningShown) return;
    warningShown = true;
    const overlay = document.createElement('div');
    overlay.id = 'relay-warning';
    Object.assign(overlay.style, {
      position: 'fixed', inset: '0', zIndex: '999999',
      background: 'rgba(0,0,0,0.6)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    });
    overlay.innerHTML = `
      <div style="background:#0f172a;color:#e2e8f0;border:2px solid #ef4444;
        border-radius:16px;padding:32px;max-width:420px;width:90%;text-align:center;">
        <div style="font-size:32px;margin-bottom:12px">⚡</div>
        <h2 style="margin:0 0 8px;font-size:20px">${count} turns reached</h2>
        <p style="margin:0 0 24px;font-size:14px;color:#94a3b8">
          コンテキストが限界に近づいています。新しいchatに引き継ぎますか？
        </p>
        <div style="display:flex;gap:10px;justify-content:center">
          <button id="relay-btn-continue" style="background:#3b82f6;color:#fff;border:none;
            padding:10px 24px;border-radius:8px;font-size:14px;cursor:pointer;">今すぐ引き継ぎ ↗</button>
          <button id="relay-btn-dismiss" style="background:transparent;color:#64748b;
            border:1px solid #334155;padding:10px 20px;border-radius:8px;font-size:14px;cursor:pointer;">後で</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    document.getElementById('relay-btn-continue').onclick = () => { overlay.remove(); triggerHandoff(); };
    document.getElementById('relay-btn-dismiss').onclick  = () => { overlay.remove(); };
  }

  // ── Toast ─────────────────────────────────────────────────────────────────
  function showToast(msg) {
    const existing = document.getElementById('relay-lb-toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.id = 'relay-lb-toast';
    Object.assign(toast.style, {
      position: 'fixed', bottom: '70px', right: '20px', zIndex: '999998',
      background: '#0f172a', color: '#94a3b8',
      border: '1px solid #1e3a5f',
      fontFamily: '-apple-system,sans-serif', fontSize: '11px',
      padding: '6px 12px', borderRadius: '8px',
      opacity: '0', transition: 'opacity 0.3s', pointerEvents: 'none',
    });
    toast.textContent = msg;
    document.body.appendChild(toast);
    requestAnimationFrame(() => { toast.style.opacity = '1'; });
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }

  // ── injectText ────────────────────────────────────────────────────────────
  function injectText(text) {
    const sels = [
      'div[contenteditable="true"][data-placeholder]',
      'div[contenteditable="true"].ProseMirror',
      'div[contenteditable="true"]',
    ];
    let el = null;
    for (const s of sels) { el = document.querySelector(s); if (el) break; }
    if (!el) return false;
    el.focus();
    try {
      document.execCommand('selectAll', false, null);
      if (document.execCommand('insertText', false, text)) return true;
    } catch (_) {}
    try {
      el.innerText = text;
      el.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true, inputType: 'insertText', data: text }));
      return true;
    } catch (_) {}
    return false;
  }

  // ── Message handler ───────────────────────────────────────────────────────
  if (isContextValid()) {
    chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
      if (!isContextValid()) return;

      if (msg.type === 'RELAY_INJECT') {
        setTimeout(() => injectText(msg.payload.text), 1200);
        return;
      }

      if (msg.type === 'RELAY_MANUAL_HANDOFF') {
        triggerHandoff();
        return;
      }

      if (msg.type === 'RELAY_GET_SUMMARY_FOR_VAULT') {
        const messages = getMessages();
        const lb = extractLogbook(messages);
        const text = [
          lb.decisions.length ? 'Decisions:\n' + lb.decisions.map(d => `• ${d}`).join('\n') : '',
          lb.todos.length     ? 'Next steps:\n' + lb.todos.map(t => `• ${t}`).join('\n') : '',
          lb.insights.length  ? 'Key insights:\n' + lb.insights.map(i => `• ${i}`).join('\n') : ''
        ].filter(Boolean).join('\n\n');
        sendResponse({ text });
        return true;
      }

      // TODO API (popup → background経由で呼ばれる場合のフォールバック)
      if (msg.type === 'RELAY_LB_GET_TODOS') {
        loadTodos((todos) => sendResponse({ todos }));
        return true;
      }

      if (msg.type === 'RELAY_LB_ADD_TODO') {
        loadTodos((todos) => {
          const id = nextTodoId(todos);
          todos.push({
            id, content: msg.content,
            status: '未着手', priority: '中',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            sessionUrl: location.href,
          });
          saveTodosToStorage(todos);
          sendResponse({ ok: true, id });
        });
        return true;
      }

      if (msg.type === 'RELAY_LB_UPDATE_STATUS') {
        loadTodos((todos) => {
          const t = todos.find(x => x.id === msg.id);
          if (t) {
            t.status = msg.status;
            t.updatedAt = new Date().toISOString();
            if (msg.status === '完了') t.completed_at = new Date().toISOString();
            saveTodosToStorage(todos);
            sendResponse({ ok: true });
          } else {
            sendResponse({ ok: false });
          }
        });
        return true;
      }

      if (msg.type === 'RELAY_LB_DELETE_TODO') {
        loadTodos((todos) => {
          saveTodosToStorage(todos.filter(t => t.id !== msg.id));
          sendResponse({ ok: true });
        });
        return true;
      }

      if (msg.type === 'RELAY_LB_COMPLETE_TO_LOG') {
        loadTodos((todos) => {
          const idx = todos.findIndex(t => t.id === msg.id);
          if (idx === -1) { sendResponse({ ok: false }); return; }
          const done = Object.assign({}, todos[idx], { status: '完了', completed_at: new Date().toISOString() });
          todos.splice(idx, 1);
          saveTodosToStorage(todos);
          chrome.storage.local.get('mocka_relay_log', (data) => {
            const log = data.mocka_relay_log || [];
            log.unshift(done);
            chrome.storage.local.set({ mocka_relay_log: log }, () => {
              showToast('✅ ' + done.id + ' 完了 → LOG');
              sendResponse({ ok: true });
            });
          });
        });
        return true;
      }

      if (msg.type === 'RELAY_LB_ARCHIVE_DONE') {
        loadTodos((todos) => {
          const now = new Date().toISOString();
          const done   = todos.filter(t => t.status === '完了').map(t => Object.assign({}, t, { completed_at: t.completed_at || now }));
          const active = todos.filter(t => t.status !== '完了');
          saveTodosToStorage(active);
          chrome.storage.local.get('mocka_relay_log', (data) => {
            const log = data.mocka_relay_log || [];
            chrome.storage.local.set({ mocka_relay_log: done.concat(log) }, () => {
              showToast('✅ ' + done.length + '件をLOGへ');
              sendResponse({ ok: true, count: done.length });
            });
          });
        });
        return true;
      }
    });
  }

  // ── autosave hooks ────────────────────────────────────────────────────────
  window.addEventListener('beforeunload', () => autoSave());
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) autoSave();
  });

  // ── init ──────────────────────────────────────────────────────────────────
  if (isOnChatPage()) {
    turnCount = countTurns();
    updateBadge(turnCount);
    startObserver();
  }

  let _lastPath = location.pathname;
  intervalId = setInterval(() => {
    if (!isContextValid()) { teardown(); return; }
    // 定期autosave (30秒)
    autoSave();
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
  }, 30000);

})();
