// background.js — PHI OS Service Worker
// chrome.storage.local のみ使用（IndexedDB は content.js 経由）
'use strict';

import { ensureSchemaVersion } from './core/schema-registry.js';
import { registerProduct }     from './core/permission-manager.js';

// ─── 起動時初期化 ──────────────────────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(async () => {
  await ensureSchemaVersion();
  console.log('[PHI OS] Installed / Updated');
});

chrome.runtime.onStartup.addListener(async () => {
  await ensureSchemaVersion();
  console.log('[PHI OS] Started');
});

// ─── メッセージハブ ────────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  handleMessage(msg, sender)
    .then(sendResponse)
    .catch(err => {
      console.error('[PHI OS BG] handler error:', msg.type, err);
      sendResponse({ error: err.message });
    });
  return true; // async response
});

async function handleMessage(msg, sender) {
  switch (msg.type) {

    case 'PHI_COMMIT_DONE':
      // コミット完了をログ（将来: MoCKA送信もここで行う）
      console.log('[PHI OS BG] Commit done. trigger:', msg.trigger);
      return { ok: true };

    case 'PHI_REGISTER_PRODUCT':
      await registerProduct(msg.product, msg.extensionId || sender.id);
      return { ok: true };

    case 'PHI_PANEL_MODE_CHANGED':
      // sidePanel.open() は呼び出し元ページ側で直接実行済み。
      // ここでは action の popup 設定と次回クリック挙動のみ更新する。
      if (msg.mode === 'sidepanel') {
        await chrome.action.setPopup({ popup: '' });
        await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
      } else {
        await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });
        await chrome.action.setPopup({ popup: 'ui/options.html' });
      }
      return { ok: true };

    case 'PHI_GET_STATUS': {
      const { phi_commit_index = [] } = await chrome.storage.local.get('phi_commit_index');
      const { phi_last_commit_ts }    = await chrome.storage.local.get('phi_last_commit_ts');
      return {
        commit_count:    phi_commit_index.length,
        last_commit_ts:  phi_last_commit_ts || null,
      };
    }

    case 'PHI_CLEAR_OLD_DATA': {
      // 古いコミットを削除してストレージを解放
      const { phi_commit_index = [] } = await chrome.storage.local.get('phi_commit_index');
      const toDelete = phi_commit_index.slice(20); // 20件より古いものを削除
      const keys     = toDelete.map(id => `phi_commit_${id}`);
      if (keys.length) await chrome.storage.local.remove(keys);
      const newIndex = phi_commit_index.slice(0, 20);
      await chrome.storage.local.set({ phi_commit_index: newIndex });
      return { ok: true, deleted: keys.length };
    }

    default:
      return { error: `Unknown type: ${msg.type}` };
  }
}
