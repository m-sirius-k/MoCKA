// background.js — PHI OS Service Worker
// import完全排除・自己完結型（Service Worker対応）
// ensureSchemaVersion / registerProduct をインライン化
'use strict';

// MOCKA_DEV_MODE: 開発者バイパス（PHI-OSはライセンス不要だが識別子として定義）
const MOCKA_DEV_ID = "m-sirius-k";

const SCHEMA_VERSION  = '1.0.0';
const KNOWN_PRODUCTS  = ['relay', 'orchestra', 'memory'];

// ─── schemaバージョン確認（インライン）─────────────────────────────────────────

async function ensureSchemaVersion() {
  try {
    const { phi_schema_version } = await chrome.storage.local.get('phi_schema_version');
    if (phi_schema_version !== SCHEMA_VERSION) {
      await chrome.storage.local.set({ phi_schema_version: SCHEMA_VERSION });
    }
  } catch (e) {
    // non-critical
  }
}

// ─── 製品ID登録（インライン）──────────────────────────────────────────────────

async function registerProduct(productName, extensionId) {
  if (!KNOWN_PRODUCTS.includes(productName)) return;
  try {
    await chrome.storage.local.set({ [`phi_product_id_${productName}`]: extensionId });
    console.log('[PHI OS] Registered:', productName, extensionId);
  } catch (e) {
    console.warn('[PHI OS] registerProduct failed:', e.message);
  }
}

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

    case 'PHI_HEARTBEAT':
      // content.jsからの定期死活確認。Service Worker維持目的。
      return { ok: true, ts: Date.now() };

    case 'PHI_COMMIT_DONE':
      try {
        await fetch('http://127.0.0.1:5000/api/phi-os-event', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type:      'PHI_COMMIT_DONE',
            source:    'phi-os',
            workspace: msg.workspace || '',
            payload:   msg.payload   || {},
            timestamp: new Date().toISOString()
          })
        });
      } catch (e) {
        console.warn('[PHI OS BG] MoCKA送信失敗(オフライン時は無視):', e.message);
      }
      console.log('[PHI OS BG] Commit done. trigger:', msg.trigger);
      return { ok: true };

    case 'PHI_REGISTER_PRODUCT':
      await registerProduct(msg.product, msg.extensionId || sender.id);
      return { ok: true };

    case 'PHI_OPEN_POPUP':
      await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });
      await chrome.action.setPopup({ popup: 'ui/options.html' });
      try { await chrome.action.openPopup(); } catch (_) {}
      await chrome.storage.local.set({ phi_panel_mode: 'popup' });
      return { ok: true };

    case 'PHI_PANEL_MODE_CHANGED':
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
        commit_count:   phi_commit_index.length,
        last_commit_ts: phi_last_commit_ts || null,
      };
    }

    case 'PHI_CLEAR_OLD_DATA': {
      const { phi_commit_index = [] } = await chrome.storage.local.get('phi_commit_index');
      const toDelete = phi_commit_index.slice(20);
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
