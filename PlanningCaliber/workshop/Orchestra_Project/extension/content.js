window.__orchestra_loaded = true;
console.log("[Orchestra] content.js loaded");
// AI Conversation Logger - content.js
// Monitors claude.ai DOM and captures messages

(function () {
  'use strict';

  const SERVICE = 'claude.ai';
  let sessionId = generateSessionId();
  let capturedIds = new Set();
  let lastUrl = location.href;

  // ── ストリーミング中テキストのプレフィックス（除外対象）──────────────────
  // Claudeのtool use / thinking表示がcontentに混入するパターン
  const STREAMING_PREFIXES = [
    'VConnecting',
    'Vread_me',
    'Vvisualiz',
    'Loading...',
    'Ran ',           // "Ran 3 commands..."
    'Read ',          // "Read N files..."
    'Viewed ',
    'Created ',
    'Wrote ',
    'Executed ',
  ];

  function isStreamingArtifact(text) {
    return STREAMING_PREFIXES.some(p => text.startsWith(p));
  }

  function generateSessionId() {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  }

  // IDはtextの末尾80文字でハッシュ → ストリーミング途中と完成で同じIDになる
  // （先頭はツール状態が変わるが末尾の実コンテンツは安定している）
  function generateMessageId(role, text) {
    const safeRole = role || '';
    const safeText = text || '';
    const stable   = safeText.slice(-80); // ★ 末尾80文字を使用（旧: 先頭80文字）
    const hash = btoa(encodeURIComponent(safeRole + stable)).slice(0, 16);
    return 'msg_' + hash;
  }

  // ── ストリーミング完了検知 ──────────────────────────────────────────────
  // Claude.aiはストリーミング完了後に streaming 属性 / stop-button が消える
  function isStreaming() {
    // 送信中ボタン（Stop generating）が存在する場合はストリーミング中
    const stopBtn = document.querySelector(
      'button[aria-label="Stop"], button[data-testid="stop-button"], [data-testid="input-menu-stop"]'
    );
    return !!stopBtn;
  }

  // Extract all visible messages from the DOM
  function extractMessages() {
    const messages = [];

    // User messages
    document.querySelectorAll('[data-testid="user-message"]').forEach((el) => {
      const text = el.textContent?.trim();
      if (!text) return;
      messages.push({ role: 'user', text });
    });

    // Assistant messages
    const assistantBlocks = document.querySelectorAll('div.group.relative.pb-3');
    assistantBlocks.forEach((el) => {
      const text = el.textContent?.trim();
      if (!text) return;
      messages.push({ role: 'assistant', text });
    });

    // Fallback
    if (messages.length === 0) {
      const turns = document.querySelectorAll(
        '[class*="conversation-turn"], [class*="human-turn"], [class*="ai-turn"]'
      );
      turns.forEach((turn) => {
        const isHuman =
          turn.className.includes('human') ||
          turn.querySelector('[class*="human"]');
        const text = turn.innerText?.trim();
        if (text) {
          messages.push({ role: isHuman ? 'user' : 'assistant', text });
        }
      });
    }

    return messages;
  }

  // Send with retry
  function sendWithRetry(record, retries = 3) {
    try {
      chrome.runtime.sendMessage({ type: 'SAVE_MESSAGE', payload: record }, (response) => {
        if (chrome.runtime.lastError) {
          console.warn('[Orchestra] SW dead, retry...', chrome.runtime.lastError.message);
          if (retries > 0) {
            setTimeout(() => sendWithRetry(record, retries - 1), 1000);
          }
        }
      });
    } catch (e) {
      if (retries > 0) {
        setTimeout(() => sendWithRetry(record, retries - 1), 1000);
      }
    }
  }

  function saveNewMessages(messages) {
    messages.forEach((msg) => {
      // ★ ストリーミング中artifact除外
      if (isStreamingArtifact(msg.text)) return;

      const id = generateMessageId(msg.role, msg.text);
      if (capturedIds.has(id)) return;
      capturedIds.add(id);

      const record = {
        id,
        service: SERVICE,
        role: msg.role,
        content: msg.text,
        timestamp: new Date().toISOString(),
        session_id: sessionId,
        url: location.href,
      };

      sendWithRetry(record);
    });
  }

  // ── スキャン：ストリーミング中は実行しない ──────────────────────────────
  let scanTimer = null;

  function scheduleScan() {
    // ストリーミング中はキャンセル → 完了後500ms待って実行
    if (scanTimer) clearTimeout(scanTimer);
    scanTimer = setTimeout(() => {
      if (!isStreaming()) {
        const messages = extractMessages();
        if (messages.length > 0) saveNewMessages(messages);
      }
    }, 500);
  }

  function checkUrlChange() {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      sessionId = generateSessionId();
      capturedIds.clear();
      setTimeout(scheduleScan, 1000);
    }
  }

  // MutationObserver
  const observer = new MutationObserver(() => {
    checkUrlChange();
    scheduleScan();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: false,
  });

  // Initial scan
  setTimeout(scheduleScan, 2000);

  // Periodic scan (safety net)
  setInterval(() => {
    checkUrlChange();
    if (!isStreaming()) scheduleScan();
  }, 5000);

  // Keep Service Worker alive
  function pingServiceWorker() {
    try {
      chrome.runtime.sendMessage({ type: 'PING' }, (res) => {
        if (chrome.runtime.lastError) {
          setTimeout(pingServiceWorker, 1000);
        }
      });
    } catch(e) {
      setTimeout(pingServiceWorker, 1000);
    }
  }
  setInterval(pingServiceWorker, 5000);
  pingServiceWorker();

  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'GET_SESSION') {
      sendResponse({ sessionId, capturedCount: capturedIds.size });
    }
  });
})();
// ─── Drag Support ────────────────────────────────────────────────────────────
function makeDraggable(el, storageKey, defaultRight, defaultBottom) {
  if (typeof chrome === 'undefined' || !chrome.storage) return;
  chrome.storage.local.get(storageKey, (r) => {
    const pos = r[storageKey];
    if (pos) {
      el.style.left = pos.left + 'px'; el.style.top = pos.top + 'px';
      el.style.right = 'auto'; el.style.bottom = 'auto';
    }
  });
  let isDragging = false, startX, startY, startLeft, startTop;
  el.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    isDragging = false;
    const rect = el.getBoundingClientRect();
    startX = e.clientX; startY = e.clientY;
    startLeft = rect.left; startTop = rect.top;
    el.style.left = startLeft + 'px'; el.style.top = startTop + 'px';
    el.style.right = 'auto'; el.style.bottom = 'auto';
    const onMove = (e) => {
      const dx = e.clientX - startX, dy = e.clientY - startY;
      if (Math.abs(dx) > 5 || Math.abs(dy) > 5) isDragging = true;
      if (isDragging) {
        el.style.left = Math.max(0, Math.min(window.innerWidth  - el.offsetWidth,  startLeft + dx)) + 'px';
        el.style.top  = Math.max(0, Math.min(window.innerHeight - el.offsetHeight, startTop  + dy)) + 'px';
      }
    };
    const onUp = () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      if (isDragging) chrome.storage.local.set({ [storageKey]: { left: parseInt(el.style.left), top: parseInt(el.style.top) } });
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
    e.preventDefault();
  });
  el.addEventListener('click', (e) => { if (isDragging) { e.stopImmediatePropagation(); isDragging = false; } }, true);
  el.style.cursor = 'grab';
}

// ── Orchestra: Status panel & synthesis (Pro/One) ─────────────────────────────
// Handles status panel display and response synthesis for Share/Deliberate

(function () {
  'use strict';

  // ── Incoming messages from background ──────────────────────────────────────

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === 'ORCHESTRA_STARTED') {
      showStatusPanel(msg.targets || [], msg.mode || 'deliberation');
      sendResponse({ ok: true });
    }

    if (msg.type === 'ORCHESTRA_AI_DONE') {
      markAiDone(msg.ai);
      sendResponse({ ok: true });
    }

    if (msg.type === 'ORCHESTRA_SYNTHESIZE') {
      injectSynthesisPrompt(msg.prompt);
      sendResponse({ ok: true });
    }
  });

  // ── Status panel ────────────────────────────────────────────────────────────

  let _statusTimers = {};
  let _statusStart  = {};
  let _statusMode   = 'deliberation';

  function showStatusPanel(targets, mode) {
    removeStatusPanel();
    _statusMode   = mode || 'deliberation';
    _statusTimers = {};
    _statusStart  = {};

    const isCollab  = _statusMode === 'collaboration';
    const modeLabel = isCollab ? '🤝 Share' : '💬 Deliberate';
    const mainColor = isCollab ? '#4fc3f7' : '#e0c070';
    const borderCol = isCollab ? '#2a7fa0' : '#e0c070';

    const panel = document.createElement('div');
    panel.id = 'orchestra-status-panel';
    panel.style.cssText = [
      'position:fixed', 'bottom:80px', 'right:16px', 'z-index:8900',
      'background:#0d0d1a', `border:1px solid ${borderCol}`,
      'border-radius:10px', 'padding:14px 18px', 'color:#e8e8ec',
      'font-family:-apple-system,BlinkMacSystemFont,sans-serif',
      'font-size:12px', 'min-width:240px', 'max-width:300px',
      'box-shadow:0 6px 30px rgba(0,0,0,0.7)', 'line-height:1.8',
    ].join(';');

    const header = document.createElement('div');
    header.style.cssText = `font-weight:700;color:${mainColor};margin-bottom:8px;font-size:13px`;
    header.textContent = `🎼 Orchestra  ${modeLabel}`;
    panel.appendChild(header);

    const startTime = Date.now();
    targets.forEach(t => {
      _statusStart[t] = startTime;
      const row = document.createElement('div');
      row.id = `orch-row-${t.replace(/\s/g, '_')}`;
      row.style.cssText = 'margin:2px 0;display:flex;justify-content:space-between;align-items:center;';
      row.innerHTML =
        `<span><span id="orch-dot-${t.replace(/\s/g, '_')}" style="color:${mainColor}">●</span> ${t}</span>` +
        `<span id="orch-timer-${t.replace(/\s/g, '_')}" style="color:${mainColor};font-size:11px;min-width:40px;text-align:right">0.0s</span>`;
      panel.appendChild(row);

      _statusTimers[t] = setInterval(() => {
        const el = document.getElementById(`orch-timer-${t.replace(/\s/g, '_')}`);
        if (el) {
          const elapsed = ((Date.now() - _statusStart[t]) / 1000).toFixed(1);
          el.textContent = `${elapsed}s`;
        }
      }, 100);
    });

    const footer = document.createElement('div');
    footer.style.cssText = 'margin-top:8px;color:#666;font-size:10px';
    footer.textContent = isCollab ? 'Sending to all AIs...' : 'Waiting for responses...';
    panel.appendChild(footer);

    document.body.appendChild(panel);
    makeDraggable(panel, 'orchestra_badge_pos', 16, 80);
    setTimeout(removeStatusPanel, 90000);
  }

  function markAiDone(aiName) {
    if (_statusTimers[aiName]) {
      clearInterval(_statusTimers[aiName]);
      delete _statusTimers[aiName];
    }
    const dotEl = document.getElementById(`orch-dot-${aiName.replace(/\s/g, '_')}`);
    if (dotEl) { dotEl.style.color = '#4caf50'; }
    const timerEl = document.getElementById(`orch-timer-${aiName.replace(/\s/g, '_')}`);
    if (timerEl) {
      const elapsed = ((_statusStart[aiName] ? Date.now() - _statusStart[aiName] : 0) / 1000).toFixed(1);
      timerEl.style.color = '#4caf50';
      timerEl.textContent = `✓ ${elapsed}s`;
    }
    if (Object.keys(_statusTimers).length === 0) {
      setTimeout(removeStatusPanel, 3000);
    }
  }

  function removeStatusPanel() {
    Object.values(_statusTimers).forEach(id => clearInterval(id));
    _statusTimers = {};
    _statusStart  = {};
    document.getElementById('orchestra-status-panel')?.remove();
  }

  // ── Synthesis prompt injection into Claude input ────────────────────────────

  const CLAUDE_INPUT_SELECTORS = [
    'div[contenteditable="true"][data-placeholder]',
    'div[contenteditable="true"].ProseMirror',
    'div[contenteditable="true"]',
    'textarea',
  ];

  function injectSynthesisPrompt(prompt) {
    removeStatusPanel();

    let input = null;
    for (const sel of CLAUDE_INPUT_SELECTORS) {
      input = document.querySelector(sel);
      if (input) break;
    }

    if (!input) {
      showNotification('⚠ Input field not found. Please paste manually.', '#ff8844');
      navigator.clipboard.writeText(prompt).catch(() => {});
      return;
    }

    input.focus();

    if (input.contentEditable === 'true' || input.tagName !== 'TEXTAREA') {
      input.innerHTML = '';
      document.execCommand('selectAll', false, null);
      document.execCommand('delete', false, null);
      document.execCommand('insertText', false, prompt);
      input.dispatchEvent(new InputEvent('input', { bubbles: true, data: prompt, inputType: 'insertText' }));
    } else {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
      if (setter) {
        setter.call(input, prompt);
      } else {
        input.value = prompt;
      }
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }

    showNotification('🎼 Orchestra complete! Synthesis prompt injected.', '#e0c070');
  }

  // ── Notification ────────────────────────────────────────────────────────────

  function showNotification(message, color = '#e0c070') {
    const el = document.createElement('div');
    el.style.cssText = [
      'position:fixed', 'top:16px', 'right:16px', 'z-index:2147483647',
      'background:#0d0d1a', `border:1px solid ${color}`,
      'border-radius:8px', 'padding:12px 18px', `color:${color}`,
      'font-family:-apple-system,BlinkMacSystemFont,sans-serif',
      'font-size:13px', 'font-weight:600',
      'box-shadow:0 4px 20px rgba(0,0,0,0.6)',
      'max-width:340px', 'line-height:1.5',
    ].join(';');
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 6000);
  }

})();
