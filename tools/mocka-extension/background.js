const AI_DOMAINS = {
  'ChatGPT':    'chatgpt.com',
  'Gemini':     'gemini.google.com',
  'Perplexity': 'perplexity.ai',
  'Claude':     'claude.ai',
  'Copilot':    'copilot.microsoft.com',
  'Genspark':   'genspark.ai'
};

// ── 右クリックメニュー ──────────────────────────────────────
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({ id:'mocka_collect_selected', title:'選択範囲をMoCKAに収集', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka_collect_full',     title:'このchat全文をMoCKAに収集', contexts:['page'] });
    chrome.contextMenus.create({ id:'mocka_share',            title:'MoCKAに共有（Broadcast）', contexts:['selection'] });
    chrome.contextMenus.create({ id:'mocka_collaborate',      title:'MoCKAで協議（Orchestra）', contexts:['selection'] });
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const source = detectSource(tab.url);

  if (info.menuItemId === 'mocka_share') {
    const text = info.selectionText || '';
    if (!text) return;
    try {
      await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ c: 'B', o: text, memo: `${source}から共有` })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'MoCKA共有完了', message:'オーケストラに送信しました' });
    } catch(e) { console.error('share error:', e); }
    return;
  }

  if (info.menuItemId === 'mocka_collaborate') {
    const text = info.selectionText || '';
    if (!text) return;
    try {
      await fetch('http://127.0.0.1:5000/orchestra', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text, mode: 'orchestra' })
      });
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'MoCKA協議開始', message:'4AI合議を開始しました' });
    } catch(e) { console.error('collaborate error:', e); }
    return;
  }

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

// ── ユーティリティ ──────────────────────────────────────────
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
      chrome.notifications.create({ type:'basic', iconUrl:'icon.png', title:'MoCKA収集完了', message:`${source} から収集しました` });
    }
  } catch(e) { console.error('MoCKA send error:', e); }
}
