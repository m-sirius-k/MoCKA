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

// ── Orchestra Pro/One: Button injection & synthesis ───────────────────────────
// Separate block — Free機能（上のIIFE）は一切変更しない

(function () {
  'use strict';

  let orchestraPlan = 'free';

  // Load plan and keep in sync with storage changes
  function refreshPlan() {
    chrome.runtime.sendMessage({ type: 'GET_PLAN' }, res => {
      if (res?.ok) orchestraPlan = res.plan;
    });
  }

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === 'sync' && changes.license_plan) {
      orchestraPlan = changes.license_plan.newValue || 'free';
      // Re-scan to show/hide buttons if plan just upgraded
      injectOrchestraButtons();
    }
  });

  refreshPlan();

  function canShowPro() {
    return orchestraPlan === 'pro' || orchestraPlan === 'one';
  }
  function canShowOne() {
    return orchestraPlan === 'one';
  }

  // ── Button injection ────────────────────────────────────────────────────────

  const ASSISTANT_SELECTORS = [
    '.font-claude-response',
    '[data-testid="assistant-message"]',
    '.font-claude-message',
  ];

  function findAssistantBlocks() {
    for (const sel of ASSISTANT_SELECTORS) {
      const els = document.querySelectorAll(sel);
      if (els.length > 0) return Array.from(els);
    }
    return [];
  }

  function injectOrchestraButtons() {
    if (!canShowPro()) return;

    const blocks = findAssistantBlocks();
    blocks.forEach(block => {
      // Walk up to a stable container element
      const container = block.closest(
        '[data-test-render-count], [class*="group-"], [class*="message-"]'
      ) || block.parentElement;
      if (!container) return;
      if (container.hasAttribute('data-orchestra-injected')) return;
      container.setAttribute('data-orchestra-injected', '1');

      const wrapper = document.createElement('div');
      wrapper.style.cssText = 'display:inline-flex;gap:6px;margin-top:8px;flex-wrap:wrap;';

      // Pro button (always shown when Pro or One)
      const proBtn = buildButton('🎼 5AI Orchestra', '#e0c070');
      proBtn.title = 'Orchestra Pro: 5つのAIに同じ質問を送り、回答を統合';
      proBtn.onclick = () => {
        const text = block.innerText || block.textContent || '';
        chrome.runtime.sendMessage({ type: 'START_ORCHESTRA', text: text.trim() }, res => {
          if (res?.ok) {
            proBtn.textContent = '🎼 起動中...';
            proBtn.disabled = true;
            setTimeout(() => {
              proBtn.textContent = '🎼 5AI Orchestra';
              proBtn.disabled = false;
            }, 60000);
          } else {
            showNotification('⚠ ' + (res?.error || 'Orchestra起動失敗'), '#ff4444');
          }
        });
      };
      wrapper.appendChild(proBtn);

      // One button (only when One plan)
      if (canShowOne()) {
        const oneBtn = buildButton('⚡ Orchestra One', '#c9a84c');
        oneBtn.title = 'Orchestra One: Playwrightで完全自律実行';
        oneBtn.onclick = () => {
          const text = block.innerText || block.textContent || '';
          chrome.runtime.sendMessage({ type: 'START_ORCHESTRA_ONE', text: text.trim() }, res => {
            if (res?.ok) {
              oneBtn.textContent = '⚡ 実行中...';
              oneBtn.disabled = true;
              setTimeout(() => {
                oneBtn.textContent = '⚡ Orchestra One';
                oneBtn.disabled = false;
              }, 120000);
            } else {
              showNotification('⚠ ' + (res?.error || 'Orchestra One起動失敗'), '#ff4444');
            }
          });
        };
        wrapper.appendChild(oneBtn);
      }

      container.appendChild(wrapper);
    });
  }

  function buildButton(label, color) {
    const btn = document.createElement('button');
    btn.className = 'orchestra-action-btn';
    btn.textContent = label;
    btn.style.cssText = [
      'background:linear-gradient(135deg,#0d0d1a,#16213e)',
      `color:${color}`,
      `border:1px solid ${color}`,
      'border-radius:6px',
      'padding:5px 12px',
      'cursor:pointer',
      'font-size:11px',
      'font-family:-apple-system,BlinkMacSystemFont,sans-serif',
      'font-weight:600',
      'letter-spacing:0.3px',
      'transition:opacity 0.15s',
      'white-space:nowrap',
    ].join(';');
    btn.addEventListener('mouseenter', () => { btn.style.opacity = '0.8'; });
    btn.addEventListener('mouseleave', () => { btn.style.opacity = '1'; });
    return btn;
  }

  // ── Incoming messages from background ──────────────────────────────────────

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg.type === 'ORCHESTRA_STARTED') {
      showStatusPanel(msg.targets || []);
      sendResponse({ ok: true });
    }

    if (msg.type === 'ORCHESTRA_SYNTHESIZE') {
      injectSynthesisPrompt(msg.prompt);
      sendResponse({ ok: true });
    }
  });

  // ── Status panel ────────────────────────────────────────────────────────────

  function showStatusPanel(targets) {
    removeStatusPanel();
    const panel = document.createElement('div');
    panel.id = 'orchestra-status-panel';
    panel.style.cssText = [
      'position:fixed', 'bottom:20px', 'right:20px', 'z-index:2147483647',
      'background:#0d0d1a', 'border:1px solid #e0c070',
      'border-radius:10px', 'padding:16px 20px', 'color:#e8e8ec',
      'font-family:-apple-system,BlinkMacSystemFont,sans-serif',
      'font-size:12px', 'min-width:240px', 'max-width:300px',
      'box-shadow:0 6px 30px rgba(0,0,0,0.7)', 'line-height:1.6',
    ].join(';');

    panel.innerHTML =
      '<div style="font-weight:700;color:#e0c070;margin-bottom:10px;font-size:13px">🎼 Orchestra 実行中</div>' +
      targets.map(t => `<div style="margin:3px 0">⏳ ${t}</div>`).join('') +
      '<div style="margin-top:10px;color:#888;font-size:10px">各タブでプロンプトを確認し Enter で送信してください。<br>回答完了後、自動的に統合プロンプトを生成します。</div>';

    document.body.appendChild(panel);
    // Auto-dismiss after 90 seconds
    setTimeout(removeStatusPanel, 90000);
  }

  function removeStatusPanel() {
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
      showNotification('⚠ 入力欄が見つかりませんでした。手動で貼り付けてください。', '#ff8844');
      // Fallback: copy to clipboard
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

    showNotification('🎼 Orchestra完了！統合プロンプトを注入しました。', '#e0c070');
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

  // ── Periodic button injection (picks up new messages) ──────────────────────

  // Run when DOM settles after streaming
  const btnObserver = new MutationObserver(() => {
    if (canShowPro()) {
      clearTimeout(btnObserver._timer);
      btnObserver._timer = setTimeout(injectOrchestraButtons, 800);
    }
  });
  btnObserver.observe(document.body, { childList: true, subtree: true });

  // Initial pass after page fully loads
  setTimeout(() => {
    refreshPlan();
    setTimeout(injectOrchestraButtons, 1500);
  }, 3000);
})();
