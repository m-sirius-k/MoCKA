// mocka_perplexity.js v1.1
console.log("[MOCKA] mocka_perplexity.js content script loaded!");

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'collect_clipboard') {
    (async () => {
      try {
        document.execCommand('selectAll');
        await new Promise(r => setTimeout(r, 300));
        document.execCommand('copy');
        await new Promise(r => setTimeout(r, 300));
        const text = await navigator.clipboard.readText();
        window.getSelection().removeAllRanges();
        if (text && text.length > 20) {
          sendResponse({ ok: true, text: text });
        } else {
          const fallback = document.body.innerText;
          sendResponse({ ok: true, text: fallback });
        }
      } catch(e) {
        try {
          const text = document.body.innerText;
          sendResponse({ ok: true, text: text });
        } catch(e2) {
          sendResponse({ ok: false, error: e2.message });
        }
      }
    })();
    return true;
  }
});
