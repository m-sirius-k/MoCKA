// panel-switch.js — popup ⇔ sidepanel 切り換え
'use strict';

const PANEL_MODE_KEY = 'phi_panel_mode'; // 'popup' | 'sidepanel'

/**
 * @returns {Promise<'popup'|'sidepanel'>}
 */
export async function getCurrentMode() {
  try {
    const stored = await chrome.storage.local.get(PANEL_MODE_KEY);
    return stored[PANEL_MODE_KEY] || 'popup';
  } catch {
    return 'popup';
  }
}

/**
 * popup ⇔ sidepanel を切り換える
 * @returns {Promise<'popup'|'sidepanel'>}
 */
export async function togglePanelMode() {
  const current = await getCurrentMode();
  const next    = current === 'popup' ? 'sidepanel' : 'popup';
  try {
    await chrome.storage.local.set({ [PANEL_MODE_KEY]: next });

    if (next === 'sidepanel') {
      // Relay と同じパターン: windowId ではなく tabId を使う。
      // tabs.query で現在のアクティブタブを取得してからサイドパネルを開き、
      // ポップアップを window.close() で明示的に閉じる。
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab?.id) {
        await chrome.sidePanel.open({ tabId: tab.id });
      }
    }
    // setPopup() / setPanelBehavior() は background 側でのみ変更可能なため委譲
    await new Promise((resolve) => {
      chrome.runtime.sendMessage({ type: 'PHI_PANEL_MODE_CHANGED', mode: next }, resolve);
    });
    // ポップアップを明示的に閉じる（sidepanel が開いた後 popup が残るのを防ぐ）
    if (next === 'sidepanel') {
      window.close();
    }
  } catch (e) {
    console.error('[PHI OS PanelSwitch] togglePanelMode error:', e);
  }
  return next;
}
