/**
 * Relay for Claude — background.js v2.0
 * A: Logbook付きセッション保存
 * B: Vault Pro — 過去文脈注入
 */

const INDEX_KEY  = 'mocka_relay_sessions_index';
const VAULT_KEY  = 'mocka_relay_vault';       // Pro: 手動ピン留め文脈
const NS         = 'mocka_relay_';
const MAX_SESSIONS = 50;                       // ストレージ上限

// ── Session storage ────────────────────────────────────────────────────────

async function getIndex() {
  return new Promise(resolve => {
    chrome.storage.local.get(INDEX_KEY, r => resolve(r[INDEX_KEY] || []));
  });
}

async function saveSession(data) {
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  const session = {
    id, product: 'relay',
    title:    data.title    || 'Untitled',
    url:      data.url      || '',
    turns:    data.messages?.length || 0,
    messages: data.messages || [],
    logbook:  data.logbook  || { decisions: [], todos: [], insights: [] },
    createdAt: now, updatedAt: now
  };

  await new Promise(resolve => {
    chrome.storage.local.set({ [NS + id]: session }, resolve);
  });

  let index = await getIndex();
  index.unshift({
    id, title: session.title, turns: session.turns,
    createdAt: now,
    logbook: {
      decisions: session.logbook.decisions.length,
      todos:     session.logbook.todos.length,
      insights:  session.logbook.insights.length
    }
  });

  // 古いセッションを削除（容量管理）
  if (index.length > MAX_SESSIONS) {
    const removed = index.splice(MAX_SESSIONS);
    removed.forEach(s => chrome.storage.local.remove(NS + s.id));
  }

  await new Promise(resolve => {
    chrome.storage.local.set({ [INDEX_KEY]: index }, resolve);
  });
  return id;
}

async function getSession(id) {
  return new Promise(resolve => {
    chrome.storage.local.get(NS + id, r => resolve(r[NS + id] || null));
  });
}

async function getStats() {
  const index = await getIndex();
  const totalTodos = index.reduce((s, e) => s + (e.logbook?.todos || 0), 0);
  return {
    sessions: index.length,
    messages: index.reduce((s, e) => s + (e.turns || 0), 0),
    todos:    totalTodos
  };
}

// ── [B] Vault: Pro機能 ────────────────────────────────────────────────────

async function getVaultContext() {
  // Vaultにピン留めされた文脈を返す
  return new Promise(resolve => {
    chrome.storage.local.get(VAULT_KEY, r => {
      const vault = r[VAULT_KEY] || [];
      if (!vault.length) return resolve(null);
      // 有効なエントリを最大3件結合
      const active = vault.filter(v => v.active).slice(0, 3);
      if (!active.length) return resolve(null);
      const context = active.map(v => `[${v.label}]\n${v.text}`).join('\n\n');
      resolve(context);
    });
  });
}

async function addToVault(data) {
  return new Promise(resolve => {
    chrome.storage.local.get(VAULT_KEY, r => {
      const vault = r[VAULT_KEY] || [];
      vault.unshift({
        id:        crypto.randomUUID(),
        label:     data.label || 'Saved context',
        text:      data.text  || '',
        sessionId: data.sessionId || null,
        active:    true,
        createdAt: new Date().toISOString()
      });
      // 最大20件
      if (vault.length > 20) vault.splice(20);
      chrome.storage.local.set({ [VAULT_KEY]: vault }, () => resolve(true));
    });
  });
}

async function toggleVaultEntry(id, active) {
  return new Promise(resolve => {
    chrome.storage.local.get(VAULT_KEY, r => {
      const vault = (r[VAULT_KEY] || []).map(v =>
        v.id === id ? { ...v, active } : v
      );
      chrome.storage.local.set({ [VAULT_KEY]: vault }, () => resolve(true));
    });
  });
}

async function deleteVaultEntry(id) {
  return new Promise(resolve => {
    chrome.storage.local.get(VAULT_KEY, r => {
      const vault = (r[VAULT_KEY] || []).filter(v => v.id !== id);
      chrome.storage.local.set({ [VAULT_KEY]: vault }, () => resolve(true));
    });
  });
}

async function getVaultList() {
  return new Promise(resolve => {
    chrome.storage.local.get(VAULT_KEY, r => resolve(r[VAULT_KEY] || []));
  });
}

// ── License check (Pro) ─────────────────────────────────────────────────────

function isProLicense(key) {
  // MVP: プレフィックスチェック（将来サーバー検証に差し替え可）
  return typeof key === 'string' && key.startsWith('RELAY-PRO-') && key.length >= 20;
}

// ── Message handler ────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {

  if (msg.type === 'RELAY_SAVE_SESSION') {
    saveSession(msg.payload).then(id => sendResponse({ ok: true, id }));
    return true;
  }

  if (msg.type === 'RELAY_GET_STATS') {
    getStats().then(stats => sendResponse(stats));
    return true;
  }

  if (msg.type === 'RELAY_GET_INDEX') {
    getIndex().then(index => sendResponse({ index }));
    return true;
  }

  if (msg.type === 'RELAY_GET_SESSION') {
    getSession(msg.id).then(session => sendResponse({ session }));
    return true;
  }

  if (msg.type === 'RELAY_OPEN_NEW_CHAT') {
    const text = msg.payload.text;
    chrome.tabs.create({ url: 'https://claude.ai/new' }, (tab) => {
      const listener = (tabId, info) => {
        if (tabId !== tab.id || info.status !== 'complete') return;
        chrome.tabs.onUpdated.removeListener(listener);
        setTimeout(() => {
          chrome.tabs.sendMessage(tab.id, { type: 'RELAY_INJECT', payload: { text } });
        }, 2000);
      };
      chrome.tabs.onUpdated.addListener(listener);
    });
    sendResponse({ ok: true });
    return true;
  }

  // ── Vault (Pro) ──────────────────────────────────────────────────────────

  if (msg.type === 'RELAY_GET_VAULT_CONTEXT') {
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result?.mocka_global_prefs || {};
      if (!isProLicense(prefs.licenseKey)) {
        sendResponse({ context: null, error: 'pro_required' });
        return;
      }
      getVaultContext().then(context => sendResponse({ context }));
    });
    return true;
  }

  if (msg.type === 'RELAY_VAULT_ADD') {
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result?.mocka_global_prefs || {};
      if (!isProLicense(prefs.licenseKey)) {
        sendResponse({ ok: false, error: 'pro_required' });
        return;
      }
      addToVault(msg.payload).then(() => sendResponse({ ok: true }));
    });
    return true;
  }

  if (msg.type === 'RELAY_VAULT_TOGGLE') {
    toggleVaultEntry(msg.id, msg.active).then(() => sendResponse({ ok: true }));
    return true;
  }

  if (msg.type === 'RELAY_VAULT_DELETE') {
    deleteVaultEntry(msg.id).then(() => sendResponse({ ok: true }));
    return true;
  }

  if (msg.type === 'RELAY_VAULT_LIST') {
    getVaultList().then(vault => sendResponse({ vault }));
    return true;
  }

  // ── License verify ───────────────────────────────────────────────────────

  if (msg.type === 'RELAY_VERIFY_LICENSE') {
    const valid = isProLicense(msg.key);
    sendResponse({ valid, tier: valid ? 'pro' : 'free' });
    return true;
  }

  // ── Handoff via background (popup→background→content) ───────────────────
  // popupからcontent.jsへ直接sendMessageできない場合のフォールバック
  if (msg.type === 'RELAY_POPUP_HANDOFF') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (!tab) { sendResponse({ ok: false, error: 'no_tab' }); return; }

      // まずscriptingで注入を試みる（content.jsが未注入の場合）
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      }).catch(() => {}).finally(() => {
        // 注入後にメッセージ送信
        setTimeout(() => {
          chrome.tabs.sendMessage(tab.id, { type: 'RELAY_MANUAL_HANDOFF' }, (res) => {
            if (chrome.runtime.lastError) {
              sendResponse({ ok: false, error: chrome.runtime.lastError.message });
            } else {
              sendResponse({ ok: true });
            }
          });
        }, 300);
      });
    });
    return true;
  }
});
