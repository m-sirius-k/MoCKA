/**
 * Relay for Claude — relay-main.js v4.0
 * GPT設計通りに完全書き直し
 * - localStorage廃止 → chrome.storage.local統一
 * - debounce observer 1200ms (streaming完了検知)
 * - autosave: beforeunload / visibilitychange / 60秒定期
 * - popup → background直通信 (content script依存排除)
 * - content scriptは「DOM収集専用」に縮退
 */
(() => {
  'use strict';

  // ─── 多重起動防止 ─────────────────────────────────────────────────────────
  if (window.__RELAY_MAIN_LOADED__) return;
  window.__RELAY_MAIN_LOADED__ = true;

  // ─── 設定 ─────────────────────────────────────────────────────────────────
  const TURN_LIMIT        = 20;
  const STREAM_IDLE_MS    = 1200;  // streaming完了判定
  const AUTOSAVE_INTERVAL = 60000; // 60秒定期保存
  const BADGE_UPDATE_MS   = 3000;  // バッジ更新間隔

  // ─── 状態 ─────────────────────────────────────────────────────────────────
  let turnCount         = 0;
  let lastAssistantText = '';
  let lastSavedHash     = '';
  let streamTimer       = null;
  let badgeTimer        = null;
  let warningShown      = false;
  let sessionId         = crypto.randomUUID();
  let messages          = [];

  // ─── セレクター ────────────────────────────────────────────────────────────
  function getAssistantEl() {
    return (
      document.querySelector('[data-is-streaming="false"] .font-claude-message') ||
      document.querySelector('.font-claude-message') ||
      document.querySelector('[class*="prose"]') ||
      null
    );
  }

  function getInputEl() {
    return (
      document.querySelector('div[contenteditable="true"][data-testid]') ||
      document.querySelector('div[contenteditable="true"]') ||
      null
    );
  }

  function countTurns() {
    const els = document.querySelectorAll(
      '[data-testid*="human-turn"], [data-testid*="assistant-turn"], ' +
      '.font-user-message, .font-claude-message'
    );
    return Math.floor(els.length / 2);
  }

  // ─── ハッシュ (重複保存防止) ───────────────────────────────────────────────
  function simpleHash(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) {
      h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
    }
    return String(h);
  }

  // ─── TODO抽出 ─────────────────────────────────────────────────────────────
  function extractTodos(text) {
    if (!text) return [];
    const lines = text.split('\n');
    const todos = [];
    const todoPattern = /^[\s\-\*\d\.]*(\[RELAY_TODO\]|TODO[:\s]|次[のに]|確認|修正|実装|追加|対応|fix[:\s]|add[:\s])/i;

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.length < 8) return;
      if (/^```|^\s*[{};=>]|function |const |let |var |return /.test(trimmed)) return;
      if (trimmed.match(todoPattern) || trimmed.startsWith('[RELAY_TODO]')) {
        const content = trimmed.replace(/^\[RELAY_TODO\]\s*/, '').replace(/^[\-\*\d\.]+\s*/, '').trim();
        if (content.length >= 8) {
          todos.push(content);
        }
      }
    });
    return todos.slice(0, 5);
  }

  // ─── chrome.storage.local へ保存 ──────────────────────────────────────────
  function saveTodos(todos) {
    if (!todos.length) return;
    chrome.runtime.sendMessage({ type: 'RELAY_GET_STATS' }, (stats) => {
      // 既存TODOを取得してマージ
      chrome.storage.local.get('relay_todos', (data) => {
        const existing = data.relay_todos || [];
        const existingContents = new Set(existing.map(t => t.content));
        const newTodos = todos
          .filter(c => !existingContents.has(c))
          .map((content, i) => {
            const nums = existing.map(t => parseInt((t.id || '').replace('LB_', ''), 10)).filter(n => !isNaN(n));
            const nextNum = nums.length ? Math.max(...nums) + i + 1 : existing.length + i + 1;
            return {
              id:        'LB_' + String(nextNum).padStart(3, '0'),
              content,
              status:    '未着手',
              priority:  '中',
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              sessionId
            };
          });
        if (newTodos.length) {
          chrome.storage.local.set({ relay_todos: [...existing, ...newTodos] });
        }
      });
    });
  }

  // ─── autosave ─────────────────────────────────────────────────────────────
  function buildSessionData() {
    return {
      title:    document.title || 'Untitled',
      url:      location.href,
      messages,
      turns:    turnCount,
      sessionId
    };
  }

  function autoSave() {
    const data = buildSessionData();
    const hash = simpleHash(JSON.stringify(data));
    if (hash === lastSavedHash) return;
    if (!messages.length) return;
    lastSavedHash = hash;
    chrome.runtime.sendMessage({ type: 'RELAY_SAVE_SESSION', payload: data });
  }

  // ─── バッジ更新 ────────────────────────────────────────────────────────────
  function refreshBadge() {
    if (typeof chrome === 'undefined' || !chrome.storage) return;
    chrome.storage.local.get('relay_todos', (data) => {
      const todos  = (data.relay_todos || []).filter(t => t.status !== '完了');
      const count  = todos.length;
      const pct    = TURN_LIMIT > 0 ? turnCount / TURN_LIMIT : 0;

      let color = '#22c55e'; // 緑
      if (pct >= 0.8)       color = '#ef4444'; // 赤
      else if (pct >= 0.5)  color = '#f97316'; // オレンジ

      // バッジ要素
      let badge = document.getElementById('__relay_badge__');
      if (!badge) {
        badge = document.createElement('div');
        badge.id = '__relay_badge__';
        Object.assign(badge.style, {
          position:     'fixed',
          bottom:       '16px',
          right:        '16px',
          zIndex:       '2147483647',
          background:   '#0d0d1a',
          border:       '1.5px solid ' + color,
          borderRadius: '20px',
          padding:      '4px 12px',
          fontFamily:   'monospace',
          fontSize:     '12px',
          fontWeight:   'bold',
          color:        color,
          cursor:       'pointer',
          boxShadow:    '0 2px 8px rgba(0,0,0,0.4)',
          transition:   'border-color 0.3s, color 0.3s',
          userSelect:   'none',
        });
        badge.addEventListener('click', triggerHandoff);
        document.body.appendChild(badge);
      }

      badge.style.borderColor = color;
      badge.style.color       = color;
      badge.textContent       = count > 0
        ? `${turnCount}/${TURN_LIMIT} 📋${count}`
        : `${turnCount}/${TURN_LIMIT}`;

      // 80%超で点滅
      if (pct >= 0.8) {
        badge.style.animation = 'relay-blink 1s step-end infinite';
        if (!document.getElementById('__relay_blink_style__')) {
          const s = document.createElement('style');
          s.id = '__relay_blink_style__';
          s.textContent = '@keyframes relay-blink{0%,100%{opacity:1}50%{opacity:0.3}}';
          document.head.appendChild(s);
        }
      } else {
        badge.style.animation = '';
      }
    });
  }

  // ─── 引き継ぎポップアップ ──────────────────────────────────────────────────
  function showHandoffPopup() {
    if (document.getElementById('__relay_popup__')) return;

    chrome.storage.local.get('relay_todos', (data) => {
      const open = (data.relay_todos || []).filter(t => t.status !== '完了');
      let todoPart = '';
      if (open.length) {
        todoPart = `<div style="font-size:11px;color:#888;margin:8px 0 4px">未完了TODO:</div>
          <div style="font-size:12px;background:#1a1a2e;border:1px solid #333;border-radius:6px;
                      padding:8px;max-height:80px;overflow-y:auto;line-height:1.6">
            ${open.slice(0, 3).map(t => `• ${t.content}`).join('<br>')}
            ${open.length > 3 ? `<br>他 ${open.length - 3} 件` : ''}
          </div>`;
      }

      const popup = document.createElement('div');
      popup.id = '__relay_popup__';
      Object.assign(popup.style, {
        position:     'fixed',
        bottom:       '60px',
        right:        '20px',
        zIndex:       '2147483647',
        background:   '#0d0d1a',
        border:       '1.5px solid #e2c97e',
        borderRadius: '12px',
        padding:      '16px',
        width:        '260px',
        fontFamily:   'monospace',
        boxShadow:    '0 4px 20px rgba(0,0,0,0.5)',
      });
      popup.innerHTML = `
        <div style="color:#e2c97e;font-size:13px;font-weight:bold;margin-bottom:6px">
          ⚡ Relay: ${turnCount}ターンに達しました
        </div>
        <div style="color:#94a3b8;font-size:11px;line-height:1.6;margin-bottom:8px">
          新しいチャットへ引き継ぐことを推奨します。
        </div>
        ${todoPart}
        <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:12px">
          <button id="__relay_dismiss__"
            style="background:none;border:1px solid #555;color:#888;border-radius:6px;
                   padding:6px 14px;cursor:pointer;font-size:12px">後で</button>
          <button id="__relay_handoff__"
            style="background:#e2c97e;border:none;color:#0d0d1a;border-radius:6px;
                   padding:6px 14px;cursor:pointer;font-size:12px;font-weight:bold">
            新しいチャットへ →
          </button>
        </div>`;
      document.body.appendChild(popup);

      document.getElementById('__relay_dismiss__')?.addEventListener('click', () => {
        popup.remove(); warningShown = true;
      });
      document.getElementById('__relay_handoff__')?.addEventListener('click', () => {
        popup.remove(); warningShown = true; triggerHandoff();
      });
    });
  }

  // ─── 引き継ぎ実行 ──────────────────────────────────────────────────────────
  function triggerHandoff() {
    autoSave();
    chrome.storage.local.get('relay_todos', (data) => {
      const open = (data.relay_todos || []).filter(t => t.status !== '完了');
      const lines = ['[Relay 引き継ぎ]', `セッション: ${sessionId}`, `ターン数: ${turnCount}`];
      if (open.length) {
        lines.push('', '未完了TODO:');
        open.slice(0, 5).forEach(t => lines.push(`- ${t.content}`));
      }
      const text = lines.join('\n');
      chrome.runtime.sendMessage({ type: 'RELAY_OPEN_NEW_CHAT', payload: { text } });
    });
  }

  // ─── streaming完了検知 (debounce) ─────────────────────────────────────────
  function onStreamingStable() {
    const el = getAssistantEl();
    if (!el) return;
    const text = el.innerText?.trim() || '';
    if (!text || text === lastAssistantText) return;
    lastAssistantText = text;

    // メッセージ記録
    messages.push({ role: 'assistant', content: text.slice(0, 2000), ts: Date.now() });
    if (messages.length > 200) messages.splice(0, messages.length - 200);

    // TODO抽出 → chrome.storage.local保存
    const todos = extractTodos(text);
    if (todos.length) saveTodos(todos);

    // ターン数更新
    const newTurn = countTurns();
    if (newTurn !== turnCount) {
      turnCount = newTurn;
      refreshBadge();
      if (turnCount >= TURN_LIMIT && !warningShown) {
        showHandoffPopup();
      }
    }

    // autosave
    autoSave();
  }

  // ─── MutationObserver ─────────────────────────────────────────────────────
  const observer = new MutationObserver(() => {
    clearTimeout(streamTimer);
    streamTimer = setTimeout(onStreamingStable, STREAM_IDLE_MS);
  });

  observer.observe(document.body, {
    childList:     true,
    subtree:       true,
    characterData: true
  });

  // ─── autosave トリガー ─────────────────────────────────────────────────────
  window.addEventListener('beforeunload', autoSave);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') autoSave();
  });
  setInterval(autoSave, AUTOSAVE_INTERVAL);

  // ─── バッジ定期更新 ────────────────────────────────────────────────────────
  setInterval(refreshBadge, BADGE_UPDATE_MS);

  // ─── メッセージ受信 (background / popup から) ─────────────────────────────
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {

    if (msg.type === 'RELAY_MANUAL_HANDOFF') {
      triggerHandoff();
      sendResponse({ ok: true });
      return true;
    }

    if (msg.type === 'RELAY_INJECT') {
      const input = getInputEl();
      if (!input) { sendResponse({ ok: false, error: 'no_input' }); return true; }
      input.focus();
      document.execCommand('selectAll');
      document.execCommand('insertText', false, msg.payload?.text || '');
      sendResponse({ ok: true });
      return true;
    }

    if (msg.type === 'RELAY_GET_SUMMARY_FOR_VAULT') {
      const lines = [`セッション: ${sessionId}`, `ターン数: ${turnCount}`, `URL: ${location.href}`];
      if (messages.length) {
        lines.push('', '直近のやりとり:');
        messages.slice(-3).forEach(m => lines.push(`[${m.role}] ${m.content.slice(0, 200)}`));
      }
      sendResponse({ text: lines.join('\n'), title: document.title });
      return true;
    }

    if (msg.type === 'RELAY_LB_COMPLETE_TO_LOG') {
      chrome.storage.local.get(['relay_todos', 'mocka_relay_log'], (data) => {
        let todos = data.relay_todos || [];
        const log = data.mocka_relay_log || [];
        const idx = todos.findIndex(t => t.id === msg.id);
        if (idx !== -1) {
          const done = { ...todos[idx], status: '完了', completed_at: new Date().toISOString() };
          todos.splice(idx, 1);
          log.unshift(done);
          chrome.storage.local.set({ relay_todos: todos, mocka_relay_log: log });
        }
        sendResponse({ ok: true });
      });
      return true;
    }

    if (msg.type === 'RELAY_LB_UPDATE_STATUS') {
      chrome.storage.local.get('relay_todos', (data) => {
        const todos = data.relay_todos || [];
        const t = todos.find(x => x.id === msg.id);
        if (t) { t.status = msg.status; t.updatedAt = new Date().toISOString(); }
        chrome.storage.local.set({ relay_todos: todos });
        sendResponse({ ok: true });
      });
      return true;
    }

    if (msg.type === 'RELAY_LB_DELETE') {
      chrome.storage.local.get('relay_todos', (data) => {
        const todos = (data.relay_todos || []).filter(t => t.id !== msg.id);
        chrome.storage.local.set({ relay_todos: todos });
        sendResponse({ ok: true });
      });
      return true;
    }

    return false;
  });

  // ─── 起動完了 ─────────────────────────────────────────────────────────────
  refreshBadge();
  console.info('[Relay] relay-main.js v4.0 started. session:', sessionId);

})();
