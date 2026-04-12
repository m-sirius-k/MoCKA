chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes('claude.ai/new')) {
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ['content.js']
        }).catch(err => console.error("[MOCKA] 注入失敗:", err));
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "GET_SYSTEM_STATUS") {
        fetch('http://127.0.0.1:5000/get_latest_dna')
            .then(response => response.json())
            .then(data => sendResponse({ status: 'OK', dna: data }))
            .catch(err => sendResponse({ status: 'ERROR', error: err.message }));
        return true;
    }
});

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

        // 最小注入：H/G/C/Pのみ（chat欄汚染なし）
        const text = '[MOCKA]{"H":"' + p.H + '","G":' + p.G + ',"C":"' + p.C + '","P":"' + p.P + '"}';

        const observer = new MutationObserver(() => {
          const input = document.querySelector('div[contenteditable="true"]');
          if (!input) return;
          observer.disconnect();
          input.focus();
          input.innerText = text;
          input.dispatchEvent(new InputEvent('input', { bubbles: true }));
          sessionStorage.setItem('MOCKA_DNA_SET', '1');
          console.log('[MOCKA] DNA最小注入完了');
        });
        observer.observe(document.body, { childList: true, subtree: true });
        setTimeout(() => observer.disconnect(), 15000);
      } catch(e) { console.log('[MOCKA] fetch error:', e); }
    }
  });
});
