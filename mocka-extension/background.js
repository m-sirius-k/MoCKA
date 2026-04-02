const AI_DOMAINS = {
  'ChatGPT':    'chatgpt.com',
  'Gemini':     'gemini.google.com',
  'Perplexity': 'perplexity.ai',
  'Claude':     'claude.ai',
  'Copilot':    'copilot.microsoft.com',
  'Genspark':   'genspark.ai'
};

async function poll() {
  for (const [name, domain] of Object.entries(AI_DOMAINS)) {
    try {
      const res = await fetch(`http://127.0.0.1:5000/get_intent/${name}`).catch(() => null);
      if (!res || !res.ok) continue;
      const data = await res.json();
      if (!data) continue;
      const tabs = await chrome.tabs.query({});
      const targetTab = tabs.find(t => t.url && t.url.includes(domain));
      if (targetTab) {
        await chrome.tabs.update(targetTab.id, { active: true });
        await chrome.windows.update(targetTab.windowId, { focused: true });
        chrome.scripting.executeScript({
          target: { tabId: targetTab.id },
          func: (text) => {
            const el = document.querySelector('textarea, [contenteditable="true"], input');
            if (el) {
              if (el.tagName === 'DIV') el.innerText = text; else el.value = text;
              el.dispatchEvent(new Event('input', { bubbles: true }));
              el.focus();
            }
          },
          args: [data.payload]
        });
      } else {
        chrome.tabs.create({ url: 'https://' + domain });
      }
    } catch(e) { console.error(e); }
  }
}
setInterval(poll, 1500);

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id:'mocka_collect_selected', title:'選択範囲をMoCKAに収集', contexts:['selection'] });
  chrome.contextMenus.create({ id:'mocka_collect_full', title:'このchat全文をMoCKAに収集（自動スクロール）', contexts:['page'] });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const source = detectSource(tab.url);
  if (info.menuItemId === 'mocka_collect_selected') {
    await sendToMocka(source, info.selectionText, tab.url, 'selected');
  } else if (info.menuItemId === 'mocka_collect_full') {
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: async function(source) {
        let last = null;
        for (let i = 0; i < 30; i++) {
          window.scrollTo(0, 0);
          await new Promise(r => setTimeout(r, 1200));
          const h = document.body.scrollHeight;
          if (h === last) break;
          last = h;
        }
        await new Promise(r => setTimeout(r, 2000));
        const SEL = {
          chatgpt:    '[data-message-author-role]',
          claude:     '[data-testid*="message"], .font-claude-message',
          gemini:     'message-content, model-response, user-query',
          perplexity: '[class*="Message"]',
          copilot:    '[class*="message"]',
        };
        const sel = SEL[source] || '[class*="message"], p';
        const nodes = document.querySelectorAll(sel);
        let lines = [];
        nodes.forEach((n, i) => {
          const role = n.getAttribute('data-message-author-role') || (i%2===0 ? 'user' : 'assistant');
          const text = n.innerText.trim();
          if (text) lines.push(`[${role}] ${text}`);
        });
        if (!lines.length) {
          document.execCommand('selectAll');
          const t = window.getSelection().toString().trim();
          window.getSelection().removeAllRanges();
          if (t) lines.push(t);
        }
        return lines.join('\n\n');
      },
      args: [source]
    });
    if (results && results[0] && results[0].result) {
      await sendToMocka(source, results[0].result, tab.url, 'full_scroll');
    }
  }
});

function detectSource(url) {
  if (!url) return 'unknown';
  if (url.includes('chatgpt.com'))       return 'chatgpt';
  if (url.includes('gemini.google.com')) return 'gemini';
  if (url.includes('perplexity.ai'))     return 'perplexity';
  if (url.includes('claude.ai'))         return 'claude';
  if (url.includes('microsoft.com'))     return 'copilot';
  return 'unknown';
}

async function sendToMocka(source, text, url, mode) {
  if (!text) return;
  try {
    const res = await fetch('http://127.0.0.1:5000/collect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source, text, url, mode, timestamp: new Date().toISOString() })
    });
    if (res.ok) {
      chrome.notifications.create({
        type: 'basic', iconUrl: 'icon.png',
        title: 'MoCKA収集完了',
        message: `${source} から収集しました`
      });
    }
  } catch(e) { console.error('MoCKA send error:', e); }
}
