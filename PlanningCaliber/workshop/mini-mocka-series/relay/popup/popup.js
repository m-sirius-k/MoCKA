/**
 * Relay — popup.js
 */

async function init() {
  // Load stats
  chrome.runtime.sendMessage({ type: 'RELAY_GET_STATS' }, (stats) => {
    if (stats) {
      document.getElementById('stat-sessions').textContent = stats.sessions || 0;
      document.getElementById('stat-messages').textContent = stats.messages || 0;
    }
  });

  // Load turn limit from storage
  chrome.storage.sync.get('mocka_global_prefs', (result) => {
    const prefs = result.mocka_global_prefs || {};
    document.getElementById('turn-limit').value = prefs.turnLimit || 20;
  });

  // Save turn limit on change
  document.getElementById('turn-limit').addEventListener('change', (e) => {
    const val = parseInt(e.target.value, 10);
    chrome.storage.sync.get('mocka_global_prefs', (result) => {
      const prefs = result.mocka_global_prefs || {};
      chrome.storage.sync.set({ mocka_global_prefs: { ...prefs, turnLimit: val } });
    });
  });

  // Manual handoff
  document.getElementById('btn-handoff').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { type: 'RELAY_MANUAL_HANDOFF' });
      window.close();
    });
  });

  // History (placeholder for v1.1)
  document.getElementById('btn-history').addEventListener('click', () => {
    chrome.tabs.create({ url: chrome.runtime.getURL('history/history.html') });
  });
}

document.addEventListener('DOMContentLoaded', init);
