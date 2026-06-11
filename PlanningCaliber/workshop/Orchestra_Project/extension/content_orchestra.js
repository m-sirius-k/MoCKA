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

function createInputEvent(text, inputType = 'insertText') {
  try {
    return new InputEvent('input', {
      bubbles: true,
      cancelable: true,
      composed: true,
      data: text,
      inputType,
    });
  } catch (_) {
    return new Event('input', { bubbles: true, cancelable: true });
  }
}

function dispatchReactInputEvents(el, text, inputType = 'insertText') {
  el.dispatchEvent(createInputEvent(text, inputType));
  el.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
}

function setTextareaValue(el, text) {
  // ChatGPT: execCommand方式でReact内部stateも更新する
  el.focus();
  document.execCommand('selectAll', false, null);
  const ok = document.execCommand('insertText', false, text);
  console.log('[MoCKA] setTextareaValue execCommand result:', ok, 'length:', el.value.length);
}

function setContentEditableValue(el, text) {
  el.focus();

  // ① 既存テキストを全選択して削除
  document.execCommand('selectAll', false, null);
  document.execCommand('delete', false, null);

  // ② execCommand('insertText') でProseMirror内部stateごと更新
  const ok = document.execCommand('insertText', false, text);
  console.log('[MoCKA] execCommand insertText:', ok, 'length:', el.innerText.length);

  // ③ カーソルを末尾へ
  const range = document.createRange();
  range.selectNodeContents(el);
  range.collapse(false);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);

  // ④ keyup でComposerの送信可能状態をトリガー
  el.dispatchEvent(new KeyboardEvent('keyup', { key: 'a', bubbles: true }));

  console.log('[MoCKA] setContentEditable done, length:', el.innerText.length);
  console.log('[MoCKA] activeElement match:', document.activeElement === el);
}

function injectText(el, text) {
  el.focus();

  if (el instanceof HTMLTextAreaElement || el.tagName === 'TEXTAREA') {
    setTextareaValue(el, text);
    return;
  }

  const isEditable = el.isContentEditable || el.contentEditable === 'true' || el.tagName === 'DIV';

  if (isEditable) {
    setContentEditableValue(el, text);
  } else {
    el.textContent = text;
    dispatchReactInputEvents(el, text);
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
  'http://localhost:5000/api/handshake';

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
  const risks = (b.known_risks || []).slice(0, 3);
  const todos = ctx.top_todo || [];
  const mentor = ctx.mentor_package || {};
  const snapshot = mentor.institution_memory_snapshot || {};

  const projectBlock = `
[PROJECT STATUS]
Project       : MoCKA ${ctx.contract_version || '1.0'}
Phase         : ${(ctx.current_phase || 'Phase 4').substring(0, 40)}
Current Branch: main
Last Verified : ${ctx.contract_seal ? '2026-06-10 / seal:' + ctx.contract_seal : ''}
Active TODOs  : ${snapshot.active_todos || '?'}
Total Events  : ${snapshot.total_events || '?'}
Blockers      : ${warnings.filter(w => {
    const msg = typeof w === 'string' ? w : (w.message || '');
    return msg.toLowerCase().includes('block') || msg.toLowerCase().includes('fail');
  }).length}
Open Incidents: ${warnings.filter(w => {
    const msg = typeof w === 'string' ? w : (w.message || '');
    return msg.toLowerCase().includes('incident') || msg.toLowerCase().includes('active');
  }).length}
`.trim();

  const roleBlock = `
[ROLES]
ChatGPT : 監査官（設計・制度審査）
Claude  : 制度書記官・実装調整官
Codex   : 実装官（大規模バッチ）
Gemini  : 調査官（情報収集）
`.trim();

  const priorityBlock = todos.slice(0, 3).map((t, i) =>
    `${i + 1}. [${t.priority || '?'}] ${t.title || t.id}`
  ).join('\n');

  const riskBlock = risks.length > 0
    ? risks.map(r => `⚠ ${r}`).join('\n')
    : '（なし）';

  const warnBlock = warnings.length > 0
    ? warnings.slice(0, 3).map(w =>
        typeof w === 'string' ? `• ${w}` : `• ${w.message || JSON.stringify(w)}`
      ).join('\n')
    : '（なし）';

  const strategyBlock = b.recommended_strategy
    ? b.recommended_strategy.substring(0, 200)
    : '';

  return `━━━━━━━━━━━━━━━━━━━━━━━━
⚡ MoCKA Living Context
━━━━━━━━━━━━━━━━━━━━━━━━

${projectBlock}

${roleBlock}

[MISSION]
${b.mission || ''}

[TOP PRIORITY]
${priorityBlock}

[KNOWN RISKS]
${riskBlock}

[WARNINGS]
${warnBlock}

[STRATEGY]
${strategyBlock}

━━━━━━━━━━━━━━━━━━━━━━━━
上記はMoCKA制度OSからの自動ブリーフィングです。
あなたは「監査官（R01）」として、この文脈を前提に応答してください。
制度原則: Not AI-to-AI. AI-to-Institution.
Reasoning with a living institution.
━━━━━━━━━━━━━━━━━━━━━━━━`;
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

// __reactPropsが存在する入力欄が安定するまで待つ
async function waitForReactInput(selectors, timeout = 10000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    for (const sel of selectors) {
      try {
        const el = document.querySelector(sel);
        if (el) {
          const hasProps = Object.keys(el).some(k => k.startsWith('__reactProps'));
          if (hasProps) {
            console.log('[MoCKA] reactProps確認済み要素を取得:', el.tagName, el.id);
            return el;
          }
        }
      } catch (_) {}
    }
    await sleep(200);
  }
  console.warn('[MoCKA] waitForReactInput: タイムアウト');
  return null;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Relay_Project/extension/content.js (v4.6) のINPUT_SELECTORS / setInputValue() を流用
const MOCKA_INPUT_SELECTORS = [
  'div[contenteditable="true"][id="prompt-textarea"]',
  'div[contenteditable="true"].ProseMirror',
  'div[contenteditable="true"][data-testid="composer-input"]',
  'div[contenteditable="true"]',
];

function mockaSetInputValue(el, text) {
  el.focus();

  if (el instanceof HTMLTextAreaElement || el.tagName === 'TEXTAREA') {
    setTextareaValue(el, text);
    return;
  }

  if (el.isContentEditable || el.contentEditable === 'true') {
    setContentEditableValue(el, text);
    return;
  }

  el.textContent = text;
  dispatchReactInputEvents(el, text);
}
async function injectAndSendContext(ctx) {
  if (!location.hostname.includes('chatgpt.com') &&
      !location.hostname.includes('chat.openai.com')) return;
  console.log('[MoCKA] injectAndSendContext: start');
  const input = await waitForElement(MOCKA_INPUT_SELECTORS.join(', '), 8000);
  if (!input) {
    console.warn('[MoCKA] 入力欄が見つかりませんでした');
    return;
  }
  console.log('[MoCKA] 入力欄を検出:', input.tagName, input.id, 'contentEditable=', input.contentEditable);
  const message = buildContextMessage(ctx);
  mockaSetInputValue(input, message);
  await sleep(600);
  console.log('[MoCKA] 入力欄の現在のテキスト長:', (input.textContent || input.value || '').length);
  console.log('[MoCKA] innerText先頭80:', input.innerText?.substring(0, 80));
  console.log('[MoCKA] activeElement:', document.activeElement?.tagName, document.activeElement?.id);
  const sendBtn = document.querySelector('.composer-submit-button-color')
    || document.querySelector('button[data-testid="send-button"]')
    || document.querySelector('button[aria-label="Send prompt"]');
  console.log('[MoCKA] sendBtn disabled:', sendBtn?.disabled, 'aria-disabled:', sendBtn?.getAttribute('aria-disabled'));
  // MutationObserver: disabled/aria-disabledがfalseになるまで最大3秒待つ
  await new Promise(resolve => {
    const isReady = () => sendBtn && !sendBtn.disabled && sendBtn.getAttribute('aria-disabled') !== 'true';
    if (isReady()) { resolve(); return; }
    const obs = new MutationObserver(() => {
      if (isReady()) { obs.disconnect(); resolve(); }
    });
    if (sendBtn) obs.observe(sendBtn, { attributes: true, attributeFilter: ['disabled', 'aria-disabled'] });
    setTimeout(() => { obs.disconnect(); resolve(); }, 3000);
  });

  function fireClick(btn) {
    ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(type => {
      btn.dispatchEvent(new MouseEvent(type, {
        bubbles: true, cancelable: true, composed: true,
        buttons: 1, button: 0,
      }));
    });
  }

  const btnReady = sendBtn && !sendBtn.disabled && sendBtn.getAttribute('aria-disabled') !== 'true';
  if (btnReady) {
    console.log('[MoCKA] 送信: pointerdown→mousedown→pointerup→mouseup→click');
    fireClick(sendBtn);
    await sleep(600);
    // フォールバック: まだボタンが有効なら送信されていない可能性
    const stillReady = !sendBtn.disabled && sendBtn.getAttribute('aria-disabled') !== 'true';
    if (stillReady) {
      console.log('[MoCKA] フォールバック: form.requestSubmit()');
      const form = input.closest('form');
      if (form) {
        try { form.requestSubmit(); } catch(e) { console.warn('[MoCKA] requestSubmit失敗:', e); }
      }
    }
  } else {
    console.warn('[MoCKA] 送信ボタンが見つからないか無効のまま', { sendBtn, disabled: sendBtn?.disabled, ariaDisabled: sendBtn?.getAttribute('aria-disabled') });
  }
  console.log('[MoCKA] 送信処理完了');
}
// ── 起動 ──────────────────────────────────────────────────────────────────────
async function mockaAutoInject() {
  if (!location.hostname.includes('chatgpt.com') &&
      !location.hostname.includes('chat.openai.com')) return;

  console.log('[MoCKA] autoInject: fetch Living Context...');
  const ctx = await fetchLivingContext();
  if (!ctx) {
    console.warn('[MoCKA] Living Context 取得失敗 — localhost:5000 起動確認');
    return;
  }
  console.log('[MoCKA] Living Context 取得成功:', Object.keys(ctx));
  await injectAndSendContext(ctx);
}

function scheduleMockaAutoInject() {
  const start = () => setTimeout(() => {
    mockaAutoInject().catch(e => console.error('[MoCKA] autoInject failed:', e));
  }, 2000);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else {
    start();
  }
}

scheduleMockaAutoInject();



