// orchestra_search_bridge.js
// Relay → Orchestra 検索ブリッジ（postMessage方式）
// Orchestra manifest.json の content_scripts に追記して使用
// "matches": ["https://claude.ai/*"] に追加すること

(function () {
  'use strict';

  // 既にロード済みなら二重起動防止
  if (window.__orchestra_search_bridge_loaded) return;
  window.__orchestra_search_bridge_loaded = true;

  console.log('[Orchestra Bridge] Search bridge loaded');

  // ── postMessage受信 → IndexedDB検索 → 結果返送 ──────────────────────────

  window.addEventListener('message', async (event) => {
    // 同一オリジン（claude.ai）のみ受け付ける
    if (event.origin !== location.origin) return;
    const msg = event.data;
    if (!msg || msg.__source !== 'relay') return;

    // 生存確認
    if (msg.type === 'ORCHESTRA_PING') {
      window.postMessage({ __source: 'orchestra', type: 'ORCHESTRA_PONG', reqId: msg.reqId }, '*');
      return;
    }

    // 全文検索
    if (msg.type === 'ORCHESTRA_SEARCH') {
      try {
        const results = await searchViaBackground(msg.query, msg.limit || 30);
        window.postMessage({
          __source: 'orchestra',
          type:     'ORCHESTRA_SEARCH_RESULT',
          reqId:    msg.reqId,
          results,
        }, '*');
      } catch (e) {
        window.postMessage({
          __source: 'orchestra',
          type:     'ORCHESTRA_SEARCH_RESULT',
          reqId:    msg.reqId,
          results:  [],
          error:    e.message,
        }, '*');
      }
      return;
    }

    // セッション一覧取得
    if (msg.type === 'ORCHESTRA_GET_SESSIONS') {
      try {
        const sessions = await getSessionsViaBackground(msg.limit || 20);
        window.postMessage({
          __source: 'orchestra',
          type:     'ORCHESTRA_SESSIONS_RESULT',
          reqId:    msg.reqId,
          sessions,
        }, '*');
      } catch (e) {
        window.postMessage({
          __source: 'orchestra',
          type:     'ORCHESTRA_SESSIONS_RESULT',
          reqId:    msg.reqId,
          sessions: [],
          error:    e.message,
        }, '*');
      }
      return;
    }
  });

  // ── background.js経由でIndexedDB検索 ──────────────────────────────────────

  function searchViaBackground(query, limit) {
    return new Promise((resolve, reject) => {
      try {
        chrome.runtime.sendMessage(
          { type: 'ORCHESTRA_SEARCH_MESSAGES', query, limit },
          (response) => {
            if (chrome.runtime.lastError) {
              reject(new Error(chrome.runtime.lastError.message));
              return;
            }
            resolve(response?.results || []);
          }
        );
      } catch (e) {
        reject(e);
      }
    });
  }

  function getSessionsViaBackground(limit) {
    return new Promise((resolve, reject) => {
      try {
        chrome.runtime.sendMessage(
          { type: 'ORCHESTRA_GET_SESSIONS_LIST', limit },
          (response) => {
            if (chrome.runtime.lastError) {
              reject(new Error(chrome.runtime.lastError.message));
              return;
            }
            resolve(response?.sessions || []);
          }
        );
      } catch (e) {
        reject(e);
      }
    });
  }

})();
