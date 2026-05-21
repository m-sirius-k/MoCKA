// Orchestra - content_orchestra.js
// Handles prompt injection and response capture for external AI services
// Injected into: ChatGPT / Gemini / Perplexity / Copilot

'use strict';

const AI_CONFIGS = {
  'chatgpt.com': {
    inputSelectors: ['#prompt-textarea', 'div[contenteditable="true"][data-id]', 'textarea'],
    responseSelector: '[data-message-author-role="assistant"] .markdown, [data-message-author-role="assistant"] .prose',
    stopSelectors: ['button[aria-label="Stop streaming"]', 'button[aria-label="Stop"]', '[data-testid="stop-button"]'],
    isContentEditable: true,
  },
  'gemini.google.com': {
    inputSelectors: ['.ql-editor', 'rich-textarea .ql-editor', 'div[contenteditable="true"]'],
    responseSelector: 'model-response .response-container, .model-response-text, [data-response-id] .markdown',
    stopSelectors: ['button[aria-label="Stop response"]', '.stop-button', 'mat-icon[fonticon="stop_circle"]'],
    isContentEditable: true,
  },
  'perplexity.ai': {
    inputSelectors: ['textarea[placeholder]', 'textarea'],
    responseSelector: '.prose, [data-testid="answer"] .prose, .answer-content',
    stopSelectors: ['button[aria-label="Stop"]', 'button[aria-label="Stop generating"]'],
    isContentEditable: false,
  },
  'copilot.microsoft.com': {
    inputSelectors: ['textarea', '#userInput', 'div[contenteditable="true"]'],
    responseSelector: '[data-testid="response"] .prose, .cib-chat-turn [class*="response"] .ac-textBlock',
    stopSelectors: ['button[aria-label="Stop responding"]', 'cib-typing-indicator'],
    isContentEditable: false,
  },
};

function getConfig() {
  const hostname = window.location.hostname;
  const entry = Object.entries(AI_CONFIGS).find(([key]) => hostname.includes(key));
  return entry ? entry[1] : null;
}

function findElement(selectors) {
  for (const sel of selectors) {
    try {
      const el = document.querySelector(sel);
      if (el) return el;
    } catch (_) { /* invalid selector — skip */ }
  }
  return null;
}

function injectText(el, text) {
  el.focus();

  const isEditable = el.contentEditable === 'true' || el.tagName === 'DIV';

  if (isEditable) {
    el.innerHTML = '';
    // execCommand keeps React/framework state in sync
    document.execCommand('selectAll', false, null);
    document.execCommand('delete', false, null);
    document.execCommand('insertText', false, text);
    el.dispatchEvent(new InputEvent('input', { bubbles: true, data: text, inputType: 'insertText' }));
  } else {
    // textarea: use native setter to bypass React synthetic event wrapping
    const nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, 'value'
    )?.set;
    if (nativeSetter) {
      nativeSetter.call(el, text);
    } else {
      el.value = text;
    }
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
}

function isGenerating(config) {
  return config.stopSelectors.some(sel => {
    try { return !!document.querySelector(sel); } catch (_) { return false; }
  });
}

function captureLatestResponse(config) {
  const selectors = config.responseSelector.split(',').map(s => s.trim());
  for (const sel of selectors) {
    try {
      const all = document.querySelectorAll(sel);
      if (all.length > 0) {
        // Take the last visible response block
        const last = all[all.length - 1];
        const text = last.innerText?.trim();
        if (text && text.length > 10) return text;
      }
    } catch (_) { /* skip */ }
  }
  return '';
}

function showToast(message, durationMs = 8000) {
  let toast = document.getElementById('orchestra-inject-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'orchestra-inject-toast';
    toast.style.cssText = [
      'position:fixed', 'top:16px', 'right:16px', 'z-index:2147483647',
      'background:#0d0d1a', 'color:#e0c070', 'border:1px solid #e0c070',
      'border-radius:8px', 'padding:12px 18px', 'font-size:13px',
      'font-family:-apple-system,BlinkMacSystemFont,sans-serif',
      'box-shadow:0 4px 20px rgba(0,0,0,0.6)', 'max-width:320px',
      'line-height:1.5', 'pointer-events:none',
    ].join(';');
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.style.display = 'block';
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { toast.style.display = 'none'; }, durationMs);
}

// ── Response monitor ──────────────────────────────────────────────────────────

let _monitorInterval = null;

function startResponseMonitor(config, sessionId, aiName) {
  if (_monitorInterval) clearInterval(_monitorInterval);

  let lastLength = 0;
  let stableCount = 0;
  let waitingForStart = true;
  let startWaitCount = 0;

  _monitorInterval = setInterval(() => {
    // First wait until generation actually starts (stop button appears)
    if (waitingForStart) {
      if (isGenerating(config)) {
        waitingForStart = false;
      } else {
        startWaitCount++;
        if (startWaitCount > 90) {
          // 90 seconds without start — give up waiting
          clearInterval(_monitorInterval);
          _monitorInterval = null;
        }
      }
      return;
    }

    // Generation has started; now wait for it to stop and text to stabilize
    const generating = isGenerating(config);
    if (generating) {
      stableCount = 0;
      return;
    }

    const response = captureLatestResponse(config);
    if (response.length > 0 && response.length === lastLength) {
      stableCount++;
      if (stableCount >= 3) {
        clearInterval(_monitorInterval);
        _monitorInterval = null;
        chrome.runtime.sendMessage({
          type: 'ORCHESTRA_RESPONSE',
          sessionId,
          aiName,
          ai: window.location.hostname,
          response,
        });
      }
    } else {
      stableCount = 0;
      lastLength = response.length;
    }
  }, 1000);
}

// ── Message listener ──────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === 'ORCHESTRA_INJECT') {
    const config = getConfig();
    if (!config) {
      sendResponse({ ok: false, error: 'No config for ' + window.location.hostname });
      return true;
    }

    // Retry injecting up to 10 times (1 second apart) in case input isn't ready yet
    let attempts = 0;
    const tryInject = () => {
      const el = findElement(config.inputSelectors);
      if (el) {
        try {
          injectText(el, msg.prompt);
          showToast('🎼 Orchestra: プロンプト注入済み。Enterで送信してください。');
          startResponseMonitor(config, msg.sessionId, msg.aiName || window.location.hostname);
          sendResponse({ ok: true });
        } catch (e) {
          sendResponse({ ok: false, error: e.message });
        }
      } else if (attempts < 10) {
        attempts++;
        setTimeout(tryInject, 1000);
      } else {
        sendResponse({ ok: false, error: 'Input element not found after retries' });
      }
    };

    tryInject();
    return true; // keep channel open for async sendResponse
  }

  if (msg.type === 'ORCHESTRA_GET_RESPONSE') {
    const config = getConfig();
    const response = config ? captureLatestResponse(config) : '';
    sendResponse({ ok: true, response });
    return true;
  }

  if (msg.type === 'ORCHESTRA_PING') {
    sendResponse({ ok: true, hostname: window.location.hostname });
    return true;
  }
});
