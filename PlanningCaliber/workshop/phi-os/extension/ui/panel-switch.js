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
      await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
    } else {
      await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });
    }
    // background.js に通知してaction.popupを切り換える
    chrome.runtime.sendMessage({ type: 'PHI_PANEL_MODE_CHANGED', mode: next }).catch(() => {});
  } catch (e) {
    console.error('[PHI OS PanelSwitch] togglePanelMode error:', e);
  }
  return next;
}
