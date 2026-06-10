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
    stopSelectors: ['button[aria-label="Stop response"]', 'button[aria-label="回答を停止"]', '.stop-button', 'mat-icon[fonticon="stop_circle"]'],
    isContentEditable: true,
  },
  'perplexity.ai': {
    inputSelectors: ['#ask-input', 'div[contenteditable="true"]', 'textarea[placeholder]', 'textarea'],
    responseSelector: '.prose, [data-testid="answer"] .prose, .answer-content',
    stopSelectors: ['button[aria-label="Stop"]', 'button[aria-label="Stop generating"]'],
    isContentEditable: true,
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

// ─── MoCKA Living Context 自動注入（TODO_293） ───────────────────────
const MOCKA_HANDSHAKE_URL =
  'https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/api/handshake';

const MOCKA_ROLE_MAP = {
  'chatgpt.com': 'R01',
  'chat.openai.com': 'R01',
  'claude.ai': 'R02',
};

async function fetchLivingContext() {
  const role = MOCKA_ROLE_MAP[location.hostname] || 'R01';
  try {
    const res = await fetch(MOCKA_HANDSHAKE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ai_id: location.hostname.includes('claude') ? 'claude' : 'gpt-4o',
        role,
        scope: 'mocka',
        contract_version: '1.0'
      })
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.warn('[MoCKA] Handshake failed:', e);
    return null;
  }
}

function buildContextMessage(ctx) {
  const b = ctx.briefing || {};
  const warnings = ctx.warnings || [];
  const risks = b.known_risks || [];

  return `[MoCKA Living Context]
Mission: ${b.mission || ''}
Top Priority: ${b.top_priority || ''}
Strategy: ${b.recommended_strategy || ''}
Warnings: ${warnings.slice(0,3).map(w => typeof w === 'string' ? w : w.message || JSON.stringify(w)).join(' / ')}
Known Risks: ${risks.slice(0,3).join(' / ')}
Phase: ${ctx.current_phase || 'Phase 4'}
Contract: MoCKA ${ctx.contract_version || '1.0'} / Seal: ${ctx.contract_seal || ''}

上記はMoCKA制度OSからのブリーフィングです。あなたは今日、制度参加者として以下の役割で仕事を始めてください。`;
}

function waitForElement(selector, timeout = 5000) {
  return new Promise(resolve => {
    const el = document.querySelector(selector);
    if (el) { resolve(el); return; }

    const observer = new MutationObserver(() => {
      const el = document.querySelector(selector);
      if (el) { observer.disconnect(); resolve(el); }
    });
    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => { observer.disconnect(); resolve(null); }, timeout);
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function injectAndSendContext(ctx) {
  if (!location.hostname.includes('chatgpt.com') &&
      !location.hostname.includes('chat.openai.com')) return;

  const textarea = await waitForElement(
    'div[contenteditable="true"], textarea#prompt-textarea, textarea',
    8000
  );
  if (!textarea) {
    console.warn('[MoCKA] 入力欄が見つかりませんでした');
    return;
  }

  const message = buildContextMessage(ctx);

  if (textarea.contentEditable === 'true') {
    textarea.focus();
    textarea.textContent = message;
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  } else {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, 'value'
    ).set;
    nativeInputValueSetter.call(textarea, message);
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  }

  await sleep(800);

  const sendBtn = document.querySelector(
    'button[data-testid="send-button"], button[aria-label="Send"], button[aria-label="メッセージを送信"]'
  );
  if (sendBtn && !sendBtn.disabled) {
    sendBtn.click();
  } else {
    textarea.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true
    }));
  }
}

function createMockaPanel(ctx) {
  const existing = document.getElementById('mocka-living-context');
  if (existing) existing.remove();

  const briefing = ctx.briefing || {};
  const warnings = ctx.warnings || [];

  const panel = document.createElement('div');
  panel.id = 'mocka-living-context';
  panel.style.cssText = `
    position: fixed;
    top: 16px;
    right: 16px;
    width: 320px;
    max-height: 80vh;
    overflow-y: auto;
    background: #1a1a2e;
    color: #e8e6f0;
    border: 1px solid #533483;
    border-radius: 12px;
    padding: 16px;
    font-family: -apple-system, sans-serif;
    font-size: 13px;
    line-height: 1.6;
    z-index: 999999;
    box-shadow: 0 4px 24px rgba(83,52,131,0.4);
  `;

  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
      <span style="font-size:14px;font-weight:600;color:#a78bfa">
        ⚡ MoCKA Living Context
      </span>
      <button id="mocka-close" style="background:none;border:none;color:#888;cursor:pointer;font-size:16px">✕</button>
    </div>

    ${briefing.mission ? `
    <div style="margin-bottom:12px">
      <div style="color:#7c6fcd;font-size:11px;font-weight:600;margin-bottom:4px">MISSION</div>
      <div style="color:#e8e6f0">${briefing.mission}</div>
    </div>` : ''}

    ${briefing.top_priority ? `
    <div style="margin-bottom:12px">
      <div style="color:#7c6fcd;font-size:11px;font-weight:600;margin-bottom:4px">TOP PRIORITY</div>
      <div style="color:#fbbf24">${briefing.top_priority}</div>
    </div>` : ''}

    ${briefing.recommended_strategy ? `
    <div style="margin-bottom:12px">
      <div style="color:#7c6fcd;font-size:11px;font-weight:600;margin-bottom:4px">STRATEGY</div>
      <div style="color:#e8e6f0">${briefing.recommended_strategy}</div>
    </div>` : ''}

    ${warnings.length > 0 ? `
    <div style="margin-bottom:12px">
      <div style="color:#ef4444;font-size:11px;font-weight:600;margin-bottom:4px">⚠ WARNINGS</div>
      ${warnings.map(w => `<div style="color:#fca5a5;margin-bottom:4px">• ${typeof w === 'string' ? w : JSON.stringify(w)}</div>`).join('')}
    </div>` : ''}

    ${(briefing.known_risks||[]).length > 0 ? `
    <div style="margin-bottom:12px">
      <div style="color:#f59e0b;font-size:11px;font-weight:600;margin-bottom:4px">KNOWN RISKS</div>
      ${briefing.known_risks.slice(0,3).map(r => `<div style="color:#fcd34d;margin-bottom:4px">• ${r}</div>`).join('')}
    </div>` : ''}

    <div style="margin-top:12px;padding-top:12px;border-top:1px solid #533483;color:#666;font-size:11px">
      MoCKA ${ctx.contract_version || '1.0'} · ${ctx.current_phase ? ctx.current_phase.substring(0,30)+'...' : 'Phase 4'}
    </div>
  `;

  document.body.appendChild(panel);
  document.getElementById('mocka-close').onclick = () => panel.remove();
}

async function initMockaContext() {
  if (!['chatgpt.com','chat.openai.com','claude.ai']
      .some(h => location.hostname.includes(h))) return;

  const cached = sessionStorage.getItem('mocka_context_ts');
  if (cached && Date.now() - parseInt(cached) < 3600000) return;

  const ctx = await fetchLivingContext();
  if (!ctx || ctx.handshake !== 'READY') return;

  sessionStorage.setItem('mocka_context_ts', Date.now().toString());
  createMockaPanel(ctx);
  await injectAndSendContext(ctx);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMockaContext);
} else {
  setTimeout(initMockaContext, 1500);
}
// ─────────────────────────────────────────────────────────────────────
