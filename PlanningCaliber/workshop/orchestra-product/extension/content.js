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
    const stable = text.slice(-80);  // ★ 末尾80文字を使用（旧: 先頭80文字）
    const hash = btoa(encodeURIComponent(role + stable)).slice(0, 16);
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
    const assistantBlocks = document.querySelectorAll('.font-claude-response');
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
