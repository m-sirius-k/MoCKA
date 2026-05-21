// Relay content.js v3.0.0
// Role: observe claude.ai, count turns, extract TODOs, send to background.js

(function () {
  'use strict';

  // -- config --
  const TURN_WARN_THRESHOLD = 20;
  const SCAN_INTERVAL_MS    = 3000;
  const IDLE_WAIT_MS        = 1500; // wait after streaming stops

  // -- TODO extraction patterns --
  // English: imperative patterns
  const EN_PATTERNS = [
    /^\[RELAY_TODO\]\s*(.+)/i,                          // explicit tag (highest priority)
    /^please\s+(?:make\s+sure\s+to\s+)?(.+)/i,         // Please...
    /^make\s+sure\s+to\s+(.+)/i,                       // Make sure to...
    /^do\s+(?:this|that)?\s*(.+)/i,                    // Do ...
    /^could\s+you\s+(.+)/i,                            // Could you...
    /^would\s+you\s+(.+)/i,                            // Would you...
    /^(?:complete|finish|update|submit|add|fix|check|review|create|write|send|remove|delete|deploy|test|verify|confirm)\s+(.+)/i,
  ];
  // Japanese: request/instruction patterns
  const JA_PATTERNS = [
    /^TODO[:：]?\s*(.+)/i,                              // TODO: ...
    /(.+)[\u3092\u3092](?:todo\u3057\u3066|todo\u767b\u9332\u3057\u3066|\u30bf\u30b9\u30af\u306b\u8ffd\u52a0\u3057\u3066)/,
    /(.+)[\u3057\u3066\u3066](?:\u304a\u3044\u3066|\u304a\u304f|\u304f\u3060\u3055\u3044|\u4e0b\u3055\u3044)/,
    /(.+)(?:\u306e\u5bfe\u5fdc|\u3092\u5b9f\u65bd|\u3092\u78ba\u8a8d|\u3092\u4fee\u6b63|\u3092\u8ffd\u52a0|\u3092\u524a\u9664|\u3092\u66f4\u65b0)(?:\u3057\u3066|\u3059\u308b|\u304a\u9858\u3044)/,
    /\u3053\u306e\u30d7\u30e9\u30f3\u3067(?:\u884c\u304d|\u3044\u304d)\u307e\u3059[^\S\n]*todo\u3057\u3066/,
    /\u4eca\u306e\u8a71[^\S\n]*todo\u3057\u3066\u304a\u3044\u3066/,
  ];

  // -- state --
  let lastSeenMessages = new Set();
  let turnCount        = 0;
  let warnShown        = false;
  let lastScanTime     = 0;
  let scanTimer        = null;

  // -- DOM helpers --
  function getMessageEls() {
    // get conversation message elements
    return Array.from(document.querySelectorAll(
      '[data-testid="human-turn"], [data-testid="ai-turn"], ' +
      '.font-claude-message, .font-user-message, ' +
      '.font-claude-response'
    ));
  }

  function getStableText(el) {
    // check not streaming
    const streaming = el.closest('[data-is-streaming="true"]');
    if (streaming) return null;
    return (el.textContent || el.innerText || '').trim();
  }

  function isAssistantEl(el) {
    const turn = el.closest('[data-testid="ai-turn"]');
    if (turn) return true;
    if (el.classList.contains('font-claude-message')) return true;
    if (el.classList.contains('font-claude-response')) return true;
    return false;
  }

  // -- extract TODOs --
  function extractTodos(text) {
    const results = [];
    const lines = text.split(/\n/);

    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line || line.length < 5 || line.length > 200) continue;

      // skip code-like lines
      if (/^[`{};=<>]/.test(line)) continue;
      if (/\bfunction\b|\bconst\b|\blet\b|\bvar\b|\breturn\b/.test(line)) continue;
      // skip high-symbol-density lines
      const symbolCount = (line.match(/[^a-zA-Z0-9\u3040-\u9FFF\s]/g) || []).length;
      if (symbolCount / line.length > 0.3) continue;

      // match English patterns
      for (const pat of EN_PATTERNS) {
        const m = line.match(pat);
        if (m) {
          const body = (m[1] || line).trim();
          if (body.length >= 5) {
            results.push({ text: body, source: 'en_pattern', raw: line });
            break;
          }
        }
      }
      // match Japanese patterns
      for (const pat of JA_PATTERNS) {
        const m = line.match(pat);
        if (m) {
          const body = (m[1] || line).trim();
          if (body.length >= 3) {
            results.push({ text: body, source: 'ja_pattern', raw: line });
            break;
          }
        }
      }
    }
    return results;
  }

  // -- scan --
  function scan() {
    const now = Date.now();
    if (now - lastScanTime < IDLE_WAIT_MS) return;
    lastScanTime = now;

    const els = getMessageEls();
    if (!els.length) return;

    let newTurnCount = 0;
    const newTodos   = [];

    for (const el of els) {
      const text = getStableText(el);
      if (!text) continue;

      // count turns by unique message ID or text
      const key = el.dataset?.messageId || text.slice(0, 80);
      if (!lastSeenMessages.has(key)) {
        lastSeenMessages.add(key);
        newTurnCount++;

        // extract TODOs from both assistant and user messages
        const todos = extractTodos(text);
        for (const t of todos) {
          t.isAssistant = isAssistantEl(el);
          newTodos.push(t);
        }
      }
    }

    // update turn count
    if (newTurnCount > 0) {
      turnCount = lastSeenMessages.size;
      chrome.runtime.sendMessage({
        type: 'RELAY_TURN_UPDATE',
        payload: { count: turnCount }
      }).catch(() => {});

      // threshold warning
      if (turnCount >= TURN_WARN_THRESHOLD && !warnShown) {
        warnShown = true;
        showWarning();
      }
    }

    // send new TODOs
    for (const t of newTodos) {
      chrome.runtime.sendMessage({
        type: 'RELAY_ADD_TODO',
        payload: {
          text:        t.text,
          source:      t.isAssistant ? 'assistant' : 'user',
          pattern:     t.source,
          created_at:  new Date().toISOString(),
          url:         location.href
        }
      }).catch(() => {});
    }
  }

  // -- warning popup --
  function showWarning() {
    const div = document.createElement('div');
    div.id = 'relay-warn';
    div.style.cssText = [
      'position:fixed', 'bottom:20px', 'right:20px', 'z-index:999999',
      'background:#1a1a2e', 'color:#e0e0e0', 'padding:16px 20px',
      'border-radius:10px', 'border:1px solid #ff6b6b',
      'font-family:system-ui,sans-serif', 'font-size:14px',
      'box-shadow:0 4px 20px rgba(0,0,0,.5)', 'max-width:320px'
    ].join(';');
    div.innerHTML = `
      <div style="font-weight:bold;color:#ff6b6b;margin-bottom:8px">
        ⚠️ Relay: ${turnCount} turns
      </div>
      <div style="margin-bottom:12px;line-height:1.5">
        Context is getting long.<br>Consider starting a new chat.
      </div>
      <button id="relay-warn-close"
        style="background:#ff6b6b;color:#fff;border:none;padding:6px 14px;
               border-radius:6px;cursor:pointer;font-size:13px">
        Got it
      </button>
    `;
    document.body.appendChild(div);
    div.querySelector('#relay-warn-close').onclick = () => div.remove();
    setTimeout(() => div.remove(), 15000);
  }

  // -- URL change detection (reset on new chat) --
  let lastUrl = location.href;
  function checkUrlChange() {
    if (location.href !== lastUrl) {
      lastUrl      = location.href;
      turnCount    = 0;
      warnShown    = false;
      lastSeenMessages.clear();
      chrome.runtime.sendMessage({
        type: 'RELAY_TURN_UPDATE',
        payload: { count: 0 }
      }).catch(() => {});
    }
  }

  // -- MutationObserver --
  const observer = new MutationObserver(() => {
    checkUrlChange();
    clearTimeout(scanTimer);
    scanTimer = setTimeout(scan, IDLE_WAIT_MS);
  });

  observer.observe(document.body, {
    childList: true,
    subtree:   true
  });

  // periodic scan (fallback)
  setInterval(() => {
    checkUrlChange();
    scan();
  }, SCAN_INTERVAL_MS);

  // initial scan
  setTimeout(scan, 2000);

  console.log('[Relay] v3.0.0 content.js started');
})();
