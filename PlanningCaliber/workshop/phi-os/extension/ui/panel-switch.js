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
      // chrome.sidePanel.open() はユーザーアクションの直接チェーン内でのみ動作する。
      // background.js 経由（message → SW → open）だと Chrome がブロックするため、
      // popup/options ページ側でユーザーアクション直後に直接呼ぶ必要がある。
      const win = await chrome.windows.getCurrent();
      await chrome.sidePanel.open({ windowId: win.id });
    }
    // setPopup() / setPanelBehavior() は background 側でのみ変更可能なため委譲
    // sidepanel→popup 方向は close() API がないため setPanelBehavior のみ設定し
    // 次回ツールバークリックでポップアップが開くようにする
    await new Promise((resolve) => {
      chrome.runtime.sendMessage({ type: 'PHI_PANEL_MODE_CHANGED', mode: next }, resolve);
    });
  } catch (e) {
    console.error('[PHI OS PanelSwitch] togglePanelMode error:', e);
  }
  return next;
}
