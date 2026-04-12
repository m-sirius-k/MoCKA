chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('claude.ai/new')) {
        console.log("[MOCKA] DNA注入開始: " + tab.url);
        
        // メッセージ送信ではなく、直接スクリプトを実行してステータスバーを強制描画
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ['content.js']
        }).then(() => {
            console.log("[MOCKA] content.js 物理注入完了");
        }).catch(err => console.error("[MOCKA] 注入失敗:", err));
    }
});

// fetch要求を受け取るリスナー
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "GET_SYSTEM_STATUS") {
        fetch('http://127.0.0.1:5000/get_latest_dna')
            .then(response => response.json())
            .then(data => sendResponse({ status: 'OK', dna: data }))
            .catch(err => sendResponse({ status: 'ERROR', error: err.message }));
        return true; // 非同期応答を維持
    }
});

// ── 新規chat時DNA注入（入力欄にセット・送信しない） ──
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete') return;
  if (!tab.url) return;
  if (!tab.url.includes('claude.ai/new') && !tab.url.includes('claude.ai/chat/new')) return;
  chrome.scripting.executeScript({
    target: { tabId: tabId },
    func: async function() {
      if (sessionStorage.getItem('MOCKA_DNA_SET')) return;
      try {
        const res = await fetch('http://127.0.0.1:5000/get_latest_dna');
        if (!res.ok) return;
        const data = await res.json();
        if (data.status !== 'OK') return;
        const p = data.ping;
        const text = '[MOCKA]{"H":"' + p.H + '","G":' + p.G + ',"C":"' + p.C + '","P":"' + p.P + '"}';
        const observer = new MutationObserver(() => {
          const input = document.querySelector('div[contenteditable="true"]');
          if (!input) return;
          observer.disconnect();
          input.focus();
          input.innerText = text;
          input.dispatchEvent(new InputEvent('input', { bubbles: true }));
          sessionStorage.setItem('MOCKA_DNA_SET', '1');
        });
        observer.observe(document.body, { childList: true, subtree: true });
        setTimeout(() => observer.disconnect(), 15000);
      } catch(e) { console.log('[MOCKA] fetch error:', e); }
    }
  });
});
