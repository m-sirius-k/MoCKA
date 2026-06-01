// background.js — Relay Service Worker
// バッジ管理・セッション間状態の永続化・popup/content.js 間メッセージング
'use strict';

const BADGE_COLORS = {
  ok:      '#3fb950',
  warning: '#d29922',
  handoff: '#00d4ff',
};

// ─── バッジ更新 ──────────────────────────────────────────────────────────────

function updateBadge(tabId, text, color) {
  chrome.action.setBadgeText({ text: String(text), tabId });
  chrome.action.setBadgeBackgroundColor({ color: BADGE_COLORS[color] || color, tabId });
}

// ─── メッセージ受信 ──────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  const tabId = sender.tab?.id;

  switch (msg.type) {
    case 'SESSION_STARTED':
      // LB_005: notifySessionStart は background 側でのみ処理する
      // content.js の init() から直接呼ばないこと（レースコンディション防止）
      if (tabId) updateBadge(tabId, '0', 'ok');
      sendResponse({ ok: true });
      break;

    case 'TURN_COUNT_UPDATE':
      if (tabId) {
        const count = msg.count || 0;
        const color = count >= 18 ? 'warning' : 'ok';
        updateBadge(tabId, String(count), color);
      }
      sendResponse({ ok: true });
      break;

    case 'HANDOFF_READY':
      if (tabId) updateBadge(tabId, '✓', 'handoff');
      sendResponse({ ok: true });
      break;

    default:
      sendResponse({ ok: false, error: 'unknown message type' });
  }

  return true;  // async response
});

// ─── MoCKA サーバーへの定期ping ──────────────────────────────────────────────

const MOCKA_PING_URL = 'http://localhost:5000/relay/ping';
const PING_INTERVAL_MS = 5 * 60 * 1000;  // 5分

async function pingMoCKA() {
  try {
    const manifest = chrome.runtime.getManifest();
    await fetch(MOCKA_PING_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        version: manifest.version,
        selector_alive: true,
        timestamp: Date.now(),
      }),
    });
  } catch (_) {
    // MoCKAサーバーが起動していない場合は無視
  }
}

// 起動時に即ping、以降5分ごとに繰り返す
pingMoCKA();
setInterval(pingMoCKA, PING_INTERVAL_MS);

// ─── インストール時初期化 ─────────────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    relay_plan_level: 'free',
    relay_turn_count: 0,
  });
  console.log('[Relay] installed / updated');
  pingMoCKA();
});
