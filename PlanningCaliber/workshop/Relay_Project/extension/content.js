/**
 * Relay for Claude — content.js v3.0
 * Add: Logbook TODO Engine
 *   - ユーザー発言から自然語でTODO自動抽出・LB_NNN番号付き管理
 *   - 「LB_001完了」「001終わった」でステータス更新
 *   - セッション跨いでlocalStorage永続化
 *   - 次セッション冒頭に未着手TODO自動注入
 * v2.5: getMessages() のassistant取得を .font-claude-response + textContent に修正
 * v2.4: RELAY_GET_SUMMARY_FOR_VAULT が sendResponse/return true を欠いていたバグ修正
 * Fix: Extension context invalidated — B案根本解決
 */

(function() {
  'use strict';

  let TURN_LIMIT = 20;
  let warningShown = false;
  let badge = null;
  let turnCount = 0;
  let lastUrl = location.href;
  let observer = null;
  let intervalId = null;
  let contextAlive = true;

  // ── コンテキスト有効チェック ──────────────────────────────────────────────
  function isContextValid() {
    try {
      return !!(chrome && chrome.runtime && chrome.runtime.id);
    } catch (_) {
      return false;
    }
  }

  function teardown() {
    contextAlive = false;
    if (observer) { observer.disconnect(); observer = null; }
    if (intervalId) { clearInterval(intervalId); intervalId = null; }
    if (badge && badge.parentNode) { badge.remove(); badge = null; }
  }

  // ── Load prefs ─────────────────────────────────────────────────────────────
  if (isContextValid()) {
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = (result && result.mocka_global_prefs) || {};
      TURN_LIMIT = prefs.turnLimit || 20;
    });
  }

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

  function getMessages() {
    var userNodes = Array.prototype.slice.call(document.querySelectorAll('[data-testid="user-message"]'));
    var assistantNodes = Array.prototype.slice.call(document.querySelectorAll('.font-claude-response'));
    if (!userNodes.length) return [];

    var messages = [];
    userNodes.forEach(function(node, i) {
      var text = node.textContent ? node.textContent.trim() : '';
      if (!text) return;
      messages.push({ role: 'user', text: text, turn: i * 2 + 1 });

      var assistantEl = assistantNodes[i];
      if (assistantEl) {
        var assistantText = assistantEl.textContent ? assistantEl.textContent.trim() : '';
        if (assistantText) {
          messages.push({ role: 'assistant', text: assistantText.slice(0, 500), turn: i * 2 + 2 });
        }
      }
    });
    return messages;
  }

  function isOnChatPage() {
    return /claude\.ai\/(chat|new)/.test(location.href);
  }

  // ════════════════════════════════════════════════════════════════════════════
  // ██ LOGBOOK TODO ENGINE v1.0
  // ════════════════════════════════════════════════════════════════════════════

  const LB_STORAGE_KEY = 'relay_logbook_todos';

  // TODOパターン（日英）
  const TODO_PATTERNS = [
    // 日本語
    /(?:^|[。\n])\s*(?:TODO[：:]?\s*|・|→\s*|次[はに]?[：:]?\s*|やること[：:]?\s*|対応[：:]?\s*|実装[：:]?\s*|確認[：:]?\s*)(.{5,80})(?=[。\n！？!?]|$)/gi,
    /(.{5,80})(?:してください|する予定|しておく|しておいて|実装する|対応する|確認する|作成する|修正する|追加する)(?=[。\n]|$)/gi,
    // 英語
    /(?:^|[\.\n])\s*(?:TODO[：:]?\s*|[-•→]\s*|Next[：:]?\s*|Need to[：:]?\s*|Should[：:]?\s*)(.{5,80})(?=[.\n!?]|$)/gi,
  ];

  // ステータス更新コマンドパターン
  const STATUS_PATTERNS = [
    // 完了：「LB_001完了」「001終わった」「LB_003 done」
    { re: /(?:LB[_-]?)?(\d{3})\s*(?:完了|終わった|done|finished|完成|済み|ok)/gi, status: '完了' },
    // 進行中：「LB_002進行中」「002やってる」
    { re: /(?:LB[_-]?)?(\d{3})\s*(?:進行中|やってる|作業中|対応中|in progress|wip)/gi, status: '進行中' },
    // 未着手に戻す
    { re: /(?:LB[_-]?)?(\d{3})\s*(?:未着手|戻す|キャンセル|cancel|undo)/gi, status: '未着手' },
  ];

  // localStorage からTODOリストを取得
  function lbLoad() {
    try {
      const raw = localStorage.getItem(LB_STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (_) {
      return [];
    }
  }

  // localStorageに保存
  function lbSave(todos) {
    try {
      localStorage.setItem(LB_STORAGE_KEY, JSON.stringify(todos));
    } catch (_) {}
  }

  // 次のLB番号を採番
  function lbNextId(todos) {
    if (!todos.length) return 'LB_001';
    const nums = todos.map(t => parseInt(t.id.replace('LB_', ''), 10)).filter(n => !isNaN(n));
    const next = Math.max(...nums) + 1;
    return 'LB_' + String(next).padStart(3, '0');
  }

  // テキストからTODO候補を抽出
  function extractTodoCandidates(text) {
    const candidates = new Set();

    // パターンマッチ
    TODO_PATTERNS.forEach(pat => {
      pat.lastIndex = 0;
      let m;
      while ((m = pat.exec(text)) !== null) {
        const candidate = (m[1] || m[0]).trim().replace(/[。！？!?\n]+$/, '').trim();
        if (candidate.length >= 5 && candidate.length <= 100) {
          candidates.add(candidate);
        }
      }
    });

    // 行頭の箇条書きパターン
    text.split('\n').forEach(line => {
      const trimmed = line.trim();
      const bulletMatch = trimmed.match(/^(?:[-•✓→]\s*|(?:TODO|todo)[：:]\s*|(?:\d+[.)]\s*))(.{5,100})$/);
      if (bulletMatch) {
        candidates.add(bulletMatch[1].trim());
      }
    });

    return [...candidates];
  }

  // ユーザー発言からステータス更新コマンドを検出して処理
  function processStatusCommands(text) {
    const todos = lbLoad();
    let updated = false;

    STATUS_PATTERNS.forEach(({ re, status }) => {
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(text)) !== null) {
        const num = parseInt(m[1], 10);
        const id = 'LB_' + String(num).padStart(3, '0');
        const todo = todos.find(t => t.id === id);
        if (todo && todo.status !== status) {
          todo.status = status;
          todo.updatedAt = new Date().toISOString();
          updated = true;
        }
      }
    });

    if (updated) {
      lbSave(todos);
      showLbToast('✓ TODOステータスを更新しました');
    }
    return updated;
  }

  // 新しいTODOを追加（重複チェックあり）
  function addTodos(candidates) {
    const todos = lbLoad();
    const existing = todos.map(t => t.content.toLowerCase());
    let added = 0;

    candidates.forEach(content => {
      if (existing.includes(content.toLowerCase())) return;
      const id = lbNextId(todos);
      todos.push({
        id,
        content,
        status: '未着手',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        sessionUrl: location.href,
      });
      existing.push(content.toLowerCase());
      added++;
    });

    if (added > 0) lbSave(todos);
    return added;
  }

  // 未着手TODOのサマリー文字列を生成
  function buildTodoSummary() {
    const todos = lbLoad();
    const pending = todos.filter(t => t.status === '未着手');
    const inProgress = todos.filter(t => t.status === '進行中');

    if (!pending.length && !inProgress.length) return '';

    const lines = ['[Logbook — 前回からの積み残し]'];
    if (inProgress.length) {
      lines.push('📌 進行中:');
      inProgress.forEach(t => lines.push(`  ${t.id}: ${t.content}`));
    }
    if (pending.length) {
      lines.push('📋 未着手:');
      pending.slice(0, 10).forEach(t => lines.push(`  ${t.id}: ${t.content}`));
      if (pending.length > 10) lines.push(`  ... 他${pending.length - 10}件`);
    }
    return lines.join('\n');
  }

  // ユーザーが送信したテキストを監視してTODO処理
  let _lastUserText = '';
  function monitorUserInput() {
    const userNodes = document.querySelectorAll('[data-testid="user-message"]');
    if (!userNodes.length) return;
    const lastNode = userNodes[userNodes.length - 1];
    const text = lastNode.textContent.trim();
    if (!text || text === _lastUserText) return;
    _lastUserText = text;

    // ステータス更新コマンドを先に処理
    const hasCommand = processStatusCommands(text);

    // TODO候補を抽出して追加（コマンド行でなければ）
    if (!hasCommand) {
      const candidates = extractTodoCandidates(text);
      if (candidates.length > 0) {
        const added = addTodos(candidates);
        if (added > 0) {
          showLbToast(`📋 TODO ${added}件を記録しました`);
        }
      }
    }
  }

  // トースト通知
  function showLbToast(msg) {
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
      opacity: '0', transition: 'opacity 0.3s',
      pointerEvents: 'none',
    });
    toast.textContent = msg;
    document.body.appendChild(toast);
    requestAnimationFrame(() => { toast.style.opacity = '1'; });
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }

  // ════════════════════════════════════════════════════════════════════════════
  // 以下 既存ロジック（extractLogbook / generateSummary / injectText / etc.）
  // ════════════════════════════════════════════════════════════════════════════

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

  function generateSummary(messages, vaultContext) {
    const userMsgs = messages.filter(m => m.role === 'user');
    const lastMsg = userMsgs[userMsgs.length - 1];
    const last = (lastMsg && lastMsg.text && lastMsg.text.slice(0, 200)) || '';
    const count = messages.length;
    const logbook = extractLogbook(messages);

    const parts = [`[Relay — continuing from ${count} turns]`];

    // ★ Logbook TODO注入（新機能）
    const todoSummary = buildTodoSummary();
    if (todoSummary) {
      parts.push(todoSummary);
    }

    if (vaultContext) {
      parts.push(`[Vault context]\n${vaultContext}`);
    }
    if (logbook.decisions.length) {
      parts.push(`Decisions:\n${logbook.decisions.map(d => `• ${d}`).join('\n')}`);
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
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      nativeSetter.call(el, text);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }

    try {
      el.focus();
      document.execCommand('selectAll', false, null);
      const ok = document.execCommand('insertText', false, text);
      if (ok && el.innerText.trim() === text.trim()) {
        el.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
      }
    } catch (_) {}

    try {
      el.focus();
      el.innerText = text;
      el.dispatchEvent(new InputEvent('input', {
        bubbles: true, cancelable: true, inputType: 'insertText', data: text
      }));
      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(el);
      range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
      return true;
    } catch (_) {}

    try {
      navigator.clipboard.writeText(text).then(() => {
        el.focus();
        document.execCommand('paste');
      });
      return true;
    } catch (_) {}

    return false;
  }

  function getVaultContext(callback) {
    if (!isContextValid()) return callback(null);
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      if (!isContextValid()) return callback(null);
      const prefs = (result && result.mocka_global_prefs) || {};
      const isProUser = !!prefs.vaultEnabled;
      if (!isProUser) return callback(null);

      chrome.runtime.sendMessage({ type: 'RELAY_GET_VAULT_CONTEXT' }, (res) => {
        callback((res && res.context) || null);
      });
    });
  }

  function triggerHandoff() {
    if (!isContextValid()) return;

    const messages = getMessages();
    const title = (document.title && document.title.replace(' - Claude', '').trim()) || 'Untitled';
    const logbook = extractLogbook(messages);

    chrome.runtime.sendMessage({
      type: 'RELAY_SAVE_SESSION',
      payload: { title, url: location.href, messages, logbook }
    });

    getVaultContext((vaultContext) => {
      if (!isContextValid()) return;
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

    // TODO件数をバッジに追加表示
    const todos = lbLoad();
    const pendingCount = todos.filter(t => t.status !== '完了').length;
    const todoLabel = pendingCount > 0 ? ` · 📋${pendingCount}` : '';
    b.textContent = `Relay · ${count}/${TURN_LIMIT}${todoLabel}`;
  }

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

  function checkUrlChange() {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      turnCount = 0;
      warningShown = false;
      _lastUserText = '';
      updateBadge(0);
    }
  }

  function startObserver() {
    if (observer) observer.disconnect();
    observer = new MutationObserver(() => {
      if (!isContextValid()) { teardown(); return; }
      checkUrlChange();
      if (!isOnChatPage()) return;
      const count = countTurns();
      if (count !== turnCount) {
        turnCount = count;
        updateBadge(count);
        if (count >= TURN_LIMIT && !warningShown) showWarning(count);
      }
      // ★ ユーザー発言監視（TODO抽出）
      monitorUserInput();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  // ── Message handler ────────────────────────────────────────────────────────
  if (isContextValid()) {
    chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
      if (!isContextValid()) return;

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
        sendResponse({ text });
        return true;
      }

      // ★ Logbook TODO API
      if (msg.type === 'RELAY_LB_GET_TODOS') {
        sendResponse({ todos: lbLoad() });
        return true;
      }

      if (msg.type === 'RELAY_LB_UPDATE_STATUS') {
        const todos = lbLoad();
        const todo = todos.find(t => t.id === msg.id);
        if (todo) {
          todo.status = msg.status;
          todo.updatedAt = new Date().toISOString();
          lbSave(todos);
          sendResponse({ ok: true });
        } else {
          sendResponse({ ok: false, error: 'not found' });
        }
        return true;
      }

      if (msg.type === 'RELAY_LB_ADD_TODO') {
        const todos = lbLoad();
        const id = lbNextId(todos);
        todos.push({
          id,
          content: msg.content,
          status: '未着手',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          sessionUrl: location.href,
        });
        lbSave(todos);
        sendResponse({ ok: true, id });
        return true;
      }

      if (msg.type === 'RELAY_LB_DELETE_TODO') {
        const todos = lbLoad().filter(t => t.id !== msg.id);
        lbSave(todos);
        sendResponse({ ok: true });
        return true;
      }

      if (msg.type === 'RELAY_LB_CLEAR_DONE') {
        const todos = lbLoad().filter(t => t.status !== '完了');
        lbSave(todos);
        sendResponse({ ok: true });
        return true;
      }
    });
  }

  // ── Init ───────────────────────────────────────────────────────────────────
  if (isOnChatPage()) {
    turnCount = countTurns();
    updateBadge(turnCount);
    startObserver();
  }

  let _lastPath = location.pathname;
  intervalId = setInterval(() => {
    if (!isContextValid()) { teardown(); return; }

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
