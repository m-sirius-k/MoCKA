// mocka_perplexity.js v1.0
// Perplexityページで自動全選択→クリップボードコピー→MoCKAに送信

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'collect_clipboard') {
    // 自動でCtrl+A → Ctrl+C → clipboard読み取り
    (async () => {
      try {
        // 全選択
        document.execCommand('selectAll');
        await new Promise(r => setTimeout(r, 300));

        // クリップボードにコピー
        document.execCommand('copy');
        await new Promise(r => setTimeout(r, 300));

        // クリップボードから読み取り
        const text = await navigator.clipboard.readText();

        // 選択解除
        window.getSelection().removeAllRanges();

        if (text && text.length > 20) {
          sendResponse({ ok: true, text: text });
        } else {
          // fallback: innerTextで取得
          const fallback = document.body.innerText;
          sendResponse({ ok: true, text: fallback });
        }
      } catch(e) {
        // clipboard APIが使えない場合はinnerTextで代替
        try {
          const text = document.body.innerText;
          sendResponse({ ok: true, text: text });
        } catch(e2) {
          sendResponse({ ok: false, error: e2.message });
        }
      }
    })();
    return true; // async response
  }
});
