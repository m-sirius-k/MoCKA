// AI Conversation Logger - content.js
// Monitors claude.ai DOM and captures messages

(function () {
  'use strict';

  const SERVICE = 'claude.ai';
  let sessionId = generateSessionId();
  let capturedIds = new Set();
  let lastUrl = location.href;

  function generateSessionId() {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  }

  function generateMessageId(role, text) {
    const hash = btoa(encodeURIComponent(role + text.slice(0, 80))).slice(0, 16);
    return 'msg_' + hash;
  }

  // Extract all visible messages from the DOM
  function extractMessages() {
    const messages = [];

    // Claude.ai message structure: role determined by container class
    // User messages: [data-testid="user-message"] or similar
    // Assistant messages: prose content blocks

    // Strategy: look for the main conversation turn containers
    const turnSelectors = [
      '[data-testid="user-message"]',
      '.font-claude-response',
    ];

    // User messages
    document.querySelectorAll('[data-testid="user-message"]').forEach((el) => {
      const text = el.innerText?.trim();
      if (!text) return;
      messages.push({ role: 'user', text });
    });

    // Assistant messages - look for the streaming/rendered prose blocks
    // Claude uses a specific structure for its responses
    const assistantBlocks = document.querySelectorAll(
      '.font-claude-response'
    );
    assistantBlocks.forEach((el) => {
      const text = el.innerText?.trim();
      if (!text) return;
      messages.push({ role: 'assistant', text });
    });

    // Fallback: interleaved scan based on conversation-turn containers
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

  // Send new messages to background for storage
  function saveNewMessages(messages) {
    messages.forEach((msg) => {
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

      chrome.runtime.sendMessage({ type: 'SAVE_MESSAGE', payload: record });
    });
  }

  // Main scan function
  function scan() {
    const messages = extractMessages();
    if (messages.length > 0) {
      saveNewMessages(messages);
    }
  }

  // Reset session on URL change (new chat)
  function checkUrlChange() {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      sessionId = generateSessionId();
      capturedIds.clear();
      setTimeout(scan, 1000);
    }
  }

  // Observe DOM mutations (streaming responses)
  const observer = new MutationObserver(() => {
    checkUrlChange();
    scan();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: false,
  });

  // Initial scan after page load
  setTimeout(scan, 2000);

  // Periodic scan as safety net
  setInterval(() => {
    checkUrlChange();
    scan();
  }, 5000);

  // Listen for popup requests to get current session info
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'GET_SESSION') {
      sendResponse({ sessionId, capturedCount: capturedIds.size });
    }
  });
})();
