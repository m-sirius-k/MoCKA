/**
 * Relay for Claude — content.js
 * Turn counter + warning overlay + handoff trigger.
 * Uses Core SDK: MockaWatcher, MockaExtractor, MockaSummary, MockaInjector, MockaPrefs
 */

import { MockaWatcher }   from '../core-sdk/src/dom/watcher.js';
import { MockaExtractor } from '../core-sdk/src/dom/extractor.js';
import { MockaSummary }   from '../core-sdk/src/summary/generator.js';
import { MockaInjector }  from '../core-sdk/src/summary/injector.js';
import { MockaPrefs }     from '../core-sdk/src/settings/prefs.js';

let turnLimit = 20;
let warningShown = false;
let badge = null;

// ── Badge ──────────────────────────────────────────────────────────────────

function getBadge() {
  if (badge && document.body.contains(badge)) return badge;
  badge = document.createElement('div');
  badge.id = 'relay-badge';
  badge.style.cssText = `
    position:fixed;bottom:20px;right:20px;z-index:99999;
    background:#1a1a2e;color:#e2e8f0;
    font-family:-apple-system,sans-serif;font-size:12px;font-weight:500;
    padding:6px 12px;border-radius:20px;
    border:1px solid #334155;
    pointer-events:none;opacity:0.85;
    transition:opacity .2s;
  `;
  document.body.appendChild(badge);
  return badge;
}

function updateBadge(count) {
  const b = getBadge();
  const pct = Math.min(100, Math.round((count / turnLimit) * 100));
  const color = pct >= 100 ? '#ef4444' : pct >= 80 ? '#f59e0b' : '#10b981';
  b.style.borderColor = color;
  b.textContent = `Relay · ${count}/${turnLimit} turns`;
}

// ── Warning overlay ────────────────────────────────────────────────────────

function showWarning(turnCount) {
  if (warningShown) return;
  warningShown = true;

  const overlay = document.createElement('div');
  overlay.id = 'relay-warning';
  overlay.style.cssText = `
    position:fixed;inset:0;z-index:999999;
    background:rgba(0,0,0,0.6);
    display:flex;align-items:center;justify-content:center;
    font-family:-apple-system,sans-serif;
  `;

  overlay.innerHTML = `
    <div style="
      background:#0f172a;color:#e2e8f0;
      border:1px solid #334155;border-radius:16px;
      padding:32px;max-width:420px;width:90%;text-align:center;
    ">
      <div style="font-size:32px;margin-bottom:12px">⚡</div>
      <h2 style="margin:0 0 8px;font-size:20px;color:#f1f5f9">
        ${turnCount} turns reached
      </h2>
      <p style="margin:0 0 24px;font-size:14px;color:#94a3b8;line-height:1.5">
        Relay will summarise this conversation and continue in a new chat — so you never lose context.
      </p>
      <div style="display:flex;gap:10px;justify-content:center">
        <button id="relay-continue" style="
          background:#3b82f6;color:#fff;border:none;
          padding:10px 24px;border-radius:8px;font-size:14px;
          cursor:pointer;font-weight:500;
        ">Continue in new chat ↗</button>
        <button id="relay-dismiss" style="
          background:transparent;color:#64748b;
          border:1px solid #334155;
          padding:10px 20px;border-radius:8px;font-size:14px;
          cursor:pointer;
        ">Stay here</button>
      </div>
      <p style="margin:16px 0 0;font-size:11px;color:#475569">
        Context will be preserved automatically
      </p>
    </div>
  `;

  document.body.appendChild(overlay);

  document.getElementById('relay-continue').onclick = () => {
    overlay.remove();
    triggerHandoff();
  };

  document.getElementById('relay-dismiss').onclick = () => {
    overlay.remove();
    warningShown = false;
  };
}

// ── Handoff ────────────────────────────────────────────────────────────────

async function triggerHandoff() {
  const conv = MockaExtractor.getConversation();
  const result = MockaSummary.generate(conv.turns);
  const handoff = MockaSummary.formatHandoff(result);

  // Save session to storage via background
  chrome.runtime.sendMessage({
    type: 'RELAY_SAVE_SESSION',
    payload: {
      title: conv.title,
      url: conv.url,
      messages: conv.turns
    }
  });

  // Open new chat and inject
  await MockaInjector.openNewChatAndInject(handoff);
}

// ── Init ───────────────────────────────────────────────────────────────────

async function init() {
  if (!MockaExtractor.isOnChatPage()) return;

  turnLimit = await MockaPrefs.get('turnLimit', 20);

  MockaWatcher.init({
    onTurn({ count }) {
      updateBadge(count);
      if (count >= turnLimit && !warningShown) {
        showWarning(count);
      }
    },
    onNewChat() {
      warningShown = false;
      updateBadge(0);
    }
  });

  updateBadge(MockaWatcher.getTurnCount());
}

// Handle injection from background (new chat opened by Relay)
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === 'MOCKA_INJECT') {
    MockaInjector.inject(msg.payload.text, { delay: 800 });
  }
});

init();
