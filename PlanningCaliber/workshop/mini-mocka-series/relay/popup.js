// popup.js — Relay ポップアップ UI ロジック
'use strict';

(async () => {
  // ── 状態読み込み ──────────────────────────────────────────────────────────
  const { relay_plan_level, relay_turn_count, relay_density_score } =
    await chrome.storage.local.get(['relay_plan_level', 'relay_turn_count', 'relay_density_score']);

  const plan     = relay_plan_level || 'free';
  const turns    = relay_turn_count || 0;
  const density  = relay_density_score || 0;

  // ── UI 更新 ──────────────────────────────────────────────────────────────
  const planLabel = document.getElementById('plan-label');
  const turnEl    = document.getElementById('turn-count');
  const densityEl = document.getElementById('density-score');
  const densityFill = document.getElementById('density-bar-fill');
  const planSelect  = document.getElementById('plan-select');
  const statusMsg   = document.getElementById('status-msg');

  planLabel.textContent = plan.charAt(0).toUpperCase() + plan.slice(1);
  turnEl.textContent    = String(turns);
  turnEl.className      = `stat-value ${turns >= 18 ? 'warn' : 'ok'}`;

  densityEl.textContent = plan === 'one' ? `${Math.round(density * 100)}%` : 'Free/Pro非対応';
  densityFill.style.width = plan === 'one' ? `${Math.round(density * 100)}%` : '0%';

  if (planSelect) {
    planSelect.value = plan;
    planSelect.addEventListener('change', async () => {
      await chrome.storage.local.set({ relay_plan_level: planSelect.value });
      planLabel.textContent = planSelect.value.charAt(0).toUpperCase() + planSelect.value.slice(1);
      setStatus('プラン変更: 次のページ読み込みで反映');
    });
  }

  // ── 引き継ぎボタン ────────────────────────────────────────────────────────
  document.getElementById('btn-handoff')?.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) return;
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => window.dispatchEvent(new CustomEvent('relay:handoff-request', {
        detail: { source: 'popup', messages: window.RelayState?.getMessages() || [] },
      })),
    });
    setStatus('引き継ぎパケットを生成中...');
    window.close();
  });

  // ── リセットボタン ────────────────────────────────────────────────────────
  document.getElementById('btn-clear')?.addEventListener('click', async () => {
    await chrome.storage.local.set({ relay_turn_count: 0, relay_density_score: 0 });
    turnEl.textContent    = '0';
    densityFill.style.width = '0%';
    setStatus('セッションをリセットしました');
  });

  function setStatus(msg) {
    if (statusMsg) statusMsg.textContent = msg;
  }
})();
